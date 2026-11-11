from flask import Flask,send_from_directory
import re
import os,threading
from flask import Flask, jsonify, request
from controller import Person_Controller
from controller import ChildController ,AdoptivePersonController,PoliceController
from controller import  EdhiController
import websockets
import asyncio
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'

# Signup Person
@app.route('/SignupPerson', methods=['POST'])
def SignupPerson():
    
    cnic = request.form.get('CNIC')
    pname = request.form.get('PNAME')
    passwords = request.form.get('PASSWORDS')
    contact = request.form.get('CONTACT')
    address = request.form.get('P_ADDRESS')
    filename=""
    
    if 'P_Image' in request.files:
        file = request.files['P_Image']
        print(file)
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
    response = Person_Controller.SignupPerson(cnic,pname,passwords,contact,address,filename)
    return jsonify(response)
# Login Person
@app.route('/LoginPerson', methods=['POST'])
def LoginPerson():
    cnic = request.form.get('CNIC')
    password = request.form.get('P_Password')
    response = Person_Controller.LoginPerson(cnic,password)
    return jsonify(response)
# Update Person
@app.route('/UpdatePerson/<string:CNIC>',methods=['PUT'])
def UpdatePerson(CNIC):
    search=CNIC
    cnic = request.form.get('CNIC')
    pname = request.form.get('P_Name')
    passwords = request.form.get('P_Password')
    contact = request.form.get('P_Contact')
    address= request.form.get('P_Address')
    filename=""
    if 'P_Image' in request.files:
        file = request.files['P_Image']
        print(file)
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
    response = Person_Controller.UpdatePerson(cnic,pname,passwords,contact,address,filename,search)
    return jsonify(response)
# Add Missing Report
@app.route('/AddMissingReport',methods=['POST'])
def AddMissingReport():
    
    name=request.form.get('name')
    fathername=request.form.get('fathername')
    fathercontact=request.form.get('fathercontact')
    age = request.form.get('age')
    gender = request.form.get('gender')
    missing_location_longitude = request.form.get('missing_location_longitude')
    missing_location_latitude = request.form.get('missing_location_latitude')
    missing_date = request.form.get('missing_date')
    missing_time = request.form.get('missing_time')
    descriptions = request.form.get('descriptions')
    #current_status = request.form.get('current_status')
    cnic = request.form.get('cnic')
    relation=request.form.get('relation')
    
    reportedat = request.form.get('reportedat')
    filename=""
    allfiles=[]
    if 'images' in request.files:
       for img in request.files.getlist('images'):
         filename = os.path.join(UPLOAD_FOLDER, img.filename)
         img.save(filename)
         allfiles.append(filename)
    
    
    response = Person_Controller.addmissingreport(name,fathername,fathercontact,age,gender,missing_location_longitude,missing_location_latitude,
                                                       missing_date,missing_time,descriptions,cnic,
                                                       relation,reportedat,allfiles)
    
    return jsonify(response)
# add found report
@app.route('/AddFoundReport',methods=['POST'])
def AddFoundReport():
    cname = request.form.get('cname')
    age = request.form.get('age')
    gender = request.form.get('gender')
    found_loc_latitude = request.form.get('found_loc_latitude')
    found_loc_longitude = request.form.get('found_loc_longitude')
    # shelter_loc_latitude = request.form.get('shelter_loc_latitude')
    # shelter_loc_longitude = request.form.get('shelter_loc_longitude')
    found_date = request.form.get('found_date')
    description = request.form.get('description')
    current_status = request.form.get('current_status')
    CNIC = request.form.get('cnic')
    filename=""
    allfiles=[]
    if 'images' in request.files:
       for img in request.files.getlist('images'):
         filename = os.path.join(UPLOAD_FOLDER, img.filename)
         img.save(filename)
         allfiles.append(filename)
    response = Person_Controller.addfoundreport(CNIC,cname,age,found_loc_latitude,found_loc_longitude,
                                                found_date,
                                                description,current_status,
                                                gender,
                                                allfiles)
   
    return jsonify(response)
# get images
@app.route('/images/<path:image_name>')
def get_image(image_name):
    return send_from_directory('uploads', image_name)
# get all childs images path
@app.route('/getChildImage/<path:cid>',methods=['GET'])
def get_images_path(cid):
    response= ChildController.get_child_images(cid)
    return jsonify(response)
# get all missing and found childs
@app.route('/MissingChilds',methods=['GET'])
def get_missing_childs_route():
    cnic = request.args.get('cnic') 
    return ChildController.get_missing_childs(cnic)

@app.route('/FoundChilds',methods=['GET'])
def get_found_childs_route():
    cnic = request.args.get('cnic')
    return ChildController.get_found_childs(cnic)
