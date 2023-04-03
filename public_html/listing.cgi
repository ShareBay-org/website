#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR CREATING, EDITING AND DISPLAYING
# USER LISTINGS

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );

require 'common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);



;

if ($a eq 'new'){&newListing;}
elsif ($a eq 'edit'){&editListing();}
elsif ($a eq 'showlisting' && $FORM{id}){&showListing($FORM{id});}
elsif (!$a && $FORM{id}){&showListing($FORM{id});}
elsif (!$a && !$FORM{id}){&showAllListings();}


sub newListing{
&header('Create a listing', 'Post an offer or request on the Sharebay posts', undef, undef, 'page');

if (!$LOGGED_IN){
print qq~<p class="error">Please log in to post a listing.</p>~;
&showLogin;
}else{
print qq~<h2 class="center">Post an offer</h2>
<p class="center">
<a class="green-button center" href="listing?a=edit&type=offer&physical=yes"><i class="fas fa-box-open fa-2x" style="vertical-align:middle;"></i>&nbsp;&nbsp;OFFER AN ITEM</a>
<a class="green-button center" href="listing?a=edit&type=offer&physical="><i class="fas fa-wrench fa-2x fa-flip-horizontal" style="vertical-align:middle;"></i>&nbsp;&nbsp;OFFER A SERVICE</a></p>
<p class="helper">Can't think what to offer? Try one of our <a href="page?id=templates">offer templates</a>.</p>
<p class="center">You can also:<br/>
&nbsp;<a href="listing?a=edit&type=request&physical=yes">Request an item</a>&nbsp;&nbsp;
<a href="listing?a=edit&type=request&physical=">Request a service</a>&nbsp;
</p>~;
}
&footer;
}


