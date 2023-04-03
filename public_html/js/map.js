// THS SCRIPT IS RELATED TO THE SEARCH MAP

var markers = [];
var oldMarkers = [];
var markerClick = false;
var mapStyle=[{featureType:"administrative",elementType:"labels.text.fill",stylers:[{color:"#444444"}]},{featureType:"poi",elementType:"all",stylers:[{visibility:"off"}]},{featureType:"road",elementType:"all",stylers:[{saturation:-100},{lightness:20}]},{featureType:"road.highway",elementType:"all",stylers:[{visibility:"simplified"}]},{featureType:"road.arterial",elementType:"labels.icon",stylers:[{visibility:"off"}]},{featureType:"transit",elementType:"all",stylers:[{visibility:"off"}]}];



$(document).ready(function() {
	
var mapCenter = '';
	
var map = new google.maps.Map(document.getElementById('map_div'), {
	center: new google.maps.LatLng(myLat, myLon),
	zoom: myZoom,
	mapTypeId: google.maps.MapTypeId.ROADMAP,
	styles: mapStyle,
	disableDefaultUI: true,
	zoomControl: true,
	mapTypeControl: false,
	streetViewControl: true
});

var oms = new OverlappingMarkerSpiderfier(map, {
  markersWontMove: true,
  markersWontHide: true,
  basicFormatEvents: true,
  keepSpiderfied: true
});

let timeout = null;

google.maps.event.addListener(map, 'dragend', function() {
	clearTimeout(timeout);
	timeout = setTimeout(function () {
	getResults();	
    }, 1000);
});

google.maps.event.addListener(map, 'zoom_changed', function() {
	clearTimeout(timeout);
	timeout = setTimeout(function () {
	getResults();	
    }, 1000);
});

var loadMarkers = google.maps.event.addListener(map, 'idle', function() {
	getResults();
	google.maps.event.removeListener(loadMarkers);
});

$('.map-filter').bind('click', function() {
	clearTimeout(timeout);
	timeout = setTimeout(function () {
	getResults();	
    }, 1000);
});

$('#list-view').bind('click', function(e) {
	e.preventDefault();
	var query = $('.search_bar_query').val();
	window.location.href = baseURL + '/?search=&order=nearest';
});




function getResults(){
	$('#loading').show();
	var resultType;
	
if ($('#query').is(':visible') && $('#query').val() != ''){query = $('#query').val();}
if ($('#mobile_query').is(':visible') && $('#mobile_query').val() != ''){query = $('#mobile_query').val()}

// PREPARE URL
var searchIn = [];
if ($("input[name='members']:checked").val()){searchIn.push('members')};
if ($("input[name='offers']:checked").val()){searchIn.push('offers')};
if ($("input[name='requests']:checked").val()){searchIn.push('requests')};
if ($("input[name='sharepoints']:checked").val()){searchIn.push('sharepoints')};
var appendURL = 'query=' + query + '&in=' + searchIn + '&strict=' + $("input[name='strict']:checked").val() + '&last7=' + $("input[name='last7']:checked").val() + '&showall=' + $("input[name='showall']:checked").val();	

// RETURN MAP RESULTS	
$('#map_div').show();
resultType = 'markers';
	
newBounds  = new google.maps.LatLngBounds();
var bounds = map.getBounds();
var SW = bounds.getSouthWest();
var NE = bounds.getNorthEast();

var mapCenter = map.getCenter();
var thisLat = mapCenter.lat();
var thisLng = mapCenter.lng();
appendURL += '&a=get' + resultType + '&myLat=' + thisLat + '&myLon=' + thisLng + '&n=' + NE.lat() + '&s=' + SW.lat() + '&e=' + NE.lng() + '&w=' + SW.lng();

var reqURL = baseURL + '/ajax.cgi?' + appendURL;

	$.ajax({
		url: reqURL,
		success: function(result) {
				if (oldMarkers) {
					for (var i = 0; i < oldMarkers.length; i++) {
						oldMarkers[i].setMap(null);
					}
					oldMarkers = [];
				}
			if (result != '') {
				markers = JSON.parse(result);
				var total = markers.length;
				for (var i = 0; i < markers.length; i++) {
					var icon;
					var z;
					if (markers[i].type == 'member') {
						icon = 'member-pin.png'
					}
					if (markers[i].type == 'offer_1') {
						z = google.maps.Marker.MAX_ZINDEX + 1;
						icon = 'item-offer-pin.png'
					}
					if (markers[i].type == 'request_1') {
						z = google.maps.Marker.MAX_ZINDEX + 1;
						icon = 'item-request-pin.png'
					}
					if (markers[i].type == 'offer_0') {
						z = google.maps.Marker.MAX_ZINDEX + 1;
						icon = 'skill-offer-pin.png'
					}
					if (markers[i].type == 'request_0') {
						z = google.maps.Marker.MAX_ZINDEX + 1;
						icon = 'skill-request-pin.png'
					}
					var myLatlng = new google.maps.LatLng(markers[i].lat, markers[i].lon);
					newBounds.extend(myLatlng);
					var marker = new google.maps.Marker({
						position: myLatlng,
						map: map,
						zIndex: z,
						icon: 'i/' + icon,
						title: markers[i].name
					});
					attachInfo(marker, markers[i].id);
					oldMarkers.push(marker);
				}
				
						//~ map.setCenter(new google.maps.LatLng(thisLat, thisLng));
						//~ map.setZoom(myZoom);
						
				if (total >= 100 && $('#showall').is(':checked') === false){
				$("#total").html('OVER 100 MATCHES! Results are clipped to reduce server load. Please zoom in for more results.');
					 
				}else{
				if (total == 1){
				$("#total").html(total + ' MATCH FOUND');
				}
				if (total > 1){
				$("#total").html(total + ' MATCHES FOUND');
				}}
			} else { //nothing found
			var noResultsMsg;
			if (query != ''){
				noResultsMsg = 'NO RESULTS FOR &quot;' + query + '&quot;';
			}else{
				noResultsMsg = 'NO MATCHES';				
			}
				$("#total").html(noResultsMsg);
			}
			$('#loading').hide();
			$('#map_results').show();
			$('#map_results').delay(6000).fadeOut(1000);
		},
		error: function(result){
			alert('Error. Couldn\'t load markers.. Server said:\n' + result);
			$('#loading').hide();
		}
	});		
myZoom = map.getZoom();
appendURL += '&zoom=' + myZoom;

history.pushState('data', 'Sharebay Map', baseURL + '/map?' + appendURL);
}

var infoWindowInit = '<div class="div-main-infoWindow"><div class="tSpinner"></div></div>';
var infoWindow = new google.maps.InfoWindow({
		content: infoWindowInit
});

function attachInfo(marker, id) {

	marker.addListener('spider_click', function() {
	//~ clickTime = Date.now();
		markerClick = true;
		infoWindow.close();
		infoWindow.setContent(infoWindowInit);
		var url = baseURL + '/ajax.cgi?a=getinfobox&id=' + id;
		$.ajax({
			url: url,
			contentType: "charset=utf-8",
			success: function(result) {
				infoWindow.setContent(result);
			}
		});
		infoWindow.open(map, this);
	});
    oms.addMarker(marker);
}

// GET MARKERS ON PRESS ENTER
$(".search_bar_query").keyup(function(e){
    if(e.keyCode == 13){
	getResults();
    }
});

// SEND TOPBAR QUERY SEARCH TO MAP IF VISIBLE  
    $(document).on('submit', 'form#search_form, form#mobile_search_form', function(e) {
		e.preventDefault();
		if($('#map_div').is(':visible')){
			getResults();
		}else{
		document.getElementById("search_form").submit();
	}
    });


    
}); //Doc ready
