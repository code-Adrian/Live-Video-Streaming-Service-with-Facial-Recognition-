from flask_socketio import SocketIO, emit
from flask import Flask, render_template
from waitress import serve
import face_recognition
import subprocess
import threading
import eventlet
import base64
import math
import time
import cv2
import os

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'LastAssignment'
#Socketio (Monkey Patch eventlet) Enables many concurrent connections efficiently.
socketio = SocketIO(app,async_mode='eventlet',ping_timeout=60,max_packet_size=50)
#Host IP
IP = 'localhost'
#Port
PORT = 1122
#Frontal Face Cascade for facial detection. (For drawing faces)
face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
cap = cv2.VideoCapture(0)
#Resizing frame for client receival (Not for SubProcess)
frameSize = (900, 700)
#Global variable -> Defines total amount of connected clients
total_clients = 0
#Array of identified people and there face location
procresult = []

#Face Identification background process
def sub_procs():
    time.sleep(1)
    #Starts sub process client for heavy face identifaction processing 
    subprocess.Popen(['python', 'client.py',str(IP),str(PORT)])
    #Starts sub process client for constant broadcast
    subprocess.Popen(['python', 'requester.py',str(IP),str(PORT)])
    print("Sub Processes Starting...")

frame_counter = 0
faces = []
def send_video():
    global frame_counter
    global faces
    ret, frame = cap.read()
    if ret:
        frame_counter+=1
        #Frame without resizing (For SubProcesses)
        #Resized Frame
        #rmframe = frame
        frame = cv2.resize(frame, frameSize)
        
        #Displays face rectangle every (x) amount frames (Can slow down Face recognition during stream)
        #Recommendations: FAST CPU Frames (1|5|10) SLOW CPU Frames (30|45|60)
        #Dont skip if (x) == 1
        #if frame_counter == 1:
            #frame_counter = 0
        if frame_counter == 2:
            frame_counter = 0
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)            
            faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        

            #Iterating through faces & drawing rectangles on faces identified.
        for (x, y, w, h) in faces:
            face_distances = procresult
            #Divide the x axis by 3 since face recognition frame was scaled down.
            xVal = x / 3
            if len(face_distances) > 0:
                # Find the index of the of the closest value to the X coordinate.
                abs_diff = lambda x: abs(x[2] - xVal)
                closest_index = min(enumerate(face_distances), key=lambda x: abs_diff(x[1]))[0]
                #Get the name
                name = face_distances[closest_index][1]

                #Draw rectangles using the respectable index that defines which face location has its name and rectangle color
                if face_distances[closest_index][0] is True: # If Detected Face
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    text = name
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                    text_x = x + (w - text_size[0]) // 2
                    text_y = y + h + 30 + (30 - text_size[1]) // 2
                    cv2.putText(frame, text, (text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                else: # If face not Detected
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    text = name
                    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                    text_x = x + (w - text_size[0]) // 2
                    text_y = y + h + 30 + (30 - text_size[1]) // 2
                    cv2.putText(frame, text, (text_x, text_y),cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)        
        
        #============================= 
        #=======SENDING DATA==========
        #=============================
        
        #For Clients (Resized Frame -> Base64 -> Send)
        _, jpeg = cv2.imencode('.jpg', frame)
        b64 = base64.b64encode(jpeg.tobytes()).decode('utf-8')
        package = [b64,total_clients]
        emit('stream', package,broadcast=True)
        #For Face Recognition SubProcess Client (Regular Frame -> Base64 -> Send)
        _, jpeg = cv2.imencode('.jpg', frame)
        b64 = base64.b64encode(jpeg.tobytes()).decode('utf-8')
        emit('process',b64)
        #For Requester Subprocess to request more from requester sub process
        emit('requester')

#Render Template
@app.route('/')
def index():
    return render_template('index.html')

#On Connect Clear console & Upate total users
@socketio.on('connect')
def connect():
    global total_clients
    os.system('cls')
    total_clients+=1
    print("Total Clients:", total_clients)

#On Disconnect Clear console & Upate total users
@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')
    global total_clients
    total_clients -= 1
    os.system('cls')
    print("Total Clients:", total_clients)

#Broadcast video stream to all clients.
@socketio.on('request')
def request():
        send_video()

#Data received from SubProcess client is set to globally
#(Data Structure) [Detected = True|False, Name = "Bob", faceLocation= 200]
@socketio.on('set_face_vars')
def connect(result):
    global procresult
    procresult=result
    print(procresult)

if __name__ == '__main__':
    print("Total Clients:", total_clients)
    #Start background task (Thread) to create client subproces
    socketio.start_background_task(sub_procs)
    #Using Waitress serve to start socket io server
    #(Waitress serve for production environment)(Handles high concurrency of connected clients)
    #(Just Socket io run for development environment)
    serve(socketio.run(app, host=IP, port=PORT))



    