var pressed = new Set();

$(document).ready(function(){
  document.body.addEventListener('keydown', function(e) {

    // 37 -> left
    // 38 -> up
    // 39 -> right
    // 40 -> down

    if (e.which in [37,38,39,40]) {
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
  }, 1000);
});
