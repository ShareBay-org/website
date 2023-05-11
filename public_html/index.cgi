#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR THE MAIN HOME PAGE

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );

require './common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

if ($ENV{QUERY_STRING} =~ /^search/){
## PERFORM SEARCH

my $title;

if (!$FORM{filter}){$FORM{filter} = 'listings'};

my $this_filter = $FORM{filter};
if ($this_filter =~ m/cat_/){
my (undef, $cat_id) = split('_' , $this_filter);
($this_filter, undef) = &getCategory($cat_id);
}elsif($this_filter =~ m/member_/){
my (undef, $lister_id) = split('_' , $this_filter);
$this_filter = &getFullName($lister_id) . q~'s listings~;
}
# $this_filter = ucfirst($this_filter);

if ($FORM{search}){
$title = qq~Searching &apos;$FORM{search}&apos; in $this_filter~;
}else{
$title = qq~Showing all in $this_filter~;
}

my $footerInject = q~
<script>
var page = 1;
var loading = 0;

$('.searchIcon').css('visibility','visible');

var queryString = window.location.search.replace('?','&');


$(document).on('scroll', function() {
        if(($(this).scrollTop() > ($(this).innerHeight()/2)) && loading == 0) {
		loading = 1;
	if (LOGGED_IN === true){
		$('.page-loader').removeClass('hidden');
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=dosearch&screen=' + $(document).width() + '&page=' + page + queryString,
        success: function(result) {
			$('#feed-content').append(result);
            $('.page-loader').addClass('hidden');
			page++;
			loading = 0;
        },
        error: function(xhr) {
			$('#feed-content').append('Communication error! [Details: ' + xhr.status + ' - ' + xhr.responseText + ']');
            $('.page-loader').addClass('hidden');
			loading = 0;
        }
    })
	}else{
			$('#feed-content').append('<p class="helper bottom20">Please <a class="showLogin" href="javascript:void(0);">log in</a> to see more results.</p>');
        }
	}
    })

function getSuggestions(){
	if ($(document).width() >= 1024){
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=getsuggestions&height=' + $(window).height(),
        success: function(result) {
			$('#suggestions').html(result);
        }
    })
setTimeout(function() {getSuggestions()}, 120000);
	}
}

$(document).on('submit','form#search', function(){
toggleSideBar();
$('#loading').show();
});

getSuggestions();
window.setInterval(function(){
checkMessages();
}, 60000);



</script>

~;

my $desc = $title;
my $headerImage = $baseURL . '/i/crowds.jpg';
&header($title, $desc, $headerImage, undef, 'screen');

print qq~
<div class="feed-container clearfix">
<div class="page-loader hidden"><div></div><div></div><div></div></div>~;

&leftBar;

print qq~<div id="feed">~;

if ($LOGGED_IN){
	my $iCode = substr($myAuth, 0, 6);
	print qq~<div class="item" id="invite-nudge"><div id="closeBannerWrap"><div id="closeNudge">&times;</div></div>Like what we're doing? Why not <a href="$baseURL/?invite=$iCode">Invite your friends</a> and help expand the network?</div>~;
	my $pending = &checkPendingTrans;
	if ($pending){
	print qq~<div class="item" id="feed-alert"><div id="closeBannerWrap"><div id="closeBanner">&times;</div></div>You have $pending pending transaction~;
	print qq~s~ if $pending > 1;
	print qq~. <a href="$baseURL/transactions?id=$myID">See transactions</a>.</div>~;
	}
	print qq~	
	<div class="item" id="post-buttons">
	<button class="post-button post-offer">I can offer...</button>
	<button class="post-button post-request">I'm looking for...</button>
	</div>~;	
}else{
	print qq~<div class="item" id="feed-alert"><div id="closeBannerWrap"><div id="closeBanner">&times;</div></div><a class="showLogin" href="javascript:void(0);">Log in</a> or <a href="$baseURL/join">register</a> to access the full site and start sharing with other members.</div>~;
}

print qq~<div id="feed-content">~;
&doSearch;

print qq~
</div></div>

