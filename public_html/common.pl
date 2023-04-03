#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT CONTAINS COMMON SUBROUTINES AND 
# BASIC INPUT PROCESSING USED BY OTHER SCRIPTS 

# MODULES AND SCRIPT SETTINGS
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );
use Env qw( REQUEST_METHOD QUERY_STRING REMOTE_ADDR CONTENT_LENGTH );
# use JSON;
use JSON::PP;
use DBI;
use CGI;
our $maintenance = 0; # 1 = MAINTENANCE MODE; 0 = NORMAL
our $version = 3.045003;
# our $version = time();

# PROCESS FORM AND QUERY INPUT
our (%FORM, $buffer);
if(defined($ENV{REQUEST_METHOD}) && $ENV{REQUEST_METHOD} eq "GET"){$buffer=$ENV{QUERY_STRING};}
else {read(STDIN, $buffer, $ENV{CONTENT_LENGTH});}
my @pairs = split(/&/, $buffer);
foreach my $pair (@pairs){
my ($name, $value) = split(/=/, $pair);
$value =~ tr/+/ /;
$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
#~ $value = &addSlashes($value);
$FORM{$name} = $value;}

# GET IP ADDRESS
our $ip = $ENV{REMOTE_ADDR}; # if defined($ENV{REMOTE_ADDR});

# FORMAT TIME
our $now=(time);

use Cwd 'abs_path';
my $thisDir .= abs_path();
require $thisDir . '/config.pl';

our ($domain, $dir, $baseURL, $siteroot, $root, $salt, $dbName, $dbHost, $dbUser, $dbPass, $emailPW, $HP_dbName, $HP_dbHost, $HP_dbUser, $HP_dbPass);

# GLOBAL VARIABLES
# our $domain = 'sharebay.org'; 
# our $siteroot = '/home/sharebay/public_html'; 
# our $root = '/home/sharebay/_private';
# our $salt = 'Spider Spider'; # FOR PASSWORD ENCRYPTION
# our $baseURL = 'https://www.' . $domain;
our $admin = 'hello@sharebay.org';
our $notify = 'notify@sharebay.org';
our $newsletter = 'newsletter@sharebay.org';
our ($LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount);
our $a = $FORM{a};
our $isModal = $FORM{isModal};
our $defaultImage = $baseURL . '/i/giving-balloon-OG-image.png';

## CONNECT TO SHAREBAY (REMOTE) DATABASE
our $SBdb = DBI->connect("DBI:mysql:database=$dbName;host=$dbHost;mysql_local_infile=1", $dbUser, $dbPass,{RaiseError => 1, PrintError => 1});
my $SB_enc = $SBdb->do("SET NAMES 'utf8mb4'");

# CONNECT TO HONORPAY DATABASE
our $HPdb = DBI->connect("DBI:mysql:database=$HP_dbName;host=$HP_dbHost;mysql_local_infile=1", $HP_dbUser, $HP_dbPass,{RaiseError => 1, PrintError => 1});
my $HP_enc = $HPdb->do("SET NAMES 'utf8mb4'");

# CHECK FOR LOG IN COOKIE0
my $cgi = new CGI;
our $SESSION_ID = $cgi->cookie('SESS_ID'); #GLOBAL TO ENABLE THUMBNAIL CHANGE
my $iCode;

if ($SESSION_ID){
## CHECK FOR SESSION ID IN DATABASE
my $getSession = $SBdb->prepare("SELECT m.id, CONCAT_WS(' ', m.first_name, m.last_name) AS full_name, m.image, m.language, m.auto_trans, m.lat, m.lon, m.authcode, m.is_moderator, m.is_author, m.is_admin, m.joined, COUNT(p.id) AS listing_count FROM members AS m LEFT JOIN posts AS p ON m.id = p.lister WHERE m.session_id = '$SESSION_ID' GROUP BY m.id LIMIT 1");
$getSession->execute;
if ($getSession->rows eq 1){
($myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount) = $getSession->fetchrow_array;
if (!$myImage){$myImage = 'q'};
$LOGGED_IN = 1;
$iCode = substr($myAuth, 0, 6);
}
$getSession->finish;

if ($LOGGED_IN){
my $setActive = $SBdb->do("UPDATE members SET last_active = '$now' WHERE id = '$myID' LIMIT 1");
}
$getSession->finish;
}


# TEST FOR VISITOR ID OR CREATE ONE IF NOT EXISTS
# my $visitor_id = '';
my $get_visitor = new CGI;
my $visitor_id = $get_visitor->cookie('visitorID');
if (!$visitor_id){
# CREATE VISITOR ID
my @chars = ('a'..'z','A'..'Z',0..9);
$visitor_id = join '', (map {$chars [rand@chars]} @chars)[0..16];
}
if (!$LOGGED_IN){$myID = $visitor_id;}


# GET IP LOCATION IF NO LAT OR LONG
if ($ip && (!$myLat || !$myLon)){
($myLat, $myLon, undef, undef, undef, undef) = &getCurrentLocation;
}


# SET HTTP HEADERS

my $commonHeader = "Access-Control-Allow-Origin: $baseURL;\nExpires:0\nSet-Cookie: visitorID=$visitor_id; Domain=$domain; Path=/; Expires=Fri, 31 Dec 9999 23:59:59 GMT; Secure; HttpOnly;\n";

sub textHeader{
print $commonHeader, qq~Content-type: text/plain; charset=utf-8\n\n~;
}

sub htmlHeader{
print $commonHeader, qq~Content-type: text/html; charset=utf-8\n\n~;
}

sub jsonHeader{
print $commonHeader, qq~Content-type: application/json; charset=utf-8\n\n~;
}

sub header{
if ($maintenance && !$myAdmin){
print qq~Content-type: text/html; charset=utf-8\n\n<html><body style="background-color: #dde3bd;text-align:center !important;font-family:'sans serif', helvetica, arial;"><img src="$baseURL/apple-touch-icon.png" style="width:120px;height:120px;"/><h2>Sharebay is temporarily closed for maintenance.</h2><p>Please be patient while we are carrying out essential site maintenance.</p><p>Check our <a href="https://facebook.com/sharebay.org" title="Facebook">Facebook</a> or <a href="https://twitter.com/sharebayorg" title="Twitter">Twitter</a> accounts for updates.</p></body></html>~;
exit;
}

# MAIN SITE HEADER
my ($title, $desc, $image, $headerInject, $template) = @_;

$headerInject .= qq~
<style>

</style>
<script>
</script>
~;

if ($isModal){
print qq~$headerInject\n~;
}else{

if (!$image){$image = $defaultImage;}
my $pending = 0; # PENDING TRANSACTIONS
$pending = &checkPendingTrans if $LOGGED_IN;
# START HTML
# &htmlHeader;
print qq~Access-Control-Allow-Origin: $baseURL;\nExpires:0\nSet-Cookie: visitorID=$visitor_id; Domain=$domain; Path=/; Expires=Fri, 31 Dec 9999 23:59:59 GMT; Secure; HttpOnly;\nContent-type: text/html; charset=utf-8\n\n
<!DOCTYPE html>
<html>
<head>
<script>
var domain = '$domain';
var dir = '$dir';
var baseURL = '$baseURL';
var visitorID = '$visitor_id';
var LOGGED_IN = ~; if ($LOGGED_IN){print 'true; '}else{print 'false;'};

if ($LOGGED_IN){

# GET DEFINED LANGUAGE
print qq~
var pending = $pending;
var myLang = '$myLang';
var myTrans = '$myTrans';
if (myTrans == 1){
document.cookie = "googtrans=" + "/auto/" + myLang + ";expires=;path=/;";
document.cookie = "googtrans=" + "/auto/" + myLang + ";expires=;domain=$domain;path=/;";
}else{
document.cookie = "googtrans=;expires=;path=/;";
document.cookie = "googtrans=;expires=;domain=$domain;path=/;";
}
history.scrollRestoration = "manual";
~;
}
print qq~</script>~;

my $cat_select = &getFilters($FORM{filter});

print qq~
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<meta name="theme-color" content="#E8E8E8"/>
<meta name="mobile-web-app-capable" content="yes">
<title>$title</title>
<meta name="keywords" content="sharing, library, tool library, skill library, sharing library, skill sharing, volunteers, internet of things, library of things, degrowth, open access, open access economy, resource-based economy, gift economy, sharing economy, buy nothing, cooperative, shop less share more, freeworlder, colin r turner, freebay, p2p, freeconomy, free goods and services" />
<meta name="description" content="$desc" />
<link rel="canonical" href="$ENV{HTTP_HOST}$ENV{REQUEST_URI}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="$title" />
<meta property="og:description" content="$desc" />
<meta property="og:url" content="$ENV{HTTP_HOST}$ENV{REQUEST_URI}" />
<meta property="og:image" content="$image" />
<meta name="twitter:card" content="summary">
<meta name="twitter:creator" content="\@sharebayorg">
<meta property="twitter:title" content="$title">
<meta name="twitter:image" content="$image">
<meta property="twitter:description" content="$desc">	  
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="stylesheet" href="$baseURL/css/styles.css?v=$version">
<link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght\@400;700&family=Raleway:wght\@400&family=Merriweather:wght\@400&display=swap" rel="stylesheet">~;
if ($LOGGED_IN){print qq~
<script type="text/javascript">
function googleTranslateElementInit() {
  new google.translate.TranslateElement({pageLanguage: 'en', layout: google.translate.TranslateElement.InlineLayout.SIMPLE, autoDisplay: false, multilanguagePage: true}, 'google_translate_element');
}
</script>
<script type="text/javascript" src="https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit"></script>~;
}
print qq~
<script src="https://kit.fontawesome.com/b1f9d7508a.js" crossorigin="anonymous"></script>
<!-- Global site tag (gtag.js) - Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2LYB66GDWG"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-2LYB66GDWG');
</script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
<script src="//maps.googleapis.com/maps/api/js?v=3&key=AIzaSyD4zc3ELJ8ZgqLMZqLhLGv7beewD6wN9eU"></script>
<script src="$baseURL/js/linkify.min.js"></script>
<script src="$baseURL/js/linkify-jquery.min.js"></script>
$headerInject		
</head>
<body>
<div id="loading"><div class="spinner"></div></div>
<div id="contentBlur"></div>
<div id="toast"><span id="toastMessage"></span><div id="closeToast">&times;</div></div>
<div id="cookies-message"><div>Please be aware that we use cookies to improve your browsing experience according to our <a href="$baseURL/page?id=privacy-policy">privacy policy</a>.</div> <button id="accept-cookies">I accept</button></div>~;
if ($LOGGED_IN && $template ne 'map'){
	print qq~
<div id="add_offer" title="Share something.." class="post-offer"><i class="fa fa-plus" aria-hidden="true"></i></div>~;
}
print qq~
<div id="modalWrap">
<div id="modal"><div id="closeModal">&times;</div>
<div id="modalContent"><div class="tSpinner"></div></div>
</div></div>~;
if ($LOGGED_IN){
print qq~<div id="google_translate_element"></div>~;
}
print qq~
<div id ="topbar">
<div id="logo" class="flex-center-left pointer" onclick="window.location.href='$baseURL';"><img alt="Sharebay logo" src="$baseURL/i/logo.svg"/></div>

<!-- LINKS -->

<div class="bigLinks">

<!-- BIG SCREENS -->~;

if (!$LOGGED_IN){
print qq~
<a class="button showMenu" title="Log in or register" href="javascript:void(0);">Log in&nbsp;<div class="pro_thumb" title="Log in or register"  style="background-image: url('$baseURL/user_pics/q_t.jpg');"></div></a>~;
}else{
print qq~
<a class="button showMenu" title="Logged in as $myName" href="javascript:void(0);"><div class="pro_thumb" title="Logged in as $myName"  style="background-image: url('$baseURL/user_pics/$myImage\_t.jpg');"></div></a>

<a class="button menu-icon showMessages" href="javascript:void(0);" title="My messages"><i class="fa-regular fa-envelope"></i><div class="message-alert yellow-alert"></div></a>

<a class="button menu-icon showNotifications" href="javascript:void(0);" title="Notifications"><i class="fa-regular fa-bell bigger"></i><div class="notification-alert yellow-alert"></div></a>

<a class="button menu-icon smallOnlyFlex searchIcon" href="javascript:void(0);" onclick="toggleSideBar();" title="Search"><i class="fa fa-search"></i></a>
~;
}

if ($maintenance){
print qq~<a class="button" style="color: red;" href="#">[M]</a>~;
}
if ($domain !~ /sharebay.org/){
print qq~<a class="button" style="color: red;" href="#">[DEV]</a>~;
}

print qq~
</div>
<div class="menu" id="notifications"></div>
<div class="menu" id="messages"></div>
<div class="menu" id="subMenu">~;
if ($LOGGED_IN){
print qq~
<a class="button" href="$baseURL/post">Post a listing</a>
<a class="button" href="$baseURL/?invite=$iCode">Invite a friend</a>~;
}else{
print qq~
<a class="button" href="$baseURL/join">Join Sharebay</a>
<a class="button showLogin" href="javascript:void(0);">Log in</a>~;
}

if ($LOGGED_IN){
print qq~
<a class="button" href="$baseURL/profile?id=$myID">View Profile</a><br/>
<a class="button" href="$baseURL/listings">My Listings</a><br/>~;

my $getTrans = $SBdb->do("SELECT id FROM transactions WHERE giver_id = '$myID' OR getter_id = '$myID'");
if ($getTrans > 0){
print qq~
<a class="button" href="$baseURL/transactions?id=$myID">My Transactions</a><br/>
<a class="button" href="$baseURL/reviews?a=myreviews">Reviews given</a><br/>
<a class="button" href="$baseURL/reviews?a=read&id=$myID">Reviews received</a><br/>
~;
}
print qq~
<a class="button" href="$baseURL/messages">My Messages</a><br/>
<a class="button" href="$baseURL/edit">Edit Profile &amp; Settings</a><br/>
<a class="button logout" href="javascript:void(0);">Log out</a>~;
}

print qq~
</div>
</div>~;




if ($template eq 'page'){print qq~<div class="page">~;}
elsif ($template eq 'blog'){print qq~<div class="page blog">~;}
elsif ($template eq 'chat'){print qq~<div class="chat-container">~;}
elsif ($template eq 'search'){print qq~<div id="searchContainer">~;}
elsif ($template eq 'wall'){print qq~<div class="wall">~;}
elsif ($template eq 'map'){print qq~<div class="map">~;}
elsif ($template eq 'screen'){print qq~<div class="screen">~;}
}
}

sub footer{
my $footerInject = shift;

if ($isModal){
print $footerInject;
}else{
print qq~</div>
<div class="bottom"><div class="bottomLinks-container">
	<div class="bottomLinks">
	<p>Browse</p>
	<a href="$baseURL/?search&filter=offers&order=latest" title="Latest offers">Latest offers</a>
	<a href="$baseURL/?search&filter=requests&order=latest" title="Requests">Latest requests</a>
	<a href="$baseURL/?search&filter=members&order=latest" title="Browse newest members">Latest members</a>
	<a href="$baseURL/map" title="Search on map">Search on map</a>
	<a href="$baseURL/page?id=categories" title="Browse categories<">Browse categories</a>
	<a href="$baseURL/post" title="Create a listing">Create a listing</a>
	<a href="$baseURL/page?id=templates" title="Browse our listing templates">Listing templates</a>
</div>
	<div class="bottomLinks">	
	<p>About Sharebay</p>
	<a href="$baseURL/about" title="About Sharebay">About</a>
	<a href="$baseURL/how-it-works" title="How Sharebay works">How it works</a>
	<a href="$baseURL/page?id=stats" title="Statistics">Statistics</a>
	<a href="$baseURL/transactions" title="Public Transaction Record">Transaction Record</a>
	<a href="$baseURL/faqs" title="Frequently asked questions">FAQs</a>
	<a href="$baseURL/blog" title="Blog">Sharebay Blog</a>
	<a href="$baseURL/page?id=terms-of-service" title="Terms of service">Terms of service</a>
	<a href="$baseURL/page?id=privacy-policy" title="Privacy policy">Privacy policy</a>
	<a href="$baseURL/contact" title="Contact us">Contact us</a>
</div>
	<div class="bottomLinks">
	<p>My account</p>~;
	if ($LOGGED_IN){
		
print qq~
<a href="$baseURL/profile?id=$myID">View Profile</a>
<a href="$baseURL/listings">My Listings</a>
<a href="$baseURL/transactions?id=$myID">My Transactions</a>
<a href="$baseURL/messages">My Messages</a>
<a href="$baseURL/notifications">My Notifications</a>
<a href="$baseURL/edit">Edit Profile &amp; Settings</a>
<a class="logout" href="javascript:void(0);">Log out</a>~;
	}else{
		print qq~
		<a class="showLogin" href="javascript:void(0);">Log in</a>
		<a href="$baseURL/join">Create account</a>~;
	}
	print qq~
</div>
	<div class="bottomLinks">
	<p>Find us on</p>
	<a href="https://facebook.com/sharebay.org" title="Facebook">Facebook</a>
	<a href="https://twitter.com/sharebayorg" title="Twitter">Twitter</a>
	
	<p>Support us</p>
	<a href="$baseURL/donate" title="Support us">Become a patron</a>
	<a href="$baseURL/media" title="Media / Press">Media &amp; printables kit</a>
</div>
</div>
<div class="bottomStrap">
<a href="https://ezweb.ie/" target="_blank" style="color: lightgrey">Designed by ezWeb.ie</a> &#127795; <a href="https://wildhost.co.uk/" target="_blank" style="color: lightgrey">Powered by Wildhost</a><br/><a href="https://www.trade-free.org/directory/goods-services/sharebay-org/" title="Sharebay.org is a trade-free site" target="_blank" style="color: lightgrey">Sharebay.org is a trade-free site</a>
</div></div>
<script>
\$('.comment, .chat-right, .chat-left, .chat-alert').linkify({target: "_blank"});
</script>
<script src="$baseURL/js/common.js?v=$version"></script>~;

if ($FORM{msg}){
print qq~
<script>
showToast('$FORM{msg}');
</script>~;
}

if ($LOGGED_IN){
	print qq~
<script>
window.setInterval(function(){
checkMessages();
}, 60000);
checkMessages();
</script>~;
}
print qq~$footerInject
</body></html>~;
}
}


