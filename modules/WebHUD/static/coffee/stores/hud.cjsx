FluxStore = require 'flux/lib/FluxStore'
React = require 'react'
ReactDOM = require 'react-dom'

Dispatcher = require '../dispatcher/dispatcher'
actionTypes = require '../actions/types'
{RobotCard, RobotVideo} = require '../components/hud'


_path = false
_order = false
_user = false


class HUDStore extends FluxStore
    onPath: -> _path

    onOrder: -> _order

    onUser: -> _user

    onDefault: -> not (_path or _order or _user)

    __onDispatch: (action) ->
        switch action.type
            when actionTypes.PATH_HUD
                _path = action.value
                _order = _user = false if _path
                @__emitChange()

            when actionTypes.ORDER_HUD
                _order = action.value
                _path = _user = false if _order
                @__emitChange()

            when actionTypes.USER_HUD
                _user = action.value
                _path = _order = false if _user
                @__emitChange()

            when actionTypes.CLICK_ROBOT
                # show streaming
                ReactDOM.render <RobotVideo robot={action.robot}/>,
                    document.getElementById 'streaming'
                # show info
                action.robot.getMetadata (data) ->
                    ReactDOM.render <RobotCard robot={action.robot} {...data}/>,
                        document.getElementById 'robot-info-wrapper'

            when actionTypes.CLICK_MAP
                unless _path
                    ReactDOM.unmountComponentAtNode document.getElementById 'streaming'
                    ReactDOM.unmountComponentAtNode document.getElementById 'robot-info-wrapper'
            else return
        return


module.exports = new HUDStore Dispatcher
