import os

import time
import pickle
import uuid
import math
import xlrd

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exists, or_, and_

from timedata import Base, Bid, Bid_Register
import multiprocessing


rootDir = 'C:\\Proposals\\Proposals 2019\\Proposals'

engine = create_engine('sqlite:///mets_data.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
x=0
job_phase = ("A","B","C","D","E","F","G","H","I","J")


def add_task(name, met, tech, snr, wo):
    try:
        add_task= Bid(task_name =name,
                       mets_hours =met,
                       tech_hours =tech,
                       snr_hours =  snr,
                       wo_id = wo)
        session.add(add_task)
        session.commit
    except Exception as e:
        session.rollback
        print(e)

def add_bid(client, bid, description, submit, contact, ms, bd):
    try:
        bid = Bid_Register(client=client,
                               bid_number=bid,
                               description=description,
                               submit=submit,
                               contact=contact,
                               ms=ms,
                               bd=bd)
        session.add(bid)
        session.commit()
    except Exception as e:
        print(e)

def isBid(ws):
    if ws.ncols <2 or ws.nrows <2:
        return False
    if 'Proposal' in str(ws.cell(0, 1).value) and "Revision" in str(ws.cell(1,1).value) and "Client" in str(ws.cell(2, 1).value):
        return True
    else:
        return False

def parse_bid(ws, fpath, fdate):
    bid = str(ws.cell(0,2).value)
    bid = bid.replace(" ",'')

    if session.query(Bid_Register.id).filter(Bid_Register.bid_number==bid).scalar() is None:
        add_bid(client=ws.cell(2,2).value, bid= bid,description = ws.cell(4,2).value, submit = ws.cell(8,2).value,
                contact = ws.cell(5,2).value, ms =ws.cell(6,2).value, bd = ws.cell(7,2).value  )

    bid_id = session.query(Bid_Register.id).filter(Bid_Register.bid_number == bid).one()[0]


    rev = str(ws.cell(1,2).value)
    client= ws.cell(2,2).value
    scope = ws.cell(4,2).value
    dt = ws.cell(8,2).value
    cost_row=0
    start_col=0
    itm=""
    itm_1=""
    sub_desc=""
    desc= ""
    resource=''
    amt=0
    cost=0

    for r in range(ws.nrows):
        if 'cost' in str((ws.cell(r,1).value)).lower():
            cost_row = r
        if 'SCOPE' in str(ws.cell(r,2).value):
            resource_row = r+1

    for c in range(ws.ncols):
        if 'tech' in  str(ws.cell(11,c)).lower():
            start_col = c
            break

    if session.query(Bid.id).filter(and_(Bid.rev == rev, Bid.id == bid_id)).scalar() is None:
        for r in range(0,cost_row-1):
            if not ws.cell(r,2).ctype==0 or not ws.cell(r,2).value=="Sub-total":
                if ws.cell(r,1).value in job_phase:
                    itm_1= ws.cell(r,1).value
                    sub_desc = ws.cell(r,2).value
                elif isinstance(ws.cell(r,1).value,float):
                    itm = str(itm_1) + str(ws.cell(r,1).value)
                    desc = ws.cell(r,2).value
                    start_col=4
                    for c in range(start_col, ws.ncols):
                        if isinstance(ws.cell(r,c).value,float):
                            if "xrf" in ws.cell( resource_row ,c).value.lower():
                                resource='XRF'
                            else:
                                resource = ws.cell( resource_row ,c).value
                            amt = ws.cell(r,c).value
                            cost =ws.cell(cost_row,c).value
                            if not isinstance(cost,str):

                                new_bid = Bid(bid_id =bid_id,
                                              rev=str(rev),
                                              scope=str(scope),
                                              item=str(itm),
                                              subDesc=str(sub_desc),
                                              desc=str(desc),
                                              service=str(resource),
                                              amount=amt,
                                              cost=cost,
                                              file=fpath,
                                              date=fdate
                                              )

                                session.add(new_bid)
                                session.commit()




def main():
    for dirName, subdirList, fileList in os.walk(rootDir):
        if "mt" in dirName.lower():
            for fname in fileList:
                if '.xls' in fname or '.xlsx' in fname:
                    fileDate = time.ctime(os.path.getctime(os.path.join(dirName, fname)))
                    try:
                        rs = xlrd.open_workbook(os.path.join(dirName, fname))
                        for index in range(rs.nsheets):
                            if isBid(rs.sheet_by_index(index)):
                                parse_bid(rs.sheet_by_index(index),  fname, fileDate)
                    except Exception as e:
                        print (fname)
                        print(e)


if __name__ == '__main__':

    main()