sub bareFooter{
my $footerInject = shift;
print qq~</div>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
<script src="$baseURL/js/linkify.min.js"></script>
<script src="$baseURL/js/linkify-jquery.min.js"></script>
<script>
\$('.comment, .chat-right, .chat-left, .chat-alert').linkify({target: "_blank"});
</script>
<script src="$baseURL/js/common.js?v=$version"></script>~;

if ($FORM{msg}){
print qq~
<script>
showToast('$FORM{msg}');
</script>~;
}
if ($LOGGED_IN){
	print qq~
<script>
window.setInterval(function(){
checkMessages();
}, 60000);
checkMessages();
</script>~;
}
print qq~$footerInject
</body></html>~;
}


sub adminBox{
my ($object_type, $object_id, $risk) = @_;
if ($object_type && $object_id){
my ($maxRisk, $is_moderator, $is_author, $is_admin);
if ($object_type eq 'profile'){
my $getRights = $SBdb->prepare("SELECT is_moderator, is_author, is_admin FROM members WHERE id = '$object_id' LIMIT 1");
$getRights->execute;
if ($getRights->rows eq 1){
($is_moderator, $is_author, $is_admin) = $getRights->fetchrow_array;
}
my $getMax = $SBdb->prepare("SELECT MAX(risk) FROM members WHERE activated = 1");
$getMax->execute;
$maxRisk = $getMax->fetchrow_array;
$getRights->finish;
$getMax->finish;
}elsif($object_type eq 'listing'){
my $getMax = $SBdb->prepare("SELECT MAX(risk) FROM posts WHERE status = 'live'");
$getMax->execute;
$maxRisk = $getMax->fetchrow_array;
$getMax->finish;
}
if (!defined $risk){
my $sth;
$sth = $SBdb->prepare("SELECT risk FROM members WHERE id = '$object_id' LIMIT 1") if $object_type eq 'profile';
$sth = $SBdb->prepare("SELECT risk FROM posts WHERE id = '$object_id' LIMIT 1") if $object_type eq 'listing';
$sth->execute;
$risk = $sth->fetchrow_array;
}
my $colour = 'green';
my $risk_type = 'Safe';
if ($risk > ($maxRisk / 3) && $risk <= ($maxRisk * 2 / 3)){$colour = 'orange'; $risk_type = 'Moderate'}
elsif ($risk > ($maxRisk * 2 / 3)){$colour = 'red'; $risk_type = 'High'};
my $box = qq~<div class="admin" style="border-color:$colour;"><div class="admin-legend" style="color:$colour;">ADMIN TOOLS</div><span style="color:$colour">&#11044; $risk_type</span> | Score: $risk/$maxRisk</br/>~;
$box .= qq~<a class="smaller" onclick="adminObject('safe', '$object_type', $object_id);" href="javascript:void(0);">Mark as safe</a> | ~ if $risk > 0;
$box .= qq~<a class="smaller" onclick="adminObject('remove', '$object_type', $object_id);" href="javascript:void(0);">Remove ~;
$box .= $object_type eq 'profile' ? 'profile' : 'listing';
$box .= qq~</a>~;
if ($object_type eq 'profile' && $myAdmin){
$box .= qq~ | <a class="smaller" onclick="adminObject('~;
$box .= $is_moderator ? 'remove' : 'make';
$box .= qq~_moderator', '$object_type', $object_id);" href="javascript:void(0);">~;
$box .= $is_moderator ? 'Remove as' : 'Make';
$box .= qq~ moderator</a>~;
$box .= qq~ | <a class="smaller" onclick="adminObject('~;
$box .= $is_author ? 'remove' : 'make';
$box .= qq~_author', '$object_type', $object_id);" href="javascript:void(0);">~;
$box .= $is_author ? 'Remove as' : 'Make';
$box .= qq~ author</a>~;
$box .= qq~ | <a class="smaller" onclick="adminObject('~;
$box .= $is_admin ? 'remove' : 'make';
$box .= qq~_admin', '$object_type', $object_id);" href="javascript:void(0);">~;
$box .= $is_admin ? 'Remove as' : 'Make';
$box .= qq~ admin</a>~;
}
$box .= qq~</div>~;
return $box;
}else{
return;
}
}



sub getMyStuff{
my $my_stuff;

## WHICH LISTINGS DO I OWN?
my $listing_ids;
my $getListings = $SBdb->prepare("SELECT id FROM posts WHERE lister = '$myID' AND status = 'live'");
$getListings->execute;
if ($getListings->rows > 0){
while (my $id = $getListings->fetchrow_array){
$listing_ids .= "$id,";
}
chop($listing_ids);
$my_stuff .= qq~ OR (i.object_type = 'listing' AND i.object_id IN ($listing_ids))~;
}
$getListings->finish;

## WHICH BLOGS DO I OWN?
my $getBlogs = $SBdb->prepare("SELECT id FROM blog WHERE author_id = '$myID'");
$getBlogs->execute;
my $blog_ids;
if ($getBlogs->rows > 0){
while (my $id = $getBlogs->fetchrow_array){
$blog_ids .= "$id,";
};
chop($blog_ids);
$my_stuff .= qq~ OR (i.object_type = 'blog' AND i.object_id IN ($blog_ids))~;
}
$getBlogs->finish;

## WHICH REVIEWS DID I WRITE?
my $getReviews = $SBdb->prepare("SELECT id FROM reviews WHERE reviewer_id = '$myID'");
$getReviews->execute;
my $review_ids;
if ($getReviews->rows > 0){
while (my $id = $getReviews->fetchrow_array){
$review_ids .= "$id,";
};
chop($review_ids);
$my_stuff .= qq~ OR (i.object_type = 'review' AND i.object_id IN ($review_ids))~;
}
$getReviews->finish;

# WHICH COMMENTS DID I WRITE?
my $getComments = $SBdb->prepare("SELECT id FROM interactions WHERE action = 'comment' AND thread = id AND actor_id = '$myID'");
$getComments->execute;
my $comment_ids;
if ($getComments->rows > 0){
while (my $id = $getComments->fetchrow_array){
$comment_ids .= "$id,";
};
chop($comment_ids);
$my_stuff .= qq~ OR (i.action = 'comment' AND i.thread IN ($comment_ids))~;
}
$getComments->finish;

return $my_stuff;
}


sub getObjectTitle{
my ($object_type, $object_id) = @_;
my $title;
if ($object_type eq 'profile'){
my $sth = $SBdb->prepare("SELECT CONCAT_WS(' ', first_name, last_name) AS title FROM members WHERE id = '$object_id' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
$title = $sth->fetchrow_array;
}
}elsif ($object_type eq 'listing'){
my $sth = $SBdb->prepare("SELECT title, description FROM posts WHERE id = '$object_id' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
my $description;
($title, $description) = $sth->fetchrow_array;
$title = substr($description, 0, 50) . '...' if !$title;
}
}elsif ($object_type eq 'blog'){
my $sth = $SBdb->prepare("SELECT title FROM blog WHERE id = '$object_id' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
$title = $sth->fetchrow_array;
}
}
return $title;
}


sub getNotifications{
my $page = $FORM{page} || 0;
my $resultsPP = 20;
my $offset = $page * $resultsPP;
my $notifications;

my $getInteractions= $SBdb->prepare("SELECT i.id, i.action, i.actor_id, i.object_type, i.object_id, i.thread, i.status, i.timestamp, m.first_name, m.last_name FROM interactions AS i JOIN members AS m ON m.id = i.actor_id WHERE NOT EXISTS (SELECT id FROM unsubscribes WHERE object_type = i.object_type AND object_id = i.object_id AND actor_id = '$myID') AND i.action != 'view' AND i.actor_id != '$myID' AND ((i.object_type = 'profile' AND i.object_id = '$myID')" . &getMyStuff . ") ORDER BY i.id DESC LIMIT $resultsPP OFFSET $offset");

# GROUP BY i.action, i.object_type, i.object_id

$getInteractions->execute;
if ($getInteractions->rows > 0){
$notifications .= qq~<div class="clearfix"><a onclick="markAllNotificationsSeen();" href="javascript:void(0);" class="notification tiny clear right">MARK ALL SEEN</a></div>~ if $page eq 0;
while (my ($id, $action, $actor_id, $object_type, $object_id, $thread, $status, $timestamp, $actor_first_name, $actor_last_name) = $getInteractions->fetchrow_array){
my $xClass;
$xClass = 'bold' if !$status;
my $isReply;
$isReply = 1 if ($action eq 'comment' && $id ne $thread);
$notifications .= qq~<a onclick="openNotification(event, this,'$object_type', '$object_id', '$action', '$actor_id');" href="$baseURL/$object_type?id=$object_id" class="notification $xClass">$actor_first_name $actor_last_name ~;
if ($isReply){$notifications .= qq~replied to your comment on &apos;~ . &getObjectTitle($object_type ,$object_id) . qq~&apos; ~;
}else{
if ($action eq 'like'){$notifications .= qq~liked your ~;}
if ($action eq 'comment'){$notifications .= qq~commented on your ~;}
if ($action eq 'view'){$notifications .= qq~viewed your ~;}
if ($object_type eq 'profile'){$notifications .= qq~profile ~;}
if ($object_type eq 'listing'){$notifications .= qq~listing &apos;~ . &getObjectTitle('listing',$object_id) . qq~&apos; ~;}
if ($object_type eq 'review'){$notifications .= qq~review ~;}
if ($object_type eq 'blog'){$notifications .= qq~article &apos;~ . &getObjectTitle('blog',$object_id) . qq~&apos; ~;}
}
$notifications .= &getWhen($timestamp) . qq~.</a>~;
}
}
return $notifications;
}


sub descTitle{
my ($t, $d) = @_;
$t = substr($d, 0, 50) . '...' if !$t;
return $t;
}

sub descSummary{
my $d = shift;
$d =~ s/\n|\r/ /g;
$d =~ s/  / /g;
$d = substr($d, 0, 500) . '...' if length($d) > 496;
return $d
}

sub getCurrentLocation{
require $siteroot . '/get_location.pl';
my ($lat, $lon, $city, $region, $country, $country_iso) = &getIPLocation($ip);
return ($lat, $lon, $city, $region, $country, $country_iso);
}

sub getRegion{
my $id = shift;
my $sth = $SBdb->prepare("SELECT city, region, country FROM members WHERE id = '$id'");
$sth->execute;
if ($sth->rows >0){
my ($city, $region, $country) = $sth->fetchrow_array;
return &stringifyRegion($city, $region, $country);
}else{
return;
}
$sth->finish;
}

sub stringifyRegion{
my ($city, $region, $country) = @_;
my $string;
$string .= $city if $city;
$string .= ', ' if $city && ($region || $country);
$string .= $region if $region;
$string .= ', ' if $region && $country;
$string .= $country if $country;
return $string;
}



sub getWants{
### RETURN MEMBER NEEDS AS TAG STRING	
my $wants;
my $member_id = shift;
if (!$member_id){$member_id = $myID};

if ($member_id){
	# FIND RECENT SEARCHES
	my $getSearches = $SBdb->prepare("SELECT DISTINCT query FROM searches WHERE user_id = '$member_id' AND timestamp > (NOW() - INTERVAL 1 YEAR)");
	$getSearches->execute;
	if ($getSearches->rows > 0){
	while (my $q = $getSearches->fetchrow_array){$wants .= $q . ' ';}
	}
	$getSearches->finish;
	
	# GET INFO FROM REQUEST LISTINGS
	my $getRequests = $SBdb->prepare("SELECT title, description, tags FROM posts WHERE lister = '$member_id' AND type = 'request' AND status = 'live'");
	$getRequests->execute;
	if ($getRequests->rows > 0){
	while (my ($title, $description, $tags) = $getRequests->fetchrow_array){
	$description = substr($description, 0, 150) if length($description) > 149;
	$wants .= lc($title . ' ' . $description . ' ' . $tags . ' ');
	}
	}
	$getRequests->finish;
	
	# GET INFO FROM VIEWED OFFERS
	my $getViews = $SBdb->prepare("SELECT i.object_id, p.title, p.description, p.tags FROM interactions AS i LEFT JOIN posts AS p ON p.id = i.object_id WHERE i.action = 'view' AND i.object_type = 'listing' AND i.actor_id = '$member_id' AND p.lister != '$member_id' AND p.type = 'offer' GROUP BY i.object_id");
	$getViews->execute;
	if ($getViews->rows > 0){
	while (my (undef, $title, $description, $tags) = $getViews->fetchrow_array){
	$description = substr($description, 0, 150) if length($description) > 149;
	$wants .= lc($title . ' ' . $description . ' ' . $tags . ' ');
	}
	}
	$getViews->finish;
	
}
$wants = makeTagString($wants);
return $wants;
}



sub getHaves{
### RETURN MEMBER SKILLS AND INTERESTS AS TAG STRING	
my $haves;
my $member_id = shift;
if (!$member_id){$member_id = $myID};

if ($member_id){
	
	# GET INFO FROM OFFER LISTINGS
	my $getOffers = $SBdb->prepare("SELECT title, description, tags FROM posts WHERE lister = '$member_id' AND type = 'offer' AND status = 'live'");
	$getOffers->execute;
	if ($getOffers->rows > 0){
	while (my ($title, $description, $tags) = $getOffers->fetchrow_array){
	$description = substr($description, 0, 150) if length($description) > 149;
	$haves .= lc($title . ' ' . $description . ' ' . $tags . ' ' );
	}
	}
	$getOffers->finish;
	
	# GET INFO FROM VIEWED REQUESTS
	my $getViews = $SBdb->prepare("SELECT i.object_id, p.title, p.description, p.tags FROM interactions AS i LEFT JOIN posts AS p ON p.id = i.object_id WHERE i.action = 'view' AND i.object_type = 'listing' AND i.actor_id = '$member_id' AND p.lister != '$member_id' AND p.type = 'request' GROUP BY i.object_id");
	$getViews->execute;
	if ($getViews->rows > 0){
	while (my (undef, $title, $description, $tags) = $getViews->fetchrow_array){
	$description = substr($description, 0, 150) if length($description) > 149;
	$haves .= lc($title . ' ' . $description . ' ' . $tags . ' ');
	}
	}
	$getViews->finish;
	
	# GET USER PROFILE INFO
	my $getProfileInfo = $SBdb->prepare("SELECT tags, about_me FROM members WHERE id = '$member_id'");
	$getProfileInfo->execute;
	my ($tags, $about_me) = $getProfileInfo->fetchrow_array;
	$getProfileInfo->finish;
	$haves .= lc($tags . ' ' . $about_me);
	
}
$haves = makeTagString($haves);
return $haves;
}



