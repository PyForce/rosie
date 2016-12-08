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
            position: {x: pos.y, y: pos.x, theta: -pos.theta}

    @path: (robot, path=null, smooth=False, interpolation='linear', k=0.1,
            time=10) ->
        if path
            robot.setPath path
            return
        # TODO: read the time for each point and place where 0
        path = mapStore.getPath().map (e) -> [e.lng, e.lat, 0]
        robot.setPath path, smooth, interpolation, k, time

        Dispatcher.dispatch
            type: actionTypes.PATH_ROBOT
            robot: robot
            path: path

    @keys: (data) ->
        Dispatcher.dispatch
            type: actionTypes.KEYS_ROBOT
            keys: data

    @command: (robot, text) ->
        robot.postCommand text

        Dispatcher.dispatch
            type: actionTypes.CMD_ROBOT
            text: text


module.exports = RobotActions

mapStore = require '../stores/map'
