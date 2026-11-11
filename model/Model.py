from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Person(Base):
    __tablename__ = 'Person'

    CNIC = Column(String, primary_key=True)
    P_Name = Column(String(90))
    P_Password = Column(String(70))
    P_Contact = Column(String(90))
    P_Address = Column(String(90))
    P_Image = Column(String(90))
    adaptive_person = relationship("Adaptive_Person", back_populates="person")
    adaptive_request = relationship('Adaptive_Request', back_populates='person')
    citizen = relationship('Citizen', back_populates='person')
    found_report = relationship('Found_Report', back_populates='person')
    missing_report = relationship('Missing_Report', back_populates='person')  # Added this line


class Adaptive_Person(Base):
    __tablename__ = 'Adapative_Person'

    CNIC = Column(String, ForeignKey('Person.CNIC'), primary_key=True)
    Income = Column(Integer)
    Martial_Status = Column(String(90))
    person = relationship("Person", back_populates="adaptive_person")

class Child(Base):
    __tablename__ = 'Child'

    C_Id = Column(Integer, primary_key=True)
    CName = Column(String(80), nullable=False)
    Age = Column(Integer, nullable=False)
    Gender = Column(String(40), nullable=False)
    Father_Name = Column(String(90))
    Father_Contact = Column(String(50))
    Ethenicity = Column(String(90))
    adaptive_request = relationship('Adaptive_Request', back_populates='child')
    shelter_home = relationship('Shelter_Home', back_populates='child')
    found_report = relationship('Found_Report', back_populates='child')
    image = relationship('Image', back_populates='child')
    missing_report = relationship('Missing_Report', back_populates='child')

class Police(Base):
    __tablename__ = 'Police'

    P_Id = Column(Integer, primary_key=True)
    P_Name = Column(String(40))
    Rank = Column(String(40))
    Station_Address = Column(String(100))
    Contact = Column(String(70))
    missing_report = relationship('Missing_Report', back_populates='police')  # Added this line



class Shelter_Home(Base):
    __tablename__ = 'Shelter_Home'

    S_Id = Column(Integer, primary_key=True)
    S_Name = Column(String(70))
    Shelter_Location = Column(String(70))
    Contact_Info = Column(String(90))
    C_Id = Column(Integer, ForeignKey('Child.C_Id'))
    adaptive_request = relationship('Adaptive_Request', back_populates='shelter_home')
    child = relationship('Child', back_populates='shelter_home')
    found_report = relationship('Found_Report', back_populates='shelter_home')  # Added this line


class Adaptive_Request(Base):
    __tablename__ = 'Adapative_Request'

    CID = Column(Integer, ForeignKey('Child.C_Id'), primary_key=True)
    CNIC = Column(String, ForeignKey('Person.CNIC'), primary_key=True)
    S_Id = Column(Integer, ForeignKey('Shelter_Home.S_Id'), primary_key=True)
    Ar_Status = Column(String(90))
    Reason_Of_Adoption = Column(String(90))
    Ethenicity = Column(String(90))

    child = relationship('Child', back_populates='adaptive_request')
    person = relationship('Person', back_populates='adaptive_request')
    shelter_home = relationship('Shelter_Home', back_populates='adaptive_request')


class Citizen(Base):
    __tablename__ = 'Citizen'

    CNIC = Column(String, ForeignKey('Person.CNIC'), primary_key=True)
    Relation = Column(String(89))
    person = relationship('Person', back_populates='citizen')


class Found_Report(Base):
    __tablename__ = 'Found_Report'

    Fr_Id = Column(Integer, primary_key=True)
    Found_Location = Column(String(40))
    Found_Date = Column(String(40))
    Description = Column(String(40))
    Current_Status = Column(String(40))
    C_Id = Column(Integer, ForeignKey('Child.C_Id'))
    CNIC = Column(String, ForeignKey('Person.CNIC'))
    P_Id = Column(Integer, ForeignKey('Police.P_Id'))
    S_Id = Column(Integer, ForeignKey('Shelter_Home.S_Id'))

    child = relationship('Child', back_populates='found_report')
    person = relationship('Person', back_populates='found_report')
    shelter_home = relationship('Shelter_Home', back_populates='found_report')


class Image(Base):
    __tablename__ = 'Image'

    C_Id = Column(Integer, ForeignKey('Child.C_Id'), primary_key=True)
    Image = Column(String(900))
    child = relationship('Child', back_populates='image')


class Missing_Report(Base):
    __tablename__ = 'Missing_Report'

    Mr_Id = Column(Integer, primary_key=True)
    Missing_Location = Column(String(40))
    Missing_Date = Column(String(40))
    Missing_Time = Column(String(40))
    Description = Column(String(70))
    Current_Status = Column(String(40))
    C_Id = Column(Integer, ForeignKey('Child.C_Id'))
    CNIC = Column(String, ForeignKey('Person.CNIC'))
    P_Id = Column(Integer, ForeignKey('Police.P_Id'))

    child = relationship('Child', back_populates='missing_report')
    person = relationship('Person', back_populates='missing_report')
    police = relationship('Police', back_populates='missing_report')