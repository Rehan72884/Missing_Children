from sqlalchemy.orm import aliased, Session
from sqlalchemy import distinct
from sqlalchemy import func
from flask import Flask,jsonify
import DBHandler as db
from model import citizen_missing_report_model,citizen_found_report_model


def get_missing_childs(cnic):
    try:
        session = db.return_session()
        
        child_alias = aliased(citizen_missing_report_model.Child)
        person_alias = aliased(citizen_missing_report_model.Person)
        police_alias = aliased(citizen_missing_report_model.Police) 
        image_alias = aliased(citizen_missing_report_model.Image)
        missing_report_alias = aliased(citizen_missing_report_model.Missing_Report)

        # Subquery to retrieve the minimum image for each child
        subquery = (
            session.query(
                image_alias.C_ID,
                func.MIN(image_alias.Image).label('Image')
            )
            .filter(image_alias.type == 'missing')
            .group_by(image_alias.C_ID)
            .subquery()
        )

        # Main query to select details of missing children along with the image
        query = (
            session.query(
                child_alias.C_ID.label('C_ID'),
                child_alias.CNAME.label('CNAME'),
                child_alias.AGE.label('AGE'),
                child_alias.GENDER.label('GENDER'),
                child_alias.FATHER_NAME.label('FATHER_NAME'),
                missing_report_alias.m_loc_latitude.label('m_loc_latitude'),
                missing_report_alias.m_loc_longitude.label('m_loc_longitude'),
                missing_report_alias.missing_date.label('missing_date'),
                missing_report_alias.description.label('description'),
                missing_report_alias.Missing_Time.label('Missing_Time'),
                missing_report_alias.mr_id.label('mr_id'),
                person_alias.P_ADDRESS.label('P_ADDRESS'),
                person_alias.P_CONTACT.label('P_CONTACT'),
                police_alias.STATION_ADDRESS.label('STATION_ADDRESS'),
                subquery.c.Image.label('Image')
            )
            .join(missing_report_alias, child_alias.C_ID == missing_report_alias.C_ID)
            .join(person_alias, missing_report_alias.CNIC == person_alias.CNIC)
            .join(police_alias, missing_report_alias.P_ID == police_alias.P_ID)
            .outerjoin(subquery, child_alias.C_ID == subquery.c.C_ID)
            .filter(person_alias.CNIC == cnic)  # Filter by the given CNIC
        )

        results = query.all()

        # Convert SQLAlchemy results to a list of dictionaries
        formatted_results = [
            {
                'C_Id': row.C_ID,
                'Child_Name': row.CNAME,
                'Child_Age': row.AGE,
                'Child_Gender': row.GENDER,
                'Father_Name': row.FATHER_NAME,
                'm_loc_latitude': row.m_loc_latitude,
                'm_loc_longitude': row.m_loc_longitude,
                'Missing_Date': row.missing_date,
                'Description': row.description,
                'Person_Address': row.P_ADDRESS,
                'Person_Contact': row.P_CONTACT,
                'Station_Address': row.STATION_ADDRESS,
                'Missing_Time': row.Missing_Time,
                'Image': row.Image,
                'mrid': row.mr_id
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
def get_found_childs(cnic):
    try:
        session = db.return_session()

        child_alias = aliased(citizen_missing_report_model.Child)
        person_alias = aliased(citizen_missing_report_model.Person)
        police_alias = aliased(citizen_missing_report_model.Police) 
        image_alias = aliased(citizen_missing_report_model.Image)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)
        
        
        subquery = (
            session.query(
                found_report_alias.C_ID,
                func.MIN(image_alias.Image).label('Image')
            )
            .join(image_alias, found_report_alias.C_ID == image_alias.C_ID)
            .filter(image_alias.type == 'found')
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
            .filter(person_alias.CNIC == cnic) 
        )

        results = query.all()
        formatted_results = [
            {
                'C_Id': row.C_ID,
                'CName': row.CNAME,
                'Age': row.AGE,
                'Description':row.description,
                'Gender': row.GENDER,
                'P_Name': row.P_NAME,
                'P_Contact': row.P_CONTACT,
                'Found_Location_Latitude': row.f_loc_latitude,
                'Found_Location_Longitude':row.f_loc_longitude,
                'Shelter_Location': row.S_Name,
                'Image': row.Image,
                
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return {'error': str(e)}, 500



def search_missing_childs(text):
    try:
        session = db.return_session()
        child_alias = aliased(citizen_found_report_model.Child)
        missing_report_alias = aliased(citizen_found_report_model.Missing_Report)

        query = (
            session.query(
                child_alias.C_ID,
                child_alias.CNAME,
                child_alias.AGE,
                child_alias.GENDER,
                missing_report_alias.m_loc_latitude,
                missing_report_alias.m_loc_longitude,
                missing_report_alias.missing_date,
                missing_report_alias.description,
                missing_report_alias.current_status
            )
            .join(missing_report_alias, child_alias.C_ID == missing_report_alias.C_ID)
            .filter(
                (child_alias.FATHER_NAME.ilike(f"%{text}%")) |
                (child_alias.CNAME.ilike(f"%{text}%")) |
                (child_alias.AGE.ilike(f"%{text}%")) |
                (child_alias.GENDER.ilike(f"%{text}%")) 
                # (Missing_Report.Missing_Location.ilike(f"%{text}%")) |
                # (Missing_Report.Missing_Date.ilike(f"%{text}%")) |
                # (Missing_Report.Description.ilike(f"%{text}%")) |
                # (Missing_Report.Current_Status.ilike(f"%{text}%"))
            
            )
            .all()
        )

        results = [
            {
                'C_Id': result.C_ID,
                'CName': result.CNAME,
                'Age': result.AGE,
                'Gender': result.GENDER,
                'Missing_Location_Latitude': result.m_loc_latitude,
                'Missing_Location_Longitude': result.m_loc_longitude,
                'Missing_Date': result.missing_date,
                'Description': result.description,
                'Current_Status': result.current_status
            }
            for result in query
        ]

        print(results)
        return jsonify(results)

    except Exception as e:
        return {'error': str(e)}, 500
def get_child_images(cid):
    session = db.return_session()
    image_alias = aliased(citizen_missing_report_model.Image)
    query = (
        session.query(
            image_alias.Image
        )
        .filter(image_alias.C_ID == cid)
        .all()
    )
    return [image[0] for image in query]


# def search_missing_childs(text):
#     try:
#         session = db.return_session()
#         child_alias = aliased(Child)
#         missing_report_alias = aliased(Missing_Report)

#         query = (
#             session.query(
#                 Child.C_Id,
#                 Child.CName,
#                 Child.Age,
#                 Child.Gender,
#                 Missing_Report.Missing_Location,
#                 Missing_Report.Missing_Date,
#                 Missing_Report.Description,
#                 Missing_Report.Current_Status
#             )
#             .join(Missing_Report, Child.C_Id == Missing_Report.C_Id)
#             .filter(
#                 (Child.Father_Name.ilike(f"%{text}%")) |
#                 (Child.CName.ilike(f"%{text}%")) |
#                 (Child.Age.ilike(f"%{text}%")) |
#                 (Child.Gender.ilike(f"%{text}%")) |
#                 (Missing_Report.Missing_Location.ilike(f"%{text}%")) |
#                 (Missing_Report.Missing_Date.ilike(f"%{text}%")) |
#                 (Missing_Report.Description.ilike(f"%{text}%")) |
#                 (Missing_Report.Current_Status.ilike(f"%{text}%"))
#             )
#             .all()
#         )

#         results = [
#             {
#                 'C_Id': result.C_Id,
#                 'CName': result.CName,
#                 'Age': result.Age,
#                 'Gender': result.Gender,
#                 'Missing_Location': result.Missing_Location,
#                 'Missing_Date': result.Missing_Date,
#                 'Description': result.Description,
#                 'Current_Status': result.Current_Status
#             }
#             for result in query
#         ]

#         print(results)
#         return jsonify(results)

#     except Exception as e:
#         return {'error': str(e)}, 500


# def search_found_childs(text):
#     try:
#         session = db.return_session()
#         child_alias = aliased(Child)
#         found_report_alias = aliased(Found_Report)

#         query = (
#             session.query(
#                 Child.Father_Name,
#                 Child.CName,
#                 Child.Age,
#                 Child.Gender,
#                 Found_Report.Found_Location,
#                 Found_Report.Found_Date,
#                 Found_Report.Description
#             )
#             .join(Found_Report, Child.C_Id == Found_Report.C_Id)
#             .filter(
#                 (Child.Father_Name.ilike(f"%{text}%")) |
#                 (Child.CName.ilike(f"%{text}%")) |
#                 (Child.Age.ilike(f"%{text}%")) |
#                 (Child.Gender.ilike(f"%{text}%")) |
#                 (Found_Report.Found_Location.ilike(f"%{text}%")) |
#                 (Found_Report.Found_Date.ilike(f"%{text}%")) |
#                 (Found_Report.Description.ilike(f"%{text}%"))
#             )
#             .all()
#         )

#         results = [
#             {
#                 'Father_Name': result.Father_Name,
#                 'CName': result.CName,
#                 'Age': result.Age,
#                 'Gender': result.Gender,
#                 'Found_Location': result.Found_Location,
#                 'Found_Date': result.Found_Date,
#                 'Found_Description': result.Description
#             }
#             for result in query
#         ]

#         print(results)
#         return jsonify(results)

#     except Exception as e:
#         return {'error': str(e)}, 500
    
def get_ownmissing_childs(cnic):
    try:
        session = db.return_session()
        child_alias = aliased(citizen_missing_report_model.Child)
        person_alias = aliased(citizen_missing_report_model.Person)
        police_alias = aliased(citizen_missing_report_model.Police) 
        image_alias = aliased(citizen_missing_report_model.Image)
        missing_report_alias = aliased(citizen_missing_report_model.Missing_Report)

        # Subquery to retrieve the minimum image for each child
        subquery = (
            session.query(
                image_alias.C_ID,
                func.MIN(image_alias.Image).label('Image')
            )
            .group_by(image_alias.C_ID)
            .subquery()
        )

        # Main query to select details of missing children along with the image
        query = (
    session.query(
        distinct(child_alias.C_ID),
        child_alias.C_ID.label('C_ID'),
        child_alias.CNAME.label('CNAME'),
        child_alias.AGE.label('AGE'),
        child_alias.GENDER.label('GENDER'),
        child_alias.FATHER_NAME.label('FATHER_NAME'),
        missing_report_alias.m_loc_latitude,
        missing_report_alias.m_loc_longitude,
        missing_report_alias.missing_date,
        missing_report_alias.description,
        missing_report_alias.Missing_Time,
        person_alias.P_ADDRESS.label('P_ADDRESS'),
        person_alias.P_CONTACT.label('P_CONTACT'),
        police_alias.STATION_ADDRESS.label('STATION_ADDRESS'),
        subquery.c.Image.label('Image')
    )
    .join(missing_report_alias, child_alias.C_ID == missing_report_alias.C_ID)
    .join(person_alias, missing_report_alias.CNIC == cnic)  # Filter by provided CNIC
    .filter(person_alias.CNIC == cnic)  # Add filter condition for CNIC
    .join(police_alias, missing_report_alias.P_ID == police_alias.P_ID)
    .outerjoin(subquery, child_alias.C_ID == subquery.c.C_ID)
)

        results = query.all()

        # Convert SQLAlchemy results to a list of dictionaries
        formatted_results = [
            {
                'C_Id':row.C_ID,
                'Child_Name': row.CNAME,
                'Child_Age': row.AGE,
                'Child_Gender': row.GENDER,
                'Father_Name':row.FATHER_NAME,
                'm_loc_latitude': row.m_loc_latitude,
                 'm_loc_longitude': row.m_loc_longitude,
                'Missing_Date': row.missing_date,
                'Description': row.description,
                'Person_Address': row.P_ADDRESS,
                'Person_Contact': row.P_CONTACT,
                'Station_Address':row.STATION_ADDRESS,
                'Missing_Time':row.Missing_Time,
                'Image': row.Image
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return {'error': str(e)}, 500
def get_ownfound_childs(cnic):
    try:
        session = db.return_session()
        child_alias = aliased(citizen_missing_report_model.Child)
        person_alias = aliased(citizen_missing_report_model.Person)
        police_alias = aliased(citizen_missing_report_model.Police) 
        image_alias = aliased(citizen_missing_report_model.Image)
        found_report_alias = aliased(citizen_found_report_model.Found_Report)
        shelter_home_alias = aliased(citizen_found_report_model.Shelter_Home)

        # Subquery to retrieve the minimum image for each child
        subquery = (
            session.query(
                image_alias.C_ID,
                func.MIN(image_alias.Image).label('Image')
            )
            .group_by(image_alias.C_ID)
            .subquery()
        )

        # Main query to select details of missing children along with the image
        query = (
    session.query(
        distinct(child_alias.C_ID),
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
    .join(person_alias, found_report_alias.CNIC == cnic)  # Filter by provided CNIC
    .filter(person_alias.CNIC == cnic)  # Add filter condition for CNIC
    .join(police_alias, found_report_alias.P_ID == police_alias.P_ID)
    .join(shelter_home_alias, found_report_alias.S_ID == shelter_home_alias.S_Id)
    .outerjoin(subquery, child_alias.C_ID == subquery.c.C_ID)
)

        results = query.all()

        # Convert SQLAlchemy results to a list of dictionaries
        formatted_results = [
            {
                'C_Id': row.C_ID,
                'CName': row.CNAME,
                'Age': row.AGE,
                'Description':row.description,
                'Gender': row.GENDER,
                'P_Name': row.P_NAME,
                'P_Contact': row.P_CONTACT,
                'Found_Location_Latitude': row.f_loc_latitude,
                'Found_Location_Longitude':row.f_loc_longitude,
                'Shelter_Location': row.S_Name,
                'Image': row.Image
            }
            for row in results
        ]

        return jsonify(formatted_results)

    except Exception as e:
        return {'error': str(e)}, 500


