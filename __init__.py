from flask import Flask
from flask_sockets import Sockets


app = Flask(__name__)
sockets = Sockets(app)


if __name__ == '__main__':
    app.run()
