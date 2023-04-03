#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR HANDLING INLINE AJAX REQUESTS

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );


require 'common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

# FOR FORMATTING RESPONSES
my @data; ##For returning JSON data
my $response; ##For text response data

my $imgTempDir = "$siteroot/slim/tmp";


if ($a eq 'register'){
### PROCESS EMAIL SIGN-UP
&htmlHeader;
my $email = &textFormat($FORM{email});
## CHECK TO SEE IF EXISTS
my $check = $SBdb->prepare("SELECT activated FROM members WHERE email like '$email'");
$check->execute;
if ($check->rows > 0){
my $is_activated = $check->fetchrow_array();
if ($is_activated eq 1){
## ALREADY A MEMBER
print qq~<p>This email account is already registered. Click here to log in:</p>
<p class="center"><a class="showHomeLogin green-button" href="javascript: void(0);">log in</a></p>~;
}elsif($is_activated eq 0){
## ALREADY REGISTERED BUT NOT ACTIVATED
print qq~<input type="hidden" id="email" value="$email" class="hidden"/><p>This account has not yet been activated. Would you like to resend the activation code to complete sign-up?</p>
<p class="center"><a class="green-button" id="resendCode" href="javascript: void(0);">Resend the activation code</a></p>~;
}

}else{
## GOOD TO GO
my $token = &randomString;
my $sth = $SBdb->prepare("INSERT INTO members (activated, email, authcode, joined, invited_by) VALUES (?,?,?,?,?)");
$sth->execute(0, "$FORM{email}", "$token", "$now", "$FORM{invite}");
$sth->finish;
my $subject = qq~Set up your Sharebay account~;
my $body = qq~Hey there, thanks for signing up! Please click here to finish setting up your Sharebay account.~;
my $call2act = qq~Continue~;
my $link = qq~$baseURL/edit?token=$token~;
&sendMail($FORM{email}, $notify, $subject, undef, $body, $call2act, $link, undef, undef);
print qq~<p class="delivered center nomargin">&#x2714;</p><h2>Great, thank you! We've just sent you an email to complete the sign-up process.</h2><p>Please click the link in the email to get started. (If for some reason you don't see the email, please check your spam folder)</p>~;
}
$check->finish;
}



if ($a eq 'gettags'){
### SEND STRING-MATCHING TAGS TO JAVASCRIPT FOR AUTO-FILLING TAGS SECTION
my $s = $FORM{s};
if (length($s) > 0){
my $sth = $SBdb->prepare("SELECT tag FROM dictionary WHERE tag LIKE '$s%' ORDER BY used DESC LIMIT 10");
$sth->execute;
while($_ = $sth->fetchrow_array){
push(@data, $_);
}
my $json_data = encode_json(\@data);

&jsonHeader;
print $json_data;
$sth->finish;
}
}

if ($a eq 'checkmail'){
### CHECK FOR UNIQUE EMAIL WHEN EDITING PROFILE EMAIL
my $email = &textFormat($FORM{e});
my $sth = $SBdb->prepare("SELECT * FROM members WHERE email LIKE '$email'");
$sth->execute;
if ($sth->rows > 0){
$response = 1; ##EMAIL ALREADY EXISTS!!
}else{
$response = 0; ##EMAIL IS UNIQUE!!
}
&textHeader;
print $response;
$sth->finish;
}


if ($a eq 'saveprofile'){
my ($good2go, $saveInfo, $password_hash, $authcode, $id, $result, $country_name, $activated, $confirmRqd, $isNew);
if ($FORM{ac_type} eq 1 && $FORM{good2go} >= 10 && $FORM{pledge_box} eq 'agree'){$good2go++;}
elsif ($FORM{ac_type} eq 2 && $FORM{good2go} >= 11 && $FORM{pledge_box} eq 'agree'){$good2go++;}
else{
$result = '<h2>Sorry!</h2><p>There was an error processing your request. Please try again later.</p>';
}

if ($good2go){
my $visitor_id;
if (!$LOGGED_IN && $myID){$visitor_id = $myID};

### LET'S GO!!
$activated = 0;
$isNew = 0;
my ($savedMail, $savedMailPref, $imageRef);

## GET COUNTRY NAME
my $cname = $SBdb->prepare("SELECT country FROM countries WHERE iso = '$FORM{country}'");
$cname->execute;
$country_name = $cname->fetchrow_array;
$cname -> finish;

## HASH PASSWORD
if ($FORM{password} ne ''){
$password_hash = &hashPW($FORM{password});
}

## SANITISE TAGS
my $tags = &conformTags($FORM{tags});

## SEE IF MAIL CONFIRMATION REQUIRED AND GET IMAGEREF
my $checkCurrent = $SBdb->prepare("SELECT activated, email, image, mailme FROM members WHERE id = '$FORM{id}'");
$checkCurrent->execute;
($activated, $savedMail, $imageRef, $savedMailPref) = $checkCurrent->fetchrow_array;
$checkCurrent->finish;


$saveInfo = $SBdb->prepare("UPDATE members SET first_name = ?, last_name = ?, email = ?, password = COALESCE(NULLIF(?,''),password), activated = ?, ac_type = ?, org_name = ?, org_desc = ?, street = ?, city = ?, region = ?, postcode = ?, country_iso = ?, country = ?, lat = ?, lon = ?, phone = ?, tags = ?, about_me = ?, mailme = ?, allow_contact = ?, matchme = ?, timestamp = COALESCE(timestamp, ?), language = ?, auto_trans = ?, ip = ?, joined = CASE WHEN joined = 0 THEN $now ELSE joined END WHERE id = $FORM{id} LIMIT 1");


## EXECUTE!
$saveInfo->execute("$FORM{first_name}", "$FORM{last_name}", "$FORM{email}", "$password_hash", "1", "$FORM{ac_type}", "$FORM{org_name}", "$FORM{org_desc}", "$FORM{street}", "$FORM{city}", "$FORM{region}", "$FORM{postcode}", "$FORM{country}", "$country_name", "$FORM{lat}", "$FORM{lon}", "$FORM{phone}", "$tags", "$FORM{about_me}", "$FORM{mailme}", "$FORM{allow_contact}", "$FORM{matchme}", "$now", "$FORM{language}", "$FORM{auto_trans}", "$ip");

if ($visitor_id){
my $update_searches = $SBdb->do("UPDATE searches SET user_id = '$FORM{id}' WHERE user_id = '$visitor_id'");
}

## UPDATE LISTING LOCATIONS THAT AREN'T SHARE POINTS
my $updateListingLoc = $SBdb->do("UPDATE posts SET lat = '$FORM{lat}', lon = '$FORM{lon}' WHERE lister = '$FORM{id}' AND category != 51");


my $imageName;

# IF UNIQUE IMAGE DEFINED AND TEMP FILE EXISTS, GET IMAGE, RESIZE AND SAVE
# if ($FORM{image} && $FORM{image} ne "$imageRef\.jpg" && -e "$imgTempDir/$FORM{image}"){
if ($FORM{image} && -e "$imgTempDir/$FORM{image}"){

$imageName = $FORM{id} . '_' . $now;	

# RESIZE UPLOADED IMAGE TO 300 x 300

use Image::Resize;
my $img = Image::Resize->new("$imgTempDir/$FORM{image}");
my $resized = $img->resize(300, 300);
open (my $IM, ">", "$siteroot/user_pics/$imageName\.jpg");
print $IM $resized->jpeg();
close $IM;

# CREATE THUMBNAIL 
my $img2 = Image::Resize->new("$imgTempDir/$FORM{image}");
my $thumb = $img2->resize(50, 50);
open (my $TH, ">", "$siteroot/user_pics/$imageName\_t.jpg");
print $TH $thumb->jpeg();
close $TH;

# DELETE TEMP IMAGE AND UPDATE DATABASE

unlink ("$imgTempDir/$FORM{image}");
my $update = $SBdb->do("UPDATE members SET image = '$imageName' WHERE id = '$FORM{id}' LIMIT 1");
}

## SAVE THE tags
&savetags($FORM{tags}) if $FORM{tags};

if ($FORM{hasData} eq 'false'){
## SEND A WELCOME EMAIL
my ($to, $from, $subject, $name, $body, $call2act, $link);
$to = $FORM{email};
$from = $admin;
$subject = 'Welcome to Sharebay!';
$name = $FORM{first_name};
my $body = qq~Welcome and thank you so much for being here. My name is Colin and I founded Sharebay in 2018 because I believe there are so many ways we can do things better in the world today – and sharing networks like Sharebay could go a long way towards realizing them.

What do you think are the biggest problems in the world today? Maybe it’s climate change; maybe it’s hunger and poverty; maybe it’s inequality and disconnection between people. Take your pick, but one thing I know for certain is that successful sharing networks could alleviate many if not all of these problems.

Even though Sharebay is just getting started, imagine if no child ever had to go hungry again because there was always someone on hand kind enough to provide food? Imagine if we could drastically reduce our environmental footprint because we shared our reusable goods more efficiently rather than over-producing them? Imagine if we could always provide practical help and advice to people in danger whatever their circumstances without a price tag?

Call me over-enthusiastic, but, done right, I think there’s no social or environmental problem that sharing networks like Sharebay can’t help solve.

No price tag. Just people sharing in a normal familial way. Imagine the re-connection we could achieve together?

I’ve worked especially hard to try and make Sharebay the safest space possible, so people can share their talents and used items without fear of being taken advantage of. Much as we would all love to see a sharing world, it’s important that we look after and protect each other from those who are not ready to think like that – and they are many.

So come let’s enjoy this safe space and see what kind of amazing secret garden we can build together!

Kind regards,
Colin R. Turner~;
$call2act = 'BROWSE OUR OFFERS AND REQUESTS';
$link = $baseURL;

my $bccTrustPilot = 'www.sharebay.org+f3d955ae38@invite.trustpilot.com';
&sendMail($to, $from, $subject, $name, $body, $call2act, $link, $defaultImage, $bccTrustPilot);
$result = '<h2>Thank you and welcome!</h2><p class="success">Your Sharebay account has been activated.</p>';

}else{
$result = '<p class="success">Your details have been saved!</p>';
}

## SYNC / UNSYNC HONORPAY IF SET
&syncHonorPay($FORM{id},$FORM{email},$FORM{connect_HP});


## OK ADD TO ACTIVITY
my $profileImage;
my $profileImage;
my $getImage = $SBdb->prepare("SELECT image FROM members WHERE id = '$FORM{id}' AND image != '' LIMIT 1");
$getImage->execute;
if ($getImage->rows > 0){
$profileImage = $baseURL . '/user_pics/' . $getImage->fetchrow_array . '.jpg';
}
$getImage->finish;
my $text = qq~<span class="notranslate">$FORM{first_name} $FORM{last_name}</span>&nbsp;has just joined Sharebay!~;
if ($FORM{hasData} eq 'true'){$text = qq~<span class="notranslate">$FORM{first_name} $FORM{last_name}</span>&nbsp;has just updated their profile.~;}
my $link = qq~$baseURL/profile?id=$FORM{id}~;
my $location = &stringifyRegion($FORM{city}, $FORM{region}, $country_name);
&assessRisk('profile', $FORM{id});
&addActivity($FORM{id}, 'profile', $FORM{id}, $profileImage, $text, $link, $location, undef, $now);

$saveInfo->finish;
}
&textHeader;
print $result;
}


