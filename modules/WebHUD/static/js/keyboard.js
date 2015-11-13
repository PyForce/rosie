var pressed = new Set();

$(document).ready(function(){
  document.body.addEventListener('keydown', function(e) {

    // 87 -> W
    // 65 -> A
    // 83 -> S
    // 68 -> D

    if ([87, 65, 83, 68].some(function(element, index, array) { return element === e.which })) {
      pressed.add(e.which);
    }
    
  }, true);

  document.body.addEventListener('keyup', function(e) {
    pressed.delete(e.which);
  }, true);

  setInterval(function(){
    var l = [...pressed];
    console.log(l);
    sio.emit('manual', {'keys': l});
  }, 100);
});
