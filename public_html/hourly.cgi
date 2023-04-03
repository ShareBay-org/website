#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR HOURLY CRON JOBS

# use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );
my $active = 1; # 0 to disable
require '/home/sharebay/public_html/common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

if ($maintenance){$active = 0}; # DISABLE IN MAINTENANCE MODE

&textHeader;
if ($active){
# &bumpListing;
&bumpRecentBlog;
&tweetListing;
$SBdb->disconnect;
}


sub bumpListing{
unless ($SBdb->do("SELECT id FROM activity WHERE object_type = 'listing' AND timestamp > ($now - 3600)") > 0){
my $oldest = $now - 31000000; # IN THE LAST YEAR
my $newest = $now; # MORE THAN 5 DAYS AGO
my $getListing = $SBdb->prepare("SELECT p.id FROM posts AS p WHERE NOT EXISTS (SELECT id FROM spam_reports WHERE object_type = 'listing' AND object_id = p.id) AND p.status = 'live' AND p.timestamp BETWEEN $oldest AND $newest ORDER BY RAND() LIMIT 1");
$getListing->execute;
if ($getListing->rows eq 1){
## BUMP AWAY
my $id = $getListing->fetchrow_array;
my $getTargetID = $SBdb->prepare("SELECT MAX(id) + 1 FROM activity");
$getTargetID->execute;
my $target = $getTargetID->fetchrow_array;
$SBdb->do("UPDATE activity SET id = $target WHERE object_type = 'listing' AND object_id = $id LIMIT 1");
$getTargetID->finish;
$getListing->finish;
}
}
}


sub bumpRecentBlog{
my $recent = $now - 500000; # 5 DAYS AGO
my $getBlog = $SBdb->prepare("SELECT id FROM blog WHERE timestamp > $recent ORDER BY id DESC");
$getBlog->execute;
if ($getBlog->rows eq 1){
## BUMP AWAY
my $id = $getBlog->fetchrow_array;
my $getTargetID = $SBdb->prepare("SELECT MAX(id) + 1 FROM activity");
$getTargetID->execute;
my $target = $getTargetID->fetchrow_array;
$SBdb->do("UPDATE activity SET id = $target WHERE object_type = 'blog' AND object_id = $id LIMIT 1");
$getTargetID->finish;
$getBlog->finish;
}
}



sub tweetListing{
my $getLatest = $SBdb->prepare("SELECT id FROM posts WHERE status = 'live' AND timestamp > ($now - 3600) ORDER BY id DESC LIMIT 1");
$getLatest->execute;
if ($getLatest->rows eq 1){
## TWEET LATEST
my $id = $getLatest->fetchrow_array;
&sendTweet('listing', $id);
}else{
## TWEET OLD LISTING
my $oldest = $now - 31000000; # IN THE LAST YEAR
my $newest = $now; # MORE THAN 5 DAYS AGO
my $getListing = $SBdb->prepare("SELECT p.id FROM posts AS p WHERE NOT EXISTS (SELECT id FROM spam_reports WHERE object_type = 'listing' AND object_id = p.id) AND p.status = 'live' AND p.image != '' AND p.timestamp BETWEEN $oldest AND $newest ORDER BY RAND() LIMIT 1");
$getListing->execute;
if ($getListing->rows eq 1){
my $id = $getListing->fetchrow_array;
&sendTweet('listing', $id);
}
$getListing->finish;
}
$getLatest->finish;
}



sub sendTweet{
my ($object_type, $object_id) = @_;
my $max_length = 280;
if ($object_type, $object_id){
my $tweet;
if ($object_type eq 'listing'){
my $getListing = $SBdb->prepare("SELECT p.title, p.description, p.type, m.first_name FROM posts AS p JOIN members AS m ON m.id = p.lister WHERE p.id = '$object_id' LIMIT 1");
$getListing->execute;
my ($title, $desc, $type, $name) = $getListing->fetchrow_array;
$getListing->finish;
my $link = qq~ $baseURL/listing?id=$object_id~; #LEADING SPACE INTENTIONAL
my $remaining = $max_length - length($link);
if ($type eq 'offer'){$tweet = 'FREE: ';}
elsif($type eq 'request'){$tweet = 'Can you help? ';}
$title = substr($desc, 0, 100) . '...' if (!$title);
$tweet .= $title;
if ($type eq 'offer'){$tweet .= '. Offered by ' . $name;}
elsif($type eq 'request'){$tweet .= '. Requested by ' . $name;}
$tweet = substr($tweet, 0, ($remaining - 3)) . '...' if length($tweet) > $remaining;
$tweet .= $link;
}
use Net::Twitter;	
my $api_key = 'cIkcx9hetEmvogqiUs8VHcJmA';
my $api_key_secret = 'ujH0mATd86oyZDKrOWFaZmtFY7gXyEwTMEVlYu4P2QTNQEg0iN';
my $access_token = '1045730745677942786-dsgvcYMH4JORSVEIw1ehEzxSyQSQ0x';
my $access_token_secret = 'WebaVeUbvtZu5yGxLEswnSJJyMBt3SNo1xNj4WhJoJTGh';
my $nt = Net::Twitter->new(
traits   => [qw/API::RESTv1_1/],
consumer_key        => $api_key,
consumer_secret     => $api_key_secret,
access_token		 => $access_token,
access_token_secret => $access_token_secret,
);
my $t = $nt->update($tweet);
}
}
# Exeunt
