#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR CREATING, EDITING 
# AND DISPLAYING USER PROFILES

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );

require 'common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

;

if ($a){
# ACTION DEFINED
if ($a eq 'edit'){&editProfile;}
elsif ($a eq 'confirm'){&confirmAccount;}
elsif ($a eq 'showprofile'){&showProfile;}
elsif ($a eq 'invite'){&showInvite;}
elsif ($a eq 'newpassword'){&showNewPassword;}
elsif ($a eq 'wall'){&wall();}
elsif ($a eq 'new'){&signUp();}
elsif ($a eq 'login'){&hardLogIn();}
elsif ($a eq 'cleanemail'){&cleanEmail;}
elsif ($a eq 'unsubscribe_mailme'){&unsubscribe('mailme');}
elsif ($a eq 'unsubscribe_matchme'){&unsubscribe('matchme');}
elsif ($a eq 'deleteaccount'){&deleteAccount;}
}
if (!$a){
# NO ACTION DEFINED (QUICK URLS)

if ($FORM{id} && $FORM{auth}){&editProfile()} # FOR ONE STEP SIGN UPS
elsif ($FORM{id} && !$FORM{auth}){&showProfile()}
else{&signUp}; # START NEW OTHERWISE
}

sub unsubscribe{
my $unsub = shift;
my $authcode = $FORM{token};
my $title = "Unsubscribe $unsub";
&header($title, undef, undef, undef, 'page');

if ($authcode && ($unsub eq 'mailme' || $unsub eq 'matchme')){
if ($SBdb->do("UPDATE members SET $unsub = 0  WHERE $unsub = 1 AND authcode = '$authcode' LIMIT 1") eq 1){
print qq~<p class="success">You have successfully unsubscribed! You can re-subscribe to this list at any time from your <a href="$baseURL/edit">profile settings</a> page. Thank you.</p>~;
}else{
print qq~<p class="error">We couldn't unsubscribe you! You may have entered a wrong link or have already unsubscribed from this list. Try checking the subscription settings on your <a href="$baseURL/edit">profile settings</a>.</p>~;
}
}
&footer;
}



sub signUp{
if ($LOGGED_IN){
print "Location: $baseURL\n\n"; exit;
}else{
# ENTER EMAIL TO SIGN UP
my $title = "Join Sharebay";
my $desc = "Enter your email to join our amazing free sharing network.";
&header($title, $desc, undef, undef, 'page');
print qq~
<form id="signup" class="center">
<img class="full-width-image bottom20" src="$baseURL/i/nine-ways.jpg"/>
<h2>Hey! You're just one step away from accessing a world of free goods and services.</h2>
<input type="hidden" name="a" value="register"/>
<input type="hidden" name="invite" value="$FORM{invite}"/>
<input type="email" id="email" name="email" placeholder="Enter an email address" class="forminput"/>
<div id="email_E" class="inlineerror">! Please add a valid email address</div>
<input type="submit" name="submit" value="sign up" class="green-button"/>
<p class="center smaller">Already a member? <a class="showHomeLogin">Log in here</a>.</p>
</form>
~;
&bareFooter;
}
}


sub hardLogIn{
	&header(undef,undef,undef,undef,'page');
	&showLogin('home');
	&footer;
}


