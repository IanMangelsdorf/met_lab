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

from timedata import Base, Bid_Register
import multiprocessing

fname = "V:\\1TECHSRV\\Proposals\\Register of Proposal Numbers\\Proposal # 2019\\Proposal # 2019.xlsm"
#fname =  'V:\\1TECHSRV\Proposals\\Register of Proposal Numbers\\Proposal # 2018\\proposal # 2018.xlsx'

engine = create_engine('sqlite:///mets_data.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
x=0


def isBidSheet():
    pass

def parse_register(ws):
    for r in range(ws.nrows):
        if 'MT' in ws.cell(r,2).value and not ws.cell(r,3).value=="":
            new_bid = Bid_Register(
                bid_number = (ws.cell(r,2).value).replace(" ", ''),
                submit = ws.cell(r,0).value,
                close = ws.cell(r,1).value,
                client =ws.cell(r,3).value,
                contact = ws.cell(r,4).value,
                description = ws.cell(r,5).value,
                ms = ws.cell(r,6).value,
                bd = ws.cell(r,7).value,
                mineral = ws.cell(r,8).value,
                region = ws.cell(r,9).value,
                go = ws.cell(r,12).value,
                get = ws.cell(r,13).value,
                margin = ws.cell(r,14).value,
                status = ws.cell(r,18).value)

            session.add(new_bid)
            session.commit()

def main():


    try:
        rs = xlrd.open_workbook(fname)

        for index in range(rs.nsheets):
            if 'MT MS #' in rs.sheet_by_index(index).name:
                parse_register(rs.sheet_by_index(index))
                print(fname)
    except Exception as e:
        print (e)
        pass


if __name__ == '__main__':

    main()

