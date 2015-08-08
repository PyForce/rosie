$(document).ready(function() {
    // MENU
    $('#i-menu').click(function() {
        $('#settings').hide();
        $('#menu').toggle();
    });

    // SETTINGS
    $('#i-settings').click(function() {
        $('#menu').hide();
        $('#settings').toggle();
    });

    // TOGGLE MENU/SETTINGS
    $('.list-menu a').click(function() {
        $('.list-menu').hide();
    });

    // MODE (TEXT)
    $('#m-item1, #i-text').click(function() {
        $('#mode-text').toggle(true);
        $("#video-streaming").css("margin-bottom", "60px");
        setAutoMode();
    });

    $('#btn-order').click(function() {
        setText(undefined, $("#text-order").val());
    })

    $("#form-text").submit(function(event) {
        event.preventDefault();
    });

    // KEY
    $('#m-item2, #i-key').click(function() {
        $('#mode-text').hide();
        $("#video-streaming").css("margin-bottom", "10px");
        setManualMode();
    });

    // P2P
    $('#m-item3, #i-p2p').click(function() {
        $('#mode-text').hide();
        $("#video-streaming").css("margin-bottom", "10px");
    });

    // CAMERA
    $('#m-item4').click(function() {
        $('#video-streaming').toggle();
    });

    $('.icon').click(function() {
        $('.icon').removeClass('active');
        $(this).addClass('active');
    });

    setInterval(function(){
		getOdometry(undefined, function(pos){
			car.setLatLng([pos.x, pos.y]);
			//car.setAngle(pos.theta*180/Math.pi); // converting to degrees
			car.setAngle(pos.theta);
		});
	}, 100);
});
