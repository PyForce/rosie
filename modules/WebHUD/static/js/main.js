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
    });

    $('#btn-order').click(function() {
        setText(undefined, 'Hi my bro');
    })

    // KEY
    $('#m-item2, #i-key').click(function() {
        $('#mode-text').hide();
        $("#video-streaming").css("margin-bottom", "10px");
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
});
