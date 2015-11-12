var pressed = new Set();

$(document).ready(function(){
  document.body.addEventListener('keydown', function(e) {

    // 37 -> left
    // 38 -> up
    // 39 -> right
    // 40 -> down

    if ([37,38,39,40].some(function(element, index, array) { return element === e.which })) {
      pressed.add(e.which);
    }
    
  }, true);

  document.body.addEventListener('keyup', function(e) {
    pressed.delete(e.which);
  }, true);

  setInterval(function(){
    var l = [...pressed];
    console.log(l);
    // sio.emit('manual', {'keys': l});
  }, 100);
});
