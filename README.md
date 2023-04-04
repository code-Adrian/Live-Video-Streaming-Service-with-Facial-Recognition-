# Live Video Streaming Web Application with Facial Recognition

This server uses Flask and SocketIO to stream video frames from a webcam and apply face recognition to the frames. To reduce lag and improve performance, it leverages sub-processes to handle video frame processing separately from the main server process. This allows for faster processing of video frames and reduces the chances of the server becoming unresponsive due to heavy processing loads.

## Installation
This server requires Python 3 to be installed. The required libraries are located in the requirements.txt file. Install them using pip:
```
pip install -r requirements.txt
```

## Usage
To start the server, run the following command:
```
python server.py
```
After the server is started, it will spawn 2 new subprocess clients that connect to the server, after they connect, you can view the video stream by accessing http://localhost:1122 using a web browser.

## Configuration
### Host IP
The host IP can be set in the IP variable in the server.py file. By default, it is set to localhost.

### Port
The port can be set in the PORT variable in the server.py file. By default, it is set to 1122.

### Face Recognition
The face recognition feature in the client.py subprocess is implemented using the face_recognition library. If you want to update the default images used for recognition, you can simply add new images to the 'images' folder. Note that if the server is currently running, you will need to restart it for the changes to take effect.

### Face Cascade
The server uses the haarcascade_frontalface_default.xml file for face detection.

### Example
<p float="left" align="middle">
<img src="https://res.cloudinary.com/dv5ambux0/image/upload/v1680637795/Distribute_rheovu.png" alt="Example"/>
</p>