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