<div id="rightbar-container">
<div id="rightbar">
<h3>You might like:</h3>
<div id="suggestions"></div>
</div>
</div>
</div>
~;

&bareFooter($footerInject);


}elsif ($ENV{QUERY_STRING} =~ /^invite/){
	
# SHOW USER INVITATION

if (!$FORM{invite}){
&errorCatcher('Sorry, no such page exists, or you might not have permission to view it.');
}

my $sth = $SBdb->prepare("SELECT m.id, m.first_name, m.last_name, m.city, m.region, m.country, m.image, IFNULL(SUM(CASE WHEN m.id = t.giver_id AND t.status = 'delivered' THEN 1 END), 0) AS gave, IFNULL(SUM(CASE WHEN m.id = t.getter_id AND t.status = 'delivered' THEN 1 END), 0) AS got FROM members AS m LEFT JOIN transactions AS t ON m.id = t.giver_id OR m.id = t.getter_id WHERE m.authcode LIKE '$FORM{invite}%' AND activated = 1 GROUP BY m.first_name, m.last_name LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
# SHOW PROFILE
my ($id, $first_name, $last_name, $city, $region, $country, $imageRef, $gave, $got) = $sth->fetchrow_array;

if ($LOGGED_IN && $id != $myID){
&errorCatcher('You&apos;re already logged in. You need to <a class="logout" href="javascript:void(0);">log out</a> to view this page.');
}

my $title = "$first_name $last_name is inviting you to join Sharebay";
my $desc = "$first_name $last_name from $city, $region is inviting you to join them on Sharebay &ndash; the free sharing network.";

my $image;
my $hasImage = 1 if (-e "$siteroot/user_pics/$imageRef\.jpg");
if ($hasImage){
$image = qq~$baseURL/user_pics/$imageRef\.jpg~;
}else{
$image = '';
}

my $footerInject = qq~
<script>
var now = new Date();
now.setTime(now.getTime() + (86400000 * 30)); // SUPPRESS FOR 30 DAYS
document.cookie = "suppressNudge=1; expires=" + now.toUTCString() + "; domain=" + domain + "; path=/";
</script>
~;


&header($title, $desc, $image, undef, 'page');

my $offers = int($SBdb->do("SELECT id FROM posts WHERE lister = $id AND status = 'live' AND type = 'offer'")) || 0;
my $noMembers = &commafy(int($SBdb->do("SELECT id FROM members")/100) * 100) . '+';
my $getPosts = $SBdb->prepare("SELECT SUM(quantity) FROM posts");
$getPosts->execute;
my $noOffers = &commafy(int($getPosts->fetchrow_array/100) * 100) . '+';

if ($id eq $myID){
print qq~<p class="helper">This is a preview of your invitation page. <a href="javascript:void(0);" onclick="shareThis('$baseURL/?invite=$FORM{invite}')">Click here</a> to invite people to join you on Sharebay</p>~;
}
print qq~<div class="center clearfix">~;

if ($hasImage){
print qq~<img src="$image" class="profile-image rounded" title="$first_name $last_name"/>~;
}

# $got = 10;
# $gave = 0;
# $offers = 0;
print qq~<div class="profile-name">
<h1>&#9886; YOU&apos;RE INVITED &#9887;</h1>


<p class="bigger">$desc~;
print qq~ $first_name~ if ($got || $gave || $offers);
print qq~ has~ if ($got || $gave);
print qq~ already~;
print qq~ received $got time~ if ($got);
print qq~s~ if ($got > 1);
print qq~,~ if ($got && $gave && $offers);
print qq~ and~ if ($got && $gave && !$offers);
print qq~ given $gave time~ if ($gave);
print qq~s~ if ($gave > 1);
print qq~ and~ if (($gave||$got) && $offers);
print qq~ has $offers item~ if $offers;
print qq~s~ if $offers > 1;
print qq~ on offer~ if $offers;
print qq~!~ if ($got || $gave || $offers);
print qq~</p>

<p class="bigger">Why not join $first_name and start sharing in some of the $noOffers free goods and services already on offer from our amazing community of $noMembers givers?</p>~;

print qq~</div></div>~;

if ($id eq $myID){
print qq~<p class="center"><a href="javascript:void(0);" onclick="shareThis('$baseURL/?invite=$FORM{invite}')" class="green-button bigger">SEND INVITATIONS</a></p>~;
}else{
print qq~<p class="center"><a href="$baseURL/join?invite=$FORM{invite}" class="green-button bigger">Join $first_name</a></p>~;
}
print qq~<p class="center grey">Sharebay is a global network, based in Ireland. It’s free to use and always will be.</p>~;

&bareFooter($footerInject);

}else{
# NO PROFILE FOUND
&errorCatcher("Sorry, no such profile exists.");
}
	
}elsif ($LOGGED_IN){
## SHOW LOGGED IN FEED

## PREVENT CACHING
my $headerInject = qq~<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<link rel="stylesheet" href="$baseURL/slim/slim.min.css">
~;

my $footerInject = q~
<script>
var page = 1;
var loading = 0;

$('.searchIcon').css('visibility','visible');

$(document).on('scroll', function() {
        if(($(this).scrollTop() > ($(this).innerHeight()/2)) && loading == 0) {
		loading = 1;
		$('.page-loader').removeClass('hidden');
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=getfeed&screen=' + $(document).width() + '&page=' + page,
        success: function(result) {
			$('#feed-content').append(result);
            $('.page-loader').addClass('hidden');
			page++;
			loading = 0;
        },
        error: function(xhr) {
			$('#feed-content').append('Communication error! [Details: ' + xhr.status + ' - ' + xhr.responseText + ']');
            $('.page-loader').addClass('hidden');
			loading = 0;
        }
    })
        }
    })