# get current user missing reports
@app.route('/OwnFosterReport', methods = ['GET'])
def get_ownFosterReport_route():
    cnic = request.args.get('cnic') 
    return AdoptivePersonController.get_own_adopted_childs(cnic=cnic)

@app.route('/OwnFoundReport', methods = ['GET'])
def get_ownFoundReport_route():
    cnic = request.args.get('cnic') 
    return ChildController.get_ownfound_childs(cnic)
# search missing and found childs

@app.route('/Search_Missing_Childs/<string:text>',methods=['GET'])
def search_missing_child_route(text):
    return ChildController.search_missing_childs(text)

@app.route('/Search_Found_Childs/<string:text>',methods=['GET'])
def search_found_child_route(text):
    return ChildController.search_found_childs(text)
# Adoption Controller
# get adopted child
@app.route('/getAdoptedChilds',methods=['GET'])
def get_adopted_childs_route():
    return AdoptivePersonController.get_adopted_childs()
# search adopted Child
@app.route('/SearchAdopableChilds/<string:text>',methods=['GET'])
def search_adopted_childs_route(text):
    return AdoptivePersonController.search_adopted_childs(text)
# Adoptable Childs
@app.route('/get_Adoptable_Childs',methods=['GET'])
def get_adoptable_childs_route():
    return AdoptivePersonController.get_adoptable_child()
# Search Adoptable Child
@app.route('/Search_Adopted_Childs/<string:text>',methods=['GET'])
def search_adoptable_childs_route(text):
    return AdoptivePersonController.search_adoptable_child(text)

@app.route('/Insert_Adopted_Childs',methods=['POST'])
def Insert_adopted_childs_route():
    data = request.form
        
        # Accessing specific fields from the JSON data
    cid = data.get('cid')
    cnic = data.get('cnic')
    sid = data.get('sid')
    status = data.get('status')
    reason_of_adaption = data.get('reason_of_adaption')
    request_date = data.get('request_date')
    martial_status = data.get('martial_status')
    income = data.get('income')
    
    response= AdoptivePersonController.insert_adaptive_child(cid,cnic,sid,status,reason_of_adaption,
                                                             request_date,martial_status,income)
    return jsonify(response)

#routes of edhi controller
@app.route('/edhi/foundrequest',methods=['GET'])
def edhi_found_request():
    return EdhiController.found_request()

@app.route('/adoptiverequest',methods=['GET'])
def edhi_adoptive_request():
    cnic = request.args.get('CNIC')
    return EdhiController.adopted_request(cnic)

@app.route('/edhi/searchrequest/<string:text>',methods=['GET'])
def edhi_search_request(text):
    return EdhiController.search_request(text)

@app.route('/edhi/getdetails/<string:text>',methods=['GET'])
def edhi_get_details(text):
    return EdhiController.particular_detail(text)

#routes of police controllers
@app.route('/MissingChildsRequest',methods=['GET'])
def get_missing_childs_request():
    cnic = request.args.get('CNIC')
    return PoliceController.get_missing_childs(cnic)

@app.route('/foundrequestpolice',methods=['GET'])
def policefoundrequest():
    cnic = request.args.get('CNIC')
    return PoliceController.get_found_childs_Police(cnic)
@app.route('/PoliceReportVerification',methods=['POST'])
def police_Report_Verification():
    mr_id = request.form.get('mr_id')
    current_status = request.form.get('current_status')
    response = PoliceController.report_verfication(mr_id,current_status)
    return jsonify(response)
@app.route('/FosterReportVerification',methods=['POST'])
def Foster_Report_Verification():
    foster_id = request.form.get('foster_id')
    current_status = request.form.get('current_status')
    approved_date = request.form.get('approved_date')
    response = EdhiController.foster_report_verfication(foster_id,current_status,approved_date)
    return jsonify(response)
@app.route('/PoliceInprogressFir',methods=['GET'])
def get_InProgress_Fir():
    cnic = request.args.get("CNIC")
    return PoliceController.inprogress_fir(cnic)

@app.route('/police/searchrequest/<string:text>',methods=['GET'])
def police_search_request(text):
     return PoliceController.search_request(text)

@app.route('/police/getdetail/<string:text>',methods=['GET'])
def police_get_details(text):
     return PoliceController.search_missing_childs(text)

@app.route('/getNotification',methods=['GET'])
def get_Notification():    
    return Person_Controller.get_notification_periodically()

@app.route('/getFoundedChildToSendNotification',methods=['GET'])
def getFoundedChildToSendNotification():    
    cnic = request.args.get('CNIC')
    return PoliceController.getFoundedChildToSendNotification(cnic)

@app.route('/foundrequesteidi',methods=['GET'])
def eidifoundrequest():
    cnic = request.args.get('CNIC')
    return EdhiController.getfoundrequesteidi(cnic)

