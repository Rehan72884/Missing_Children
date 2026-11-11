from model import personModel as c,citizen_missing_report_model,citizen_found_report_model
from DBHandler import DBHandler
from DBHandler import return_session
import DBHandler as db
import json
from flask import jsonify
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.orm import aliased
import time
from datetime import datetime
import face_recognition
import threading
from sqlalchemy import or_
import websockets
import asyncio
from blinker import Namespace
base_directory = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# signup Person Function
def SignupPerson(cnic, pname, passwords, contact,address,filename):
    try:
        session = db.return_session()
        person = citizen_found_report_model.Person(CNIC=cnic, P_NAME=pname, P_PASSWORD=passwords, P_CONTACT=contact, P_ADDRESS=address, P_Image=filename,person_type ='CITIZEN')
      
        #person = c.Person(CNIC=cnic, P_Name=pname, P_Password=passwords, P_Contact=contact, P_Address=address, P_Image=filename)
                       
        session.add(person)
        session.commit()
        return {"message": "Person added successfully"}, 200
    except Exception as e:
        print(e)
        return {"errors": str(e)}, 500
# Login Person Function
def LoginPerson(cnic, password):
    try:
        session = db.return_session()
        user = session.query(c.Person).filter_by(CNIC=cnic).first()
        if user and user.P_Password == password:
             serialized_user = {
                "cnic": user.CNIC,
                "name": user.P_Name,
                "password":user.P_Password,
                "contact":user.P_Contact,
                "address":user.P_Address,
                "image":user.P_Image,
                "person_type": user.person_type
                # Add other user attributes as needed
            }
             return {"user": serialized_user}, 200
        else:
            return {"message": "Invalid credentials"}, 401

    except Exception as e:
        return {"errors": str(e)}, 500
    
# update Person Function
def UpdatePerson(cnic, pname ,passwords, contact,address,image,search):
    try:
        session = db.return_session()
        user = session.query(citizen_found_report_model.Person).filter_by(CNIC=search).first()
        if user:    
            if cnic:
                user.CNIC = cnic
            if pname:
                user.P_NAME = pname
            if passwords:
                user.P_PASSWORD = passwords
            if contact:
                user.P_CONTACT = contact
            if address:
                user.P_ADDRESS = address
            if image:
                user.P_Image = image
            session.commit()

    except Exception as e:
        return {"errors": str(e)}, 500
    
# # Create a namespace for signals
# my_signals = Namespace()

# # Define a signal called 'missing_report_added'
# missing_report_added = my_signals.signal('missing_report_added')

# # Function to match person using face recognition
def match_person(image_paths, target_image_path, cid):
    target_image = face_recognition.load_image_file(target_image_path)
    target_encodings = face_recognition.face_encodings(target_image)
    if len(target_encodings) == 0:
        print("No faces found in the target image.")
        return False, None  # Return False and None if no faces are found in the target image
    target_encoding = target_encodings[0]
    for image_path in image_paths:
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        if len(face_encodings) > 0:
            for face_encoding in face_encodings:
                match = face_recognition.compare_faces([target_encoding], face_encoding)
                if match[0]:
                    # Return True and the child ID (cid) if a match is found
                    return True, cid
    return False, None 

# # Function to get missing images from the database
def get_missing_images_from_database():
    session = db.return_session()
    images = session.query(citizen_found_report_model.Image).filter(citizen_found_report_model.Image.type == 'missing').all()
    image_paths = [os.path.join(base_directory, img.Image) for img in images]
    session.close()
    return image_paths

# # Function to get found images from the database
def get_found_images_from_database():
    session = db.return_session()
    images = session.query(citizen_found_report_model.Image).filter(citizen_found_report_model.Image.type == 'found').all()
    image_paths = [os.path.join(base_directory, img.Image) for img in images]
    session.close()
    return image_paths

# # Function to trigger face recognition
# def trigger_face_recognition(child_id, allfiles):
#     images = get_found_images_from_database(connection_string)
#     for file in allfiles:
#         if match_person(images, file):
#             return True
#     return False
# def handle_missing_report(sender, **extra):
#     child_id = extra.get('child_id')
#     allfiles = extra.get('allfiles')
#     # Call the function to match the person using the images
#     match_result = trigger_face_recognition(child_id, allfiles)
#     if match_result:
#         print("Person found!")
#     else:
#         print("Person not found!")

