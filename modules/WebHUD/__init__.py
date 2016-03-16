from flask import Flask
from flask_socketio import SocketIO, emit


app = Flask(__name__)
sio = SocketIO(app)
sio.init_app(app)

if __name__ == '__main__':
    raise Exception('do not launch directly!')
