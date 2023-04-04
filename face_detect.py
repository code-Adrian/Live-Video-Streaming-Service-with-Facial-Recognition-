import cv2
import threading
import time


def detect_face(queue,outputqueue,known_face_encodings,known_faces):
    while True:
        import face_recognition as fr
        if not queue.empty():
            frame = queue.get()
            
            #small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            face_locations = fr.face_locations(rgb_small_frame,model='hog')
            frame_face_encoding = fr.face_encodings(rgb_small_frame, face_locations,model='hog')
            
            if len(frame_face_encoding) > 0:
                result = []

                for index, face_encoding in enumerate(known_face_encodings):
                    results = fr.compare_faces([frame_face_encoding[0]], face_encoding)
                    if True in results:
                        name = known_faces[index]
                        result = [True,name]
                    
                if len(result) > 0:    
                    outputqueue.put(result)
                else:
                    name = "Unknown"
                    result = [False,name]
                    outputqueue.put(result)