sub editProfile{
# CREATE NEW OR EDIT EXISTING PROFILE

my $hasData = 'false';
my $hasImage = '';
my ($id, $what_to_fetch, $first_name, $last_name, $email, $activated, $ac_type, $org_name, $org_desc, $street, $city, $region, $postcode, $country_iso, $myLat, $myLon, $phone, $imageRef, $tags, $about_me, $mailme, $badmail, $allow_contact, $matchme, $language, $auto_trans, $rows, $HP_id);


if ($FORM{token} || $LOGGED_IN){
# GET EXISTING DATA...

if ($LOGGED_IN){
# FOR AJAX CALLS, EDITING SELF
$what_to_fetch = qq~id = '$myID'~;
}

elsif ($FORM{token}){
# FOR NEW SIGN-UPS
$what_to_fetch = qq~activated = 0 AND authcode = '$FORM{token}'~;
}

my $sth = $SBdb->prepare("SELECT id, first_name, last_name, email, activated, ac_type, org_name, org_desc, street, city, region, postcode, country_iso, lat, lon, phone, image, tags, about_me, mailme, badmail, allow_contact, matchme, language, auto_trans, HP_id from members WHERE $what_to_fetch LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
($id, $first_name, $last_name, $email, $activated, $ac_type, $org_name, $org_desc, $street, $city, $region, $postcode, $country_iso, $myLat, $myLon, $phone, $imageRef, $tags, $about_me, $mailme, $badmail, $allow_contact, $matchme, $language, $auto_trans, $HP_id) = $sth->fetchrow_array;
$hasData = 'true' if $activated eq 1;
if (-e "$siteroot/user_pics/$imageRef\.jpg"){
$hasImage = $imageRef . '.jpg';
}
}else{
&errorCatcher('No data found! You might have clicked an old link or you may need to log in.');
}
}else{
&errorCatcher('Nothing to see here! Maybe you typed the wrong URL or you need to log in?');
}

if ($hasData eq 'false' || $myLat eq ''){
# GET GEO LOCATION FROM IP IF NEW PROFILE
($myLat, $myLon, $city, $region, undef, $country_iso) = &getCurrentLocation;
}

# BUILD COUNTRY LIST
my $countries;
my $coSelect = $SBdb->prepare("SELECT iso, country FROM countries ORDER BY country");
$coSelect->execute();
$countries = qq~<option value="">select a country...</option>~;
while (my ($iso, $countryName) = $coSelect->fetchrow_array){
$countries .= qq~<option value="$iso"~;
$countries .= qq~ selected~ if ($iso eq $country_iso);
$countries .= qq~>$countryName</option>~;
}
$coSelect->finish;

# BUILD LANGUAGE LIST
my $languages;
my $langSelect = $SBdb->prepare("SELECT iso, language FROM languages ORDER BY language");
$langSelect->execute();
while (my ($iso, $langName) = $langSelect->fetchrow_array){
$languages .= "<option value=\"$iso\">$langName</option>";
}
$langSelect->finish;
if ($language){
$languages =~ s/value=\"$language\"/value=\"$language\" selected/;
}else{
$languages =~ s/value=\"en\"/value=\"en\" selected/;
}


# CREATE PAGE
my $title = "Join Sharebay";
my $desc = "Register here to join the world's largest free sharing network - connecting free people, skills and things.";
if ($hasData eq 'true'){
$title = "Edit profile and settings";
$desc = "Edit your profile information, photo and settings.";
}


my $headerInject = qq~
<link rel="stylesheet" href="$baseURL/css/jquery-ui.css">
<link rel="stylesheet" href="$baseURL/css/jquery.tagit.css">
<link href="$baseURL/slim/slim.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css?family=Merriweather" rel="stylesheet">
<script type="text/javascript">
var myLatLng = {lat: $myLat, lng: $myLon};
var hasData = $hasData;
var hasImage = '$hasImage';
</script>~;

my $footerInject = qq~
<script src="https://ajax.googleapis.com/ajax/libs/jqueryui/1.12.1/jquery-ui.min.js"></script>
<script src="$baseURL/js/tag-it.js?v=$version"></script>
<script src="$baseURL/slim/slim.jquery.js?v=$version"></script>
<!-- script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?v=3&key=AIzaSyD4zc3ELJ8ZgqLMZqLhLGv7beewD6wN9eU"></script -->
<script src="$baseURL/js/profile.js?v=$version"></script>
~;

&header($title, $desc, undef, $headerInject, 'page');

print qq~<div id="register">~;

if ($hasData eq 'true'){
print qq~<h2 class="center">Edit profile and settings</h2>~;
}else{
print qq~<h2 class="center">Create your Sharebay profile</h2>~;
}

print qq~

<div id="rForm">

<!-- Begin form -->
<form name="profile" id="profile">
<input type="hidden" name="a" value="saveprofile"/>
<input type="hidden" name="good2go" value=""/>
<input type="hidden" name="id" value="$id"/>
<input type="hidden" name="hasData" value="$hasData"/>~;
if ($hasData eq 'true'){
print qq~
<input type="hidden" name="hasImage" value="$hasImage"/>~;
}
print qq~
<input type="hidden" name="image" value=""/>

<label for="profilePic" class="inputrequired">Add a profile picture</label>
<input type="file" id="profilePic" class="forminput"/>

<label for="first_name" class="inputrequired">First name:</label>
<input type="text" id="first_name" name="first_name" class="forminput" value="$first_name"/>
<div id="first_name_E" class="inlineerror">! Please add your first name</div>

<label for="last_name" class="inputrequired">Last name:</label>
<input type="text" id="last_name" name="last_name" class="forminput" value="$last_name"/>
<div id="last_name_E" class="inlineerror">! Please add a last name</div>

<div class="hidden">

<p>Choose if your Sharebay account is for personal use or on behalf of a group or organisation:</p>

    <div id="ac_type" class="buttons">
      <input type="radio" id="individual" name="ac_type" value="1" ~; if (!$ac_type || $ac_type eq 1){print qq~checked="checked"~;}print qq~/><label for="individual" title="For personal use">Individual</label><br/>
 
      <input type="radio" id="organisation" name="ac_type" value="2" ~; if ($ac_type eq 2){print qq~checked="checked"~;}print qq~/><label for="organisation" title="For organisations or groups">Organisation or group</label>
    </div>
	<div id="ac_type_E" class="inlineerror">! You must select an account type</div>

</div>

<div id="group_opts" class="hidden">
<label for="org_name" class="inputrequired">Name of organisation:</label>
<input type="text" id="org_name" name="org_name" class="forminput" value="$org_name"/>
<div id="org_name_E" class="inlineerror">! Please add the name of your organisation</div>

<label for="org_desc" class="inputoptional">What does your organisation do?</label>
<input type="text" id="org_desc" name="org_desc" class="forminput" value="$org_desc"/>
</div>

<label for="email" class="inputrequired disabled">Email address: <span class="smaller">(can't be changed)</span></label>~;

if ($hasData eq 'true' && $badmail > 0){
print qq~<p id="unblockMessage" class="error">Your email address '$email' has been blocked because we've been unable to send mail to that address. This means we can't alert you to requests and offers from other members.<br/><br/>To unblock your email, please <a href="javascript:void(0);" onclick="unblockEmail($id);" title="Send unblocking link">click here</a> and we'll send you a link to unblock it. (If you've tried this and it doesn't work, please <a href="$baseURL/contact">contact us</a> and we'll fix it for you)</p>~;
}

print qq~
<input type="email" id="email" name="email" class="forminput~; if ($hasData eq 'false'){print qq~ disabled~;}
print qq~" title="Your email is never made public." value="$email"/>
<div id="email_exists_E" class="inlineerror">! Email address already exists</div>
<div id="email_E" class="inlineerror">! Please add a valid email address</div><label for="password" ~; if ($activated eq 1){print qq~ class="inputoptional">Change your password:~;}else{print qq~ class="inputrequired">Choose a password:~;}print qq~</label>
<input type="password" id="password" name="password" class="forminput" ~; if ($activated eq 1){print qq~placeholder="PASSWORD ON FILE"~;}print qq~/>
<div id="password_E" class="inlineerror">! Please set your password</div>~;

if ($hasData eq 'true'){
print qq~
<label for="street" class="inputoptional">Street address: <span class="smaller">(Optional, private)</span><div class="tooltip" onclick="openModal('<h2>Info</h2><p>We may require your street address to arrange collection or deliveries, but will never publish this information.</p>');"></div></label>
<input type="text" id="street" name="street" class="forminput" title="Your street address is private by default." value="$street"/>
<div id="street_E" class="inlineerror">! Please enter a street address</div>~;
}

print qq~
<label for="city" class="inputrequired">City:</label>
<input type="text" id="city" name="city" class="forminput" value="$city"/>
<div id="city_E" class="inlineerror">! Please add your city or town</div>

<label for="region" class="inputrequired">State / Region:</label>
<input type="text" id="region" name="region" class="forminput" value="$region"/>
<div id="region_E" class="inlineerror">! Please add your region or state</div>~;


if ($hasData eq 'true'){
print qq~
<label for="postcode" class="inputoptional">Post/Zip code: <span class="smaller">(Optional, private)</span><div class="tooltip" onclick="openModal('<h2>Info</h2><p>We may require your post or ZIP code to arrange collection or deliveries, but will never publish this information.</p>');"></div></label>
<input type="text" id="postcode" name="postcode" class="forminput" value="$postcode"/>
<div id="postcode_E" class="inlineerror">! Please enter a ZIP / postcode</div>~;
}

print qq~
<label for="country" class="inputrequired">Country:</label>
<select id="country" name="country" class="forminput">
$countries
</select>
<div id="country_E" class="inlineerror">! Please select a country</div>~;


if ($hasData eq 'true'){
print qq~
<label for="phone" class="inputoptional">Phone number, including country code: <span class="smaller">(Optional, private)</span><div class="tooltip" onclick="openModal('<h2>Info</h2><p>We may need your phone number to arrange collection or deliveries, but will never phone you or give your number away.</p>');"></div></label>
<input type="text" id="phone" name="phone" class="forminput" title="Your phone number is private by default." value="$phone" placeholder="eg. +44 123 4567"/>
<div id="phone_E" class="inlineerror">! Please enter a phone number</div>~;
}

print qq~
<label for="gMap" class="inputrequired">Set your map location: (approximate location is sufficient)<div class="tooltip" title="Drag the red marker to your location. (An approximate location is sufficient)"></div></label>
<div id="gMap"></div>
<input type="hidden" name="lat" id="lat" value="$myLat"/>
<input type="hidden" name="lon" id="lon" value="$myLon"/>
<div id="gMap_E" class="inlineerror">! Please set your location</div>

<div id="personal">
	
<h3>About you</h3>

<label for="about_me" class="inputoptional">About me: <span class="smaller">(optional)</span><div class="tooltip" title="Add an optional about_me. This will be publicly visible on your profile page. Use 'http:' to add links."></div></label>
<textarea name="about_me" class="forminput" placeholder="Tell us about yourself...">$about_me</textarea>

<label for="tags" class="inputoptional">What words describe you, your skills, interests, lifestyle and views?</label>
<span class="smaller italic">eg. "photographer, vegetarian, Metallica, history, walking, Salvador Dali, libertarian."</span>
<ul id="tags" class="forminput notranslate">~;
my @tags = split(',',$tags);
my $tags;
for (@tags){$tags .= '<li>' . $_ . '</li>'};
print qq~
$tags</ul>
<div id="tags_too_few_E" class="inlineerror">! Please enter at least five tags</div>
<div id="tags_too_long_E" class="inlineerror">! tags cannot exceed 25 characters. Please use only single words or short phrases</div>

<label for="language" class="inputrequired">Preferred language:</label>
<select id="language" name="language" class="forminput">
$languages
</select>
<div id="language_E" class="inlineerror">! Please select a language</div>

<h3>Connect to HonorPay<div class="tooltip" title="HonorPay is a free, independent service."></div></h3>
<div id="honorpay-connect" class="forminput">
<p class="smaller"><input type="checkbox" id="connect_HP" name="connect_HP" value="1" ~; 

print qq~checked="checked"~ unless ($LOGGED_IN && !$HP_id);

print qq~/>&nbsp;<span class="bold">Connect to <a href="https://honorpay.org" target="_blank" title="Visit HonorPay">HonorPay?</a></span> (~;

if ($HP_id){
print qq~You are already connected~;
}else{
print qq~recommended~;
}

print qq~)</p><p class="smaller">
HonorPay is a free, independent awards network where people can show their appreciation of others. If you already have an HonorPay account, we’ll try and connect you. If not, we'll create one for you.</p>~;

if ($LOGGED_IN && $HP_id){
print qq~<p class="smaller"><a href="https://honorpay.org/?profile=$HP_id" title"My HonorPay profile" target="_blank"><span class="honoricon"></span>View HonorPay profile</a></p>~;
}

print qq~</div>~;

print qq~
<h3>Settings</h3>
<div id="settings">
	<table align="center" cellspacing="20" style="border:none;font-size:90%;text-align:left;">
	<tr>
	<td>Translate site into my language (via Google Translate)</td>
	<td width="60" valign="top">
	<input type="checkbox" name="auto_trans" value="1" class="fancy" data-on-value="YES" data-off-value="NO" ~; 
	if ($auto_trans eq 1){print qq~checked="true"~;}print qq~/>
	</td>
	</tr>
	<tr>
	<td>Receive digest of listings that match my interests</td>
	<td width="60" valign="top">
	<input type="checkbox" name="matchme" value="1" class="fancy" data-on-value="YES" data-off-value="NO" ~; 
	unless ($matchme eq 0){print qq~checked="true"~;}print qq~/>
	</td>
	</tr>
	<tr>
	<td>Receive occasional newsletters and updates</td>
	<td width="60" valign="top">
	<input type="checkbox" name="mailme" value="1" class="fancy" data-on-value="YES" data-off-value="NO" ~; 
	unless ($mailme eq 0){print qq~checked="true"~;}print qq~/>
	</td>
	</tr>
	<tr>
	<td>Allow other members to contact me (NB. members will still be able to contact you via your listings)</td>
	<td width="60" valign="top">
	<input type="checkbox" name="allow_contact" value="1" class="fancy" data-on-value="YES" data-off-value="NO" ~; 
	unless ($allow_contact eq 0){print qq~checked="true"~;}print qq~/>
	</td>
	</tr>
	</table>~;
	
if ($LOGGED_IN){
	# GET BLOCKED PROFILES IF ANY

my $getBlocked = $SBdb->prepare("SELECT b.blocked_id, m.first_name, m.last_name FROM member_blocks b LEFT JOIN members m ON b.blocked_id = m.id WHERE b.blocker_id = '$myID'");
$getBlocked->execute;
if ($getBlocked->rows > 0){
	print qq~<p class="smaller center">Members currently blocked (click to unblock):<br/>~;
while (my ($blocked_id, $blocked_first_name, $blocked_last_name) = $getBlocked->fetchrow_array){
	print qq~<a onclick="unblock($blocked_id);" href="javascript:void(0);">$blocked_first_name $blocked_last_name</a>&nbsp;~;
}
print qq~</p>~;
}
	
print qq~
	<p class="smaller center"><a href="javascript:void(0);" class="logoutall">Log out of all devices</a></p>
	<p class="smaller center"><a href="javascript:void(0);" onclick="deleteAccount('$myName');">Delete my account</a></p>
~;
}	
print qq~	
	</div>
	
<div class="pledge"~; if ($LOGGED_IN){print qq~ title="You can't change this setting"~;}print qq~><p id="pledge"><input type="checkbox" id="pledge_box" name="pledge_box" value="agree" ~; if ($LOGGED_IN){print qq~checked="checked" class="disabled" title="You can't change this setting"~;}print qq~/>&nbsp;I agree to use this site honourably, for the purpose of sharing goods and services freely with other Sharebay members in accordance with the <a href="javascript:void(0);" onclick="openModal('$baseURL/page?id=terms-of-service&isModal=1');">Terms of Service</a>.</p>
</div>
<div id="pledge_E" class="inlineerror">! You must agree to this to register</div>


<p class="center clear"><button id="save_profile" name="save_profile" value="register" class="green-button submit">~;

if ($hasData eq 'true'){
print qq~SAVE~;
}else{
print qq~CREATE ACCOUNT~;
}

print qq~</button></p>
<div id="save_profile_E" class="inlineerror">!! SOME INFORMATION IS MISSING OR INCORRECT !!</div>
</form>
</div></div></div>
<!-- END FORM CONTENT -->~;

&footer($footerInject);
}


