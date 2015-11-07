import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from WebHUD import app
from WebHUD.restapi import *

host = '0.0.0.0'
port = 5000
debug = True
use_reloader = True

if __name__ == "__main__":
    app.run(host, port, debug, use_reloader=use_reloader)