# # Connect signal handler to signal
# missing_report_added.connect(handle_missing_report)
# Add Missing Report
def addmissingreport(name, fathername, fathercontact, age, gender, missing_location_longitude, missing_location_latitude, missing_date, missing_time, descriptions, cnic, relation, reportedat, allfiles):
    try:
        session = db.return_session()

        age_int = int(age)
        current_status = "Submitted"
        child = session.query(citizen_found_report_model.Child).filter_by(CNAME=name).first()
        if child is None :
            
            child = citizen_missing_report_model.Child(CNAME=name, FATHER_NAME=fathername, AGE=age_int, GENDER=gender, FATHER_CONTACT=fathercontact)
        else:
            child.CNAME = name
            child.AGE = age
            child.FATHER_NAME = fathername
            child.FATHER_CONTACT = fathercontact
            child.GENDER = gender
            
        # Query police coordinates for different locations
        police_saddar = session.query(citizen_missing_report_model.PoliceCoordinates).filter_by(P_ID=4).all()
        police_satellite = session.query(citizen_missing_report_model.PoliceCoordinates).filter_by(P_ID=5).all()
        police_g6 = session.query(citizen_missing_report_model.PoliceCoordinates).filter_by(P_ID=6).all()

        missing_location_longitude_float = float(missing_location_longitude)
        missing_location_latitude_float = float(missing_location_latitude)

        # Calculate the difference for each police location
        saddar_diff = [abs(police.Longitude - missing_location_longitude_float) + abs(police.Latitude - missing_location_latitude_float) for police in police_saddar]
        satellite_diff = [abs(police.Longitude - missing_location_longitude_float) + abs(police.Latitude - missing_location_latitude_float) for police in police_satellite]
        g6_diff = [abs(police.Longitude - missing_location_longitude_float) + abs(police.Latitude - missing_location_latitude_float) for police in police_g6]

        # Find the minimum difference for each location
        min_diff_saddar = min(saddar_diff)
        min_diff_satellite = min(satellite_diff)
        min_diff_g6 = min(g6_diff)

        # Determine the location with the minimum difference
        if min_diff_saddar < min_diff_satellite and min_diff_saddar < min_diff_g6:
            closest_city = 'Saddar'
            closest_police_coordinates = police_saddar[saddar_diff.index(min_diff_saddar)]
            police_id = 4
        elif min_diff_satellite < min_diff_g6 and min_diff_satellite < min_diff_saddar:
            closest_city = 'Satellite'
            closest_police_coordinates = police_satellite[satellite_diff.index(min_diff_satellite)]
            police_id = 5
        else:
            closest_city = 'G6'
            closest_police_coordinates = police_g6[g6_diff.index(min_diff_g6)]
            police_id = 6

        print(f"Closest city: {closest_city}")
        print(f"Closest police coordinates: {closest_police_coordinates}")

        session.add(child)
        session.commit()  # Commit to save the child and get the child ID

        child = session.query(citizen_missing_report_model.Child).filter_by(CNAME=name).first()
        user = session.query(citizen_missing_report_model.Person).filter_by(CNIC=cnic).first()
        type = 'missing'

        for img in allfiles:
            image = citizen_missing_report_model.Image(C_ID=child.C_ID, Image=img, type=type)
            session.add(image)

        report = citizen_missing_report_model.Missing_Report(
            m_loc_latitude=missing_location_latitude,
            m_loc_longitude=missing_location_longitude,
            missing_date=missing_date,
            Missing_Time=missing_time,
            Relation=relation,
            description=descriptions,
            current_status=current_status,
            C_ID=child.C_ID,
            P_ID=police_id,
            CNIC=user.CNIC
        )

        session.add(report)
        session.commit()
        mr = session.query(citizen_found_report_model.Missing_Report).filter_by(CNIC=cnic,C_ID=child.C_ID).first()
        
        #image_paths = get_missing_images_from_database()
        # image_paths=threading.Thread(target=get_missing_images_from_database).start()
        # res =threading.Thread(target=match_person(image_paths, allfiles[0], child.C_ID)).start()
        # get_images_thread = threading.Thread(target=get_missing_images_from_database)
        # get_images_thread.start()
        # get_images_thread = get_missing_images_from_database()

    # Create a thread for matching the person
        # match_thread = threading.Thread(target=match_person, args=(get_images_thread, allfiles[0], child.C_ID))
        # match_thread.start()
        images_path = get_found_images_from_database()
        #images_remove = images_path.pop()
        match,match_cid = match_person(images_path,allfiles[0],child.C_ID)

    # Wait for both threads to finish
       # get_images_thread.join()
        # match_thread.join()
        if match:
            noti = citizen_found_report_model.Notification(mid=mr.mr_id,status = 0,type='CITIZEN')
            session.add(noti)
            session.commit()
            print("Notification created successfully")
            today = datetime.now().date()  # Get the current date
            current_date = today.strftime("%Y-%m-%d")
            fr = session.query(citizen_found_report_model.Found_Report).filter_by(C_ID=child.C_ID).first()
            missing_found_noti = citizen_found_report_model.missing_found_child(fr_id = fr.fr_id,mr_id=mr.mr_id,approval_date=current_date)
            session.add(missing_found_noti)
            session.commit()
            # pnoti = citizen_found_report_model.Notification(fid=fr.fr_id,mid=mr.mr_id,status = 0,type = 'POLICE')
            # session.add(pnoti)
            # session.commit()
            print("Police Notification created successfully")
        
        return {"message": "Missing Report added successfully"}, 200
    except Exception as e:
        print(e)
        return {"errors": str(e)}, 500