sub showProfile{
# DISPLAY ANY USER PROFILE
my $profile_id = $FORM{id};

if ($LOGGED_IN){
my $blocked = &getBlockedIds;
my @array = join(',', $blocked);
if (grep(/^$profile_id$/, @array)){
$profile_id = '';
}
}


if (!$profile_id){
&errorCatcher('Sorry, no such page exists, or you might not have permission to view it.');
}

my $sth = $SBdb->prepare("SELECT m.first_name, m.last_name, m.activated, m.city, m.region, m.country, m.lat, m.lon, m.image, m.tags, m.about_me, m.allow_contact, m.badmail, m.last_active, m.gifted, m.trust_score, m.badge_level, m.ip, m.HP_id, m.is_founder, m.is_moderator, m.is_author, m.is_admin, m.joined, m.risk, IFNULL(SUM(CASE WHEN m.id = t.giver_id AND t.status = 'delivered' THEN 1 END), 0) AS gave, IFNULL(SUM(CASE WHEN m.id = t.getter_id AND t.status = 'delivered' THEN 1 END), 0) AS got FROM members AS m LEFT JOIN transactions AS t ON m.id = t.giver_id OR m.id = t.getter_id WHERE m.id = $profile_id AND activated = 1 GROUP BY m.first_name, m.last_name LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
# SHOW PROFILE
my ($first_name, $last_name, $activated, $city, $region, $country, $myLat, $myLon, $imageRef, $tags, $about_me, $allow_contact, $badmail, $last_active, $gifted, $trust_score, $badge_level, $ip_address, $HP_id, $is_founder, $is_moderator, $is_author, $is_admin, $joined, $risk, $gave, $got) = $sth->fetchrow_array;
my $honors = &getHonors($HP_id);
my $title = "$first_name $last_name";
my $desc = "$first_name $last_name is on Sharebay.org";

my $joinedWhen = &getWhen($joined);
$last_active = &getWhen($last_active);

my ($stripe_1, $stripe_2, $stripe_3, $offers_max, $gave_max, $got_max, $trust_max) = &getAverages;

my $image;
my $hasImage = 1 if (-e "$siteroot/user_pics/$imageRef\.jpg");
if ($hasImage){
$image = qq~$baseURL/user_pics/$imageRef\.jpg~;
}else{
$image = '';
}

my $headerInject = qq~
<script type="text/javascript">
var myLatLng = {lat: $myLat, lng: $myLon};
</script>
~;

my $footerInject = qq~
<!-- script src="https://maps.googleapis.com/maps/api/js?v=3&key=AIzaSyD4zc3ELJ8ZgqLMZqLhLGv7beewD6wN9eU"></script -->
<script>

        var map = new google.maps.Map(document.getElementById('gMap'), {
            zoom: 8,
            center: myLatLng
        });

        var marker = new google.maps.Marker({
            position: myLatLng,
            map: map,
            draggable: false,
        });
		
\$('.about-me').linkify({target: "_blank"});
</script>~;
my $status;
if ($is_founder){
	$status .= qq~<a class="view-status" href="javascript:void(0);" onclick="openModal('<h2><i class=\\'fas fa-landmark\\'></i>&nbsp;&nbsp;Longtime Member</h2><p>$first_name $last_name has been an active participant in Sharebay since our first prototype in 2017, and is recognised as a longtime member.</p>');"><i class="fas fa-landmark"></i> LONGTIME MEMBER</a>~;}
if ($is_moderator){
	if ($status){$status .= ', ';}
		$status .= qq~<a class="view-status" href="javascript:void(0);" onclick="openModal('<h2><i class=\\'fa-solid fa-scale-balanced\\'></i>&nbsp;&nbsp;Moderator</h2><p>$first_name $last_name is a site moderator.</p>');"><i class="fa-solid fa-scale-balanced"></i> MODERATOR</a>~;
		}
if ($is_author){
	if ($status){$status .= ', ';}
		$status .= qq~<a class="view-status" href="javascript:void(0);" onclick="openModal('<h2><i class=\\'fa-solid fa-pen-nib\\'></i>&nbsp;&nbsp;Author</h2><p>$first_name $last_name is a site author.</p>');"><i class="fa-solid fa-pen-nib"></i> AUTHOR</a>~;
		}
if ($is_admin){
	if ($status){$status .= ', ';}
		$status .= qq~<a class="view-status" href="javascript:void(0);" onclick="openModal('<h2><i class=\\'fas fa-tools\\'></i>&nbsp;&nbsp;Admin</h2><p>$first_name $last_name is an admin of this site.</p>');"><i class="fas fa-tools"></i> ADMIN</a>~;
		}

&header($title, $desc, $image, $headerInject, 'page');

# PROFILE BODY
my $tags = &printDottedtags($tags);
my $LOCATION = &printLocation($city, $region, $country);

my $spamReports = int($SBdb->do("SELECT id FROM spam_reports WHERE object_type = 'profile' AND object_id = $profile_id"));


print qq~<div class="center">~;

if ($hasImage){
print qq~<img src="$image" class="profile-image" title="$first_name $last_name"/>~;
}
print qq~<div class="profile-name notranslate">
<h2 class="center">$first_name $last_name~;
&printBadge($first_name, $badge_level);
if ($HP_id && $honors){
	print qq~&nbsp;<a class="honors" title="See $first_name\'s HonorPay record" href="https://honorpay.org/?profile=$HP_id" target="_blank"><span class="honoricon"></span>$honors</a>~;
}
	
if ($status){print qq~<div class="status">$status</div>~;}

print qq~</h2>
$LOCATION<br/>~;
if ($activated){

my $offers = int($SBdb->do("SELECT id FROM posts WHERE lister = $profile_id AND status = 'live' AND type = 'offer'")) || 0;

my ($trust_width, $gave_width, $got_width, $offers_width);
if ($trust_score > 0){$trust_width = ($trust_score / $trust_max) * 100;}
else {$trust_width = 0;}

if ($gave > 0){$gave_width = ($gave / $gave_max) * 100;}
else{$gave_width = 0;}

if ($got > 0){$got_width = ($got / $got_max) * 100;}
else{$got_width = 0;}

if ($offers > 0){$offers_width = ($offers / $offers_max) * 100;}
else{$offers_width = 0;}


print qq~
<table class="reputation-table">
<tr title="$first_name has a trust score of $trust_score">
<td>TRUST</td><td><div class="reputation-box"><div class="reputation-bar" style="width:$trust_width\%;background:#2e3192;"></div></div></td><td>($trust_score)</td>
</tr>
<tr title="$first_name has given $gave times">
<td>GAVE</td><td><div class="reputation-box"><div class="reputation-bar" style="width:$gave_width\%;background:green;"></div></div></td><td>($gave)</td>
</tr>
<tr title="$first_name has received $got times">
<td>GOT</td><td><div class="reputation-box"><div class="reputation-bar" style="width:$got_width\%;background:red;"></div></div></td><td>($got)</td>
</tr>
<tr title="$first_name has $offers live offers">
<td>OFFERS</td><td><div class="reputation-box"><div class="reputation-bar" style="width:$offers_width\%;background:#c61e59;"></div></div></td><td>($offers)</td>
</tr>
</table>
<!-- div id="meet"></div>
<script src='https://meet.jit.si/external_api.js'></script>

<script>
const video_service = 'meet.jit.si';
const options = {
    roomName: 'Sharebay-meeting',
    width: 700,
    height: 700,
    parentNode: document.querySelector('#meet')
};
const api = new JitsiMeetExternalAPI(video_service, options);
</script -->
~;

my $star_rating = &showStars($profile_id);
print qq~<p class="center smaller">$star_rating</p>~;

if ($LOGGED_IN){
if (($gave + $got) > 0){
print qq~<p class="center smaller"><a href="$baseURL/transactions?id=$profile_id" title="View $first_name $last_name\'s Transaction Record">View $first_name\'s Transaction Record</a></p>~;
}else{
print qq~<p class="grey center smaller">$first_name hasn't made any transactions yet.</p>~;
}
print qq~<p class="grey center smaller">Joined $joinedWhen.<br/>Last active: $last_active.</p>~ if $last_active;
}
if ($SBdb->do("SELECT id FROM posts WHERE lister = '$profile_id'") > 0){
print qq~<p class="grey center smaller"><a href="$baseURL/?search&filter=member_$profile_id" title="Browse $first_name $last_name\'s listings">Browse $first_name\'s listings</a></p>~;
}else{
print qq~<p class="grey center smaller">$first_name hasn't listing anything yet.</p>~;
}

if ($myAdmin || $myModerator){
print qq~<div id="admin_profile_$profile_id">~, &adminBox('profile', $profile_id, $risk), qq~</div>~;
}


if ($HP_id && ($profile_id ne $myID)){
print qq~<p class="center"><a class="honor-button notranslate" href="https://honorpay.org/?award=$HP_id" title="Award an Honor to $first_name $last_name (opens in new window)" target="_blank"><span class="honoricon"></span>Honor $first_name</a></p>~;
}
}else{
print qq~<p class="smaller center disabled">(Unactivated Member)</p>~;
}

print qq~</div></div>~;

if ($about_me){
	$about_me =~ s/\r?\n/<br\/>/g;
	print qq~<h3>About me</h3><p class="about-me">$about_me</p>~;}

print qq~<p class="smaller clear">Tags: $tags</p>~;
if ($myAdmin || $myModerator){
	print qq~<div id="gMap"></div>~;
}

#### SOCIAL COMPONENT

&showSocial('profile', $profile_id, "$baseURL/profile?id=$profile_id");

#### MY LISTINGS ####

my $getListings = $SBdb->prepare("SELECT id, title, description, type, category, quantity, image, status FROM posts WHERE lister = $profile_id AND status = 'live' ORDER BY timestamp DESC");
$getListings->execute;

if ($getListings->rows > 0){
print qq~<h3><span class=notranslate">$first_name\'s</span> current listings</h3>~;



while(my($listing_id, $title, $description, $type, $category, $quantity, $imageRef, $status)= $getListings->fetchrow_array){
my $image;
$title = substr($description, 0, 50) . '...' if !$title;
if ($imageRef){
$image = qq~$baseURL/listing_pics/$imageRef\_t.jpg~;
}else{
$image = qq~$baseURL/category_pics/cat$category\.jpg~;
}
print qq~
<a href="$baseURL/listing?id=$listing_id" title="$title">~;
$title = qq~<span class="request notranslate">REQUEST:</span> ~ . $title if ($type eq 'request');
print qq~
<div class="result">
<div class="result-image" style="background-image: url('$image');"></div>~;
if ($profile_id eq $myID){
print qq~
<div class="result-location" title="Edit listings"><a href="$baseURL/listing?id=$listing_id" title="View listing"><i class="far fa-eye"></i> VIEW</a>&nbsp;&nbsp;<a href="$baseURL/listing?a=edit&id=$listing_id" title="Edit listing"><i class="far fa-edit"></i> EDIT</a>&nbsp;&nbsp;<a onclick="deleteListing($listing_id,document.URL);" href="javascript:void(0);" title="Delete listing"><i class="far fa-trash-alt"></i> DELETE</a></div>~;
}
print qq~
<div class="result-info-container"><div class="result-info-text">$title <span class="smallOnlyInline">&mdash; $description</span></div></div>
</div>
</a>~;
}


print qq~<p class="helper italic">Note: To enquire about one of <span class="notranslate">$first_name\'s</span> listings, please use the form on the listing page, otherwise your transaction may not be recorded.</p>~;
}

#### END LISTINGS ####


if ($LOGGED_IN){

if ($profile_id eq $myID){
# IF ME, SHOW EDIT LINK
print qq~<p class="center"><a href="$baseURL/edit" class="green-button"">Edit profile</a></p>~;
}else{

print qq~<p class="center tiny"><i class="fas fa-exclamation-triangle red bigger"></i>&nbsp;Be careful! This profile has been reported by other members.</p>~ if $spamReports > 0;

if ($allow_contact eq 1 && $badmail < 2){

# OK TO CONTACT
print qq~
<form id="post_message" class="center">
<div class="response_hide">
<input type="hidden" name="a" value="send_message"/>
<input type="hidden" name="to" value="$profile_id"/>
<textarea name="message" id="message" class="forminput" placeholder="Send a message to $first_name $last_name"></textarea>
</div>
<button class="green-button" id="send_message">Contact <span class="notranslate">$first_name</span></button>
</form>~;
}else{
# NO CONTACT
print qq~<p class="disabled center">CONTACT NOT POSSIBLE AT THIS TIME</p>~;
}
}
}else{
print qq~<p class="center"><a class="showLogin" href="javascript:void(0);" title="Log in to send a message to $first_name">Log in to send a message to <span class="notranslate">$first_name</span></a></p>~;
}

if ($LOGGED_IN && $profile_id ne $myID){
print qq~<p class="center tiny grey"><a class="grey" onclick="report('profile', $profile_id);" href="javascript:void(0);">Report this profile</a> | <a class="grey" onclick="block($profile_id);" href="javascript:void(0);">Block this member</a></p>~;
}
&footer($footerInject);
&saveView('profile',$profile_id) if $profile_id != $myID;
}else{
# NO PROFILE FOUND
&errorCatcher("Sorry, no such profile exists.");
}
}