sub getInterests{
### RETURN MEMBER INTERESTS AS TAG STRING	
my $interests;
my $member_id = shift;
if (!$member_id){$member_id = $myID};

if ($member_id){
	# FIND RECENT SEARCHES
	my $getSearches = $SBdb->prepare("SELECT DISTINCT query FROM searches WHERE user_id = '$member_id' AND timestamp > (NOW() - INTERVAL 1 YEAR)");
	$getSearches->execute;
	if ($getSearches->rows > 0){
	while (my $q = $getSearches->fetchrow_array){$interests .= $q . ' ';}
	}
	$getSearches->finish;
if ($LOGGED_IN){
	
	# GET INFO FROM REQUEST LISTINGS
	my $getRequests = $SBdb->prepare("SELECT title, description, tags FROM posts WHERE lister = '$member_id' AND type = 'request' AND status = 'live'");
	$getRequests->execute;
	if ($getRequests->rows > 0){
	my ($title, $description, $tags) = $getRequests->fetchrow_array;
	$getRequests->finish;
	$interests .= lc($title . ' ' . $description . ' ' . $tags);
	}
	
	# GET USER PROFILE INFO
	my $getProfileInfo = $SBdb->prepare("SELECT tags, about_me FROM members WHERE id = '$member_id'");
	$getProfileInfo->execute;
	my ($tags, $about_me) = $getProfileInfo->fetchrow_array;
	$getProfileInfo->finish;
	$interests .= lc($tags . ' ' . $about_me);
}
}
$interests = makeTagString($interests);
return $interests;
}


sub printDottedtags{
## FORMAT tagS FOR DISPLAY
my $tags = shift;
my @tagS = split(',', $tags);
$tags = '';
foreach my $tag (@tagS){
$tags .= qq~&middot; <a href="$baseURL/?search=$tag" alt="Search for $tag" rel="nofollow">$tag</a> ~;
}
return $tags;
}

sub printtags{
## FORMAT tagS FOR DISPLAY
my $tags = shift;
my @tagS = split(',', $tags);
@tagS = map {ucfirst} @tagS;
$tags = join(', ', @tagS);
return $tags;
}

sub commafy{
my $n = shift;
if ($n < 1000){
return $n;
}else{
$n = reverse $n;
$n =~ s/(\d\d\d)(?=\d)(?!\d*\.)/$1,/g;
return scalar reverse $n;
}
}

sub savetags{
## SAVE tagS TO DICTIONARY OR INCREMENT USAGE
my $tags = shift;
my @tagS = split(',', $tags);
my $writeTag = $SBdb->prepare("INSERT INTO dictionary (tag, used) VALUES (?,?) ON DUPLICATE KEY UPDATE used = used + 1");
foreach my $tag(@tagS){
$tag = &textFormat($tag);
$writeTag->execute("$tag","1");
}
$writeTag->finish;
}

sub errorCatcher{
my $error = shift;
&header('Error!','There was a problem with your request', undef, undef, 'page');
print qq~<p class="error">$error</p>~;
&footer;
exit;
}


sub getConvoID{
# CREATE UNIQUE CONVERSATION ID BETWEEK TWO MEMBERS
my ($from, $to) = @_;
use Digest::MD5 qw( md5_hex );
my ($l, $h);
if ($from > $to){
	$l = $to;
	$h = $from;
}else{
	$l = $from;
	$h = $to;
}
return md5_hex($l . '&' . $h);
}


sub sendMessage{
# SEND CHAT MESSAGE
my ($from, $to, $message, $message_type) = @_;

# SET CONVO_ID
my $convo_id = &getConvoID($from, $to);

$message =~ s/\r\n|\r|\n/<br\/>/g;

my $saveMessage = $SBdb->prepare("INSERT INTO messages (sender, recipient, convo_id, message, type, status, timestamp) VALUES (?,?,?,?,?,?,?)");
$saveMessage->execute("$from", "$to", "$convo_id", "$message", "$message_type", 'sent', "$now");
my $id = $SBdb->{ mysql_insertid };
$saveMessage->finish;
return $id;
}

sub printLocation{
my $string = join(', ', @_);
return $string;
}

sub syncHonorPay{
my ($FW_id, $email, $sync) = @_;
my $honors;
my $result;

## GET SHAREBAY INFO
my $getFW = $SBdb->prepare("SELECT first_name, last_name, region, country, image, tags, password, authcode, HP_id FROM members WHERE id = '$FW_id'");
$getFW->execute;
my ($first_name, $last_name, $region, $country, $imageRef, $tags, $password, $authcode, $HP_id) = $getFW->fetchrow_array;
$getFW->finish;

if ($HP_id && $sync){
## ALREADY CONNECTED. DO NOTHING
return;
}
elsif($HP_id && !$sync){
## DISCONNECT SHAREBAY FROM HONORPAY
my $FWupdate = $SBdb->do("UPDATE members SET HP_id = '' WHERE id = $FW_id");
my $HPupdate = $HPdb->do("UPDATE users SET FW_id = '', FW_auth = '' WHERE id = $HP_id");
return;
}
else{

$tags = &printtags($tags);

## CHECK FOR EXISTING ACCOUNT
my $checkHP = $HPdb->prepare("SELECT id, honors_received FROM users WHERE email LIKE '$email'");
$checkHP->execute;

if ($checkHP->rows > 0){
## HP ACCOUNT EXISTS, ADD ID, AUTHCODE AND PASSWORD IF BLANK
($HP_id, $honors) = $checkHP->fetchrow_array;
my $HPsth = $HPdb->do("UPDATE users SET FW_id = '$FW_id', FW_auth = '$authcode', type = 2, password = COALESCE(password,'$password') WHERE id = '$HP_id'");

## UPDATE SHAREBAY WITH HP_id
my $FWupdate = $SBdb->do("UPDATE members SET HP_id = '$HP_id' WHERE id = '$FW_id'");

$result = 'CONNECTED';

## SEND CONNECTED NOTIFICATION EMAIL
my $to = $email;
my $from = $admin;
my $subject = "Your HonorPay account was successfully connected!";
my $name = $first_name;
my $body = "As part of registering for Sharebay.org, we have now linked Sharebay.org to your existing HonorPay account. This means you will be able to use HonorPay directly from within the Sharebay site.\n\n(NB. If you've never logged in to HonorPay before, you can now log in using the same email and password as for Sharebay.org)";
my $call2act = 'Log in to HonorPay';
my $link = 'https://honorpay.org/login';
my $image = 'https://honorpay.org/i/honor.png';
&sendMail($to, $from, $subject, $name, $body, $call2act, $link, $image, undef);

# $HPsth->finish;
# $FWupdate->finish;
}else{

## NO HONORPAY ACCOUNT EXISTS, CREATE NEW
my $HPsth = $HPdb->prepare("INSERT INTO users (first_name, last_name, region, country, attributes, email, password, type, joined, FW_id, FW_auth) VALUES (?,?,?,?,?,?,?,?,?,?,?)");
$HPsth->execute("$first_name", "$last_name", "$region", "$country", "$tags", "$email", "$password", "2", "$now", "$FW_id", "$authcode");
$HP_id = $HPdb->{ mysql_insertid };
$HPsth->finish;

## UPDATE SHAREBAY WITH NEW HP_id
my $FWupdate = $SBdb->do("UPDATE members SET HP_id = '$HP_id' WHERE id = '$FW_id'");

# $FWupdate->finish;
$result = 'CREATED';

## SEND WELCOME EMAIL
my $to = $email;
my $from = $admin;
my $subject = "Welcome to HonorPay!";
my $name = $first_name;
my $body = "We have just created an HonorPay account for you.\n\nHonorPay is a free and open awards network created for the sole purpose of spreading appreciation and gratitude.\n\nYou can log in straight away to HonorPay using the same email and password as for Sharebay.org</p>";
my $call2act = 'Log in to HonorPay';
my $link = 'https://honorpay.org/login';
my $image = 'https://honorpay.org/i/honor.png';
&sendMail($to, $from, $subject, $name, $body, $call2act, $link, $image, undef);
}

## COPY AVATARS TO HONORPAY
# my $HProot = '/home/rtxmedia/public_html/honorpay.org';
# if (-e "$siteroot/user_pics/$imageRef\.jpg" && !-e "$HProot/user_pics/$HP_id\.jpg"){
# use File::Copy;
# my $imagename = $imageRef . '.jpg';
# my $thumbname = $imageRef . '_t.jpg';
# my $newimagename = $HP_id . '.jpg';
# my $newthumbname = $HP_id . '_t.jpg';
# copy("$siteroot/user_pics/$imagename","$HProot/user_pics/$newimagename");
# copy("$siteroot/user_pics/$thumbname","$HProot/user_pics/$newthumbname");
# }

$checkHP->finish;
return $result;
}
}


sub sendMail{
my ($to, $from, $subject, $name, $body, $call2act, $link, $image, $bcc) = @_;

my $nicefrom = $from;
if ($from eq $admin){$nicefrom = '"Sharebay Admin" <' . $admin . '>';}
elsif ($from eq $notify){$nicefrom = '"Sharebay" <' . $notify . '>';}
elsif ($from eq $newsletter){$nicefrom = '"Sharebay News" <' . $newsletter . '>';}
# CHECK RECIPIENT IS ACTIVATED
my ($checkMember, $mailFooter, $textMailFooter);
if ($to =~ m/^\d+$/){
# 'TO' IS ID
$checkMember = $SBdb->prepare("SELECT id, email, activated, authcode, badmail FROM members WHERE id = $to");
}else{
# NO IT'S PROBABLY AN EMAIL
$checkMember = $SBdb->prepare("SELECT id, email, activated, authcode, badmail FROM members WHERE email = '$to'");
}
$checkMember->execute;
my ($id, $email, $activated, $authcode, $badmail) = $checkMember->fetchrow_array;
$checkMember->finish;


if ($id && ($badmail eq 0 || $subject =~ m/unblock request/)){

my $text = $body;
# ADD PARAGRAPHS TO BODY
$body =~ s/\n\n/<\/p><p class="font-family: 'Open Sans', sans-serif;">/g; #CONVERT TWO NEWLINES TO PARA BREAK
$body =~ s/\n/<br\/>/g; #CONVERT REMAINING SINGLE NEWLINES TO BREAK
# WRAP PARAGRAPHS TO BODY
$body = qq~<p class="font-family: 'Open Sans', sans-serif;">~ . $body . qq~</p>~;
$checkMember->finish;
# STANDARD FOOTER
if ($activated){
$mailFooter = qq~You have received this email as a member of <a href="$baseURL/profile?id=$id">Sharebay.org</a>. If you prefer not to receive emails like this, you can unsubscribe <a href="$baseURL/profile?a=unsubscribe_mailme&token=$authcode">here</a>.~;
}else{
$mailFooter = qq~You have received this email because you registered to be a member of <a href="$baseURL">Sharebay.org</a>. If you did not register or did not authorise this, please report this issue to <a href="hello\@sharebay.org">hello\@sharebay.org</a>.~;
}
$textMailFooter = $mailFooter . "\n$baseURL/edit";
$textMailFooter =~ s/<[^>]*>//g;

my $html = qq~<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>~ . $subject . qq~</title>
</head>
<body style="width: 100% !important;min-width: 100%;-webkit-text-size-adjust: 100%;-ms-text-size-adjust: 100% !important;margin: 0;padding: 0;font-family: 'Open Sans', sans-serif;">
<table border="0" cellpadding="0" cellspacing="0" width="100%" style="width:100%;max-width:600px;">
<tr>
<td align="left" width="100%" valign="middle" style="text-align:left;background-color: #fff; width:100%;vertical-align:middle;padding:10px;">
<a href="$baseURL/" title="Sharebay.org">
<img src="$baseURL/i/main-logo.png" width="148" height="36" style="border:none;width:148px;height:36px;" alt="Sharebay Logo"/>
</a>
</td></tr>~;
if ($image){
$html .= qq~
<tr><td align="center" valign="top" width ="100%" style="width:100%;padding:10px;"><a href="~ . $link . qq~" title="~ . $call2act . qq~"><img src="~ . $image . qq~" width="100%" style="width:100%;height:auto;border:none;"/></a>
</td></tr>~;}

$html .= qq~<tr style="display:none;">
<td align="left" style="text-align:left;padding:0 10px;">
<h2 style="font-size: 16px;font-weight:normal;color: #7a9108;">~ . $subject . qq~</h2>
</td></tr>
<tr><td align="left" valign="top" width="100%" style="width:100%;vertical-align:top;padding:0 10px;">~;

$html .= $body . qq~</td>
</tr>
<tr>
<td align="center" style="text-align:center;padding-bottom:30px;">
<div style="display: inline-block;width: auto;margin: 6px;border: none;padding: 8px 16px;text-align: center;font-size: 17px;font-weight:normal;color: #fff;border-radius: 6px;cursor: pointer;text-transform:uppercase;-moz-box-shadow: inset 0 0 12px rgba(0,0,0,0.1);-webkit-box-shadow: inset 0 0 12px rgba(0,0,0,0.1);box-shadow:         inset 0 0 12px rgba(0,0,0,0.1);text-decoration: none !important;background: #7a9108;">
<a style="color:#ffffff;font-size: 17px;font-weight:normal;text-decoration:none;"  href="~ . $link . qq~" target="_blank">~ . $call2act . qq~</a></div>
</td>
</tr>
<tr>
<td align="left" width="100%" style="padding: 12px;text-align:left;width:100%;font-size:85%;background-color: #eee;color: #333;">
$mailFooter
</td>
</tr>
</table>
</body></html>~;

my $fulltext;
$fulltext = qq~### ~ . $subject . qq~ ###\n\n~;
$fulltext .= qq~Hi ~ . $name . qq~,\n\n~ if $name;
$fulltext .= $text . qq~\n\n~;
$fulltext .= $call2act . qq~\n~;
$fulltext .= $link;
$fulltext .= qq~\n\n=====================================\n\n~ . $textMailFooter;

## ENCODE SUBJECT
use MIME::Base64;
my $subject_enc = encode_base64($subject);
$subject_enc =~ s/^\s+|\s+$//g;
$subject_enc = '=?UTF-8?B?' . $subject_enc . '?=';

if ($from eq 'hello@sharebay.org'){
## SEND IMMEDIATELY IF IT'S FROM MAIN EMAIL

my $host = 'othello.ldn.kgix.net';
my $user = $from;
use MIME::Lite;
use Net::SMTP;
MIME::Lite->send('smtp', $host, AuthUser=>$user, AuthPass=>$emailPW);
my $msg = MIME::Lite->new(
        From    => $nicefrom,
        To      => $email,
        Bcc     => $bcc,
        Subject => $subject_enc,
        Type    => 'multipart/alternative'
    );
    $msg->attach(
        Type     => 'text/plain; charset=UTF-8',
		Encoding => 'quoted-printable',
        Data     => $fulltext
    );
    $msg->attach(
        Type     => 'text/html',
		Encoding => 'quoted-printable',
        Data     => $html
    );    
    $msg->send;
}else{
	
# OR SEND IT TO EMAIL QUEUE
my $account = $from;
$account =~ s/^(.*)@.*$/$1/; # STRIP ACCOUNT NAME FROM EMAIL ADDRESS

## CONNECT TO SHAREBAY MAILER DATABASE
my $EMdb = DBI->connect("DBI:mysql:database=sbmail_emails;host=localhost;mysql_local_infile=1", 'sbmail_mailer', '}+{_P0o9i8',{RaiseError => 1, PrintError => 1});

my $addEmail = $EMdb->prepare("INSERT INTO email_queue (account, to_email, bcc, subject, html, text) VALUES(?,?,?,?,?,?)");
$addEmail->execute("$account", "$email", "$bcc", "$subject_enc", "$html", "$fulltext");
$addEmail->finish;
$EMdb->disconnect;
}
}
}


sub sendPlainMail{
my ($to, $from, $reply, $subject, $body) = @_;

## ENCODE SUBJECT
use MIME::Base64;
my $subject_enc = encode_base64($subject);
$subject_enc =~ s/^\s+|\s+$//g;
$subject_enc = '=?UTF-8?B?' . $subject_enc . '?=';

## OK LET'S SEND IT!
my $host = 'othello.ldn.kgix.net';
my $user = 'notify@sharebay.org';
use MIME::Lite;
use Net::SMTP;
MIME::Lite->send('smtp', $host, AuthUser=>$user, AuthPass=>$emailPW);
my $msg = MIME::Lite->new(
        From    => $from,
        'Reply-To' => $reply,
        To      => $to,
        Subject => $subject_enc,
        Type     => 'text/plain; charset=UTF-8',
		Encoding => 'quoted-printable',
        Data     => $body
    );
    $msg->send;
}


sub getMessages{
my $convo_id = $FORM{convo_id} || shift;
my $page = $FORM{page} || 0;
my $resultsPP = 25;
my $offset = $page * $resultsPP;
my $response;

my $sth = $SBdb->prepare("SELECT * FROM (SELECT id, sender, recipient, convo_id, message, type, timestamp FROM messages WHERE convo_id = '$convo_id' AND (sender = $myID OR recipient = $myID) ORDER by id DESC LIMIT $resultsPP OFFSET $offset) AS tmp ORDER BY id");
$sth->execute;

if ($sth->rows > 0){
# SHOW CHAT CONVERSATION
while (my ($id, $sender, $recipient, $convo_id, $message, $type, $timestamp) = $sth->fetchrow_array){
my $class;
if ($sender eq $myID){$class = 'chat-right notranslate'}else{$class = 'chat-left';}
if ($type eq 'alert'){$class = 'chat-alert';}
$response .= qq~<div class="$class">$message</div>~;
}
}
$sth->finish;
return $response;
}


