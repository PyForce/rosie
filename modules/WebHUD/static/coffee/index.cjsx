$ = jQuery = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'

RobotActions = require './actions/robot'
MapActions = require './actions/map'
robotStore = require './stores/robot'
hudStore = require './stores/hud'
mapStore = require './stores/map'

{TopMenu, Sidebar, SettingsModal, AboutModal} = require './components/ui'
{RobotVideo, RobotCard, TextOrderInput} = require './components/hud'
{PathConfig} = require './components/path'


about = ReactDOM.render <AboutModal/>, document.getElementById 'about'
settings = ReactDOM.render <SettingsModal/>, document.getElementById 'settings'
sidebar = ReactDOM.render <Sidebar modal={settings.refs.modal}/>, document.getElementById 'sidebar'
ReactDOM.render <TopMenu sidebar={sidebar.refs.bar} about={about.refs.modal}/>,
    document.getElementById 'menu'


# local robot
robot = RobotActions.add()
robot.getRequest 'map', (data) ->
    MapActions.update data


# robot info ui handler
class InfoHandler
    robotStore.addListener ->
        if robotStore.selectedRobot()
            InfoHandler.mount()
        else
            InfoHandler.unmount()

    hudStore.addListener ->
        return if not hudStore.onDefault()
        InfoHandler.mount()

    @mount: ->
        robot = robotStore.selectedRobot()
        # show streaming
        ReactDOM.render <RobotVideo robot={robot}/>,
            document.getElementById 'right-ui'
        # show info
        robot.getMetadata (data) ->
            ReactDOM.render <RobotCard robot={robot} {...data}/>,
                document.getElementById 'left-ui'

    @unmount: ->
        ReactDOM.unmountComponentAtNode document.getElementById 'left-ui'
        ReactDOM.unmountComponentAtNode document.getElementById 'right-ui'


# path mode handler
hudStore.addListener ->
    return if not hudStore.onPath()
    ReactDOM.render <PathConfig/>,
        document.getElementById 'left-ui'
    hudStore.addListener ->
        return if hudStore.onPath()
        ReactDOM.unmountComponentAtNode document.getElementById 'left-ui'
        hudStore.removeCurrentListener()


# text command handler
hudStore.addListener ->
    return if not hudStore.onOrder()
    ReactDOM.render <TextOrderInput/>, document.getElementById 'center-ui'
    hudStore.addListener ->
        return if hudStore.onOrder()
        ReactDOM.unmountComponentAtNode document.getElementById 'center-ui'
        hudStore.removeCurrentListener()


# key handler
class KeyHandler
    @pressed = new Set()

    hudStore.addListener ->
        if hudStore.onUser()
            # add key handling events
            $(document.body).on 'keydown.robot', (e) =>
                # 87 -> W
                # 65 -> A
                # 83 -> S
                # 68 -> D

                # 81 -> Q
                # 69 -> E

                KeyHandler.pressed.add e.which if e.which in [87, 65, 83, 68, 81, 69]
                KeyHandler.sendKeys()

            $(document.body).on 'keyup.robot', (e) =>
                KeyHandler.pressed.delete e.which
                KeyHandler.sendKeys()
        else
            $(document.body).off 'keydown.robot'
            $(document.body).off 'keyup.robot'

    @sendKeys: ->
        l = []
        KeyHandler.pressed.forEach (e) -> l.push e
        RobotActions.keys l


window.jQuery = window.$ = jQuery
