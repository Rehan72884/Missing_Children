from sqlalchemy.orm import aliased
from sqlalchemy import func, cast, Date
import sqlalchemy
from flask import Flask,jsonify
from sqlalchemy import distinct
from datetime import datetime, timedelta
import DBHandler as db
from model.Model import Child, Found_Report, Shelter_Home, Person, Adaptive_Request
from model.adapative_model import Adapative_Request
from sqlalchemy.sql import func
from model.Model import Image
from model import citizen_found_report_model
import face_recognition

def insert_adaptive_child(cid,cnic,sid,ar_status,reason_of_adoption,request_date,martial_status,income):
    try:
        session = db.return_session()
        req=citizen_found_report_model.Adapative_Request(CID=cid,CNIC=cnic,S_ID=sid,request_date=request_date,
                              Reason_Of_Adoption=reason_of_adoption,Ar_Status=ar_status, Martial_Status=martial_status,
                             Income = income )
        session.add(req)
        session.commit()
        return {"message": "Adaptive Request added successfully"}, 200
        

    except Exception as e:
        print(e)
        return {'error': str(e)}, 500
    
def insert_foster_child(cid,cnic,sid,ar_status,request_date):
    try:
        session = db.return_session()
        req=citizen_found_report_model.Foster_Request(CID=cid,CNIC=cnic,S_ID=sid,request_date=request_date,
                             status=ar_status)
        session.add(req)
        session.commit()
        return {"message": "Adaptive Request added successfully"}, 200
        

    except Exception as e:
        print(e)
        return {'error': str(e)}, 500
    
    
    
def return_foster_child(cid,cnic,to_sid,from_sid,request_date):
    try:
        session = db.return_session()
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        
        req=citizen_found_report_model.Return_Foster_Child(CID=cid,CNIC=cnic,to_shelter=to_sid,from_shelter=from_sid,
                             return_date=request_date)
        session.add(req)
        session.commit()
        report = session.query(found_report_alias).filter(found_report_alias.C_ID==cid).one_or_none()
        
        # Check if the report exists
        if report:
            # Update the current status
            report.current_status = 'submitted'
            session.add(report)
            session.commit()
        return {"message": "Return To Shelter Request added successfully"}, 200
        

    except Exception as e:
        print(e)
        return {'error': str(e)}, 500
def get_adaptive_child_with_image(img):
    try:
        session = db.return_session()
        req = citizen_found_report_model.Image(Image=img, type='adoption')
        session.add(req)
        current_date = datetime.utcnow().date()

        # Calculate the threshold date (6 months before the current date)
        threshold_date = current_date - timedelta(days=6 * 30)  # Approximation for 6 months

        session = db.return_session()

        child_alias = aliased(citizen_found_report_model.Child)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        image_alias = aliased(citizen_found_report_model.Image)
        shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)

        query = (
            session.query(
                child_alias.FATHER_NAME.label('Father_Name'),
                child_alias.C_ID.label('C_Id'),
                child_alias.CNAME.label('CName'),
                child_alias.AGE.label('Age'),
                child_alias.GENDER.label('Gender'),
                found_report_alias.f_loc_latitude.label('Found_Location_Latitude'),
                found_report_alias.f_loc_longitude.label('Found_Location_Longitude'),
                found_report_alias.found_date.label('Found_Date'),
                found_report_alias.description.label('Description'),
                func.MAX(image_alias.Image).label('Image'),
                shelter_home_alias.S_Name.label('Shelter_Location'),
                shelter_home_alias.S_Id.label('S_Id')
            )
            .join(found_report_alias, child_alias.C_ID == found_report_alias.C_ID)
            .join(image_alias, child_alias.C_ID == image_alias.C_ID)
            .join(shelter_home_alias, found_report_alias.S_ID == shelter_home_alias.S_Id)
            .filter(found_report_alias.found_date <= threshold_date)  # Filter for threshold date
            .group_by(
                child_alias.FATHER_NAME,
                child_alias.C_ID,
                child_alias.CNAME,
                child_alias.AGE,
                child_alias.GENDER,
                found_report_alias.f_loc_latitude,
                found_report_alias.f_loc_longitude,
                found_report_alias.found_date,
                found_report_alias.description,
                shelter_home_alias.S_Name,
                shelter_home_alias.S_Id,
            )
            .all()
        )

        results = [
            {
                'Father_Name': result.Father_Name,
                'C_Id': result.C_Id,
                'CName': result.CName,
                'Age': result.Age,
                'Gender': result.Gender,
                'Found_Location_Latitude': result.Found_Location_Latitude,
                'Found_Location_Longitude': result.Found_Location_Longitude,
                'S_Id': result.S_Id,
                'Found_Date': result.Found_Date,
                'Description': result.Description,
                'Image': result.Image,
                'Shelter_Location': result.Shelter_Location
            }
            for result in query
        ]  # Assuming this returns a list of dictionaries or objects with image and cid
        print(results)
        list_of_child_images_and_cid = []

        for child in results:
            image = child['Image']  # Or use child.image if it's an object
            cid = child['C_Id'] # Or use child.cid if it's an object
            list_of_child_images_and_cid.append((image, cid))
        matching_cids = match_person(
       {child[0]: child[1] for child in list_of_child_images_and_cid},  # Accessing elements by index
       img,
       0.7
       )
        
      
        
        matching_children_details = [
            child for child in results if child.get('cid') in matching_cids
        ]
        
        session.commit()
        return {"matching_children": matching_cids}, 200

    except Exception as e:
        print(e)
        return {'error': str(e)}, 500



