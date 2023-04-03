#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR SENDING CUSTOM MAILS TO MEMBERS
# use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );

my $active = 1; # 0 to disable

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
require '/home/sharebay/public_html/common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

if ($maintenance){$active = 0}; # DISABLE IN MAINTENANCE MODE

my ($h_content, $html, $text, $thisID, $first_name, $last_name, $thisLat, $thisLon, $email, $authcode);

if ($active){


my @subjects = (
"Here's some things you might like on Sharebay",
"Sharebay latest auto-matches",
"Latest Sharebay items for you",
"Have you seen what's on Sharebay recently?",
"We found some Sharebay items for you",
"What's new on Sharebay",
"Your latest Sharebay matches"
);

my $subject = $subjects[rand @subjects];

my $getMember = $SBdb->prepare("SELECT id, first_name, last_name, lat, lon, email, authcode FROM members WHERE activated = 1 AND lat != '' AND matchme = 1 AND matchme_sent = 0 AND badmail = 0 LIMIT 1");
# my $getMember = $SBdb->prepare("SELECT id, first_name, last_name, lat, lon, email, authcode FROM members WHERE activated = 1 AND lat != '' AND id = 30 LIMIT 1");
$getMember->execute;

if ($getMember->rows > 0){
($thisID, $first_name, $last_name, $thisLat, $thisLon, $email, $authcode) = $getMember->fetchrow_array;
my $intro = 'Hi ' . $first_name . ', our auto-match bot found some listings that you might be interested in.';

# my $grabtags = $SBdb->prepare("SELECT tags FROM members WHERE id = $thisID");
# $grabtags->execute;
# my $tags = $grabtags->fetchrow_array;
# $grabtags->finish;

my $tags = &getInterests($thisID);

my $blocked = &getBlockedIds($thisID);
my ($notBlockedLister, $notBlockedProfile);
if ($blocked){	
$notBlockedLister = qq~ AND lister NOT IN ($blocked)~;
$notBlockedProfile = qq~ AND id NOT IN ($blocked)~;
}

## LATEST LISTINGS ANYWHERE
my $latestTemp = $SBdb->prepare("CREATE TEMPORARY TABLE IF NOT EXISTS temp_latest AS (SELECT id, type, title, description, image, (6371 * acos(cos(radians($thisLat)) * cos(radians(lat)) * cos(radians(lon) - radians($thisLon)) + sin(radians($thisLat)) * sin(radians(lat)))) AS distance FROM posts WHERE image != '' AND lister != $thisID $notBlockedLister AND status = 'live' ORDER BY timestamp DESC LIMIT 10)");
$latestTemp->execute;

my $latest = $SBdb->prepare("SELECT * FROM temp_latest ORDER BY RAND() LIMIT 2");
$latest->execute;
if ($latest->rows > 0){
$h_content .= &sectionHeading('Latest offers and requests anywhere');
# $h_content .= &intro('The latest listings from anywhere:');
while (my ($id, $type, $title, $description, $image, $distance) = $latest->fetchrow_array){
$distance = sprintf(" (%.1f Kms)", $distance);
$title = '[' . uc($type) . '] ' . $title . $distance;
my $title_length = length($title);
my $max_length = 200 - $title_length;
$description =~ s/^(.{0,$max_length})\b.*$/$1.../s if length($description) > $max_length;
$h_content .= &mailItem(
$title,
$description,
$baseURL . '/listing_pics/' . $image . '.jpg',
$baseURL . '/listing?id=' . $id,
'View listing'
);
}
$h_content .= &divider;
}
$latest->finish;



## BEST MATCHES ANYWHERE ##
my $matchesTemp = $SBdb->prepare("CREATE TEMPORARY TABLE IF NOT EXISTS matches AS (SELECT id, type, title, description, image, (6371 * acos(cos(radians($thisLat)) * cos(radians(lat)) * cos(radians(lon) - radians($thisLon)) + sin(radians($thisLat)) * sin(radians(lat)))) AS distance, MATCH (title, description, tags) AGAINST ('$tags') AS rank FROM posts WHERE image != '' AND status = 'live' AND lister != $thisID $notBlockedLister AND MATCH (title, description, tags) AGAINST ('$tags') ORDER BY rank DESC LIMIT 20)");
$matchesTemp->execute;

my $matches = $SBdb->prepare("SELECT * FROM matches ORDER BY RAND() LIMIT 2");
$matches->execute;
if ($matches->rows > 0){
$h_content .= &sectionHeading('Best matches anywhere');
# $h_content .= &intro('A selection of listings that match your preferences');
while (my ($id, $type, $title, $description, $image, $distance, $rank) = $matches->fetchrow_array){
$distance = sprintf(" (%.1f Kms)", $distance);
$title = '[' . uc($type) . '] ' . $title . $distance;
my $title_length = length($title);
my $max_length = 200 - $title_length;
$description =~ s/^(.{0,$max_length})\b.*$/$1.../s if length($description) > $max_length;
$h_content .= &mailItem(
$title,
$description,
$baseURL . '/listing_pics/' . $image . '.jpg',
$baseURL . '/listing?id=' . $id,
'View listing'
);
}
$h_content .= &divider;
}
$matches->finish;



## NEAREST LISTINGS
my $nearestTemp = $SBdb->prepare("CREATE TEMPORARY TABLE IF NOT EXISTS temp_nearest AS (SELECT id, type, title, description, image, (6371 * acos(cos(radians($thisLat)) * cos(radians(lat)) * cos(radians(lon) - radians($thisLon)) + sin(radians($thisLat)) * sin(radians(lat)))) AS distance FROM posts WHERE image != '' AND lister != $thisID $notBlockedLister AND status = 'live' HAVING distance < 100 ORDER BY distance ASC LIMIT 20)");
$nearestTemp->execute;

my $nearest = $SBdb->prepare("SELECT * FROM temp_nearest ORDER BY RAND() LIMIT 1");
$nearest->execute;
if ($nearest->rows > 0){
$h_content .= &sectionHeading('In your area (within 100km)');
# $h_content .= &intro('We found these listings within 100km of you:');
while (my ($id, $type, $title, $description, $image, $distance) = $nearest->fetchrow_array){
$distance = sprintf(" (%.1f Kms)", $distance);
$title = '[' . uc($type) . '] ' . $title . $distance;
my $title_length = length($title);
my $max_length = 200 - $title_length;
$description =~ s/^(.{0,$max_length})\b.*$/$1.../s if length($description) > $max_length;
$h_content .= &mailItem(
$title,
$description,
$baseURL . '/listing_pics/' . $image . '.jpg',
$baseURL . '/listing?id=' . $id,
'View listing'
);
}
$h_content .= &divider;
}
$nearest->finish;



## MOST POPULAR LISTING
my $popularTemp = $SBdb->prepare("CREATE TEMPORARY TABLE IF NOT EXISTS temp_popular AS (SELECT id, type, title, description, image, (6371 * acos(cos(radians($thisLat)) * cos(radians(lat)) * cos(radians(lon) - radians($thisLon)) + sin(radians($thisLat)) * sin(radians(lat)))) AS distance FROM posts WHERE image != '' AND lister != $thisID $notBlockedLister AND status = 'live' ORDER BY rank DESC LIMIT 5)");
$popularTemp->execute;

my $popular = $SBdb->prepare("SELECT * FROM temp_popular ORDER BY RAND() LIMIT 1");
$popular->execute;
if ($popular->rows > 0){
$h_content .= &sectionHeading('Trending now');
# $h_content .= &intro('The most popular listings from anywhere:');
while (my ($id, $type, $title, $description, $image, $distance) = $popular->fetchrow_array){
$distance = sprintf(" (%.1f Kms)", $distance);
$title = '[' . uc($type) . '] ' . $title . $distance;
my $title_length = length($title);
my $max_length = 200 - $title_length;
$description =~ s/^(.{0,$max_length})\b.*$/$1.../s if length($description) > $max_length;
$h_content .= &mailItem(
$title,
$description,
$baseURL . '/listing_pics/' . $image . '.jpg',
$baseURL . '/listing?id=' . $id,
'View listing'
);
}
$h_content .= &divider;
}
$popular->finish;



## FIND REQUEST MATCHES ##
my $reqMatchesTemp = $SBdb->prepare("CREATE TEMPORARY TABLE IF NOT EXISTS req_matches AS (SELECT id, type, title, description, image, (6371 * acos(cos(radians($thisLat)) * cos(radians(lat)) * cos(radians(lon) - radians($thisLon)) + sin(radians($thisLat)) * sin(radians(lat)))) AS distance, MATCH (title, description, tags) AGAINST ('$tags') AS rank FROM posts WHERE image != '' AND status = 'live' AND type = 'request' AND lister != $thisID $notBlockedLister AND MATCH (title, description, tags) AGAINST ('$tags') ORDER BY rank DESC LIMIT 20)");
$reqMatchesTemp->execute;

my $reqMatches = $SBdb->prepare("SELECT * FROM req_matches ORDER BY RAND() LIMIT 1");
$reqMatches->execute;
if ($reqMatches->rows > 0){
$h_content .= &sectionHeading('Can you help with this?');
# $h_content .= &intro('Can you help with any of these?');
while (my ($id, $type, $title, $description, $image, $distance, $rank) = $reqMatches->fetchrow_array){
$distance = sprintf(" (%.1f Kms)", $distance);
$title = '[' . uc($type) . '] ' . $title . $distance;
my $title_length = length($title);
my $max_length = 200 - $title_length;
$description =~ s/^(.{0,$max_length})\b.*$/$1.../s if length($description) > $max_length;
$h_content .= &mailItem(
$title,
$description,
$baseURL . '/listing_pics/' . $image . '.jpg',
$baseURL . '/listing?id=' . $id,
'View listing'
);
}
$h_content .= &divider;
}
$reqMatches->finish;


if ($blocked){	
$notBlockedLister = qq~ AND lister NOT IN ($blocked)~;
}

## SOMEONE LIKE YOU ##
my $bestPeopleTemp = $SBdb->prepare("CREATE TEMPORARY TABLE IF NOT EXISTS best_people AS (SELECT id, first_name, last_name, region, country, about_me, tags, image, (MATCH (about_me, tags) AGAINST ('$tags')) AS rank FROM members WHERE activated = 1 AND id != $thisID $notBlockedProfile AND MATCH (about_me, tags) AGAINST ('$tags') ORDER BY rank DESC LIMIT 20)");
$bestPeopleTemp->execute;

my $bestPeople = $SBdb->prepare("SELECT * FROM best_people ORDER BY RAND() LIMIT 1");
$bestPeople->execute;

if ($bestPeople->rows > 0){
$h_content .= &sectionHeading('Someone like you');
# $h_content .= &intro('We found some people with similar interests:');

while (my ($id, $first_name, $last_name, $region, $country, $about_me, $tags, $image, $rank) = $bestPeople->fetchrow_array){
my $title = $first_name . ' ' . $last_name . ', ' . $region . ', ' . $country;
my $title_length = length($title);
my $max_length = 400 - $title_length;
my $desc = '<strong>tags:</strong> ' . &printtags($tags);
$desc .= '</p><p style="font-size:16px;line-height:19px;font-style:italic;">&quot;' . $about_me . '&quot;' if ($about_me);
$desc =~ s/^(.{0,$max_length})\b.*$/$1.../s if length($desc) > $max_length;
$h_content .= &mailItem(
$title,
$desc,
$baseURL . '/user_pics/' . $image . '.jpg',
$baseURL . '/profile?id=' . $id,
'See profile'
);
}
$h_content .= &divider;
}


## CREATE A LISTING ##
$h_content .= &sectionHeading('Post an offer');
$h_content .= &mailItem(
'Post a new offer or request.',
'Help us grow Sharebay by lising an item you no longer need or offer your skills freely to another member.',
$baseURL . '/i/crowds.jpg',
$baseURL . '/post',
'Create a listing'
);
$h_content .= &divider;



if ($h_content){
my $newText = $text;
$text = '';
$html .= &mailHeader($subject);
$html .= &intro('Hi ' . $first_name . ', our auto-match system found some listings that you might be interested in.');
$html .= $h_content;
$text .= $newText;
$html .= &mailFooter($thisID);

$text =~ s/<[^>]*>//g; # REMOVE HTML TAGS FOR TEXT

# FOR TESTING - REMOVE FOR EMAIL !!!
# print $html;
# $text =~ s/\\n/<br\/>/g;
# print $text;

## SEND MAIL
## ENCODE SUBJECT
use MIME::Base64;
my $subject_enc = encode_base64($subject);
$subject_enc =~ s/^\s+|\s+$//g;
$subject_enc = '=?UTF-8?B?' . $subject_enc . '?=';

## OK LET'S SEND IT!
my $host = 'othello.ldn.kgix.net';
my $user = 'auto-match@sharebay.org';
my $pass = $emailPW;
use MIME::Lite;
use Net::SMTP;
MIME::Lite->send('smtp', $host, AuthUser=>$user, AuthPass=>$pass);
my $msg = MIME::Lite->new(
        From    => '"Sharebay Digest" <' . $user . '>',
        To      => $email,
        Subject => $subject_enc,
        Type    => 'multipart/alternative'
    );
    $msg->attach(
        Type     => 'text/plain; charset=UTF-8',
		Encoding => 'quoted-printable',
        Data     => $text
    );
    $msg->attach(
        Type     => 'text/html',
		Encoding => 'quoted-printable',
        Data     => $html
    );
    $msg->send;

# SET SENT
my $setSent = $SBdb->do("UPDATE members SET matchme_sent = 1 WHERE id = $thisID LIMIT 1");
}


}else{
## NO ROWS FOUND -> RESET SENT
my $resetAllSent = $SBdb->do("UPDATE members SET matchme_sent = 0");
}
$getMember->finish;
}