sub editListing{
&bounceNonLoggedIn('Please log in to edit this listing.');
my ($hasData, $hasImage, $listing_id, $listing_title, $listing_desc, $listing_quantity, $image, $type, $physical, $category, $trusted_only, $terms, $imageRef, $tags, $lat, $lon, $send_ok, $status, $listingLatLon, $from_template);
$hasData = 'false';
$hasImage = '';


### GET TEMPLATE DATA IF REQUESTED
if ($FORM{from_template}){
	my $getTemplate = $SBdb->prepare("SELECT title, description, tags, category, physical FROM listing_templates WHERE id = '$FORM{from_template}' LIMIT 1");
	$getTemplate->execute;
	if ($getTemplate->rows > 0)	{
		($listing_title, $listing_desc, $tags, $category, $physical) = $getTemplate->fetchrow_array;
		$from_template = 1;
}
$getTemplate->finish;
}


##IF LISTING EXISTS AND IS OWNER, GET EXISTING DATA...
if ($FORM{id}){
$listing_id = $FORM{id};
my $sth = $SBdb->prepare("SELECT title, description, quantity, type, physical, category, trusted_only, terms, image, tags, lat, lon, send_ok, status from posts WHERE id = $listing_id AND lister = '$myID' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
($listing_title, $listing_desc, $listing_quantity, $type, $physical, $category, $trusted_only, $terms, $imageRef, $tags, $lat, $lon, $send_ok, $status) = $sth->fetchrow_array;
$hasData = 'true';
$listingLatLon = 'lat: ' . $lat . ', lng: ' . $lon;
if (-e "$siteroot/listing_pics/$imageRef\.jpg"){
$hasImage = $imageRef . '.jpg';
}
}else{
## NO SUCH LISTING OR YOU DON'T HAVE PERMISSION
&errorCatcher("You can't edit this listing! It may have expired or you don't have access rights.");
}
}
if (!$listingLatLon){$listingLatLon = 'lat: ' . $myLat . ', lng: ' . $myLon;}

my $title;
if ($from_template){$type = 'offer';}
if (!$type){$type = $FORM{type}};
if (!$physical){$physical = $FORM{physical}};
if ($hasData eq 'true'){
	$title = "Edit listing";
}else{
	if ($type eq 'request'){
		if ($physical){
			$title = '<i class="fas fa-box-open"></i>&nbsp;&nbsp;Request an item'}else{$title = '<i class="fas fa-wrench fa-flip-horizontal"></i>&nbsp;&nbsp;Request a skill or service'}}
	else{
		if ($physical){
			$title = '<i class="fas fa-box-open"></i>&nbsp;&nbsp;Offer a physical item'}else{$title = '<i class="fas fa-wrench fa-flip-horizontal"></i>&nbsp;&nbsp;Offer a skill or service'}}
}
my $pageTitle = $title;
$pageTitle =~ s/<[^>]*>//g;
my $desc = "List an offer or request on Sharebay.";
my $headerInject = qq~
<link rel="stylesheet" href="$baseURL/css/jquery-ui.css">
<link rel="stylesheet" href="$baseURL/css/jquery.tagit.css?v=$version">
<link href="slim/slim.min.css" rel="stylesheet">
<script type="text/javascript">
var myListingLatLng = {$listingLatLon};
var hasData = $hasData;
var hasImage = '$hasImage';
</script>~;
my $footerInject = qq~
<script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
<!-- script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?v=3&key=AIzaSyD4zc3ELJ8ZgqLMZqLhLGv7beewD6wN9eU"></script -->
<script src="$baseURL/js/tag-it.js?v=$version"></script>
<script src="slim/slim.jquery.js?v=$version"></script>
<script src="$baseURL/js/listing.js?v=$version"></script>~;

&header($pageTitle, $desc, undef, $headerInject, 'page');

if (!$LOGGED_IN){
print qq~<p class="error">Please log in to post a listing.</p>~;
&showLogin;
}else{

# GET CATEGORIES AND SET SELECTED IF EXISTS

my $cat_select = &getCategories($category);

my $qtySelect = &qtySelect($listing_quantity);

print qq~

<!-- BEGIN FORM CONTENT -->
<!-- Begin form -->
<div id="rForm">
<form name="listing" id="listing">
<h2>$title</h2>~;
if ($from_template){print qq~<p>This is a standard listing template. Please edit the information below to make it your own.</p>~;};
print qq~
<input type="hidden" name="a" value="savelisting"/>
<input type="hidden" name="good2go" value=""/>
<input type="hidden" name="listing_id" value="$listing_id"/>
<input type="hidden" name="image" value=""/>
<input type="hidden" name="from_template" value="$FORM{from_template}"/>
<input type="hidden" name="type" value="$type"/>
<input type="hidden" name="physical" value="$physical"/>


<label for="listing_title" id="title_label" class="inputrequired">Listing title:</label>
<input type="text" id="listing_title" name="listing_title" class="forminput" value="$listing_title" placeholder="~;
if ($type eq 'request'){print qq~What are you looking for?~;}else{print qq~What are you offering?~;} print qq~"/>
<div id="listing_title_E" class="inlineerror">! Please add a title or description</div>

<label for="listing_desc" class="inputrequired">Description:</label>
<textarea name="listing_desc" id="listing_desc" class="forminput" placeholder="Add a short description...">$listing_desc</textarea>
<div id="listing_desc_E" class="inlineerror">! Please add a title or description</div>

<label for="category" class="inputrequired">Category:</label>
     <select name="category" id="category_select" class="forminput"><option value="">select a category</option>$cat_select</select> 
	<div id="category_select_E" class="inlineerror">! You must select a category</div>

<label for="listing_quantity" id="quantity_label" class="inputrequired">~;
if ($type eq 'request'){print qq~How many do you need?~;}else{print qq~How many are you offering?~;} print qq~</label>
<select name="listing_quantity" id="listing_quantity" class="forminput">$qtySelect</select>


<label for="listingPic" class="inputrequired">Add a picture to your listing:</label>
<div id="listingPicContainer">
<input type="file" id="listingPic" class="forminput"/>
</div>

<label for="listingMap" class="inputrequired">Please set your listing location:</label>
<div id="listingMap"></div>
<input type="hidden" name="listingLat" id="listingLat" value="~; if ($hasData eq 'true'){print qq~$lat~}else{print qq~$myLat~;} print qq~"/>
<input type="hidden" name="listingLon" id="listingLon" value="~; if ($hasData eq 'true'){print qq~$lon~}else{print qq~$myLon~;} print qq~"/>
<div id="listingMap_E" class="inlineerror">! Please set a location for your item</div>


<label for="tags" class="inputrequired">Add some tags to your listing to help people find it.</label>
<span class="smaller italic">eg. "skin care, nutrition, consultant, etc"</span>
<ul id="tags" class="forminput notranslate">~;
my @tagS = split(',',$tags);
my $tags;
for (@tagS){$tags .= '<li>' . $_ . '</li>'};
print qq~
$tags</ul>
<div id="tags_E" class="inlineerror">! Please enter at least two tags to describe your listing</div>
~;

if ($physical){
my $question = 'Is this item free to keep or to borrow?';
$question = 'Do you need one to keep or just on loan?' if $type eq 'request';
print qq~	
<label for="terms" id="terms_label" class="inputrequired">$question</label>
    <div id="terms" class="buttons">
    <input type="radio" id="terms_free" name="terms" value="free"~; if (!$terms || $terms eq 'free'){print qq~checked="checked"~;}print qq~>&nbsp;&nbsp;<label for="terms_free"><span>Free to keep</span></label><br/><input type="radio" id="terms_loan" name="terms" value="loan"~; if ($terms eq 'loan'){print qq~checked="checked"~;}print qq~>&nbsp;&nbsp;<label for="terms_loan"><span>On loan</span></label>
    </div>
<div id="terms_E" class="inlineerror">! Please select one</div>~;
}


if ($physical){
my $question = 'If the recipient offers to pay postage, will you package and send the item?';
$question = 'Will you pay postage if recipient agrees to send the item?' if $type eq 'request';
my $answer1 = 'Yes, I will pack the item for sending';
$answer1 = 'Yes, I will pay postage costs' if $type eq 'request';
my $answer2 = 'No, this item is unsuitable for sending';
$answer2 = 'No' if $type eq 'request';
print qq~
<label for="send_ok" id="send_ok_label" class="inputrequired">$question</label>
    <div id="send_ok" class="buttons">
    <input type="radio" id="send_ok_yes" name="send_ok" value="1"~; if (!$send_ok || $send_ok eq '1'){print qq~checked="checked"~;}print qq~>&nbsp;&nbsp;<label for="send_ok_yes"><span>$answer1</span></label><br/><input type="radio" id="send_ok_no" name="send_ok" value="0"~; if ($send_ok eq '0'){print qq~checked="checked"~;}print qq~>&nbsp;&nbsp;<label for="send_ok_no"><span>$answer2</span></label>
    </div>
<div id="send_ok_E" class="inlineerror">! Please select one</div>~;
}

my $my_stripes = &getStripeLevel(&getTrustScore($myID));

my $trust_question = 'Who can apply for this offer?';
$trust_question = 'Who would you like to hear from?' if $type eq 'request';
print qq~
<label for="trusted_only" id="trusted_only_label" class="inputrequired">$trust_question</label>
    <div id="trusted_only" class="buttons"> 
<div><input type="radio" id="trusted_only_0" name="trusted_only" value="0"~; if ($trusted_only eq 0 || $trusted_only eq ''){print qq~checked="checked"~;}print qq~>&nbsp;&nbsp;<label for="trusted_only_0"> Any member</label></div>
      <div><input type="radio" id="trusted_only_1" name="trusted_only" value="1"~; if ($trusted_only eq 1){print qq~checked="checked"~;}print qq~>&nbsp;&nbsp;<label for="trusted_only_1"><img src="$baseURL/i/shield-silver.png" class="badge" alt="Trust badge"/> Trusted members only</label></div>
    </div>
<div id="trusted_only_E" class="inlineerror">! Please select one</div>~;




if ($type eq 'offer'){
	print qq~<p class="helper">Please note all offers must be for genuine and unconditionally free items or services.</p>~;
}
print qq~

<p class="center"><button id="post_listing" name="post" value="POST LISTING" class="green-button">POST LISTING</button></p>
<div id="post_listing_E" class="inlineerror">!! SOME INFORMATION IS MISSING OR INCORRECT !!</div>
</form>
</div>

<!-- END FORM CONTENT -->~;

}
&footer($footerInject);
}


