$ = jQuery = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'

RobotActions = require './actions/robot'
MapActions = require './actions/map'
robotStore = require './stores/robot'

{TopMenu, Sidebar, SettingsModal, AboutModal} = require './components/ui'
{RobotVideo, RobotCard} = require './components/hud'


about = ReactDOM.render <AboutModal/>, document.getElementById 'about'
settings = ReactDOM.render <SettingsModal/>, document.getElementById 'settings'
sidebar = ReactDOM.render <Sidebar modal={settings.refs.modal}/>, document.getElementById 'sidebar'
ReactDOM.render <TopMenu sidebar={sidebar.refs.bar} about={about.refs.modal}/>,
    document.getElementById 'menu'


# local robot
robot = RobotActions.add()
robot.getRequest 'map', (data) ->
    MapActions.update data


robotStore.addListener ->
    if robotStore.selectedRobot()
        robot = robotStore.selectedRobot()
        # show streaming
        ReactDOM.render <RobotVideo robot={robot}/>,
            document.getElementById 'streaming'
        # show info
        robot.getMetadata (data) ->
            ReactDOM.render <RobotCard robot={robot} {...data}/>,
                document.getElementById 'robot-info-wrapper'
    else
        ReactDOM.unmountComponentAtNode document.getElementById 'streaming'
        ReactDOM.unmountComponentAtNode document.getElementById 'robot-info-wrapper'


window.jQuery = window.$ = jQuery
