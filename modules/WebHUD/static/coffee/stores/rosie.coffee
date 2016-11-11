FluxStore = require 'flux/lib/FluxStore'


class RosieStore extends FluxStore
    removeCurrentListener: ->
        @__emitter.removeCurrentListener()


module.exports = RosieStore