function getSuggestions(){
	if ($(document).width() >= 1024){
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=getsuggestions&height=' + $(window).height(),
        success: function(result) {
			$('#suggestions').html(result);
        }
    })
setTimeout(function() {getSuggestions()}, 120000);
	}
}

getSuggestions();

window.onload = function() {
    if (window.jQuery) {  
        // jQuery is loaded  
		$('.post-offer, .post-request').removeClass('disabled');
    }

}

</script>
<script src="~ . $baseURL . q~/slim/slim.jquery.js"></script>
<script src="~ . $baseURL . q~/js/post.js?v=~ . $version . q~"></script>
~;

my $title = 'Latest activity on Sharebay';
my $desc = qq~The latest offers and requests on Sharebay~;
my $headerImage = $baseURL . '/i/crowds.jpg';
&header($title, $desc, $headerImage, $headerInject, 'screen');

print qq~
<div class="feed-container clearfix">
<div class="page-loader hidden"><div></div><div></div><div></div></div>~;

&leftBar;

print qq~<div id="feed">~;

if ($LOGGED_IN){
	my $iCode = substr($myAuth, 0, 6);
	print qq~<div class="item" id="invite-nudge"><div id="closeBannerWrap"><div id="closeNudge">&times;</div></div>Like what we're doing? Why not <a href="$baseURL/?invite=$iCode">Invite your friends</a> and help expand the network?</div>~;
	my $pending = &checkPendingTrans;
	if ($pending){
	print qq~<div class="item" id="feed-alert"><div id="closeBannerWrap"><div id="closeBanner">&times;</div></div>You have $pending pending transaction~;
	print qq~s~ if $pending > 1;
	print qq~. <a href="$baseURL/transactions?id=$myID">See transactions</a>.</div>~;
	}
	print qq~	
	<div class="item" id="post-buttons">
	<button class="post-button post-offer disabled">I can offer...</button>
	<button class="post-button post-request disabled">I'm looking for...</button>
	</div>~;	
}else{
	print qq~<div class="item" id="feed-alert"><div id="closeBannerWrap"><div id="closeBanner">&times;</div></div><a class="showLogin" href="javascript:void(0);">Log in</a> or <a href="$baseURL/join">register</a> to access the full site and start sharing with other members.</div>~;
}

print qq~<div id="feed-content">~;
&getFeed;

print qq~
</div></div>

<div id="rightbar-container">
<div id="rightbar">
<h3>You might like:</h3>
<div id="suggestions"></div>
</div>
</div>
</div>
~;

