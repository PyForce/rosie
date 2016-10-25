Dispatcher = require '../dispatcher/dispatcher'
actionTypes = require './types'
Robot = require '../robot'


class RobotActions
    @auto: (robot, value=true) ->
        if value
            robot.setAuto()
        else robot.setManual()

    @add: (info) ->
        robot = new Robot info

        Dispatcher.dispatch
            type: actionTypes.ADD_ROBOT
            robot: robot
        # return the newly created robot
        return robot

    @remove: (robot) ->
        Dispatcher.dispatch
            type: actionTypes.RM_ROBOT
            robot: robot

    @click: (robot) ->
        Dispatcher.dispatch
            type: actionTypes.CLICK_ROBOT
            robot: robot

    @move: (robot, pos) ->
        Dispatcher.dispatch
            type: actionTypes.MOVE_ROBOT
            robot: robot
            position: pos


module.exports = RobotActions
