from sqlalchemy.orm import aliased
from flask import Flask,jsonify
import DBHandler as db
from sqlalchemy import func
from model.Model1 import Child, Found_Report, Shelter_Home, Person, Image, Police, Missing_Report
from model import citizen_missing_report_model,citizen_found_report_model

def get_missing_childs(cnic):
    try:
        session = db.return_session()
        child_alias = aliased(citizen_found_report_model.Child)
        person_alias = aliased(citizen_found_report_model.Person)
        missing_report_alias = aliased(citizen_found_report_model.Missing_Report)
        police_alias = aliased(citizen_found_report_model.Police)
        image_alias = aliased(citizen_found_report_model.Image)

        subquery = (
            session.query(
                image_alias.C_ID,
                func.MIN(image_alias.Image).label('Image')
            )
            .group_by(image_alias.C_ID)
            .subquery()
        )

        query = (
            session.query(
                child_alias.C_ID.label('C_ID'),
                child_alias.CNAME.label('CNAME'),
                child_alias.AGE.label('AGE'),
                child_alias.GENDER.label('GENDER'),
                missing_report_alias.m_loc_latitude,
                missing_report_alias.m_loc_longitude,
                missing_report_alias.missing_date,
                missing_report_alias.description,
                missing_report_alias.Missing_Time,
                missing_report_alias.mr_id,
                missing_report_alias.current_status,
                person_alias.P_ADDRESS.label('P_ADDRESS'),
                person_alias.P_CONTACT.label('P_CONTACT'),
                police_alias.STATION_ADDRESS.label('STATION_ADDRESS'),
                subquery.c.Image.label('Image')
            )
            .join(missing_report_alias, child_alias.C_ID == missing_report_alias.C_ID)
            .join(person_alias, missing_report_alias.CNIC == person_alias.CNIC)
            .join(police_alias, missing_report_alias.P_ID == police_alias.P_ID)
            .outerjoin(subquery, child_alias.C_ID == subquery.c.C_ID)
            .filter(missing_report_alias.current_status == 'submitted')
            .filter(police_alias.cnic == cnic)  # Filter by provided CNIC
        )

        results = query.all()

        formatted_results = [
            {
                'C_Id': row.C_ID,
                'mr_id': row.mr_id,
                'Child_Name': row.CNAME,
                'Child_Age': row.AGE,
                'Child_Gender': row.GENDER,
                'm_loc_latitude': row.m_loc_latitude,
                'm_loc_longitude': row.m_loc_longitude,
                'Missing_Date': row.missing_date,
                'Description': row.description,
                'Person_Address': row.P_ADDRESS,
                'Person_Contact': row.P_CONTACT,
                'Station_Address': row.STATION_ADDRESS,
                'Current_Status': row.current_status,
                'Missing_Time': row.Missing_Time,
                'Image': row.Image
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return {'error': str(e)}, 500

    
def report_verfication(mrid,current_status):
    try: 
        session = db.return_session()
        missingreport_alias = aliased(citizen_missing_report_model.Missing_Report)

        # Query the report with the given mrid
        report = session.query(missingreport_alias).filter(missingreport_alias.mr_id == mrid).one_or_none()

        # Check if the report exists
        if report:
            # Update the current status
            report.current_status = current_status
            session.commit()  # Commit the changes
            return {'message': 'Report status updated successfully'}, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
def inprogress_fir(cnic):
    try:
        session = db.return_session()
        child_alias = aliased(citizen_found_report_model.Child)
        person_alias = aliased(citizen_found_report_model.Person)
        missing_report_alias = aliased(citizen_found_report_model.Missing_Report)
        police_alias = aliased(citizen_found_report_model.Police) 
        image_alias = aliased(citizen_found_report_model.Image)

        subquery = (
            session.query(
                image_alias.C_ID,
                func.MIN(image_alias.Image).label('Image')
            )
            .group_by(image_alias.C_ID)
            .subquery()
        )

        # Main query to select other details along with the image
        query = (
         session.query(
        child_alias.C_ID.label('C_ID'),
        child_alias.CNAME.label('CNAME'),
        child_alias.AGE.label('AGE'),
        child_alias.GENDER.label('GENDER'),
        missing_report_alias.m_loc_latitude,
        missing_report_alias.m_loc_longitude,
        missing_report_alias.missing_date,
        missing_report_alias.description,
        missing_report_alias.Missing_Time,
        missing_report_alias.mr_id,
        missing_report_alias.current_status,
        person_alias.P_ADDRESS.label('P_ADDRESS'),
        person_alias.P_CONTACT.label('P_CONTACT'),
        police_alias.STATION_ADDRESS.label('STATION_ADDRESS'),
        subquery.c.Image.label('Image')
        )
         .join(missing_report_alias, child_alias.C_ID == missing_report_alias.C_ID)
        .join(person_alias, missing_report_alias.CNIC == person_alias.CNIC)
        .join(police_alias, missing_report_alias.P_ID == police_alias.P_ID)
        .outerjoin(subquery, child_alias.C_ID == subquery.c.C_ID)
        .filter(missing_report_alias.current_status == 'Verified')
        .filter(police_alias.cnic == cnic)
        # Use outer join to include all missing children
        )

        results = query.all()
        results.reverse()


        # Convert SQLAlchemy results to a list of dictionaries
        formatted_results = [
            {
                'C_Id':row.C_ID,
                'mr_id':row.mr_id,
                'Child_Name': row.CNAME,
                'Child_Age': row.AGE,
                'Child_Gender': row.GENDER,
                'm_loc_latitude': row.m_loc_latitude,
                 'm_loc_longitude': row.m_loc_longitude,
                'Missing_Date': row.missing_date,
                'Description': row.description,
                'Person_Address': row.P_ADDRESS,
                'Person_Contact': row.P_CONTACT,
                'Station_Address':row.STATION_ADDRESS,
                'Current_Status':row.current_status,
                'Missing_Time':row.Missing_Time,
                'Image': row.Image
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return {'error': str(e)}, 500
    
        
# def get_found_childs():
#     try:
#         session = db.return_session()

#         child_alias = aliased(Child)
#         person_alias = aliased(Person)
#         found_report_alias = aliased(Found_Report)
#         shelter_home_alias = aliased(Shelter_Home)
#         police_alias = aliased(Police)

#         query = (
#             session.query(
#                 child_alias.C_Id.label('C_Id'),
#                 child_alias.CName.label('CName'),
#                 child_alias.Age.label('Age'),
#                 child_alias.Gender.label('Gender'),
#                 person_alias.P_Name.label('P_Name'),
#                 person_alias.P_Contact.label('P_Contact'),
#                 found_report_alias.Found_Location.label('Found_Location'),
#                 shelter_home_alias.Shelter_Location.label('Shelter_Location')
#             )
#             .join(found_report_alias, child_alias.C_Id == found_report_alias.C_Id)
#             .join(shelter_home_alias, found_report_alias.S_Id == shelter_home_alias.S_Id)
#             .join(police_alias, found_report_alias.Fr_Id == police_alias.P_Id)
#             .join(person_alias, person_alias.CNIC == found_report_alias.CNIC)
#         )


#         print(query)

#         results = query.all()
#         for rows in results:
#             print(results)
#         formatted_results = [
#             {
#                 'C_Id': row.C_Id,
#                 'CName': row.CName,
#                 'Age': row.Age,
#                 'Gender': row.Gender,
#                 'P_Name': row.P_Name,
#                 'P_Contact': row.P_Contact,
#                 'Found_Location': row.Found_Location,
#                 'Shelter_Location': row.Shelter_Location
#             }
#             for row in results
#         ]

#         return jsonify(formatted_results)

#     except Exception as e:
#         return {'error': str(e)}, 500

def get_found_childs_Police(cnic):
    try:
        session = db.return_session()

        child_alias = aliased(citizen_found_report_model.Child)
        person_alias = aliased(citizen_found_report_model.Person)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        # shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)
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
                found_report_alias.fr_id,
                found_report_alias.f_loc_latitude,
                found_report_alias.f_loc_longitude,
                # shelter_home_alias.S_Name,
                subquery.c.Image.label('Image')
            )
            .join(found_report_alias, child_alias.C_ID == found_report_alias.C_ID)
            # .join(shelter_home_alias, found_report_alias.S_ID == shelter_home_alias.S_Id)
            .join(police_alias, found_report_alias.P_ID == police_alias.P_ID)
            .join(person_alias, person_alias.CNIC == found_report_alias.CNIC)
            .join(subquery, child_alias.C_ID == subquery.c.C_ID)
            .filter(police_alias.cnic == cnic)  # Filter by police CNIC
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
                # 'Shelter_Location': row.S_Name,
                'Image': row.Image,
                'Fr_id':row.fr_id
                
                
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return {'error': str(e)}, 500

def getnearShelterhome(frid):
    try:
        session = db.return_session()
        child_alias = aliased(citizen_found_report_model.Child)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        police_alias = aliased(citizen_found_report_model.Police)

        fr = session.query(found_report_alias).filter_by(fr_id=frid).first()
 # Query shelter home coordinates for Islamabad and Rawalpindi
        shelter_homes_saddar = session.query(citizen_found_report_model.ShelterHomeCoordinates).filter_by(S_ID=3).all()
        shelter_homes_satellite = session.query(citizen_found_report_model.ShelterHomeCoordinates).filter_by(S_ID=4).all()
        shelter_homes_g6 = session.query(citizen_found_report_model.ShelterHomeCoordinates).filter_by(S_ID=5).all()
        found_location_longitude_float = float(fr.f_loc_longitude)
        found_location_latitude_float = float(fr.f_loc_latitude)
    
    # Calculate the differences for Islamabad shelter homes
        saddar_diff = [abs(shelter.Longitude - found_location_longitude_float) + abs(shelter.Latitude - found_location_latitude_float) for shelter in shelter_homes_saddar]
        min_diff_saddar = min(saddar_diff)
        closest_shelter_home_saddar = shelter_homes_saddar[saddar_diff.index(min_diff_saddar)]

        # Calculate the differences for Satellite shelter homes
        satellite_diff = [abs(shelter.Longitude - found_location_longitude_float) + abs(shelter.Latitude - found_location_latitude_float) for shelter in shelter_homes_satellite]
        min_diff_satellite = min(satellite_diff)
        closest_shelter_home_satellite = shelter_homes_satellite[satellite_diff.index(min_diff_satellite)]

        # Calculate the differences for G6 shelter homes
        g6_diff = [abs(shelter.Longitude - found_location_longitude_float) + abs(shelter.Latitude - found_location_latitude_float) for shelter in shelter_homes_g6]
        min_diff_g6 = min(g6_diff)
        closest_shelter_home_g6 = shelter_homes_g6[g6_diff.index(min_diff_g6)]

        shelter_id = 0
        # Compare the minimum differences
        if min_diff_saddar < min_diff_satellite and min_diff_saddar < min_diff_g6:
            closest_shelter_home_coordinates = closest_shelter_home_saddar
            closest_city = 'Saddar'
            shelter_id = 3
        elif min_diff_satellite < min_diff_g6 and min_diff_satellite < min_diff_saddar:
            closest_shelter_home_coordinates = closest_shelter_home_satellite
            closest_city = 'Satellite'
            shelter_id = 4
        elif min_diff_g6 < min_diff_saddar and min_diff_g6 < min_diff_satellite:
            closest_shelter_home_coordinates = closest_shelter_home_g6
            closest_city = 'G6'
            shelter_id = 5
    
        print(f"Closest city: {closest_city}")
        print(f"Closest shelter home coordinates: {closest_shelter_home_coordinates}") 
        sh = session.query(citizen_found_report_model.Shelter_Home).filter_by(S_Id=shelter_id).first()
        if sh:
            results = {
                "S_Name":sh.S_Name
            }

        print(results)
        return jsonify(results)

    except Exception as e:
        return {'error': str(e)}, 500


def allocateshelter(sname,frid):
    try:
        session = db.return_session()
        shelter_alias = aliased(citizen_found_report_model.Shelter_Home)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        
        # Query the shelter home by name
        sh = session.query(shelter_alias).filter(shelter_alias.S_Name == sname).first()
        fr = session.query(found_report_alias).filter(found_report_alias.fr_id == frid).first()
        if fr:
            fr.S_ID = sh.S_Id
            session.commit()
        return jsonify({"Message": "Shelter allocated successfully"})
        
    

    except Exception as e:
        return {'error': str(e)}, 500

       
def search_request(text):
    try:
        session = db.return_session()
        child_alias = aliased(Child)
        missing_report_alias = aliased(Missing_Report)

        query = (
            session.query(
                Child.C_Id,
                Child.CName,
                Child.Age,
                Child.Gender,
                Missing_Report.Missing_Location,
                Missing_Report.Missing_Date,
                Missing_Report.Description,
                Missing_Report.Current_Status
            )
            .join(Missing_Report, Child.C_Id == Missing_Report.C_Id)
            .filter(
                (Child.Father_Name.ilike(f"%{text}%")) |
                (Child.CName.ilike(f"%{text}%")) |
                (Child.Age.ilike(f"%{text}%")) |
                (Child.Gender.ilike(f"%{text}%")) |
                (Missing_Report.Missing_Location.ilike(f"%{text}%")) |
                (Missing_Report.Missing_Date.ilike(f"%{text}%")) |
                (Missing_Report.Description.ilike(f"%{text}%")) |
                (Missing_Report.Current_Status.ilike(f"%{text}%"))
            )
            .all()
        )

        results = [
            {
                'C_Id': result.C_Id,
                'CName': result.CName,
                'Age':result.Age,
                'Gender': result.Gender,
                'Description': result.Description,
                

            }
            for result in query
        ]

        print(results)
        return jsonify(results)

    except Exception as e:
        return {'error': str(e)}, 500

def search_missing_childs(text):
    try:
        session = db.return_session()
        child_alias = aliased(Child)
        missing_report_alias = aliased(Missing_Report)

        query = (
            session.query(
                Child.C_Id,
                Child.CName,
                Child.Age,
                Child.Gender,
                Missing_Report.Missing_Location,
                Missing_Report.Missing_Date,
                Missing_Report.Description,
                Missing_Report.Current_Status
            )
            .join(Missing_Report, Child.C_Id == Missing_Report.C_Id)
            .filter(
                (Child.Father_Name.ilike(f"%{text}%")) |
                (Child.CName.ilike(f"%{text}%")) |
                (Child.Age.ilike(f"%{text}%")) |
                (Child.Gender.ilike(f"%{text}%")) |
                (Missing_Report.Missing_Location.ilike(f"%{text}%")) |
                (Missing_Report.Missing_Date.ilike(f"%{text}%")) |
                (Missing_Report.Description.ilike(f"%{text}%")) |
                (Missing_Report.Current_Status.ilike(f"%{text}%"))
            )
            .all()
        )

        results = [
            {
                'C_Id': result.C_Id,
                'CName': result.CName,
                'Age': result.Age,
                'Gender': result.Gender,
                'Missing_Location': result.Missing_Location,
                'Missing_Date': result.Missing_Date,
                'Description': result.Description,
                'Current_Status': result.Current_Status
            }
            for result in query
        ]

        print(results)
        return jsonify(results)

    except Exception as e:
        return {'error': str(e)}, 500
    
   
def getFoundedChildToSendNotification(cnic):
    try:
        session = db.return_session()

        child_alias = aliased(citizen_found_report_model.Child)
        person_alias = aliased(citizen_found_report_model.Person)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)
        found_report_police_alias = aliased(citizen_found_report_model.Police, name="found_report_police")
        missing_report_police_alias = aliased(citizen_found_report_model.Police, name="missing_report_police")
        image_alias = aliased(citizen_found_report_model.Image)
        missing_found_alias = aliased(citizen_found_report_model.missing_found_child)
        missing_report_alias = aliased(citizen_found_report_model.Missing_Report)

        # Get the P_ID based on the provided CNIC
        found_police_details = session.query(found_report_police_alias.P_ID).filter(found_report_police_alias.cnic == cnic).first()

        if not found_police_details:
            return jsonify({'error': 'No police record found with the provided CNIC'}), 404

        # Subquery to get the latest image for each child
        subquery = (
            session.query(
                image_alias.C_ID,
                func.MIN(image_alias.Image).label('Image')
            )
            .join(found_report_alias, found_report_alias.C_ID == image_alias.C_ID)
            .group_by(image_alias.C_ID)
            .subquery()
        )

        # Main query to fetch the details
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
                found_report_police_alias.STATION_ADDRESS.label('found_report_station_address'),
                shelter_home_alias.S_Name,
                missing_report_alias.mr_id,
                found_report_alias.fr_id,
                subquery.c.Image.label('Image'),
                missing_report_police_alias.STATION_ADDRESS.label('missing_report_station_address')
            )
            .join(found_report_alias, child_alias.C_ID == found_report_alias.C_ID)
            .join(shelter_home_alias, found_report_alias.S_ID == shelter_home_alias.S_Id)
            .join(found_report_police_alias, found_report_alias.P_ID == found_report_police_alias.P_ID)
            .join(person_alias, person_alias.CNIC == found_report_alias.CNIC)
            .join(missing_found_alias, found_report_alias.fr_id == missing_found_alias.fr_id)
            .join(missing_report_alias, missing_report_alias.mr_id == missing_found_alias.mr_id)
            .join(missing_report_police_alias, missing_report_alias.P_ID == missing_report_police_alias.P_ID)
            .join(subquery, child_alias.C_ID == subquery.c.C_ID)
            .filter(found_report_alias.P_ID == found_police_details.P_ID)  
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
                'Image': row.Image,
                'Found_Report_Station_Address': row.found_report_station_address,
                'Missing_Report_Station_Address': row.missing_report_station_address,
                'mr_id': row.mr_id,
                'fr_id': row.fr_id,
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return {'error': str(e)}, 500
    
# def sendNotificationToRelevantPolice(mrid):
#     try:
#         session = db.return_session()

#         child_alias = aliased(citizen_found_report_model.Child)
#         person_alias = aliased(citizen_found_report_model.Person)
#         found_report_alias = aliased(citizen_found_report_model.Found_Report)
#         shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)
#         police_alias = aliased(citizen_found_report_model.Police)
        
#         image_alias = aliased(citizen_found_report_model.Image)
#         missing_found_alias = aliased(citizen_found_report_model.missing_found_child)
#         missing_report_alias = aliased(citizen_found_report_model.Missing_Report)

#         mr = session.query(missing_report_alias).filter_by(missing_report_alias.mr_id == mrid)
        
    


#     except Exception as e:
#         return {'error': str(e)}, 500

def sendNotificationToRelevantPolice(cnic,missingstation,cid):
    try:
        session = db.return_session()
        police_alias = aliased(citizen_found_report_model.Police)
        police_notification_alias = aliased(citizen_found_report_model.policeNotification)
        
        # Query the shelter home by name
        from_police = session.query(police_alias).filter(police_alias.cnic == cnic).first()
        to_police = session.query(police_alias).filter(police_alias.STATION_ADDRESS == missingstation).first()
        
        noti = citizen_found_report_model.policeNotification(to_pid = to_police.P_ID,from_pid = from_police.P_ID,cid = cid)
        session.add(noti)
        session.commit()
        return jsonify({"Message": "Shelter allocated successfully"})
        
    

    except Exception as e:
        return {'error': str(e)}, 500  

def getAllNotifications(cnic):
    try:
        session = db.return_session()
        police_alias = aliased(citizen_found_report_model.Police)
        police_notification_alias = aliased(citizen_found_report_model.policeNotification)
        child_alias = aliased(citizen_found_report_model.Child)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        shelter_alias = aliased(citizen_found_report_model.Shelter_Home)
        image_alias = aliased(citizen_found_report_model.Image)
        missing_report_alias = aliased(citizen_found_report_model.Missing_Report)
        # Query the shelter home by name
        to_police = session.query(police_alias).filter(police_alias.cnic == cnic).first()
        
        # Query notifications sent to this police officer
        notifications = session.query(police_notification_alias).filter(police_notification_alias.to_pid == to_police.P_ID).all()
        notificationdetails = []
        for noti in notifications:
            from_police = session.query(police_alias).filter(police_alias.P_ID == noti.from_pid).first()
            child = session.query(child_alias).filter(child_alias.C_ID == noti.cid).first()
            fr = session.query(found_report_alias).filter(found_report_alias.C_ID == child_alias.C_ID).first()
            sh = session.query(shelter_alias).filter(shelter_alias.S_Id==fr.S_ID).first()
            img = session.query(image_alias).filter(image_alias.C_ID == child.C_ID, image_alias.type == 'found').first()
            mr = session.query(missing_report_alias).filter(missing_report_alias.C_ID == Child.C_Id).first()
            mpolice = session.query(police_alias).filter(police_alias.P_ID==mr.P_ID).first()
            notificationdetails.append(
                {
                'from_police_id': noti.from_pid,
                'to_police_id': noti.to_pid,
                'from_police_name':from_police.STATION_ADDRESS,
                'from_police_contact':from_police.CONTACT,
                'Child_Name':child.CNAME,
                'Age':child.AGE,
                'Gender':child.GENDER,
                'Father_Name':child.FATHER_NAME,
                'Father_Contact':child.FATHER_CONTACT,
                'Found_Location_Latitude':fr.f_loc_latitude,
                'Found_Location_Longitude':fr.f_loc_longitude,
                'Shelter_Name':sh.S_Name,
                'Image':img.Image,
                'Missing_Location_Latitude':mr.m_loc_latitude,
                'Missing_Location_Longitude':mr.m_loc_longitude,
                'Missing_Location_Police':mpolice.STATION_ADDRESS,
                'C_Id':child.C_ID
                }
            )
        
        return jsonify(notificationdetails)
        
    

    except Exception as e:
        return {'error': str(e)}, 500 