sub showLogin{
my $go = shift;
print qq~
<div class="box300"><h2>Log in</h2>
<form id="logIn" class="full-width">
<input type="hidden" name="a" value="dologin"/>
<input type="hidden" name="go" value="$go"/>
<label for="email">Email address:</label>
<input id="email" class="forminput" type="text" name="email" placeholder="Email address"/>
<label for="password">Password:</label>
<input id="password" class="forminput" type="password" name="password" placeholder="Password"/>
<p class="center clear"><button class="green-button no-margin" id="doLogin">Log in</button></p>
<span class="inlineerror" id="loginError">Sorry, email and password do not match!</span>
<span class="inlineerror" id="unactivatedError">This account has not yet been activated. Please activate your account using the link in your confirmation email. <a href="javascript:void(0);" id="resendCode">Resend activation code?</a></span>
<span class="inlineerror" id="accountLockedError">This account has been locked by an admin. Please <a href="$baseURL/contact">contact support</a> to unlock your account.</span></form>
<p class="smaller center"><a href="$baseURL/join">Create an account</a> | 
<a class="forgot-password" href="javascript:void(0);">Forgot password?</a></p>
</div>~;
}


sub hashPW{
my $pw = shift;
use Digest::MD5 qw(md5_hex);
return md5_hex($pw . $salt);
}


sub showForgot{
print qq~
<div class="box300"><h2>Reset Password</h2>
<p>Enter your email address and we'll send you a link to reset your password.</p>
<input id="reset_email" class="forminput" type="text" name="reset_email" placeholder="Your email..."/>
<button class="green-button no-margin" id="pw-reset">Reset Password</button><br/>
<span class="inlineerror" id="resetError">! Sorry, this email doesn't exist on our system</span><br/>
<span class="smaller"><a href="$baseURL/join">Create an account</a> |  <a class="showLogin" href="javascript:void(0);">Log in</a>
</div>~;
}

sub bounceNonLoggedIn{
if (!$LOGGED_IN){
my $message = shift;
if (!$message){$message = 'You need to log in to view this page.'};
&header($message, $message, undef, undef, 'page');
print qq~<p class="error">$message</p>~;
&showLogin;
&footer;
exit;
}
}


sub showOffer{
my $listingLatLon = 'lat: ' . $myLat . ', lng: ' . $myLon;
my $qty = &qtySelect;
print qq~
<script>
var myListingLatLng = {$listingLatLon};
</script>
<form class="full-width" id="post_listing">
<input type="hidden" name="a" value="postlisting"/>
<input type="hidden" name="good2go" value=""/>
<input type="hidden" name="image" value=""/>
<input type="hidden" name="type" value="offer"/>
<input type="hidden" name="listingLat" id="listingLat" value="$myLat"/>
<input type="hidden" name="listingLon" id="listingLon" value="$myLon"/>
<input type="hidden" name="category" value=""/>
<div id="listingPicContainer"></div>
<input type="file" id="listingPic"/>
<textarea name="text" id="post_text" class="full-width" placeholder="What are you offering?" rows="2"></textarea>
<div id="post_text_E" class="inlineerror">! Please enter a short description</div>
	
<div id="matched_categories" class="clearfix"></div>
<div id="selected_category">In: <span></span>&nbsp;<a href="javascript:void(0);" onclick="reselectCategory();" class="smaller">Change</a></div>
<div id="category_select_E" class="inlineerror">! You must select a category</div>

<p class="center"><input type="checkbox" id="is_physical" name="physical" value="1"/><label for="is_physical">&nbsp;&nbsp;This is a physical item</label></p>
<table id="physical_options">
<tr>
<td>Quantity:</td><td><select name="quantity" id="post_quantity">$qty</select>&nbsp;offered</td>
</tr>
<tr>
<td>Terms:</td><td><input type="radio" name="terms" id="free" value="free" checked>&nbsp;<label for="free">Free to keep</label>&nbsp; <input type="radio" name="terms" id="loan_only" value="loan">&nbsp;<label for="loan_only">Loan only</label></td>
</tr>
<tr>
<td>Delivery:</td><td><input type="checkbox" id="will_send" name="send_ok" value="1" checked/>&nbsp;&nbsp;<label for="will_send">Will send if recipient pays delivery</label></td>
</tr>
<tr>
<td>Location:</td><td><span id="location_info">My saved location</span> <a href="javascript:void(0);" onclick="openMap();" class="smaller">Change</a></td></tr>
</table>
<div id="listingMap" class="hidden"></div>
<p class="center"><input type="submit" name="POST" value="POST" class="green-button"/></p>
<div id="post_E" class="inlineerror">!! PLEASE CORRECT ERRORS ABOVE !!</div>
<script>
initialize();
</script>
</form>
~;
}


sub showRequest{
my $listingLatLon = 'lat: ' . $myLat . ', lng: ' . $myLon;
my $qty = &qtySelect;
print qq~
<script>
var myListingLatLng = {$listingLatLon};
</script>
<form class="full-width" id="post_listing">
<input type="hidden" name="a" value="postlisting"/>
<input type="hidden" name="good2go" value=""/>
<input type="hidden" name="image" value=""/>
<input type="hidden" name="type" value="request"/>
<input type="hidden" name="listingLat" id="listingLat" value="$myLat"/>
<input type="hidden" name="listingLon" id="listingLon" value="$myLon"/>
<input type="hidden" name="category" value=""/>
<div id="listingPicContainer"></div>
<input type="file" id="listingPic"/>
<textarea name="text" id="post_text" class="full-width" placeholder="What do you need?" rows="2"></textarea>
<div id="post_text_E" class="inlineerror">! Please enter a short description</div>
	
<div id="matched_categories" class="clearfix"></div>
<div id="selected_category">In: <span></span>&nbsp;<a href="javascript:void(0);" onclick="reselectCategory();" class="smaller">Change</a></div>
<div id="category_select_E" class="inlineerror">! You must select a category</div>

<p class="center"><input type="checkbox" id="is_physical" name="physical" value="1"/><label for="is_physical">&nbsp;&nbsp;This is a physical item</label></p>
<table id="physical_options">
<tr>
<td>Quantity:</td><td><select name="quantity" id="post_quantity">$qty</select>&nbsp;needed</td>
</tr>
<tr>
<td>Terms:</td><td><input type="radio" name="terms" id="free" value="free" checked>&nbsp;<label for="free">Free to keep</label>&nbsp; <input type="radio" name="terms" id="loan_only" value="loan">&nbsp;<label for="loan_only">Borrow</label></td>
</tr>
<tr>
<td>Delivery:</td><td><input type="checkbox" id="will_send" name="send_ok" value="1" checked/>&nbsp;&nbsp;<label for="will_send">Will pay delivery if giver can send</label></td>
</tr>
<tr>
<td>Location:</td><td><span id="location_info">My saved location</span> <a href="javascript:void(0);" onclick="openMap();" class="smaller">Change</a></td></tr>
</table>
<div id="listingMap" class="hidden"></div>
<p class="center"><input type="submit" name="POST" value="POST" class="green-button"/></p>
<div id="post_E" class="inlineerror">!! PLEASE CORRECT ERRORS ABOVE !!</div>
<script>
initialize();
</script>
</form>
~;
}


sub addActivity{
my ($actor_id, $object_type, $object_id, $image, $text, $link, $location, $data, $timestamp) = @_;
if ($object_type && $object_id){
my $del = $SBdb->do("DELETE FROM activity WHERE object_type = '$object_type' AND object_id = '$object_id'")
}
my $sth = $SBdb->prepare("INSERT INTO activity (actor_id, object_type, object_id, image, text, link, location, data, timestamp) VALUES (?,?,?,?,?,?,?,?,?)");
$sth->execute("$actor_id", "$object_type", "$object_id", "$image", "$text", "$link", "$location", "$data", "$timestamp");
}


sub deleteActivity{
my ($object_type, $object_id) = @_;
if ($object_type && $object_id){
$SBdb->do("DELETE FROM activity WHERE object_type = '$object_type' AND object_id = '$object_id'");
}
}


sub showStars{
my $id = shift;
my $sth = $SBdb->prepare("SELECT stars FROM reviews WHERE target_id = '$id'");
$sth->execute;		
my $total = 0;
my $no_reviews = $sth->rows;
while (my $star = $sth->fetchrow_array){$total += $star;}
$sth->finish;
my $rating = 0;
my $stars;
$rating = $total / $no_reviews if $no_reviews > 0;
if ($rating > int($rating)){$rating = (int($rating) + 0.5)};
if ($no_reviews > 0){
$stars .= qq~<a href="$baseURL/reviews?a=read&id=$id" title="$rating stars based on $no_reviews reviews">~;
$stars .= &renderStars($rating);
$stars .= qq~ <span class="smaller grey">($no_reviews)</span></a>~}
return $stars;
}


sub renderStars{
my $rating = shift;
my $s;
if ($rating > 0){$s .= qq~<img src="$baseURL/i/gold-star.svg" class="star" alt="$rating stars"/>~}else{$s .= qq~<img src="$baseURL/i/grey-star.svg" class="star" alt="$rating stars"/>~}
if ($rating > 1 && $rating < 2){$s .= qq~<img src="$baseURL/i/half-star.svg" class="star" alt="$rating stars"/>~}elsif($rating >= 2){$s .= qq~<img src="$baseURL/i/gold-star.svg" class="star" alt="$rating stars"/>~}else{$s .= qq~<img src="$baseURL/i/grey-star.svg" class="star" alt="$rating stars"/>~}
if ($rating > 2 && $rating < 3){$s .= qq~<img src="$baseURL/i/half-star.svg" class="star" alt="$rating stars"/>~}elsif($rating >= 3){$s .= qq~<img src="$baseURL/i/gold-star.svg" class="star" alt="$rating stars"/>~}else{$s .= qq~<img src="$baseURL/i/grey-star.svg" class="star" alt="$rating stars"/>~}
if ($rating > 3 && $rating < 4){$s .= qq~<img src="$baseURL/i/half-star.svg" class="star" alt="$rating stars"/>~}elsif($rating >= 4){$s .= qq~<img src="$baseURL/i/gold-star.svg" class="star" alt="$rating stars"/>~}else{$s .= qq~<img src="$baseURL/i/grey-star.svg" class="star" alt="$rating stars"/>~}
if ($rating > 4 && $rating < 5){$s .= qq~<img src="$baseURL/i/half-star.svg" class="star" alt="$rating stars"/>~}elsif($rating >= 5){$s .= qq~<img src="$baseURL/i/gold-star.svg" class="star" alt="$rating stars"/>~}else{$s .= qq~<img src="$baseURL/i/grey-star.svg" class="star" alt="$rating stars"/>~}
return $s;
}


sub textFormat{
# TRIM TRAILING SPACES AND MAKE LOWER CASE (FOR EMAIL)
my $s = shift;
$s =~ s/^\s+|\s+$//g;
$s = lc($s);
return $s;
}

sub conformTags{
	my $tags = shift;
	$tags = lc($tags); # LOWER CASE
	$tags =~ s/,/Q1Q/g; # REPLACE COMMAS WITH PLACEHOLDER FIRST
	$tags =~ s/[[:punct:]]//g; # REMOVE TAGS PUNCTUATION
	$tags =~ s/Q1Q/,/g; # PUT COMMAS BACK
	return $tags;
}