sub showListing{
my $listing_id = shift;
my $sth = $SBdb->prepare("SELECT p.lister, p.title, p.description, p.quantity, p.type, p.physical, p.category, p.trusted_only, p.terms, p.image, p.tags, p.lat, p.lon, p.send_ok, p.status, p.timestamp, p.rank, p.risk, m.badmail FROM posts AS p JOIN members AS m ON m.id = p.lister WHERE p.id = $listing_id AND (p.status = 'live' OR p.status = 'complete') LIMIT 1");


# my $sth = $SBdb->prepare("SELECT lister, title, description, quantity, type, physical, category, trusted_only, terms, image, tags, lat, lon, send_ok, status, timestamp, rank, risk FROM posts WHERE id = $listing_id AND (status = 'live' OR status = 'complete') LIMIT 1");


$sth->execute;
if ($sth->rows eq 1){
my ($lister, $title, $description, $quantity, $type, $physical, $category, $trusted_only, $terms, $imageRef, $tags, $lat, $lon, $send_ok, $status, $timestamp, $rank, $risk, $badmail) = $sth->fetchrow_array;
$sth->finish;

my $views = int($SBdb->do("SELECT id FROM interactions WHERE object_type = 'listing' AND object_id = $listing_id AND action = 'view'")) || 0;
my ($category_name, $transactable) = &getCategory($category);
my $when = &getWhen($timestamp);

# CREATE QUANTITY REQUEST SELECT
my $quantity_select;
if ($quantity > 1){
my $quantity_label;
if ($type eq 'offer'){$quantity_label = 'How many would you like?'};
if ($type eq 'request'){$quantity_label = 'How many can you offer?'};
$quantity_select .= qq~<label for="quantity">$quantity_label</label><select class="forminput" name="quantity" id="quantity" title="$quantity_label">~;
for (my $i = 1; $i <= $quantity; $i++){
$quantity_select .= qq~<option value="$i">$i</option>~;
}
$quantity_select .= qq~</select>~;
}

my $image;

my $responseText;
if ($transactable){
if ($type eq 'offer'){$responseText = 'REQUEST THIS ';}
else{$responseText = 'OFFER THIS ';}
# if ($physical eq 1){$responseText .= 'ITEM';}
# else{$responseText .= 'SKILL';}
}else{
$responseText = 'GET IN TOUCH';}
if (-e "$siteroot/listing_pics/$imageRef\.jpg"){
$image = qq~$baseURL/listing_pics/$imageRef\.jpg~;
}else{
$image = '';
}
my $listingLatLon = 'lat: ' . $lat . ', lng: ' . $lon;
my $headerInject = qq~
<script type="text/javascript">
var myListingLatLng = {$listingLatLon};
</script>
~;
my $footerInject = qq~
<!-- script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?v=3&key=AIzaSyD4zc3ELJ8ZgqLMZqLhLGv7beewD6wN9eU"></script -->
<script src="$baseURL/js/listing.js?v=$version"></script>
<script>\$('.listing-desc-container p, .listing-info-container p').linkify({target: "_blank"});</script>~;
my ($lister_first_name, $lister_last_name) = &getNames($lister);

my $tagS = &printDottedtags($tags);
my $location = &getRegion($lister);
$title = substr($description, 0, 70) . '...' if !$title;

&header($title, $description, $image, $headerInject, 'page');

my $quantity_desc;
if ($type eq 'offer'){$quantity_desc =  'offered';}
if ($type eq 'request'){$quantity_desc = 'needed';}
if ($terms eq 'free'){$terms = 'Free to keep'}
else{$terms = 'Loan only'};

$description =~ s/\r?\n/<br\/>/g if $description;

my $from_text;
if ($type eq 'offer'){$from_text = 'Offered by:'}
elsif ($type eq 'request'){$from_text = 'Requested by:'}

$title = '<span class="request notranslate">[REQ<span class="bigOnlyInline">UEST</span>]</span> ' . $title if ($type eq 'request');

print qq~<div class="disabled">~ if $status eq 'complete';
print qq~<h2>$title</h2>~;
print qq~<img src="$image" class="full-width-image"/>~ if ($image);
print qq~<div class="listing-info-container center">
<table class="listing-info-table">~;
if ($transactable){
print qq~<tr><td class="listing-info-icon"><i class="fas fa-cubes"></i></td><td>$quantity $quantity_desc</td></tr>~;
if ($physical){print qq~<tr><td class="listing-info-icon"><i class="far fa-hand-paper"></i></td><td>$terms</td></tr>~;}
}
print qq~
<tr><td class="listing-info-icon"><i class="fas fa-map-marker-alt"></i></td><td>$location</td></tr>~;
if ($physical && $transactable){
	my $send_legend;
	if ($type eq 'offer'){
	if ($send_ok){$send_legend = 'Delivery possible (see below)'}
	else{$send_legend = 'Collection only'}
	}else{
	if ($send_ok){$send_legend = 'Can pay delivery if required'}
	else{$send_legend = 'Will collect'}
	}
	print qq~
<tr><td class="listing-info-icon"><i class="fas fa-shipping-fast"></i></td><td>$send_legend</td></tr>~;}
print qq~
<tr><td class="listing-info-icon">~;
if ($trusted_only){
	print qq~<img src="$baseURL/i/shield-silver.png" class="badge" alt="Badge"/></td><td>Available to trusted members only</td>~;
}else{
	print qq~<img src="$baseURL/i/stripe_0.svg" class="badge" alt="Badge"/></td><td>Available to any member</td>~;
}
print qq~
</tr>
</table>
<p class="smallOnly">$description ($quantity $quantity_desc)</p>
<p class="smaller center">$from_text</p>~;

&getUserCard($lister);

print qq~
</div>
<div class="listing-desc-container"><p class="bigOnly clear top">$description ($quantity $quantity_desc)</p>
<p class="clear smaller">Posted in <a href="$baseURL/search?filter=cat_$category">$category_name</a> $when.~;
print qq~ Tags: $tagS.~ if $tagS;
print qq~ Viewed $views times.</p>~;

my $spamReports = int($SBdb->do("SELECT id FROM spam_reports WHERE object_type = 'listing' AND object_id = $listing_id"));

if ($myAdmin || $myModerator){
print qq~<div id="admin_listing_$listing_id">~, &adminBox('listing', $listing_id, $risk), qq~</div>~;
}

print qq~
</div>
<div id="listingMap"></div>
<input type="hidden" name="listingLat" id="listingLat" value="$lat"/>
<input type="hidden" name="listingLon" id="listingLon" value="$lon"/>~;
print qq~</div>~ if $status eq 'complete';


if ($LOGGED_IN){
if ($lister eq $myID){
# IF MINE, SHOW EDIT LINK
print qq~<p class="clear center"><a class="green-button" href="listing?a=edit&id=$listing_id">Edit listing</a></p>~;
}else{
# SHOW REPORT WARNING TO OTHER MEMBERS

print qq~<p class="center tiny"><i class="fas fa-exclamation-triangle red bigger"></i>&nbsp;Be careful! This listing has been reported by other members.</p>~ if $spamReports > 0;

# SHOW CONTACT FORM IF TRUST ENOUGH
# my $STRIPES = &getStripeLevel(&getTrustScore($myID));
if (&getStripeLevel(&getTrustScore($myID)) < $trusted_only && $type eq 'offer'){
	
	# NOT ENOUGH TRUST TO REQUEST OFFER
	print qq~<div class="empty-block"><p class="center bigger">Sorry, this listing has been restricted to <img src="$baseURL/i/shield-silver.png" class="badge" alt="Trust badge"/>&nbsp;Trusted Members only.</p>
<p class="center">Increase your trust score:</p>
<p class="center"><a class="green-button" href="$baseURL/post">POST AN OFFER</a> <a class="green-button" href="$baseURL/?search&filter=requests">FULFILL A REQUEST</a></p>
<p class="helper">Not sure what to offer? Try one of our <a href="$baseURL/page?id=templates">offer templates</a>.</p></div>~;
}elsif($badmail){
	
# EMAIL IS BLOCKED
print qq~<div class="empty-block"><p class="center bigger">Sorry, we are currently unable to contact this member due to an issue with their email.</p>
<p class="center"><a class="green-button" href="$baseURL/?search">BROWSE OTHER OFFERS</a></div>~;

}else{	print qq~
<form id="post_response" class="center top20">
<div class="response_hide">
<input type="hidden" name="a" value="send_response"/>
<input type="hidden" name="listing_id" value="$listing_id"/>~;
if ($transactable){print $quantity_select;}
my $placeholder = "Hi $lister_first_name!";
if ($transactable){
if ($type eq 'offer' && $physical){$placeholder .= ' Is this item still available?'}
if ($type eq 'offer' && !$physical){$placeholder .= ' Can you do this for me?'}
if ($type eq 'request' && $physical){$placeholder .= ' I think I have what you need.'}
if ($type eq 'request' && !$physical){$placeholder .= ' I think I can do this for you.'}
}
print qq~
<textarea name="listing_message" id="listing_message" class="forminput" placeholder="$placeholder"></textarea>~;
if ($physical && $transactable){
if ($type eq 'offer' && $send_ok){
print qq~
<p class="center"><span class="bold brand">SafePay:</span> $lister_first_name lives in $location. Would you like to offer shipping costs through SafePay?&nbsp;<input type="checkbox" onclick="toggleHide('payform');"/> <span class="smaller">(Recommended)</span></p><div class="pay-form hidden" id="payform"><p>Suggest an amount to cover delivery costs. $lister_first_name will only receive payment after you've confirmed delivery:</p><p class="center">Shipping cost: \$&nbsp;<input type="number" placeholder="0.00" name="shipping_cost" id="shipping_cost" min="0" max="301" step="0.01" title="Currency" pattern="^\d+(?:\.\d{1,2})?$" onblur="
this.parentNode.parentNode.style.backgroundColor=/^\d+(?:\.\d{1,2})?$/.test(this.value)?'inherit':'red'
" style="max-width:60px;"></p><p>If $lister_first_name agrees, we'll send you a link to complete payment via Paypal. (No account required)</p><p class="smaller">Note: If the item is not shipped you'll be refunded automatically.</p></div>~;
}
if ($type eq 'request' && $send_ok){
print qq~
<p class="center"><span class="bold brand">SafePay:</span> $lister_first_name lives in $location. Would you like to suggest shipping costs through SafePay?&nbsp;<input type="checkbox" onclick="toggleHide('payform');"/> <span class="smaller">(Recommended)</span></p><div class="pay-form hidden" id="payform"><p>Suggest an amount to cover delivery costs. Note, you will only receive payment after $lister_first_name has confirmed delivery:</p><p class="center">Shipping cost: \$&nbsp;<input type="number" placeholder="0.00" name="shipping_cost" id="shipping_cost" min="0" max="301" step="0.01" title="Currency" pattern="^\d+(?:\.\d{1,2})?$" onblur="
this.parentNode.parentNode.style.backgroundColor=/^\d+(?:\.\d{1,2})?$/.test(this.value)?'inherit':'red'
" style="max-width:60px;"></p><p>If $lister_first_name agrees, we'll send them a link to complete payment via Paypal. (You will need to have a Paypal account to receive the money, but you can create one later)</p><p class="smaller">Note: If you don't ship the item $lister_first_name will be refunded automatically.</p></div>~;
}
}

print qq~</div>~;
if (!$transactable){print qq~<p class="smaller center">This is a non-transactable listing, but you can still get in touch with <span class="notranslate">$lister_first_name</span>.</p>~;}
print qq~
<button class="green-button center" id="send_response">$responseText</button>
</form>~;
}
}
}else{
print qq~<p class="clear center"><button class="showLogin" href="javascript:void(0);" title="Log in to contact">Log in or register to respond to this listing</button></p>~;
}

&showSocial('listing', $listing_id, "$baseURL/listing?id=$listing_id");


&footer($footerInject);

&saveView('listing',$listing_id) if $lister != $myID;
}else{
&errorCatcher("This listing does not exist or may have expired.");
}
}



