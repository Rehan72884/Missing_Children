from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Person(Base):
    __tablename__ = 'person'
    

    CNIC = Column(String(20), primary_key=True, autoincrement=False, nullable=False)
    P_Name = Column(String(50), nullable=False)
    P_Password = Column(String(50), nullable=False)
    P_Contact = Column(String(20), nullable=False)
    P_Address = Column(String(55))
    P_Image = Column(String(255))
    person_type = Column(String(255))
