$ = jQuery = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'

{map} = require './map.js'
{Command, CommandList, TextCommand,
 RobotCard, RobotVideo} = require './hud.js'


# HUD control
mountHUD = (robot) ->
    robot.setAuto()
    # commands
    commands =
        path: Command 'line chart', (-> robot.setAuto(); robot.path = on),
            -> robot.path = off
        wasd: Command 'game', (-> robot.setManual()),
            -> robot.setAuto()

    # show streaming
    ReactDOM.render <RobotVideo robot={robot}/>,
        document.getElementById 'streaming'
    # show info
    ReactDOM.render <RobotCard robot={robot}/>,
        document.getElementById 'robot-info-wrapper'

    #load commands
    cmdList = ReactDOM.render <CommandList/>,
        document.getElementById 'commands'
    cmdList.addCommand k, v for k, v of commands

    text = Command 'font', (-> robot.setAuto(); ReactDOM.render <TextCommand
        robot={robot} cmdList={cmdList}/>, document.getElementById 'mode-text'),
        -> ReactDOM.unmountComponentAtNode document.getElementById 'mode-text'
    cmdList.addCommand 'text', text
    # use auto mode as default
    robot.setAuto()

unmountHUD = ->
    # destroy HUD components
    ReactDOM.unmountComponentAtNode(
        document.getElementById 'streaming')
    ReactDOM.unmountComponentAtNode(
        document.getElementById 'robot-info-wrapper')

    ReactDOM.unmountComponentAtNode document.getElementById 'commands'
    delete window.car

map.on 'click', (e) ->
    car = window.car
    console.debug e.latlng.lat, e.latlng.lng
    if car and car.path
        car.setPath [[e.latlng.lat, e.latlng.lng]]
    else unmountHUD()

module.exports =
  mountHUD: mountHUD
