var main_URL='https://flexifly.nl'
var main_URL='https://yurick.duckdns.org:8000'
var main_URL='http://127.0.0.1:8000'
var greenIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });
  var violetIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });
  var yellowIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gold.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });
  var redIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
  });
  
  Date.prototype.addDays = function(days) {
    var date = new Date(this.valueOf());
    date.setDate(date.getDate() + days);
    return date;
    }





// from here
function myOwmMarker(data) {
    // just a Leaflet default marker
    return L.marker([data.coord.Lat, data.coord.Lon]);
}

function myOwmPopup(data) {
    // just a Leaflet default popup with name as content
    return L.popup().setContent(data.name);
}

var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'});
  
var temp = L.OWM.temperature({opacity: 0.3, palette: '3:FF0000;5:00FF00;9:0000FF', appId: '4aa410d2d7b9d37b47518bf48df5ce3f'});
var rain = L.OWM.rain({appId: '4aa410d2d7b9d37b47518bf48df5ce3f'});
var map = L.map('map', { center: new L.LatLng(52.01, 4.4), zoom: 9, layers: [osm] });
var baseMaps = { "Current weather": osm };
var overlayMaps = { "Temp": temp,"Rain": rain };
var layerControl = L.control.layers(baseMaps, overlayMaps).addTo(map);
var imageUrl = 'owmloading.gif';




// up to here
var outbound_date_from= new Date().addDays(1).toLocaleString('en-GB').slice(0,10).replaceAll('/','-');
var outbound_date_to= new Date().addDays(1).toLocaleString('en-GB').slice(0,10).replaceAll('/','-');
var inbound_date_from= new Date().addDays(8).toLocaleString('en-GB').slice(0,10).replaceAll('/','-');
var inbound_date_to= new Date().addDays(8).toLocaleString('en-GB').slice(0,10).replaceAll('/','-');
var origins = [];
var destinations =[];
var price_limit = 1000;

var cities = L.layerGroup();

function display_dest(){
    cities.clearLayers();
    for (i=0; i<destinations.length; i++){
        // console.log(destinations[i]);
        if (destinations[i].options.price <= price_limit){
        destinations[i].addTo(cities)
        }
        cities.addTo(map);
        


    }
}

function onMapClick(e) {
    // console.log(e.target.options.name);
    $("body").css("cursor", "progress");
    $('.leaflet-container').css('cursor','progress');
    var coords = (e.target._latlng)
    bounds=[[coords.lat-0.1, coords.lng-0.2],[coords.lat+0.1, coords.lng+0.2]];

    progs=L.imageOverlay(imageUrl, bounds).addTo(map).bringToFront();



    fetch(main_URL+'/get_all_flights_from/'+e.target.options.name+"?" + new URLSearchParams({
        outbound_date_from: outbound_date_from,
        outbound_date_to: outbound_date_to,
        inbound_date_from: inbound_date_from,
        inbound_date_to: inbound_date_to,
    }))
    .then(response => response.json())
    .then (function (data){
        if (data){
            destinations =[];
            cities.clearLayers();
            for (i=0;i<data.length;i++){
                // console.log(data[i].outbound.route.to_airport.id);
                const lat = data[i].outbound.route.to_airport.location.latitude;
                const lon = data[i].outbound.route.to_airport.location.longitude;
                // console.log(data[i]);
                const flight_no = data[i].outbound.flight_number.toString();
                var company;
                let my_icon;
                
                if (flight_no.startsWith('FR')){
                    company = 'Ryanair';
                    my_icon = yellowIcon;
                }
                else if(flight_no.startsWith('WZ')){
                    company = 'Wizzair';
                    my_icon = violetIcon;
                }
                else if(flight_no.startsWith('EA')){
                    company = 'Easyjet';
                    my_icon = redIcon;
                }
                else{
                    company = 'Transavia';
                    my_icon = greenIcon;
                }
                const text="Flight by " + company + " from "+e.target.options.name+
                " to "+data[i].outbound.route.to_airport.id + 
                "<br> depart " + data[i].outbound.departure_date  +
                "<br> return " + data[i].inbound.arrival_date +
                "<br> price: "+ data[i].price.toString()+" EUR.";
                destinations.push (L.marker([lat,lon],{
                    icon: my_icon,
                    fillOpacity: 0.5,
                    price:data[i].price,
                    name: data[i].outbound.route.to_airport.id,
                })
                // .addTo(map)
                .bindPopup(text))
                // .on('click', onMapClick))
            }
            // console.log(destinations);
            cities = L.layerGroup(destinations);
            display_dest();
            // cities = L.layerGroup(destinations);
            // cities.addTo(map);

        }
        else{
            e.target.bindPopup("No flights") 
        }
        $("body").css("cursor", "default");
        $('.leaflet-container').css('cursor','default');
        map.removeLayer(progs);
    })

}

// map.on('click', onMapClick);



fetch(main_URL+'/get_origin_airports/')
  .then(response => response.json())
  .then(function(data){
    const codes=Object.keys(data);
    for (i=0; i<codes.length; i++){
        
        origins.push (L.marker([data[codes[i]].location.latitude,data[codes[i]].location.longitude],{
            // icon: greenIcon,
            fillOpacity: 0.5,
            name: data[codes[i]].id,
        })
        .addTo(map)
        .bindPopup(data[codes[i]].name)
        .on('click', onMapClick))
    }
    
  })



$('input[name="date_outbound"]').daterangepicker(
{
    locale: {
        format: 'DD-MM-YYYY'
    },
    startDate: new Date().addDays(1),
    endDate: new Date().addDays(1),
}, 
function(start, end, label) {
    // alert("A new date range was chosen: " + start.format('DD-MM-YYYY') + ' to ' + end.format('DD-MM-YYYY'));
    outbound_date_from = start.format('DD-MM-YYYY');
    outbound_date_to = end.format('DD-MM-YYYY');
});
$('input[name="date_inbound"]').daterangepicker(
    {
        locale: {
            format: 'DD-MM-YYYY'
        },
        startDate: new Date().addDays(8),
        endDate: new Date().addDays(8),
    }, 
    function(start, end, label) {
        // alert("A new date range was chosen: " + start.format('DD-MM-YYYY') + ' to ' + end.format('DD-MM-YYYY'));
        inbound_date_from = start.format('DD-MM-YYYY');
        inbound_date_to = end.format('DD-MM-YYYY');
    });

$ ('input[name="price"]').on('change', function() {
    price_limit=$('input[name="price"]:checked').val(); 
    display_dest();
 });
