# HUD control
mountHUD = (robot) ->
    robot.setAuto()
    # commands
    commands =
        path: Command 'line chart', (-> robot.setAuto(); robot.path = on),
            -> robot.path = off
        wasd: Command 'game', (-> robot.setManual()),
            -> robot.setAuto()

    if not Modernizr.mq '(max-width: 600px)'
        mountInfo robot
    #load commands
    cmdList = ReactDOM.render <CommandList/>,
        document.getElementById 'commands'
    cmdList.addCommand k, v for k, v of commands

    text = Command 'font', (-> robot.setAuto(); ReactDOM.render <TextCommand
        robot={robot} cmdList={cmdList}/>, document.getElementById 'mode-text'),
        -> ReactDOM.unmountComponentAtNode document.getElementById 'mode-text'
    cmdList.addCommand 'text', text

mountInfo = (robot) ->
    # show streaming
    ReactDOM.render <RobotVideo robot={robot}/>,
        document.getElementById 'streaming'
    # show info
    ReactDOM.render <RobotCard robot={robot}/>,
        document.getElementById 'robot-info-wrapper'

unmountHUD = ->
    # destroy HUD components
    unmountInfo()
    ReactDOM.unmountComponentAtNode document.getElementById 'commands'
    delete window.car

unmountInfo = ->
    ReactDOM.unmountComponentAtNode(
        document.getElementById 'streaming')
    ReactDOM.unmountComponentAtNode(
        document.getElementById 'robot-info-wrapper')

map.on 'click', (e) ->
    car = window.car
    console.debug e.latlng.lat, e.latlng.lng
    if car and car.path
        car.setPath [[e.latlng.lat, e.latlng.lng]]
    else unmountHUD()

$(window).resize ->
    if Modernizr.mq '(max-width: 600px)'
        unmountInfo()
    else if Modernizr.mq '(max-width: 3000px)'
        # mountInfo car
        false
