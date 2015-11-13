var map = L.map('map', {
    crs: L.CRS.Simple,
    zoomAnimation: false
}).setView([0, 0], 5);

var imageUrl = "static/images/LTL_min1.png";
var imagebounds = [
    [-10, -10],
    [10, 22]
];

var width = 20;
var height = 32;
var coords = [0, 0];


L.DomUtil.setTransform = function(el, offset, scale, angle) {
    var pos = offset || new L.Point(0, 0);

    el.style[L.DomUtil.TRANSFORM] =
        (L.Browser.ie3d ?
        'translate(' + pos.x + 'px,' + pos.y + 'px)' :
        'translate3d(' + pos.x + 'px,' + pos.y + 'px,0)') +
        (angle ? ' rotate(' + angle + 'deg)' : '') +
        (scale ? ' scale(' + scale + ')' : '');
};

L.DomUtil.setPosition = function(el, point, angle) { // (HTMLElement, Point[, Boolean])

    /*eslint-disable */
    el._leaflet_pos = point;
    /*eslint-enable */

    if (L.Browser.any3d) {
        L.DomUtil.setTransform(el, point, undefined, angle);
    } else {
        el.style.left = point.x + 'px';
        el.style.top = point.y + 'px';
    }
}

L.MyImageOverlay = L.ImageOverlay.extend({

    initialize: function(imageUrl, latlng, width, height, options) {
        this._url = imageUrl;
        this._latlng = L.latLng(latlng);
        this._width = width;
        this._height = height;
        this._angle = 45;

        this._recalcBounds();
        L.setOptions(this, options);

    },


    _recalcBounds: function() {
        var x1 = [this._latlng.lat - this._width / 2, this._latlng.lng - this._height / 2];
        var x2 = [this._latlng.lat + this._width / 2, this._latlng.lng + this._height / 2];

        var bounds = [x1, x2];

        this._bounds = L.latLngBounds(bounds);
    },

    _reset: function() {
        var image = this._image,
            bounds = new L.Bounds(
                this._map.latLngToLayerPoint(this._bounds.getNorthWest()),
                this._map.latLngToLayerPoint(this._bounds.getSouthEast())),
            size = bounds.getSize();

        L.DomUtil.setPosition(image, bounds.min, this._angle);

        image.style.width = size.x + 'px';
        image.style.height = size.y + 'px';
    },

    setAngle: function(angle) {
        this._angle = angle;

        this._reset();
    },

    getAngle: function(angle) {
        return _angle;
    },

    setLatLng: function(latlng) {
        var oldLatLng = this._latlng;
        this._latlng = L.latLng(latlng);

        this._recalcBounds();

        if (this._map) {
            this._reset();
        }

        if (L.DomUtil.TRANSFORM) {
            // use the CSS transform rule if available
            this._image.style[L.DomUtil.TRANSFORM] += ' rotate(' + this.options.angle + 'deg)';
        }

        return this.fire('move', {
            oldLatLng: oldLatLng,
            latlng: this._latlng
        });
    },

    getLatLng: function() {
        return this._latlng;
    }
})

L.myImageOverlay = function(imageUrl, coords, width, height, options) {
    return new L.MyImageOverlay(imageUrl, coords, width, height, options);
}


car = L.myImageOverlay(imageUrl, coords, width, height).addTo(map);

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