sub mailHeader{
my $title = shift;
return qq~<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional //EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office"><head><!--[if gte mso 9]><xml><o:OfficeDocumentSettings><o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml><![endif]--><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><meta name="viewport" content="width=device-width"><!--[if !mso]><!--><meta http-equiv="X-UA-Compatible" content="IE=edge"><!--<![endif]--><title>$title</title><!--[if !mso]><!-- --><link href="https://fonts.googleapis.com/css?family=Open+Sans" rel="stylesheet" type="text/css"><!--<![endif]--><style type="text/css" id="media-query">body{margin:0;padding:0}table,td,tr{vertical-align:top;border-collapse:collapse}.ie-browser table,.mso-container table{table-layout:fixed}*{line-height:inherit}a[x-apple-data-detectors=true]{color:inherit!important;text-decoration:none!important}[owa] .img-container button,[owa] .img-container div{display:block!important}[owa] .fullwidth button{width:100%!important}[owa] .block-grid .col{display:table-cell;float:none!important;vertical-align:top}.ie-browser .block-grid,.ie-browser .num12,[owa] .block-grid,[owa] .num12{width:650px!important}.ExternalClass,.ExternalClass div,.ExternalClass font,.ExternalClass p,.ExternalClass span,.ExternalClass td{line-height:100%}.ie-browser .mixed-two-up .num4,[owa] .mixed-two-up .num4{width:216px!important}.ie-browser .mixed-two-up .num8,[owa] .mixed-two-up .num8{width:432px!important}.ie-browser .block-grid.two-up .col,[owa] .block-grid.two-up .col{width:325px!important}.ie-browser .block-grid.three-up .col,[owa] .block-grid.three-up .col{width:216px!important}.ie-browser .block-grid.four-up .col,[owa] .block-grid.four-up .col{width:162px!important}.ie-browser .block-grid.five-up .col,[owa] .block-grid.five-up .col{width:130px!important}.ie-browser .block-grid.six-up .col,[owa] .block-grid.six-up .col{width:108px!important}.ie-browser .block-grid.seven-up .col,[owa] .block-grid.seven-up .col{width:92px!important}.ie-browser .block-grid.eight-up .col,[owa] .block-grid.eight-up .col{width:81px!important}.ie-browser .block-grid.nine-up .col,[owa] .block-grid.nine-up .col{width:72px!important}.ie-browser .block-grid.ten-up .col,[owa] .block-grid.ten-up .col{width:65px!important}.ie-browser .block-grid.eleven-up .col,[owa] .block-grid.eleven-up .col{width:59px!important}.ie-browser .block-grid.twelve-up .col,[owa] .block-grid.twelve-up .col{width:54px!important}\@media only screen and (min-width:670px){.block-grid,.block-grid .col.num12{width:650px!important}.block-grid .col{vertical-align:top}.block-grid.mixed-two-up .col.num4{width:216px!important}.block-grid.mixed-two-up .col.num8{width:432px!important}.block-grid.two-up .col{width:325px!important}.block-grid.three-up .col{width:216px!important}.block-grid.four-up .col{width:162px!important}.block-grid.five-up .col{width:130px!important}.block-grid.six-up .col{width:108px!important}.block-grid.seven-up .col{width:92px!important}.block-grid.eight-up .col{width:81px!important}.block-grid.nine-up .col{width:72px!important}.block-grid.ten-up .col{width:65px!important}.block-grid.eleven-up .col{width:59px!important}.block-grid.twelve-up .col{width:54px!important}}\@media (max-width:670px){.block-grid,.col,img.fullwidth,img.fullwidthOnMobile{max-width:100%!important}.block-grid,.col{min-width:320px!important;display:block!important}.block-grid{width:calc(100% - 40px)!important}.col{width:100%!important}.col>div{margin:0 auto}.no-stack .col{min-width:0!important;display:table-cell!important}.no-stack.two-up .col{width:50%!important}.no-stack.mixed-two-up .col.num4{width:33%!important}.no-stack.mixed-two-up .col.num8{width:66%!important}.no-stack.three-up .col.num4{width:33%!important}.no-stack.four-up .col.num3{width:25%!important}.mobile_hide{min-height:0;max-height:0;max-width:0;display:none;overflow:hidden;font-size:0}}</style></head><body class="clean-body" style="margin: 0;padding: 0;-webkit-text-size-adjust: 100%;background-color: #FFFFFF"><style type="text/css" id="media-query-bodytag">\@media (max-width:520px){.block-grid,.col,img.fullwidth,img.fullwidthOnMobile{max-width:100%!important}.block-grid,.col{min-width:320px!important;width:100%!important;display:block!important}.col>div{margin:0 auto}.no-stack .col{min-width:0!important;display:table-cell!important}.no-stack.two-up .col{width:50%!important}.no-stack.mixed-two-up .col.num4{width:33%!important}.no-stack.mixed-two-up .col.num8{width:66%!important}.no-stack.three-up .col.num4{width:33%!important}.no-stack.four-up .col.num3{width:25%!important}.mobile_hide{min-height:0!important;max-height:0!important;max-width:0!important;display:none!important;overflow:hidden!important;font-size:0!important}} </style><!--[if IE]><div class="ie-browser"><![endif]--><!--[if mso]><div class="mso-container"><![endif]--><table class="nl-container" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;min-width: 320px;Margin: 0 auto;background-color: #FFFFFF;width: 100%" cellpadding="0" cellspacing="0"><tbody><tr style="vertical-align: top"><td style="word-break: break-word;border-collapse: collapse !important;vertical-align: top"><!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td align="center" style="background-color: #FFFFFF;"><![endif]--><div style="background-color:transparent;"><div style="Margin: 0 auto;min-width: 320px;max-width: 650px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #FFFFFF;" class="block-grid "><div style="border-collapse: collapse;display: table;width: 100%;background-color:#FFFFFF;"><!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="background-color:transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width: 650px;"><tr class="layout-full-width" style="background-color:#FFFFFF;"><![endif]--><!--[if (mso)|(IE)]><td align="center" width="650" style=" width:650px; padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:5px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><![endif]--><div class="col num12" style="min-width: 320px;max-width: 650px;display: table-cell;vertical-align: top;"><div style="background-color: transparent; width: 100% !important;"><!--[if (!mso)&(!IE)]><!--><div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;"><!--<![endif]--><div align="left" class="img-container left autowidth " style="padding: 15px; background-color: #fff;"><!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr style="line-height:0px;line-height:0px;"><td style="padding: 15px; background-color: #fff;" align="left"><![endif]--><div style="line-height:5px;font-size:1px">&#160;</div><!-- LOGO --><a href="$baseURL" target="_blank"><img src="$baseURL/i/main-logo.png" width="148" height="36" style="border:none;width:148px;height:36px;" alt="Sharebay Logo"/></a><div style="line-height:5px;font-size:1px">&#160;</div><!--[if mso]></td></tr></table><![endif]--></div><!--[if (!mso)&(!IE)]><!--></div><!--<![endif]--></div></div><!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]--></div></div></div>~;
}



