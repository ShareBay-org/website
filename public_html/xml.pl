#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT CONTAINS READABLE USER INFORMATION
# AND INSTRUCTIONS

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );

require 'common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);


if ($a eq 'validate'){
my ($e, $t) = &validateXML($FORM{url});
print $t;
}


sub validateXML{
my $url = shift;
my $result;
my $errors = 0;

my $urlRegex = '^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z0-9\x{00a1}-\x{ffff}][a-z0-9\x{00a1}-\x{ffff}_-]{0,62})?[a-z0-9\x{00a1}-\x{ffff}]\.)+(?:[a-z\x{00a1}-\x{ffff}]{2,}\.?))(?::\d{2,5})?(?:[\/?#]\S*)?$';

use LWP::UserAgent;
my $ua = LWP::UserAgent->new;
$ua->agent('Mozilla/5.0');
$ua->default_header('Accept-Encoding' => scalar HTTP::Message::decodable());
$ua->timeout(20);
my $req = $ua->get($url);
if ($req->is_success){
my $xml = $req->decoded_content;
if ($xml){
	
use XML::LibXML;

my $parser = XML::LibXML->new({ line_numbers => 1 });
my $dom = $parser->load_xml(string => $xml);

# CHECK IF IT'S AN INDEX FILE. IF IT IS, ITERATE THROUGH FILES
if ($dom->findnodes("/index")) {
foreach ($dom->findnodes('/index')){
my $file = $_->findvalue('./file');
if ($file){
if ($file =~ /$urlRegex/iu){
my ($e, $r);
# PROCESS FILE WITHOUT LOOPING THE SAME FILE
($e, $r) = &validateXML($file) unless $file =~ /$url/;
$errors += $e;
$result .= $r;
}else{
$result .= "❌ Invalid URL specified in index!\n";
}
}else{
$result .= "❌ No file specified in index!\n";
$errors++;
}
}

# NO INDEX FOUND. OK LET'S VALIDATE LIST CONTENTS
}else{
if (!$dom->findnodes('/freelist')){
$result .= "❌ The freelist tag is missing!\n";
$errors++;
}
if (!$dom->findnodes('/freelist/header')){
$result .= "❌ The header tag is missing!\n";
$errors++;
}
if (!$dom->findvalue('/freelist/header/appID')){
$result .= "❌ No appID specified!\n";
$errors++;
}
if (!$dom->findvalue('/freelist/header/date')){
$result .= "❌ No date specified!\n";
$errors++;
}elsif ($dom->findvalue('/freelist/header/date') !~ /^\d{4}-[01]\d-[0-3]\d$/){
$result .= "❌ Wrong date format! (Should be yyyy-mm-dd)\n";
$errors++;
}
if (!$dom->findnodes('/freelist/list')){
$result .= "❌ The list tag is missing!\n";
$errors++;
}
if (!$dom->findnodes('/freelist/list/item')){
$result .= "❌ No items found, or item tag is missing!\n";
$errors++;
}else{
foreach ($dom->findnodes('/freelist/list/item')){
if (!$_->findvalue('./title')){
my $line = $dom->line_number;
$result .= "❌ No title specified in item at line $line!\n";
$errors++;
};
if (!$_->findvalue('./url')){
$result .= "❌ No URL specified in item!\n";
$errors++;
}elsif($_->findvalue('./url') !~ /$urlRegex/iu){
$result .= "❌ Invalid URL specified in item!\n";
$errors++;
};
if ($_->findvalue('./imageURL') && $_->findvalue('./imageURL') !~ /$urlRegex/iu){
$result .= "❌ Invalid imageURL specified in item!\n";
$errors++;
};
if ($_->findvalue('./terms') && $_->findvalue('./terms') !~ /^free|loan|commons|swap$/i){
$result .= "❌ Invalid terms specified in item! Expected 'free', 'loan', 'commons' or 'swap'.\n";
$errors++;
};
if ($_->findvalue('./type') && $_->findvalue('./type') !~ /^item|skill|info$/i){
$result .= "❌ Invalid type specified in item! Expected 'item', 'skill' or 'info'.\n";
$errors++;
};
if ($_->findvalue('./countryCode') && $_->findvalue('./countryCode') !~ /^[a-zA-Z]{2}$/i){
$result .= "❌ Invalid countryCode specified in item! Expected two letter code.\n";
$errors++;
};
if ($_->findvalue('./updated') && $_->findvalue('./updated') !~ /^\d{4}-[01]\d-[0-3]\d$/){
$result .= "❌ Invalid updated date value specified in item! Expected format: yyyy-mm-dd.\n";
$errors++;
};
if ($_->findvalue('./lat') && $_->findvalue('./lat') !~ /^-*\d+\.\d+$/){
$result .= "❌ Invalid lat (latitude) value specified in item! Decimal value expected.\n";
$errors++;
};
if ($_->findvalue('./long') && $_->findvalue('./long') !~ /^-*\d+\.\d+$/){
$result .= "❌ Invalid long (longitude) value specified in item! Decimal value expected.\n";
$errors++;
};
if ($_->findvalue('./lat') && $_->findvalue('./long') eq ''){
$result .= "❌ lat (latitude) specified but long (longitude) value missing.\n";
$errors++;
};
if ($_->findvalue('./long') && $_->findvalue('./lat') eq ''){
$result .= "❌ long (longitude) specified but lat (latitude) value missing.\n";
$errors++;
};
if ($_->findvalue('./quantity') && $_->findvalue('./quantity') =~ /^\d+$/){
unless ($_->findvalue('./quantity')	> 0){
$result .= "❌ quantity specifed must be greater than zero.\n";
$errors++;
}
}else{
$result .= "❌ quantity is not an integer in item.\n";
$errors++;
}
}
}
}
}else{$result .= "❌ File is empty!\n"; $errors++;}
}else{$result .= "❌ " . $req->status_line() . "\n"; $errors++;}
if ($errors){
return $errors, "File had $errors errors:\n\n$result";
}else{
return 0, "✔️ Freelist XML file is valid.\n";
}
}

