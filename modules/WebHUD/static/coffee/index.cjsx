$ = jQuery = require 'jquery'
React = require 'react'
ReactDOM = require 'react-dom'

RobotActions = require './actions/robot'
MapActions = require './actions/map'

{TopMenu, Sidebar, SettingsModal, AboutModal} = require './components/ui'


about = ReactDOM.render <AboutModal/>, document.getElementById 'about'
settings = ReactDOM.render <SettingsModal/>, document.getElementById 'settings'
sidebar = ReactDOM.render <Sidebar modal={settings.refs.modal}/>, document.getElementById 'sidebar'
ReactDOM.render <TopMenu sidebar={sidebar.refs.bar} about={about.refs.modal}/>,
    document.getElementById 'menu'


# local robot
robot = RobotActions.add()
robot.getRequest 'map', (data) ->
    MapActions.update data

window.jQuery = window.$ = jQuery
