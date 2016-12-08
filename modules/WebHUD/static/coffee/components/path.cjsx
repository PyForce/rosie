React = require 'react'
ReactDOM = require 'react-dom'

RobotActions = require '../actions/robot'
robotStore = require '../stores/robot'


class PathConfig extends React.Component
    constructor: (@props) ->
        @sendPath = @sendPath.bind @
        super @props

    sendPath: ->
        k = this.refs.k.valueAsNumber
        time = this.refs.time.valueAsNumber

        RobotActions.path robotStore.selectedRobot(), null,
            this.refs.smooth.checked,
            this.refs.interpolation.value or 'linear',
            if isNaN k then 0.1 else k,
            if isNaN time then 10 else time
        return

    componentDidMount: ->
        # $(this.refs.interpolation).popup content: "Interpolation"
        $(this.refs._dropdown).dropdown()
        return

    render: ->
        <div className='ui raised segment' style={width: '300px'}>
            <div className='ui one column grid'>
                <div className="column">
                    <div className="ui sub header">Interpolation</div>
                    <div className="ui fluid selection dropdown" ref="_dropdown">
                      <input type="hidden" ref="interpolation"/>
                      <i className="dropdown icon"></i>
                      <div className="default text">Interpolation</div>
                      <div className="menu">
                        <div className="item" data-value="cubic">Cubic</div>
                        <div className="item" data-value="linear">Linear</div>
                      </div>
                    </div>
                </div>
                <div className="column">
                    <div className="ui toggle checkbox">
                        <input type="checkbox" ref="smooth"/>
                        <label>Smooth</label>
                    </div>
                </div>
                <div className="column">
                    <div className="ui fluid right labeled input">
                        <input type="number" placeholder="Time" ref="time"/>
                        <div className="ui basic label">sec</div>
                    </div>
                </div>
                <div className="column">
                    <div className="ui fluid input">
                        <input type="number" placeholder="k" ref="k"/>
                    </div>
                </div>
                <div className="column">
                    <button className='ui fluid green button' onClick={@sendPath}>Go</button>
                </div>
            </div>
        </div>


module.exports =
    PathConfig: PathConfig
