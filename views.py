from flask import render_template, request
from WebHUD import app
from WebHUD.utils import allow_origin

@app.route('/', methods=['GET'])
@allow_origin
def index():
    host = request.base_url.split('://')[1][:-1]
    return render_template('index.html', host=host)
