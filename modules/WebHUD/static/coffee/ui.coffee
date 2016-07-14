# commands
commands =
    path: Command 'line chart', (-> car.setAuto(); car.path = on),
        -> car.path = off
    wasd: Command 'game', (-> car.setManual()),
        -> car.setAuto()
        text: Command 'font', (-> robot.setAuto(); ReactDOM.render <TextCommand
            robot={robot}/>, document.getElementById 'mode-text'),
            -> ReactDOM.unmountComponentAtNode(
                document.getElementById 'mode-text')

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
