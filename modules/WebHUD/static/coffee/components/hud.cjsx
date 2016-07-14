
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
    <div id='robot-logo' className="ui raised compact segment">
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
Command = (icon, onAction, offAction) ->
  icon: icon
  onAction: onAction
  offAction: offAction
  active: false


CommandComponent = React.createClass
  run: ->
    if not @props.active
      @props.onAction()
      @props.switchActive @props._key, true
    else
      @props.switchActive @props._key, false
      if @props.offAction
        @props.offAction()

  render: ->
    {icon, active} = @props
    <li>
      <a className={"icon#{if active then ' active' else ''}"} onClick={@run}>
        <img src={icon} alt="cmd" className="shadow-map"/>
      </a>
    </li>

class CommandList extends React.Component
  constructor: (@props) ->
    @state = commands: {}
    super @props

  switchActive: (key, val) ->
    nCommands = {}
    for k, cmd of @state.commands
      do (k, cmd) ->
        if k == key
          cmd.active = val
        else if val  # deactivate only if activating
          cmd.active = false
          cmd.offAction() if cmd.offAction # invoke off
        nCommands[k] = cmd
    @setState commands: nCommands

  addCommand: (key, command) ->
    @state.commands[key] = command
    @setState commands: @state.commands

  render: ->
    <div className="commands">
      <ul className="commands-list">
        {<CommandComponent key={k} _key={k} {...cmd}
          switchActive={@switchActive.bind @}/> for k, cmd of @state.commands}
      </ul>
    </div>
