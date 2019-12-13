import os
import pandas as pd
import time
import pickle
import uuid
import math

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists

from sqllite import XRF, Base, Project,Sample
import multiprocessing

#rootDir = 'V:\\1TECHSRV'
rootDir = 'E:\\Genral Files\\2018 Data Folder'
#rootDir = 'C:\\2018 Data Folder'
engine = create_engine('sqlite:///mets_data.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
x=0
df_Headers = ['Project','Date','Sample','Test','Method','Units','Detection','Element','Value','file']
final_df = pd.DataFrame(columns=df_Headers)
dictProjects ={}
dictFiles ={}


def get_test(zz):
    if zz=="":
        x = zz.split(" ")
        for index, y in enumerate(x):
            if y[0].lower()=='t' and len(y)==1:
                test = y + x[index + 1]
                return test
            elif y[0].lower()=='t' and len(y)>2:
                test = y
                return test



def get_source(x):
    dictSource = {'head':"Head",
                  'headsample':"Head",
                  'con':"Cons",
                  'mid':'Mids',
                  'tail':'Tails',
                  'mag':'Mag',
                  'feed':'Feed',
                  'cond':'Conditioning',
                  'composite':'Compostie',
                  'whims':'WHIMS',
                  'u/f':'Cyclone U/F',
                  'cyclone':'Cyclone',
                  'rougher':'Rougher',
                  'cyclosizer':'Cylcosizer',
                  'bulk':'Bulk Product',
                  'c1':'Cons',
                  'c2:':'Cons',
                  'c3:':'Cons',
                  'm1:':'Mids',
                  'm2:': 'Mids',
                  'm3:':'Mids',
                  'mid3:': 'Mids',
                  'mid:': 'Mids',
                  'mid3:': 'Mids',
                  'con1': 'Cons',
                  'con2:': 'Cons',
                  'con3:': 'Cons'

                }



    if isinstance(x, str):
        tests = x.split(" ")
        for s in range((len(tests))-1,0,-1):
            if tests[s].lower() in dictSource:
                y = tests[s].lower()
                return dictSource[y]
    else:
        return ""



def barcode_exists(v):

    while not Sample.querry(exists().where(Sample.barcode==v)):
        v= uuid.uuid4().__str__()
    return v

def meta_detail(df):
    dictHeaders = {'UNITS':"", 'ELEMENTS':"", 'SAMPLE':"", 'DETECTION':"", 'METHOD':"" ,'LLD':"" ,'CODE':"",'StartCol':2}

    #xx = [index  for index, rows in df.itterows() if rows[0].upper() in dictHeaders]
    for index, rows in df.iterrows():
        if str(rows[0]).upper() in dictHeaders:
            dictHeaders[rows[0].upper()]=index
        if not isinstance(rows[1], str) and not math.isnan(rows[1]):
            dictHeaders['StartCol']=1
        if isinstance(rows[0],int):
            dictHeaders['ELEMENTS']=index

    if not dictHeaders['LLD']=="":
        dictHeaders['DETECTION']= dictHeaders['LLD']
    if not dictHeaders['CODE']=="":
        dictHeaders['METHOD']= dictHeaders['CODE']
    if not dictHeaders['SAMPLE']=="":
        dictHeaders['ELEMENTS']= dictHeaders['SAMPLE']


    return dictHeaders

def sgRange(detail):
    sg=(0,0)
    if ' ' in detail:
        x = detail.split(' ')
        for index, y in enumerate(x):
            if isinstance(y,float):
                if -5 <= y <= 5:
                    if y<0: sg[0]=y
                    if y>0: sg[1]=y
    return sg

def this_size(detail):
    size = ('','')
    if  ' ' in detail:
        x = detail.split(' ')

        for index, y in enumerate(x):
            if y[0]=='-':
                size[0] = y
            elif y[0] == '+':
                size[1] = y


            if y=='-':
                size[0] = y +x[index +1]
            elif y== '+':
                size[1] = y+ x[index +1]

        return size


def get_project(str):
    str= "  ".join(str.split())
    lst = str.split('\\')

    if len(lst[-1].split(' '))>1:
        p = lst[-1]
    else:
        p = lst[-2].strip()

    l = p.split(' ')

    if  l[0].isdigit:
        project_number = l[0]
        client = ' '.join(l[1:])
    else:
        project_number = "Unknown"
        client = "Unknown"
    return p, project_number, client


def isAssay(fname):
    if "-" in fname:
        fname = fname.split(".")
        a = fname[0].split("-")
        if len(a[0])==4 and len(a[1])==4 and len(a)==2:
            return True


def parse_xrf(xl, new_project_id, path, fileDate):
    df = xl.parse(xl.sheet_names[0],header=None)

    dictHeaders = meta_detail(df.iloc[0:10, 0:2])


    for index, rows in df.iterrows():
        if "/" in str(rows[0]):

            if dictHeaders['StartCol'] == 2:
                test = rows[1]
            else:
                test = "Unknown"

            if isinstance(test, str) and not str=="":
                source = get_source(test)
                test_no = get_test(test)
                #lower, upper = size_fraction(test)
                size = this_size(test)
                sg= sgRange(test)
                split_test = ['','','','','']

                zz = test.split(' ')
                for s in range(4):
                    try:
                        split_test[s]=zz[s]
                    except:
                        pass
            if not session.query(exists().where(Sample.name == rows[0])).scalar():
                new_sample = Sample(name = rows[0],
                                    test= test,
                                    barcode =uuid.uuid4().__str__(),
                                    project_id= new_project_id,
                                    xrf_file= path,
                                    xrf_date=fileDate,
                                    source = source,
                                    test_no= test_no,
                                    lower_size=split_test[0],
                                    upper_size = split_test[1],
                                    upper_sg = split_test[2],
                                    lower_sg = split_test[3],
                                    spare = split_test[4]
                                    )
                try:
                    session.add(new_sample)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print ('{} {} {}'.format (e, rows[0], path))


                col_no = dictHeaders['StartCol']

                for col, itms in rows[dictHeaders['StartCol']:].items():

                    if dictHeaders["UNITS"] =="":
                        unit = "%"
                    else:
                        unit = df.iloc[dictHeaders["UNITS"],col_no]


                    if dictHeaders["DETECTION"] =="":
                        detection = "Unknown"
                    else:
                        detection = df.iloc[dictHeaders["DETECTION"],col_no]

                    if dictHeaders["METHOD"] =="":
                        method = "Unknown"
                    else:
                        method = df.iloc[dictHeaders["METHOD"],col_no]

                    if dictHeaders['ELEMENTS']=="":
                        element ="Unknown"
                    else:
                        element = df.iloc[dictHeaders['ELEMENTS'], col_no]

                    if not itms =="":
                        if "<" in str(itms) or (itms <0 and not 'loi' in element):
                            itms ='Tr'

                        try:
                            new_xrf = XRF(sample_id = new_sample.id,
                                             method =method,
                                             unit =unit,
                                             detection =detection,
                                             element =element,
                                             value =str(itms),
                                             report_order =col-dictHeaders['StartCol']
                                             )
                            session.add(new_xrf)
                            session.commit()
                            col_no+= 1
                            #print(os.path.join(path) + ' ' +rows[0] +' Success')
                        except Exception as e:
                            session.rollback()
                            print(os.path.join(path) + '  ' + rows[0] +'Failed')



def main():
    for dirName, subdirList, fileList in os.walk(rootDir):
        if "Assays" in dirName:
            p, project_number, client = get_project(dirName)

            if not session.query(exists().where(Project.project_code == project_number)).scalar():

                new_project = Project(project_name=p,
                                      project_code=project_number,
                                      client=client)
                session.add(new_project)
                session.commit()
                print (dirName + ' project added')

                for fname in fileList:
                    if '.xls' in fname or '.xlsx' in fname:



                        fileDate = time.ctime(os.path.getctime(os.path.join(dirName, fname)))
                        if isAssay(fname):
                            try:
                                xl = pd.ExcelFile(os.path.join(dirName, fname))
                                parse_xrf(xl, new_project.id, os.path.join(dirName, fname), fileDate)

                            except Exception as e:
                                pass
                                # + " " 'Failed')


if __name__ == '__main__':

    main()