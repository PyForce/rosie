pressed = new Set()

$(document).ready () ->
  document.body.addEventListener 'keydown', (e) ->

    # 87 -> W
    # 65 -> A
    # 83 -> S
    # 68 -> D

    if [87, 65, 83, 68].some((element, index, array) -> element == e.which)
      pressed.add e.which

  , true

  document.body.addEventListener 'keyup', (e) ->
    pressed.delete e.which
  , true

  setInterval () ->
    l = []
    pressed.forEach (e) -> l.push e
    sio.emit 'manual', {'keys': l}
  , 100
