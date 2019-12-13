import os
import pandas as pd
import time
import pickle
import uuid
import math

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists

from sqllite import XRF, Base, Project,Sample, Files

rootDir = 'V:\\1TECHSRV'
#rootDir = 'E:\\Genral Files\\2018 Data Folder'
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


def isAssay(fname):
    try:
        if "-" in fname:
            fname = fname.split(".")
            a = fname[0].split("-")
            if len(a[0])==4 and len(a[1])==4 and len(a)==2:
                return True
        elif 'assay' in fname.lower():
                return True
        else: return False
    except Exception as e:
        print (e)
        return False


def isfinal(fname):
    pass



def isSpiral(fname):
    if 'spiral' in fname.lower():
        return True
    else:
        return False
def isCircuit(fname):
    if 'circuit' in fname.lower():
        return True
    else:
        return False
def isFlowsheet(fname):
    if 'flow' in fname.lower():
        return True
    else:
        return False

def isRelease(fname):
    if 'release' in fname.lower() or 'mg' in fname.lower():
        return True
    else:
        return False

def isFeed(fname):
    if 'feed' in fname.lower():
        return True
    else:
        return False

def isMetBalance(fname):
    if 'bal' in fname.lower() and 'met' in fname.lower():
        return True
    else:
        return False

def isMassBalance(fname):

    if 'bal' in fname.lower() and not 'met' in fname.lower() and not 'water' in fname.lower():
        return True
    else:
        return False

def isWaterBalance(fname):
    if 'bal' in fname.lower() and 'water' in fname.lower():
        return True
    else:
        return False

def isCharacterization(fname):
    if 'charact' in fname.lower():
        return True
    else:
        return False

def isWhimms(fname):
    if 'whimm' in fname.lower():
        return True
    else:
        return False


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








if __name__ == '__main__':
    for dirName, subdirList, fileList in os.walk(rootDir):
        p, project_number, client = get_project(dirName)

        if not session.query(exists().where(Project.project_code==project_number)).scalar():

            new_project = Project(project_name=p,
                                  project_code=project_number,
                                  client=client)
            session.add(new_project)
            session.commit()

            for fname in fileList:
                if '.xls' in fname or '.xlsx' in fname:
                    fileDate = time.ctime(os.path.getctime(os.path.join(dirName, fname)))
                    new_file = Files (filename=fname,
                                        path=os.path.join(dirName, fname),

                                        isAssay=isAssay(fname),
                                        isSpiral = isSpiral(fname),
                                        isCircuit = isCircuit(fname),
                                        isFlowsheet = isFlowsheet(fname),
                                        isRelease = isRelease(fname),
                                        isFeed = isFeed(fname),
                                        isMetBalance = isMetBalance(fname),
                                        isMassBalance = isMassBalance(fname),
                                        isWaterBalance = isWaterBalance(fname),
                                        isCharacterization = isCharacterization(fname),
                                        isWhimms= isWhimms(fname),
                                        project_id=new_project.id)

                    if not (new_file.isWhimms or new_file.isCharacterization or new_file.isWaterBalance or new_file.isMetBalance or new_file.isFeed or new_file.isMassBalance or new_file.isRelease or new_file.isCircuit or new_file.isFlowsheet or new_file.isAssay or new_file.isSpiral):
                        new_file.noselection = True

                    session.add(new_file)
                    session.commit()
                    print (new_file.filename)

