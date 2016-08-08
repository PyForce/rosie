DEBUG = false

$(document).ready () ->
    # setInterval () ->
    #     car.getOdometry (pos) ->
    #         # car.setLatLng [pos.x, pos.y]
    #         # car.setAngle(pos.theta*180/Math.pi) # converting to degrees
    #         # car.setAngle(pos.theta)
    #         car.move pos
    # , 100

    # keyboards events
    pressed = new Set()
    document.body.addEventListener 'keydown', (e) ->
        # 87 -> W
        # 65 -> A
        # 83 -> S
        # 68 -> D

        # 81 -> Q
        # 69 -> E

        if [87, 65, 83, 68, 81, 69].some((element, index, array) -> element == e.which)
          pressed.add e.which
    , true

    document.body.addEventListener 'keyup', (e) ->
        pressed.delete e.which
    , true

    setInterval () ->
        l = []
        pressed.forEach (e) -> l.push e
        car.sio.emit 'manual', {'keys': l} if car
    , 100
