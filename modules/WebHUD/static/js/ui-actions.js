$('.icon').click(function() {
    var wasActive = $(this).hasClass('active');
    $('.icon').removeClass('active');
    if (!wasActive)
        $(this).addClass('active');
});

// KEY
$('#m-item2, #key').click(function() {
    toggleTransition($('#mode-text'), true)
    // $("#video-streaming").css("margin-bottom", "10px");
    setManualMode();
});

// P2P
$('#m-item3, #p2p').click(function() {
    toggleTransition($('#mode-text'), true);
    // $("#video-streaming").css("margin-bottom", "10px");
});

// MODE (TEXT)
$('#m-item1, #text').click(function() {
    toggleTransition($('#mode-text'));
    // $("#video-streaming").css("margin-bottom", "60px");
    setAutoMode();
});

// CAMERA
$('#m-item4').click(function() {
    $('#video-streaming').toggle();
});

$(".clickable#menu").click(function() {
    var sbar = $(".side-bar");
    toggleTransition(sbar);
    toggleOverlay(!sbar.hasClass(sbar.data('transition')));
});

$("#overlay").click(function() {
    var settings = $("#settings-dialog");
    if (settings.hasClass(settings.data('transition')))
        toggleOverlay(false);
    toggleTransition($(".side-bar"), true);
});

$(".clickable#settings").click(function() {
    toggleTransition($(".side-bar"), true);
    openDialog($("#settings-dialog"));
});

$('.clickable#about').click(function() {
    openDialog($('#about-dialog'));
})

$('.cancel-btn, .close, .ok-btn').click(function() {
    var open = $('.open-dialog');
    toggleTransition(open, true);
    open.removeClass('open-dialog');
    toggleOverlay(false, true);
});

/*
L.DomEvent.on(imageOverlay._image, 'click', function(e) {
    $("#robot-logo").css("visibility", "visible");
    $("#video-streaming").css("visibility", "visible");
    $("#video-streaming").attr("src", "http://10.0.0.1:8080/stream/video.mjpeg")
});
*/

// L.DomEvent.on(imageOverlay._image, 'mouseout', function(e) {
//     $("#robot-logo").css("visibility", "hidden");
//     $("#video-streaming").css("visibility", "hidden");
//     $("#video-streaming").attr("src", null);
// });

function toggleTransition(elem, val) {
    elem.toggleClass(elem.data('transition'), val);
}

function toggleOverlay(mode, dim) {
    var overlay = $("#overlay");
    if (dim)
        overlay.addClass('dim');
    else overlay.removeClass('dim');
    overlay.toggleClass("visible", mode);
}

function openDialog (dialog) {
    toggleTransition(dialog, false);
    dialog.addClass('open-dialog');
    toggleOverlay(true, true);
}

/*
imageOverlay.on("mouseover", function() {
    $("#robot-logo").css("visibility", "visible");
    $("#video-streaming").css("visibility", "visible");
    $("#video-streaming").attr("src", "http://10.0.0.1:8080/stream/video.mjpeg")
});

imageOverlay.on("mouseout", function() {
    $("#robot-logo").css("visibility", "hidden");
    $("#video-streaming").css("visibility", "hidden");
    $("#video-streaming").attr("src", null);
});
*/
