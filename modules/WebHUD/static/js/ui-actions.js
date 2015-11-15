$(".clickable#menu").click(function() {
    $(".side-bar").toggleClass("transition-out");
    toggleOverlay(!$(".side-bar").hasClass("transition-out"));
});

$("#overlay").click(function() {
    if ($("#settings-dialog").hasClass('transition-in'))
        toggleOverlay(false);
    $(".side-bar").addClass("transition-out");
});

$(".clickable#settings").click(function(){
    $(".side-bar").addClass("transition-out");
    $("#settings-dialog").removeClass('transition-in');
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
