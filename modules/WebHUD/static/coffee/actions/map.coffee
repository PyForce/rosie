Dispatcher = require '../dispatcher/dispatcher'
{CLICK_MAP, UPDATE_MAP} = require './types'


class MapActions
    @click: (latlng) ->
        Dispatcher.dispatch
            type: CLICK_MAP
            latlng: latlng

    @update: (newmap) ->
        Dispatcher.dispatch
            type: UPDATE_MAP
            map: newmap


module.exports = MapActions
