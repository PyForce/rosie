DEBUG = false

$(document).ready () ->
    # keyboards events
    pressed = new Set()
    $(document.body).on 'keydown', (e) ->
        # 87 -> W
        # 65 -> A
        # 83 -> S
        # 68 -> D

        # 81 -> Q
        # 69 -> E

        pressed.add e.which if e.which in [87, 65, 83, 68, 81, 69]

    $(document.body).on 'keyup', (e) -> pressed.delete e.which

    setInterval () ->
        car = window.car
        l = []
        pressed.forEach (e) -> l.push e
        car.sio.emit 'manual', {'keys': l} if car
    , 100