def match_person(image_paths_with_cids, target_image_path, threshold):
    target_image = face_recognition.load_image_file(target_image_path)
    target_encodings = face_recognition.face_encodings(target_image)
    
    if len(target_encodings) == 0:
        print("No faces found in the target image.")
        return []  # Return an empty list if no faces are found in the target image
    
    target_encoding = target_encodings[0]
    matching_cids = []
    
    for image_path, cid in image_paths_with_cids.items():
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        
        if len(face_encodings) > 0:
            for face_encoding in face_encodings:
                distance = face_recognition.face_distance([target_encoding], face_encoding)[0]
                if distance < threshold:
                    matching_cids.append(cid)
                    break
    
    return matching_cids

def get_own_adopted_childs(cnic):
    try:
        session = db.return_session()
        Foster_Request_alias = aliased(citizen_found_report_model.Foster_Request)
        child_alias = aliased(citizen_found_report_model.Child)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)
        image_alias = aliased(citizen_found_report_model.Image)
        person_alias = aliased(citizen_found_report_model.Person)

        subquery = (
            session.query(
                child_alias.C_ID,
                func.MIN(image_alias.Image).label('Image')
            )
            .join(Foster_Request_alias, child_alias.C_ID == Foster_Request_alias.CID)
            .join(image_alias, image_alias.C_ID == child_alias.C_ID)
            .group_by(child_alias.C_ID)
            .subquery()
        )

        query = (
            session.query(
                child_alias.C_ID,
                child_alias.CNAME,
                child_alias.AGE,
                child_alias.GENDER,
                found_report_alias.f_loc_latitude,
                found_report_alias.f_loc_longitude,
                shelter_home_alias.S_Name,
                Foster_Request_alias.request_date,
                Foster_Request_alias.status,
                Foster_Request_alias.foster_id,
                person_alias.P_NAME,
                subquery.c.Image.label('Image'),
                person_alias.P_CONTACT,
               
                person_alias.CNIC,
                shelter_home_alias.S_Id,
            )
            .join(found_report_alias, child_alias.C_ID == found_report_alias.C_ID)
            .join(Foster_Request_alias, child_alias.C_ID == Foster_Request_alias.CID)
            .join(shelter_home_alias, Foster_Request_alias.S_ID == shelter_home_alias.S_Id)
            .join(person_alias, person_alias.CNIC == Foster_Request_alias.CNIC)
            .outerjoin(subquery, child_alias.C_ID == subquery.c.C_ID)
            .filter(found_report_alias.current_status == 'Adopted')
            .where(Foster_Request_alias.CNIC == cnic)
            
            .distinct()
        )

        results = query.all()

        formatted_results = [
            {
                'C_Id': row.C_ID,
                'CName': row.CNAME,
                'Age': row.AGE,
                'Gender': row.GENDER,
                'Found_Location_Latitude': row.f_loc_latitude,
                'Found_Location_Longitude': row.f_loc_longitude,
                'Shelter_Location': row.S_Name,
                
                'Request_Date': row.request_date,  # Convert datetime to string
                'Ar_Status': row.status,
                'P_Name': row.P_NAME,
                'Image': row.Image,
                'P_Contact': row.P_CONTACT,
                'foster_id':row.foster_id,
                
                'cnic':row.CNIC,
                'sid':row.S_Id
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_new_adoptable_child(cids):
    try:
        session = db.return_session()

        child_alias = aliased(citizen_found_report_model.Child)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        image_alias = aliased(citizen_found_report_model.Image)
        shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)
        
        query = (
            session.query(
                child_alias.FATHER_NAME.label('Father_Name'),
                child_alias.C_ID.label('C_Id'),
                child_alias.CNAME.label('CName'),
                child_alias.AGE.label('Age'),
                child_alias.GENDER.label('Gender'),
                found_report_alias.f_loc_latitude.label('Found_Location_Latitude'),
                found_report_alias.f_loc_longitude.label('Found_Location_Longitude'),
                found_report_alias.found_date.label('Found_Date'),
                found_report_alias.description.label('Description'),
                func.MAX(image_alias.Image).label('Image'),
                shelter_home_alias.S_Name.label('Shelter_Location'),
                shelter_home_alias.S_Id.label('S_Id')
            )
            .filter(child_alias.C_ID.in_(cids))  # Filter by the provided child IDs
            .join(found_report_alias, child_alias.C_ID == found_report_alias.C_ID)
            .join(image_alias, child_alias.C_ID == image_alias.C_ID)
            .join(shelter_home_alias, found_report_alias.S_ID == shelter_home_alias.S_Id)
            .group_by(
                child_alias.FATHER_NAME,
                child_alias.C_ID,
                child_alias.CNAME,
                child_alias.AGE,
                child_alias.GENDER,
                found_report_alias.f_loc_latitude,
                found_report_alias.f_loc_longitude,
                found_report_alias.found_date,
                found_report_alias.description,
                shelter_home_alias.S_Name,
                shelter_home_alias.S_Id,
            )
            .all()
        )

        results = [
            {
                'Father_Name': result.Father_Name,
                'C_Id': result.C_Id,
                'CName': result.CName,
                'Age': result.Age,
                'Gender': result.Gender,
                'Found_Location_Latitude': result.Found_Location_Latitude,
                'Found_Location_Longitude': result.Found_Location_Longitude,
                'S_Id': result.S_Id,
                'Found_Date': result.Found_Date.strftime('%Y-%m-%d %H:%M:%S'),  # Format date if needed
                'Description': result.Description,
                'Image': result.Image,  # Assuming 'Image' is a URL or file path
                'Shelter_Location': result.Shelter_Location
            }
            for result in query
        ]

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_adoptable_child():
    try:
        # Get the current date
        current_date = datetime.utcnow().date()

        # Calculate the threshold date (6 months before the current date)
        threshold_date = current_date - timedelta(days=6 * 30)  # Approximation for 6 months

        session = db.return_session()

        child_alias = aliased(citizen_found_report_model.Child)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        image_alias = aliased(citizen_found_report_model.Image)
        shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)

        query = (
            session.query(
                child_alias.FATHER_NAME.label('Father_Name'),
                child_alias.C_ID.label('C_Id'),
                child_alias.CNAME.label('CName'),
                child_alias.AGE.label('Age'),
                child_alias.GENDER.label('Gender'),
                found_report_alias.f_loc_latitude.label('Found_Location_Latitude'),
                found_report_alias.f_loc_longitude.label('Found_Location_Longitude'),
                found_report_alias.found_date.label('Found_Date'),
                found_report_alias.description.label('Description'),
                func.MAX(image_alias.Image).label('Image'),
                shelter_home_alias.S_Name.label('Shelter_Location'),
                shelter_home_alias.S_Id.label('S_Id')
            )
            .join(found_report_alias, child_alias.C_ID == found_report_alias.C_ID)
            .join(image_alias, child_alias.C_ID == image_alias.C_ID)
            .join(shelter_home_alias, found_report_alias.S_ID == shelter_home_alias.S_Id)
            .filter(found_report_alias.found_date <= threshold_date) 
            .filter(found_report_alias.current_status == 'submitted')# Filter for threshold date
            .group_by(
                child_alias.FATHER_NAME,
                child_alias.C_ID,
                child_alias.CNAME,
                child_alias.AGE,
                child_alias.GENDER,
                found_report_alias.f_loc_latitude,
                found_report_alias.f_loc_longitude,
                found_report_alias.found_date,
                found_report_alias.description,
                shelter_home_alias.S_Name,
                shelter_home_alias.S_Id,
            )
            .all()
        )

        results = [
            {
                'Father_Name': result.Father_Name,
                'C_Id': result.C_Id,
                'CName': result.CName,
                'Age': result.Age,
                'Gender': result.Gender,
                'Found_Location_Latitude': result.Found_Location_Latitude,
                'Found_Location_Longitude': result.Found_Location_Longitude,
                'S_Id': result.S_Id,
                'Found_Date': result.Found_Date,
                'Description': result.Description,
                'Image': result.Image,
                'Shelter_Location': result.Shelter_Location
            }
            for result in query
        ]

        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def search_adoptable_child(value):
    try:
        session = db.return_session()
        child_alias = aliased(Child)
        found_report_alias = aliased(Found_Report)

        query = (
            session.query(
                Child.Father_Name,
                Child.CName,
                Child.Age,
                Child.Gender,
                Found_Report.Found_Location,
                Found_Report.Found_Date,
                Found_Report.Description
            )
            .join(Found_Report, Child.C_Id == Found_Report.C_Id)
            .filter(
                (Child.Father_Name.ilike(f"%{value}%")) |
                (Child.CName.ilike(f"%{value}%")) |
                (Child.Age.ilike(f"%{value}%")) |
                (Child.Gender.ilike(f"%{value}%")) |
                (Found_Report.Found_Location.ilike(f"%{value}%")) |
                (Found_Report.Description.ilike(f"%{value}%")),
                Found_Report.Found_Date < datetime(2023, 1, 1)  # Filter condition
            )
            .all()
        )
       
        results = [
            {
                'Father_Name': result.Father_Name,
                'CName': result.CName,
                'Age': result.Age,
                'Gender': result.Gender,
                'Found_Location': result.Found_Location,
                'Found_Date': result.Found_Date,
                'Found_Description': result.Description
            }
            for result in query
            if value.lower() in [result.Father_Name.lower(), result.CName.lower(), str(result.Age).lower(), result.Gender.lower(), result.Found_Location.lower()]
        ]

        print(results)
        return jsonify(results)

    except Exception as e:
        return {'error': str(e)}, 500
  
