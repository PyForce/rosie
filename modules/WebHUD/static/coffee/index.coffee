DEBUG = false

$(document).ready () ->
    # MENU
    $('#i-menu').click () ->
        $('#settings').hide()
        $('#menu').toggle()

    # SETTINGS
    $('#i-settings').click () ->
        $('#menu').hide()
        $('#settings').toggle()

    # TOGGLE MENU/SETTINGS
    $('.list-menu a').click () ->
        $('.list-menu').hide()

    $('#btn-order').click () ->
        setText undefined, $("#text-order").val()

    $("#form-text").submit (event) ->
        setText undefined, $("#text-order").val()
        event.preventDefault()

    setInterval () ->
        car.getOdometry (pos) ->
            # car.setLatLng [pos.x, pos.y]
            # car.setAngle(pos.theta*180/Math.pi) # converting to degrees
            # car.setAngle(pos.theta)
            car.move pos
    , 100

    # websocket
    sio = io.connect "http://#{document.domain}:#{location.port}"

    sio.onclose = () ->
        alert 'SIO CLOSED!!!'

    sio.on 'echo reply', (msg) ->
        console.log msg.text

    sio.on 'position', (data) ->
        console.log 'position', data

    sio.emit 'echo',
        'text': 'hello socket.io world!'

    # keyboards events
    pressed = new Set()
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


imageUrl = "static/images/LTL.svg";
width = 0.43;
height = 0.25;
coords = [0, 0];
overlay = (new RobotOverlay imageUrl, coords, width, height).addTo map

car = new Robot overlay

# UI
# commands
path = Command 'static/icons/b-p2p.svg', 'p2p', (->
    car.setAuto(); car.path = on), -> car.path = off
wasd = Command 'static/icons/b-key.svg', 'key', (-> car.setManual()),
    -> car.setAuto()
text = Command 'static/icons/b-text.svg', 'text', ->
    car.setAuto()

map.on 'click', (e) ->
    if car.path
        car.setPath [[e.latlng.lat, e.latlng.lng]]
    else
        ReactDOM.unmountComponentAtNode(
            document.getElementById 'video-streaming')
        ReactDOM.unmountComponentAtNode(
            document.getElementById 'robot-info-wrapper')
        ReactDOM.unmountComponentAtNode document.getElementById 'commands'

$(car.overlay._image).click ->
    # show streaming
    ReactDOM.render <RobotVideo robot={car}/>,
        document.getElementById 'video-streaming'
    # show info
    ReactDOM.render <RobotCard robot={car}/>,
        document.getElementById 'robot-info-wrapper'
    ReactDOM.render <CommandList commands={[path, wasd, text]}/>,
        document.getElementById 'commands'

    false