sub showNewPassword{
&header('Reset password', undef, undef, undef, 'page');

if ($FORM{id} && $FORM{auth}){
print qq~
<form id="reset-pw">
<h2>Change your password</h2>
<input type="hidden" name="id" value="$FORM{id}"/>
<input type="hidden" name="auth" value="$FORM{auth}"/>
<label for="password1" class="inputrequired">Enter a new password:</label>
<input type="password" class="forminput" name="password1" id="password1"/>
<label for="password2" class="inputrequired">Retype password:</label>
<input type="password" class="forminput" name="password2" id="password2"/>
<button id="setNewPassword" class="blue-button">SET NEW PASSWORD</button><br/>
<span class="inlineerror" id="resetError">! Passwords don't match</span>
</form>
<div class="success" style="display:none;">Password reset complete. Logging you back in...</div>
<div class="error" style="display:none;">There was a problem with your request. Please try again later.</div>~;
}else{
print qq~<div class="error">Sorry, something went wrong. Invalid link.</div>~;
}
&footer;
}



sub wall{
my $title = "The Sharebay Wall - see who's here!";
my $description = "See who's here and ready to create a free world! Check out all our members at a glance.";
my $image = "$baseURL/i/sharebay-wall.jpg";
&header($title, $description, $image, undef, 'screen');
my $sth = $SBdb->prepare("SELECT id, first_name, last_name, region, country, image, tags, HP_id FROM members WHERE activated = 1 ORDER BY RAND()");
$sth->execute;
my $count = $sth->rows;
while(my($id, $first_name, $last_name, $region, $country, $imageRef, $tags, $HP_id) = $sth->fetchrow_array){
$tags = &printtags($tags);
if ($LOGGED_IN){print qq~<a href="$baseURL/profile?id=$id" target="_blank">~;}
print qq~
<img src="$baseURL/user_pics/$imageRef\_t.jpg" title="$first_name $last_name, $region, $country, [$tags]" class="mosaic"/>~;
if ($LOGGED_IN){print qq~</a>~;}
} 
$sth->finish;

&footer;
}


