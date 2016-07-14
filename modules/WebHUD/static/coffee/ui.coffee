# HUD control
mountHUD = (robot) ->
    # commands
    commands =
        path: Command 'line chart', (-> robot.setAuto(); robot.path = on),
            -> robot.path = off
        wasd: Command 'game', (-> robot.setManual()),
            -> robot.setAuto()
        text: Command 'font', (-> robot.setAuto(); ReactDOM.render <TextCommand
            robot={robot}/>, document.getElementById 'mode-text'),
            -> ReactDOM.unmountComponentAtNode(
                document.getElementById 'mode-text')

    # show streaming
    ReactDOM.render <RobotVideo robot={robot}/>,
        document.getElementById 'video-streaming'
    # show info
    ReactDOM.render <RobotCard robot={robot}/>,
        document.getElementById 'robot-info-wrapper'
    #load commands
    cmdList = ReactDOM.render <CommandList/>,
        document.getElementById 'commands'
    cmdList.addCommand k, v for k, v of commands

unmountHUD = ->
    # destroy HUD components
    ReactDOM.unmountComponentAtNode(
        document.getElementById 'video-streaming')
    ReactDOM.unmountComponentAtNode(
        document.getElementById 'robot-info-wrapper')
    ReactDOM.unmountComponentAtNode document.getElementById 'commands'


map.on 'click', (e) ->
    if car.path
        car.setPath [[e.latlng.lat, e.latlng.lng]]
    else unmountHUD()

$(car.overlay._image).click ->
    # show HUD
    mountHUD car
    # don't propagate event
    false

$(window).resize ->
    if Modernizr.mq '(max-width: 600px)'
        unmountHUD()
    else if Modernizr.mq '(max-width: 3000px)'
        mountHUD car
