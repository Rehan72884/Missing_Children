from sqlalchemy import func
from sqlalchemy.orm import aliased, Session, class_mapper
from flask import Flask,jsonify
import DBHandler as db
from model.Model1 import Child, Person, Police, Found_Report, Shelter_Home,Adaptive_Request,Image
from model import citizen_found_report_model


from sqlalchemy.orm import aliased

def getfoundrequesteidi(cnic):
    try:
        session = db.return_session()

        child_alias = aliased(citizen_found_report_model.Child)
        person_alias = aliased(citizen_found_report_model.Person)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)
        police_alias = aliased(citizen_found_report_model.Police)
        image_alias = aliased(citizen_found_report_model.Image)
        
        subquery = (
            session.query(
                found_report_alias.C_ID,
                func.MIN(image_alias.Image).label('Image')
            )
            .join(image_alias, found_report_alias.C_ID == image_alias.C_ID)
            .group_by(found_report_alias.C_ID)
            .subquery()
        )

        query = (
            session.query(
                child_alias.C_ID,
                child_alias.CNAME,
                child_alias.AGE,
                child_alias.GENDER,
                person_alias.P_NAME,
                person_alias.P_CONTACT,
                found_report_alias.description,
                found_report_alias.f_loc_latitude,
                found_report_alias.f_loc_longitude,
                shelter_home_alias.S_Name,
                subquery.c.Image.label('Image')
            )
            .join(found_report_alias, child_alias.C_ID == found_report_alias.C_ID)
            .join(shelter_home_alias, found_report_alias.S_ID == shelter_home_alias.S_Id)
            .join(police_alias, found_report_alias.P_ID == police_alias.P_ID)
            .join(person_alias, person_alias.CNIC == found_report_alias.CNIC)
            .join(subquery, child_alias.C_ID == subquery.c.C_ID)
            .filter(shelter_home_alias.cnic == cnic)  # Filter by shelter home CNIC
        )

        results = query.all()
        formatted_results = [
            {
                'C_Id': row.C_ID,
                'CName': row.CNAME,
                'Age': row.AGE,
                'Description': row.description,
                'Gender': row.GENDER,
                'P_Name': row.P_NAME,
                'P_Contact': row.P_CONTACT,
                'Found_Location_Latitude': row.f_loc_latitude,
                'Found_Location_Longitude': row.f_loc_longitude,
                'Shelter_Location': row.S_Name,
                'Image': row.Image
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return {'error': str(e)}, 500


def adopted_request(scnic):
    try:
        session = db.return_session()
        Adapative_Request_alias = aliased(citizen_found_report_model.Adapative_Request)
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
            .join(Adapative_Request_alias, child_alias.C_ID == Adapative_Request_alias.CID)
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
                Adapative_Request_alias.Reason_Of_Adoption,
                Adapative_Request_alias.request_date,
                Adapative_Request_alias.Ar_Status,
                person_alias.P_NAME,
                subquery.c.Image.label('Image'),
                person_alias.P_CONTACT,
                Adapative_Request_alias.Martial_Status,
                Adapative_Request_alias.Ar_Id,
                person_alias.CNIC,
                shelter_home_alias.S_Id,
            )
            .join(found_report_alias, child_alias.C_ID == found_report_alias.C_ID)
            .join(Adapative_Request_alias, child_alias.C_ID == Adapative_Request_alias.CID)
            .join(shelter_home_alias, Adapative_Request_alias.S_ID == shelter_home_alias.S_Id)
            .join(person_alias, person_alias.CNIC == Adapative_Request_alias.CNIC)
            .outerjoin(subquery, child_alias.C_ID == subquery.c.C_ID)
            .where(shelter_home_alias.cnic == scnic)
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
                'Reason_Of_Adoption': row.Reason_Of_Adoption,
                'Request_Date': row.request_date,  # Convert datetime to string
                'Ar_Status': row.Ar_Status,
                'P_Name': row.P_NAME,
                'Image': row.Image,
                'P_Contact': row.P_CONTACT,
                'Martial_Status':row.Martial_Status,
                'Ar_Id':row.Ar_Id,
                'cnic':row.CNIC,
                'sid':row.S_Id
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def foster_request(scnic):
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
            .where(shelter_home_alias.cnic == scnic)
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
def get_all_shelter_home():
    try:
        session = db.return_session()

        shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)
        query = session.query(shelter_home_alias).all()
        

   

        formatted_results = [
            {
                'Shelter_Name': row.S_Name,
                'sid': row.S_Id,
                'scnic': row.cnic
            }
            for row in query
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def foster_report_verfication(fosterid,current_status,approved_date):
    try: 
        session = db.return_session()
        foster_request_alias = aliased(citizen_found_report_model.Foster_Request)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)

        # Query the report with the given mrid
        report = session.query(foster_request_alias).filter(foster_request_alias.foster_id == fosterid).one_or_none()
        
        # Check if the report exists
        if report:
            # Update the current status
            report.status = current_status
            report.approved_date = approved_date
            session.commit() 
            
        # Commit the changes
        if(current_status == 'approved'):
            found = session.query(found_report_alias).filter(found_report_alias.C_ID == report.CID).first()
            if found:
              found.current_status='Adopted'
              session.commit()
            
        
        return {'message': 'Report status updated successfully'}, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
