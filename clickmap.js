

var map = L.map('map').setView([51.505, -0.09], 12);
L.tileLayer('https://api.mapbox.com/styles/v1/bardzobardzo/clgg7lng500vu01oannips1iw/tiles/256/{z}/{x}/{y}@2x?access_token=YOUR_MAPBOX_TOKEN', {
  maxZoom: 19,
  attribution: '&copy; <a href="http://www.mapbox.com">Mapbox</a>'
}).addTo(map);



map.panTo(data)
var popup = L.popup();
var greenIcon = L.icon({
    iconUrl: 'leaf-green.png',
    shadowUrl: 'leaf-shadow.png',

    iconSize:     [38, 95], // size of the icon
    shadowSize:   [50, 64], // size of the shadow
    iconAnchor:   [22, 94], // point of the icon which will correspond to marker's location
    shadowAnchor: [4, 62],  // the same for the shadow
    popupAnchor:  [-3, -76] // point from which the popup should open relative to the iconAnchor
});

function onMapClick(e) {
  popup
    .setLatLng(e.latlng)
    .setContent('<a href="http://127.0.0.1:5000/results?lat=' + e.latlng.lat.toString() + "&lon=" + e.latlng.lng.toString() + '"rel="noopener noreferrer">Click here to check the tree</a>')
    .openOn(map);
}



map.on('click', onMapClick);