if ($a eq 'send_contact'){
my $response;
if ($FORM{name} && $FORM{email} && $FORM{message}){
my $subject = qq~Web contact from $FORM{name}~;
&sendPlainMail($admin, $admin, $FORM{email}, $subject, $FORM{message});
$response = qq~<p class="success">Message sent successfully. We'll be in touch shortly.</p>~;
}else{
$response = qq~<p class="error">There was an error sending your message. Form incomplete!</p>~;	
}
&textHeader;
print $response;
}


## RETURN MARKERS FOR MAP SEARCH ##
if ($a eq 'getmarkers'){
my ($data, $memSelect, $listSelect, $tagString, $searchType);

$searchType =  'bounds';

## SET LOCATION
my $myLat = $FORM{myLat};
my $myLon = $FORM{myLon};

## PROCESS tagS
if ($FORM{strict} eq 'tags'){
$tagString = &makeTagString($FORM{query});
}

## SEARCH MEMBERS
if ($FORM{in} =~ m/members/){

## BUILD MEMBER SEARCH STATEMENT
$memSelect = qq~SELECT id, first_name, last_name, activated, lat, lon~;

if ($FORM{in} =~ m/members/){
$memSelect .= qq~ FROM members WHERE activated = 1 AND lat != ''~;
}

my $blocked = &getBlockedIds;
if ($blocked){	
$memSelect .= qq~ AND id NOT IN ($blocked)~;
}

if ($searchType eq 'bounds'){$memSelect .= qq~ AND (lat BETWEEN $FORM{s} AND $FORM{n}) AND (($FORM{w} < $FORM{e} AND lon BETWEEN $FORM{w} AND $FORM{e}) OR  ($FORM{w} > $FORM{e} AND (lon BETWEEN $FORM{w} AND 180 OR lon BETWEEN -180 AND $FORM{e})))~;}

if ($FORM{query}){
if ($FORM{strict} eq 'tags'){
$memSelect .= qq~ AND MATCH (tags) AGAINST ('$tagString' IN BOOLEAN MODE)~;
}else{
$memSelect .= qq~ AND MATCH (first_name, last_name, org_name, org_desc, tags, about_me) AGAINST ('$FORM{query}')~;
}
}
if ($FORM{last7} eq 'y'){
$memSelect .= qq~ AND FROM_UNIXTIME(`last_active`) > DATE_SUB(NOW(), INTERVAL 7 DAY)~;
}

$memSelect .= qq~ ORDER BY last_active DESC~;

$memSelect .= qq~ LIMIT 100~ unless ($FORM{showall} eq 'y');

my $members = $SBdb->prepare($memSelect);
$members->execute;
if ($members->rows > 0){
my $i = 0;
$data = qq~[~;
while(my ($id, $first_name, $last_name, $activated, $lat, $lon) = $members->fetchrow_array){
my $type;
if ($activated eq 1){$type = 'member'};
$first_name =~ s/"/&quot;/g;
$last_name =~ s/"/&quot;/g;
$data .= qq~{"lat": "$lat", "lon": "$lon", "type": "$type", "id": "$id", "name": "$first_name $last_name"},~;
$i++;
}
}else{
$data = '';
}
$members->finish;
}

## SEARCH LISTINGS
if ($FORM{in} =~ m/offers/ || $FORM{in} =~ m/requests/ || $FORM{in} =~ m/sharepoints/){

## BUILD LISTING SEARCH STATEMENT
$listSelect = qq~SELECT id, title, type, physical, lat, lon FROM posts WHERE lat != '' AND (lat BETWEEN $FORM{s} AND $FORM{n}) AND (($FORM{w} < $FORM{e} AND lon BETWEEN $FORM{w} AND $FORM{e}) OR
 ($FORM{w} > $FORM{e} AND (lon BETWEEN $FORM{w} AND 180 OR lon BETWEEN -180 AND $FORM{e})))~;
 
if ($FORM{in} =~ m/offers/ && $FORM{in} =~ m/requests/){
$listSelect .= qq~ AND (type = 'offer' OR type = 'request')~;
}else{
if ($FORM{in} =~ m/offers/){
$listSelect .= qq~ AND type = 'offer'~;
}
if ($FORM{in} =~ m/requests/){
$listSelect .= qq~ AND type = 'request'~;
}}
if ($FORM{in} =~ m/sharepoints/){
$listSelect .= qq~ AND category = '51'~;
}

if ($LOGGED_IN){
my $blocked = &getBlockedIds;
if ($blocked){	
$listSelect .= qq~ AND lister NOT IN ($blocked)~;
}
}

if ($FORM{query}){
if ($FORM{strict} eq 'tags'){
$listSelect .= qq~ AND MATCH (tags) AGAINST ('$tagString' IN BOOLEAN MODE)~;
}else{
$listSelect .= qq~ AND MATCH (title, description, tags) AGAINST ('$FORM{query}')~;
}
}

$listSelect .= qq~ AND status = 'live'~;

if ($FORM{last7} eq 'y'){
$listSelect .= qq~ AND FROM_UNIXTIME(`timestamp`) > DATE_SUB(NOW(), INTERVAL 7 DAY)~;
}

$listSelect .= qq~ LIMIT 100~ unless ($FORM{showall} eq 'y');

my $listings = $SBdb->prepare($listSelect);
$listings->execute;
if ($listings->rows > 0){
my $i = 0;
$data = qq~[~ if ($data eq '');

while(my ($id, $title, $type, $physical, $lat, $lon) = $listings->fetchrow_array){
my $xType = $type . '_' . $physical;
$title =~ s/"/&quot;/g; # REMOVE DOUBLE QUOTES
$data .= qq~{"lat": "$lat", "lon": "$lon", "type": "$xType", "id": "l_$id", "name": "$title"},~;
$i++;
}
}
$listings->finish;
}
chop($data);
$data .= qq~]~ if ($data);
## RETURN RESULTS
&textHeader;
$data =~ s/\\//g; # REMOVE JS ESCAPE CHARS
print $data;

#~ # FROM PREVIOUS LISTING SEARCH
#~ my $json = encode_json(\@data);
#~ &jsonHeader;
#~ print $json;
}


if ($a eq 'getfeed'){
&textHeader;
&getFeed;
}

if ($a eq 'featurefeed'){
&textHeader;
&featureFeed;
}

if ($a eq 'dosearch'){
&textHeader;
&doSearch;
}


if ($a eq 'setlike'){
&textHeader;
if ($LOGGED_IN && $FORM{action} && $FORM{object} && $FORM{id}){
if ($FORM{action} eq 'like'){
my $sth = $SBdb->prepare("INSERT INTO interactions (action, actor_id, object_type, object_id, timestamp) VALUES (?,?,?,?,?)");
if($sth->execute("like","$myID","$FORM{object}","$FORM{id}","$now")){
$response = &getHearts("$FORM{object}","$FORM{id}");
};
}
if ($FORM{action} eq 'unlike'){
my $sth = $SBdb->prepare("DELETE FROM interactions WHERE action = 'like' AND actor_id = ? AND object_type = ? AND object_id = ?");
if($sth->execute("$myID","$FORM{object}","$FORM{id}")){
$response = &getHearts("$FORM{object}","$FORM{id}");
};
}
}
print $response;	
}



if ($a eq 'postcomment'){
&textHeader;
if ($LOGGED_IN && $FORM{comment} && $FORM{object} && $FORM{id}){
my $sth = $SBdb->prepare("INSERT INTO interactions (action, actor_id, object_type, object_id, thread, comment, timestamp) VALUE (?,?,?,?,?,?,?)");

# REMOVE HTML AND REPLACE NEW LINES WITH <BR/>
$FORM{comment} =~ s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$FORM{comment} =~ s/</&lt;/g;
$FORM{comment} =~ s/>/&gt;/g;
$FORM{comment} =~ s/\n|\r/<br\/>/g;

if($sth->execute("comment","$myID","$FORM{object}","$FORM{id}","$FORM{thread}","$FORM{comment}","$now")){
};
if ($FORM{thread} == 0){
	my $new_thread = $SBdb->{mysql_insertid};
	my $setThread = $SBdb->do("UPDATE interactions SET thread = '$new_thread' WHERE id = '$new_thread'");
}
$response = &getComments($FORM{object},$FORM{id});
}
print $response;	
}


if ($a eq 'showcomments'){
&textHeader;
if ($FORM{object} && $FORM{id} && $FORM{link}){
$response = &getSocial($FORM{object}, $FORM{id}, $FORM{link});
}
print $response;
}


if ($a eq 'deletecomment'){
&textHeader;
if ($LOGGED_IN && $FORM{comment_id} && $FORM{object} && $FORM{id}){
	
## IF IT'S A MAIN THREAD, DELETE ALL COMMENTS ON THREAD
if ($SBdb->do("SELECT id FROM interactions WHERE action = 'comment' AND actor_id = '$myID' AND id = '$FORM{comment_id}' AND thread = id") eq 1){
my $sth = $SBdb->do("DELETE FROM interactions WHERE action = 'comment' AND thread = '$FORM{comment_id}' AND object_type = '$FORM{object}' AND object_id = '$FORM{id}'");
}else{
my $sth = $SBdb->do("DELETE FROM interactions WHERE id = '$FORM{comment_id}' AND actor_id = '$myID' LIMIT 1");
}
$response = &getComments($FORM{object},$FORM{id});
print $response;	
}
}



if ($a eq 'postreview'){
&textHeader;
my $verify = $SBdb->do("SELECT id FROM transactions WHERE id = $FORM{trans_id} AND (giver_id = '$myID' OR getter_id = '$myID') AND (giver_id = $FORM{user_id} OR getter_id = $FORM{user_id}) LIMIT 1");
if ($LOGGED_IN && $verify eq 1){
my $sth;
if ($FORM{update} && $FORM{trans_id} && $FORM{user_id}){
$sth = $SBdb->prepare("UPDATE reviews SET stars = ?, comment = ?, timestamp = ? WHERE reviewer_id = ? AND target_id = ? AND trans_id = ? LIMIT 1");
}else{
$sth = $SBdb->prepare("INSERT INTO reviews (stars, comment, timestamp, reviewer_id, target_id, trans_id) VALUES (?,?,?,?,?,?)");
}
if ($sth->execute("$FORM{rating}", "$FORM{comment}", "$now", "$myID", "$FORM{user_id}", "$FORM{trans_id}")){
	$response = qq~<p class="success">Thank you! Your review has been <a href="$baseURL/reviews?a=read&id=$FORM{user_id}">posted</a>. Leave <a href="$baseURL/reviews?a=myreviews">more reviews</a>?</p>~;
	if (!$FORM{update} && $FORM{notify_member}){
		my $email = &getEmail($FORM{user_id});
		my $subject = qq~You've just received a review on Sharebay!~;
		my $body = qq~$myName just sent you a review on Sharebay!~;
		my $call2act = qq~Read your reviews~;
		my $link = qq~$baseURL/reviews?a=read&id=$FORM{user_id}~;
&sendMail($email, $admin, $subject, undef, $body, $call2act, $link, undef, undef);
	}

}else{
	$response = qq~<p class="error">There was an error posting your review. Please try again later.</p>~;
}

## POST TO NEWSFEED IF FOUR OR FIVE STARS
if ($FORM{rating} > 3){
my $review_id;
if (!$FORM{update}){
$review_id = $SBdb->{mysql_insertid};
}else{
my $getReviewID = $SBdb->prepare("SELECT id FROM reviews WHERE reviewer_id = ? AND target_id = ? AND trans_id = ? LIMIT 1");
$getReviewID->execute("$myID", "$FORM{user_id}", "$FORM{trans_id}");
$review_id = $getReviewID->fetchrow_array;
$getReviewID->finish;
}
my $link = qq~$baseURL/reviews/?id=$FORM{user_id}~;
my $rec_name = &getFullName($FORM{user_id});
my $text = qq~<a href="$baseURL/profile/?id=$myID">$myName</a> left a <a href="$baseURL/reviews/?id=$FORM{user_id}">$FORM{rating} star review</a> for <a href="$baseURL/profile/?id=$FORM{user_id}">$rec_name</a>.~;
if ($FORM{comment}){$text .= qq~<p class="center italic">&#8220;$FORM{comment}&#8221;</p>~;}
&addActivity("$myID", 'review', "$review_id", "", "$text", "$link", "", "$FORM{rating}", "$now");
}


}else{
	$response = qq~<p class="error">You are not authorised to post this review.</p>~;
}
print $response;	
}



if ($a eq 'setseen'){
if ($SBdb->do("UPDATE interactions SET status = 'seen' WHERE action = '$FORM{action}' AND actor_id = '$FORM{actor_id}' AND object_type = '$FORM{object_type}' AND object_Id = '$FORM{object_id}'")){
&textHeader;
print 1;
}
}


if ($a eq 'getconversations'){
my $page = $FORM{page} || 0;
my $resultsPP = 20;
my $offset = $page * $resultsPP;
my $response;
&htmlHeader;


my $query = qq~SELECT messages.* FROM (SELECT id, sender, recipient, convo_id, message, type, status, max(timestamp) AS timestamp FROM messages~;
if ($FORM{filter} eq 'unseen'){
	$query .= qq~ WHERE recipient = $myID AND status != 'seen'~;
}else{
	$query .= qq~ WHERE (sender = $myID OR recipient = $myID)~;
}
my $blocked = &getBlockedIds;
if ($blocked){
$query .= qq~ AND sender NOT IN ($blocked) AND recipient NOT IN ($blocked)~;
}
$query .= qq~ GROUP BY convo_id) AS t JOIN messages USING (convo_id, timestamp) GROUP BY convo_id, timestamp ORDER BY id DESC LIMIT $resultsPP OFFSET $offset~;

my $sth = $SBdb->prepare($query);

$sth->execute;

my ($unseen_class, $all_class);
if ($FORM{filter} eq 'unseen'){$unseen_class = 'bold'; $all_class;}else{$unseen_class; $all_class = 'bold';}

if ($sth->rows > 0){
print qq~<div class="clearfix"><a href="$baseURL/messages" class="notification tiny float-left">SEE ALL</a><a onclick="markAllMessagesSeen();" href="javascript:void(0);" class="notification tiny float-right">MARK ALL SEEN</a></div>~ if $page eq 0;
while (my ($id, $sender, $recipient, $convo_id, $message, $type, $status, $timestamp) = $sth->fetchrow_array){
my $contact;
my $xClass; #FOR OPTIONAL EXTRA CLASSES
if ($sender eq $myID){$contact = $recipient; $xClass .= ' notranslate from-me';}else{$contact = $sender};
if ($status != 'seen'){$xClass .= 'bold';}
my ($contact_first_name, $contact_last_name, $imageRef, $contact_gifted, $contact_trust_score, $contact_badge_level, $contact_is_admin, $contact_last_active) = &getNameRecord($contact);
my $time = &getWhen($timestamp);
$imageRef = 'q' if !$imageRef;
$message =~ s!<br/>! !g;
$message =~ s/<(?:[^>'"]*|(['"]).*?\1)*>//gs;
$message =~ s/^(.{0,100}).*$/$1.../sg if length($message) > 100;
print qq~
<a class="notification" href="$baseURL/messages?id=$convo_id"><div class="chat-user-card notranslate"><img src="$baseURL/user_pics/$imageRef\_t.jpg" class="chat-user-card-image" title="$contact_first_name $contact_last_name"/> $contact_first_name $contact_last_name~;
print qq~ ($contact_gifted)~ if $contact_gifted;
&printBadge($contact_first_name, $contact_badge_level);
print qq~</div><div class="convo-time grey smaller">$time</div>
<div class="convo-message $xClass">$message</div></a>~;
} # END LOOP
}else{
print qq~No messages to show.~;
}
}



if ($a eq 'getmessages'){
&htmlHeader;
print &getMessages;
}


if ($a eq 'getnotifications'){
&textHeader;
print &getNotifications;
}


if ($a eq 'getinfobox'){
if ($FORM{id} =~ m/^l_/){
# IS LISTING
my $listing_id = $FORM{id};
$listing_id =~ s/^l_//;
my $sth = $SBdb->prepare("SELECT p.lister, p.title, p.description, p.image, p.type, m.first_name, m.last_name, m.gifted, m.badge_level, m.star_rating FROM posts AS p JOIN members AS m ON m.id = p.lister WHERE p.id = $listing_id LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
my ($lister, $title, $description, $imageRef, $type, $l_first_name, $l_last_name, $gifted, $badge_level, $star_rating) = $sth->fetchrow_array;
my $image;
if (-e "$siteroot/listing_pics/$imageRef\.jpg"){
$image = qq~$baseURL/listing_pics/$imageRef\_t.jpg~;
}
$title = &descTitle($title, $description);
$title = '<span class="post_type">[REQUEST]</span> ' . $title if $type eq 'request';
my $lister_name = $l_first_name . ' ' . $l_last_name;
$lister_name =~ s/^(.{0,20}).*$/$1.../sg if (length($lister_name) > 20);
$response = qq~<div class="div-main-infoWindow">~;
$response .= qq~<img class="info-listing-img" src="$image"/>~ if ($image);
$response .= qq~<div class="info-listing-details"><div class="info-listing-title"><a href="$baseURL/listing?showlisting&id=$listing_id" title="Respond to listing">$title</a></div><div class="info-listing-desc">$description</div><div class="info-listing-contact"><div class="lister-info notranslate">$lister_name~;
$response .= &getBadge($l_first_name, $badge_level);
if ($gifted){$response .= qq~&nbsp;($gifted)~;}
$response .= qq~</div>~;

if ($LOGGED_IN){$response .= qq~<a class="green-button" href="listing?showlisting&id=$listing_id" title="Respond to listing">RESPOND</a><a class="info-listing-spam" onclick="report('listing', $listing_id);" href="javascript:void(0);">Report spam</a>~;
}else{
$response .= qq~<a class="showLogin" href="javascript:void(0);" title="Log in to contact">Log in to contact</a>~;
}
$response .= qq~
</div></div></div>~;
}else{
$response = "NODATA";
}

}else{
# IS PERSON

my $profile_id = $FORM{id};
my $sth = $SBdb->prepare("SELECT activated, about_me, badmail FROM members WHERE id = $profile_id LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
my ($activated, $about_me, $badmail) = $sth->fetchrow_array;
my ($first_name, $last_name, $image, $gifted, $trust_score, $badge_level, $badge, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($profile_id);
my $height;
my $sigDisplay;
my $contactDisplay;
my $contactTop;
my $image;
if (-e "$siteroot/user_pics/$image\.jpg"){
$image = "$baseURL/user_pics/$image\.jpg";
}else{$image = "$baseURL/user_pics/q_t.jpg";}
if ($about_me){$height = '220px'}else{$height = '120px';$sigDisplay ='style="display:none;"'; $contactTop='style="top:62px;"';};

$response = qq~<div class="div-main-infoWindow"><a  href="profile?a=showprofile&id=$profile_id"><img class="info-img" src="$image"/></a><div class="info-listing-title notranslate"><a  href="profile?a=showprofile&id=$profile_id">$first_name $last_name~;
if ($badge){$response .= qq~&nbsp;<img src="$baseURL/i/$badge" class="badge" alt="Trust badge" title="Level $badge_level member"/>~;}
if ($gifted){$response .= qq~&nbsp;($gifted)~;}
$response .= qq~</a></div><div class="info-listing-desc" $sigDisplay>$about_me</div><div class="info-contact" $contactTop><a href="profile?id=$profile_id" title="View profile">VIEW PROFILE</a></div></div>~;
}else{
$response = "NODATA";
}
}
&textHeader;
print $response;
}

# REPORT CONTENT
if ($a eq 'report'){
&textHeader;
if ($FORM{object_type} && $FORM{object_id} && $LOGGED_IN){
my $sth = $SBdb->prepare("INSERT IGNORE INTO spam_reports (object_type, object_id, reporter_id) VALUES (?,?,?)");
$sth->execute("$FORM{object_type}", "$FORM{object_id}", "$myID");
$sth->finish;
&assessRisk($FORM{object_type}, $FORM{object_id});
print "Thank you. We have logged your report.";
}else{
print "Sorry, we couldn't process your request. Please try again later.";
}
}

# BLOCK PROFILE
if ($a eq 'block'){
&textHeader;
if ($FORM{profile} && $LOGGED_IN){
my $sth = $SBdb->prepare("INSERT INTO member_blocks (blocker_id, blocked_id) VALUES (?,?)");
$sth->execute($myID, $FORM{profile});
$sth->finish;
print "Profile successfully blocked.\n\nYou will no longer see content from this member. You can unblock them any time from your Profile and Settings page.";
}else{
print "Sorry, we couldn't process your request. Please try again later.";
}
}

# UNBLOCK PROFILE
if ($a eq 'unblock'){
&textHeader;
if ($FORM{profile} && $LOGGED_IN){
my $sth = $SBdb->do("DELETE FROM member_blocks WHERE blocker_id = '$myID' AND blocked_id = $FORM{profile}");
print "Profile successfully unblocked.";
}else{
print "Sorry, we couldn't process your request. Please try again later.";
}
}

# FOLLOW OBJECT
if ($a eq 'follow'){
&textHeader;
if ($FORM{object_type} && $FORM{object_id} && $LOGGED_IN && ($SBdb->do("DELETE FROM unsubscribes WHERE actor_id = '$myID' AND object_type = '$FORM{object_type}' AND object_id = '$FORM{object_id}'") == 1)){
print "You are now following this post.";
}else{
print "Sorry, we couldn't process your request. Please try again later.";
}
}

# FOLLOW OBJECT
if ($a eq 'unfollow'){
&textHeader;
if ($FORM{object_type} && $FORM{object_id} && $LOGGED_IN){
my $sth = $SBdb->prepare("INSERT IGNORE INTO unsubscribes (actor_id, object_type, object_id) VALUES (?,?,?)");
if ($sth->execute("$myID", "$FORM{object_type}", "$FORM{object_id}")){
print "You will no longer receive notifications about this post.";
}
}else{
print "Sorry, we couldn't process your request. Please try again later.";
}
}


if ($a eq 'gotit'){
&textHeader;
if ($FORM{id}){
my $gotit = $SBdb->do("UPDATE members SET gotit = 1 WHERE id = $FORM{id} LIMIT 1");
print 1;	
}
}


if ($a eq 'forgotpassword'){
&textHeader;
&showForgot;
}

if ($a eq 'resetpassword'){
&textHeader;
my $sth = $SBdb->prepare("SELECT id, first_name, last_name, email, authcode FROM members WHERE email LIKE '$FORM{email}' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
my ($id, $first_name, $last_name, $email, $authcode) = $sth->fetchrow_array;
my $subject = 'Reset your Sharebay.org password';
my $body = 'To create a new password for your account, please click here:';
my $call2act = 'Change Password';
my $link = qq~$baseURL/profile?a=newpassword&id=~ . $id . qq~&auth=~ . $authcode;
&sendMail($email, $notify, $subject, $first_name, $body, $call2act, $link, undef, undef);
$response = 1;
}else{
$response = 0;
}
print $response;
}


if ($a eq 'deletelisting' && $LOGGED_IN){
	&textHeader;
	my $id = $FORM{id} || -1;
	my $dListing = $SBdb->do("UPDATE posts SET status = 'deleted' WHERE id = '$id' AND lister = '$myID' LIMIT 1");
	if ($dListing > 0){
	# CANCEL ANY PENDING TRANSACTIONS
	my $dTransactions = $SBdb->do("UPDATE transactions SET status = 'cancelled' WHERE status != 'delivered' AND listing_id = '$id'");	
	&deleteActivity('listing', $id);
	print 1;
	}
}

if ($a eq 'admindeletelisting' && $LOGGED_IN && $myAdmin){
	&textHeader;
	my $id = $FORM{id} || -1;
	my $dListing = $SBdb->do("UPDATE posts SET status = 'spam' WHERE id = '$id' LIMIT 1");
	if ($dListing > 0){
	# CANCEL ANY PENDING TRANSACTIONS
	my $dTransactions = $SBdb->do("UPDATE transactions SET status = 'cancelled' WHERE status != 'delivered' AND listing_id = '$id'");
	&deleteActivity('listing', $id);
	print 1;
	}
}


if ($a eq 'admindeleteprofile' && $LOGGED_IN && $myAdmin){
	&textHeader;
	my $id = $FORM{id} || -1;
	my $dProfile = $SBdb->do("UPDATE members SET activated = -1, session_id = '' WHERE id = '$id' LIMIT 1");
	if ($dProfile > 0){
	# CANCEL LISTINGS AND ANY PENDING TRANSACTIONS
	my $spamListings = $SBdb->do("UPDATE posts SET status = 'spam' WHERE lister = $id");
	my $cancelTrans = $SBdb->do("UPDATE transactions SET status = 'cancelled' WHERE status != 'delivered' AND (giver_id = '$id' OR getter_id = '$id')");
	&deleteActivity('profile', $id);
	print 1;
	}
}


if ($a eq 'adminobject' && $LOGGED_IN && $myAdmin && $FORM{action} && $FORM{object} && defined($FORM{id})){
&textHeader;
my $action = $FORM{action};
my $object = $FORM{object};
my $id = $FORM{id};
if ($object eq 'listing'){
if ($action eq 'safe'){
if ($SBdb->do("UPDATE posts SET risk = 0 WHERE id = '$id' LIMIT 1") eq 1){
print &adminBox('listing', $id);
}
}elsif ($action eq 'remove'){
if ($SBdb->do("UPDATE posts SET status = 'spam' WHERE id = '$id' LIMIT 1") eq 1){
# CANCEL PENDING TRANSACTIONS AND ACTIVITY
my $dTransactions = $SBdb->do("UPDATE transactions SET status = 'admin-cancelled' WHERE status != 'delivered' AND listing_id = '$id'");
&deleteActivity('listing', $id);
print qq~<p class="success">Listing and any associated transactions removed.</p>~;
}
}
}elsif ($object eq 'profile'){
if ($action eq 'safe'){
if ($SBdb->do("UPDATE members SET risk = 0 WHERE id = '$id' LIMIT 1") eq 1){
print &adminBox('profile', $id);
}}
elsif ($action eq 'make_moderator'){
if ($SBdb->do("UPDATE members SET is_moderator = 1 WHERE id = '$id' LIMIT 1") eq 1){
&sendMessage($myID, $id, qq~$myName has just made you a site moderator. You can now amend and delete inappropriate lisings and profiles. Use your power wisely! 😀~, 'alert');
print &adminBox('profile', $id);
}}
elsif ($action eq 'remove_moderator'){
if ($SBdb->do("UPDATE members SET is_moderator = 0 WHERE id = '$id' LIMIT 1") eq 1){
print &adminBox('profile', $id);
}}
elsif ($action eq 'make_author'){
if ($SBdb->do("UPDATE members SET is_author = 1 WHERE id = '$id' LIMIT 1") eq 1){
&sendMessage($myID, $id, qq~$myName has just made you a site author. You can now add and edit articles on the official <a href="$baseURL/blog">Sharebay blog</a>.~, 'alert');
print &adminBox('profile', $id);
}}
elsif ($action eq 'remove_author'){
if ($SBdb->do("UPDATE members SET is_author = 0 WHERE id = '$id' LIMIT 1") eq 1){
print &adminBox('profile', $id);
}}
elsif ($action eq 'make_admin'){
if ($SBdb->do("UPDATE members SET is_admin = 1 WHERE id = '$id' LIMIT 1") eq 1){
&sendMessage($myID, $id, qq~$myName has just made you a site admin. You can now amend/delete inappropriate content and add/revoke admin rights of other members. Use your power wisely! 😀~, 'alert');
print &adminBox('profile', $id);
}}
elsif ($action eq 'remove_admin'){
if ($SBdb->do("UPDATE members SET is_admin = 0 WHERE id = '$id' LIMIT 1") eq 1){
print &adminBox('profile', $id);
}}
elsif ($action eq 'remove'){
if ($SBdb->do("UPDATE members SET activated = -1 WHERE id = '$id' LIMIT 1") eq 1){
my $spamListings = $SBdb->do("UPDATE posts SET status = 'spam' WHERE lister = $id");
my $cancelTrans = $SBdb->do("UPDATE transactions SET status = 'admin-cancelled' WHERE status != 'delivered' AND (giver_id = '$id' OR getter_id = '$id')");
&deleteActivity('profile', $id);
print qq~<p class="success">Profile, listings and any live transactions removed.</p>~;
}
}
}
}



if ($a eq 'testjson'){
	&jsonHeader;
	my %hash;
	%hash = ('id' => 60, 'body' => 'parsnip eile', 'foofighter' => 'Unthompson Twins');
	use JSON::PP;
	my $json = encode_json (\%hash);
	print $json;	
}


if ($a eq 'sendchat'){
&jsonHeader;
use JSON;
my $response;
if ($LOGGED_IN && $FORM{convo_id} && $FORM{message}){
my $contact;
my $getContact = $SBdb->prepare("SELECT sender, recipient FROM messages WHERE convo_id = '$FORM{convo_id}' LIMIT 1");
$getContact->execute;
if ($getContact->rows > 0){
my ($sender, $recipient) = $getContact->fetchrow_array;
if ($sender eq $myID){$contact = $recipient}else{$contact = $sender};
my $message = $FORM{message};
$message =~ s/\r?\n/<br\/>/g; # REMOVE LINE BREAKS
my $id = &sendMessage($myID, $contact, $message, 'message');

my $getMessage = $SBdb->prepare("SELECT message FROM messages WHERE id = ?");
$getMessage->execute($id);
my $returnMessage = $getMessage->fetchrow_array;
$getMessage->finish;

$response = qq~<div class="chat-right notranslate">$returnMessage</div>~;
my %data = ('lastID' => $id, 'data' => $response);
my $json = new JSON;
print $json->encode(\%data);	
}
}
}


if ($a eq 'updatechat'){
&jsonHeader;
use JSON;
my $response;
if ($LOGGED_IN && $FORM{convo_id} && $FORM{last_id}){

my $sth = $SBdb->prepare("SELECT id, sender, recipient, message, type FROM messages WHERE convo_id = '$FORM{convo_id}' AND (sender = $myID OR recipient = $myID) AND id > $FORM{last_id} ORDER by id");
$sth->execute;

my $lastID;

# SHOW CHAT CONVERSATION
while (my ($id, $sender, $recipient, $message, $type, $timestamp) = $sth->fetchrow_array){
my $class;
if ($sender eq $myID){$class = 'chat-right notranslate'}else{$class = 'chat-left';}
if ($type eq 'alert'){$class = 'chat-alert';}
$response .= qq~<div class="$class">$message</div>~;
$lastID = $id;
}
my %data = ('lastID' => $lastID, 'data' => $response);
my $json = new JSON;
print $json->encode(\%data);
}
}

if ($a eq 'markseen'){
&textHeader;
if ($LOGGED_IN && $FORM{id}){
my $markSeen = $SBdb->do("UPDATE messages SET status = 'seen' WHERE convo_id = '$FORM{id}' AND recipient = $myID AND status != 'seen'");
}
print 1;
}


if ($a eq 'changepassword'){
&textHeader;
my $password_hash = &hashPW($FORM{pw});
my $sth = $SBdb->prepare("UPDATE members SET password = ? WHERE id = $FORM{id} AND authcode = '$FORM{auth}' LIMIT 1");
if ($sth->execute("$password_hash")){
# OK, NOW CREATE SESSION AND RETURN LOG IN TOKEN
my $sth = $SBdb->prepare("SELECT id, first_name, last_name, image, language, auto_trans, lat, lon FROM members WHERE id = $FORM{id} LIMIT 1");
$sth->execute;
my ($id, $first_name, $last_name, $image, $language, $auto_trans, $lat, $lon) = $sth->fetchrow_array;
$response = &createSession($id);
}else{
$response = 0;
}
print $response;
}

if ($a eq 'showlogin'){
&textHeader;
&showLogin;
}

if ($a eq 'showhomelogin'){
&textHeader;
&showLogin('home');
}

if ($a eq 'showoffer'){
&textHeader;
&showOffer;
}

if ($a eq 'showrequest'){
&textHeader;
&showRequest;
}


if ($a eq 'checkmessages'){
&textHeader;
my $sth = $SBdb->prepare("SELECT id FROM messages WHERE recipient = $myID AND status != 'seen' GROUP BY sender");
$sth->execute;
if ($sth->rows > 0){
print $sth->rows;
}else{
print 0;
}
$sth->finish;
}


if ($a eq 'checknotifications'){
&textHeader;

# my $sth = $SBdb->prepare("SELECT i.id FROM interactions AS i WHERE ((i.object_type = 'profile' AND i.object_id = '$myID') ". &getMyStuff . ") AND i.action != 'view' AND i.actor_id != '$myID' AND i.status != 'seen' GROUP BY i.action, i.object_type, i.object_id");

my $sth = $SBdb->prepare("SELECT i.id FROM interactions AS i WHERE NOT EXISTS (SELECT id FROM unsubscribes WHERE object_type = i.object_type AND object_id = i.object_id AND actor_id = '$myID') AND i.action != 'view' AND i.actor_id != '$myID' AND i.status != 'seen' AND ((i.object_type = 'profile' AND i.object_id = '$myID')" . &getMyStuff . ")");

$sth->execute;
if ($sth->rows > 0){
print $sth->rows;
}else{
print 0;
}
$sth->finish;
}


if ($a eq 'markallnotificationsseen'){
&textHeader;
if ($SBdb->do("UPDATE interactions AS i SET status = 'seen' WHERE i.action != 'view' AND i.actor_id != '$myID' AND i.status != 'seen' AND ((i.object_type = 'profile' AND i.object_id = '$myID')" . &getMyStuff . ")")){
print 1;
}
}

if ($a eq 'getcommentmenu'){
&textHeader;
my $object_type = $FORM{object_type};
my $object_id = $FORM{object_id};
my $actor_id = $FORM{actor_id};
if ($SBdb->do("SELECT id FROM unsubscribes WHERE actor_id = '$myID' AND object_type = '$object_type' AND object_id = '$object_id'") == 1){
print qq~<a class="menu-item" href="javascript:void(0);" onclick="follow('$object_type','$object_id');">Follow this post</a>~;
}else{
print qq~<a class="menu-item" href="javascript:void(0);" onclick="unfollow('$object_type','$object_id');">Unfollow this post</a>~;
}
my ($actor_name, $actor_id) = &getActor($object_type, $object_id);
if ($actor_id ne $myID){
if ($object_type eq 'listing' || $object_type eq 'profile'){
print qq~<a class="menu-item" href="javascript:void(0);" onclick="report('$object_type','$object_id');">Report this</a>~;
}
if ($SBdb->do("SELECT id FROM member_blocks WHERE blocker_id = '$myID' AND blocked_id = '$actor_id'") == 1){
print qq~<a class="menu-item" href="javascript:void(0);" onclick="unblock($actor_id);">Unblock $actor_name</a>~;
}else{
print qq~<a class="menu-item" href="javascript:void(0);" onclick="block($actor_id);">Block $actor_name</a>~;
}
}

}

if ($a eq 'markallmessagesseen'){
&textHeader;
if ($SBdb->do("UPDATE messages SET status = 'seen' WHERE recipient = $myID")){
print 0;
}
}

if ($a eq 'dologin'){
&textHeader;
my $password_hash = &hashPW($FORM{password});
my $sth = $SBdb->prepare("SELECT id, first_name, last_name, activated, image, language, auto_trans, lat, lon FROM members WHERE email LIKE '$FORM{email}' AND password = '$password_hash' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
my ($id, $first_name, $last_name, $activated, $imageRef, $language, $auto_trans, $lat, $lon) = $sth->fetchrow_array;
if ($activated eq 1){
$response = &createSession($id);

# UPDATE COOKIE VISITOR IDS
if ($myID && ($myID ne $id)){
my $searchUpdate = $SBdb->do("UPDATE searches SET user_id = '$id' WHERE user_id = '$myID'");
my $viewsUpdate = $SBdb->do("UPDATE interactions SET actor_id = '$id' WHERE actor_id = '$myID'");
}

}elsif ($activated eq 0){
$response = 'UNACTIVATED';

}elsif ($activated eq -1){
$response = 'LOCKED';
}

}else{
$response = 'WRONG';
}
$sth->finish;
print $response;
}


if ($a eq 'dologout'){
&textHeader;
$LOGGED_IN = 0;
print 1;
}


if ($a eq 'dologoutall'){
use CGI;
my $cgi = new CGI;
my $SESSION_ID = $cgi->cookie('SESS_ID');
my $deleteSession = $SBdb->do("UPDATE members SET session_id = '' WHERE session_id = '$SESSION_ID'");
$LOGGED_IN = 0;
&textHeader;
print 1;
}

if ($a eq 'postlisting'){
my $imageName;

# SAVE IMAGE IF EXISTS
if ($FORM{image}){
$imageName = &randomString(16);

use Image::Resize;
my $img = Image::Resize->new("$imgTempDir/$FORM{image}");
my $resized = $img->resize(800, 800);
open (my $IM, ">", "$siteroot/listing_pics/$imageName\.jpg");
print $IM $resized->jpeg();
close $IM;

# CREATE THUMBNAIL
my $img2 = Image::Resize->new("$imgTempDir/$FORM{image}");
my $thumb = $img2->resize(300, 300);
open (my $TH, ">", "$siteroot/listing_pics/$imageName\_t.jpg");
print $TH $thumb->jpeg();
close $TH;

# DELETE TEMP IMAGE
unlink ("$imgTempDir/$FORM{image}");
}

my $sth = $SBdb->prepare("INSERT INTO posts (lister, description, quantity, type, physical, category, trusted_only, terms, image, lat, lon, send_ok, status, timestamp) VAlUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)");

&htmlHeader;
if ($sth->execute("$myID", "$FORM{text}", "$FORM{quantity}", "$FORM{type}", "$FORM{physical}", "$FORM{category}", "0", "$FORM{terms}", "$imageName", "$FORM{listingLat}", "$FORM{listingLon}", "$FORM{send_ok}", "live", "$now")){
my $thisId = $SBdb->{mysql_insertid};
my $link = qq~$baseURL/listing?id=$thisId~;
my $image = '';
$image = qq~$baseURL/listing_pics/$imageName\.jpg~ if $imageName;
my $location = getRegion($myID);
&assessRisk('listing', $thisId);
&addActivity($myID, 'listing', $thisId, $image, $FORM{text}, $link, $location, $FORM{type}, $now);
my $type = ucfirst($FORM{type});
print qq~$type posted successfully. <a href="$baseURL/listing?id=$thisId">View</a>~;
}else{
print qq~Unknown error! Your listing couldn't be saved. Please try again later. [CODE: 440]~;
}
}


if ($a eq 'savelisting'){
my $thisId;
use URI::Escape;
if ($FORM{good2go} >= 2 && $LOGGED_IN){

## SANITISE TAGS
my $tags = &conformTags($FORM{tags});

my $location = &getRegion($myID);
my $imageName;

if ($FORM{listing_quantity} > 99){$FORM{listing_quantity} = 99};
if ($FORM{physical} eq 'yes'){$FORM{physical} = 1};
if (!$FORM{listingLat}){$FORM{listingLat} = $myLat; $FORM{listingLon} = $myLon;}
if ($FORM{listing_id}){

# CHECK LISTING EXISTS, OWNERSHIP AND UPDATE IT
my $check = $SBdb->prepare("SELECT id, image FROM posts WHERE id = $FORM{listing_id} AND lister = '$myID'");
$check->execute;
if ($check->rows eq 1){
my (undef, $imageRef) = $check->fetchrow_array;
$imageName = $imageRef if $imageRef;

# GO FOR UPDATE
my $update = $SBdb->prepare("UPDATE posts SET title = ?, description = ?, quantity = ?, type = ?, physical = ?, category = ?, trusted_only = ?, terms = ?, tags = ?, lat = ?, lon = ?, send_ok = ?, status = ?, timestamp = ? WHERE id = $FORM{listing_id} LIMIT 1");

$update->execute("$FORM{listing_title}", "$FORM{listing_desc}", "$FORM{listing_quantity}", "$FORM{type}", "$FORM{physical}", "$FORM{category}", "$FORM{trusted_only}", "$FORM{terms}", "$tags", "$FORM{listingLat}", "$FORM{listingLon}", "$FORM{send_ok}", "live", "$now");
}

$thisId = $FORM{listing_id};
$check->finish;
$response = qq~Listing saved successfully. <a href="$baseURL/listing?id=$thisId" title="View listing">View</a>~;
}else{
# SAVE NEW LISTING

# ADD CITY, REGION AND CATEGORY TO TAGS TO HELP SEARCHES
my ($cat_name, $cat_trans) = &getCategory($FORM{category});
$tags .= qq~,$location,$cat_name~;
my $save = $SBdb->prepare("INSERT INTO posts (lister, title, description, quantity, type, physical, category, trusted_only, terms, tags, lat, lon, send_ok, status, timestamp) VAlUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)");

$save->execute("$myID", "$FORM{listing_title}", "$FORM{listing_desc}", "$FORM{listing_quantity}", "$FORM{type}", "$FORM{physical}", "$FORM{category}", "$FORM{trusted_only}", "$FORM{terms}", "$tags", "$FORM{listingLat}", "$FORM{listingLon}", "$FORM{send_ok}", "live", "$now");
$thisId = $SBdb->{ mysql_insertid };
$save->finish;
$response = qq~New listing added successfully. <a href="$baseURL/listing?id=$thisId" title="View listing">View</a>~;
}

## IF OFFER, GET OFFERS AND INCREMENT TRUST IF OFFERS < 4
if ($FORM{type} eq 'offer'){
my $getOffers = $SBdb->do("SELECT id FROM posts WHERE lister = '$myID' AND status = 'live' AND type = 'offer'");
if ($getOffers >= 0 && $getOffers < 4){
my $incrementTrust = $SBdb->do("UPDATE members SET trust_score = trust_score + 1 WHERE id = '$myID'");
}
}

# SAVE THE TAGS
&savetags($tags);

# SAVE IMAGE IF NEW ONE EXISTS
if ($FORM{image} && $thisId && -e "$imgTempDir/$FORM{image}"){
$imageName = $thisId . '_' . $now;

# RESIZE UPLOADED IMAGE TO 800 x 450
# use Image::Magick;
# my $img = Image::Magick->new;
# $img->Read("$imgTempDir/$FORM{image}");
# $img->Resize(geometry=>'800x450', blur=>0.9);
# $img->Write("$siteroot/listing_pics/$imageName\.jpg");


use Image::Resize;
my $img = Image::Resize->new("$imgTempDir/$FORM{image}");
my $resized = $img->resize(800, 800);
open (my $IM, ">", "$siteroot/listing_pics/$imageName\.jpg");
print $IM $resized->jpeg();
close $IM;



# CREATE THUMBNAIL

my $img2 = Image::Resize->new("$imgTempDir/$FORM{image}");
my $thumb = $img2->resize(300, 300);
open (my $TH, ">", "$siteroot/listing_pics/$imageName\_t.jpg");
print $TH $thumb->jpeg();
close $TH;


# my $img2 = Image::Magick->new;
# $img2->Read("$imgTempDir/$FORM{image}");
# $img2->Resize(geometry=>'224x126', blur=>0.9);
# $img2->Write("$siteroot/listing_pics/$imageName\_t.jpg");

# DELETE TEMP IMAGE AND UPDATE DATABASE
unlink ("$imgTempDir/$FORM{image}");
my $update = $SBdb->do("UPDATE posts SET image = '$imageName' WHERE id = $thisId LIMIT 1");
}
my $image_path;
$image_path = "$baseURL/listing_pics/$imageName\.jpg" if $imageName;
&assessRisk('listing', $thisId);
&addActivity($myID, 'listing', $thisId, $image_path, "$FORM{listing_title} $FORM{listing_desc}", "$baseURL/listing?id=$thisId", $location, $FORM{type}, $now);

if ($FORM{from_template}){
## UPDATE TEMPLATE USE IF USED
my $updateTemplate = $SBdb->prepare("UPDATE listing_templates SET uses = uses + 1 WHERE id = ? LIMIT 1");
$updateTemplate->execute("$FORM{from_template}");
$updateTemplate->finish;
}

}else{
# NOT GOOD TO GO OR NOT LOGGED IN
$response = qq~There was a problem with your request and we couldn't save your listing! (ERROR CODE: 201)~;
}
&textHeader;
print $response;
}



if ($a eq 'getsuggestions'){
&htmlHeader;
my $no_items = 3;
if ($FORM{height} <= 820){$no_items = 2;}
if ($FORM{height} >= 1080){$no_items = 4;}
my $interests;
my $seen;
my $matchesTemp;
if ($LOGGED_IN){
	# FIND RECENT SEARCHES
	my $getSearches = $SBdb->prepare("SELECT DISTINCT query FROM searches WHERE user_id = '$myID'");
	$getSearches->execute;
	while (my $q = $getSearches->fetchrow_array){$interests .= $q . ' ';}
	$getSearches->finish;
	
	# TRY MATCH ACCORDING TO USER PROFILE INFO
	my $getProfileInfo = $SBdb->prepare("SELECT tags, about_me FROM members WHERE id = '$myID'");
	$getProfileInfo->execute;
	my ($tags, $about_me) = $getProfileInfo->fetchrow_array;
	$getProfileInfo->finish;
	$interests .= $tags . ' ' . $about_me;
	$interests = &makeTagString($interests);
	
	my $getSeen = $SBdb->prepare("SELECT object_id FROM interactions WHERE actor_id = '$myID' AND action = 'view' AND object_type = 'listing'");
	$getSeen->execute;
	if ($getSeen->rows > 0){
	while (my $id = $getSeen->fetchrow_array){	
	$seen .= "$id,";
	}
	chop($seen);
	}
$seen = qq~ AND id NOT IN ($seen)~ if $seen;


my $blocked = &getBlockedIds($myID);
my $notBlocked;
if ($blocked){	
$notBlocked = qq~ AND lister NOT IN ($blocked)~;
}



$matchesTemp = $SBdb->prepare("CREATE TEMPORARY TABLE IF NOT EXISTS suggestions AS (SELECT id, type, CONCAT_WS(' ', title, description) AS text, image FROM posts WHERE image != '' AND status = 'live' AND lister != '$myID' $notBlocked AND MATCH (title, description, tags) AGAINST ('$interests') $seen ORDER BY rank DESC LIMIT 50)");
}else{
$matchesTemp = $SBdb->prepare("CREATE TEMPORARY TABLE IF NOT EXISTS suggestions AS (SELECT id, type, CONCAT_WS(' ', title, description) AS text, image FROM posts WHERE image != '' AND status = 'live' ORDER BY rank DESC LIMIT 50)");	
}


$matchesTemp->execute;
my $matches = $SBdb->prepare("SELECT * FROM suggestions ORDER BY RAND() LIMIT $no_items");
$matches->execute;
if ($matches->rows > 0){
while (my ($id, $type, $text, $image) = $matches->fetchrow_array){
$text = substr($text, 0, 120) . '...' if length($text) > 120;
print qq~<div class="rightbar-item" onclick="window.location.href='$baseURL/listing?id=$id';">
<img src="$baseURL/listing_pics/$image\_t.jpg"/>
<p>$text</p></div>~;
}
}else{
print qq~<p>Add some more information on <a href="$baseURL/edit">your profile</a> to see site suggestions.~;
}
print qq~<p class="center smaller">See all my matching <a href="$baseURL/?search=&filter=offers&order=relevance">offers</a> and <a href="$baseURL/?search=&filter=requests&order=relevance">requests</a>.~;
$matches->finish;
}


if ($a eq 'send_message'){
# SEND MESSAGE TO USER
my $response;

if ($LOGGED_IN && $FORM{message} && $FORM{to}){
&sendMessage($myID, $FORM{to}, $FORM{message}, 'message');
$response = qq~<p class="success">Message sent successfully!</p>~;
}else{
#NOT LOGGED IN, NO DATA
$response = qq~<p class="error">There was a problem with your request. Please make sure you are logged in! (ERROR CODE: 203)</p>~;
}
&textHeader;
print $response;
}


if ($a eq 'send_response'){
my $response;
# SEND USER RESPONSE TO LISTER
if ($LOGGED_IN && $FORM{listing_message} && $FORM{listing_id}){

# GET LISTER INFO FROM LIST ID
my $getListerInfo = $SBdb->prepare("SELECT m.id, m.first_name, p.title, p.description, p.type, p.category FROM members AS m INNER JOIN posts AS p ON m.id = p.lister WHERE p.id = '$FORM{listing_id}' LIMIT 1");
$getListerInfo->execute;
my ($lister, $lister_first_name, $listing_title, $listing_desc, $type, $category_id) = $getListerInfo->fetchrow_array;
$getListerInfo->finish;

$listing_title = substr($listing_desc, 0, 50) . '...' if (!$listing_title);

# GET RESPONDER INFO
my ($resp_first_name, $resp_last_name, $image, $gifted, $trust_score, $badge_level, $badge, $star_rating, $myModerator, $myAuthor, $myAdmin, $last_active) = &getNameRecord($myID);

# SEND MESSAGE
my $subject = qq~$resp_first_name $resp_last_name responded to your listing <a href="$baseURL/listing?id=$FORM{listing_id}">$listing_title</a>~;
my $body = qq~$resp_first_name $resp_last_name just responded to your listing $listing_title~;
if ($FORM{shipping_cost} > 0){
$body .= qq~ and has offered to pay \$$FORM{shipping_cost} to cover delivery costs~ if $type eq 'offer';
$body .= qq~ and has suggested a payment of \$$FORM{shipping_cost} to cover delivery costs~ if $type eq 'request';
}
$body .= qq~:<hr/><em>$FORM{listing_message}</em><hr/>$resp_first_name $resp_last_name~;
$body .= &getBadge($resp_first_name, $badge_level);
if ($gifted){$body .= qq~&nbsp;($gifted)~;}
my $call2act = qq~Reply to $resp_first_name $resp_last_name~;

&sendMessage($myID, $lister, $subject, 'alert');
&sendMessage($myID, $lister, $body, 'message');

# CREATE TRANSACTION IF TRANSACTABLE
my (undef, $transactable) = &getCategory($category_id);
if ($transactable){
my ($giver, $getter, $quantity);
if ($FORM{quantity}){$quantity = $FORM{quantity}}else{$quantity = 1};
if ($type eq 'offer'){$giver = $lister; $getter = $myID};
if ($type eq 'request'){$giver = $myID; $getter = $lister};
my $createTransaction = $SBdb->prepare("INSERT INTO transactions (listing_id, listing_type, giver_id, getter_id, quantity, shipping_cost, status, timestamp) VALUES (?,?,?,?,?,?,?,?)");
$createTransaction->execute("$FORM{listing_id}", "$type", "$giver", "$getter", "$quantity", "$FORM{shipping_cost}", "applied", "$now");
}

$response = qq~<p class="success">Response sent successfully!</p>~;
}else{
# NOT LOGGED IN
$response = qq~<p class="error">There was a problem with your request. Please make sure you are logged in! (ERROR CODE: 202)</p>~;
}
&textHeader;
print $response;
}


if ($a eq 'resendcode'){
my $email = $FORM{e};
my $sth = $SBdb->prepare("SELECT authcode FROM members WHERE email LIKE '$email' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
# SEND EMAIL
my $authcode = $sth->fetchrow_array;
my $subject = 'Activate your Sharebay account';
my $body = 'To activate and continue setting up your Sharebay account, please click here:';
my $call2act = 'CONTINUE';
my $link = qq~$baseURL/edit?token=$authcode~;
# my $link = $baseURL . '/edit?confirm=' . $authcode;
&sendMail($email, $admin, $subject, undef, $body, $call2act, $link, undef, undef);
$response = qq~<p class="success">We've just sent you a new activation email. Please click the link in the email to activate your account.</p>~;
}else{
$response = qq~<p class="error">There was a problem with your request. Please make sure you have entered a correct email.</p>~;
}
&textHeader;
print $response;
}




if ($a eq 'matchcategories'){
my $text = $FORM{text};
$text =~ s/[[:punct:]]//g;
my $matchCategory = $SBdb->prepare("SELECT p.category, COUNT(*) AS count, c.category FROM posts AS p JOIN categories AS c ON c.id = p.category WHERE p.status != 'spam' AND MATCH (p.title, p.description, p.tags) AGAINST ('$text') GROUP BY c.id ORDER BY count DESC LIMIT 3");
$matchCategory->execute;
if ($matchCategory->rows > 0){
$response .= qq~Select a category:<br/>~;
while(my($cat_id, $count, $cat_name) = $matchCategory->fetchrow_array){
$response .= qq~<label class="cat_result" for="cat$cat_id" onclick="categorySelected()";><input type="radio" name="auto_category" class="cat_picker" id="cat$cat_id" value="$cat_id"/><img src="$baseURL/category_pics/cat$cat_id\_t.jpg" alt="$cat_name"/><div class="cat_name flex-center"><p id="name$cat_id">$cat_name</p></div></label>~;
}
}
$response .= qq~<label class="cat_result" onclick="manualSelect();"><img src="$baseURL/category_pics/cat47\_t.jpg" alt="Select category"/><div class="cat_name flex-center"><p><a href="#">Select category</a></p></div></label>~;


&htmlHeader;
print $response;
}



if ($a eq 'getcategoryselect'){
	
my $cat_select = '<select name="manual_category" onchange="manualSelected();"><option value="">Select a category...</soption>';
$cat_select .= &getCategories;
$cat_select .= '</select>';

&textHeader;
print $cat_select;
}




if ($a eq 'updatetransaction'){
if ($LOGGED_IN && $FORM{id} && $FORM{state}){
my $transaction_id = $FORM{id};
my $transaction_state = $FORM{state};
my $shipping = $FORM{shipping};
my $transaction_check;
if ($transaction_state eq 'accepted'){$transaction_check = "status = 'applied'";}
elsif ($transaction_state eq 'payment_requested'){$transaction_check = "status = 'applied' OR status = 'payment_offered'";}
elsif ($transaction_state eq 'payment_offered'){$transaction_check = "status = 'applied'";}
elsif ($transaction_state eq 'sent'){$transaction_check = "(status = 'paid' OR status = 'accepted')";}
elsif ($transaction_state eq 'delivered'){$transaction_check = "status = 'sent'";}
elsif ($transaction_state eq 'cancelled'){$transaction_check = "status LIKE '%'";}
else{$transaction_check = "status = ''";}
my $sth = $SBdb->prepare("UPDATE transactions SET status = ?, shipping_cost = COALESCE(NULLIF(?,''),shipping_cost), timestamp = ? WHERE id = $transaction_id AND (giver_id = '$myID' OR getter_id = '$myID') AND $transaction_check LIMIT 1");

if ($sth->execute("$transaction_state", "$shipping", "$now")){
$response = 1;
# CREATE MESSAGE ALERT
my $getTransInfo = $SBdb->prepare("SELECT listing_id, giver_id, getter_id, quantity, shipping_cost FROM transactions WHERE id = $transaction_id LIMIT 1");
$getTransInfo->execute;
my ($listing_id, $giver_id, $getter_id, $quantity, $shipping_cost) = $getTransInfo->fetchrow_array;
$getTransInfo->finish;
my $other;
if ($giver_id eq $myID){$other = $getter_id}else{$other = $giver_id};
my $other_name = &getFullName($other);
my $title = &getListingTitle($listing_id);
my $titleLink = qq~<a href="$baseURL/listing?id=$listing_id">$title</a>~;
my $alert;
if ($transaction_state eq 'accepted'){$alert = "$myName accepted $other_name\'s response to $titleLink";}
if ($transaction_state eq 'payment_requested'){$alert = &getFullName($giver_id) . " is requesting a delivery payment from " . &getFullName($getter_id) . " for $titleLink";}
if ($transaction_state eq 'payment_offered'){$alert = &getFullName($getter_id) . " is offering to pay delivery costs to " . &getFullName($giver_id) . " for $titleLink";}
elsif ($transaction_state eq 'cancelled'){$alert = "$myName cancelled the transaction for $titleLink";}
elsif ($transaction_state eq 'sent'){$alert = "$myName has sent $titleLink";}
elsif ($transaction_state eq 'delivered'){
# SEND ALERT, DECREMENT QUANTITY AND COMPLETE LISTING IF NECESSARY
$alert = "$myName confirmed delivery of $titleLink";
my $setQuantity = $SBdb->do("UPDATE posts SET quantity = quantity - $quantity WHERE id = $listing_id LIMIT 1");
my $closeListing = $SBdb->do("UPDATE posts SET status = 'complete' WHERE id = $listing_id AND quantity < 1 LIMIT 1");

### REIMBURSE SENDER >>>
if ($shipping_cost){
my $member_name = &getFullName($giver_id);
my $member_email = &getEmail($giver_id);
my $message = qq~$member_name [$member_email] is due a payment of &dollar;$shipping_cost for shipping costs incurred.~;
&sendMessage(30, 30, $message, 'alert');
}

}
&sendMessage($myID, $other, $alert, 'alert');
}else{
# PROBLEM UPDATING TRANSACTION
$response = -1;
}
}else{
# NOT LOGGED IN, NO DATA
$response = -1;
}
&textHeader;
print $response;
}

if ($a eq 'sendunblock'){
my $sth = $SBdb->prepare("SELECT email, authcode FROM members WHERE id = $FORM{id} LIMIT 1");
$sth->execute;
my ($email, $authcode) = $sth->fetchrow_array;
my $subject = 'Your email unblock request';
my $call2act = 'Click to unblock your email';
my $link = $baseURL . '/profile?a=cleanemail&id=' . $FORM{id} . '&auth=' . $authcode;
my $body = qq~We received a request from you to unblock your email address. Please click the button below to reinstate your email so you can continue to receive emails and notifications from other Sharebays.~;
&sendMail($email, $admin, $subject, undef, $body, $call2act, $link, undef, undef);
&textHeader;
}

if ($a eq 'test'){
&textHeader;
print 'Run OK';
}
$SBdb->disconnect;
#EXEUNT
