// GET

function getSensor(host, name, callback) {
    getRequest(host, "sensor", callback, name);
}

function getOdometry(host, callback) {
    getRequest(host, "odometry", callback);
}

function getMetadata(host, callback) {
    getRequest(host, "metadata", callback);
}
// SET

function setPosition(host, x, y, theta, callback) {
    setRequest(host, "position", callback, {
        'x': x,
        'y': y,
        'theta': theta
    });
}

function setPath(host, path, callback) {

    if (path === undefined) {
        path = trajectory.getLatLngs().map(
            function(elem) {
                return [elem.lat, elem.lng]
            }
        );
    }

    setRequest(host, 'path', callback, {
        'path': path
    });
}

function setText(host, text, callback) {
    setRequest(host, 'text', callback, {
        'text': text
    });
}

function setManualMode(host, callback) {
    setRequest(host, 'manual_mode', callback);
}

function setAutoMode(host, callback) {
    setRequest(host, 'auto_mode', callback);
}

// Helpers
var debug = true;

// Uses HTTP GET verb to query status
function getRequest(host, route, callback, param) {
    if (host === undefined) {
        host = document.domain + ':' + location.port;
    };
    var request = {
        "url": 'http://' + host + '/' + route + (param === undefined ? '' : '/' + param),
        "method": "GET",
        "crossDomain": true
    };

    $.ajax(request).done(function(data) {
        if (callback !== undefined) {
            callback(data);
        }
        if (debug) {
            for (var prop in data) {
                console.log("result." + prop + " = " + data[prop]);
            }
        };
    });
}

// Uses HTTP PUT verb for settings
function setRequest(host, route, callback, param) {
    if (host === undefined) {
        host = document.domain + ':' + location.port;
    };
    var request = {
        "url": "http://" + host + '/' + route,
        "method": "PUT",
        "crossDomain": true,
        "data": param
    };
    $.ajax(request).done(function(data) {
        if (callback !== undefined) {
            callback.call(data)
        }
        if (debug) {
            for (var prop in data) {
                console.log("result." + prop + " = " + data[prop]);
            }
        };
    });
}
