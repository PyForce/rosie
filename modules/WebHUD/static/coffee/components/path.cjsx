React = require 'react'
ReactDOM = require 'react-dom'

RobotActions = require '../actions/robot'


class PathConfig extends React.Component
    constructor: (@props) ->
        @sendPath = @sendPath.bind @
        super @props

    sendPath: ->
        interpolation = this.refs.interpolation.value
        console.log interpolation
        # RobotActions.path robotStore.selectedRobot(), interpolation

    render: ->
        <div className='ui raised compact segment' style={width: '200px'}>
            <div className='ui grid'>
                <div className="one column row">
                    <div className="two wide column">
                        <div className="ui labeled input">
                            <a className="ui basic label">Interpolation:</a>
                            <select className="ui selection dropdown" ref="interpolation">
                                <option value="cubic">Cubic</option>
                                <option value="linear">Linear</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div className="one column row">
                    <div className="two wide column">
                        <div className="ui toggle checkbox">
                            <input type="checkbox" name="smooth"></input>
                            <label>Smooth</label>
                        </div>
                    </div>
                </div>
                <div className="row">
                    <div className="column">
                        <button className='ui blue fluid button' onClick={@sendPath}>Go</button>
                    </div>
                </div>
            </div>
        </div>


module.exports =
    PathConfig: PathConfig
