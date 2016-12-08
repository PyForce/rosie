L = require 'leaflet'

RosieStore = require './rosie'
Dispatcher = require '../dispatcher/dispatcher'
actionTypes = require '../actions/types'
robotStore = require './robot'
hudStore = require './hud'
{drawMap, map} = require '../map'


_popup = L.popup()
# points from trajectory
_path = []
# used to notify if next click will reset path or not
resetPath = false


class MapStore extends RosieStore
    getPath: -> _path

    clearPath: -> _path = []

    __onDispatch: (action) ->
        switch action.type
            when actionTypes.UPDATE_MAP
                Dispatcher.waitFor [robotStore.getDispatchToken()]
                drawMap action.map

            when actionTypes.CLICK_MAP
                # show a popup to print coordiantes
                # _popup.setLatLng(action.latlng)
                #       .setContent("Goto #{action.latlng}")
                #       .openOn map
                # update trajectory
                if resetPath
                    _path = [action.latlng]
                    resetPath = false
                else
                    _path.push action.latlng
                @__emitChange()

            when actionTypes.PATH_HUD
                Dispatcher.waitFor [hudStore.getDispatchToken()]
                # clear path
                # return if not action.value
                _path = []
                @__emitChange()

            when actionTypes.PATH_ROBOT
                Dispatcher.waitFor [robotStore.getDispatchToken()]
                resetPath = true
            else return


module.exports = new MapStore Dispatcher
