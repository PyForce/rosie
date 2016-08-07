from flask import Flask
from flask.ext.static import Static
from flask_socketio import SocketIO

app = Flask(__name__)

sio = SocketIO(app)
sio.init_app(app)

st = Static(app)

from . import restapi
from . import views
from . import static

if __name__ == '__main__':
    raise Exception('do not launch directly!')