def get_adopted_childs():
    try:
        session = db.return_session()
        child_alias = aliased(Child)
        found_report_alias = aliased(Found_Report)
        shelter_home_alias = aliased(Shelter_Home)
        Adapative_Request_alias= aliased(Adapative_Request)
        Person_alias = aliased(Person)
       

        query = (
          session.query(
           Child.C_Id,
           Child.CName,
           Child.Age,
           Child.Gender,
           func.min(Found_Report.Found_Location).label('Found_Location'),
           Shelter_Home.Shelter_Location
        )
         .join(Adapative_Request_alias, Child.C_Id == Adapative_Request_alias.CID, isouter=False)
         .join(shelter_home_alias, Adapative_Request_alias.S_Id == shelter_home_alias.S_Id)
         .join(Person_alias, Adapative_Request_alias.CNIC == Person_alias.CNIC)
         .group_by(
          Child.C_Id,
          Child.CName,
          Child.Age,
          Child.Gender,
          Shelter_Home.Shelter_Location
        )
        )      


        results = query.all()

        # Convert Row objects to dictionaries
        serialized_results = [
            {
                'C_ID': result.C_Id,
                'CName': result.CName,
                'Age': result.Age,
                'Gender': result.Gender,
                'Found_Location': result.Found_Location,
                'Shelter_Location': result.Shelter_Location
            }
            for result in results
        ]

        return jsonify(serialized_results)

    except Exception as e:
        return {'error': str(e)}, 500


