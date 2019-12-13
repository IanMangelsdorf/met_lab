from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship



Base = declarative_base()

metadata = MetaData()



class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True,nullable=False)
    project_name = Column(String(), nullable=False, unique=False)
    project_code = Column(String(), nullable=False, unique=False)
    client = Column(String(), nullable=False, unique=False)
    open = Column(Boolean(),nullable=False)

    def __repr__(self):
        return '<Project(%r, $r ,%r)>' % (
            self.project_name, self.project_code, self.client
        )

class WorkOrder(Base):
    __tablename__ = 'workorder'

    id = Column(Integer, primary_key=True,nullable=False)
    wo_name = Column(String(), nullable=False, unique=False)
    wo_code = Column(String(), nullable=False, unique=True)
    bid = Column(String(),nullable = False, unique = False)

    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', backref='projects')


    def __repr__(self):
        return '<Project(%r, $r ,%r)>' % (
            self.wo_name, self.wo_code
        )


class Task(Base):
    __tablename__ = 'task'

    id = Column(Integer, primary_key=True, nullable=False)
    task_name = Column(String(), nullable=False, unique=False)
    mets_hours = Column(Float())
    tech_hours= Column(Float())
    snr_hours= Column(Float())

    wo_id = Column(Integer, ForeignKey('workorder.id'))
    workorder = relationship('WorkOrder', backref='workorders')

    def __repr__(self):
        return '<Project(%r, $r ,%r)>' % (
            self.task_name, self.task_hours)


class Staff(Base):
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True, nullable=False)
    first= Column(String(30),nullable = False)
    surname =  Column(String(30),nullable = False)
    jobstep = Column(Integer(),nullable=False)
    jobtype= Column(String(8),nullable=False)
    jdegsOBJ = Column(Integer(),nullable=False)
    oricle = Column(Integer(),nullable=False)
    active = Column(Boolean(),nullable=False)

    def __repr__(self):
        return '<Staff Member(%r, $r ,%r)>' % (
            self.first, self.surname, self.active)

class Timesheet(Base):
    __tablename__ = 'time'
    id = Column(Integer, primary_key=True, nullable=False)

    weekstarting = Column(Date())
    monday = Column(Float(),nullable=True)
    tuesday = Column(Float(),nullable=True)
    wednesday = Column(Float(),nullable=True)
    thursday = Column(Float(),nullable=True)
    friday = Column(Float(),nullable=True)
    saturday = Column(Float(),nullable=True)
    sunday = Column(Float(),nullable=True)

    jdeg_obj = Column(Integer(),nullable=True)
    jdeg_sub = Column(Integer(),nullable=True)

    staff_id = Column(Integer, ForeignKey('staff.id'))
    staff = relationship('Staff', backref='staffs')

    task_id = Column(Integer, ForeignKey('task.id'))
    task = relationship('Task', backref='tasks')

    wo_id = Column(Integer, ForeignKey('workorder.id'))
    wo = relationship('WorkOrder', backref='wos')

    bu_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', backref='bus')

class Bid(Base):
    __tablename__ = 'bid'

    id = Column(Integer, primary_key=True, nullable=False)
    #quote = Column(String(255), nullable=True, unique=False)
    #client = Column(String(255), nullable=True, unique=False)
    rev =  Column(String(255), nullable=True, unique=False)
    #date = Column(String(255), nullable=True, unique=False)
    scope = Column(String(255), nullable=True, unique=False)
    item = Column(String(255), nullable=True, unique=False)
    subDesc = Column(String(255), nullable=True, unique=False)
    desc = Column(String(255), nullable=True, unique=False)
    service = Column(String(255), nullable=True, unique=False)
    amount = Column(Float(), nullable=True, unique=False)
    cost = Column(Float(), nullable=True, unique=False)
    file = Column(String(255))
    date = Column(String(255))


    bid_id = Column(Integer, ForeignKey('bid_register.id'))
    bid= relationship('Bid_Register', backref='bids')

    def __repr__(self):
        return '<Bid %r %r>' % (
            self.quote, self.rev)

class Bid_Register(Base):
    __tablename__ = 'bid_register'
    id = Column(Integer, primary_key=True, nullable=False)
    bid_number = Column(String(255), nullable = False, unique=True)
    submit = Column(Integer)
    close = Column(Integer)
    client = Column(String(255))
    contact = Column(String(255))
    description = Column(String(255))
    mineral = Column(String(255))
    region = Column(String(255))
    go = Column(Integer)
    get= Column(Integer)
    margin = Column(Integer)
    status = Column(String(255))
    ms = Column(String(255))
    bd = Column(String(255))
    bid_file = Column(String(255))
    def __repr__(self):
        return '<Bid %r %r>' % (
            self.bid_number, self.client)


engine = create_engine('sqlite:///mets_data.db')
Base.metadata.create_all(engine)