sub makeTagString{
my $string = shift;
$string =~ s/((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w\-_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)//g; # REMOVE URLS
$string =~ s/,/ /g; # REPLACE COMMAS WITH SPACES FIRST
$string =~ s/-/JqJ/g; # REPLACE DASHES WITH PLACHOLDER FIRST
$string =~ s/[[:punct:]]//g; # REMOVE PUNCTUATION
$string =~ s/JqJ/-/g; # REPLACE DASHES WITH PLACHOLDER
$string =~ s/\b[a-z]{1,3}\b//gi; #REMOVE WORDS UNDER 3 CHARACTERS
$string =~ s/  / /g; # REMOVE ANY DOUBLE SPACES
my @tagS = split(' ', $string);
my @unique = &uniq(@tagS);
my @clean = &removeStopWords(@unique);
my $newString = join(' ', @clean);
return $newString;
}


sub assessRisk{
my ($object_type, $object_id) = @_;
my $noImagePenalty = 1;
my $noInfoPenalty = 2;
my $noLocationPenalty = 2;
my $badwordPenalty = 5;
my $reportPenalty = 9;
my $count = 0;
my @badwords = qw(bitcoin btc crypto ethereum invest porn singles sale earn earnings price sell);

## LISTINGS
if ($object_type eq 'listing'){
my $getListing = $SBdb->prepare("SELECT id, title, description, tags, image, lon FROM posts WHERE id = '$object_id' LIMIT 1");
my $setListingRisk = $SBdb->prepare("UPDATE posts SET risk = ? WHERE id = ? AND risk != -1 LIMIT 1");
$getListing->execute;
while (my ($id, $title, $description, $tags, $image, $lon) = $getListing->fetchrow_array){
my $risk = 0;
$risk += $noInfoPenalty if !$description;
$risk += $noImagePenalty if !$image;
$risk += $noLocationPenalty if !$lon || $lon eq 0;
$risk += $reportPenalty * int($SBdb->do("SELECT id FROM spam_reports WHERE object_type = 'listing' AND object_id = '$id'")) || 0;
my @words = split(' ', $title . ' ' . $description . ' ' . $tags);
chomp @words;
my $badwordCount = 0;
foreach my $word (@words) {
$word =~ s/[[:punct:]]//g;
$badwordCount++ if grep {$_ =~ m/^$word$/i} @badwords;
}
$risk += $badwordPenalty * $badwordCount if $badwordCount > 0;
$setListingRisk->execute("$risk", "$id");
$count++;
}
$getListing->finish;
}

## PROFILES
if ($object_type eq 'profile'){
my $getMember = $SBdb->prepare("SELECT id, about_me, image, tags, lon FROM members WHERE id = '$object_id' LIMIT 1");
my $setProfileRisk = $SBdb->prepare("UPDATE members SET risk = ? WHERE id = ? AND risk != -1 LIMIT 1");
$getMember->execute;
while (my ($id, $about_me, $image, $tags, $lon) = $getMember->fetchrow_array){
my $risk = 0;
$risk += $noInfoPenalty if !$about_me;
$risk += $noImagePenalty if !$image;
$risk += $noLocationPenalty if !$lon || $lon eq 0;
$risk += $reportPenalty * int($SBdb->do("SELECT id FROM spam_reports WHERE object_type = 'profile' AND object_id = '$id'")) || 0;
my @words = split(' ', $about_me . ' ' . $tags);
chomp @words;
my $badwordCount = 0;
foreach my $word (@words) {
$word =~ s/[[:punct:]]//g;
$badwordCount++ if grep {$_ =~ m/^$word$/i} @badwords;
}
$risk += $badwordPenalty * $badwordCount if $badwordCount > 0;
$setProfileRisk->execute("$risk", "$id");
$count++;
}
$getMember->finish;
}
return $count;
}


sub uniq {
my %seen;
grep !$seen{$_}++, @_;
}

sub getBlockedIds{
	my $id = shift || $myID;
	my @blocked;
	my $result;
	my $sth = $SBdb->prepare("SELECT blocker_id, blocked_id FROM member_blocks WHERE blocker_id = '$id' OR blocked_id = '$id'");
	$sth->execute;
	if ($sth->rows > 0){
		while(my @array = $sth->fetchrow_array){
		push (@blocked, @array);
		}
		@blocked = &uniq(@blocked);
		@blocked = grep {!/^$id$/} @blocked;
		$result = join(',', @blocked);
	}
	$sth->finish;
	return $result;
}

sub getGravatar{
my ($id, $email) = @_;
use LWP::UserAgent;
use Digest::MD5 qw( md5_hex );
my $email_hash = md5_hex( &textFormat($email) );
my $url = 'https://www.gravatar.com/avatar/' . $email_hash . '?s=300&d=identicon';
my $ua = LWP::UserAgent->new;
$ua->default_header('Accept-Encoding' => scalar HTTP::Message::decodable());
$ua->default_header('Accept-Language' => "en, es");
$ua->timeout(60);
my $req = $ua->get($url);
if ($req->is_success){
my $gravatar = $req->decoded_content;
my $imageRef = $id . '_' . $now;
open (my $FH, ">", "$siteroot/user_pics/" . $imageRef . ".jpg");
print $FH $gravatar;
close $FH;
sleep 5;
if (-e "$siteroot/user_pics/$imageRef\.jpg"){

use Image::Resize;
my $img = Image::Resize->new("$siteroot/user_pics/$imageRef\.jpg");
my $thumb = $img->resize(50, 50);
open (my $TH, ">", "$siteroot/user_pics/$imageRef\_t.jpg");
print $TH $thumb->jpeg();
close $TH;

# UPDATE DATABASE
my $update = $SBdb->do("UPDATE members SET image = '$imageRef' WHERE id = '$id' LIMIT 1");
}
return $imageRef;
}else{
return "q"; # LAST RESORT DEFAULT IMAGE
}
}

sub getNames{
my $id = shift;
my $sth = $SBdb->prepare("SELECT first_name, last_name FROM members WHERE activated = 1 AND id = '$id' LIMIT 1");
$sth->execute;
my ($first_name, $last_name);
if ($sth->rows > 0){
($first_name, $last_name) = $sth->fetchrow_array;
}else{
($first_name, $last_name) = ('[Deleted User]', '');
}
$sth->finish;
return ($first_name, $last_name);
}

sub getFullName{
my $id = shift;
my ($first_name, $last_name) = getNames($id);
return "$first_name $last_name";
}

sub getNameRecord{
my $id = shift;

# GET NAME, IMAGE, BADGE, GIFTS, RATING

my $sth = $SBdb->prepare("SELECT first_name, last_name, image, gifted, trust_score, badge_level, star_rating, is_moderator, is_author, is_admin, last_active FROM members WHERE id = '$id' LIMIT 1");

$sth->execute;

if ($sth->rows > 0){
my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = $sth->fetchrow_array;

return($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active);
}else{
return('UNKNOWN', 'USER', 'q', 0, 0, 0, undef, 0, 0, 0, 0, undef);
}
$sth->finish;
}

sub getBadge{
my ($name, $level) = @_;
my $badge;
if ($level eq 1){$badge = '';}
elsif ($level eq 2){$badge = qq~&nbsp;<img src="$baseURL/i/shield-silver.png" class="badge" alt="Level $level member" title="$name is a Trusted Member"/>~;}
elsif ($level eq 3){$badge = qq~&nbsp;<img src="$baseURL/i/shield-gold.png" class="badge" alt="Level $level member" title="$name is a Top Trusted Member"/>~;}
return $badge;
}

sub printBadge{
print getBadge(@_);
}


sub getUserCard{
my $user = shift;
my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($user);
if (!$image){$image = 'q';}

print qq~
<div class="user-card clearfix" onclick="window.location.href='$baseURL/profile?id=$user'">~;
if ($last_active > ($now - 1800)){print qq~<div class="user-active" title="Active recently"></div>~;}
# if ($myAdmin || $myModerator){print qq~ <div class="is-admin" title="$first_name is a site admin">a</div>~;}
print qq~<img src="$baseURL/user_pics/$image\_t.jpg" class="user-image" alt="$first_name $last_name"/><div class="user-name flex-center"><div><span class="notranslate">$first_name $last_name</span>~;
if ($gifted){print qq~ <span class="smaller" title="$first_name has given $gifted times">($gifted)</span>~;}
&printBadge($first_name, $badge_level);
if ($myModerator && !$myAdmin){print qq~ <span class="brand" title="$first_name is a moderator"><i class="fa-solid fa-scale-balanced"></i></span>~;}
if ($myAuthor){print qq~ <span class="brand" title="$first_name is a site author"><i class="fa-solid fa-pen-nib"></i></span>~;}
if ($myAdmin){print qq~ <span class="brand" title="$first_name is a site admin"><i class="fas fa-tools"></i></span>~;}
if ($star_rating){
print qq~<br/>~;
if ($star_rating){
my $stars = &renderStars($star_rating);
print qq~<span title="$first_name has a $star_rating star rating">$stars</span>~;
}
}
print qq~</div></div></div>~;
}


sub getTrustScore{
	my $id = shift;
	my $sth = $SBdb->prepare("SELECT trust_score FROM members WHERE id = '$id' LIMIT 1");
	$sth->execute;
	return($sth->fetchrow_array);
	$sth->finish;
}


sub getStripes{
my $trust_score = shift;

my $sth = $SBdb->prepare("SELECT stripe_1, stripe_2, stripe_3 FROM site_averages WHERE id = 1");
$sth->execute;
my ($stripe_1, $stripe_2, $stripe_3) = $sth->fetchrow_array;
$sth->finish;
	
my $stripe_image;
my $stripe_legend;

if ($trust_score >= $stripe_1 && $trust_score < $stripe_2){
	$stripe_image = 'stripe_1.svg';
	$stripe_legend = qq~Contributing member ($trust_score)~;
	}
elsif ($trust_score >= $stripe_2 && $trust_score < $stripe_3){
	$stripe_image = 'shield-silver.png';	
	$stripe_legend = qq~Active contributing member ($trust_score)~;
	}
elsif ($trust_score >= $stripe_3){
	$stripe_image = 'shield-gold.png';
	$stripe_legend = qq~Prolific contributing member ($trust_score)~;
	}
	
return ($stripe_image, $stripe_legend);
}


sub getStripeLevel{
my $trust_score = shift;

my $sth = $SBdb->prepare("SELECT stripe_1, stripe_2, stripe_3 FROM site_averages WHERE id = 1");
$sth->execute;
my ($stripe_1, $stripe_2, $stripe_3) = $sth->fetchrow_array;
$sth->finish;
	
my $stripes = 0;

if ($trust_score >= $stripe_1 && $trust_score < $stripe_2){
	$stripes = 1;
	}
elsif ($trust_score >= $stripe_2 && $trust_score < $stripe_3){
	$stripes = 2;
	}
elsif ($trust_score >= $stripe_3){
	$stripes = 3;
	}

return $stripes;
}

sub saveView{
	if ($myID && !$myAdmin){
	my ($object_type, $object_id) = @_;
	my $sth = $SBdb->prepare("INSERT INTO interactions (action, actor_id, object_type, object_id, timestamp) VALUES (?,?,?,?,?)");
	$sth->execute('view', "$myID", "$object_type", "$object_id", "$now");
	$sth->finish;
	}
}


sub getAverages{
my $sth = $SBdb->prepare("SELECT stripe_1, stripe_2, stripe_3, offers_max, gave_max, got_max, trust_max FROM site_averages WHERE id = 1");
$sth->execute;
return($sth->fetchrow_array);
$sth->finish;
}


sub getFilters{
my $selected = shift;
my $type;
if ($selected =~ /.*_.*/){
($type, $selected) = split('_' , $selected);
}

my $cat_select;
$cat_select .= '<option value="listings"';
$cat_select .= ' SELECTED' if ($selected eq 'listings');
$cat_select .= '>All listings</option><option value="offers"';
$cat_select .= ' SELECTED' if ($selected eq 'offers');
$cat_select .= '>Offers only</option><option value="requests"';
$cat_select .= ' SELECTED' if ($selected eq 'requests');
$cat_select .= '>Requests only</option>';
if ($LOGGED_IN){
$cat_select .= '<option value="members"';
$cat_select .= ' SELECTED' if ($selected eq 'members');
$cat_select .= '>Members</option>';
}
if ($type eq 'member'){
$cat_select .= '<option value="member_' . $selected . '" SELECTED class="notranslate">' . &getFullName($selected) . '</option>';
}
# if ($myAdmin || $myModerator){
# $cat_select .= '<option value="spam_listings"';
# $cat_select .= ' SELECTED' if ($selected eq 'spam_listings');
# $cat_select .= '>Spam Listings (admin)</option>';
# $cat_select .= '<option value="spam_members"';
# $cat_select .= ' SELECTED' if ($selected eq 'spam_members');
# $cat_select .= '>Spam Members (admin)</option>';
# }
my $sth = $SBdb->prepare("SELECT id, category FROM categories ORDER by category ASC");
$sth->execute;

while(my ($id, $cat) = $sth->fetchrow_array){
$cat_select .= '<option value="cat_' . $id . '"';
if ($id eq $selected && $type eq 'cat'){$cat_select .= ' SELECTED';}
$cat_select .= '>' . $cat . '</option>';
}
$sth->finish;
return $cat_select;
}


sub getCategories{
my $selected = shift;

my $cat_select;

my $sth = $SBdb->prepare("SELECT id, category FROM categories ORDER by category ASC");
$sth->execute;

while(my ($id, $cat) = $sth->fetchrow_array){
$cat_select .= qq~<option value="$id"~;
if ($id eq $selected ){$cat_select .= ' SELECTED';}
$cat_select .= qq~>$cat</option>~;
}
$sth->finish;
return $cat_select;
}


sub getCategory{
my $id = shift;
my $sth = $SBdb->prepare("SELECT category, transactable FROM categories WHERE id = '$id' LIMIT 1");
$sth->execute;
my ($category, $transactable);
if ($sth->rows > 0){
($category, $transactable) = $sth->fetchrow_array;
}
$sth->finish;
return ($category, $transactable);
}

sub qtySelect{
	my $input = shift;
	my ($string, $select);
	for (my $i=1;$i<100;$i++){
		if ($i eq $input){$select = ' selected';}else{$select = '';}
		$string .= '<option value="' . $i . '"' . $select . '>' . $i . '</option>';
	}
	return $string;	
}

sub getHonors{
my $HP_id = shift;
my $honors;
if ($HP_id){
my $getHonors = $HPdb->prepare("SELECT honors_received FROM users WHERE id = $HP_id");
$getHonors->execute;
$honors = $getHonors->fetchrow_array if ($getHonors->rows > 0);
$getHonors->finish;
}
return $honors;
}



sub getHearts{
my ($object, $id) = @_;
my $sth = $SBdb->prepare("SELECT actor_id FROM interactions WHERE action = 'like' AND object_type = '$object' AND object_id = '$id'");
$sth->execute;
my $heart = 'fa-heart-o';
my $num_color;
my $action = 'like';
my $heart_num = 'Like';
if ($sth->rows > 0){
$heart_num = $sth->rows;
if ($heart_num > 0){
	$heart .= ' pink';
	$num_color = 'pink';
}
if ($LOGGED_IN){
while(my $id = $sth->fetchrow_array){
if ($id eq $myID){
$heart = 'fa-heart pink';
$action = 'unlike';
last;
}
}
}
}
$sth->finish;

return qq~<span class="social social-box" id="like_$object\_$id"><a href="javascript:void(0);" onclick="setHeart('$action','$object',$id);"><i class="fa $heart heart"></i>&nbsp;<span class="smaller $num_color">~. &commafy($heart_num) . qq~</span></a></span>~;
}

sub showHearts{
print &getHearts(@_);
}


sub getComments{
my ($object_type, $object_id) = @_;

my $getComments = $SBdb->prepare("SELECT c.id, c.actor_id, c.thread, c.comment, c.timestamp, m.first_name, m.last_name, m.image FROM interactions AS c JOIN members AS m ON m.id = c.actor_id WHERE action = 'comment' AND c.object_type = '$object_type' AND c.object_id = $object_id ORDER BY c.thread, c.id");
$getComments->execute;
my $num_comments = int($getComments->rows);
my $comment_legend = 'No comments yet';
if ($num_comments == 1){$comment_legend = '1 comment';}
if ($num_comments > 1){$comment_legend = $num_comments . ' comments';}

my $comments = qq~<div class="social comments-box" id="comments_$object_id"><p class="smaller"><div class="comment-menu-link" href="javascript:void(0);" onclick="toggleCommentMenu('$object_type','$object_id')";>&vellip;<div class="comment-menu hidden" id="menu_$object_type\_$object_id"></div></div>$comment_legend</p>~;

if ($LOGGED_IN){
$comments .= qq~<div class="comment-wrapper clearfix">
<a href="$baseURL/profile?id=$myID"><img class="commenter-pic" src="$baseURL/user_pics/$myImage\_t.jpg" alt="$myName"/></a>
<div class="comment" id="new_comment_$object_type\_$object_id">
<textarea class="comment-response" placeholder="Type your comment here" rows="1" id="new_comment_$object_type\_$object_id\_text"></textarea>
<button class="comment-submit smaller right top10" onclick="postComment('new_comment_$object_type\_$object_id',0,'$object_type',$object_id);">POST</button></div>
</div>~;
}else{
$comments .= qq~<p class="center grey">Please <a class="showLogin" href="javascript:void(0);">log in</a> to comment.</p>~;
}
my $thread_top;

while (my ($id, $actor_id, $thread, $comment, $timestamp, $first_name, $last_name, $image) = $getComments->fetchrow_array){
if ($thread == $id){$thread_top = $id;}
my $when = &getWhen($timestamp);
my $hearts = &getHearts('comment', $id);
my $type = 'comment';
if ($thread != $id){$type = 'reply';}
$image = 'q' if !$image;
$comment =~ s/\n|\r/<br\/>/g;
$comments .= qq~
<div class="$type\-wrapper clearfix" id="comment$id">
<a href="$baseURL/profile?id=$actor_id"><img class="commenter-pic" src="$baseURL/user_pics/$image\_t.jpg" alt="$first_name $last_name"/></a>
<div class="comment"><div class="commenter"><a href="$baseURL/profile?id=$actor_id" class="notranslate">$first_name $last_name</a><div class="float-right grey smaller normal">$when</div></div>$comment<div class="comment-actions">$hearts&nbsp;&nbsp;<a href="javascript:void(0);" onclick="toggleHide('replyBox_$id');"><i class="fas fa-undo-alt"></i>&nbsp;<span class="smaller">Reply</span></a>~;
if ($actor_id eq $myID){
$comments .= qq~&nbsp;&nbsp;<a href="javascript:void(0);" onclick="deleteComment('comment$id',$id,'$object_type',$object_id);"><i class="fas fa-trash"></i>&nbsp;<span class="smaller">Delete</span></a>~;
}
$comments .= qq~</div></div>
</div>

<div class="reply-wrapper clearfix hidden" id="replyBox_$id">
<a href="$baseURL/profile?id=$myID"><img class="commenter-pic" src="$baseURL/user_pics/$myImage\_t.jpg" alt="$myName"/></a>
<div class="comment" id="reply_$id">
<textarea class="comment-response" placeholder="Reply to $first_name" rows="1" id="reply_$id\_text"></textarea>
<button class="comment-submit smaller right top10" onclick="postComment('reply_$id',$thread_top,'$object_type',$object_id);">POST</button></div>
</div>
<script>\$(".comment").linkify({target: "_blank"});</script>
~;

}
$getComments->finish;
$comments .= qq~</div>~;
return $comments;
}

sub showComments{
print &getComments(@_);
}


sub showSocialSummary{
my ($object_type, $object_id, $link) = @_;
my $social = qq~<div id="social_$object_type\_$object_id" class="social clearfix"><div class="float-right">~;
$social .= &getHearts($object_type, $object_id);
my $commentNum = int($SBdb->do("SELECT id FROM interactions WHERE action = 'comment' AND object_type = '$object_type' AND object_id = '$object_id'"));
$social .= qq~&nbsp;&nbsp;<span class="social-box"><a href="javascript:void(0);" onclick="showComments('social_$object_type\_$object_id','$object_type',$object_id,'$link');"><i class="fa~;
if ($commentNum > 0) {$social .= qq~s~}else{$social .= qq~r~;}
$social .= qq~ fa-comment"></i> <span class="smaller">~;
if ($commentNum > 0){
$social .= qq~$commentNum comment~;
$social .= qq~s~ if $commentNum > 1;
}else{
$social .= qq~Comment~;
}
$social .= qq~</span></a></span>~;
$social .= qq~&nbsp;&nbsp;<span class="social-box"><a href="javascript:void(0);" onclick="shareThis('$link');"><i class="fas fa-share-alt"></i> <span class="smaller">Share</span></a></span></div></div>~;
print $social;
}


sub getSocial{
my ($object_type, $object_id, $link) = @_;
my $social = qq~<div id="social_$object_type\_$object_id" class="social clearfix"><div class="text-right clear">~;
$social .= &getHearts($object_type, $object_id);
$social .= qq~&nbsp;&nbsp;<span class="social-box"><a href="javascript:void(0);" onclick="shareThis('$link');"><i class="fas fa-share-alt"></i> <span class="smaller">Share</span></a></span>&nbsp;&nbsp;<span class="social-box grey"><a href="javascript:void(0);" onclick="report('$object_type', '$object_id');"><i class="smaller fa-regular fa-flag grey"></i> <span class="smaller grey">Report</span></a></span></div></p>~;
$social .= &getComments($object_type, $object_id);
$social .= qq~</div>~;
return $social;
}


sub showSocial{
print &getSocial(@_);	
}

sub getActor{
my ($object_type, $object_id) = @_;
my $sth = $SBdb->prepare("SELECT CONCAT_WS(' ', m.first_name, m.last_name) AS full_name, m.id FROM members AS m JOIN activity AS a ON a.actor_id = m.id WHERE a.object_type = '$object_type' AND a.object_id = '$object_id' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
return $sth->fetchrow_array;
}else{
return ('UNKNOWN USER',-1);
}
}


sub getEmail{
my $id = shift;
my $sth = $SBdb->prepare("SELECT email FROM members WHERE id = '$id' LIMIT 1");
$sth->execute;
my $email = $sth->fetchrow_array;
$sth->finish;
$email = 'UNKNOWN@sharebay.org' if (!$email);
return $email;
}

sub getListingTitle{
my $listing_id = shift;
my $sth = $SBdb->prepare("SELECT title, description FROM posts WHERE id = $listing_id LIMIT 1");
$sth->execute;
my ($title, $description) = $sth->fetchrow_array;
$title = substr($description, 0, 50) . '...' if ($description && !$title);
$title = 'UNKNOWN' if !$title;
$sth->finish;
return $title;
}

sub generalCTA{
print qq~<p class="center">~;
if ($LOGGED_IN){
print qq~<a class="green-button post-offer" href="javascript:void(0);" title="Post a listing">Post a listing</a>~;
}else{
print qq~<a class="green-button" href="$baseURL/join" title="Join Sharebay - It's Free">Join Sharebay - It's Free!</a></p><p class="center smaller"><a class="showLogin" href="javascript:void(0);">Already a member? Log in</a>~;
}
print qq~</p>~;
}



# sub showSocial{
# my ($url, $desc, $comments) = @_;
# use URI::Escape;
# my $escURL = uri_escape($url);

# print qq~
# <div class="clear" style="margin-top:30px;"><div style="text-align:left;float:left;margin-right:4px"><a href="https://twitter.com/share" class="twitter-share-button" data-url="$url" data-text="$desc" data-via="freeworlder" data-count="none">Tweet</a>
# <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs');</script></div>

# <iframe src="https://www.facebook.com/plugins/like.php?href=$escURL&width=0&layout=standard&action=like&size=small&share=true&height=35&appId=288542516079119" width="80%" height="35" style="border:none;overflow:hidden;width:80%;height:35px;" scrolling="no" frameborder="0" allowfullscreen="true" allow="autoplay; clipboard-write; encrypted-media; picture-in-picture; web-share"></iframe></div>~;

# if ($comments){
# print qq~<a name="comments"></a><div class="fb-comments" data-href="$url" data-numposts="10" data-width="100\%"></div>~;
# }
# }

sub processingFee{
my $amount = shift;
return sprintf("%.2f", (($amount * .04) + 1));
}


sub checkPendingTrans{
my $n = 0;
my $sth = $SBdb->prepare("SELECT id, giver_id, getter_id, listing_type, status FROM transactions WHERE status != 'delivered' AND status != 'cancelled' AND (giver_id = '$myID' OR getter_id = '$myID')");
$sth->execute;

if ($sth->rows > 0){
	while(my ($id, $giver_id, $getter_id, $listing_type, $status) =  $sth->fetchrow_array){
	if ($listing_type eq 'offer'){
		if ($status eq 'applied' && $giver_id eq $myID){$n++;}
	}
	if ($listing_type eq 'request'){
		if ($status eq 'applied' && $getter_id eq $myID){$n++;}
	}
		if ($status eq 'accepted' && $giver_id eq $myID){$n++;}
		if ($status eq 'payment_requested' && $getter_id eq $myID){$n++;}
		if ($status eq 'paid' && $giver_id eq $myID){$n++;}
		if ($status eq 'sent' && $getter_id eq $myID){$n++;}
	}
}
return $n;
}

sub pendingActions{
my $person = shift;

# POSSIBLE STATES:
# applied, accepted, payment_offered, payment_requested, paid, sent, delivered, cancelled, auto-cancelled

# OFFER LISTING STATES (WITH PAYMENT):

# applied = GETTER APPLIES TO OFFER > GIVER
# payment_requested = GIVER ACCEPTS AND ASKS FOR DELIVERY PAYMENT > GETTER
# paid = GETTER PAYS DELIVERY COSTS > GIVER
# sent = GIVER SENDS ITEM > GETTER
# delivered = GETTER RECEIVES ITEM > GIVER


# OFFER LISTING STATES (WITHOUT PAYMENT):

# applied = GETTER APPLIES TO OFFER > GIVER
# accepted = GIVER AGREES TO GIVE > GETTER
# sent = GIVER SENDS ITEM > GETTER
# delivered = GETTER RECEIVES ITEM > GIVER



# REQUEST LISTING STATES (WITH PAYMENT):

# applied = GIVER APPLIES TO GETTER > GETTER
# accepted = GETTER ACCEPTS OFFER > GIVER
# payment_requested = GIVER ASKS FOR DELIVERY PAYMENT > GETTER
# paid = GETTER PAYS DELIVERY COSTS > GIVER
# sent = GIVER SENDS ITEM > GETTER
# delivered = GETTER RECEIVES ITEM > GIVER


# REQUEST LISTING STATES (WITHOUT PAYMENT):

# applied = GIVER APPLIES TO GETTER > GETTER
# accepted = GETTER ACCEPTS OFFER > GIVER
# sent = GIVER SENDS ITEM > GETTER
# delivered = GETTER RECEIVES ITEM > GIVER


# CHECK FOR PENDING ACTIONS
my $transactions;
my $who_string = qq~t.giver_id = '$myID' OR t.getter_id = '$myID'~;
if ($person){
$who_string = qq~(t.giver_id = '$myID' AND t.getter_id = $person) OR (t.giver_id = $person AND t.getter_id = '$myID')~;
}
$transactions = $SBdb->prepare("SELECT t.id, t.listing_id, t.listing_type, t.giver_id, t.getter_id, t.quantity, t.shipping_cost, t.status, p.physical, p.terms FROM transactions AS t JOIN posts AS p ON p.id = t.listing_id WHERE (t.status = 'applied' OR t.status = 'payment_requested' OR t.status = 'payment_offered' OR t.status = 'paid' OR t.status = 'accepted' OR t.status = 'sent') AND ($who_string) ORDER by t.id");
$transactions->execute;
if ($transactions->rows > 0 ){
print qq~<div class="pending-actions">~;

while (my ($id, $listing_id, $listing_type, $giver_id, $getter_id, $quantity, $shipping_cost, $status, $physical, $terms) = $transactions->fetchrow_array){

# SET CONVO_ID
my $convo_id = &getConvoID($giver_id, $getter_id);
my $printQty = $quantity . ' x ';
my $itemS;
if ($quantity > 1){$itemS = 's'};

if ($listing_type eq 'offer'){
# OFFER SPECIFIC
	
if ($status =~ /applied/ && $giver_id eq $myID){

# SOMEONE APPLIED TO YOUR OFFER - ACCEPT? REQUEST PAYMENT?

my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $badge, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($getter_id);
my $listing_title = &getListingTitle($listing_id);
print qq~<div id="trans_$id" class="pending-action"><div class="action-required">ACTION REQUIRED</div><p><a href="$baseURL/profile?id=$getter_id">$first_name $last_name</a>~;
if ($gifted){print qq~ ($gifted)~;}
&printBadge($first_name, $badge_level);
print qq~ has applied for <a href="$baseURL/listing?id=$listing_id">$printQty$listing_title</a>.</p>~;
unless ($person){print qq~<p><a href="$baseURL/messages?id=$convo_id">Send a message to $first_name</a> to discuss, or accept the request?</p>~;}
if ($physical eq 1){
if ($shipping_cost){
print qq~<p>$first_name has suggested a payment of <strong>&dollar;$shipping_cost</strong> to cover shipping costs. (You can accept or change this offer)</p><div class="pay-form" id="payform_$id">~;
}else{
print qq~<p>NOTE: $first_name lives in ~, &getRegion($getter_id), qq~. If you like, you can <a href="javascript:void(0);" onclick="toggleHide('payform_$id');">request a payment</a> to cover delivery costs. (Paypal account required)</p><div class="pay-form hidden" id="payform_$id">~;
}
print qq~<p>Enter an amount that will cover your delivery costs and press 'Accept Request'. (Paypal account required)</p><p class="center">Shipping cost: \$&nbsp;<input type="number" placeholder="0.00" id="shipping_cost" name="shipping_cost" min="0" max="301" value="$shipping_cost" step="0.01" title="Currency" pattern="^\d+(?:\.\d{1,2})?$" onblur="
this.parentNode.parentNode.style.backgroundColor=/^\d+(?:\.\d{1,2})?$/.test(this.value)?'inherit':'red'
" style="max-width:60px;"></p><p>We'll request payment from $first_name on your behalf. As soon as they've paid we'll let you know so you can send the item. Once $first_name confirms delivery of the item, we'll forward the payment to you in full.</p>
<p class="helper">It is your reponsibility to ensure the item is packed and sent correctly. Sharebay bears no responsibility for missing or broken items.</p><p class="smaller">NOTE: We recommend agreeing a shipping amount with $first_name before requesting payment! (<a href="$baseURL/messages?id=$convo_id">Message $first_name</a>)</p></div>~;
}
print qq~<p class="center"><a class="green-button" href="javascript:void(0);" onclick="updateTransaction($id,'accepted');"><i class="fa-solid fa-check"></i>&nbsp;ACCEPT REQUEST</a><br/><span class="smaller">You can also <a title="Cancel this transaction? (You can't undo this)" href="javascript:void(0);" onclick="updateTransaction($id,'cancelled');">cancel this transaction</a>.</span></div>~;
}

if ($status =~ /accepted/ && $giver_id eq $myID){

# YOU ACCEPTED A REQUEST - SEND ITEMS?

my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $badge, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($getter_id);
my $listing_title = &getListingTitle($listing_id);
my $button_text = 'ITEM HAS BEEN SENT';
$button_text = 'ITEMS HAVE BEEN SENT' if $quantity > 1;
print qq~<div id="trans_$id" class="pending-action"><div class="action-required">ACTION REQUIRED</div><p>You accepted a request from <a href="$baseURL/profile?id=$getter_id">$first_name $last_name</a>~;
if ($gifted){print qq~ ($gifted)~;}
&printBadge($first_name, $badge_level);
print qq~ for <a href="$baseURL/listing?id=$listing_id">$printQty$listing_title</a>. You can now send the item$itemS.</p>~;
unless ($person){
print qq~<p><a href="$baseURL/messages?id=$convo_id">Send a message</a> to arrange collection/delivery, or mark item$itemS as sent?</p>~;
}
print qq~<p class="center"><a class="green-button" href="javascript:void(0);" onclick="updateTransaction($id,'sent');"><i class="fa-solid fa-check"></i>&nbsp;$button_text</a><br/><span class="smaller">You can also <a title="Cancel this transaction? (You can't undo this)" href="javascript:void(0);" onclick="updateTransaction($id,'cancelled');">cancel this transaction</a>.</span></p></div>~;
}
}


if ($listing_type eq 'request'){
# REQUEST SPECIFIC

if ($status =~ /applied/ && $getter_id eq $myID){

# SOMEONE RESPONDED TO YOUR REQUEST - ACCEPT?

my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $badge, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($giver_id);
my $listing_title = &getListingTitle($listing_id);
print qq~<div id="trans_$id" class="pending-action"><div class="action-required">ACTION REQUIRED</div><p><a href="$baseURL/profile?id=$giver_id">$first_name $last_name</a>~;
if ($gifted){print qq~ ($gifted)~;}
&printBadge($first_name, $badge_level);
print qq~ has offered to grant your request for <a href="$baseURL/listing?id=$listing_id">$printQty$listing_title</a>.~;
unless ($person){
print qq~<p><a href="$baseURL/messages?id=$convo_id">Send a message</a> to discuss, or accept offer?</p>~;
}
if ($physical eq 1){
if ($shipping_cost){
print qq~<p>$first_name has suggested a payment from you of <strong>&dollar;$shipping_cost</strong> to cover their shipping costs. Do you accept?<input class="hidden" type="number" id="shipping_cost" name="shipping_cost" value="$shipping_cost"/>~;
}else{
print qq~<p>NOTE: $first_name lives in ~, &getRegion($getter_id), qq~. If you like, you can <a href="javascript:void(0);" onclick="toggleHide('payform_$id');">offer a payment</a> to cover their delivery costs. (Paypal account required)</p><div class="pay-form hidden" id="payform_$id">
<p>Enter an amount that you think will cover $first_name\'s shipping costs and press 'Accept Offer'.</p><p class="center">Shipping cost: \$&nbsp;<input type="number" placeholder="0.00" id="shipping_cost" name="shipping_cost" min="0" max="301" value="$shipping_cost" step="0.01" title="Currency" pattern="^\d+(?:\.\d{1,2})?$" onblur="
this.parentNode.parentNode.style.backgroundColor=/^\d+(?:\.\d{1,2})?$/.test(this.value)?'inherit':'red'
" style="max-width:60px;"></p><p>If $first_name agrees, we'll send you a link to complete payment. As soon as you've paid we'll tell $first_name to ship the item$itemS. NOTE: We'll only forward your payment to $first_name after you receive your item$itemS. If they don't arrive we'll refund you.</p>
<p class="helper">It will be up to $first_name to ensure that the item is packed and sent correctly. Sharebay bears no responsibility for missing or broken items.</p><p class="smaller">NOTE: We recommend agreeing a shipping amount with $first_name before offering payment! (<a href="$baseURL/messages?id=$convo_id">Message $first_name</a>)</p></div>~;
}
}
print qq~<p class="center"><a class="green-button" href="javascript:void(0);" onclick="updateTransaction($id,'offer_accepted');"><i class="fa-solid fa-check"></i>&nbsp;ACCEPT OFFER</a><br/><span class="smaller">You can also <a href="javascript:void(0);" title="Cancel this transaction? (You can't undo this)" onclick="updateTransaction($id,'cancelled');">cancel this transaction</a>.</span></p></div>~;
}


if ($status =~ /payment_offered/ && $giver_id eq $myID){

# SOMEONE OFFERED DELIVERY PAYMENT - ACCEPT OR AMEND?

my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $badge, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($getter_id);
my $listing_title = &getListingTitle($listing_id);
print qq~<div id="trans_$id" class="pending-action"><div class="action-required">ACTION REQUIRED</div><p><a href="$baseURL/profile?id=$getter_id">$first_name $last_name</a>~;
if ($gifted){print qq~ ($gifted)~;}
&printBadge($first_name, $badge_level);
print qq~ has accepted your offer to grant their request for <a href="$baseURL/listing?id=$listing_id">$printQty$listing_title</a>.~;
unless ($person){
print qq~<p><a href="$baseURL/messages?id=$convo_id">Send a message</a> to discuss, or accept offer?</p>~;
}
if ($physical eq 1){
if ($shipping_cost){
print qq~<p>$first_name (who lives in ~, &getRegion($getter_id), qq~) has offered a payment of <strong>&dollar;$shipping_cost</strong> to cover your shipping costs. Accept or change amount?.</p><div class="pay-form" id="payform_$id">
<p>Enter an amount that will cover your shipping costs and press 'Accept Offer'.</p><p class="center">Shipping cost: \$&nbsp;<input type="number" placeholder="0.00" id="shipping_cost" name="shipping_cost" min="0" max="301" value="$shipping_cost" step="0.01" title="Currency" pattern="^\d+(?:\.\d{1,2})?$" onblur="
this.parentNode.parentNode.style.backgroundColor=/^\d+(?:\.\d{1,2})?$/.test(this.value)?'inherit':'red'
" style="max-width:60px;"></p><p>If $first_name agrees, we'll send them a link to complete payment. As soon as they've paid we'll let you know so you can ship the item$itemS. We'll reimburse you as soon as $first_name has received your item$itemS. NOTE: You need a Paypal account to receive the funds.</p>
<p class="helper">It will be your responsibility to ensure that the item is packed and sent correctly. Sharebay bears no responsibility for missing or broken items.</p><p class="smaller">NOTE: We recommend agreeing a shipping amount with $first_name before requesting payment! (<a href="$baseURL/messages?id=$convo_id">Message $first_name</a>)</p></div>~;
}
}
print qq~<p class="center"><a class="green-button" href="javascript:void(0);" onclick="updateTransaction($id,'accepted');"><i class="fa-solid fa-check"></i>&nbsp;ACCEPT OFFER</a><br/><span class="smaller">You can also <a href="javascript:void(0);" title="Cancel this transaction? (You can't undo this)" onclick="updateTransaction($id,'cancelled');">cancel this transaction</a>.</span></p></div>~;
}

if ($status =~ /accepted/ && $giver_id eq $myID){

# SOMEONE ACCEPTED YOUR OFFER - GRANT REQUEST?

my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $badge, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($getter_id);
my $listing_title = &getListingTitle($listing_id);
print qq~<div id="trans_$id" class="pending-action"><div class="action-required">ACTION REQUIRED</div><p><a href="$baseURL/profile?id=$getter_id">$first_name $last_name</a>~;
if ($gifted){print qq~ ($gifted)~;}
&printBadge($first_name, $badge_level);
print qq~ has accepted your offer to grant their request for <a href="$baseURL/listing?id=$listing_id">$printQty$listing_title</a>.~;
unless ($person){
print qq~<p><a href="$baseURL/messages?id=$convo_id">Send a message</a> to discuss, or grant request?</p>~;
}
print qq~<p class="center"><a class="green-button" href="javascript:void(0);" onclick="updateTransaction($id,'sent');"><i class="fa-solid fa-check"></i>&nbsp;GRANT REQUEST</a><br/><span class="smaller">You can also <a href="javascript:void(0);" title="Cancel this transaction? (You can't undo this)" onclick="updateTransaction($id,'cancelled');">cancel this transaction</a>.</span></p></div>~;
}
}


if ($status =~ /payment_requested/ && $getter_id eq $myID){

# SOMEONE REQUESTED PAYMENT - PAY?

my $processing_fee = &processingFee($shipping_cost);
my $total = sprintf("%.2f", ($shipping_cost + $processing_fee));
use URI::Escape;
my $notify_url = uri_escape("$baseURL/pp_verify.cgi");
my $return_url = uri_escape("$baseURL/messages?id=$convo_id");
my $cancel_url = uri_escape("$baseURL/transactions?id=$myID");
my $ppURL = "https://www.paypal.com/cgi-bin/webscr?cmd=_xclick&business=colinrturner%40gmail.com&item_name=Sharebay+item+shipping&item_number=$id&amount=$total&currency_code=USD&notify_url=$notify_url&return=$return_url&cancel_return=$cancel_url";

my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $badge, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($giver_id);
my $listing_title = &getListingTitle($listing_id);
print qq~<div id="trans_$id" class="pending-action"><div class="action-required">ACTION REQUIRED</div><p><a href="$baseURL/profile?id=$giver_id">$first_name $last_name</a>~;
if ($gifted){print qq~ ($gifted)~;}
&printBadge($first_name, $badge_level);
print qq~ has requested a shipping payment of <strong>&dollar;$shipping_cost</strong> for sending <a href="$baseURL/listing?id=$listing_id">$printQty$listing_title</a>.</p>~;
unless ($person){print qq~<p><a href="$baseURL/messages?id=$convo_id">Send a message to $first_name</a> to discuss, or send payment?</p>~}
print qq~<p class="helper">For your protection, shipping payments are held by Sharebay until you receive your item. If the item doesn't arrive, you'll be refunded in full.</p>
<p class="center"><a class="blue-button" href="$ppURL"><i class="fa-solid fa-check"></i>&nbsp;PAY WITH PAYPAL</a><br/><span class="smaller">You can also <a title="Cancel this transaction? (You can't undo this)" href="javascript:void(0);" onclick="updateTransaction($id,'cancelled');">cancel this transaction</a>.<br/><span class="smaller">Payments are processed by Paypal. A processing fee of <strong>&dollar;$processing_fee</strong> will be applied at checkout.</span></span></div>~;
}

### TRANSACTION UPDATED TO PAID VIA PP_VERIFY, THEN...

if ($status =~ /paid/ && $giver_id eq $myID){

# SOMEONE PAID YOU FOR DELIVERY - SEND ITEMS?

my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $badge, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($getter_id);
my $listing_title = &getListingTitle($listing_id);
my $button_text = 'ITEM HAS BEEN SENT';
$button_text = 'ITEMS HAVE BEEN SENT' if $quantity > 1;
print qq~<div id="trans_$id" class="pending-action"><div class="action-required">ACTION REQUIRED</div><p><a href="$baseURL/profile?id=$getter_id">$first_name $last_name</a>~;
if ($gifted){print qq~ ($gifted)~;}
&printBadge($first_name, $badge_level);
print qq~ has submitted payment of &dollar;$shipping_cost to cover shipping costs for sending <a href="$baseURL/listing?id=$listing_id">$printQty$listing_title</a>. You can now send the item$itemS.</p>~;
unless ($person){
print qq~<p><a href="$baseURL/messages?id=$convo_id">Send a message</a> to confirm delivery details, or mark item$itemS as sent?</p>~;
}
print qq~<p class="center"><a class="green-button" href="javascript:void(0);" onclick="updateTransaction($id,'sent');"><i class="fa-solid fa-check"></i>&nbsp;$button_text</a><br/><span class="smaller">You can also <a title="Cancel this transaction? (You can't undo this)" href="javascript:void(0);" onclick="updateTransaction($id,'cancelled');">cancel this transaction</a>. ($first_name will be refunded)</span></p></div>~;
}


if ($status =~ /sent/ && $getter_id eq $myID){

# ITEMS HAVE BEEN SENT - DID YOU RECEIVE?

my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $badge, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($giver_id);
my $listing_title = &getListingTitle($listing_id);
print qq~<div id="trans_$id" class="pending-action"><div class="action-required">ACTION REQUIRED</div><p><a href="$baseURL/profile?id=$giver_id">$first_name $last_name</a>~;
if ($gifted){print qq~ ($gifted)~;}
&printBadge($first_name, $badge_level);
print qq~ has sent you <a href="$baseURL/listing?id=$listing_id">$printQty$listing_title</a>. When you have received it, please mark this as delivered.</p>
<p class="center"><a class="green-button" href="javascript:void(0);" onclick="updateTransaction($id,'delivered');"><i class="fa-solid fa-check"></i>&nbsp;CONFIRM DELIVERY</a></p></div>~;
}
}
print qq~</div>~;
}
}


sub leftBar{
my $filter_opts = &getFilters($FORM{filter});

print qq~
<div id="sidebar-container" class="clearfix">
<div id="sidebar-wrap" class="clearfix">
<div id="sidebar-handle-container" onclick="toggleSideBar();">
<div id="sidebar-handle"><div></div><div></div><div></div><div></div></div>
<div id="sidebar-handle"><div></div><div></div><div></div><div></div></div>
</div>
<div id="sidebar">
<form id="search" action="" method="get">
<input type="text" id="sidebar-search" name="search" placeholder="Search..." value="$FORM{search}"/>
<select name="filter">$filter_opts</select>
<select name="order">
<option value="latest"~; if ($FORM{order} eq 'latest') {print qq~ selected~;} print qq~>Latest</option>
<option value="relevance"~; if ($FORM{order} eq 'relevance') {print qq~ selected~;} print qq~>Most relevant</option>
<option value="popular"~; if ($FORM{order} eq 'popular') {print qq~ selected~;} print qq~>Most popular</option>
<option value="nearest"~; if ($FORM{order} eq 'nearest') {print qq~ selected~;} print qq~>Nearest to me</option>~;
if ($myAdmin || $myModerator){
print qq~
<option value="risk"~; if ($FORM{order} eq 'risk') {print qq~ selected~;} print qq~>Spam risk (admin)</option>~;
}
print qq~
</select>
<p>
<!-- div id="source_options">
<label class="source_select" for="sharebay.org"><input type="checkbox" name="sharebay.org" id="sharebay.org" value="1" checked/>&nbsp;Sharebay</label>
<label class="source_select" for="craigslist.com"><input type="checkbox" name="craigslist.com" id="craigslist.com" value="1" checked/>&nbsp;Craigslist</label>
<label class="source_select" for="facebook.com"><input type="checkbox" name="facebook.com" id="facebook.com" value="1" checked/>&nbsp;FB Marketplace</label>
<label class="source_select" for="freecycle.org"><input type="checkbox" name="freecycle.org" id="freecycle.org" value="1" checked/>&nbsp;Freecycle</label>
<label class="source_select" for="gumtree.com"><input type="checkbox" name="gumtree.com" id="gumtree.com" value="1" checked/>&nbsp;Gumtree</label>
</div -->
</p>
<p class="center">
<button type="submit" class="green-button">SEARCH</button>
</p>
</form>
<p class="center smaller">
<a href="$baseURL/map" title="Search on map"><i class="fas fa-map-marker-alt"></i>&nbsp;Search map</a>
</p>
<p class="center">
<a href="$baseURL/?search=&order=relevance" title="You might like..."><i class="fa fa-smile-o"></i>&nbsp;You might like...</a>
</p>
<p class="center smaller" style="margin-top:3em; margin-bottom: 0;">
	<a href="$baseURL/about" title="About Sharebay">About</a> &middot; 
	<a href="$baseURL/how-it-works" title="How Sharebay works">How it works</a> &middot; 
	<a href="$baseURL/faqs" title="Frequently asked questions">FAQs</a> &middot;
	<a href="$baseURL/blog" title="Blog">Sharebay Blog</a> &middot; 
	<a href="$baseURL/page?id=templates" title="Browse our listing templates">Listing templates</a> &middot; 
	<a href="$baseURL/page?id=categories" title="Browse categories<">Browse categories</a> &middot; 
	<a href="$baseURL/page?id=stats" title="Statistics">Statistics</a> &middot; 
	<a href="$baseURL/transactions" title="Public Transaction Record">Transaction Record</a> &middot; 
	<a href="$baseURL/contact" title="Contact us">Contact</a></p>
	
	
</div>
</div></div>~;

}

sub getFeed{
my $page = $FORM{page} || 0;
my $screen = $FORM{screen} || 900;
my $resultsPP = 10;
my $offset = $page * $resultsPP;
my $notBlocked = 1;
if ($LOGGED_IN){
my $blocked = &getBlockedIds;
if ($blocked){$notBlocked = qq~actor_id NOT IN ($blocked)~;
}
}
my $getActivity = $SBdb->prepare("SELECT actor_id, object_type, object_id, image, text, link, location, data, timestamp FROM activity WHERE $notBlocked AND object_type LIKE '%' ORDER BY id DESC LIMIT $resultsPP OFFSET $offset");
$getActivity->execute;
while (my ($actor_id, $object_type, $object_id, $image, $text, $link, $location, $data, $timestamp) = $getActivity->fetchrow_array){
&renderFeed($actor_id, $object_type, $object_id, $image, $text, $link, $location, $data, $timestamp, $screen);
} # END LOOP
print q~<script>$('#feed .item').linkify({target: "_blank"});</script>~;
}


	
sub renderFeed{
my ($actor_id, $object_type, $object_id, $image, $text, $link, $location, $data, $timestamp, $screen, $feature) = @_;
my $when = '<i class="fa fa-clock-o" aria-hidden="true"></i>&nbsp;' . &getWhen($timestamp);
print qq~<div class="item clearfix">~;
&getUserCard($actor_id) unless $object_type eq 'profile';
my $info;
if ($location){
$info = qq~<i class="fas fa-map-marker-alt"></i>&nbsp;$location&nbsp;~;
}
$info .= qq~$when~;
print qq~<div class="item-location smaller">$info</div>~;
if ($object_type eq 'listing'){
# if ($image){
# $image =~ s/\.jpg/_t.jpg/ if $screen <= 600;
	# print qq~<div class="image-wrapper bottom20"><a href="$link"><img src="$image"/></a></div>~;
# }
$link = qq~$baseURL/listing?id=$object_id~;
my $buttonText = 'REQUEST THIS';
my $TYPE = 'OFFER';
if ($data eq 'request'){
	$buttonText = 'OFFER THIS';
	$TYPE = 'REQUEST';
	}
$text = qq~<span class="post_type">$TYPE:</span> ~ . $text;
if ($actor_id eq $myID){
	$buttonText = 'VIEW';
	$link = qq~$baseURL/listing?id=$object_id~;
	}
if (length($text) > 300){
my $first = substr($text, 0, 300);
my $last = substr($text, 300);
$text = qq~<input type="checkbox" class="read-more-check" id="more_$object_type\_$object_id"/><span class="feed-text">$first~;
$text .= qq~<span class="more-text">$last</span></span>&nbsp;<label for="more_$object_type\_$object_id" class="read-more-trigger"></label>~;
}
$text =~ s/\r?\n/<br\/>/g;

print qq~<p>$text</p><p class="smaller brand smallOnly">$info</p>~;

if ($image){
$image =~ s/\.jpg/_t.jpg/ if $screen <= 600;
print qq~<div class="image-wrapper bottom20"><a href="$link"><img src="$image"/></a></div>~;
}

print qq~
<p class="center"><a class="green-button" href="$link" title="$buttonText">$buttonText</a>~;
if ($actor_id eq $myID){
print qq~
<a href="$baseURL/listing?a=edit&id=$object_id" title="Edit listing" class="green-button"><i class="fa fa-pencil"></i></a>
<a onclick="deleteListing($object_id,document.URL);" href="javascript:void(0);" title="Delete listing" class="green-button"><i class="far fa-trash-alt"></i></a>~;
}
if ($myAdmin || $myModerator){
print qq~<div id="admin_listing_$object_id">~, &adminBox('listing', $object_id), qq~</div>~;
}
print qq~</p>~;
}
elsif ($object_type eq 'profile'){
if (!$image){
$image = qq~$baseURL/user_pics/q.jpg~;
}
$link = qq~$baseURL/profile?id=$object_id~;
print qq~<div class="clearfix center"><a href="$link"><img class="item-profile-image" src="$image"/></a><p onclick="window.location.href='$link';" class="center pointer">$text</p></div>~;
if ($myAdmin || $myModerator){
print qq~<div id="admin_profile_$object_id">~, &adminBox('profile', $object_id), qq~</div>~;
}
}
elsif ($object_type eq 'review'){
if ($data){
my $stars = &renderStars($data);
print qq~<div class="clearfix center"><a class="bigger" href="$link">$stars</a>~;
}
print qq~<p class="center">$text</p></div>~;
}
elsif ($object_type eq 'transaction'){
print qq~<div class="clearfix center"><a href="$link" class="delivered">&#x2714;</a><br/>
<p class="center">$text</p></div>~;
}elsif ($object_type eq 'blog'){
print qq~~;
if ($image){
	print qq~<div class="image-wrapper bottom20"><a href="$link"><img src="$image"/></a></div>~;
}
print qq~<p>$text</p>
<p class="center"><a class="green-button" href="$link">Read article</a></p>
~;
}
if ($feature){
&showSocial($object_type, $object_id, $link);
}else{
&showSocialSummary($object_type, $object_id, $link);
}
print qq~</div>~;
}



sub featureFeed{
my $object_type = $FORM{object_type};
my $object_id = $FORM{object_id};
my $screen = $FORM{screen} || 900;
if ($object_type && $object_id){
my $notBlocked;
if ($LOGGED_IN){
my $blocked = &getBlockedIds;
if ($blocked){$notBlocked = qq~AND actor_id NOT IN ($blocked)~;
}
}
my $getActivity = $SBdb->prepare("SELECT actor_id, object_type, object_id, image, text, link, location, data, timestamp FROM activity WHERE object_type = '$object_type' AND object_id = '$object_id' $notBlocked LIMIT 1");
$getActivity->execute;
if ($getActivity->rows > 0){
my ($actor_id, $object_type, $object_id, $image, $text, $link, $location, $data, $timestamp) = $getActivity->fetchrow_array;
&renderFeed($actor_id, $object_type, $object_id, $image, $text, $link, $location, $data, $timestamp, $screen, 1);
}
}
&getFeed;
}



sub wtfLog{
my $WTF = shift;
open (WTFILE, ">>$root/WTF.log");
print WTFILE "$WTF\n";
close (WTFILE);
}

sub createToken{
my $value = shift;
my @chars = ('a'..'z','A'..'Z',0..9);
my $passport = join '', (map {$chars [rand@chars]} @chars)[0..9];
open(FILE, ">$root/temp/$passport");
print FILE "$value";
close (FILE);
return $passport;
}

sub getDate{
my $timestamp = shift;
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime($timestamp);
$mon+=1;
$year+=1900;
my $time=sprintf("%02d:%02d, %02d/%02d/%02d",$hour,$min,$mday,$mon,$year);
return $time;
}

sub getW3CDate{
my $timestamp = shift;
my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst)=localtime($timestamp);
$mon+=1;
$year+=1900;
my $time=sprintf("%02d-%02d-%02d",$year,$mon,$mday);
return $time;
}