&bareFooter($footerInject);


}else{
## NOT LOGGED IN, SHOW HOME PAGE
	
my $title = 'Sharebay - The Sharing Network';
my $desc = 'We are a community of thousands of people across the world sharing free goods and services';

my $num_members = $SBdb->do("SELECT id FROM members WHERE activated = 1");
my $get_listings = $SBdb->prepare("SELECT SUM(quantity) FROM posts WHERE status = 'live'");
$get_listings->execute;
my $num_listings = $get_listings->fetchrow_array;
$get_listings->finish;

my $headerInject = qq~
<style>

body{
	
background-color: var(--opaque);
}
.homeBG{
	width: 100%;
	background: var(--opaque) url('$baseURL/i/crowds.jpg') no-repeat center center; 
	background-size: cover;
	background-blend-mode: multiply;

}
.heading{
	font-weight: 600;
	text-align: center;
	color: white;
	text-shadow:
	0 6px 6px rgba(0,0,0,0.84);
}
.boomer{
	font-size: 84px;
}
.subheading{
	font-size: 40px;
}
.home-page-height{
	min-height: 85%;
	min-height: calc(100vh - 160px);
	position: relative;
}
.button-container{
	width: auto;
	display: inline-block;
	max-width: 500px;
	text-align: center;
	border-radius: 20px;
	background: rgba(255,255,255,1);
	padding: 1em 2em;
	}
a.home-button{
	background-color: var(--brand);
	display: inline-block;
	width: 70%;
	max-width: 400px;
	font-size: 20px;
	padding: 10px 20px;
	margin: 2%;
	border-radius: 9px;
	color: white;
	text-transform: uppercase;
	transition: 0.3s ease;
}
a.home-button:hover{
	text-decoration: none;
	background: var(--darkbrand);
	color: #fff;
}
.flex-center{
 display: flex;
 align-items: center;
 justify-content: center;
}
.bullets{
	font-size: 1.2em;
	width: 100%;
	max-width: 600px;
	margin: 0 auto;
	color: var(--darkbrand);
	overflow: hidden;
	margin-bottom: 2em;
	border-radius: 16px;
	}

.fadein {
    opacity: 0;
}
.slidein-left{
    opacity: 0;
	position: absolute;
	width: 100%;
	top:0;
	bottom:0;
	right: 20%;	
}
.slidein-right{
    opacity: 0;
	position: absolute;
	width: 100%;
	top:0;
	bottom:0;
	left: 20%;	
}
.guest{
	background: var(--navy);
	color: white;
	padding: 5px 10px;
}
.image-background, .image-contain{
	background-position: center center;
	background-repeat: no-repeat;
}
.image-background{
	background-size: cover;
}
.image-contain{
	background-size: contain;
}
.giving-container{
	min-height: 45vw;
	overflow: hidden;
}
.giving{
	min-height: 45vw;
}
.giving h1 {
    position: absolute;
    bottom: 8%;
    left: 15%;
    font-size: 2.4em;
    text-align: left;
}

\@media only screen and (max-width : 600px) {

h1{
	font-size: 1.8em;
}
h2{
	font-size: 1.3em;
}
.bullets{
	margin-bottom: 0;
	border-radius: 0;
	}
.giving-container{
	min-height: 90vw;
}
.giving{
	min-height: 90vw;
}
.giving h1 {
    left: 10%;
    font-size: 2.1em;
}
.home-page-height{
Xmin-height: calc(50vh - 60px);
}
.boomer{
	font-size: 48px;
}
.subheading{
	font-size: 28px;
}
a.home-button{
	margin: 10px 4%;
}
}

\@media only screen and (max-width : 400px) {

body{
	font-size: 14px;
}
}
</style>~;

$headerInject .= q~
<script>

$(window).scroll(function(){
	
        $('.fadein').each( function(i){
			
            var bottom_of_object = $(this).offset().top + ($(this).outerHeight() / 2);
            var bottom_of_window = $(window).scrollTop() + $(window).height();
            if( bottom_of_window > bottom_of_object ){
                
                $(this).animate({'opacity':'1'},400);
				
            }
        }); 
		
        $('.slidein-left').each( function(i){
			
            var bottom_of_object = $(this).offset().top + ($(this).outerHeight() / 2);
            var bottom_of_window = $(window).scrollTop() + $(window).height();
            if( bottom_of_window > bottom_of_object ){
				$(this).animate({'opacity':'1'},{duration : 400, queue : false})
						.animate({'right' : 0},{duration : 400, queue : false});
            }
			
        }); 
		
        $('.slidein-right').each( function(i){
			
            var bottom_of_object = $(this).offset().top + ($(this).outerHeight() / 2);
            var bottom_of_window = $(window).scrollTop() + $(window).height();
            if( bottom_of_window > bottom_of_object ){
				$(this).animate({'opacity':'1'},{duration : 400, queue : false})
						.animate({'left' : 0},{duration : 400, queue : false});
            }
            
        }); 
    });

</script>
~;

&header($title, $desc, undef, $headerInject, 'screen');

print qq~
<div class="homeBG clearfix">
<div class="half flex-center home-page-height bigOnly"></div>

<div class="half home-page-height flex-center">
<div class="button-container">
<div class="content">
<img src="$baseURL/icon.png" style="width:200px;height:200px;margin-top:-100px;"/>
<h1 class="center">Welcome to our global sharing network of <span id="member-count" data-count="$num_members">0</span> members sharing <span id="listing-count" data-count="$num_listings">0</span> free goods and services.</h1>
</div>~;
&generalCTA;
print qq~
<!-- a class="home-button clear" a href="$baseURL/join">Join (It's free)</a>
<a class="home-button showLogin clear">Log in</a -->
<div class="center smaller top20 hidden">
<a href="$baseURL/?search" class="guest">CONTINUE AS GUEST</a>
</div></div></div></div>

<div class="content">
<h1 class="center">Join our amazing community of givers and helpers!</h1>
<div class="giving-container">
<div class="half flex-center giving">
<div class="giving image-contain slidein-left" style="background-image: url('$baseURL/i/giving-balloon-01.png');">
<h1>Give a little...</h1>
</div>
</div>
<div class="half flex-center giving">
<div class="giving image-contain slidein-right" style="background-image: url('$baseURL/i/giving-balloon-02.png');">
<h1>Get a lot!</h1>
</div>
</div>
</div>
</div>


<div class="content">
<h1 class="center">That's it. There's no catch.</h1>
<h2 class="center">Sharebay is free to use and always will be.</h2>
</div>
<div>
<div class="bullets green-white">
<img class="full-width-image bottom20" src="$baseURL/i/nine-ways.jpg"/>
<div class="content">
<p>Use Sharebay to:</p>
<ul>
<li>Enjoy free goods and services!</li>
<li>Share your talents &amp; skills</li>
<li>Give away items you no longer need</li>
<li>Get help when you need it</li>
<li>Reduce emissions and waste</li>
<li>Promote sharing and collaboration</li>
<li>Build trust locally and around the world</li>
<li>Organise community programs and meetups</li>
<li>Meet like-minded people</li>
</ul>~;
&generalCTA;

print qq~</div></div></div>

<script>

const memberCount = document.getElementById('member-count');
const listingCount = document.getElementById('listing-count');
let m_count = 0;
let l_count = 0;

const memberCountUp = setInterval(() => {
  let m_boxCount = parseInt(memberCount.dataset.count)
  if(m_count == m_boxCount) clearInterval(memberCountUp)
  memberCount.innerHTML = m_count.toLocaleString()
  m_count = m_count + Math.floor((m_boxCount/100))
  if(m_count > m_boxCount) m_count = m_boxCount
}, 20);

const listingCountUp = setInterval(() => {
  let l_boxCount = parseInt(listingCount.dataset.count)
  if(l_count == l_boxCount) clearInterval(listingCountUp)
  listingCount.innerHTML = l_count.toLocaleString()
  l_count = l_count + Math.floor((l_boxCount/100))
  if(l_count > l_boxCount) l_count = l_boxCount
}, 20);


</script>~;

&footer;
}
# Exeunt
