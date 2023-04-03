// THIS      CONTAINS COMMON AND CORE JS FUNCTIONS
var eRegex = new RegExp("^[a-zA-Z0-9._%+-]+@([a-zA-Z0-9.-]+)([.]+)([a-zA-Z]{2,})$");
$.ajaxSetup({
    cache: false
});
var success = '<p class="success">Success!</p>';
var notPossible = 'Something went wrong! Action not possible at this time. Please try later.';

var shareURL;
var shareDesc;


$(document).ready(function() { //Everything loaded

    shareURL = encodeURIComponent(document.URL);
    shareDesc = encodeURIComponent(document.title);


    $(document).on('click', '.showLogin', function() {
        openModal(baseURL + '/ajax.cgi?a=showlogin')
    });
    $(document).on('click', '.showHomeLogin', function() {
        openModal(baseURL + '/ajax.cgi?a=showhomelogin')
    });
    $(document).on('click', '.forgot-password', function() {
        openModal(baseURL + '/ajax.cgi?a=forgotpassword')
    });

var postScriptsLoaded = 0;

function loadPostScripts(){
	if (postScriptsLoaded == 0){
	$('head').append('<link rel="stylesheet" href="' + baseURL + '/slim/slim.min.css">');
	$.getScript( "//maps.googleapis.com/maps/api/js?v=3&key=AIzaSyD4zc3ELJ8ZgqLMZqLhLGv7beewD6wN9eU");
    $.getScript( baseURL + "/slim/slim.jquery.js" );
    $.getScript( baseURL + "/js/post.js" + '?v=' + Date.now());
	postScriptsLoaded = 1;
		}
	return true;
}

	
    $(document).on('click', '.post-offer', function() {		
	openModal(baseURL + '/ajax.cgi?a=showoffer');
    });

	
    $(document).on('click', '.post-request', function() {	
	openModal(baseURL + '/ajax.cgi?a=showrequest');	
    });


    $(document).on('change', '#order_select', function() {
        window.location = $('#order_select').val()
    });

    $(document).on('change', '#filter_inline_select', function() {
        window.location = baseURL + '/search?query=' + $('.search_bar_query').val() + '&filter=' + $('#filter_inline_select').val();
    });

    // DO LOGIN
    $(document).on('click', '#doLogin', function(e) {
        e.preventDefault();
        var returnPage = '';
        if (document.location.href.match(/confirm/) || $('input[name="go"]').val() == 'home') {
            // EXCEPTION FOR ONE-OFF LINKS
            returnPage = baseURL;
        } else {
            returnPage = document.location.href;
        }
        $('#loading').show();
        $.ajax({
            type: "POST",
            data: $('form#logIn').serialize(),
            url: baseURL + '/ajax.cgi',
            success: function(result) {
                if (result == 'WRONG') {
                    $('#loading').hide();
                    $('#loginError').slideDown();
                } else if (result == 'UNACTIVATED') {
                    $('#loading').hide();
                    $('#unactivatedError').slideDown();
                } else if (result == 'LOCKED') {
                    $('#loading').hide();
                    $('#accountLockedError').slideDown();
                } else {
                    document.cookie = "SESS_ID=" + result + "; expires=Fri, 31 Dec 9999 23:59:59 GMT; domain=" + domain + "; path=/;";
                    window.location = returnPage;
                }
            },
            error: function(xhr) {
                $('#loading').hide();
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
    });


    // DO LOGOUT
    $('.logout').click(function() {
        var returnPage = baseURL;
        $('#loading').show();
        var $query = baseURL + '/ajax.cgi?a=dologout';
        $.ajax({
            url: $query,
            success: function() {
                document.cookie = "SESS_ID=; expires=Thu, 1 Jan 1970 00:00:00 GMT; domain=" + domain + "; path=/;";
				showToast('You are now logged out.');
                window.location = returnPage;
            },
            error: function(xhr) {
                $('#loading').hide();
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
    });


    // DO LOGOUT EVERYWHERE
    $('.logoutall').click(function() {
        var returnPage = baseURL;
        $('#loading').show();
        var $query = baseURL + '/ajax.cgi?a=dologoutall';
        $.ajax({
            url: $query,
            success: function() {
                document.cookie = "SESS_ID=; expires=Thu, 1 Jan 1970 00:00:00 GMT; domain=" + domain + "; path=/;";
				showToast('You are now logged out of all devices.');
                window.location = returnPage;
            },
            error: function(xhr) {
                $('#loading').hide();
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
    });
	
	
	
	   // CLOSE TOAST
    $('#closeToast').click(function() {
        $('#toast').css('opacity',0);
        $('#toast').css('left',-50);
        $('#toastMessage').html('');
    });



    // RESEND CODE FROM REGISTRATION ERROR
    $(document).on('click', '#resendCode', function(e) {
        e.preventDefault();
        $('#loading').show();
        var $query = baseURL + '/ajax.cgi?a=resendcode&e=' + $('#email').val();
        $.ajax({
            url: $query,
            success: function(result) {
                $('#loading').hide();                
				$("form#signup").html(result);
            },
            error: function(xhr) {
                $('#loading').hide();
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
    });


    $(document).on('focus', '.search_bar_query', function() {
        $(".search_bar_query").attr("placeholder", "");
    });
    

    $('#closeModal').click(function() {
        $('#modalWrap').hide();
        $('#contentBlur').hide();
    });


    //// CLICK ANYWHERE TO EXIT MODAL	
         // if ($(this.target).closest('#modal').length == 0) {
            // $('#modalWrap').hide();
            // $('#contentBlur').hide();
        // }
    // });


    $('#close-funding').click(function(e) {
        $('#funding-box').css('height', 0);
    });

    $('#patron-button').click(function(e) {
        openPatron();
    });

    $(document).on('click', '.patron', function(e) {
        openPatron();
    });


    $('#p_amount').change(function(e) {
        $('.set_amount').prop('checked', false);
        $('#fund_opts').buttonset('refresh');
    });

    $('.set_amount').change(function(e) {
        $('#p_amount').val('');
    });

    $(".showMenu").click(function() {
        if ($('#subMenu').is(':hidden')) {
            $('#subMenu').show();
        } else {
            $('#subMenu').hide();
        }
    });
    $(document).click(function(e) {
        if ($(e.target).closest('.showMenu').length == 0) {
            $('#subMenu').hide();
        }
    });

    $(".showMessages").click(function() {
        if ($('#messages').is(':hidden')) {			
            $('#messages').show();
			$('.page-loader').show();
        var $query = baseURL + '/ajax.cgi?a=getconversations';
        $.ajax({
            url: $query,
            success: function(result) {
			$('.page-loader').hide();                
				$("#messages").html(result);
            },
            error: function(xhr) {
			$('.page-loader').hide();
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });		
        } else {
            $('#messages').hide();
        }
    });
    $(document).click(function(e) {
        if ($(e.target).closest('.showMessages').length == 0) {
            $('#messages').hide();
        }
    });

    $(".showNotifications").click(function() {
		$(".showNotifications").addClass('disabled');
        if ($('#notifications').is(':hidden')) {
            $('#notifications').show();
			$('.page-loader').show();
        var $query = baseURL + '/ajax.cgi?a=getnotifications';
        $.ajax({
            url: $query,
            success: function(result) {
			$('.page-loader').hide(); 
if (result == ''){$("#notifications").append('Nothing to show')}else{
			$("#notifications").append(result);
}
            },
            error: function(xhr) {
			$('.page-loader').hide();      
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });	
        } else {
            $('#notifications').hide();
            $('#notifications').html('');
        }
		$(".showNotifications").removeClass('disabled');
    });
	
    $(document).click(function(e) {
        if ($(e.target).closest('.showNotifications').length == 0) {
            $('#notifications').hide();
            $('#notifications').html('');
        }
    });
	
	
	
	
    // $(".menu").click(function() {
        // if ($('.menu').is(':visible')) {
            // $('.menu').hide();
        // }
    // });




    $('#p_submit').click(function(e) {
        e.preventDefault();
        var amount;
        if ($("input[name='p_amount']").val() != '') {
            amount = $("input[name='p_amount']").val();
        } else {
            amount = $("input[name='amount']:checked").val();
        }
        var PPurl = '';
        var singleItem = encodeURIComponent('One-off contribution to Sharebay.org');
        var subItem = encodeURIComponent('Monthly contribution to Sharebay.org');

        if ($("input[name='p_type']:checked").val() == 'single') {
            PPurl = 'https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=colinrturner%40gmail.com&item_name=' + singleItem + '&amount=' + amount + '&currency_code=EUR';
        } else {
            PPurl = 'https://www.paypal.com/cgi-bin/webscr?cmd=_xclick-subscriptions&business=colinrturner%40gmail.com&item_name=' + subItem + '&a3=' + amount + '&p3=1&t3=M&src=1&currency_code=EUR';
        }
        window.open(PPurl, '_blank');
    });



    // RESET USER PASSWORD
    $(document).on('click', '#pw-reset', function(e) {
        e.preventDefault();
        if ($('#reset_email').val() == '') {
            $('#resetError').slideDown();
            return false;
        } else {
            $('#loading').show();
            // var email = encodeURIComponent($('#reset_email').val());
            var $query = baseURL + '/ajax.cgi?a=resetpassword&email=' + $('#reset_email').val();
            // alert('Query is: ' + $query);
            $.ajax({
                url: $query,
                success: function(result) {
                    $('#loading').hide();
                    if (result != 1) {
                        $('#resetError').slideDown();
                    } else {
                        $('.box300').html('<p class="success">We have just sent you an email with a link to reset your password.</p>');
                    }
                },
                error: function(xhr) {
                    $('#loading').hide();
                    console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                }
            })
        };
    });


    // SET NEW PASSWORD
    $(document).on('click', '#setNewPassword', function(e) {
        e.preventDefault();
        if ($('#password1').val() != '' && ($('#password1').val() == $('#password2').val())) {
            $('#loading').show();
            var $query = baseURL + '/ajax.cgi?a=changepassword&id=' + $("input[name='id']").val() + '&auth=' + $("input[name='auth']").val() + '&pw=' + encodeURI($('#password1').val());
            $.ajax({
                url: $query,
                success: function(result) {
                    $('#loading').hide();
                    if (result == '' || result == 0) {
                        $('.error').slideDown();
                    } else {
                        $('#reset-pw').slideUp();
                        $('.success').slideDown();
					// TRASH OLD COOKIES FIRST, THEN WRITE NEW
                    document.cookie = "SESS_ID=; expires=Thu, 1 Jan 1970 00:00:00 GMT; domain=" + domain + "; path=/;";
                        document.cookie = "SESS_ID=" + result + "; expires=Fri, 31 Dec 9999 23:59:59 GMT; domain=" + domain + "; path=/;";
                        window.location = baseURL;
                    }
                },
                error: function(xhr) {
                    $('#loading').hide();
                    console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                }
            })
        } else {
            $('#resetError').slideDown();
            return false;
        };
    });

    if (getCookie('suppressNag') != 1 && $('#feed-alert').html() != '') {
        $('#feed-alert').slideDown();
    }

    // CLOSE BANNER ALERT
    $(document).on('click', '#closeBanner', function(e) {
        var now = new Date();
        now.setTime(now.getTime() + 86400000); // SUPPRESS FOR 24 HOURS
        document.cookie = "suppressNag=1; expires=" + now.toUTCString() + "; domain=" + domain + "; path=/";
        $('#feed-alert').slideUp();
    });

    if (getCookie('suppressNudge') != 1) {
        $('#invite-nudge').slideDown();
    }

    // CLOSE INVITE NUDGE
    $(document).on('click', '#closeNudge', function(e) {
        var now = new Date();
        now.setTime(now.getTime() + (86400000 * 30)); // SUPPRESS FOR 30 DAYS
        document.cookie = "suppressNudge=1; expires=" + now.toUTCString() + "; domain=" + domain + "; path=/";
        $('#invite-nudge').slideUp();
    });




    // SUBMIT CHAT MESSAGE
    $(document).on('submit', '#send-chat', function(e) {
        sendChat(e);
    });

    // SEND CHAT MESSAGE ON ENTER
    $(document).on('keyup', '#messageBox', function(e) {
        if (e.keyCode == 13 && e.shiftKey !== true) {
        sendChat(e);
		
        sendChat(e);
        }
    });


// var posting = 0;

   // POST REVIEW
    $(document).on('submit', 'form#write_review', function(e) {
        e.preventDefault();
	// if (posting == 0){
		// posting++;
		
		if ($("input[name='rating']:checked").val() == 0) {
   alert('Please select a rating!');
   return false;
} else {
        $('#loading').show();
        $.ajax({
            type: "POST",
            data: $('form#write_review').serialize(),
            url: baseURL + '/ajax.cgi',
            success: function(result) {
                $('#loading').hide();
				$('form#write_review').html(result)
            },
            error: function(xhr) {
                $('#loading').hide();
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });	
}
		// }else{
			// return false;
		// }
		// setTimeout(function(){posting = 0;},1000);
    });
	


var sending = 0;
	
	
    function sendChat(e) {
        e.preventDefault();
		if (sending == 0){
			sending++;
        if ($('#messageBox').val() == '') {
            alert('You must enter a message!');
        } else {
            //POST MESSAGE	
            $.ajax({
                type: 'POST',
                url: baseURL + '/ajax.cgi',
                dataType: "json",
                data: $("form#send-chat").serialize(),
                success: function(result) {
                    // DISPLAY RESULT
                    $("#chat-window").append(result.data);
                    $('#last_id').val(result.lastID);
                    $('#messageBox').val('');
                    scrollChat();
                },
                error: function(xhr) {
                    console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                }        
            });        
				$('.chat-right, .chat-left, .chat-alert').linkify({target: "_blank"});
        }
		}else{
			return false;
		}
		setTimeout(function(){sending = 0;},1000);
    }


    // MARK SEEN ON MESSAGE BOX CLICK
    $(document).on('click', '#messageBox', function(e) {
        markSeen($('#convo_id').val());
        checkMessages();
    });

// RESIZE COMMENT TEXT AREA
$(document).on('input', '.comment-response', function() {
    $(this).css("height", ""); //reset the height
    $(this).css("height", $(this).prop('scrollHeight') + "px");
});

resizeBar();

$( window ).resize(function() {
resizeBar();
});




$(document).on('submit', 'form#signup', function(e){
        e.preventDefault();
		if ($("#email").val() != '' && eRegex.test($("#email").val()) === true) {
            toggleError('#email', 1);
			$('#loading').show();
			//SUBMIT FORM...
		$.ajax({
			type: "POST",
			data: $("form#signup").serialize(),
			url: baseURL + '/ajax.cgi',
			success: function(result) {
				// DISPLAY RESULT
				$("form#signup").html(result);
				$("#loading").hide();
				$(window).scrollTop(0); 
			},
			error: function(xhr) {
				$("#loading").hide();
				console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
			}
		});
        } else {
            toggleError('#email', 0)
        }
});



$(document).on('submit', 'form#contact_form', function(e){
        e.preventDefault();
		if ($("#email").val() != '' && eRegex.test($("#email").val()) === true) {
            toggleError('#email', 1);
			$('#loading').show();
			//SUBMIT FORM...
		$.ajax({
			type: "POST",
			data: $("form#contact_form").serialize(),
			url: baseURL + '/ajax.cgi',
			success: function(result) {
				// DISPLAY RESULT
				$("form#contact_form").html(result);
				$("#loading").hide();
				$(window).scrollTop(0); 
			},
			error: function(xhr) {
				$("#loading").hide();
				console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
			}
		});
        } else {
            toggleError('#email', 0)
        }
});

// setTimeout(function() { enableButtons(); }, 5000);
// enableButtons();


if (getCookie('accept-cookies') != 1){
	$('#cookies-message').show();
}


$('#accept-cookies').bind("click", function(e) {
	$('#cookies-message').hide();
	setCookie('accept-cookies',1);
});




}); // End document ready

// function enableButtons(){
// $('.post-offer, .post-request').removeClass('disabled');
// };



function shareThis(link){
	if (navigator.share) {
   navigator.share({
      // title: 'some title',
      url: link
    }).then(() => {
      // console.log('Thanks for sharing!');
    })
    .catch(console.error);
    }else{
		var shareLink = encodeURIComponent(link);
		var dialog = '<h2 class="center">Share this:</h2><p class="center"><a class="share-list share-facebook" target="_blank" href="https://www.facebook.com/sharer/sharer.php?u=' + shareLink + '" title="Share on Facebook"><img src="' + baseURL + '/i/facebook_f.png"/> Share on Facebook</a><a class="share-list share-twitter" target="_blank" href="https://twitter.com/share?url=' + shareLink + '&hashtags=sharebay" title="Share on Twitter"><img src="' + baseURL + '/i/twitter_bird.png"/> Share on Twitter</a></p><p class="center smaller">Click to copy link:<br/><input type="text" id="link" value="' + link +'" onclick="copyText(\'link\');"/><span class="copied hidden"><br/>Link copied!</span></p>';
		openModal(dialog);
	}
}

function copyText(input){
$('#' + input).select();
document.execCommand("Copy");
$('.copied').show();
}

	
function openNotification(e,elem,object_type,object_id,action,actor_id){
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=setseen' + '&object_type=' + object_type + '&object_id=' + object_id + '&action=' + action + '&actor_id=' + actor_id,
        success: function() {$(elem).removeClass('bold');}
    });
		decrementNotificationAlert();
	if ($('#feed').is(':visible')){
	e.preventDefault();
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=featurefeed&screen=' + $(document).width() + '&object_type=' + object_type + '&object_id=' + object_id,
        success: function(result) {
			$('#feed-content').html(result);
			$(window).scrollTop(0);
			
        },
        error: function(xhr) {
			$('#feed-content').html('Communication error! [Details: ' + xhr.status + ' - ' + xhr.responseText + ']');
        }
    })
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
	

function showToast(m) {
	var leftIn = '50px';
	if ($(document).width() <= 600){leftIn = '30px';}
	$('#toastMessage').html(m);
	$('#toast').animate({'opacity':'1'},{duration : 400, queue : false})
	.animate({'left' : leftIn},{duration : 400, queue : false});
	setTimeout(function() {
    $('#toast').css('opacity','0');
    $('#toast').css('left','-50px');
	$('#toastMessage').html('');
}, 8000);
}



function resizeBar() {
	
// SIZE THE BIG SEARCH BAR (IF IT WILL FIT)
var rightBarLimit;
var minBarSize = 380;
var logoSpace = 190;
if ($('.bigLinks').is(':visible')){
rightBarLimit = $('.bigLinks').position().left - 10;
}else{
rightBarLimit = $('.linkReveal').position().left - 10;
}
if ((rightBarLimit - logoSpace) > minBarSize){
	$('#search_bar').css('right', $(window).width() - rightBarLimit + 'px');
	$('.search_bar_query').width($( '#search_bar').width() - 180 + 'px' );
	$('#search_bar').show();
	$('#mobile_search_bar').hide();
}else{
	$('#search_bar').hide();
	$('#mobile_search_bar').show();
}
}


function setHeart(action, object, id){
	if (LOGGED_IN === true && action !== '' && object !== '' && id !== ''){
		var elem = '#like_' + object + '_' + id;
		$(elem).addClass('disabled');
		
	 $.ajax({
            url: baseURL + '/ajax.cgi?a=setlike&action=' + action + '&object=' + object + '&id=' + id,
            success: function(result) {
				if (result !== ''){
				$(elem).html(result);
				}
				$(elem).removeClass('disabled');
            },
            error: function(xhr) {
				$(elem).removeClass('disabled');
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        })
		
}else{
	alert('Bad request, or you need to be logged in to do this!');
}
}


function showComments(element, object, id, link){
	if (element !== '' && object !== '' && id !== '' && link !== ''){
		var elem = '#' + element;	
		$(elem).addClass('disabled');
	 $.ajax({
            url: baseURL + '/ajax.cgi?a=showcomments&object=' + object + '&id=' + id + '&link=' + encodeURIComponent(link),
            success: function(result) {
				if (result !== ''){
				$(elem).replaceWith(result);
				}
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
			$(elem).removeClass('disabled');
}else{
	alert('Bad request, or you need to be logged in to do this!');
}
}

function postComment(element, thread, object, id){
	if (LOGGED_IN === true && element !== '' && $('#' + element + '_text').val() !== '' && thread !== '' && object !== '' && id !== ''){
		var container = '#comments_' + id;
		var elem = '#' + element;
		var text = encodeURIComponent($('#' + element + '_text').val());
		$(elem).addClass('disabled');
		
	 $.ajax({
            url: baseURL + '/ajax.cgi?a=postcomment&comment=' + text + '&thread=' + thread + '&object=' + object + '&id=' + id,
            success: function(result) {
				if (result !== ''){
				$(container).html(result);
				}
				// $(elem).removeClass('disabled');
            },
            error: function(xhr) {
				$(elem).removeClass('disabled');
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        })
		
}else{
	alert('Bad request, or you need to be logged in to do this!');
}
}


function deleteComment(element, comment_id, object, id){
	if (confirm("Are you sure you want to delete this comment?") === true) {
		
	if (LOGGED_IN === true && element !== '' && comment_id !== '' && object !== '' && id !== ''){
		var container = '#comments_' + id;
		var elem = '#' + element;
		$(elem).addClass('disabled');
		
	 $.ajax({
            url: baseURL + '/ajax.cgi?a=deletecomment&comment_id=' + comment_id + '&object=' + object + '&id=' + id,
            success: function(result) {
				if (result !== ''){
				$(container).html(result);
				}
				// $(elem).removeClass('disabled');
            },
            error: function(xhr) {
				$(elem).removeClass('disabled');
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        })
		
}else{
	alert('Bad request, or you need to be logged in to do this!');
}
	}
}

function setCookie(key, value, days) {
	var expires = new Date();
	if (days > 0){
		expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
		document.cookie = key + '=' + value + ';expires=' + expires.toUTCString();	
		}else{
		document.cookie = key + '=' + value + ';expires=Fri, 30 Dec 9999 23:59:59 GMT;';		
		}
}

function getCookie(key) {
    var keyValue = document.cookie.match('(^|;) ?' + key + '=([^;]*)(;|$)');
    return keyValue ? keyValue[2] : null;
}

function updateChat() {
    if ($("#chat-window").length) {
        var existing = $('#chat-window').html();
        $.ajax({
            url: baseURL + '/ajax.cgi?a=updatechat&convo_id=' + $('#convo_id').val() + '&last_id=' + $('#last_id').val(),
            dataType: "json",
            success: function(result) {
                //~ alert(result.data);
                if (result.data !== null) {
                    $('#chat-window').append(result.data);
                    $('#last_id').val(result.lastID);
                    scrollChat();
                    $('.chat-right, .chat-left, .chat-alert').linkify({
                        target: "_blank"
                    });
                }
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        })
    };

}


function checkMessages() {
    $.ajax({
        url: baseURL + '/ajax.cgi?a=checkmessages',
        success: function(result) {
            showMessageAlert(result);
        },
        error: function(xhr) {
            console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
        }
    })
    $.ajax({
        url: baseURL + '/ajax.cgi?a=checknotifications',
        success: function(result) {
            showNotificationAlert(result);
        },
        error: function(xhr) {
            console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
        }
    })
};


function showMessageAlert(n) {
    if (n > 0) {
        $('.message-alert').html(n);
        $('.message-alert').show();
    } else {
        $('.message-alert').hide();
    }
}

function showNotificationAlert(n) {
    if (n > 0) {
        $('.notification-alert').html(n);
        $('.notification-alert').show();
    } else {
        $('.notification-alert').hide();
    }
}

function decrementNotificationAlert() {
	var num = $('.notification-alert').html();
	num--;
	showNotificationAlert(num)
}


function markAllMessagesSeen() {
    $.ajax({
        url: baseURL + '/ajax.cgi?a=markallmessagesseen',
        success: function(result) {
            showMessageAlert(result);
        },
        error: function(xhr) {
            console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
        }
    })
    checkMessages();
}


function markAllNotificationsSeen() {
    $.ajax({
        url: baseURL + '/ajax.cgi?a=markallnotificationsseen',
        success: function() {
            showNotificationAlert(0);
            $('#notifications').hide();
            $('#notifications').html('');
        },
        error: function(xhr) {
            console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
        }
    })
}

function openPatron() {
    var newHeight;
    if (screen.width >= 600) {
        newHeight = 180
    } else {
        newHeight = 250
    };
    if ($('#funding-box').height() < 1) {
        $('#funding-box').css('height', newHeight + 'px');
    }
}

function getHonorRecord(HP_id) {
    if (HP_id != '') {
        $.ajax({
            url: 'https://honorpay.org/?a=getrecord&id=' + HP_id,
            success: function(result) {
                $('.honoricon').html(result);
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        })
    };
}

function gotIt(id) {
    $.ajax({
        url: baseURL + '/ajax.cgi?a=gotit&id=' + id,
        success: function(result) {
            if (result == 1) {
                //SUCCESS				
                $('#site-alert').slideUp();
            }
        },
        error: function(xhr) {
            console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
        }
    });
}

function updateTransaction(id, state) {
    if ((state !== 'cancelled') || (state == 'cancelled' && confirm("Are you sure you want to cancel this transaction? You can't undo this.") === true)) {
		if (state == 'accepted' && $('#shipping_cost').val() > 0){
			state = 'payment_requested&shipping=' + $('#shipping_cost').val();
		}
		if (state == 'offer_accepted'){
			if ($('#shipping_cost').val() > 0){
			state = 'payment_offered&shipping=' + $('#shipping_cost').val();
			}else{
			state = 'accepted';
			}			
		}
        $('#trans_' + id).addClass('tiny-spinner disabled');
        $.ajax({
            url: baseURL + '/ajax.cgi?a=updatetransaction&id=' + id + '&state=' + state,
            success: function(result) {
                if (result == 1) {
                    //SUCCESS				
                    $('#trans_' + id).removeClass('tiny-spinner disabled');
                    $('#trans_' + id).css('background-color', 'transparent');
                    $('#trans_' + id).html(success);
                    $('#trans_' + id).delay(3000).slideUp();
                } else {
                    $('#trans_' + id).removeClass('tiny-spinner disabled');
                    alert(notPossible);
                }
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
    }
}

var notif_page = 1;
var mess_page = 1;
var loading = 0;


$('#notifications').on('scroll', function() {
        if(($(this).scrollTop() > ($(this).innerHeight()/4)) && loading == 0) {
		loading = 1;
		$('.page-loader').removeClass('hidden');
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=getnotifications&page=' + notif_page,
        success: function(result) {
			$('#notifications').append(result);
            $('.page-loader').addClass('hidden');
			notif_page++;
			loading = 0;
        },
        error: function(xhr) {
			$('#notifications').append('Communication error! [Details: ' + xhr.status + ' - ' + xhr.responseText + ']');
            $('.page-loader').addClass('hidden');
			loading = 0;
        }
    })
        }
    });

$('#messages').on('scroll', function() {
        if(($(this).scrollTop() > ($(this).innerHeight()/4)) && loading == 0) {
		loading = 1;
		$('.page-loader').removeClass('hidden');
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=getconversations&page=' + mess_page,
        success: function(result) {
			$('#messages').append(result);
            $('.page-loader').addClass('hidden');
			mess_page++;
			loading = 0;
        },
        error: function(xhr) {
			$('#messages').append('Communication error! [Details: ' + xhr.status + ' - ' + xhr.responseText + ']');
            $('.page-loader').addClass('hidden');
			loading = 0;
        }
    })
        }
    });
	
	

$(document).on('click', '#support_submit', function(e) {
    e.preventDefault();
    if ($('#support_amount').val() == '') {
        alert('Please specify an amount in Euros');
        return false;
    } else {
        var item = encodeURIComponent('One-off contribution to Sharebay.com');
        var amount = $('#support_amount').val();
        var PPurl = 'https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=colinrturner%40gmail.com&item_name=' + item + '&amount=' + amount + '&currency_code=EUR';
        window.open(PPurl, '_blank');
    }
    return false;
});



// function spammit(listing_id) {
    // if (confirm("If you feel this listing is spam, misleading, inappropriate or offering something that is not genuinely free, you can report it confidentially by clicking 'OK'.") === true) {
        // var $query = baseURL + '/ajax.cgi?a=spammit&listing=' + listing_id;
        // $.ajax({
            // url: $query,
            // success: function(result) {
                // alert(result);
            // },
            // error: function(xhr) {
                // console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            // }
        // });
    // }
// }


function report(object_type, object_id) {
    if (confirm("If you feel this content is:\n- inappropriate\n- misleading\n- trying to sell something\n- spam\n\nPlease click OK to report it anonymously.") === true) {
        var $query = baseURL + '/ajax.cgi?a=report&object_type=' + object_type + '&object_id=' + object_id;
        $.ajax({
            url: $query,
            success: function(result) {
                showToast(result);
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
    }
}


function block(profile_id) {
    if (confirm("Are you sure you want to block this person?") === true) {
        var $query = baseURL + '/ajax.cgi?a=block&profile=' + profile_id;
        $.ajax({
            url: $query,
            success: function(result) {
                showToast(result);
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
    }
}


function unblock(profile_id) {
    if (confirm("Are you sure you want to unblock this person?") === true) {
        var $query = baseURL + '/ajax.cgi?a=unblock&profile=' + profile_id;
        $.ajax({
            url: $query,
            success: function(result) {
                showToast(result);
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
    }
}


function follow(object_type, object_id) {
        var $query = baseURL + '/ajax.cgi?a=follow&object_type=' + object_type + '&object_id=' + object_id;
        $.ajax({
            url: $query,
            success: function(result) {
                showToast(result);
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
}


function unfollow(object_type, object_id) {
        var $query = baseURL + '/ajax.cgi?a=unfollow&object_type=' + object_type + '&object_id=' + object_id;
        $.ajax({
            url: $query,
            success: function(result) {
                showToast(result);
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
}



function deleteListing(listing_id, return_url) {
    if (confirm("Are you sure you want to delete this listing?") === true) {
        $.ajax({
            url: baseURL + '/ajax.cgi?a=deletelisting&id=' + listing_id,
            success: function() {
                location.href = return_url;
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        })

    }
}


function adminObject(action, object, id){
    if (confirm("Are you sure?") === true) {
		var elem = $('#admin_' + object + '_' + id);
		elem.addClass('disabled');
        $.ajax({
            url: baseURL + '/ajax.cgi?a=adminobject&action=' + action + '&object=' + object + '&id=' + id,
            success: function(response) {
					// RELOAD ADMIN BOX
					elem.html(response);
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
		elem.removeClass('disabled');
    }
	
}



function adminDeleteListing(listing_id, return_url) {
    if (confirm("Are you sure you want to remove this listing?") === true) {
        $.ajax({
            url: baseURL + '/ajax.cgi?a=admindeletelisting&id=' + listing_id,
            success: function(response) {
				if (response == 1){location.href = return_url;
				}else{
					alert('No listing found for ID:' + listing_id);
				}
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        })

    }
}


function adminDeleteProfile(profile_id, return_url) {
    if (confirm("Are you sure you want to remove this profile?") === true) {
        $.ajax({
            url: baseURL + '/ajax.cgi?a=admindeleteprofile&id=' + profile_id,
            success: function(response) {
				if (response == 1){location.href = return_url;
				}else{
					alert('No profile found for ID:' + profile_id);
				}
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        })

    }
}



$(document).on('click', '#send_response', function(e) {
    e.preventDefault();
    if ($('.response_hide').is(':hidden')) {
        $('.response_hide').slideDown();
    } else {
        if ($('#listing_message').val() == '') {
            alert('You must enter a message!');
        } else {
            $('#loading').show();
            $.ajax({
                type: "POST",
                data: $("form#post_response").serialize(),
                url: baseURL + '/ajax.cgi',
                success: function(result) {
                    // DISPLAY RESULT
                    $("#post_response").html(result);
                    $("#loading").hide();
                    $('body').scrollTop(0);
                },
                error: function(xhr) {
                    $("#loading").hide();
                    console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                }
            });
        }
    }
});



// $(document).on('submit', '#write_review', function(e) {
    // e.preventDefault();
            // $('#loading').show();
            // $.ajax({
                // type: "POST",
                // data: $("form#write_review").serialize(),
                // url: baseURL + '/ajax.cgi',
                // success: function(result) {
                    // DISPLAY RESULT
                    // $("#write_review").html(result);
                    // $("#loading").hide();
                    // $('body').scrollTop(0);
                // },
                // error: function(xhr) {
                    // $("#loading").hide();
                    // console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                // }
            // });
// });



$(document).on('click', '#send_message', function(e) {
    e.preventDefault();
    if ($('.response_hide').is(':hidden')) {
        $('.response_hide').slideDown();
    } else {
        if ($('#message').val() == '') {
            alert('You must enter a message!');
        } else {
            $('#loading').show();
            $.ajax({
                type: "POST",
                data: $("form#post_message").serialize(),
                url: baseURL + '/ajax.cgi',
                success: function(result) {
                    // DISPLAY RESULT
                    $("#post_message").html(result);
                    $("#loading").hide();
                    $('body').scrollTop(0);
                },
                error: function(xhr) {
                    $("#loading").hide();
                    console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
                }
            });
        }
    }
});


function toggleSideBar() {
	if ($(window).width() <= 720 ) {
	if (document.getElementById("sidebar-container").style.left === '0%'){
		document.getElementById("sidebar-container").style.left = '-100%';
	}else{
		document.getElementById("sidebar-container").style.left = '0%';
	}
	}
};



function toggleHide(id){
	var elem = $('#' + id);
	if (elem.hasClass('hidden')){
		elem.removeClass('hidden');
	}else{
		elem.addClass('hidden');
	}
}


function toggleCommentMenu(object_type,object_id){
	var elem = $('#menu_' + object_type + '_' + object_id);
	if (elem.hasClass('hidden')){
		$.ajax({
            url: baseURL + '/ajax.cgi?a=getcommentmenu&object_type=' + object_type + '&object_id=' + object_id,
            success: function(result) {
                elem.html(result);
				elem.removeClass('hidden');
            },
            error: function(xhr) {
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
	}else{
		elem.addClass('hidden');
	}
}


function openModal(arg) {
    $('#loading').show();
    if (arg.match(/^http/)) { //If query, then send it.
        var $query = arg;
        $.ajax({
            url: $query,
            success: function(result) {
                $('#modalWrap').show();
                $('#modalContent').html(result);
                $('#loading').hide();
            },
            error: function(xhr) {
                $("#loading").hide();
                console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
            }
        });
    } else { //Or just return the input argument
        $('#modalWrap').show();
        $('#modalContent').html(arg);
        $('#loading').hide();
    };
};

function markSeen(convo_id) {
    $.ajax({
        url: baseURL + '/ajax.cgi?a=markseen&id=' + convo_id,
        success: function() {
            return;
        },
        error: function(xhr) {
            console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.statusText + ']');
        }
    })
}


function unblockEmail(id) {
    $.ajax({
        url: baseURL + '/ajax.cgi?a=sendunblock&id=' + id,
        success: function() {
            $('#unblockMessage').slideUp();
            return;
        },
        error: function(xhr) {
            console.log('Communication error! [Details: ' + xhr.status + ' - ' + xhr.responseText + ']');
        }
    })
}


function toggleAns(x) {
    if ($("#ans" + x).is(':visible')) {
        $("#ans" + x).slideUp();
    } else {
        $("#ans" + x).slideDown();
    }
}

function deleteAccount(name) {
    if (confirm("Are you sure you wish to delete the account '" + name + "'? \n\nDeleting your account will permanently delete all your data from our system. You can't undo this.\n\nAre you sure?") === true) {
        $("#loading").show();
        window.location = baseURL + '/profile?a=deleteaccount';
    }
}

function scrollChat() {
    $("#chat-window").scrollTop($("#chat-window")[0].scrollHeight);
    // $("#chat-window").animate({
        // scrollTop: $('#chat-window').prop("scrollHeight")
    // }, 1000);
}
