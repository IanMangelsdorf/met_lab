from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float, Date
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from timedata import Project,WorkOrder



Base = declarative_base()

metadata = MetaData()





class Sample(Base):
    __tablename__ = 'sample'
    id = Column(Integer, primary_key=True, nullable=False)
    name= Column(String(255), nullable=True, unique=True)
    barcode = Column(String(255), nullable=False, unique=True)
    test = Column(String(255), nullable = True,unique = False)
    project_id = Column(Integer, ForeignKey('project.id'))
    xrf_file = Column(String(255),nullable=True,unique=False)
    xrf_date =Column(String(20), nullable=True, unique=False)
    source = Column(String(255))
    test_no = Column(String(255))
    lower_size = Column(String(255))
    upper_size = Column(String(255))
    lower_sg = Column(String(10))
    upper_sg= Column(String(10))
    spare = Column(String(10))
    project = relationship('Project', backref='projects')

    def __repr__(self):
        return '<Sample %r, %r' % (
            self.name, self.barcode
        )

class XRF(Base):
    __tablename__ = 'xrf'

    id = Column(Integer, primary_key=True,nullable=False)
    method = Column(String(25), nullable=True, unique=False)
    unit = Column(String(10), nullable=True, unique=False)
    detection = Column(String(), nullable=True, unique=False)
    element= Column(String(10), nullable=True, unique=False)
    value = Column(String, nullable=True, unique=False)
    report_order = Column(Integer)

    sample_id = Column(Integer, ForeignKey('sample.id'))

    sample = relationship('Sample', backref='samples')



    def __repr__(self):
        return '<Sample %r, %r, %r>' % (
            self.sample, self.element, self.value
        )

class Source(Base):

    __tablename__='source'
    id = Column(Integer, primary_key=True,nullable=False)
    search = Column(String(25), nullable=False, unique=False)
    final = Column(String(25), nullable=False, unique=False)

class PSD(Base):
    __tablename__ = 'psd'
    id = Column(Integer, primary_key=True,nullable=False)
    test_no = Column(String(255), nullable = True,unique = False)
    fraction = Column(String(255))
    feed = Column(String(255))
    cum_passing =  Column(String(255))

    test_id = Column(Integer, ForeignKey('test.id'))
    test = relationship('Test', backref='tests')

    def __repr__(self):
        return '<Sample %r, %r, %r>' % (
            self.test_no, self.fraction, self.cum_passing
        )

class Test(Base):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True, nullable=False)
    test_name = Column(String(255), nullable=True, unique=True)
    test = Column(String(255), nullable=True, unique=False)


    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', backref='projects1')

    def __repr__(self):
        return '<Test %r>' % (
            self.test_name
        )





class Drum(Base):
    __tablename__ = 'drum'
    id = Column(Integer, primary_key=True, nullable=False)
    container_name = Column(String(), nullable=False, unique=False)

    location_row = Column(Integer())
    location_bay = Column(Integer())
    location_slot = Column(String(1))
    location_level = Column(Integer())

    wo_id = Column(Integer, ForeignKey('workorder.id'))
    workorder = relationship('WorkOrder', backref='workorders')


engine = create_engine('sqlite:///mets_data.db')
Base.metadata.create_all(engine)

