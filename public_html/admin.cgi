#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR ADMIN FUNCTIONS AND TESTING
# AND IS ONLY AVAILABLE TO THOSE WITH ADMIN ACCESS

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );
require 'common.pl';
require '/home/sharebay/public_html/get_location.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

# SET ENABLE TO 0 TO PREVENT ACCIDENTAL OPERATIONS
my $enable = 1;

# HTTP CONTENT HEADER
;

my $result; # VARIABLE FOR FINAL OUTPUT

# GLOBAL OPERATION ADMIN TEST
if ($LOGGED_IN && $myAdmin && $enable){
# if (1 > 0){ # EMERGENCY ONLY! 

if ($a eq 'hashpw'){
# $result .= &hashPW($FORM{pw});
$result .= &hashPW('}+{_P0o9i8');
}

if ($a eq 'updateviews'){
my $object_type = 'total';
my $getSnapshot = $SBdb->prepare("SELECT id, timestamp FROM snapshot");
$getSnapshot->execute;
while (my ($id, $timestamp) = $getSnapshot->fetchrow_array){
my $lastDay = $timestamp - 86400;
# my $views = int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND object_type = '$object_type' AND actor_id REGEXP '^[0-9]+\$' AND timestamp > $lastDay AND timestamp <= $timestamp")) || 0;
my $views = int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND timestamp > $lastDay AND timestamp <= $timestamp")) || 0;
my $update = $SBdb->do("UPDATE snapshot SET $object_type\_views = $views WHERE id = $id LIMIT 1");
}
$getSnapshot->finish;
$result .= 'Done. I tink.';
}


if ($a eq 'get_convo_id'){
$result .= &getConvoID(30, 61842);
}


if ($a eq 'setranking'){
my $timespan = 30 * 86400; ## FIRST = DAYS
my $viewPoints = 1;
my $likePoints = 3;
my $commentPoints = 5;
my $transPoints = 10;

{ ## LISTINGS
my $rank = 0;
my $getListings = $SBdb->prepare("SELECT id FROM posts WHERE status = 'live'");
my $updateRank = $SBdb->prepare("UPDATE posts SET rank = ? WHERE id = ?");
$getListings->execute;
while (my $id = $getListings->fetchrow_array){
$rank += $viewPoints * int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND object_type = 'listing' AND object_id = '$id' AND actor_id REGEXP '^[0-9]+\$' AND timestamp > ($now - $timespan)")) || 0;
$rank += $likePoints * int($SBdb->do("SELECT id FROM interactions WHERE action = 'like' AND object_type = 'listing' AND object_id = '$id' AND timestamp > ($now - $timespan)")) || 0;
$rank += $commentPoints * int($SBdb->do("SELECT DISTINCT actor_id FROM interactions WHERE action = 'comment' AND object_type = 'listing' AND object_id = '$id' AND timestamp > ($now - $timespan)")) || 0;
$rank += $transPoints * int($SBdb->do("SELECT id FROM transactions WHERE listing_id = '$id' AND timestamp > ($now - $timespan)")) || 0;
$updateRank->execute("$rank", "$id");
$rank = 0;
}
$getListings->finish;
}

{ ## PROFILES
my $rank = 0;
my $getMembers = $SBdb->prepare("SELECT id FROM members WHERE activated = 1");
my $updateRank = $SBdb->prepare("UPDATE members SET rank = ? WHERE id = ?");
$getMembers->execute;
while (my $id = $getMembers->fetchrow_array){
$rank += $viewPoints * int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND object_type = 'profile' AND object_id = '$id' AND actor_id REGEXP '^[0-9]+\$' AND timestamp > ($now - $timespan)")) || 0;
$rank += $likePoints * int($SBdb->do("SELECT id FROM interactions WHERE action = 'like' AND object_type = 'profile' AND object_id = '$id' AND timestamp > ($now - $timespan)")) || 0;
$rank += $commentPoints * int($SBdb->do("SELECT DISTINCT actor_id FROM interactions WHERE action = 'comment' AND object_type = 'profile' AND object_id = '$id' AND timestamp > ($now - $timespan)")) || 0;
$updateRank->execute("$rank", "$id");
$rank = 0;
}
$getMembers->finish;
}

{ ## BLOGS
my $rank = 0;
my $getBlog = $SBdb->prepare("SELECT id FROM blog");
my $updateRank = $SBdb->prepare("UPDATE blog SET rank = ? WHERE id = ?");
$getBlog->execute;
while (my $id = $getBlog->fetchrow_array){
$rank += $viewPoints * int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND object_type = 'blog' AND object_id = '$id' AND actor_id REGEXP '^[0-9]+\$' AND timestamp > ($now - $timespan)")) || 0;
$rank += $likePoints * int($SBdb->do("SELECT id FROM interactions WHERE action = 'like' AND object_type = 'blog' AND object_id = '$id' AND timestamp > ($now - $timespan)")) || 0;
$rank += $commentPoints * int($SBdb->do("SELECT DISTINCT actor_id FROM interactions WHERE action = 'comment' AND object_type = 'blog' AND object_id = '$id' AND timestamp > ($now - $timespan)")) || 0;
$updateRank->execute("$rank", "$id");
$rank = 0;
}
$getBlog->finish;
}
$result .= qq~<p class="success">Ranking complete</p>~;
}


if ($a eq 'compilelistings'){
my $getSnapshot = $SBdb->prepare("SELECT id, timestamp FROM snapshot");
my $update = $SBdb->prepare("UPDATE snapshot SET total_listings = ? WHERE id = ?");
$getSnapshot->execute;
while (my ($id, $timestamp) = $getSnapshot->fetchrow_array){
my $total_listings = int($SBdb->do("SELECT id FROM posts WHERE status = 'live' AND timestamp <= $timestamp")) || 0;
$update->execute($total_listings, $id);
}
$result .= 'Listings compiled. I tink';
}

if ($a eq 'resetmailme'){
if ($SBdb->do("UPDATE members SET mailme_sent = 0")){
$result .= '<p class="success">Mailme reset to 0</p>';
}else{
$result .= '<p class="error">Couldn\'t reset mailme!</p>';
}
}



# use Net::Twitter;	
# my $api_key = 'cIkcx9hetEmvogqiUs8VHcJmA';
# my $api_key_secret = 'ujH0mATd86oyZDKrOWFaZmtFY7gXyEwTMEVlYu4P2QTNQEg0iN';
# my $access_token = '1045730745677942786-dsgvcYMH4JORSVEIw1ehEzxSyQSQ0x';
# my $access_token_secret = 'WebaVeUbvtZu5yGxLEswnSJJyMBt3SNo1xNj4WhJoJTGh';
# my $nt = Net::Twitter->new(
# traits   => [qw/API::RESTv1_1/],
# consumer_key        => $api_key,
# consumer_secret     => $api_key_secret,
# access_token		 => $access_token,
# access_token_secret => $access_token_secret,
# );
# my $t = $nt->update($tweet);




if ($a eq 'tweetopenaccessguy'){

my $api_key = 'qBMMOQJ1vnBtsaU7levsqLX4C';
my $api_key_secret = 'lRQkmrzPMooaVUAtvlcerrzRnTZF7BILVgB5BqzoJQTxCUID0P';
my $access_token = '260989988-dZVqEmNwfZzPYySJJPlEZeI7qORHzgGqox3NL7nW';
my $access_token_secret = 'vY65ab7JNKkMHDMUAt4EJZObqVFg0nSH0KYIDntYhIKcC';

use Net::Twitter;
my $nt = Net::Twitter->new(
traits   => [qw/API::RESTv1_1/],
consumer_key        => $api_key,
consumer_secret     => $api_key_secret,
access_token		 => $access_token,
access_token_secret => $access_token_secret,
);

if ($nt->update('What do you think would happen if everything was free?')){
$result .= 'Tweeted. I tink';
}else{
$result .= 'Not sure if that worked to be honest with you.';
}
}


if ($a eq 'createsnapshot'){

my $day = 86400;
my $firstDay = $now - ($day * 49);
my $lastDay = $now - ($day * 1);
# my $insert = $SBdb->prepare("INSERT INTO snapshot (timestamp, total_members) VALUES (?,?)");

my $insert = $SBdb->prepare("INSERT INTO snapshot (timestamp, total_members, new_members, active_members, total_listings, new_listings, total_views, listing_views, profile_views, likes, comments, transactions, completed_transactions, reviews, conversations) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)");

for(my $t = $firstDay; $t <= $lastDay; $t += $day){

my $total_members = int($SBdb->do("SELECT id FROM members WHERE activated = 1 AND joined < ($t + $day)")) || 0;
my $new_members = int($SBdb->do("SELECT id FROM members WHERE activated = 1 AND joined BETWEEN $t AND $t + $day")) || 0;
my $active_members = int($SBdb->do("SELECT id FROM members WHERE activated = 1 AND last_active BETWEEN $t AND $t + $day")) || 0;
my $total_listings = int($SBdb->do("SELECT id FROM posts WHERE status = 'live' AND timestamp < ($t + $day)")) || 0;
my $new_listings = int($SBdb->do("SELECT id FROM posts WHERE status = 'live' AND timestamp BETWEEN $t AND $t + $day")) || 0;
my $total_views = int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND timestamp BETWEEN $t AND $t + $day")) || 0;
my $listing_views = int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND object_type = 'listing' AND actor_id REGEXP '^[0-9]+\$' AND timestamp BETWEEN $t AND $t + $day")) || 0;
my $profile_views = int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND object_type = 'profile' AND actor_id REGEXP '^[0-9]+\$' AND timestamp BETWEEN $t AND $t + $day")) || 0;
my $likes = int($SBdb->do("SELECT id FROM interactions WHERE action = 'like' AND timestamp BETWEEN $t AND $t + $day")) || 0;
my $comments = int($SBdb->do("SELECT id FROM interactions WHERE action = 'comment' AND timestamp BETWEEN $t AND $t + $day")) || 0;
my $transactions = int($SBdb->do("SELECT id FROM transactions WHERE timestamp BETWEEN $t AND $t + $day")) || 0;
my $completed_transactions = int($SBdb->do("SELECT id FROM transactions WHERE status = 'delivered' AND timestamp BETWEEN $t AND $t + $day")) || 0;
my $reviews = int($SBdb->do("SELECT id FROM reviews WHERE timestamp BETWEEN $t AND $t + $day")) || 0;
my $conversations = int($SBdb->do("SELECT id FROM messages WHERE type = 'message' AND timestamp BETWEEN $t AND $t + $day GROUP BY convo_id")) || 0;

# $insert->execute($t, $total_members);

$insert->execute($t, $total_members, $new_members, $active_members, $total_listings, $new_listings, $total_views, $listing_views, $profile_views, $likes, $comments, $transactions, $completed_transactions, $reviews, $conversations);
# $result .= $t . ': ' . $conversations . '<br/>';
}

$result .= 'Snapshot created. I tink';
}



if ($a eq 'createrss'){
	# create an RSS 2.0 file

my $SB_enc = $SBdb->do("SET NAMES 'latin1'");	
use XML::RSS;
use DateTime ();
# my $dt = DateTime->from_epoch(epoch => 1_500_000_000);
my $dt = DateTime->now()->strftime("%a, %d %b %Y %H:%M:%S %z");
my $rss = XML::RSS->new (version => '2.0');
$rss->add_module(prefix=>'atom', uri=>'http://www.w3.org/2005/Atom');
$rss->channel(title          => 'Sharebay - Latest Offers and Requests',
               link           => 'https://www.sharebay.org',
               language       => 'en',
               description    => 'Sharebay - Latest Offers and Requests',
               pubDate        => $dt,
               managingEditor => 'hello@sharebay.org (Sharebay admin)',
               webMaster      => 'hello@sharebay.org (Sharebay devteam)',
			   atom => {link =>{ href=>"$baseURL/listings.rss", rel=>'self', type=>'application/rss+xml' }}
               );
 
my $getListings = $SBdb->prepare("SELECT id, lister, title, description, type, image, timestamp FROM posts WHERE status = 'live' AND timestamp > ($now - 1186400)");
$getListings->execute;
if ($getListings->rows > 0){
while (my ($id, $lister, $title, $desc, $type, $image, $timestamp) = $getListings->fetchrow_array){
$title = substr($desc, 0, 50) . '...' if (!$title && length($desc) > 50);
$title .= ' (' . &getRegion($lister) . ')';
$title = uc($type) . ': ' . $title;
my $dt = DateTime->from_epoch(epoch => $timestamp)->strftime("%a, %d %b %Y %H:%M:%S %z");
if (!$image){
$rss->add_item(title => $title,
        description => $desc,
        permaLink  => "$baseURL/listing?id=$id",
        pubDate   => $dt
);
}else{
my $image_size = -s "$siteroot/listing_pics/$image\.jpg";
$rss->add_item(title => $title,
        description => $desc,
        permaLink  => "$baseURL/listing?id=$id",
        enclosure   => { url=>"$baseURL/listing_pics/$image\.jpg", length=>$image_size, type=>"image/jpeg" },
        pubDate   => $dt
);
}
}
}
$getListings->finish;
				 
$rss->save("$siteroot/listings.rss");
$result .= 'RSS created. I tink';
}


if ($a eq 'createsitemap'){
my $baseDate = '2022-07-01';
my $updated = &getW3CDate($now);

my $lastPost = $baseDate;
my $getLastPost = $SBdb->prepare("SELECT MAX(timestamp) FROM posts WHERE status = 'live'");
$getLastPost->execute;
if ($getLastPost->rows > 0){$lastPost = &getW3CDate($getLastPost->fetchrow_array)};
$getLastPost->finish;

my $lastProfile = $baseDate;
my $getLastProfile = $SBdb->prepare("SELECT MAX(joined) FROM members WHERE activated = 1");
$getLastProfile->execute;
if ($getLastProfile->rows > 0){$lastProfile = &getW3CDate($getLastProfile->fetchrow_array)};
$getLastProfile->finish;

my $lastBlog = $baseDate;
my $getLastBlog = $SBdb->prepare("SELECT MAX(timestamp) FROM blog WHERE published = 1");
$getLastBlog->execute;
if ($getLastBlog->rows > 0){$lastBlog = &getW3CDate($getLastBlog->fetchrow_array)};
$getLastBlog->finish;

my $lastTrans = $baseDate;
my $getLastTrans = $SBdb->prepare("SELECT MAX(timestamp) FROM transactions WHERE status = 'delivered'");
$getLastTrans->execute;
if ($getLastTrans->rows > 0){$lastTrans = &getW3CDate($getLastTrans->fetchrow_array)};
$getLastTrans->finish;

open (my $fh, '>', "$siteroot/sitemap.xml");
print $fh qq~<?xml version="1.0" encoding="UTF-8"?>
<!-- LAST UPDATED $updated -->
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url>
<loc>$baseURL</loc>
<lastmod>$baseDate</lastmod>
<priority>0.9</priority>
</url>
<url>
<loc>$baseURL/about</loc>
<lastmod>$baseDate</lastmod>
</url>
<url>
<loc>$baseURL/how-it-works</loc>
<lastmod>$baseDate</lastmod>
</url>
<url>
<loc>$baseURL/join</loc>
<lastmod>$baseDate</lastmod>
<priority>0.8</priority>
</url>
<url>
<loc>$baseURL/faqs</loc>
<lastmod>$baseDate</lastmod>
</url>
<url>
<loc>$baseURL/?search&amp;filter=offers</loc>
<lastmod>$lastPost</lastmod>
<priority>0.8</priority>
</url>
<url>
<loc>$baseURL/?search&amp;filter=requests</loc>
<lastmod>$lastPost</lastmod>
<priority>0.8</priority>
</url>
~;
my $getPosts = $SBdb->prepare("SELECT id, timestamp FROM posts WHERE status = 'live'");
$getPosts->execute;
if ($getPosts->rows > 0){
while (my ($id, $timestamp) = $getPosts->fetchrow_array){
my $lastMod = &getW3CDate($timestamp);
print $fh qq~<url>
<loc>$baseURL/listing?id=$id</loc>
<lastmod>$lastMod</lastmod>
</url>
~;
}
}
print $fh qq~<url>
<loc>$baseURL/page?id=categories</loc>
<lastmod>$lastPost</lastmod>
<priority>0.8</priority>
</url>
~;
my $getCats = $SBdb->prepare("SELECT c.id, MAX(p.timestamp) FROM categories AS c JOIN posts AS p ON p.category = c.id WHERE p.status = 'live' GROUP BY c.id");
$getCats->execute;
if ($getCats->rows > 0){
while (my ($id, $timestamp) = $getCats->fetchrow_array){
my $lastMod = &getW3CDate($timestamp);
print $fh qq~<url>
<loc>$baseURL/?search&amp;filter=cat_$id</loc>
<lastmod>$lastMod</lastmod>
</url>
~;
}
}
print $fh qq~<url>
<loc>$baseURL/?search&amp;filter=members</loc>
<lastmod>$lastProfile</lastmod>
</url>
~;
my $getMembers = $SBdb->prepare("SELECT id, timestamp, joined FROM members WHERE activated = 1");
$getMembers->execute;
if ($getMembers->rows > 0){
while (my ($id, $timestamp, $joined) = $getMembers->fetchrow_array){
my $lastMod;
if ($timestamp > $joined){$lastMod = &getW3CDate($timestamp)}else{$lastMod = &getW3CDate($joined)};
print $fh qq~<url>
<loc>$baseURL/profile?id=$id</loc>
<lastmod>$lastMod</lastmod>
</url>
~;
}
}
print $fh qq~<url>
<loc>$baseURL/transactions</loc>
<lastmod>$lastTrans</lastmod>
</url>
<url>
<loc>$baseURL/blog</loc>
<lastmod>$lastBlog</lastmod>
</url>
~;
my $getBlogs = $SBdb->prepare("SELECT slug, timestamp FROM blog WHERE published = 1");
$getBlogs->execute;
if ($getBlogs->rows > 0){
while (my ($slug, $timestamp) = $getBlogs->fetchrow_array){
my $lastMod = &getW3CDate($timestamp);
print $fh qq~
<url>
<loc>$baseURL/blog/$slug</loc>
<lastmod>$lastMod</lastmod>
</url>
~;
}
}
print $fh qq~</urlset>~;
close $fh;
$result .= 'Done. I tink';
}

if ($a eq 'countlistings'){
my $oldest = $now - 63000000; # IN THE LAST TWO YEARS
my $newest = $now - 600000; # MORE THAN A MONTH AGO

my $getListings = $SBdb->prepare("SELECT p.id FROM posts AS p WHERE NOT EXISTS (SELECT id FROM spam_reports WHERE object_type = 'listing' AND object_id = p.id) AND p.status = 'live' AND p.timestamp BETWEEN $oldest AND $newest");
$getListings->execute;
$result .= $getListings->rows . ' listings';
}

if ($a eq 'markbounced'){
my $FILE = 'AUTOMATCH.mbox';
my $count = 0;
open (my $fh, '<', "$root/$FILE") || die 'File not found!';
my @addrs;
while (<$fh>){
$_ =~ s/^.*?([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+).*?$/$1/i;
push (@addrs, $1);
}
close ($fh);
my @unique = &uniq(@addrs);
$result .= @addrs . ' addresses found, of which ' . @unique . ' unique.<br/>';

foreach my $e (@unique) {
if ($SBdb->do("UPDATE members SET badmail = badmail + 1 WHERE email LIKE '$e'") > 0){
$count++;
$result .= $e . '<br/>';
}
}
$result .= $count . ' bounced emails marked as bad.<br/>';
}

# WHMCS KEY & SECRET
# TfuCj9CduDePVyZdV5CVS15DeQjGbDDe

# mDtXGu3pnWB7XIlko0JZ8nAn8gEe7WxD


if ($a eq 'changeconvo_ids'){
my $count = 0;
my $getMessages = $SBdb->prepare("SELECT id, sender, recipient FROM messages");
my $updateConvoID = $SBdb->prepare("UPDATE messages SET convo_id = ? WHERE id = ? LIMIT 1");
$getMessages->execute;
while (my ($id, $from, $to) = $getMessages->fetchrow_array){
my $convo_id = &getConvoID($from, $to);
$updateConvoID->execute("$convo_id", "$id");
$count++;
}
$result .= $count . ' convoIDs updated!';
}


if ($a eq 'getlocation'){
my @array = &getCurrentLocation;
$result = $ip . ': ';
$result .= join(', ', @array);
}




if ($a eq 'assessrisk'){
my $count = 0;

## LISTINGS..
my $getListings = $SBdb->prepare("SELECT id FROM posts WHERE status = 'live'");
$getListings->execute;
while (my $id = $getListings->fetchrow_array){
$count += &assessRisk('listing', $id);
}
$getListings->finish;

## PROFILES..
my $getProfiles = $SBdb->prepare("SELECT id FROM members WHERE activated = 1");
$getProfiles->execute;
while (my $id = $getProfiles->fetchrow_array){
$count += &assessRisk('profile', $id);
}
$getProfiles->finish;

$result .= qq~$count objects risk-assessed.~;
}

if ($a eq 'writeactivities'){
	
### DELETE EXISTING DATA
my $delete = $SBdb->do("TRUNCATE TABLE activity");

my $addActivity = $SBdb->prepare("INSERT INTO activity (actor_id, object_type, object_id, image, text, link, location, data, timestamp) VALUES (?,?,?,?,?,?,?,?,?)");

my $count = 0;
my $getListings = $SBdb->prepare("SELECT p.id, p.lister, p.title, p.description, p.type, p.terms, p.image, p.timestamp, m.region, m.country FROM posts AS p JOIN members AS m ON m.id = p.lister WHERE p.status = 'live' ORDER BY p.timestamp ASC");
$getListings->execute;

my $addActivity = $SBdb->prepare("INSERT INTO activity (actor_id, object_type, object_id, image, text, link, location, data, timestamp) VALUES (?,?,?,?,?,?,?,?,?)");

while (my ($id, $lister, $title, $description, $type, $terms, $image, $timestamp, $region, $country) = $getListings->fetchrow_array){
$count++;
my $TYPE = $type;
if ($terms eq 'loan'){
	if ($type eq 'offer'){$TYPE = 'lend'};
	if ($type eq 'request'){$TYPE = 'borrow'};
}
my $link = qq~$baseURL/listing/?id=$id~;
$image = qq~$baseURL/listing_pics/$image\.jpg~ if $image;
$addActivity->execute("$lister", 'listing', "$id", "$image", "$title - $description", "$link", "$region, $country", "$TYPE", "$timestamp");
}
$result .= $count . ' listings copied.<br/>';
$getListings->finish;


### PROFILES

$count = 0;
my $getProfiles = $SBdb->prepare("SELECT id, first_name, last_name, region, country, image, about_me, joined FROM members WHERE activated = 1 ORDER BY joined ASC");
$getProfiles->execute;

while (my ($id, $first_name, $last_name, $region, $country, $image, $about_me, $joined) = $getProfiles->fetchrow_array){
$count++;
my $link = qq~$baseURL/profile/?id=$id~;
$image = qq~$baseURL/user_pics/$image\.jpg~ if $image;
$addActivity->execute("$id", 'profile', "$id", "$image", "<span class=\"notranslate\">$first_name $last_name</span> joined Sharebay!", "$link", "$region, $country", "", "$joined");
}
$result .= $count . ' profiles copied.<br/>';
$getProfiles->finish;


### COMPLETED TRANSACTIONS


$count = 0;
my $getTrans = $SBdb->prepare("SELECT t.id, t.listing_id, t.giver_id, t.getter_id, t.timestamp, p.title, p.image, m1.first_name, m1.last_name, m2.first_name, m2.last_name FROM transactions AS t JOIN posts AS p ON p.id = t.listing_id JOIN members AS m1 ON m1.id = t.giver_id JOIN members AS m2 ON m2.id = t.getter_id WHERE t.status = 'delivered' ORDER BY t.timestamp ASC");
$getTrans->execute;

while (my ($id, $listing_id, $giver_id, $getter_id, $timestamp, $listing_title, $listing_image, $giver_first_name, $giver_last_name, $getter_first_name, $getter_last_name) = $getTrans->fetchrow_array){
$count++;
my $link = qq~$baseURL/transactions/?id=$getter_id~;
my $text = qq~<a href="$baseURL/profile/?id=$getter_id">$getter_first_name $getter_last_name</a> confirmed delivery of <a href="$baseURL/listing/?id=$listing_id">$listing_title</a> from <a href="$baseURL/profile/?id=$giver_id">$giver_first_name $giver_last_name</a>.~;
$addActivity->execute("$getter_id", 'transaction', "$id", "$listing_image", "$text", "$link", "", "", "$timestamp");
}
$result .= $count . ' transactions copied.<br/>';
$getTrans->finish;


### REVIEWS 


$count = 0;
my $getReviews = $SBdb->prepare("SELECT r.id, r.reviewer_id, r.target_id, r.stars, r.comment, r.timestamp, m1.first_name, m1.last_name, m2.first_name, m2.last_name FROM reviews AS r JOIN members AS m1 ON m1.id = r.reviewer_id JOIN members AS m2 ON m2.id = r.target_id ORDER BY r.timestamp ASC");
$getReviews->execute;

while (my ($id, $reviewer_id, $target_id, $stars, $comment, $timestamp, $reviewer_first_name, $reviewer_last_name, $target_first_name, $target_last_name) = $getReviews->fetchrow_array){
$count++;
my $link = qq~$baseURL/review/?id=$id~;
my $text = qq~<a href="$baseURL/profile/?id=$reviewer_id">$reviewer_first_name $reviewer_last_name</a> left a <a href="$link">$stars star review</a> for <a href="$baseURL/profile/?id=$target_id">$target_first_name $target_last_name</a>.~;
if ($comment){$text .= qq~<p class="center italic">&#8220;$comment&#8221;</p>~;}
$addActivity->execute("$reviewer_id", 'review', "$id", "", "$text", "$link", "", "$stars", "$timestamp");
}
$result .= $count . ' reviews copied.<br/>';
$getReviews->finish;


### BLOG


$count = 0;
my $getStories = $SBdb->prepare("SELECT b.id, b.title, b.slug, b.image, b.summary, b.author_id, b.timestamp, m.first_name, m.last_name FROM blog AS b JOIN members AS m ON m.id = b.author_id ORDER BY b.timestamp ASC");
$getStories->execute;

while (my ($id, $title, $slug, $image, $summary, $author_id, $timestamp, $author_first_name, $author_last_name) = $getStories->fetchrow_array){
$count++;
my $link = qq~$baseURL/blog/$slug~;
my $text = qq~<a href="$baseURL/profile/?id=$author_id">$author_first_name $author_last_name</a> just published a new story <a href="$baseURL/blog/$slug">$title</a>.~;
if ($summary){$text .= qq~<p class="italic">&#8220;$summary...&#8221;</p>~;}
$addActivity->execute("$author_id", 'story', "$id", "$image", "$text", "$link", "", "", "$timestamp");
}
$result .= $count . ' blogs copied.<br/>';
$getStories->finish;


my $rows = $SBdb->do("SELECT id FROM activity");
$result .= '<br/>' . $rows . ' activities added.<br/>';

}


if ($a eq 'exportxml'){
require 'xml.pl';
$result .= &exportXML;
}

if ($a eq 'getxml'){
require 'xml.pl';
my $url = 'https://www.sharebay.org/freelist.xml';
$result .= &getXML($url);
}

if ($a eq 'validatexml'){
require 'xml.pl';
my $url = 'https://www.sharebay.org/indexfile.xml';
$result .= &validateXML($url);
}


if ($a eq 'sendemails'){
# SEND BULK EMAILS TO A GROUP SPECIFIED IN MYSQL SELECT
# NB. THESE EMAILS ARE NOT QUEUED AND WILL SEND IMMEDIATELY

# SELECT WHO TO SEND TO
my $sth = $SBdb->prepare("SELECT first_name, email FROM members WHERE id = 30 LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
my $count = 0;
while (my ($first_name, $email) = $sth->fetchrow_array){
# SET EMAIL CONTENT
my $subject = qq~Hello!~;
my $body = qq~As one of our founding supporters, I thought you should know that we have decided to close the share donation program as and from next Sunday, August 13th 2017, and adopt a patronage fundraising system instead. We feel that this approach will create a more reliable income stream to safeguard the future of our site and its ongoing development, but we will no longer be offering site shares in exchange.

Of course, your current stake in our site of <strong>RASPBERRY\%</strong> still stands and won't be affected in any way by this decision. (You can also increase it if you wish up until next Sunday)

'm happy to say that our site is slowly starting to gather momentum. We have almost 800 active accounts now and 200 listings of free items and services. As you've probably heard me say before, I expect this to grow slowly, as people build confidence in the platform and a more diverse range of goods and services becomes available. This takes time, but still inside its first month, it looks like it's already happening!

Let me once again thank you for helping make all this possible and welcome to the team!
Colin Turner, Founder~;
my $call2act = "Donate";
my $link = qq~$baseURL/donate~;
my $image = $baseURL . '/i/og-image.jpg';
# SEND EMAIL
&sendMail($email, $notify, $subject, $first_name, $body, $call2act, $link, $image, undef);
$count++;
}
$result = qq~<p class="success">$count email(s) sent.</p>~;
}else{
$result = qq~<p class="error">No records found.</p>~;
}
}


if ($a eq 'set-category'){
my $update = $SBdb->do("UPDATE posts SET category = $FORM{category} WHERE id = $FORM{id} LIMIT 1") if ($FORM{category});
$result .= '<p>Success!</p>' if $update;
my $sth = $SBdb->prepare("SELECT id, title, description, type, image FROM posts WHERE category = 0 AND status = 'live' LIMIT 1");
$sth->execute;

while(my($id, $title, $description, $type, $image)= $sth->fetchrow_array){
$title = '<span class="request">[REQUEST]</span> ' . $title if ($type eq 'request');
if ($image){
$image = 'listing_pics/' . $image . '\_t.jpg';
}else{
$image = 'listing_pics/listing_default_t.jpg';
}
$result .= qq~<div class="result">
<div class="result-image" title="Listing image" style="background-image: url('$image');"></div>~;

$result .= qq~
<div class="result-location" title="Listing location"><i class="fas fa-map-marker-alt"></i></div> 
<div class="result-info-container">
<a class="result-title" href="listing?id=$id">$title</a>
<div class="result-desc" style="height: auto !important; max-height: auto !important;">$description</div>
</div>
</div>
<form action="admin.cgi">
<input type="hidden" name="a" value="set-category"/>
<input type="hidden" name="id" value="$id"/>
<select name="category" class="forminput notranslate">~;
my $cat_select = &getCategories;
$result .= qq~$cat_select</select>
<input type="submit" class="cta-button" name="submit"/>
</form>~;
}
}

if ($a eq 'getsmallprofiles'){
	
## ENCOURAGE MEMBERS TO ADD PROFILE DETAILS

my $sth = $SBdb->prepare("SELECT id, first_name, email FROM members WHERE mailme = 1 AND activated = 1 AND badmail = 0 AND ((LENGTH(about_me) + LENGTH(tags)) < 20) AND joined < (UNIX_TIMESTAMP() - 259300)");

$sth->execute;

my $count = 0;
if ($sth->rows > 0){
my $body = qq~Hey there stranger, thank you again for joining our wonderful little sharing network. But...we don't know very much about you! :/\n\nSharebay uses information from people's profiles, searches and views to get an idea what sort of things you like and what to show you.\n\nWhy not take a couple of minutes to write a little more about yourself?\n\nYou can write a short bio, add tags, tell us what you're good at and what things interest you. The more we know about you, the more we can bring you the things you like.\n\n<a href="$baseURL/edit">Click here</a> to edit your profile:~;
my $call2act = 'Edit profile';
my $link = $baseURL . '/edit';
my $image = $baseURL . '/i/stranger.png';
while (my ($id, $first_name, $email) =  $sth->fetchrow_array){
$count++;
my $subject = qq~$first_name, we'd love to know more about you~;
# &sendMail($email, $notify, $subject, undef, $body, $call2act, $link, $image, undef);
}
}
$sth->finish;
$result .= $count . ' emails sent.';
}




if ($a eq 'get_blocked'){
$result = &getBlockedIds(56956);
}

if ($a eq 'getwants'){
my $thisID = $FORM{id} || $myID;
my $string = &getWants($thisID);
$result = $string;
}

if ($a eq 'gethaves'){
my $thisID = $FORM{id} || $myID;
my $string = &getHaves($thisID);
$result = $string;
}

if ($a eq 'remove_images'){
{
my $dir = "$siteroot/user_pics";
my @images = glob "$dir/*.*";
my $count = 0;
foreach my $image_ref (@images){
$image_ref =~ s/^.*(\\|\/)(.*)\.jpg$/$2/;
$image_ref =~ s/^(.*)_t$/$1/;
unless (my $sth = $SBdb->do("SELECT id FROM members WHERE image = '$image_ref'") > 0 || $image_ref eq 'q'){
# $count++ if unlink "$dir/$image_ref\.jpg";
# $count++ if unlink "$dir/$image_ref\_t.jpg";
$count++;
}
}
$result .= "$count unreferenced files found";
}
}



if ($a eq 'create-PUG-user'){
my $name = 'GABRIELA';
my $email = 'gabrielafandino@hotmail.com';

my $PUGdb = DBI->connect('DBI:mysql:rtxmedia_PUG:host=localhost','rtxmedia_PUG','p0o9i8u7y6t5') or die "Database error!\n\n";
my @chars = ('a'..'z',0..9);
my $password = join '', (map {$chars [rand@chars]} @chars)[0..7];
use Digest::MD5 qw(md5_hex);
my $PW_hash = md5_hex($email . $password);
my $sth = $PUGdb->do("INSERT INTO users (name, email, password) VALUES ('$name', '$email', '$PW_hash')");
$result = qq~<p class="success">New user created for:<br/>Username: $name<br/>Email: $email<br/>Password: $password</p>~;

}

if ($a eq 'testurlparam'){
	if ($ENV{REQUEST_URI} =~ m/\?search/){
		$result = 'Search...';
	}else{
		$result = 'No search...';
	}
}

if ($a eq 'testregex'){
my $string = 'Dwayne "The Rock" Johnson';
$result .= $string . '<br/>';
# $string =~ s/"/\\"/g;
$result .= $string . '<br/>';
my $hash = {name => $string};
use JSON::PP;
$result .= encode_json($hash) . '<br/>';
}


if ($a eq 'copy_to_dev'){
use File::Copy::Recursive qw(rcopy);

# COPY SITE TO DEV FOLDER
my $source_dir = "/home/sharebay/public_html";
my $dest_dir = "/home/sharebay/sharebay-dev.org";
my @exclude = ("config.pl");

opendir(DIR, $source_dir) or die "Cannot open directory: $!";
my $count = 0;
while (my $file = readdir(DIR)) {
next if ($file eq "." or $file eq "..");
next if (grep {$_ eq $file} @exclude);
my $source_file = "$source_dir/$file";
my $dest_file = "$dest_dir/$file";
rcopy($source_file, $dest_file) or die "Copy failed: $!";
$count++;
}
closedir(DIR);
$result .= qq~<p class="success">$count files and folders copied to dev space.</p>~;
}


if ($a eq 'push_to_production'){
use File::Copy::Recursive qw(rcopy);
my $errors = 0;

# FIRST SAVE CURRENT FILES TO _OLD
my $source_dir = "/home/sharebay/public_html";
my $dest_dir = "/home/sharebay/sharebay_old";
my @exclude = ("config.pl", 'user_pics', 'listing_pics');

opendir(DIR, $source_dir) or die "Cannot open directory: $!";
my $count = 0;
while (my $file = readdir(DIR)) {
next if ($file eq "." or $file eq "..");
next if (grep {$_ eq $file} @exclude);

my $source_file = "$source_dir/$file";
my $dest_file = "$dest_dir/$file";
if (rcopy($source_file, $dest_file)){
$count++;
}else{
$errors++;
}
}
closedir(DIR);
$result .= qq~<p class="success">$count files and folders saved to $dest_dir</p>~;

# COPY DEV FILES TO PRODUCTION IF COPY SUCCESSFUL
if ($errors eq 0){
my $source_dir = "/home/sharebay/sharebay-dev.org";
my $dest_dir = "/home/sharebay/public_html";
my @exclude = ("config.pl", 'user_pics', 'listing_pics');

opendir(DIR, $source_dir) or die "Cannot open directory: $!";
my $count = 0;
while (my $file = readdir(DIR)) {
next if ($file eq "." or $file eq "..");
next if (grep {$_ eq $file} @exclude);

my $source_file = "$source_dir/$file";
my $dest_file = "$dest_dir/$file";
rcopy($source_file, $dest_file) or die "Copy failed: $!";
$count++;
}
closedir(DIR);
$result .= qq~<p class="success">$count files and folders pushed to production site.</p>~;
}else{
$result .= qq~<p class="error">There was an issue with creating the backup. Push aborted.</p>~;
}
}


if ($a eq 'rollback_files'){
use File::Copy::Recursive qw(rcopy);

# COPY LAST VERSION FILES FROM BACKUP
my $source_dir = "/home/sharebay/sharebay_old";
my $dest_dir = "/home/sharebay/public_html";
my @exclude = ("config.pl", 'user_pics', 'listing_pics');

opendir(DIR, $source_dir) or die "Cannot open directory: $!";
my $count = 0;
while (my $file = readdir(DIR)) {
next if ($file eq "." or $file eq "..");
next if (grep {$_ eq $file} @exclude);
my $source_file = "$source_dir/$file";
my $dest_file = "$dest_dir/$file";
rcopy($source_file, $dest_file) or die "Copy failed: $!";
$count++;
}
closedir(DIR);
$result .= qq~<p class="success">$count files and folders restored from previous version.</p>~;
}



if ($a eq 'testsend'){
## CONNECT TO EMAIL DATABASE
my $EMdb = DBI->connect("DBI:mysql:database=sbmail_emails;host=localhost;mysql_local_infile=1", 'sbmail_mailer', '}+{_P0o9i8',{RaiseError => 1, PrintError => 1});
my $EM_enc = $SBdb->do("SET NAMES 'utf8mb4'");
my $addEmail = $EMdb->prepare("INSERT INTO email_queue (account, to_email, bcc, subject, html, text) VALUES(?,?,?,?,?,?)");
$addEmail->execute('notify', 'colinrturner@gmail.com', '', 'Well how do ye do', 'Young Will E. MC Bride', 'Textually speaking');
$addEmail->finish;
$EMdb->disconnect;
$result .= 'Scent. I stink.';
}


if ($a eq 'test'){
use Cwd 'abs_path';
$result .= abs_path();
}

# SINGLE TEST EMAIL
if ($a eq 'testemail'){
my $to = '30';
my $from = $notify;
my $name = undef;
my $subject = 'Test ID email';
my $body = 'Hello, he said testily.';
my $call2act = "Do something";
my $link = 'http://dosomething.com';
my $image = undef;

# SEND EMAIL
&sendMail($to, $from, $subject, $name, $body, $call2act, $link, $defaultImage, undef);

$result .= qq~<p class="success">&apos;$subject&apos; email sent.</p>~;
}


if ($a eq 'messageall'){
my $adminID = 30;
# my $alert = 'Two Important Updates to Sharebay';
my $message = qq~Howdy, I'm Colin one of the admins of Sharebay. I'm just reaching to see what you think of the new site? Would welcome any thoughts / input on it. Cheers, Colin (PS. the full details of changes are in here: https://www.sharebay.org/blog/whats-new-in-sharebay-v3)~;

my $count = 0;
my $getall = $SBdb->prepare("SELECT id FROM members WHERE activated = 1 AND allow_contact = 1 AND id != $adminID");
$getall->execute;
while (my $id = $getall->fetchrow_array){
# &sendMessage($adminID, $id, $alert, 'alert');
&sendMessage($adminID, $id, $message, 'message');
$count++;
}
$getall->finish;
$result = qq~<p class="success">$count messages sent.</p>~;
}


if ($a eq 'resetgotit'){
my $sth = $SBdb->do("UPDATE members SET gotit = 0");
$result = qq~<p class="success">$sth records updated.</p>~;
}

if ($a eq 'resetallbounces'){
my $sth = $SBdb->do("UPDATE members SET badmail = 0 WHERE badmail > 0");
$result = qq~<p class="success">$sth records updated.</p>~;
}

if ($a eq 'mostpopularlistings'){
my $sth = $SBdb->prepare("SELECT id, title, image, rank FROM posts WHERE image != '' AND status = 'live' ORDER BY rank DESC");
$sth->execute;
if ($sth->rows > 0){
my $found = $sth->rows;
$result .= qq~<p>$found records found.</p>~;
while (my ($id, $title, $image, $rank) = $sth->fetchrow_array){
$result .= qq~<p>$title ($rank)<a href="$baseURL/listing?a=showlisting&id=$id" target="_blank"><img src="$baseURL/listing_pics/$image\.jpg"/></a></p>~;
}
}else{
$result .= qq~<p class="error">Nothing found.</p>~;
}
}


if ($a eq 'mosttransactedlistings'){
my $sth = $SBdb->prepare("SELECT listing_id, COUNT(*) as count FROM transactions WHERE status = 'delivered' GROUP BY listing_id ORDER BY count DESC LIMIT 100");
my $getListing = $SBdb->prepare("SELECT title, image, rank FROM posts WHERE status = 'live' AND image != '' AND id = ? LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
while (my ($listing_id, $count) = $sth->fetchrow_array){
$getListing->execute("$listing_id");
if ($getListing->rows > 0){
my ($title, $image, $rank) = $getListing->fetchrow_array;
$result .= qq~<a href="$baseURL/listing?a=showlisting&id=$listing_id" target="_blank"><h2>$title</h2><p>(Transactions: $count; rank: $rank)<br/><img src="$baseURL/listing_pics/$image\.jpg" style="width:100%;height:auto;"/></a></p>~;
}
}
$getListing->finish;
}else{
$result .= qq~<p class="error">Nothing found.</p>~;
}
}

if ($a eq 'test-stuff'){
	
my ($cat, $trans) = &getCategory(15);
$result .= qq~<p class="success">$cat, $trans</p>~;
}

if ($a eq 'mostgivingmember'){
my $sth = $SBdb->prepare("SELECT listing_id, COUNT(*) as count FROM transactions WHERE status = 'delivered' GROUP BY listing_id ORDER BY count DESC LIMIT 100");
my $getListing = $SBdb->prepare("SELECT title, image, rank FROM posts WHERE status = 'live' AND image != '' AND id = ? LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
while (my ($listing_id, $count) = $sth->fetchrow_array){
$getListing->execute("$listing_id");
if ($getListing->rows > 0){
my ($title, $image, $rank) = $getListing->fetchrow_array;
$result .= qq~<a href="$baseURL/listing?a=showlisting&id=$listing_id" target="_blank"><h2>$title</h2><p>(Transactions: $count; rank: $rank)<br/><img src="$baseURL/listing_pics/$image\.jpg" style="width:100%;height:auto;"/></a></p>~;
}
}
$getListing->finish;
}else{
$result .= qq~<p class="error">Nothing found.</p>~;
}
}



if ($a eq 'bestlistingmatches'){
my $grabtags = $SBdb->prepare("SELECT tags FROM members WHERE id = '$myID'");
$grabtags->execute;
my $tags = $grabtags->fetchrow_array;

my $sth = $SBdb->prepare("SELECT id, title, image, rank, MATCH (title, description, tags) AGAINST ('$tags') AS rank FROM posts WHERE image != '' AND status = 'live' AND MATCH (title, description, tags) AGAINST ('$tags') ORDER BY rank DESC");
$sth->execute;
if ($sth->rows > 0){
my $noResults = $sth->rows;
$result .= qq~<p class="success">$noResults records found for $tags.</p>~;
while (my ($id, $title, $image, $rank, $rank) = $sth->fetchrow_array){
$result .= qq~<p>$title (Rank: $rank; rank: $rank)<a href="$baseURL/listing?a=showlisting&id=$id" target="_blank"><img src="$baseURL/listing_pics/$image\.jpg" style="width:100%;height:auto;"/></a></p>~;
}
}
else{
$result .= qq~<p class="error">Nothing found.</p>~;
}
}


if ($a eq 'bestpeoplematches'){
my $grabtags = $SBdb->prepare("SELECT tags FROM members WHERE id = '$myID'");
$grabtags->execute;
my $tags = $grabtags->fetchrow_array;

my $sth = $SBdb->prepare("SELECT id, first_name, last_name, about_me, tags, image, rank, (MATCH (about_me, tags) AGAINST ('$tags')) AS rank FROM members WHERE activated = 1 AND id != $myID AND MATCH (about_me, tags) AGAINST ('$tags') ORDER BY rank DESC");
$sth->execute;
if ($sth->rows > 0){
my $noResults = $sth->rows;
$result .= qq~<p class="success">$noResults records found for $tags.</p>~;
while (my ($id, $first_name, $last_name, $about_me, $tags, $image, $rank, $rank) = $sth->fetchrow_array){
$result .= qq~<p><a href="$baseURL/profile?id=$id" target="_blank"><img src="$baseURL/user_pics/$image\.jpg"/></a>$first_name $last_name (Rank: $rank; rank: $rank) $about_me tagS: $tags</p>~;
}
}else{
$result .= qq~<p class="error">Nothing found.</p>~;
}
}

if ($a eq 'fixsessionfiles'){
	### CHANGE COMMAS TO PIPES
my $count = 0;
my $sessionDir = '/home/sharebay/_private/sessions';

opendir(DIR,$sessionDir) || die "Can't open $sessionDir: $!";
my @sessions = readdir(DIR);
close(DIR);
foreach my $session(@sessions){
open (my $FH, '<', "$sessionDir/$session") || die "Can't open $sessionDir/$session: $!";
my $FILE = <$FH>;
close $FH;
if ($FILE =~ m/,/){
$FILE =~ s/,/|/g;
open (my $NEW, '>', "$sessionDir/$session") || die "Can't open $sessionDir/$session: $!";
print $NEW $FILE;
close $NEW;
$count++;
}
}
$result .= qq~<p class="success">$count session files found.</p>~;
}



if ($a eq 'getgravatar'){
if ($FORM{id}){
my $sth = $SBdb->prepare("SELECT email FROM members WHERE id = $FORM{id} LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
my $email = $sth->fetchrow_array;
&getGravatar($FORM{id}, $email);
$result = qq~<p class="success">Gravatars saved.</p>~;
}else{
$result = qq~<p class="error">No member found!</p>~;
}
}else{
$result = qq~<p class="error">No id!</p>~;
}
}

if ($a eq 'moveimages'){
my $sth = $SBdb->prepare("SELECT id FROM posts");
$sth->execute;
my $count = 0;
while (my $id = $sth->fetchrow_array){
if (-e "$siteroot/listing_pics/$id\.jpg"){
my $name = $id . '_' . $now;
rename $siteroot . '/listing_pics/' . $id . '.jpg', $siteroot . '/listing_pics/' . $name . '.jpg';
rename $siteroot . '/listing_pics/' . $id . '_t.jpg', $siteroot . '/listing_pics/' . $name . '_t.jpg';
my $update = $SBdb->do("UPDATE posts SET image = '$name' WHERE id = '$id'");
$count++;
}
}
$result = qq~<p class="success">$count images renamed and updated.</p>~;
}


if ($a eq 'getimage'){
my $id = $FORM{id};
my $sth = $SBdb->prepare("SELECT email, image FROM members WHERE id = '$id' LIMIT 1");
$sth->execute;
my ($email, $imageRef) = $sth->fetchrow_array;
my $confirm;
if (!-e "$siteroot/user_pics/$imageRef\.jpg" || !-e "$siteroot/user_pics/$imageRef\_t.jpg"){
$confirm = &getGravatar($id, $email);
if ($confirm eq 1){
$result = qq~<p class="success">New <a href="$baseURL/profile?id=$id">images created.</a></p>~;
}else{
$result = qq~Error getting Gravatar!~;
}
}else{
$result = qq~File exists!<br/><img src="$baseURL/user_pics/$imageRef\.jpg"/><br/><img src="$baseURL/user_pics/$imageRef\_t.jpg"/>~;
}
}

if ($a eq 'getemails'){
my $sth = $SBdb->prepare("SELECT email FROM members WHERE country_iso = '$FORM{iso}'");
$sth->execute;
while (my $email = $sth->fetchrow_array){
$result .= $email . '; ';
}
}

if ($a eq 'getlatlong'){
	my $ip = $ENV{REMOTE_ADDR};
	my ($lat, $lon, $city, $region, $country, $country_iso) = &getIPLocation($ip);
	$result .= "$lat, $lon, $city, $region, $country, $country_iso";
}

if ($a eq 'checkmodule'){
my $mod_exists = eval
{
require Archive::Zip;
1;
};

if($mod_exists){
$result .= 'Yup. Module loaded.';
}else{
$result .= 'Nope. Module not loaded.';
}
}


if ($a eq 'mailoldusers'){
my $sth = $SBdb->prepare("SELECT email FROM old_users");
$sth->execute;
while (my $email = $sth->fetchrow_array){
$result .= $email . '; ';
}
}

if ($a eq 'testdistance'){
my $user1 = $FORM{user1};
my $user2 = $FORM{user2};

my $sth = $SBdb->prepare("SELECT lat, lon FROM members WHERE id = $user1");
$sth->execute;
my ($lat1, $lon1) = $sth->fetchrow_array;
$sth->finish;

my $sth2 = $SBdb->prepare("SELECT lat, lon FROM members WHERE id = $user2");
$sth2->execute;
my ($lat2, $lon2) = $sth2->fetchrow_array;
$sth2->finish;

$result = &getDistance($lat1, $lon1, $lat2, $lon2);
}

# PROCESS RESULT AND RETURN PAGE
if (!$result){
$result = qq~<p class="error">No operation selected!</p>~;
}
my $title = 'Site Admin';
my $headerInject; # ADD ANY HEADER SCRIPTS HERE

&header($title, undef, undef, $headerInject, 'page');

print qq~$result~;

&footer;

}else{
# ACCESS DENIED
&errorCatcher("Sorry, you don't have permission to view this page.");
}


$SBdb -> disconnect;
# Exeunt
