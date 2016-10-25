L = require 'leaflet'
FluxStore = require 'flux/lib/FluxStore'

Dispatcher = require '../dispatcher/dispatcher'
actionTypes = require '../actions/types'
robotStore = require './robot'
{drawMap, map} = require '../map'


_popup = L.popup()
# points from trajectory
_path = []


class MapStore extends FluxStore
    getPath: -> _path

    __onDispatch: (action) ->
        switch action.type
            when actionTypes.UPDATE_MAP
                Dispatcher.waitFor [robotStore.getDispatchToken()]
                drawMap action.map

            when actionTypes.CLICK_MAP
                # show a popup to print coordiantes
                _popup.setLatLng(action.latlng)
                    .setContent("Goto #{action.latlng}")
                    .openOn map
                # update trajectory
                _path.push action.latlng
                @__emitChange()
            else return


module.exports = new MapStore Dispatcher
