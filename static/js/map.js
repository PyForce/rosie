var map = L.map('map').setView([0, 0], 5);

var url = "static/images/LTL_min1.png";
var imagebounds = [
    [-10, -10],
    [10, 22]
];

var imageOverlay = L.imageOverlay(url, imagebounds).addTo(map);

var plottedPolyline = L.Polyline.Plotter([
    [0, 6]
], {
    weight: 5,
    readOnly: true,
}).addTo(map);

var readOnly = true;
$("#i-p2p").click(function() {
    readOnly = !readOnly;
    plottedPolyline.setReadOnly(readOnly);
});

/*
// function rotate (theta, x) {
//     // cos sin
//     // -sin cos
//     return [Math.cos(theta) * x.lat + Math.sin(theta) * x.lng,
//            -Math.sin(theta) * x.lat + Math.cos(theta) * x.lng];
// }

var map = L.map('map').setView([0, 0], 5);
var botpos = [0, 0];
var botsize = [
    [-10, -10],
    [10, 22]
];

var trajectory = L.Polyline.Plotter([
    [0, 0]
], {
    weight: 5,
    readOnly: true,
}).addTo(map);

var url = "assets/images/LTL_min1.png";
var imageOverlay;

function gettrayectory() {
    return trajectory.getLatLngs();
}

function updatebotpostrajectory(bot_pos) {
    botpos[0] = bot_pos[0];
    botpos[1] = bot_pos[1];

    var imagebounds = [
        [botsize[0][0] + botpos[0], botsize[0][1] + botpos[1]],
        [botsize[1][0] + botpos[0], botsize[1][1] + botpos[1]]
    ];

    if (typeof imageOverlay !== 'undefined') {
        map.removeLayer(imageOverlay);
    }

    imageOverlay = L.imageOverlay(url, imagebounds).addTo(map);
    imageOverlay.bringToBack();

    var tr = gettrayectory();
    tr[0] = botpos;
    trajectory.setLatLngs(tr);
}

function reach(index) { // eliminar los primeros index nodos de la ruta
};

updatebotpostrajectory([0, 0]);

var readOnly = true;
$("#plot").click(function() {
    readOnly = !readOnly;
    trajectory.setReadOnly(readOnly);
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
*/