#Add Found Report
def addfoundreport(cnic,cname,age,found_loc_longitude,
                   found_loc_latitude,found_date,
                   description,current_status,gender,
                   allfiles):
                  # shelter_loc_latitude,shelter_loc_longitude,
    try:
        session = db.return_session()
        
        age_int = int(age)
        child = session.query(citizen_found_report_model.Child).filter_by(CNAME=cname).first()
        if child is None :
            
            child = citizen_found_report_model.Child(CNAME=cname, AGE=age_int,GENDER=gender)
       
        # Fetch police coordinates
        police_saddar = session.query(citizen_missing_report_model.PoliceCoordinates).filter_by(P_ID=4).all()
        police_satellite = session.query(citizen_missing_report_model.PoliceCoordinates).filter_by(P_ID=5).all()
        police_g6 = session.query(citizen_missing_report_model.PoliceCoordinates).filter_by(P_ID=6).all()

        found_location_longitude_float = float(found_loc_longitude)
        found_location_latitude_float = float(found_loc_latitude)

        # Calculate the difference for each police location
          
        saddar_diff = [abs(police.Longitude - found_location_longitude_float) + abs(police.Latitude - found_location_latitude_float) for police in police_saddar]
        satellite_diff = [abs(police.Longitude - found_location_longitude_float) + abs(police.Latitude - found_location_latitude_float) for police in police_satellite]
        g6_diff = [abs(police.Longitude - found_location_longitude_float) + abs(police.Latitude - found_location_latitude_float) for police in police_g6]

        # Find the minimum difference for each location
        min_diff_saddar = min(saddar_diff)
        min_diff_satellite = min(satellite_diff)
        min_diff_g6 = min(g6_diff)

        # Determine the location with the minimum difference
        if min_diff_saddar < min_diff_satellite and min_diff_saddar < min_diff_g6:
            closest_city = 'Saddar'
            closest_police_coordinates = police_saddar[saddar_diff.index(min_diff_saddar)]
            police_id = 4
        elif min_diff_g6 < min_diff_satellite and min_diff_g6 < min_diff_saddar:
            closest_city = 'G6'
            closest_police_coordinates = police_g6[g6_diff.index(min_diff_g6)]
            police_id = 6
            
        else:
            closest_city = 'Satellite'
            closest_police_coordinates = police_satellite[satellite_diff.index(min_diff_satellite)]
            police_id = 5

        print(f"Closest city: {closest_city}")
        print(f"Closest police coordinates: {closest_police_coordinates}")

        session.add(child)
        print('child inserted')
        # Query shelter home coordinates for Islamabad and Rawalpindi
    #     shelter_homes_saddar = session.query(citizen_found_report_model.ShelterHomeCoordinates).filter_by(S_ID=3).all()
    #     shelter_homes_satellite = session.query(citizen_found_report_model.ShelterHomeCoordinates).filter_by(S_ID=4).all()
    #     shelter_homes_g6 = session.query(citizen_found_report_model.ShelterHomeCoordinates).filter_by(S_ID=5).all()
    #     found_location_longitude_float = float(found_loc_longitude)
    #     found_location_latitude_float = float(found_loc_latitude)
    
    # # Calculate the differences for Islamabad shelter homes
    #     saddar_diff = [abs(shelter.Longitude - found_location_longitude_float) + abs(shelter.Latitude - found_location_latitude_float) for shelter in shelter_homes_saddar]
    #     min_diff_saddar = min(saddar_diff)
    #     closest_shelter_home_saddar = shelter_homes_saddar[saddar_diff.index(min_diff_saddar)]

    #     # Calculate the differences for Satellite shelter homes
    #     satellite_diff = [abs(shelter.Longitude - found_location_longitude_float) + abs(shelter.Latitude - found_location_latitude_float) for shelter in shelter_homes_satellite]
    #     min_diff_satellite = min(satellite_diff)
    #     closest_shelter_home_satellite = shelter_homes_satellite[satellite_diff.index(min_diff_satellite)]

    #     # Calculate the differences for G6 shelter homes
    #     g6_diff = [abs(shelter.Longitude - found_location_longitude_float) + abs(shelter.Latitude - found_location_latitude_float) for shelter in shelter_homes_g6]
    #     min_diff_g6 = min(g6_diff)
    #     closest_shelter_home_g6 = shelter_homes_g6[g6_diff.index(min_diff_g6)]

    #     shelter_id = 0
    #     # Compare the minimum differences
    #     if min_diff_saddar < min_diff_satellite and min_diff_saddar < min_diff_g6:
    #         closest_shelter_home_coordinates = closest_shelter_home_saddar
    #         closest_city = 'Saddar'
    #         shelter_id = 3
    #     elif min_diff_satellite < min_diff_g6 and min_diff_satellite < min_diff_saddar:
    #         closest_shelter_home_coordinates = closest_shelter_home_satellite
    #         closest_city = 'Satellite'
    #         shelter_id = 4
    #     elif min_diff_g6 < min_diff_saddar and min_diff_g6 < min_diff_satellite:
    #         closest_shelter_home_coordinates = closest_shelter_home_g6
    #         closest_city = 'G6'
    #         shelter_id = 5
    
    #     print(f"Closest city: {closest_city}")
    #     print(f"Closest shelter home coordinates: {closest_shelter_home_coordinates}")
        
        
       
        #police = session.query(police_model.Police).filter_by(Station_Address=reportedat).first()
        child = session.query(citizen_found_report_model.Child).filter_by(CNAME=cname).first()
        user = session.query(citizen_found_report_model.Person).filter_by(CNIC=cnic).first()
        for img in allfiles:
         image= citizen_missing_report_model.Image(C_ID=child.C_ID,Image=img,type='found')
         session.add(image)
         
        report = citizen_found_report_model.Found_Report(
                               f_loc_latitude=found_loc_latitude,f_loc_longitude=found_loc_longitude,
                               found_date=found_date,
                               description=description,current_status=current_status,C_ID=child.C_ID,
                               CNIC=cnic,P_ID=police_id
                            #    ,S_ID=shelter_id
                              )
        session.add(report)
        session.commit()
        fr = session.query(citizen_found_report_model.Found_Report).filter_by(CNIC=cnic,C_ID=child.C_ID).first()
        #image_paths = get_missing_images_from_database()
        # image_paths=threading.Thread(target=get_missing_images_from_database).start()
        # res =threading.Thread(target=match_person(image_paths, allfiles[0], child.C_ID)).start()
        get_images_thread = threading.Thread(target=get_missing_images_from_database)
        get_images_thread.start()
        # without threading
        images_paths = get_missing_images_from_database()
        #remove_image = images_paths.pop()
        match,match_cid = match_person(images_paths,allfiles[0],child.C_ID)

    # Create a thread for matching the person
        # match_thread = threading.Thread(target=match_person, args=(get_images_thread, allfiles[0], child.C_ID))
        # match_thread.start()

    # Wait for both threads to finish
        # get_images_thread.join()
        # match_thread.join()
        if match:
            noti = citizen_found_report_model.Notification(fid=fr.fr_id,status = 0,type = 'CITIZEN')
            session.add(noti)
            session.commit()
            print("Notification created successfully")
            today = datetime.now().date()  # Get the current date
            current_date = today.strftime("%Y-%m-%d")
            mr = session.query(citizen_found_report_model.Missing_Report).filter_by(C_ID=child.C_ID).first()
            missing_found_noti = citizen_found_report_model.missing_found_child(fr_id = fr.fr_id,mr_id=mr.mr_id,approval_date=current_date)
            session.add(missing_found_noti)
            session.commit()
            # pnoti = citizen_found_report_model.Notification(fid=fr.fr_id,mid=mr.mr_id,status = 0,type = 'POLICE')
            # session.add(pnoti)
            # session.commit()
            print("Police Notification created successfully")
        return {"message": "Found Report added successfully"}, 200
    except Exception as e:
        print(str(e))
        return {"errors": str(e)}, 500
