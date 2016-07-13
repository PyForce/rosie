$(document).ready () ->
    # MENU
    $('#i-menu').click () ->
        $('#settings').hide()
        $('#menu').toggle()

    # SETTINGS
    $('#i-settings').click () ->
        $('#menu').hide()
        $('#settings').toggle()

    # TOGGLE MENU/SETTINGS
    $('.list-menu a').click () ->
        $('.list-menu').hide()

    $('#btn-order').click () ->
        setText undefined, $("#text-order").val()

    $("#form-text").submit (event) ->
        setText undefined, $("#text-order").val()
        event.preventDefault()

    setInterval () ->
        car.getOdometry (pos) ->
            # car.setLatLng [pos.x, pos.y]
            # car.setAngle(pos.theta*180/Math.pi) # converting to degrees
            # car.setAngle(pos.theta)
            car.move pos
    , 100

DEBUG = false