sub getWhen{
my $timestamp = shift;
my $elapsed = $now - $timestamp;
if (!$timestamp){return "never";}
elsif ($elapsed >= 0 && $elapsed <= 5){return "just now";}
elsif($elapsed > 5 && $elapsed <= 45){return "a few seconds ago";}
elsif($elapsed > 45 && $elapsed <= 105){return "a minute ago";}
elsif($elapsed > 105 && $elapsed <= 165){return "a couple of minutes ago";}
elsif($elapsed > 165 && $elapsed <= 285){return "a few minutes ago";}
elsif($elapsed > 285 && $elapsed <= 585){return "five minutes ago";}
elsif($elapsed > 585 && $elapsed <= 1185){return "ten minutes ago";}
elsif($elapsed > 1185 && $elapsed <= 1785){return "twenty minutes ago";}
elsif($elapsed > 1785 && $elapsed <= 3585){return "half an hour ago";}
elsif($elapsed > 3585 && $elapsed <= 7185){return "an hour ago";}
elsif($elapsed > 7185 && $elapsed <= 86385){
my $hours = int(($elapsed + 15) / 3600);
return $hours . " hours ago";
}
elsif($elapsed > 86385 && $elapsed <= 172785){return "a day ago";}
elsif($elapsed > 172785 && $elapsed <= 604785){
my $days = int(($elapsed + 15) / 86400);
return $days . " days ago";
}
elsif($elapsed > 604785 && $elapsed <= 691185){return "a week ago";}
elsif($elapsed > 691185 && $elapsed <= 1209585){return "over a week ago";}
elsif($elapsed > 1209585 && $elapsed <= 2591985){
my $weeks = int(($elapsed + 15) / 604800);
return $weeks . " weeks ago";
}
elsif($elapsed > 2591985 && $elapsed <= 2851185){return "a month ago";}
elsif($elapsed > 2851185 && $elapsed <= 5443185){return "over a month ago";}
elsif($elapsed > 5443185 && $elapsed <= 31557585){
my $months = int(($elapsed + 15) / 2626560);
return $months . " months ago";
}
elsif($elapsed > 31557585 && $elapsed <= 34184145){return "a year ago";}
elsif($elapsed > 34184145 && $elapsed <= 63115185){return "over a year ago";}
elsif($elapsed > 63115185){
my $years = int(($elapsed + 15) / 31557600);
return "more than two years ago";
}
}

