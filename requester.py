import socketio
import sys
import io

"""
Requester Sub Process Client to trigger constant
frame broadcast on the server side to other clients.
Connected Web clients do not have to request new frames,
just receive the frame broadcasted from the server and
display video feed.
"""


sio = socketio.Client()

@sio.event
def connect():
    print("------------------------------------------------")
    print('((Requester Process Client Connected To Server))')
    print("------------------------------------------------")
    sio.emit('request')


@sio.on('requester')
def sendRequest():
    sio.emit('request')

@sio.event
def disconnect():
    print('Disconnected from server')        

#Start client
def clientStarter(IP,PORT):
    #Connect to Server
    sio.connect(f'http://{IP}:{PORT}')

if __name__ == '__main__':
    IP = sys.argv[1]
    PORT = sys.argv[2]
    #Pass arguements
    clientStarter(IP,PORT)


    