def search_adopted_childs(text):
    try:
        session = db.return_session()
        child_alias = aliased(Child)
        adaptive_request_alias = aliased(Adaptive_Request)
        shelter_home_alias = aliased(Shelter_Home)
        Adapative_Request_alias= aliased(Adapative_Request)
        Person_alias = aliased(Person)

        query = (
           session.query(
        Child.C_Id,
        Child.CName,
        Child.Age,
        Child.Gender,
        Adaptive_Request.Ar_Status,
        func.min(Adaptive_Request.Reason_Of_Adoption).label('Reason_Of_Adoption'),
    )
    .join(Adapative_Request_alias, Child.C_Id == Adapative_Request_alias.CID, isouter=False)
    .join(shelter_home_alias, Adapative_Request_alias.S_Id == shelter_home_alias.S_Id)
    .join(Person_alias, Adapative_Request_alias.CNIC == Person_alias.CNIC)
    .group_by(
        Child.C_Id,
        Child.CName,
        Child.Age,
        Child.Gender,
        Adaptive_Request.Ar_Status,
        Adaptive_Request.Reason_Of_Adoption
    )
            .filter(
                (Child.Father_Name.ilike(f"%{text}%")) |
                (Child.CName.ilike(f"%{text}%")) |
                (Child.Age.ilike(f"%{text}%")) |
                (Child.Gender.ilike(f"%{text}%")) |
                (Adaptive_Request.Ar_Status.ilike(f"%{text}%")) |
                (Adaptive_Request.Reason_Of_Adoption.ilike(f"%{text}%")) |
                (Person.P_Name.ilike(f"%{text}%"))  # Include search in person name
            )
            .all()
        )

        results = [
            {
                'CID': result.C_Id,
                'CName': result.CName,
                'Age': result.Age,
                'Gender': result.Gender,
                'Ar_Status': result.Ar_Status,
                'Reason_Of_Adoption': result.Reason_Of_Adoption
                
            }
            for result in query
        ]

        print(results)
        return jsonify(results)

    except Exception as e:
        return {'error': str(e)}, 500