sub confirmAccount{
&header('Welcome to Sharebay!', undef, undef, undef, 'page');
## GET EMAIL ADDRESS WHILE CHECKING EXISTENCE
my $sth = $SBdb->prepare("SELECT first_name, email FROM members WHERE id = '$FORM{id}' AND authcode = '$FORM{token}' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
my $activate = $SBdb->do("UPDATE members SET activated = 1 WHERE id = '$FORM{id}' LIMIT 1");
my ($first_name, $email) = $sth->fetchrow_array;
my ($to, $from, $subject, $name, $body, $call2act, $link);
$to = $email;
$from = $admin;
$subject = 'Welcome to Sharebay!';
$name = $first_name;
$body = "Thank you for registering and welcome to Sharebay: the world's first truly free sharing network! No exchange. No credits. No barter. Just everyone sharing their excess items and skills!\n\nCan you imagine the power of free, unconditional sharing, mulitplied by millions and billions of people? What kind of world would that be?\n\nCan you imagine the problems we could solve if we didn't need to trade in order to survive?\n\nCan you imagine if the only thing that governed people's behaviour was not the money they had nor the laws they obeyed, but rather the knowledge, respect and appreciation they had for each other and their environment?\n\nThis is why we built Sharebay.org - to facilitate online what we all do every day - except to bring that trust outside our immediate circles, friends and family and around the world\n\nWe are changing the world in baby steps. Today, we can share our small excess items, skills and knowledge easily. Soon we will build enough trust and confidence in the idea of unconditional sharing, that we can begin to truly re-organise our society for the mutual benefit of all.\n\nWelcome to the world's first free-sharing network!\n\nThe Sharebay Team";
$call2act = 'SEARCH AND LOG IN';
$link = $baseURL . '/search';

&sendMail($to, $from, $subject, $name, $body, $call2act, $link, undef, undef);
print qq~
<h2>Thank you and welcome!</h2><p>Your Sharebay account has now been activated.</p><p>Please log in, take a look around and post some listings!</p>~;
&showLogin;
&syncHonorPay("$FORM{id}","$email");
}else{
print qq~<p class="error">There was a problem with your request. Perhaps a wrong link or this account has previously been activated?</p>~;
}
&footer;
}