sub intro{
my $introPara = shift;
$text .= $introPara . '\n\n';
return qq~
<!-- OPENING SECTION -->
<div style="background-color:transparent;"><div style="Margin: 0 auto;min-width: 320px;max-width: 650px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #FFFFFF;" class="block-grid "><div style="border-collapse: collapse;display: table;width: 100%;background-color:#FFFFFF;"><!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="background-color:transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width: 650px;"><tr class="layout-full-width" style="background-color:#FFFFFF;"><![endif]--><!--[if (mso)|(IE)]><td align="center" width="650" style=" width:650px; padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:5px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><![endif]--><div class="col num12" style="min-width: 320px;max-width: 650px;display: table-cell;vertical-align: top;"><div style="background-color: transparent; width: 100% !important;"><!--[if (!mso)&(!IE)]><!--><div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;"><!--<![endif]--><div class=""><!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px;"><![endif]--><div style="color:#4A443E;line-height:120%;font-family:'Open Sans', Helvetica, Arial, sans-serif; padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px;"><div style="font-size:12px;line-height:14px;color:#4A443E;font-family:'Open Sans', Helvetica, Arial, sans-serif;text-align:left;"><p style="margin: 0;font-size: 16px; line-height: 19px; color: rgb(30, 30, 30);">$introPara<br></p></div></div><!--[if mso]></td></tr></table><![endif]--></div><!--[if (!mso)&(!IE)]><!--></div><!--<![endif]--></div></div><!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]--></div></div></div>~;
}

