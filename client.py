import face_recognition as fr
import face_recognition
import numpy as np
import threading
import socketio
import base64
import time
import glob
import cv2
import sys
import io
import os

"""
Client Sub Process to handle heavy computations
like face recognition.
"""

sio = socketio.Client()

#Encodings
encodings = []
#Face Names
face_names = []

def convert_b64_to_frame(b64):
# Decode the base64-encoded image data into a binary format
    decoded_data = base64.b64decode(b64)
# Convert the binary data into a NumPy array
    np_data = np.frombuffer(decoded_data, np.uint8)
# Decode the NumPy array into a `cv2` frame
    frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
    #Return converted frame
    return frame

#Sets the encodings and face names array.
def load_encodings():
    images_path = glob.glob(os.path.join("images/", "*.*"))
    print("{} encoding images found.".format(len(images_path)))
    for img_path in images_path:
    
        img = cv2.imread(img_path)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print(img_path)
        basename = os.path.basename(img_path)
        (filename, ext) = os.path.splitext(basename)
        # Get encoding
        img_encoding = face_recognition.face_encodings(rgb_img)[0]
        #Populate encoding & face names array with each image iteration
        encodings.append(img_encoding)
        face_names.append(filename)
        

#Identifies multiple faces in a frame
def detect_faces(frame):
    try:
        #Reduce frame to 1/4 of original size to reduce computational time
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = fr.face_locations(rgb_frame, model='hog')
        frame_face_encodings = fr.face_encodings(rgb_frame, face_locations, model='hog')

        face_results = []
        for i, frame_face_encoding in enumerate(frame_face_encodings):
            matches = fr.compare_faces(encodings, frame_face_encoding)
            name = "Unknown"
            face_location = face_locations[i]
            # Check for match
            if True in matches:
                match_index = matches.index(True)
                name = face_names[match_index]
            # Add result to list of face results
            face_results.append([True, name, face_location[1]] if name != "Unknown" else [False, name, face_location[1]])
        return face_results
    except Exception as e:
        print(e)
        pass


@sio.event
def connect():
    print("-----------------------------------------------------------")
    print('((Face Recognition Sub Process Client Connected To Server))')
    print("-----------------------------------------------------------")
    sio.emit('request')

@sio.event
def disconnect():
    print('Disconnected from server')


#Return result 
@sio.on('process')
def receive_image(b64):
    #Convert base64 to frame.
    frame = convert_b64_to_frame(b64)
    #Set the face identifation variables based on frame.
    result = detect_faces(frame)
    #Request new frame
    sio.emit('request')
    if result != None:
        #Send Result Data
        sio.emit('set_face_vars',result)
        

#Start client
def clientStarter(IP,PORT):
    #Load Encodings
    load_encodings()
    #Connect to server
    sio.connect(f'http://{IP}:{PORT}')

if __name__ == '__main__':
    IP = sys.argv[1]
    PORT = sys.argv[2]
    #Pass arguements
    clientStarter(IP,PORT)