if ($a eq 'import'){
print &importXML($FORM{url});
}


sub importXML{
my $url = shift;
use LWP::UserAgent;

my $ua = LWP::UserAgent->new;
$ua->agent('Mozilla/5.0');
$ua->default_header('Accept-Encoding' => scalar HTTP::Message::decodable());
$ua->timeout(20);

## GET DATA
my $req = $ua->get($url);
if ($req->is_success){
my $xml = $req->decoded_content;
if ($xml){
	
use XML::LibXML;
my $dom = XML::LibXML->load_xml(string => $xml);

## CHECK IF IT'S AN INDEX FILE. IF IT IS, ITERATE THROUGH FILES
if ($dom->findnodes("/index")) {
foreach ($dom->findnodes('/index/file')){
my $file = $_->findvalue('./file');
&importXML($file) unless $file =~ m/$url/i; # PROCESS WITHOUT LOOPING THE SAME FILE
}

## NO INDEX FOUND. OK LET'S CHECK FOR A VALID HEADER AND ITEMS
}elsif($dom->findnodes('/freelist/header/appID') && $dom->findnodes('/freelist/header/date') && $dom->findnodes("/freelist/list/item")){
## OK IT HAS A VALID HEADER AND ITEMS. LETS GET THE HEADER...
my $appID = $dom->findvalue('/freelist/header/appID');
my $date = $dom->findvalue('/freelist/header/date');
my $appName = $dom->findvalue('/freelist/header/appName');
my $appDesc = $dom->findvalue('/freelist/header/appDesc');

# CHECK FOR A VALID FILE DATE
if ($date =~ /^\d{4}-[01]\d-[0-3]\d$/){

## CHECK IF FILE DATE SUPERCEDES EXISTING DATA IF YOU WANT...
my $lastdate = '2022-11-21'; # RETRIEVE THIS FROM PREVIOUS LOAD
if ($date ne $lastdate){

## OK LET'S LOOP THROUGH AND GET THE ITEMS...
my $count = 0;
my $sth = $SBdb->prepare("INSERT INTO `xml_test` (appID, foreign_id, title, description, url, type, quantity, category, terms, imageURL, lat, long, city, state, countryName, countryCode, language, updated), VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)");
foreach ($dom->findnodes('/freelist/list/item')){
	
my $itemID = $_->findvalue('./itemID');
my $title = $_->findvalue('./title');
my $url = lc($_->findvalue('./url')); # FORCE URL TO LOWER CASE
my $description = $_->findvalue('./description');
my $type = lc($_->findvalue('./type'));
my $quantity = int($_->findvalue('./quantity')) || 1; # INTEGER / DEFAULTS TO 1 IF NOT SPECIFIED
my $category = $_->findvalue('./category');
my $terms = lc($_->findvalue('./terms'));
my $imageURL = lc($_->findvalue('./imageURL')); # FORCE IMAGEURL TO LOWER CASE
my $lat = $_->findvalue('./lat');
my $long = $_->findvalue('./long');
my $city = $_->findvalue('./city');
my $state = $_->findvalue('./state');
my $countryName = $_->findvalue('./countryName');
my $countryCode = uc($_->findvalue('./countryCode'));
my $language = $_->findvalue('./language');
my $updated = $_->findvalue('./updated');

	
## VALIDATE AND CONFORM

# CLEAN TITLE AND CUT AT 100 CHARACTERS
$title = &cleanText($title);
$title = substr($title, 0, 100) . '...' if length($title) > 100;

# CLEAN DESCRIPTION AND CUT AT 500 CHARACTERS
$description = &cleanText($description);
$description = substr($description, 0, 500) . '...' if length($description) > 500; 

# FORCE ITEM TYPE IF MISSING OR MALFORMED
$type = 'item' if ($type != 'skill' && $type != 'info'); 

# FORCE FREE TERMS IF MISSING OR MALFORMED
$terms = 'free' if ($terms != 'loan' && $terms != 'commons' && $terms != 'swap'); 

# INITIALISE LAT & LONG IF NOT DECIMAL TO PREVENT MAP ERRORS
$lat = '' if $lat !~ /-*\d+\.\d+/;
$long = '' if $long !~ /-*\d+\.\d+/;

# INITIALISE COUNTRYCODE IF NOT A 2 LETTER STRING
$countryCode = '' if $countryCode !~ /[a-zA-Z]{2}/; 

# INITIALISE IF LANGUAGE NOT 2 LETTERS FOLLOWED BY DASH AND 2 LETTERS
$language = '' if $language !~ /[a-zA-Z]{2}-[a-zA-Z]{2}/;

# USE FILE DATE IF MISSING OR MALFORMED
$updated = $date if $updated !~ /\d{4}-[01]\d-[0-3]\d/; 

## IF LISTING HAS A TITLE AND URL. SAVE IT
## ADD ANY OTHER DATA VALIDATION HERE... EG. FILTER ITEMS WITH NO LAT / LONG
if ($title && $url){
$count++;
# $sth->execute("$appID", "$itemID", "$title", "$description", "$url", "$type", "$quantity", "$category", "$terms", "$imageURL", "$lat", "$long", "$city", "$state", "$countryName", "$countryCode", "$language", "$updated");
}
}
return "$count items imported from $appName ($appID). Filedate: $date";
}else{return "This file already been imported! ($lastdate)"};
}else{return "Invalid file date. XML file must include a valid yyyy-mm-dd date in the header."};
}else{return 'No usable data found!';}
}else{return 'Empty file!';}
}else{return $req->status_line();}
}


