$(document).ready(function() {
    sio = io.connect('http://' + document.domain + ':' + location.port);

	sio.onclose = function(){
		alert('SIO CLOSED!!!');
	}

    sio.on('echo reply', function(msg) {
        console.log(msg['text']);
    });

	sio.on('position', function(data) {
		console.log('position', data);
	});

    sio.emit('echo', {
        'text': 'hello socket.io world!'
    });

});
