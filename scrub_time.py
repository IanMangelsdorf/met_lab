import xlrd
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists
from datetime import datetime
from timedata import Base, Staff, Project, WorkOrder, Task, Timesheet


fname = 'V:\\1TECHSRV\\Met Services Personnel\\Met Manager Info\\Jess and Ian\\WE010919.xlsx'
rootDir = 'V:\\1TECHSRV\\Met Services Personnel\\Jessica\JDEGS\\Timesheet upload\\2019'
workorders = 'C:\\Users\\ian.mangelsdorf\\PycharmProjects\\met_lab\\workload.xlsx'
bidFile = 'V:\\1TECHSRV\\Project Management\\EOM\\Project master file.xlsx'
bid_directory =''
engine = create_engine('sqlite:///mets_data.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


x=0



def add_time(staff_id, hours,week, obj, sub,bu , wo):
    try:
        add_time = Timesheet(staff_id=staff_id,
                             monday=0,
                             tuesday=0,
                             wednesday=0,
                             thursday=0,
                             saturday=0,
                             sunday=0,
                             friday=hours,
                             task_id=1,
                             weekstarting=week,
                             jdeg_obj=obj,
                             jdeg_sub=sub,
                             bu_id=bu,
                             wo_id=wo)
        session.add(add_time)
        session.commit
    except:
        session.rollback
        print("failed to Add Hours")

def add_wo(name,code, bid, project):
    if bid == "":
        bid=1
    add_wo = WorkOrder(wo_code=code,
                          wo_name=name,
                          bid=bid,
                          project_id=project)
    try:
        session.add(add_wo)
        session.commit()
    except Exception as e:
        session.rollback
        print("Failed to add work order" + str(code))

def add_staff (last, first, obj, oricle, step, type, active):
    try:
        add_staff = Staff(surname=last,
                          first= first,
                          jdegsOBJ=obj,
                          oricle=oricle,
                          jobstep=step  ,
                          jobtype=type,
                          active=active
                          )
        session.add(add_staff)
        session.commit()
    except:
        session.rollback
        print ('Failed to add' + last)


def add_project(code, name, client, open):
    add_project = Project(project_code=code,
                          project_name=name,
                          client=client,
                          open=open)
    try:
        session.add(add_project)
        session.commit()
    except:
        session.rollback
        print("Failed to add project" + str(code))

def get_time_cols(xl):
    dict_headers={}
    for c in range(xl.ncols):
        dict_headers.update({xl.cell(1,c).value:c})
    return dict_headers

def parse_time():
    pass



def parse_staff(xl):
        for r in range(xl.nrows):
            if not xl.cell(r,2).ctype==0 and not str(xl.cell(r,1).value).lower() == 'emp':
                if session.query(Staff.id).filter(Staff.oricle == int((xl.cell(r,2)).value)).scalar() is None:
                    print(int(xl.cell(r, 2).value))
                    add_staff (last= xl.cell(r, 1).value, first= "",obj = "",oricle=int(xl.cell(r,2).value),
                               step=int(xl.cell(r, 17).value), type=xl.cell(r, 16).value, active=True)

                staff_id = session.query(Staff.id).filter(Staff.oricle == int(xl.cell(r,2).value)).one()[0]

                if not xl.cell(r,6).ctype==0:
                    bu = int(xl.cell(r,6).value)
                    if session.query(Project.id).filter(Project.project_code == bu).scalar() is None:
                        add_project(name= xl.cell(r,3).value , code= bu, client=bu ,  open=True)
                    bu_id = session.query(Project.id).filter(Project.project_code == bu).one()[0]
                else:
                    bu_id =1

                if not xl.cell(r,7).ctype==0:
                    jdeg_obj = int(xl.cell(r,7).value)

                else:
                    jdeg_obj =1

                if not xl.cell(r, 8).ctype==0:
                    jdeg_sub = int(xl.cell(r, 8).value)

                else:
                    jdeg_sub = 1



                if not xl.cell(r,9).ctype==0:
                    wo = int(xl.cell(r,9).value)
                    if session.query(WorkOrder.id).filter(WorkOrder.wo_code == wo).scalar() is None:
                        add_wo(name= "Unknown", code= wo, bid = "Unknown", project= bu_id)
                    wo_id = session.query(WorkOrder.id).filter(WorkOrder.wo_code == wo).one()[0]
                else:
                    wo, wo_id = 1,1



                explanation = (xl.cell(r,3).value)
                if xl.cell(r,4).ctype==3:
                    we_date = datetime.fromordinal(int(xl.cell(r,4).value))
                else:
                    we_date = datetime.now()

                add_time(staff_id= staff_id, hours = xl.cell(r,4).value, week = we_date, obj = jdeg_obj, sub = jdeg_sub,bu = bu_id, wo = wo_id)



def parse_bu(xl):
    for r in range(xl.nrows):
        if not xl.cell(r,2).value=='' and not isinstance(xl.cell(r,2).value,str):
            description = xl.cell(r, 4).value.splitlines()
            if xl.cell(r, 1) == "VF":
                active = True
            else:
                active = False

            if session.query(Project.id).filter(Project.project_code == int((xl.cell(r, 2)).value)).scalar() is None:
                try:
                    add_project(code =int(xl.cell(r,2).value) , name =description[0] , client = description[0], open = active)
                except Exception as e:
                    session.rollback()
                    print(e)

            project_id = session.query(Project.id).filter(Project.project_code == int(xl.cell(r,2).value)).one()[0]

            if session.query(WorkOrder.id).filter(WorkOrder.wo_code == int((xl.cell(r, 3)).value)).scalar() is None:
                try:
                    add_wo(name =int(xl.cell(r,3).value) , code = description[-1], bid = "", project=project_id)
                except:
                    session.rollback()


def parse_task():
    pass

def parse_bid():
    pass

def parse_bid_reg():
    xl = xlrd.open_workbook(os.path.join(bidFile))
    for index,  bu in enumerate(xl.sheet_names()):
        if not 'master' in bu.lower():
            sh = xl.sheet_by_index(index)
            bu = int(bu)
            if session.query(Project.id).filter(Project.project_code == bu).scalar() is None:
                add_project(code= bu, name=sh.cell(1, 2).value, client=sh.cell(1, 2).value, open=True)

            for r in range(4,sh.nrows):
                if sh.cell(r,1).ctype == 2:
                    if session.query(WorkOrder.id).filter(WorkOrder.wo_code==int(sh.cell(r,1).value)).scalar() is None:
                        project_id = session.query(Project.id).filter(Project.project_code == bu).one()
                        add_wo(name=sh.cell(r,2).value, code=int(sh.cell(r,1).value), bid = 'MTMS' + str(sh.cell(r,3).value), project=project_id[0])



def main():
    parse_bid_reg()
    parse_bid()
    bu = xlrd.open_workbook(workorders)
    for index in range(bu.nsheets):
        if 'sheet1' in (bu.sheet_by_index(index).name).lower():
            parse_bu(bu.sheet_by_index(index))

    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in fileList:
            if '.xls' in fname or '.xlsx' in fname:
                rs = xlrd.open_workbook(os.path.join(dirName,fname))
                for index in range(rs.nsheets):
                    if 'timesheet' in rs.sheet_by_index(index).name.lower():
                        print(fname)
                        parse_staff(rs.sheet_by_index(1))


if __name__ == '__main__':

    main()

