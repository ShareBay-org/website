// THS SCRIPT IS RELATED TO LISTINGS
$(document).ready(function() { //Everything loaded
    $.ajaxSetup({
        cache: false
    });
	

    if ($('#listingMap').length) {

        showListingMap(); // initialize the map


        function showListingMap() {

            var listingMap = new google.maps.Map(document.getElementById('listingMap'), {
                zoom: 5,
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
            });
        }
    }


    //INITIALIZE tags
    if ($('#tags').length > 0) {
        $(function() {
            $('#tags').tagit({
                allowSpaces: true
            });
        });
    }

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
        label: '<i class="fas fa-camera fa-2x"></i>&nbsp;&nbsp;Add a photo',
        buttonConfirmLabel: 'OK'
    };

    if ($("#listingPic").length) {
        $("#listingPic").slim(slimListOptions);

        if (hasImage != '') {
            var src = baseURL + '/listing_pics/' + hasImage;
            $("#listingPic").slim('load', src, slimListOptions, function(error, data) {});
        }
    }


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


    $('#post_listing').bind('click', function(e) {
        e.preventDefault();
        var good2go = 0;

        if ($("#listing_title").val() || $("#listing_desc").val()) {
            good2go++;
            toggleError('#listing_title', 1);
            toggleError('#listing_desc', 1);
        } else {
            toggleError('#listing_title', 0);
            toggleError('#listing_desc', 0);
        }; 

        if ($("#category_select").val()) {
            good2go++;
            toggleError('#category_select', 1)
        } else {
            toggleError('#category_select', 0)
        };

        if (good2go >= 2) {

            //INITIAL FORM VALUES GOOD TO GO - HIDE MAIN ERROR MESSAGE
            if ($('#post_listing_E').is(':visible')) {
                $('#post_listing_E').slideUp()
            };

            // GOOD TO GO - BEGIN SAVE
            $("#loading").show();
            $("input[name='good2go']").val(good2go);

            //CHECK FOR IMAGE AND IS NOT CURRENT IMAGE..
            var myData = $('#listingPic').slim('data');
            if (myData[0].input.name != null && myData[0].input.name != hasImage) {
                $("input[name='image']").val(myData[0].input.name);

                //SAVE IMAGE...
                $('#listingPic').slim('upload', function(error, response) {
                    $.ajax({
                        type: "POST",
                        data: $("form#listing").serialize(),
                        url: baseURL + '/ajax.cgi',
                        success: function(result) {
                            $('#loading').hide();
						showToast(result);
                        // $('#listing').html(result);
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
                    data: $("form#listing").serialize(),
                    url: baseURL + '/ajax.cgi',
                    success: function(result) {
                        $('#loading').hide();
						showToast(result);
                        // $('#listing').html(result);
						$(window).scrollTop(0); 
                    },
                    error: function(xhr) {
                        $("#loading").hide();
                        console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                    }
                });
            }

        } else {
            //INITIAL FORM VALUES ARE NO GO - SHOW MAIN ERROR AND RETURN
            if ($('#post_listing_E').is(':hidden')) {
                $('#post_listing_E').slideDown()
            };
            return false;
        };
    }); // END SUBMIT

// }

}); // End document ready
