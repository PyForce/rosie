from flask import Flask
from flask_gulp import Static
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

app = Flask(__name__)
st = Static(app)
server = None

from . import restapi
from . import views
from . import static

if __name__ == '__main__':
    raise Exception('do not launch directly!')


def init():
    from settings import config
    host = config.get('WebHUD', 'host', '0.0.0.0')
    port = config.getint('WebHUD', 'port', 5000)
    debug = config.getboolean('WebHUD', 'debug', False)
    app.debug = debug

    if debug:
        st.watch(['static/coffee/**/*.coffee', 'static/coffee/**/*.cjsx',
                  'static/less/**/*.less'], 'cjsx', 'coffee', 'less',
                 'browserify')
    else:
        st.runall()

    global server
    server = WSGIServer((host, port), restapi.handle_wsgi_request,
                        handler_class=WebSocketHandler)
    server.serve_forever()


def end():
    server.stop()
