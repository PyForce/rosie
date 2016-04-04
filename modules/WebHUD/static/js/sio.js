$(document).ready(function() {
    sio = io.connect('http://' + document.domain + ':' + location.port);

	sio.onclose = function(){
		alert('SIO CLOSED!!!');
	}

    sio.on('echo reply', function(msg) {
        console.log(msg['text']);
    });

	sio.on('position', function(pos) {
		console.log('position', pos);
        car.setLatLng([pos.x, pos.y]);
        car.setAngle(pos.theta);
	});
});