if ($a eq 'export'){
print &exportXML;
}


sub exportXML{
my $app_id = 'sharebay.org';
my $appName = 'Sharebay';
my $appDesc = 'The Sharing Network';
my $date = &getW3CDate($now);

use XML::Writer;
my $x = XML::Writer->new(OUTPUT => 'self', DATA_MODE => 1, DATA_INDENT => 2, );
$x->xmlDecl('UTF-8', standalone => 'yes');
$x->pi('xml-stylesheet', 'href="XML-styles.xsl" type="text/xsl"');
$x->comment("These are the latest free offer listings from Sharebay.org which you are free to use as you wish providing that you a) Include backlinks to the originating site, and b) Do not use the data in any way other than to display free listing information. Use of this file signifies your acceptance of these terms.");
$x->startTag('freelist');
$x->startTag('header');
$x->startTag('appID'); $x->characters($app_id); $x->endTag();
$x->startTag('appName'); $x->characters($appName); $x->endTag();
$x->startTag('appDesc'); $x->characters($appDesc); $x->endTag();
$x->startTag('date'); $x->characters($date); $x->endTag();
$x->endTag();
$x->startTag('list');

my $getListings = $SBdb->prepare("SELECT p.id, p.title, p.description, p.quantity, p.physical, p.category, p.terms, p.image, p.tags, p.lat, p.lon, p.timestamp, c.category, c.transactable, m.city, m.region, m.country, m.country_iso, m.language FROM posts AS p JOIN categories AS c ON c.id = p.category JOIN members AS m ON m.id = p.lister WHERE p.type = 'offer' AND p.status = 'live'");
$getListings->execute;

if ($getListings->rows > 0){
while (my ($id, $title, $description, $quantity, $physical, $category, $terms, $image, $tags, $lat, $lon, $timestamp, $cat_name, $transactable, $city, $region, $country, $country_iso, $language) = $getListings->fetchrow_array){
my $type = 'item';
$type = 'skill' if ($physical eq 0 && $transactable eq 1);
$type = 'info' if ($transactable eq 0);
$image = $baseURL . '/listing_pics/' . $image . '.jpg' if $image;

$x->startTag('item');
$x->startTag('itemID'); $x->characters($id); $x->endTag();
$x->startTag('title'); $x->characters(&descTitle($title, $description)); $x->endTag();
$x->startTag('description'); $x->characters(&descSummary($description)); $x->endTag();
$x->startTag('type'); $x->characters($type); $x->endTag();
$x->startTag('quantity'); $x->characters($quantity); $x->endTag();
$x->startTag('category'); $x->characters($cat_name); $x->endTag();
$x->startTag('terms'); $x->characters($terms); $x->endTag();
$x->startTag('imageURL'); $x->characters($image); $x->endTag();
$x->startTag('tags'); $x->characters($tags); $x->endTag();
$x->startTag('url'); $x->characters($baseURL . '/listing?id=' . $id); $x->endTag();
$x->startTag('lat'); $x->characters($lat); $x->endTag();
$x->startTag('long'); $x->characters($lon); $x->endTag();
$x->startTag('city'); $x->characters($city); $x->endTag();
$x->startTag('state'); $x->characters($region); $x->endTag();
$x->startTag('countryName'); $x->characters($country); $x->endTag();
$x->startTag('countryCode'); $x->characters($country_iso); $x->endTag();
$x->startTag('language'); $x->characters($language . '-' . $country_iso); $x->endTag();
$x->startTag('updated'); $x->characters(&getW3CDate($timestamp)); $x->endTag();
$x->endTag();
}
}

$x->endTag();
$x->endTag();

my $xml = $x->end();
	
open my $FH, '>', "$siteroot/freelist.xml" or die "Can't create XML file!";
print $FH $xml;
close $FH;
my $opt = qq~XML created. I tink.\n~;

use IO::Compress::Gzip qw(gzip $GzipError);
my $input = "$siteroot/freelist.xml";
my $output = "$siteroot/freelist.xml.gz";
gzip $input => $output;
$opt .= qq~GZ created. I tink.\n~;
return $opt;
}


1;
# Exeunt
