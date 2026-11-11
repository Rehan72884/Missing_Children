# from blinker import Namespace
# from Person_Controller import trigger_face_recognition

# # Create a namespace for your signals
# my_signals = Namespace()

# # Define a signal called 'missing_report_added'
# missing_report_added = my_signals.signal('missing_report_added')

# def handle_missing_report(sender, **extra):
#     child_id = extra.get('child_id')
#     allfiles = extra.get('allfiles')
#     # Call the function to match the person using the images
#     match_result = trigger_face_recognition(child_id, allfiles)
#     if match_result:
#         print("Person found!")
#     else:
#         print("Person not found!")

# missing_report_added.connect(handle_missing_report)