def get_notification_periodically():
    try:
        session = db.return_session()
        notifications = session.query(citizen_found_report_model.Notification).filter_by().all()
        if notifications:
            response_list = []
            for noti in notifications:
                if noti.fid is not None:
                    fr = session.query(citizen_found_report_model.Found_Report).filter_by(fr_id=noti.fid).first()
                    child = session.query(citizen_found_report_model.Child).filter_by(C_ID=fr.C_ID).first()
                    mfr= session.query(citizen_found_report_model.missing_found_child).filter_by(fr_id=fr.fr_id).first()
                    response = {
                        "status": "found",
                        "Child_Name": child.CNAME,
                        "C_ID": fr.C_ID,
                        "frid":fr.fr_id,
                        "mrid":mfr.mr_id
                    }
                    response_list.append(response)
                elif noti.mid is not None:
                    mr = session.query(citizen_found_report_model.Missing_Report).filter_by(mr_id=noti.mid).first()
                    child = session.query(citizen_found_report_model.Child).filter_by(C_ID=mr.C_ID).first()
                    mfr= session.query(citizen_found_report_model.missing_found_child).filter_by(mr_id=mr.mr_id).first()
                    response = {
                        "status": "found",
                        "Child_Name": child.CNAME,
                        "C_ID": fr.C_ID,
                        "mrid":mr.mr_id,
                        # "frid":mfr.fr_id
                    }
                    response_list.append(response)

                # Update notification status
                noti.status = 1

            session.commit()
            return jsonify(response_list)
        else:
            return jsonify([])
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)})
    



