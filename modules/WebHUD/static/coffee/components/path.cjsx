L = require 'leaflet'
React = require 'react'
ReactDOM = require 'react-dom'

RobotActions = require '../actions/robot'
robotStore = require '../stores/robot'
mapStore = require '../stores/map'

{map} = require '../map'


class PathConfig extends React.Component
    constructor: (@props) ->
        @sendPath = @sendPath.bind @
        @removeMarkers = @removeMarkers.bind @
        @markers = []
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
        mapStore.addListener =>
            if @removed # notified to stop listening
                mapStore.removeCurrentListener()
                return

            path = mapStore.getPath()
            if not path.length and @markers.length
                # remove remaining markers after disabling path mode
                @removeMarkers()
                return
            return if not path.length  # all point removed, nothing to do
            # the path has been reset, drop markers(if any) and mark the last(only) one
            @removeMarkers() if path.length == 1

            pos = path[path.length - 1]
            circle = L.circle(pos, .02,
                color: 'red'
                fillColor: '#f03'
                fillOpacity: .5).addTo map
            # circle.bindTooltip("#{pos.lat.toFixed 3}, #{pos.lng.toFixed 3}").openTooltip()
            @markers.push circle
            return
        return

    removeMarkers: ->
        map.removeLayer marker for marker in @markers

    componentWillUnmount: ->
        @removed = true
        @removeMarkers()

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
                        <input type="number" placeholder="Time = 10" ref="time"/>
                        <div className="ui basic label">sec</div>
                    </div>
                </div>
                <div className="column">
                    <div className="ui fluid input">
                        <input type="number" placeholder="k = 0.1" ref="k"/>
                    </div>
                </div>
                <div className="column">
                    <button className='ui fluid green button' onClick={@sendPath}>Go</button>
                </div>
            </div>
        </div>


module.exports =
    PathConfig: PathConfig
