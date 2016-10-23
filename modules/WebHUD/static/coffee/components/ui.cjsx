$ = jQuery = require 'jquery'
React = require 'react'

hudStore = require '../stores/hud'
robotStore = require '../stores/robot'
HUDActions = require '../actions/hud'

{CommandComponent} = require './hud'
{ClusterMenu} = require './cluster'


class TopMenu extends React.Component
  constructor: (@props) ->
    @state =
      path: hudStore.onPath()
      user: hudStore.onUser()
      order: hudStore.onOrder()
      selected: false

    @_onChange = @_onChange.bind @
    @_onSelected = @_onSelected.bind @

    hudStore.addListener @_onChange
    robotStore.addListener @_onSelected
    super @props

  _onChange: ->
    @setState path: hudStore.onPath(), user: hudStore.onUser(), order: hudStore.onOrder()

  _onSelected: ->
    @setState selected: robotStore.selectedRobot()?

  render: ->
    {path, user, order} = @state

    <div className="ui blue top fixed inverted borderless icon menu">
      <a className="header item" onClick={=> $(@props.sidebar).sidebar 'toggle'}>
        <i className="options icon"></i>
      </a>
      {if @state.selected
          [<CommandComponent active={path} run={-> HUDActions.path not path}
            icon='location arrow' key="path"/>,
          <CommandComponent active={user} run={-> HUDActions.user not user}
            icon='user' key="user"/>,
          <CommandComponent active={order} run={-> HUDActions.order not order}
            icon='terminal' key="order"/>]
      }
      <ClusterMenu/>
      <div className="right menu">
        <a className="ui item" onClick={=> $(@props.about).modal 'show'}>
          About
        </a>
      </div>
    </div>


class Sidebar extends React.Component
  render: ->
    <div className="ui sidebar left vertical inverted labeled icon menu" ref="bar">
      <a className="item" onClick={=> $(@props.modal).modal 'show'}>
        <i className="settings icon"></i>
        Settings
      </a>
    </div>


class SettingsModal extends React.Component
  render: ->
    <div className="ui modal" ref="modal">
      <i className="close icon"></i>
      <div className="header">Settings</div>
      <div className="content">Setup the application</div>
    </div>


class AboutModal extends React.Component
  render: ->
    <div className="ui basic modal" ref="modal">
      <i className="close icon"></i>
      <div className="header">About</div>
      <div className="content">
        <div className="description">
          This application it's designed by the <b>PyForce</b> group
        </div>
      </div>
      <div className="actions">
        <div className="ui ok green basic inverted button">
          <i className="checkmark icon"></i>
          Ok
        </div>
      </div>
    </div>


module.exports =
  TopMenu: TopMenu
  Sidebar: Sidebar
  SettingsModal: SettingsModal
  AboutModal: AboutModal