def report_verfication(arid,current_status):
    try: 
        session = db.return_session()
        adaptive_request_alias = aliased(citizen_found_report_model.Adapative_Request)

        # Query the report with the given mrid
        report = session.query(adaptive_request_alias).filter(adaptive_request_alias.Ar_Id == arid).one_or_none()

        # Check if the report exists
        if report:
            # Update the current status
            report.Ar_Status = current_status
            session.commit()  # Commit the changes
            return {'message': 'Report status updated successfully'}, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
def sendNotificationToRelevantParents(pcnic,sid,arid,status):
    try:
        session = db.return_session()
        
        # Query the shelter home by name
        noti = citizen_found_report_model.EidiNotification(cnic=pcnic,ar_id = arid,sid=sid,status = status)
        session.add(noti)
        session.commit()
        return jsonify({"Message": "Alert Sent successfully"})
        
    

    except Exception as e:
        return {'error': str(e)}, 500 

def search_request(text):
    try:
        session = db.return_session()
        child_alias = aliased(Child)
        found_report_alias = aliased(Found_Report)

        query = (
            session.query(
                Child.C_Id,
                Child.CName,
                Child.Age,
                Child.Gender,
                Found_Report.Found_Location,
                Found_Report.Found_Date,
                Found_Report.Description
            )
            .join(Found_Report, Child.C_Id == Found_Report.C_Id)
            .filter(
                (Child.Father_Name.ilike(f"%{text}%")) |
                (Child.CName.ilike(f"%{text}%")) |
                (Child.Age.ilike(f"%{text}%")) |
                (Child.Gender.ilike(f"%{text}%")) |
                (Found_Report.Found_Location.ilike(f"%{text}%")) |
                (Found_Report.Found_Date.ilike(f"%{text}%")) |
                (Found_Report.Description.ilike(f"%{text}%"))
            )
            .all()
        )

        results = [
            {
                'C_Id': result.C_Id,
                'CName': result.CName,

            }
            for result in query
        ]

        print(results)
        return jsonify(results)

    except Exception as e:
        return {'error': str(e)}, 500


def particular_detail(text):
    try:
        session = db.return_session()
        child_alias = aliased(Child)
        found_report_alias = aliased(Found_Report)

        query = (
            session.query(
                Child.C_Id,
                Child.CName,
                Child.Age,
                Child.Gender,
                Found_Report.Found_Location,
                Found_Report.Found_Date,
                Found_Report.Description
            )
            .join(Found_Report, Child.C_Id == Found_Report.C_Id)
            .filter(
                (Child.Father_Name.ilike(f"%{text}%")) |
                (Child.CName.ilike(f"%{text}%")) |
                (Child.Age.ilike(f"%{text}%")) |
                (Child.Gender.ilike(f"%{text}%")) |
                (Found_Report.Found_Location.ilike(f"%{text}%")) |
                (Found_Report.Found_Date.ilike(f"%{text}%")) |
                (Found_Report.Description.ilike(f"%{text}%"))
            )
            .all()
        )

        results = [
            {
                'C_Id': result.C_Id,
                'CName': result.CName,
                'Age': result.Age,
                'Gender': result.Gender,
                'Found_Location': result.Found_Location,
                'Found_Date': result.Found_Date,
                'Found_Description': result.Description
            }
            for result in query
        ]

        print(results)
        return jsonify(results)

    except Exception as e:
        return {'error': str(e)}, 500

