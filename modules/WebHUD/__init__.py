from flask import Flask
from flask_socketio import SocketIO, emit
from flask.ext.static import Static

app = Flask(__name__)

sio = SocketIO(app)
sio.init_app(app)

st = Static(app)

if __name__ == '__main__':
    raise Exception('do not launch directly!')
