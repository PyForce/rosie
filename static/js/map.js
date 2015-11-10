// function rotate (theta, x) {
//     // cos sin
//     // -sin cos
//     return [Math.cos(theta) * x.lat + Math.sin(theta) * x.lng,
//            -Math.sin(theta) * x.lat + Math.cos(theta) * x.lng];
// }

var map = L.map('map').setView([0, 0], 5);

var url = "assets/images/LTL_min1.png";
var imagebounds = [
    [-10, -10],
    [10, 22]
];
var imageOverlay = L.imageOverlay(url, imagebounds).addTo(map);

var plottedPolyline = L.Polyline.Plotter([
        [0,6]        
    ],{
        weight: 5,
		readOnly: true,		
    }).addTo(map);

//function plot(enable){
//	if(enable)plottedPolyline.
//}

var readOnly = true;
$("#plot").click(function(){
        readOnly = !readOnly;
        plottedPolyline.setReadOnly(readOnly);
});
	
L.DomEvent.on(imageOverlay._image, 'mouseenter', function(e) {
    $("#robot-logo").css("visibility", "visible");
    $("#video-streaming").css("visibility", "visible");
    $("#video-streaming").attr("src", "http://10.0.0.1:8080/stream/video.mjpeg")
});

L.DomEvent.on(imageOverlay._image, 'mouseout', function(e) {
    $("#robot-logo").css("visibility", "hidden");
    $("#video-streaming").css("visibility", "hidden");
    $("#video-streaming").attr("src", null);
});