sub randomString{
my $len = shift || 32;
my @chars = ('a'..'z','A'..'Z',0..9);
return join '', (map {$chars [rand@chars]} @chars)[0..$len];
}


sub createSession{
my $user_id = shift;
my $getSessionID = $SBdb->prepare("SELECT session_id FROM members WHERE id = '$user_id' AND session_id != '' LIMIT 1");
$getSessionID->execute;
if ($getSessionID->rows > 0){
return $getSessionID->fetchrow_array;	
}else{
my @chars = ('a'..'z','A'..'Z',0..9);
my $token = join '', (map {$chars [rand@chars]} @chars)[0..32];
my $setSession = $SBdb->do("UPDATE members SET session_id = '$token' WHERE id = '$user_id' LIMIT 1");
return $token;
}
}

sub addSlashes {
    my $text = shift;
    ## Make sure to do the backslash first!
    $text =~ s/\\/\\\\/g;
    $text =~ s/'/\\'/g;
    $text =~ s/"/\\"/g;
    $text =~ s/\\0/\\\\0/g;
    return $text;
}

sub removeStopWords{
	my @input = @_;
	open (my $fh, '<', "$siteroot/stopwords.txt") || die;
	my @stopwords = <$fh>;
	close ($fh);
	chomp @stopwords;
my %in_sw = map {$_ => 1} @stopwords;
my @clean  = grep {not $in_sw{$_}} @input;
return @clean;
}


