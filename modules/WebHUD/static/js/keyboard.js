var pressed = new Set();

$(document).ready(function(){
  document.body.addEventListener('keydown', function(e) {

    // 87 -> W
    // 65 -> A
    // 83 -> S
    // 68 -> D

    if ([87, 65, 83, 68].some(function(element, index, array) { return element === e.which })) {
      pressed.add(e.which);
      sio.emit('manual', {'keys': [...pressed]})
    }

	if (e.which == 32){
		setPath();
	}
    
  }, true);

  document.body.addEventListener('keyup', function(e) {
    pressed.delete(e.which);
    sio.emit('manual', {'keys': [...pressed]})
  }, true);
/*
  setInterval(function(){
    var l = [...pressed];
    sio.emit('manual', {'keys': l});
  }, 100);*/
});
