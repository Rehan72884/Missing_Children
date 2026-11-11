from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
# from model.police_model import Police
#from model.citizen_model import Citizen


Base = declarative_base()

class Missing_Report(Base):
    __tablename__ = 'Missing_Report'
    
    mr_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    m_loc_latitude = Column(String(50), nullable=False)
    m_loc_longitude = Column(String(50), nullable=False)
    missing_date = Column(String(50), nullable=False)
    Missing_Time = Column(String(50), nullable=False)
    description = Column(String(20), nullable=False)
    current_status = Column(String(20), nullable=False)
    Relation = Column(String(20))
    # Correct foreign key references
    # C_Id = Column(Integer, ForeignKey(Child,'C_Id'))
    # child = relationship('Child',primaryjoin='Missing_Report.C_Id == Child.C_Id', backref='Missing_Report', lazy=True)
    
    C_ID = Column(Integer, ForeignKey('Child.C_ID'))
    child = relationship('Child',primaryjoin='Missing_Report.C_ID == Child.C_ID', backref='Missing_Report', lazy=True)
    
    CNIC = Column(Integer, ForeignKey('Person.CNIC'))
    person = relationship('Person', backref='Missing_Report', lazy=True)
    
    P_ID = Column(Integer, ForeignKey('Police.P_ID'))
    police = relationship('Police', primaryjoin='Missing_Report.P_ID == Police.P_ID', backref='Missing_Report', lazy=True)
    

class Person(Base):
    __tablename__ = 'Person'

    CNIC = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    P_NAME = Column(String(50), nullable=False)
    P_ADDRESS = Column(String(50))
    P_CONTACT = Column(String(50)) 
    
   
class Child(Base):
    __tablename__ = 'Child'

    C_ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    CNAME = Column(String(50), nullable=False)
    AGE = Column(Integer, nullable=False)
    GENDER = Column(String(20), nullable=False)
    FATHER_NAME = Column(String(20), nullable=False)
    FATHER_CONTACT = Column(String(20), nullable=False)
    Ethenicity= Column(String(20), nullable=False) 

class Police(Base):
    __tablename__ = 'Police'
    
    P_ID = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    STATION_ADDRESS = Column(String(50), nullable=False)
    
class PoliceCoordinates(Base):
    __tablename__ = 'PoliceCoordinates'
    
    CoordinateID = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    Latitude = Column(Float, nullable=False)
    Longitude = Column(Float) 
    P_ID = Column(Integer, ForeignKey('Police.P_ID'))
    police = relationship('Police',primaryjoin='PoliceCoordinates.P_ID == Police.P_ID', backref='Police', lazy=True)
    
class Image(Base):
    __tablename__ = 'Image'
    id= Column(Integer, primary_key=True, autoincrement=True, nullable=False) 
    C_ID = Column(Integer, ForeignKey('Child.C_ID'))
    child = relationship('Child',primaryjoin='Image.C_ID == Child.C_ID', backref='Image', lazy=True)
    Image = Column(String(450), nullable=False)
    type = Column(String)

# class Found_Report(Base):
#     __tablename__ = 'Found_Report'
    
#     fr_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
#     f_loc_latitude = Column(Float)
#     f_loc_longitude = Column(Float)
#     found_date = Column(String(50), nullable=False)
#     description = Column(String(20), nullable=False)
#     current_status = Column(String(20), nullable=False)
    
#     # Correct foreign key references
#     C_ID = Column(Integer, ForeignKey('Child.C_ID'))
#     child = relationship('Child',primaryjoin='Found_Report.C_ID == Child.C_ID', backref='Found_Report', lazy=True)
    
#     CNIC = Column(Integer, ForeignKey('Person.CNIC'))
#     person = relationship('Person',primaryjoin='Found_Report.CNIC == Person.CNIC', backref='Found_Report', lazy=True)
    
#     P_ID = Column(Integer, ForeignKey('Police.P_ID'))
#     police = relationship('Police', primaryjoin='Found_Report.P_ID == Police.P_ID', backref='Found_Report', lazy=True)
    
#     S_ID = Column(Integer, ForeignKey('Shelter_Home.S_Id'))
#     shelterhome = relationship('Shelter_Home', primaryjoin='Found_Report.S_ID == Shelter_Home.S_Id', backref='Found_Report', lazy=True)
    
# class missing_found_child(Base):
#     __tablename__ = 'missing_found_child'
#     Mfc_id = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
#     approval_date = Column(String)
#     mr_id = Column(Integer, ForeignKey('Missing_Report.mr_id'))
#     fr_id = Column(Integer, ForeignKey('Found_Report.fr_id'))
#     missing_report = relationship('Missing_Report',primaryjoin='Missing_Report.mr_id == missing_found_child.mr_id', backref='missing_found_child', lazy=True)
#     found_report = relationship('Found_Report',primaryjoin='Found_Report.fr_id == missing_found_child.fr_id', backref='missing_found_child', lazy=True)