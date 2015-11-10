function getRequest(host, route, callback, param) {
    var request = {
        "url": 'http://' + host + '/' + route + (param === undefined ? '' : '/' + param),
        "method": "GET",
        "crossDomain": true
    };

    $.ajax(request).done(callback);
}


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

function setRequest(host, route, callback, param) {
    var request = {
        "url": "http://" + host + '/' + route,
        "method": "PUT",
        "crossDomain": true,
        "body": $.parseJSON(param)
    };
    $.ajax(request).done(callback);
}

// SET

function setPosition(host, x, y, callback) {
    setRequest(host, "position", callback, {
        'x': x,
        'y': y
    });
}

function setGoto(host, path, callback) {
    setRequest(host, 'goto', callback, {
        'path': path
    });
}

function setText(host, text, callback) {
    setRequest(host, 'text', callback, {
        'text': text
    });
}
