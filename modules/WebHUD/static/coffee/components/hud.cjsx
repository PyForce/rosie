React = require 'react'
MediaQuery = require 'react-responsive'


class RobotCard extends React.Component
  constructor: (@props) ->
    @state =
      x: 0
      y: 0
    super @props

  componentDidMount: ->
    $(@refs.root).transition 'fade left'

  render: ->
    {x, y} = @state
    {thumbnail, name, processor, motor_controller, size} = @props
    {host, port} = @props.robot

    <MediaQuery minWidth={600}>
      <div id='robot-logo' className='ui raised compact segment' ref='root' style={{visibility: 'hidden'}}>
        <img src={"http://#{host}:#{port}#{thumbnail}"} alt="robot"/>
        <ul>
          <li>Robot: {name}</li>
          <li>SBC: {processor}</li>
          <li>Service Board: {motor_controller}</li>
          <li>Dim: {size[1]} x {size[0]} x {size[2]}</li>
          <li>Pos: ({x.toFixed 3}, {y.toFixed 3})</li>
        </ul>
      </div>
    </MediaQuery>


class RobotVideo extends React.Component
  componentDidMount: ->
    $(@refs.root).transition 'fade up'

  render: ->
    {host, streamPort} = @props.robot
    <MediaQuery minWidth={600}>
      <img src={"http://#{host}:#{streamPort}/stream/video.mjpeg"} id='video-streaming'
        alt="streaming" style={{visibility: 'hidden'}} ref='root'/>
    </MediaQuery>


class CommandComponent extends React.Component
  render: ->
    {icon, active} = @props

    <a onClick={@props.run}
      className="item#{if active then ' active basic' else ''}">
      <i className={"icon #{icon}"}></i>
    </a>


class TextOrderInput extends React.Component
  constructor: (@props) ->
    @sendCommand = @sendCommand.bind @
    super @props

  sendCommand: (e) ->
    e.preventDefault()
    # send command to robot
    @props.robot.postCommand @refs.input.value
    @refs.input.value = ''
    @props.cmdList.switchActive 'text', false

  componentDidMount: ->
    @refs.input.focus()

  render: ->
    style =
      position: 'fixed'
      top: '20%'
      left: '30%'
      right: '30%'
      width: '40%'

    <form onSubmit={@sendCommand} className='ui form'>
      <div className="field">
        <input style={style} type='text' ref='input'/>
      </div>
    </form>


module.exports =
  CommandComponent: CommandComponent
  TextOrderInput: TextOrderInput
  RobotCard: RobotCard
  RobotVideo: RobotVideo
