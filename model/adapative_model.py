from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Adapative_Request(Base):
    __tablename__ = 'Adapative_Request'
    
    Ar_Id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    request_date = Column(String(50), nullable=False)
    Reason_Of_Adoption = Column(String(20), nullable=False)
    Ar_Status = Column(String(20), nullable=False)
    Martial_Status = Column(String)
    
    # Correct foreign key references
    CID = Column(Integer, ForeignKey('Child.C_Id'))
    child = relationship('Child',primaryjoin='Adapative_Request.CID == Child.C_Id', backref='Adapative_Request', lazy=True)
    
    CNIC = Column(Integer, ForeignKey('Citizen.CNIC'))
    person = relationship('Citizen', backref='Adapative_Request', lazy=True)
    
    S_Id = Column(Integer, ForeignKey('Shelter_Home.S_Id'))
    shelterhome = relationship('Shelter_Home', primaryjoin='Adapative_Request.S_Id == Shelter_Home.S_Id', backref='Found_Report', lazy=True)
    
class Child(Base):
    __tablename__ = 'Child'

    C_Id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    CName = Column(String(50), nullable=False)
    Age = Column(String(50), nullable=False)
    Gender= Column(String(20), nullable=False)
    Father_Name = Column(String(20), nullable=True)
    Father_Contact = Column(String(20), nullable=True)
    Ethenicity= Column(String(20), nullable=True) 
    
class Shelter_Home(Base):
    __tablename__ = 'Shelter_Home'
    S_Id = Column(Integer, primary_key=True, autoincrement=False, nullable=False) 
    S_Name = Column(String(20), nullable=False) 
    Shelter_Location = Column(String(20), nullable=False) 
    Contact_Info= Column(String(20), nullable=False) 
    C_Id = Column(Integer, ForeignKey('Child.C_Id'))
    child = relationship('Child',primaryjoin='Shelter_Home.C_Id == Child.C_Id', backref='Shelter_Home', lazy=True)
    
class Citizen(Base):
    __tablename__ = 'Citizen'

    CNIC = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    Relation = Column(String(50), nullable=False)