sub showAllListings{
&bounceNonLoggedIn('Please log in to view your listings.');

&header('My listings', 'My Sharebay listings', undef, undef, 'page');

print qq~<h2>My listings</h2>~;



my $sth = $SBdb->prepare("SELECT id, title, description, type, category, quantity, image, status FROM posts WHERE lister = '$myID' AND (status = 'live' OR status = 'complete') ORDER BY timestamp DESC");
$sth->execute;

if ($sth->rows > 0){


while(my($listing_id, $title, $description, $type, $category, $quantity, $imageRef, $status)= $sth->fetchrow_array){
$title = substr($description, 0, 50) . '...' if !$title;
my $image;
if ($imageRef){
$image = qq~$baseURL/listing_pics/$imageRef\_t.jpg~;
}else{
$image = qq~$baseURL/category_pics/cat$category\.jpg~;
}
print qq~
<a href="$baseURL/listing?id=$listing_id" title="$title">~;
$title = qq~<span class="request notranslate">REQUEST:</span> ~ . $title if ($type eq 'request');
print qq~
<div class="result~; if ($status ne 'live'){print qq~ greyed~;} print qq~">
<div class="result-image" style="background-image: url('$image');"></div>
<div class="result-location" title="Edit listings">~; if ($status eq 'live'){print qq~<a href="$baseURL/listing?id=$listing_id" title="View listing"><i class="far fa-eye"></i> VIEW</a>&nbsp;&nbsp;~;} print qq~<a href="$baseURL/listing?a=edit&id=$listing_id" title="Edit listing"><i class="far fa-edit"></i> ~; if ($status ne 'live'){print qq~RE-LIST~;} else{print qq~EDIT~;} print qq~</a>&nbsp;&nbsp;<a onclick="deleteListing($listing_id,document.URL);" href="javascript:void(0);" title="Delete listing"><i class="far fa-trash-alt"></i> DELETE</a></div>
<div class="result-info-container"><div class="result-info-text">~; if ($status ne 'live'){print qq~[COMPLETE] ~;} print qq~$title <span class="smallOnlyInline">&mdash; $description</span></div></div>
</div>
</a>~;
}

}else{
# NO LISTINGS FOUND
print qq~<p class="grey center">No listings posted yet. Why not create one? </p>~;}
print qq~<p class="center"><a class="green-button" href="post">Add a listing</a></p>~;
&footer;
}


$SBdb -> disconnect;
# Exeunt
