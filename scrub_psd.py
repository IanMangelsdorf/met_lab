import os
import pandas as pd
import time
import pickle
import uuid
import math
import xlrd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists

from sqllite import Base, Project,Sample, PSD, Test
import multiprocessing

#rootDir = 'V:\\1TECHSRV'
#rootDir = 'E:\\test'
rootDir = 'E:\\Genral Files\\2018 Data Folder'
#rootDir = 'C:\\2018 Data Folder'
engine = create_engine('sqlite:///mets_data.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
x=0





def barcode_exists(v):

    while not Sample.querry(exists().where(Sample.barcode==v)):
        v= uuid.uuid4().__str__()
    return v

def meta_detail(df):
  pass


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


def isPSD(fname):
    if 'psd' in fname.lower() or 'size analysis' in fname.lower():
        return True
    else: return False


def get_test(detail):
    x = detail.split(' ')

    for i, y in enumerate(x):
      if y.startswith('('):
        test = ' '.join([y,x[i+1]])
    #i, test = [y for index, y in iter(x) if y.startswith('(')]

    return test

def parse_xrf(xl, project, path, fileDate):
    for c in range(xl.ncols):
        for r in range(xl.nrows):

           if 'size fraction' in str(xl.cell(r, c).value):
                head_row = r
                head_col = c

                test = get_test(xl.cell(r - 1, head_col).value)
                test_name = ('  ').join([project[0], test])
                if not session.query(exists().where(Test.test_name == test_name)).scalar():
                    new_test = Test(test=test,
                                    test_name=test_name
                                    )
                    session.add(new_test)
                    session.commit()
                    test_id = Test.id
                else:
                    test_id = session.query(Test.id).filter(Test.test_name == test_name).one()
                    session.rollback()

                feed = xl.cell(r-1,head_col).value
                if xl.cell(r+2,c+1).value == "%wt":
                    r+=3
                    c+=1
                else:
                    r+=2
                    c+=1

                while not xl.cell(r, c).value == '':

                    while not xl.cell(r, c).value == '':
                        new_psd = PSD(test_no=test,
                                      fraction=xl.cell(r,head_col).value,
                                      feed= feed,
                                      cum_passing=xl.cell(r, c).value,
                                      test_id = test_id[0]
                                      )
                        session.add(new_psd)
                        session.commit()
                        print (new_psd)
                        r+=1

def main():
    for dirName, subdirList, fileList in os.walk(rootDir):
        if "data" in dirName.lower():
            p, project_number, client = get_project(dirName)

            if not session.query(exists().where(Project.project_code == project_number)).scalar():
                new_project = Project(project_name=p,
                                      project_code=project_number,
                                      client=client)
                session.add(new_project)
                session.commit()
                print (dirName + ' project added')
                project= new_project. project_code
            else:
                project = session.query(Project. project_code).filter(Project.project_code == project_number).one()

            for fname in fileList:
                if '.xls' in fname or '.xlsx' in fname:

                    if isPSD(fname):
                        fileDate = time.ctime(os.path.getctime(os.path.join(dirName, fname)))

                        try:
                            rs = xlrd.open_workbook(os.path.join(dirName, fname))
                            for index in range(rs.nsheets):
                                parse_xrf(rs.sheet_by_index(index), project, os.path.join(dirName, fname), fileDate)

                        except Exception as e:
                            print(e)


if __name__ == '__main__':

    main()