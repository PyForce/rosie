import sys
from os.path import abspath, join, dirname
sys.path.append(abspath(join(dirname(__file__), '..')))

from WebHUD import app
from WebHUD.restapi import *
from WebHUD.views import *

host = '0.0.0.0'
port = 5000
debug = True
use_reloader = True

if __name__ == "__main__":
    app.run(host, port, debug, use_reloader=use_reloader)