sub sectionHeading{
my $heading = shift;
$text .= '##### ' . $heading . ' #####\n\n';
return qq~
<!-- SECTION-HEADING -->
<div style="background-color:transparent;" clas><div style="Margin: 0 auto;min-width: 320px;max-width: 650px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #FFFFFF;" class="block-grid "><div style="border-collapse: collapse;display: table;width: 100%;background-color:#FFFFFF;"><!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="background-color:transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width: 650px;"><tr class="layout-full-width" style="background-color:#FFFFFF;"><![endif]--><!--[if (mso)|(IE)]><td align="center" width="650" style=" width:650px; padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:5px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><![endif]--><div class="col num12" style="min-width: 320px;max-width: 650px;display: table-cell;vertical-align: top;"><div style="background-color: transparent; width: 100% !important;"><!--[if (!mso)&(!IE)]><!--><div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;"><!--<![endif]--><div class=""><!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 5px; padding-left: 5px; padding-top: 5px; padding-bottom: 5px;"><![endif]--><div style="color:#555555;line-height:150%;font-family:Tahoma, Verdana, Segoe, sans-serif; padding-right: 5px; padding-left: 5px; padding-top: 5px; padding-bottom: 5px;"><div style="font-size:12px;line-height:18px;font-family:Tahoma,Verdana,Segoe,sans-serif;color:#555555;text-align:left;"><p style="margin: 0;text-align: center; color: #556600; font-size: 24px; line-height: 30px;"><!-- SECTION HEADING -->$heading<br></p></div></div><!--[if mso]></td></tr></table><![endif]--></div><!--[if (!mso)&(!IE)]><!--></div><!--<![endif]--></div></div><!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]--></div></div></div>~;
}