def get_notification_details(id):
    try:
        # Ensure the id is not None
        if not id:
            return jsonify([])

        # Return session object from the database
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
        
        # Query the notification detail based on fr_id or mr_id
        notification_detail = session.query(citizen_found_report_model.missing_found_child).filter(
            or_(
                citizen_found_report_model.missing_found_child.fr_id == id,
                citizen_found_report_model.missing_found_child.mr_id == id
            )
        ).first()

        if not notification_detail:
            return jsonify([])

        fr_id = notification_detail.fr_id
        mr_id = notification_detail.mr_id

        # Subquery to get the minimum image
        subquery = (
            session.query(
                image_alias.C_ID,
                func.MIN(image_alias.Image).label('Image')
            )
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
                missing_report_alias.m_loc_latitude,
                missing_report_alias.m_loc_longitude,
                found_report_police_alias.STATION_ADDRESS.label('found_report_station_address'),
                shelter_home_alias.S_Name,
                missing_report_alias.mr_id,
                found_report_alias.fr_id,
                shelter_home_alias.Contact_Info,
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
            .filter(
                or_(
                    missing_report_alias.mr_id == mr_id,
                    found_report_alias.fr_id == fr_id
                )
            )
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
                'Missing_Location_Latitude': row.m_loc_latitude,
                'Missing_Location_Longitude': row.m_loc_longitude,
                'Shelter_Location': row.S_Name,
                'Image': row.Image,
                'Found_Report_Station_Address': row.found_report_station_address,
                'Missing_Report_Station_Address': row.missing_report_station_address,
                'mr_id': row.mr_id,
                'fr_id': row.fr_id,
                'Shelter Contact':row.Contact_Info
            }
            for row in results
        ]

        return jsonify(formatted_results)
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)})