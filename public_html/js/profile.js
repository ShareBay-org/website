// THS SCRIPT IS RELATED TO USER PROFILE EDITING
$(document).ready(function() { //Everything loaded
    var eRegex = new RegExp("^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+)([.]+)([a-zA-Z]{2,})$");
    $.ajaxSetup({
        cache: false
    });


    function showMap() {

        var map = new google.maps.Map(document.getElementById('gMap'), {
            zoom: 8,
            center: myLatLng
        });

        var marker = new google.maps.Marker({
            position: myLatLng,
            map: map,
            draggable: true,
        });

        google.maps.event.addListener(marker, 'dragend', function(marker) {
            var latLng = marker.latLng;
            currentLatitude = latLng.lat();
            currentLongitude = latLng.lng();
            $("#lat").val(currentLatitude);
            $("#lon").val(currentLongitude);
        });
    }

    $(function() {

        $('#tags').tagit({
            allowSpaces: true
        });
    });

    var slimOptions = {
        ratio: '1:1',
        minSize: {
            width: 200,
            height: 200,
        },
        size: {
            width: 600,
            height: 600
        },
        service: baseURL + '/slim/async.php',
        download: false,
        willSave: function(data, ready) {
            ready(data);
        },
        label: '<i class="fas fa-camera fa-2x"></i>&nbsp;&nbsp;Add a photo',
        buttonConfirmLabel: 'OK'
    };

    $("#profilePic").slim(slimOptions);

    if (hasImage != '') {
        var src = baseURL + '/user_pics/' + hasImage;
        $("#profilePic").slim('load', src, slimOptions, function(error, data) {});
    }


    $('input[type=radio][name=ac_type]').click(function() {

        if ($("input[type=radio][name=ac_type]:checked").val() == 2) {
            $("#group_opts").slideDown();
        } else {
            $("#group_opts").slideUp();
        }
    });


    showMap();

    if (hasData === true) {
        $("#ac_type").addClass("disabled");
    }






    $('#save_profile').click(function(e) {
        e.preventDefault();
        var good2go = 0;
        var isGroup = 0;

        //CHECK FOR GROUP AND SHOW NAME OPTIONS
        if ($("input[name='ac_type']:checked").val() == 2) {
            isGroup++;
        }

        if ($("input[name='ac_type']:checked").val()) {
            good2go++;
            toggleError('#ac_type', 1)
        } else {
            toggleError('#ac_type', 0)
        };

        if ($("#first_name").val()) {
            good2go++;
            toggleError('#first_name', 1)
        } else {
            toggleError('#first_name', 0)
        };

        if ($("#last_name").val()) {
            good2go++;
            toggleError('#last_name', 1)
        } else {
            toggleError('#last_name', 0)
        };

        if (isGroup == 1) {
            if ($("#org_name").val()) {
                good2go++;
                toggleError('#org_name', 1)
            } else {
                toggleError('#org_name', 0)
            };
        }

        if ($("#email").val() && eRegex.test($("#email").val()) === true) {
            good2go++;
            toggleError('#email', 1)
        } else {
            toggleError('#email', 0)
        }

        if ($("#password").val() || hasData == true) {
            good2go++;
            toggleError('#password', 1)
        } else {
            toggleError('#password', 0)
        };

        if ($("#city").val()) {
            good2go++;
            toggleError('#city', 1)
        } else {
            toggleError('#city', 0)
        };

        if ($("#region").val()) {
            good2go++;
            toggleError('#region', 1)
        } else {
            toggleError('#region', 0)
        };

        if ($("#country").val()) {
            good2go++;
            toggleError('#country', 1)
        } else {
            toggleError('#country', 0)
        };

        if ($("#lat").val() && $("#lon").val()) {
            good2go++;
            toggleError('#gMap', 1)
        } else {
            toggleError('#gMap', 0)
        };

        // var tags = $("input[name='tags']").val().split(',');
        // var tooLong = 0;
        // for (var i = 0; i < tags.length; i++) {
            // if (tags[i].length > 25) {
                // tooLong++
            // };
        // }
        // if (tags.length > 4 && tooLong == 0) {
            // good2go++;
            // toggleError('#tags_too_few', 1);
            // toggleError('#tags_too_long', 1);
        // } else if (tags.length < 5) {
            // toggleError('#tags_too_few', 0);
            // toggleError('#tags_too_long', 1);
        // } else if (tooLong > 0) {
            // toggleError('#tags_too_long', 0);
            // toggleError('#tags_too_few', 1);
        // };

        if ($("input[name='pledge_box']:checked").val() == 'agree') {
            good2go++;
            toggleError('#pledge', 1)
        } else {
            toggleError('#pledge', 0)
        };


        if ((isGroup == 0 && good2go >= 10) || (isGroup == 1 && good2go >= 11)) {

            //INITIAL FORM VALUES GOOD TO GO - HIDE MAIN ERROR MESSAGE
            if ($('#save_profile_E').is(':visible')) {
                $('#save_profile_E').slideUp()
            };
            // SET RETURN PAGE
            var returnPage = baseURL;
            $("#loading").show();

            //CHECK IF EMAIL IS UNIQUE
            // var $query = baseURL + "/ajax.cgi?a=checkmail&e=" + $("#email").val();
            // $.ajax({
                // url: $query,
                // success: function(result) {
                    // if (result == '0' || hasData === true) {
                        // $("#email_E").html('! Please enter a valid email'); //RESET ERROR HTML
                        // toggleError('#email', 1);

                        // EMAIL IS GOOD TO GO - BEGIN SAVE
                        $("input[name='good2go']").val(good2go);

                        //CHECK FOR IMAGE AND IS NOT CURRENT IMAGE..
                        var myData = $('#profilePic').slim('data');
                        if (myData[0].input.name != null && myData[0].input.name != hasImage) {
                            $("input[name='image']").val(myData[0].input.name);

                            //SAVE IMAGE...
                            $('#profilePic').slim('upload', function(error, response) {

                                //SUBMIT FORM...
                                $.ajax({
                                    type: "POST",
                                    data: $("form#profile").serialize(),
                                    url: baseURL + '/ajax.cgi',
                                    success: function(result) {
                                        // DISPLAY RESULT
                                        $("#register").html(result);
                                        $("#loading").hide();
										$(window).scrollTop(0); 
                                        // setTimeout(window.location = returnPage, 2000);
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
                                data: $("form#profile").serialize(),
                                url: baseURL + '/ajax.cgi',
                                success: function(result) {
                                    // DISPLAY RESULT
                                    $("#register").html(result);
                                    $("#loading").hide();
									$(window).scrollTop(0); 
                                    // setTimeout(window.location = returnPage, 2000);
                                },
                                error: function(xhr) {
                                    $("#loading").hide();
                                    console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                                }
                            });
                        }

                    // } else {
                        // $("#loading").hide();
                        // $("#email_E").html('! This email already exists');
                        // if ($('#save_profile_E').is(':hidden')) {
                            // $('#save_profile_E').slideDown()
                        // };
                        // toggleError('#email', 0);
                        // return false;
                    // }
                // },
                // error: function(xhr) {
                    // $("#loading").hide();
                    // console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                // }
            // });

        } else {
            //INITIAL FORM VALUES ARE NO GO - SHOW MAIN ERROR AND RETURN
            if ($('#save_profile_E').is(':hidden')) {
                $('#save_profile_E').slideDown()
            };
            return false;
        };
    }); // END SUBMIT

}); // End document ready

