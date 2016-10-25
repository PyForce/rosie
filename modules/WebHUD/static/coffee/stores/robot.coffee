FluxStore = require 'flux/lib/FluxStore'

Dispatcher = require '../dispatcher/dispatcher'
actionTypes = require '../actions/types'
hudStore = require './hud'


_robots = []
_selected = null


class RobotStore extends FluxStore
    selectedRobot: -> _selected

    allRobots: -> _robots

    __onDispatch: (action) ->
        switch action.type
            when actionTypes.CLICK_ROBOT
                _selected = action.robot
                @__emitChange()

            when actionTypes.ADD_ROBOT
                _robots.push action.robot
                @__emitChange()

            when actionTypes.RM_ROBOT
                idx = _robots.indexOf action.robot
                _robots.splice idx, 1 if idx >= 0
                @__emitChange()

            when actionTypes.MOVE_ROBOT
                action.robot.overlay.setLatLng [action.position.x, action.position.y]
                action.robot.overlay.setAngle action.position.theta

            when actionTypes.UPDATE_MAP
                # TODO: create this function
                robot.setMap action.map for robot in _robots

            when actionTypes.CLICK_MAP
                _selected = null unless hudStore.onPath()
                @__emitChange()
            else return


module.exports = new RobotStore Dispatcher
