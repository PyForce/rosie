Dispatcher = require '../dispatcher/dispatcher'
RobotActions = require './robot'
{PATH_HUD, ORDER_HUD, USER_HUD} = require './types'


_singleDispath = (type, value) ->
    Dispatcher.dispatch
        type: type
        value: value


class HUDActions
    @path: (value=true) ->
        robot = robotStore.selectedRobot()
        if robot
            RobotActions.auto robot, value if value

            _singleDispath PATH_HUD, value

    @order: (value=true) ->
        robot = robotStore.selectedRobot()
        if robot
            RobotActions.auto robot, value if value

            _singleDispath ORDER_HUD, value

    @user: (value=true) ->
        robot = robotStore.selectedRobot()
        if robot
            RobotActions.auto robot, not value

            _singleDispath USER_HUD, value


module.exports = HUDActions

robotStore = require '../stores/robot'