sub doSearch{
my $page = $FORM{page} || 0;
my $screen = $FORM{screen} || 900;
my $resultsPP = 12;
my $offset = $page * $resultsPP;
	
# SAVE QUERY FOR ANALYSIS AND USER MATCHES
if ($FORM{search} && $page eq 0 && $myID ne '' && $FORM{filter} ne 'members'){ 
my $saveQuery = $SBdb->prepare("INSERT IGNORE INTO searches (user_id, query) VALUES(?,?)");
$saveQuery->execute($myID, lc($FORM{search}));
$saveQuery->finish;
}

if ($myAdmin || $myModerator){
if ($FORM{filter} eq 'spam_members'){




	
}elsif($FORM{filter} eq 'spam_listings'){



	
}
}


if ($FORM{filter} eq 'members'){
	
if (!$LOGGED_IN){
print qq~<p class="error">You need to be a logged-in member to do a member search. Please <a href="$baseURL/join">register</a> or <a class="showLogin" href="javascript: void(0);">log in</a> to continue.</p>~;
}else{


########## SEARCH MEMBERS ############
	
my $query;
if (!$FORM{search} && $FORM{order} eq 'relevance'){
$query = &getInterests($myID);
}else{
$query = $FORM{search};
}

#~ # GET NAME, INFO AND STRIPES
my $sth = qq~SELECT id, first_name, last_name, image, city, region, country, about_me, tags, gifted, trust_score, badge_level, star_rating, is_admin, joined, risk, (6371 * acos(cos(radians($myLat)) * cos(radians(lat)) * cos(radians(lon) - radians($myLon)) + sin(radians($myLat)) * sin(radians(lat)))) AS distance~;

if ($FORM{order} eq 'relevance'){
if ($FORM{search}){
	$sth .= qq~, MATCH (first_name, last_name, org_name, org_desc, tags, about_me) AGAINST ('$query' IN BOOLEAN MODE) AS bestmatch~;
	}
elsif(!$FORM{search}){
	$sth .= qq~, MATCH (tags, about_me) AGAINST ('$query' IN BOOLEAN MODE) AS bestmatch~;
	}
}else{
	$sth .= ', id AS bestmatch';
	}
		
$sth .= qq~ FROM members WHERE activated = 1 AND id != '$myID'~;
	
my $blocked = &getBlockedIds;
if ($blocked){
$sth .= qq~ AND id NOT IN ($blocked)~;
}

if ($FORM{search}){
	$sth .= qq~ AND MATCH (first_name, last_name, org_name, org_desc, tags, about_me) AGAINST ('$query')~;}

$sth .= qq~ GROUP BY id~;

my $order_by;
if ($FORM{order} eq 'nearest'){$order_by = ' ORDER BY distance ASC'}
elsif ($FORM{order} eq 'latest'){$order_by = ' ORDER BY joined DESC'}
elsif ($FORM{order} eq 'relevance'){$order_by = ' ORDER BY bestmatch DESC'}
elsif ($FORM{order} eq 'popular'){$order_by = ' ORDER BY rank DESC'}
elsif ($FORM{order} eq 'active'){$order_by = ' ORDER BY last_active DESC'}
elsif ($FORM{order} eq 'risk'){$order_by = ' ORDER BY risk DESC'}
else{
	if ($FORM{search}){
	$order_by = ' ORDER BY bestmatch DESC'; $FORM{order} = 'relevance';
	}else{
	$order_by = ' ORDER BY joined DESC'; $FORM{order} = 'latest';
	}
	};

$sth .= $order_by;

if ($page eq 0){
my $num_results = $SBdb->do($sth);
if ($num_results < 1){$num_results = 'No';}

my $heading;

$heading = qq~$num_results results found~;
if ($FORM{search}){$heading .= qq~ for &quot;$FORM{search}&quot;~;}
$heading .= qq~ in Members~;

print qq~<h3>$heading</h3>~;
}

$sth .= qq~ LIMIT $resultsPP OFFSET $offset~;

my $getResults = $SBdb->prepare($sth);
$getResults->execute;

while(my ($id, $first_name, $last_name, $image, $city, $region, $country, $about_me, $tags, $gifted, $trust_score, $badge_level, $star_rating, $myAdmin, $joined, $risk, $distance, $bestmatch)= $getResults->fetchrow_array){
my $link = qq~$baseURL/profile?id=$id~;
my ($kilometres, $miles);
if ($distance > 20){$kilometres = int($distance);}else{$kilometres = sprintf("%.1f", $distance)};
$kilometres = &commafy($kilometres);
if ($distance > 20){$miles = int($distance * .625);}else{$miles = sprintf("%.1f", ($distance * .625))};
$miles = &commafy($miles);

print qq~<div class="item clearfix">~;
print qq~<div class="item-location smaller"><i class="fas fa-map-marker-alt"></i>&nbsp;$city, $region, $country $kilometres\km ($miles\m))</div>~;

if ($image){
$image = qq~$baseURL/user_pics/$image\.jpg~;
}else{
$image = qq~$baseURL/user_pics/q.jpg~;
}

print qq~<div class="clearfix center"><a href="$link" alt="$first_name $last_name"><img class="item-profile-image" src="$image" alt="$first_name $last_name"/></a><p class="center bigger">$first_name $last_name~;

if ($gifted){
print qq~&nbsp;<span title="$first_name has given $gifted times">($gifted)</span> ~;}
&printBadge($first_name, $badge_level);
if ($star_rating){
my $stars = &renderStars($star_rating);
print qq~&nbsp;<span class="smaller" title="$first_name has a $star_rating star rating">$stars</span>~;
}

print qq~</p>~;
if ($about_me || $tags){
print qq~<p>~;
$about_me = substr($about_me, 0, 300) . '...' if length($about_me) > 300;
print qq~$about_me~ if $about_me;
print qq~, ~ if $about_me && $tags;
print qq~<span class="brand">~, &printtags($tags), qq~</span>~ if $tags;
print qq~</p>~;
}

print qq~</div>~;
if ($myAdmin || $myModerator){
print qq~<div id="admin_profile_$id">~, &adminBox('profile', $id), qq~</div>~;
}
&showSocialSummary('profile', $id, $link);
print qq~</div>~;
} ## END LOOP
}
}else{


########## SEARCH LISTINGS ############


my $query;


if (!$FORM{search}){


if ($FORM{filter} eq 'offers'){$query = &getWants($myID)}
elsif ($FORM{filter} eq 'requests'){$query = &getHaves($myID)}
else{$query = &getInterests($myID);}

# $query = &getInterests($myID);
}else{
$query = $FORM{search};
}
my $sth = qq~SELECT l.id, l.lister, l.title, l.description, l.type, l.category, l.image, l.timestamp, l.risk, (6371 * acos(cos(radians($myLat)) * cos(radians(l.lat)) * cos(radians(l.lon) - radians($myLon)) + sin(radians($myLat)) * sin(radians(l.lat)))) AS distance~;

if ($query){
	$sth .= qq~, MATCH (l.title, l.description, l.tags) AGAINST ('$query' IN BOOLEAN MODE) AS bestmatch~;
	}else{
		$sth .= ', l.id AS bestmatch';
		}

$sth .= qq~, m.region, m.country, m.image FROM posts AS l LEFT JOIN members AS m ON m.id = l.lister WHERE l.status = 'live'~;

my $cat;
my $lister_id;

if ($FORM{filter} eq 'offers'){$sth .= qq~ AND type = 'offer'~}
elsif ($FORM{filter} eq 'requests'){$sth .= qq~ AND type = 'request'~}
elsif ($FORM{filter} =~ m/cat_/){
(undef, $cat) = split('_' , $FORM{filter});
$sth .= qq~ AND l.category = '$cat'~;
}
elsif ($FORM{filter} =~ m/member_/){
(undef, $lister_id) = split('_' , $FORM{filter});
$sth .= qq~ AND l.lister = '$lister_id'~;
};
if ($FORM{physical} eq 1){$sth .= qq~ AND physical = 1~};
if ($FORM{physical} eq 0){$sth .= qq~ AND physical = 0~};
if ($LOGGED_IN){
if ($FORM{order} eq 'nearest' ){$sth .= qq~ AND l.lister != '$myID'~};
	
my $blocked = &getBlockedIds;
if ($blocked){
$sth .= qq~ AND l.lister NOT IN ($blocked)~;
}
}

if ($FORM{search}){$sth .= qq~ AND MATCH (l.title, l.description, l.tags) AGAINST ('$query' IN BOOLEAN MODE)~;}


my $order_by;
if ($FORM{order} eq 'relevance'){$order_by = ' ORDER BY bestmatch DESC'}
elsif ($FORM{order} eq 'nearest'){$order_by = ' ORDER BY distance ASC'}
elsif ($FORM{order} eq 'latest'){$order_by = ' ORDER BY l.timestamp DESC'}
elsif ($FORM{order} eq 'popular'){$order_by = ' ORDER BY l.rank DESC'}
elsif ($FORM{order} eq 'risk'){$order_by = ' ORDER BY l.risk DESC'}
else{
	if ($FORM{search}){
	$order_by = ' ORDER BY bestmatch DESC'; $FORM{order} = 'relevance';
	}else{
	$order_by = ' ORDER BY l.timestamp DESC'; $FORM{order} = 'latest';
	}
	}

$sth .= $order_by;

if ($page eq 0){
	
my $heading;
my $num_results = $SBdb->do($sth);
if ($num_results < 1){$num_results = 'No';}

$heading = qq~$num_results listings found~;
if ($FORM{search}){$heading .= qq~ for &apos;$FORM{search}&apos;~};
if ($FORM{filter} =~ m/cat_/){
my ($category, undef) = &getCategory($cat);
$heading .= qq~ in $category~
}
elsif ($FORM{filter} =~ m/member_/){
my $lister_name = &getFullName($lister_id);
$heading .= qq~ from <a href="$baseURL/profile?id=$lister_id">$lister_name</a>~
}else{
$heading .= qq~ in ~ . ucfirst($FORM{filter});
}
print qq~<h3>$heading</h3>~;
}

$sth .= qq~ LIMIT $resultsPP OFFSET $offset~;

my $getResults = $SBdb->prepare($sth);
$getResults->execute;

while(my($id, $lister, $title, $description, $type, $category, $image, $timestamp, $risk, $distance, $bestmatch, $region, $country, $member_image)= $getResults->fetchrow_array){
my $link = qq~$baseURL/listing?id=$id~;
my ($kilometres, $miles);
if ($distance > 20){$kilometres = int($distance);}else{$kilometres = sprintf("%.1f", $distance)};
$kilometres = &commafy($kilometres);
if ($distance > 20){$miles = int($distance * .625);}else{$miles = sprintf("%.1f", ($distance * .625))};
$miles = &commafy($miles);
# if ($image){
# $image = "$baseURL/listing_pics/$image\.jpg";
# $image =~ s/\.jpg/_t.jpg/ if $screen <= 600;
# }
my $when = '<i class="fa fa-clock-o" aria-hidden="true"></i>&nbsp;' . &getWhen($timestamp);
print qq~<div class="item clearfix">~;
&getUserCard($lister);
my $info;
if ($region && $country){
$info = qq~<i class="fas fa-map-marker-alt"></i>&nbsp;$region, $country&nbsp;~;
}
$info .= qq~$when~;
print qq~<div class="item-location smaller">$info</div>~;

# if ($image){
# print qq~<div class="image-wrapper bottom20"><a href="$link" title="$title"><img src="$image"/></a></div>~;
# }
my $buttonText = 'REQUEST THIS';
my $TYPE = 'OFFER';
if ($type eq 'request'){
	$buttonText = 'OFFER THIS';
	$TYPE = 'REQUEST';
	}
if ($lister eq $myID){
	$buttonText = 'VIEW';
	$link = qq~$baseURL/listing?id=$id~;
	}
print qq~<p><span class="post_type">[$TYPE]</span> $title~;
print qq~&nbsp;&mdash;&nbsp;~ if $title && $description;
print qq~$description</p><p class="smaller brand smallOnly">$info</p>~;
if ($image){
$image = "$baseURL/listing_pics/$image\.jpg";
$image =~ s/\.jpg/_t.jpg/ if $screen <= 600;
print qq~<div class="image-wrapper bottom20"><a href="$link" title="$title"><img src="$image"/></a></div>~;
}
print qq~
<p class="center"><a class="green-button" href="$link">$buttonText</a>~;

if ($lister eq $myID){
print qq~
<a href="$baseURL/listing?a=edit&id=$id" title="Edit listing" class="green-button"><i class="fa fa-pencil"></i></a>
<a onclick="deleteListing($id,document.URL);" href="javascript:void(0);" title="Delete listing" class="green-button"><i class="far fa-trash-alt"></i></a>~;
}
print qq~</p>~;

if ($myAdmin || $myModerator){
print qq~<div id="admin_listing_$id">~, &adminBox('listing', $id), qq~</div>~;
}
&showSocialSummary('listing', $id, $baseURL . '/listing?id=' . $id);

print qq~</div>~;

} ## END LOOP

}
}


sub cleanText{
# STRIP OUT HTML AND NEW LINES
my $t = shift;
$t =~ s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$t =~ s/\n|\r/ /g;
$t =~ s/  / /g;
return $t;
}




# print qq~content-type: text/html; charset=utf-8\n\nThis page is not blank.~;
1;

#EXEUNT
