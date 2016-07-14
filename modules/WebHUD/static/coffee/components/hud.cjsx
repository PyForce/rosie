
class RobotCard extends React.Component
  constructor: (@props) ->
    @state =
      photo: ''
      name: ''
      processor: ''
      motor_controller: ''
      size: [0, 0, 0]
      x: 0
      y: 0
      manual: @props.robot.manual
    @props.robot.attachInfo @
    super @props

  componentWillUnmount: ->
    @props.robot.dettachInfo()

  render: ->
    {photo, name, processor, motor_controller, size, x, y} = @state
    <div id='robot-logo' className="shadow-map">
      <img src={photo} alt="robot"/>
      <ul>
        <li>Robot: {name}</li>
        <li>SBC: {processor}</li>
        <li>Service Board: {motor_controller}</li>
        <li>Dim: {size[0]} x {size[1]} x {size[2]}</li>
        <li>Pos: ({x.toFixed 3}, {y.toFixed 3})</li>
        <li>WiFi: none</li>
        <li>Mode: {if @state.manual then 'Manual' else 'Auto'}</li>
      </ul>
    </div>


class RobotVideo extends React.Component
  render: ->
    {host, streamPort} = @props.robot
    <img src={"http://#{host}:#{streamPort}/stream/video.mjpeg"}
      alt="streaming"/>

# Wrapper for command object
Command = (icon, key, onAction, offAction) ->
  icon: icon
  key: key
  onAction: onAction
  offAction: offAction


CommandComponent = React.createClass
  getInitialState: ->
    active: false

  run: ->
    @setState (prevState) ->
      active: !prevState.active
    if not @state.active
      @props.onAction()
    else if @props.offAction
      @props.offAction()


  render: ->
    {icon} = @props
    {active} = @state
    <li>
      <a className={"icon#{if active then ' active' else ''}"} onClick={@run}>
        <img src={icon} alt="cmd" className="shadow-map"/>
      </a>
    </li>

class CommandList extends React.Component
  render: ->
    <div className="commands">
      <ul className="commands-list">
        {<CommandComponent {...cmd}/> for cmd in @props.commands}
      </ul>
    </div>
