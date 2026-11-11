from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
#from model.child_model import Child
#from model.police_model import Police
#from model.citizen_model import Citizen


Base = declarative_base()

class Found_Report(Base):
    __tablename__ = 'Found_Report'
    
    fr_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    f_loc_latitude = Column(Float)
    f_loc_longitude = Column(Float)
    found_date = Column(String(50), nullable=False)
    description = Column(String(20), nullable=False)
    current_status = Column(String(20), nullable=False)
    
    # Correct foreign key references
    C_ID = Column(Integer, ForeignKey('Child.C_ID'))
    child = relationship('Child',primaryjoin='Found_Report.C_ID == Child.C_ID', backref='Found_Report', lazy=True)
    
    CNIC = Column(Integer, ForeignKey('Person.CNIC'))
    person = relationship('Person',primaryjoin='Found_Report.CNIC == Person.CNIC', backref='Found_Report', lazy=True)
    
    P_ID = Column(Integer, ForeignKey('Police.P_ID'))
    police = relationship('Police', primaryjoin='Found_Report.P_ID == Police.P_ID', backref='Found_Report', lazy=True)
    
    S_ID = Column(Integer, ForeignKey('Shelter_Home.S_Id'))
    shelterhome = relationship('Shelter_Home', primaryjoin='Found_Report.S_ID == Shelter_Home.S_Id', backref='Found_Report', lazy=True)
    
class Person(Base):
    __tablename__ = 'Person'

    CNIC = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    P_NAME = Column(String(50), nullable=False)
    P_CONTACT = Column(String(50), nullable=False)
    P_ADDRESS = Column(String(50), nullable=False)
    P_Image = Column(String(50), nullable=False)
    person_type = Column(String(50), nullable=False)
    P_PASSWORD = Column(String(50), nullable=False)
    
   
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
    CONTACT = Column(String(50), nullable=False)
    cnic = Column(Integer, ForeignKey('Person.CNIC'))
    person = relationship('Person', backref='Police', lazy=True)
    
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
    type = Column(String(50))
    
class Shelter_Home(Base):
    __tablename__ = 'Shelter_Home'
    S_Id = Column(Integer, primary_key=True, autoincrement=False, nullable=False) 
    S_Name = Column(String(20), nullable=False)  
    Contact_Info= Column(String(20), nullable=False) 
    cnic = Column(Integer, ForeignKey('Person.CNIC'))
    person = relationship('Person', backref='Shelter_Home', lazy=True)

class policeNotification(Base):
    __tablename__ = 'policeNotification'
    
    pnid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)  # Changed autoincrement to True
    to_pid = Column(Integer, ForeignKey('Police.P_ID'))
    from_pid = Column(Integer, ForeignKey('Police.P_ID'))
    cid = Column(Integer, ForeignKey('Child.C_ID'))
    child = relationship('Child',primaryjoin='policeNotification.cid == Child.C_ID', backref='policeNotification', lazy=True)
    
    
    # Relationships
    to_police = relationship('Police', foreign_keys=[to_pid], backref='notifications_received', lazy=True)
    from_police = relationship('Police', foreign_keys=[from_pid], backref='notifications_sent', lazy=True)
class Notification(Base):
    __tablename__ = 'Notification'
    
    nid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)  # Changed autoincrement to True
    mid = Column(Integer, ForeignKey('Missing_Report.mr_id'))
    fid = Column(Integer, ForeignKey('Found_Report.fr_id'))
    status = Column(Integer)
    type = Column(String)

    # Relationships
    missingreport = relationship('Missing_Report', backref='notifications', lazy=True)
    foundreport = relationship('Found_Report', backref='notifications', lazy=True)
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
    

class ShelterHomeCoordinates(Base):
    __tablename__ = 'ShelterHomeCoordinates'
    SCoordinateID = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    Latitude = Column(Float, nullable=False)
    Longitude = Column(Float)
    S_ID = Column(Integer, ForeignKey('Shelter_Home.S_Id'))
    Shelter_Home = relationship('Shelter_Home',primaryjoin='ShelterHomeCoordinates.S_ID == Shelter_Home.S_Id', backref='Shelter_Home', lazy=True)