sub mailItem{
my ($item_title, $item_text, $item_image, $item_link, $button_text) = @_;
$text .= $item_title . '\n' . $item_text . '\n' . $item_link . '\n\n';
return qq~
<!-- MAIL ITEM -->
<div style="background-color:transparent;"><div style="margin: 0 auto;min-width: 320px;max-width: 650px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #FFFFFF;" class="block-grid two-up "><div style="border-collapse: collapse;display: table;width: 100%;background-color:#FFFFFF;"><!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="background-color:transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width: 650px;"><tr class="layout-full-width" style="background-color:#FFFFFF;"><![endif]--><!--[if (mso)|(IE)]><td align="center" width="325" style=" width:325px; padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:5px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><![endif]--><div class="col num6" style="min-width: 320px;max-width: 325px;display: table-cell;vertical-align: top;"><div style="background-color: transparent; width: 100% !important;"><!--[if (!mso)&(!IE)]><!--><div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;"><!--<![endif]--><div align="center" class="img-container center autowidth fullwidth " style="padding-right: 5px; padding-left: 5px;"><!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr style="line-height:0px;line-height:0px;"><td style="padding-right: 5px; padding-left: 5px;" align="center"><![endif]--><div style="line-height:5px;font-size:1px">&#160;</div><a href="$item_link" target="_blank"><img class="center autowidth fullwidth" align="center" border="0" src="$item_image" alt="Image" title="$item_title" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;width: 100%;max-width: 315px" width="315"></a><div style="line-height:5px;font-size:1px">&#160;</div><!--[if mso]></td></tr></table><![endif]--></div><!--[if (!mso)&(!IE)]><!--></div><!--<![endif]--></div></div><!--[if (mso)|(IE)]></td><td align="center" width="325" style=" width:325px; padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:5px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><![endif]--><div class="col num6" style="min-width: 320px;max-width: 325px;display: table-cell;vertical-align: top;"><div style="background-color: transparent; width: 100% !important;"><!--[if (!mso)&(!IE)]><!--><div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;"><!--<![endif]--><div class=""><!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 5px; padding-left: 5px; padding-top: 5px; padding-bottom: 5px;"><![endif]--><div style="color:#000000;line-height:120%;font-family:'Open Sans', Helvetica, Arial, sans-serif; padding-right: 5px; padding-left: 5px; padding-top: 5px; padding-bottom: 5px;"><div style="font-size:12px;line-height:14px;font-family:'Open Sans',Helvetica,Arial,sans-serif;color:#000000;text-align:left;"><p style="margin: 0;font-size: 16px; line-height: 19px; font-weight: bold; color: #000000;"><strong><a href="$item_link" target="_blank" style="color: #556600; text-decoration: none;">$item_title</a></strong><br></p><p style="margin: 0;color: rgb(0, 0, 0); font-size: 14px; line-height: 16px;">&#160;<br></p><p style="margin: 0;font-size: 16px; line-height: 19px; color: rgb(0, 0, 0);">$item_text</p><p style="margin: 0;color: rgb(74, 68, 62); font-size: 14px; line-height: 16px;">&#160;<br></p></div></div><!--[if mso]></td></tr></table><![endif]--></div><div align="center" class="button-container center " style="padding-right: 10px; padding-left: 10px; padding-top:0; padding-bottom:10px;"><!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-spacing: 0; border-collapse: collapse; mso-table-lspace:0pt; mso-table-rspace:0pt;"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top:10px; padding-bottom:10px;" align="center"><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word" href="$item_link" style="height:34pt; v-text-anchor:middle; width:91pt;" arcsize="9%" strokecolor="#556600" fillcolor="#556600"><w:anchorlock/><v:textbox inset="0,0,0,0"><center style="color:#ffffff; font-family:'Open Sans', Helvetica, Arial, sans-serif; font-size:18px;"><![endif]--><a href="$item_link" target="_blank" style="display: block;text-decoration: none;-webkit-text-size-adjust: none;text-align: center;color: #ffffff; background-color: #556600; border-radius: 4px; -webkit-border-radius: 4px; -moz-border-radius: 4px; max-width: 122px; width: 82px;width: auto; border-top: 0px solid transparent; border-right: 0px solid transparent; border-bottom: 0px solid transparent; border-left: 0px solid transparent; padding-top: 5px; padding-right: 20px; padding-bottom: 5px; padding-left: 20px; font-family: 'Open Sans', Helvetica, Arial, sans-serif;mso-border-alt: none"><span style="font-size:16px;line-height:32px;">$button_text</span></a><!--[if mso]></center></v:textbox></v:roundrect></td></tr></table><![endif]--></div><!--[if (!mso)&(!IE)]><!--></div><!--<![endif]--></div></div><!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]--></div></div></div>~;
}

