# commands
commands =
    path: Command 'static/icons/b-p2p.svg', (-> car.setAuto(); car.path = on),
        -> car.path = off
    wasd: Command 'static/icons/b-key.svg', (-> car.setManual()),
        -> car.setAuto()
    text: Command 'static/icons/b-text.svg', -> car.setAuto()

map.on 'click', (e) ->
    if car.path
        car.setPath [[e.latlng.lat, e.latlng.lng]]
    else
        # destroy HUD components
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
    cmdList = ReactDOM.render <CommandList/>,
        document.getElementById 'commands'
    cmdList.addCommand k, v for k, v of commands
    # don't propagate event
    false

`$(window).resize(function() {
    if (Modernizr.mq('(max-width: 600px)'))
        console.log(false);
    else if (Modernizr.mq('(max-width: 3000px)'))
        console.log(true);
});`
