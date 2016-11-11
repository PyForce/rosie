React = require 'react'
ReactDOM = require 'react-dom'

RosieStore = require './rosie'
Dispatcher = require '../dispatcher/dispatcher'
actionTypes = require '../actions/types'


_path = false
_order = false
_user = false


class HUDStore extends RosieStore
    onPath: -> _path

    onOrder: -> _order

    onUser: -> _user

    onDefault: -> not (_path or _order or _user)

    __onDispatch: (action) ->
        switch action.type
            when actionTypes.PATH_HUD
                return if _path == action.value
                _path = action.value
                _order = _user = false if _path
                @__emitChange()

            when actionTypes.ORDER_HUD
                return if _order == action.value
                _order = action.value
                _path = _user = false if _order
                @__emitChange()

            when actionTypes.USER_HUD
                return if _user == action.value
                _user = action.value
                _path = _order = false if _user
                @__emitChange()
            else return
        return


module.exports = new HUDStore Dispatcher
