$ = jQuery = require 'jquery'

$('.ui.menu>.item.options').click ->
    $('.ui.sidebar').sidebar 'toggle'

$('.ui.menu>.right.menu>.item').click ->
    $('.ui.basic.modal').modal 'show'

$('.ui.sidebar>.item.settings').click ->
    $('.ui.settings.modal').modal 'show'

window.jQuery = window.$ = jQuery