@app.route('/getNearShelterHome',methods=['GET'])
def getNearShelterHome():
    frid = request.args.get('frid')
    return PoliceController.getnearShelterhome(frid)

@app.route('/AllocateShelter',methods=['POST'])
def AllocateShelter():
   
    sname=request.form.get('S_Name')
    frid = request.form.get('frid')
    return PoliceController.allocateshelter(sname,frid)
@app.route('/SendNotificationToRelevantPolice',methods=['POST'])
def SendNotificationToRelevantPolice():
   
    cnic=request.form.get('cnic')
    stationname = request.form.get('stationName')
    cid=request.form.get('cid')
    return PoliceController.sendNotificationToRelevantPolice(cnic,stationname,cid)
@app.route('/getAllNotifications',methods=['GET'])
def getAllNotification():
   
    cnic = request.args.get('CNIC')
    return PoliceController.getAllNotifications(cnic)

@app.route('/EidiReportVerification',methods=['POST'])
def Eidi_Report_Verification():
    ar_id = request.form.get('ar_id')
    current_status = request.form.get('ar_status')
    return EdhiController.report_verfication(ar_id,current_status)

@app.route('/EidiSendNotificationToParent',methods=['POST'])
def Eidi_Send_Notification():
    ar_id = request.form.get('ar_id')
    cnic = request.form.get('cnic')
    sid = request.form.get('sid')
    status = request.form.get('status')
    return EdhiController.sendNotificationToRelevantParents(cnic,sid,ar_id,status)
@app.route('/getCitizenNotiDetails',methods=['GET'])
def Citizen_Noti_Details():
    id = request.args.get('id')
    return Person_Controller.get_notification_details(id)

@app.route('/getRelevantChild',methods=['POST'])
def Get_Relevent_Child():
    if 'img' not in request.files:
        return jsonify({'error': 'No image part in the request'}), 400
    
    img = request.files['img']
    
    if img.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    filename = os.path.join(UPLOAD_FOLDER, img.filename)
    img.save(filename)
    
    response = AdoptivePersonController.get_adaptive_child_with_image(filename)
    return jsonify(response)

@app.route('/GetChilsSendingCids', methods=['GET'])
def Get_Childs_Sending_cids():
    try:
        # Get 'cids' from form data
        cids = request.args.get('cids')
        
        # Ensure 'cids' is split into a list of integers
        cids_list = [int(cid) for cid in cids.split(',') if cid.strip().isdigit()]

        # Call the controller function to retrieve adoptable child information
        response = AdoptivePersonController.get_new_adoptable_child(cids_list)

        # Return JSON response
        return response
    
    except Exception as e:
        return jsonify({'error': str(e)}), 50
    
@app.route('/Insert_Foster_Childs',methods=['POST'])
def Insert_Foster_childs_route():
    data = request.form
        
        # Accessing specific fields from the JSON data
    cid = data.get('cid')
    cnic = data.get('cnic')
    sid = data.get('sid')
    status = data.get('status')
    request_date = data.get('request_date')
    # cid = request.form.get('cid')
    # cnic = request.form.get('cnic')
    # sid = request.form.get('sid')
    # status = request.form.get('status')
    # request_date = request.form.get('request_date')
   
    
    response= AdoptivePersonController.insert_foster_child(cid,cnic,sid,status,
                                                             request_date)
    return jsonify(response)

@app.route('/Return_Foster_Childs',methods=['POST'])
def Return_Foster_childs_route():
    # data = request.form
    #     # Accessing specific fields from the JSON data
    # cid = data.get('cid')
    # cnic = data.get('cnic')
    # to_sid = data.get('to_sid')
    # from_sid = data.get('from_sid')
    # request_date = data.get('request_date')
   
    cid = request.form.get('cid')
    cnic = request.form.get('cnic')
    to_sid = request.form.get('to_sid')
    from_sid = request.form.get('from_sid')
    status = request.form.get('status')
    request_date = request.form.get('request_date')
   
    
    response= AdoptivePersonController.return_foster_child(cid,cnic,to_sid,from_sid,
                                                             request_date)
    return jsonify(response)
@app.route('/fosterrequestEidi',methods=['GET'])
def edhi_foster_request():
    cnic = request.args.get('CNIC')
    return EdhiController.foster_request(cnic)
@app.route('/getallshelter',methods=['GET'])
def get_all_shelter():
    
    return EdhiController.get_all_shelter_home()
if __name__ == '__main__':
    # Start the WebSocket server in a separate thread
    # websocket_thread = threading.Thread(target=Person_Controller.get_notification_periodically)
    # websocket_thread.start()

    # Run the Flask app in the main thread
    app.run(host='0.0.0.0', debug=True)