sub cleanEmail{
# RESET BADMAIL TO 0
if ($FORM{id} && $FORM{auth}){
my $result = $SBdb->do("UPDATE members SET badmail = 0 WHERE id = $FORM{id} AND authcode = '$FORM{auth}'");
if ($result ne 1){
&errorCatcher("No such record found. Error 216");
}else{
&header('Email confirmed!', undef, undef, undef, 'page');
print qq~<p class="success">Your email is now unblocked, thank you.</p>~;
&footer();
}
}else{
&errorCatcher("Can't process request. Error 217");
}
}


sub deleteAccount{
if ($LOGGED_IN && $myID){
my $checkMember = $SBdb->do("SELECT id FROM members WHERE id = '$myID' LIMIT 1");
if ($checkMember eq 1){
my $delMember = $SBdb->do("DELETE FROM members WHERE id = '$myID' LIMIT 1");
my $delMessages = $SBdb->do("DELETE FROM messages WHERE sender = $myID");
my $delListings = $SBdb->do("DELETE FROM posts WHERE lister = '$myID'");
my $delListings = $SBdb->do("DELETE FROM activity WHERE actor_id = '$myID'");
my $cancelPendingTransactions = $SBdb->do("UPDATE transactions SET status = 'auto-cancelled' WHERE (giver_id = '$myID' OR getter_id = '$myID') AND status != 'delivered'");
&deleteActivity('profile', $myID);

# DELETE PROFILE PICS
unlink glob("$siteroot/user_pics/$myID\_*.jpg");

# LOG OUT
use CGI;
my $cgi = new CGI;
my $SESSION_ID = $cgi->cookie('SESS_ID');
if (-e "$root/sessions/$SESSION_ID"){
unlink ("$root/sessions/$SESSION_ID");
}
print qq~Set-Cookie: SESS_ID=trash; expires=Thu, 1 Jan 1970 00:00:00 GMT; domain=sharebay.org; path=/;\nSet-Cookie: SESS_ID=trash; expires=Thu, 1 Jan 1970 00:00:00 GMT; domain=www.sharebay.org; path=/;\n~;
$LOGGED_IN = 0;

&header('Account successfully deleted!', undef, undef, undef, 'page');
print qq~<p class="success">All your account data, listings and messages have been successfully removed from our system.</p>~;
&footer();
}else{
&errorCatcher("No such account!");
}
}else{
&errorCatcher("You need to be logged in to delete your account.");
}
}




$SBdb -> disconnect;
# Exeunt
