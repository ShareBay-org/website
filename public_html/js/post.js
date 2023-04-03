// THS SCRIPT IS FOR POSTING
    $.ajaxSetup({
        cache: false
    });
	

// $(document).ready(function() { //Everything loaded
	
// var isMapsApiLoaded = false;
// window.mapsCallback = function () {
  // isMapsApiLoaded = true;
  // console.log("Maps loaded y'all");
// };


// var isMapsApiLoaded = false;

// window.mapsCallback = function () {
  // isMapsApiLoaded = true;
// }

function initialize() {
	

    if ($('#listingMap').length > 0) {

        showListingMap(); // initialize the map


        function showListingMap() {

            var listingMap = new google.maps.Map(document.getElementById('listingMap'), {
                zoom: 12,
                center: myListingLatLng
            });

            var marker = new google.maps.Marker({
                position: myListingLatLng,
                map: listingMap,
                draggable: true,
            });

            google.maps.event.addListener(marker, 'dragend', function(marker) {
                var latLng = marker.latLng;
                currentLatitude = latLng.lat();
                currentLongitude = latLng.lng();
                $("#listingLat").val(currentLatitude);
                $("#listingLon").val(currentLongitude);
                $("#location_info").html('Custom');
				
            });
        }
    }


    //INITIALIZE tags

            // if ($('#tags').length > 0) {
        // $(function() {
            // $('#tags').tagit({
                // allowSpaces: true
            // });
        // });
    // }

    var slimListOptions = {
        // ratio: '16:9',
        // minSize: {
            // width: 250,
            // height: 140,
        // },
        // size: {
            // width: 800,
            // height: 450
        // },
        service: 'slim/async.php',
        download: false,
        willSave: function(data, ready) {
            ready(data);
        },
        label: '<i class="fas fa-camera"></i>&nbsp;&nbsp;Add photo',
        buttonConfirmLabel: 'OK'
    };

    if ($("#listingPic").length) {
        $("#listingPic").slim(slimListOptions);

    }

$('#post_text').focus();


$('#post_text').on('keyup', function(){
	var chars = $('#post_text').val().length;
	// CHECK EVERY x CHARACTERS
if (chars == 1 || (chars % 10) == 0){
	console.log('checking..');
	$.ajax({
            url: baseURL + '/ajax.cgi?a=matchcategories&text=' + $('#post_text').val(),
            success: function(result) {
				$('#matched_categories').html(result);
            }
        });
		
		
}
});

$("#is_physical").change(function() {
    if(this.checked) {
$('#physical_options').slideDown();
    }else{
		
$('#physical_options').slideUp();
	}
});

// $('input[name="category"]').on('change', function(){
	// var cat_id = $('input[name="category"]:checked').val();
	
// console.log('Cat ' + cat_id + ' picked');
	
// });


    function toggleError(input, state) {
        if (state == 1) { //IF GOOD TO GO!
            if ($(input + '_E').is(':visible')) {
                $(input + '_E').slideUp()
            };
            if ($(input).hasClass('inputerror nomargin')) {
                $(input).removeClass('inputerror nomargin')
            };
        } else {
            $(input + '_E').slideDown();
            $(input).addClass('inputerror nomargin')
        }
    }


    $('form#post_listing').on('submit', function(e) {
        e.preventDefault();
        var good2go = 0;

        if ($('#post_text').val()) {
            good2go++;
            toggleError('#post_text', 1)
        } else {
            toggleError('#post_text', 0)
        };

        if ($('input[name="category"]').val() != '') {
            good2go++;
            toggleError('#category_select', 1)
        } else {
            toggleError('#category_select', 0)
        };

        if (good2go == 2) {

            //INITIAL FORM VALUES GOOD TO GO - HIDE MAIN ERROR MESSAGE
            if ($('#post_E').is(':visible')) {
                $('#post_E').slideUp()
            };

            // GOOD TO GO - BEGIN SAVE
            $("#loading").show();
            $('input[name="good2go"]').val(good2go);

            //CHECK FOR IMAGE..
            var myData = $('#listingPic').slim('data');
            if (myData[0].input.name != null){
                $("input[name='image']").val(myData[0].input.name);

                //SAVE IMAGE...
                $('#listingPic').slim('upload', function(error, response) {
                    $.ajax({
                        type: "POST",
                        data: $("form#post_listing").serialize(),
                        url: baseURL + '/ajax.cgi',
                        success: function(result) {
							$('#modalContent').html();
							$('#modalWrap').hide();
							$('#contentBlur').hide();
							$('#loading').hide();
							showToast(result);
							setTimeout(function(){refreshFeed()}, 1000);
							$(window).scrollTop(0); 
                        },
                        error: function(xhr) {
                            $("#loading").hide();
                            console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                        }
                    });
                });
            } else {
                //SUBMIT FORM WITHOUT IMAGE...
                $.ajax({
                    type: "POST",
                    data: $("form#post_listing").serialize(),
                    url: baseURL + '/ajax.cgi',
                    success: function(result) {
						$('#modalContent').html();
						$('#modalWrap').hide();
						$('#contentBlur').hide();
                        $('#loading').hide();
						showToast(result);
						refreshFeed();
						$(window).scrollTop(0); 
                    },
                    error: function(xhr) {
                        $("#loading").hide();
                        console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                    }
                })			
            }

        } else {
            //INITIAL FORM VALUES ARE NO GO - SHOW MAIN ERROR AND RETURN
            if ($('#post_E').is(':hidden')) {
                $('#post_E').slideDown()
            };
            return false;
        };
    }); // END SUBMIT
};


function refreshFeed(){
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=getfeed&screen=' + $(document).width() + 'page=' + 0,
        success: function(result) {
			$('#feed-content').html(result);
        },
        error: function(xhr) {
			$('#feed-content').html('Communication error! [Details: ' + xhr.status + ' - ' + xhr.responseText + ']');
        }
    })
}

function categorySelected(){
$('input[name="auto_category"]').on('change', function(){
var cat_id = $('input[name="auto_category"]:checked').val();
var cat_name = $('#name' + cat_id).html();
$('input[name="category"]').val(cat_id);
$('#selected_category span').html(cat_name);
$('#selected_category').show();
$('#matched_categories').hide();
	});
};


function reselectCategory(){
$('#selected_category').hide();
$('#matched_categories').show();
};

function manualSelect(){
$('#matched_categories').html('');
$('#matched_categories').hide();
$.ajax({
		url: baseURL + '/ajax.cgi?a=getcategoryselect',
		success: function(result) {
			$('#selected_category').html(result);
			$('#selected_category').show();
		},
		error: function(xhr) {
			console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
		}
	});
};

function manualSelected(){
var cat_id = $('select[name="manual_category"]').val();
$('input[name="category"]').val(cat_id);
}


function openMap(){
$('#listingMap').show();
};

// });