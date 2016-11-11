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

    @path: (robot, path=null) ->
        if path
            robot.setPath path
            return
        path = mapStore.getPath().map (e) -> [e.lat, e.lng]
        robot.setPath path

        Dispatcher.dispatch
            type: actionTypes.PATH_ROBOT
            robot: robot
            path: path

    @keys: (data) ->
        Dispatcher.dispatch
            type: actionTypes.KEYS_ROBOT
            keys: data


module.exports = RobotActions

mapStore = require '../stores/map'