class missing_found_child(Base):
    __tablename__ = 'missing_found_child'
    Mfc_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    approval_date = Column(String)
    mr_id = Column(Integer, ForeignKey('Missing_Report.mr_id'))
    fr_id = Column(Integer, ForeignKey('Found_Report.fr_id'))
    missing_report = relationship('Missing_Report',primaryjoin='Missing_Report.mr_id == missing_found_child.mr_id', backref='missing_found_child', lazy=True)
    found_report = relationship('Found_Report',primaryjoin='Found_Report.fr_id == missing_found_child.fr_id', backref='missing_found_child', lazy=True)
    

class Adapative_Request(Base):
    __tablename__ = 'Adapative_Request'
    
    Ar_Id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    request_date = Column(String(50), nullable=False)
    Reason_Of_Adoption = Column(String(20), nullable=False)
    Ar_Status = Column(String(20), nullable=False)
    Martial_Status = Column(String)
    Income = Column(Integer)
    
    # Correct foreign key references
    CID = Column(Integer, ForeignKey('Child.C_ID'))
    child = relationship('Child',primaryjoin='Adapative_Request.CID == Child.C_ID', backref='Adapative_Request', lazy=True)
    
    CNIC = Column(Integer, ForeignKey('Person.CNIC'))
    person = relationship('Person', backref='Adapative_Request', lazy=True)
    
    S_ID = Column(Integer, ForeignKey('Shelter_Home.S_Id'))
    Shelter_Home = relationship('Shelter_Home',primaryjoin='Adapative_Request.S_ID == Shelter_Home.S_Id', backref='Adapative_Request', lazy=True)

class Foster_Request(Base):
    __tablename__ = 'Foster_Request'
    
    foster_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    request_date = Column(String(50), nullable=False)
    approved_date = Column(String(50), nullable=False)
    
    status = Column(String(20), nullable=False)
    
    
    # Correct foreign key references
    CID = Column(Integer, ForeignKey('Child.C_ID'))
    child = relationship('Child',primaryjoin='Foster_Request.CID == Child.C_ID', backref='Foster_Request', lazy=True)
    
    CNIC = Column(Integer, ForeignKey('Person.CNIC'))
    person = relationship('Person', backref='Foster_Request', lazy=True)
    
    S_ID = Column(Integer, ForeignKey('Shelter_Home.S_Id'))
    Shelter_Home = relationship('Shelter_Home',primaryjoin='Foster_Request.S_ID == Shelter_Home.S_Id', backref='Foster_Request', lazy=True)


class Return_Foster_Child(Base):
    __tablename__ = 'Return_Foster_Child'
    rid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    return_date = Column(String(50), nullable=False)
    
    
    
    # Correct foreign key references
    CID = Column(Integer, ForeignKey('Child.C_ID'))
    child = relationship('Child',primaryjoin='Return_Foster_Child.CID == Child.C_ID', backref='Return_Foster_Child', lazy=True)
    
    CNIC = Column(Integer, ForeignKey('Person.CNIC'))
    person = relationship('Person', backref='Return_Foster_Child', lazy=True)
    
    to_shelter = Column(Integer, ForeignKey('Shelter_Home.S_Id'))
    Shelter_Home = relationship('Shelter_Home',primaryjoin='Return_Foster_Child.to_shelter == Shelter_Home.S_Id', backref='Return_Foster_Child', lazy=True)
    
    from_shelter = Column(Integer, ForeignKey('Shelter_Home.S_Id'))
    Shelter_Home = relationship('Shelter_Home',primaryjoin='Return_Foster_Child.from_shelter == Shelter_Home.S_Id', backref='Return_Foster_Child', lazy=True)


class EidiNotification(Base):
    __tablename__ = 'eidinotification'
    enid = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    status = Column(Integer)
    cnic = Column(Integer, ForeignKey('Person.CNIC'))
    ar_id = Column(Integer, ForeignKey('Adapative_Request.Ar_Id'))
    sid = Column(Integer, ForeignKey('Shelter_Home.S_Id'))
    
    adapative_request = relationship('Adapative_Request',primaryjoin='Adapative_Request.Ar_Id == EidiNotification.ar_id', backref='EidiNotification', lazy=True)
    person = relationship('Person',primaryjoin='Person.CNIC == EidiNotification.cnic', backref='EidiNotification', lazy=True)
    shelter = relationship('Shelter_Home',primaryjoin='Shelter_Home.S_Id == EidiNotification.sid', backref='EidiNotification', lazy=True)
    

