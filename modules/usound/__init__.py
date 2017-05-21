from .usound import *


def init():
    from restAPI import app
    from flask import jsonify

    @app.route('/usound', methods=['GET'])
    def ultrasonic_measurements():
        return jsonify(ultrasound=get_all_sensors())