sub divider{
$text .= '\n';
return qq~
<!-- DIVIDER -->
<hr style="border-top: 1px solid rgba(0,0,0,0.3);"/>~;
}


sub mailFooter{
my $id = shift;
$text .= '\n=============================================\nToo many emails? Click here to unsubscribe from our auto-match service:\n' . $baseURL . '/profile?id=' . $id .'\n\n';
return qq~
<!-- FOOTER -->
<div style="background-color:transparent;"><div style="Margin: 0 auto;min-width: 320px;max-width: 650px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: #FFFFFF;" class="block-grid mixed-two-up "><div style="border-collapse: collapse;display: table;width: 100%;background-color:#FFFFFF;"><!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="background-color:transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width: 650px;"><tr class="layout-full-width" style="background-color:#FFFFFF;"><![endif]--><!--[if (mso)|(IE)]><td align="center" width="433" style=" width:433px; padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:5px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><![endif]--><div class="col num8" style="display: table-cell;vertical-align: top;min-width: 320px;max-width: 432px;"><div style="background-color: transparent; width: 100% !important;"><!--[if (!mso)&(!IE)]><!--><div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;"><!--<![endif]--><div class=""><!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px;"><![endif]--><div style="color:#555555;line-height:120%;font-family:'Open Sans', Helvetica, Arial, sans-serif; padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px;"><div style="font-size:12px;line-height:14px;color:#303030;font-family:'Open Sans', Helvetica, Arial, sans-serif;text-align:left;"><p style="margin: 0;font-size: 14px;line-height: 17px">Too many emails? No problem, just <a style="color:#0068A5;text-decoration: underline;" title="Unsubscribe from auto-match" href="$baseURL/profile.cgi?a=unsubscribe_matchme&token=$authcode" target="_blank" rel="noopener">click here</a> and we'll remove you from our auto-matching list. You can always opt in or out at any time from your <a style="color:#0068A5;text-decoration: underline;" title="My profile" href="$baseURL/edit" target="_blank" rel="noopener">profile settings</a>.<br></p></div></div><!--[if mso]></td></tr></table><![endif]--></div><!--[if (!mso)&(!IE)]><!--></div><!--<![endif]--></div></div><!--[if (mso)|(IE)]></td><td align="center" width="217" style=" width:217px; padding-right: 0px; padding-left: 0px; padding-top:5px; padding-bottom:5px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><![endif]--><div class="col num4" style="display: table-cell;vertical-align: top;max-width: 320px;min-width: 216px;"><div style="background-color: transparent; width: 100% !important;"><!--[if (!mso)&(!IE)]><!--><div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:5px; padding-bottom:5px; padding-right: 0px; padding-left: 0px;"><!--<![endif]--><div align="center" class="img-container center autowidth " style="padding-right: 0px; padding-left: 0px;"><!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr style="line-height:0px;line-height:0px;"><td style="padding-right: 0px; padding-left: 0px;" align="center"><![endif]--><a href="$baseURL/donate" target="_blank"><img class="center autowidth " align="center" border="0" src="$baseURL/favicon-32x32.png" alt="Image" title="Image" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;width: 100%;max-width: 32px" width="32"></a><!--[if mso]></td></tr></table><![endif]--></div><div class=""><!--[if mso]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px;"><![endif]--><div style="color:#555555;line-height:120%;font-family:Tahoma, Verdana, Segoe, sans-serif; padding-right: 10px; padding-left: 10px; padding-top: 10px; padding-bottom: 10px;"><div style="font-size:12px;line-height:14px;font-family:Tahoma,Verdana,Segoe,sans-serif;color:#555555;text-align:center;"><p style="margin: 0;font-size: 14px;line-height: 17px; text-align: center"><a href="$baseURL/donate" target="_blank">Support Sharebay</a></p></div></div><!--[if mso]></td></tr></table><![endif]--></div><div align="center" style="padding-right: 10px; padding-left: 10px; padding-bottom: 10px;" class=""><div style="line-height:10px;font-size:1px">&#160;</div><div style="display: table; max-width:188px;"><!--[if (mso)|(IE)]><table width="168" cellpadding="0" cellspacing="0" border="0"><tr><td style="border-collapse:collapse; padding-right: 10px; padding-left: 10px; padding-bottom: 10px;" align="center"><table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse; mso-table-lspace: 0pt;mso-table-rspace: 0pt; width:168px;"><tr><td width="32" style="width:32px; padding-right: 5px;" valign="top"><![endif]--><table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;Margin-right: 5px"><tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top"><a href="https://www.facebook.com/sharebay.org/" title="Facebook" target="_blank"><img src="$baseURL/i/facebook\@2x.png" alt="Facebook" title="Facebook" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important"></a><div style="line-height:5px;font-size:1px">&#160;</div></td></tr></tbody></table><!--[if (mso)|(IE)]></td><td width="32" style="width:32px; padding-right: 5px;" valign="top"><![endif]--><table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;Margin-right: 5px"><tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top"><a href="https://twitter.com/sharebayorg" title="Twitter" target="_blank"><img src="$baseURL/i/twitter\@2x.png" alt="Twitter" title="Twitter" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important"></a><div style="line-height:5px;font-size:1px">&#160;</div></td></tr></tbody></table><!--[if (mso)|(IE)]></td><td width="32" style="width:32px; padding-right: 0;" valign="top"><![endif]--><table align="left" border="0" cellspacing="0" cellpadding="0" width="32" height="32" style="border-collapse: collapse;table-layout: fixed;border-spacing: 0;mso-table-lspace: 0pt;mso-table-rspace: 0pt;vertical-align: top;Margin-right: 0"><tbody><tr style="vertical-align: top"><td align="left" valign="middle" style="word-break: break-word;border-collapse: collapse !important;vertical-align: top"><a href="https://www.youtube.com/channel/UCCZobyQQGm4u9F96Eaa2KaQ" title="YouTube" target="_blank"><img src="$baseURL/i/youtube\@2x.png" alt="YouTube" title="YouTube" width="32" style="outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;clear: both;display: block !important;border: none;height: auto;float: none;max-width: 32px !important"></a><div style="line-height:5px;font-size:1px">&#160;</div></td></tr></tbody></table><!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]--></div></div><!--[if (!mso)&(!IE)]><!--></div><!--<![endif]--></div></div><!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]--></div></div></div><!--[if (mso)|(IE)]></td></tr></table><![endif]--></td></tr></tbody></table><!--[if (mso)|(IE)]></div><![endif]--></body></html>~;
}

$SBdb->disconnect;
# Exeunt
