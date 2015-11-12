import sys
from os.path import abspath, join, dirname
sys.path.append(abspath(join(dirname(__file__), '..')))

from WebHUD import app  #, sio
from WebHUD.restapi import *
from WebHUD.views import *

myhost = '0.0.0.0'
myport = 5000
debug = False
use_reloader = True

def run_server():
    app.run(app, host=myhost, port=myport, debug=debug, use_reloader=use_reloader)
    #sio.run(app, host=host, port=port, debug=debug, use_reloader=use_reloader)


if __name__ == '__main__':
    run_server()
