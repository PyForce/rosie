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
    var settings = $("#settings-dialog");
    toggleTransition(settings, false);
    settings.addClass('open-dialog');
});

$('.cancel-btn, .close').click(function(){
    var open = $('.open-dialog');
    toggleTransition(open, true);
    open.removeClass('open-dialog');
    toggleOverlay(false);
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

function toggleOverlay(mode) {
    $("#overlay").toggleClass("visible", mode);
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
