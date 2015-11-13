
$(".icon#settings").click(function() {
    $("#sidebar-left").toggleClass("expanded");
    toggleOverlay($("#sidebar-left").hasClass("expanded"));
});

$("#overlay").click(function() {
    toggleOverlay(false);
    $("#sidebar-left").removeClass("expanded");
});

L.DomEvent.on(imageOverlay._image, 'click', function(e) {
    $("#robot-logo").css("visibility", "visible");
    $("#video-streaming").css("visibility", "visible");
    $("#video-streaming").attr("src", "http://10.0.0.1:8080/stream/video.mjpeg")
});

// L.DomEvent.on(imageOverlay._image, 'mouseout', function(e) {
//     $("#robot-logo").css("visibility", "hidden");
//     $("#video-streaming").css("visibility", "hidden");
//     $("#video-streaming").attr("src", null);
// });

function toggleOverlay(mode) {
    $("#overlay").toggleClass("visible", mode);
}

$(".icon#settings").click(function() {
    $("#sidebar-left").toggleClass("expanded");
    toggleOverlay($("#sidebar-left").hasClass("expanded"));
});

$("#overlay").click(function() {
    toggleOverlay(false);
    $("#sidebar-left").removeClass("expanded");
});

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
