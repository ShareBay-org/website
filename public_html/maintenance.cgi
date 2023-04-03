#!/usr/bin/perlml
# use cPanelUserConfig;

# THIS SCRIPT IS REGULAR MAINTENANCE TASKS
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );
my $active = 1; # 0 to disable
my $output = 1; # FOR TESTING
require '/home/sharebay/public_html/common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

if ($maintenance){$active = 0}; # DISABLE IN MAINTENANCE MODE

print qq~Content-type: text/plain; charset=utf-8\n\n~ if $output;
my $count = 0;

if ($active){
$maintenance = 1; # SET MAINTENANCE MODE
&spamCop;
&removeNonConfirmed;
# &createSnapshot;
# &setRanking;
# &removeUnusedImages;
# &setMemberScores;
&createSiteMap;
&exportFreelist;
$SBdb->disconnect;
$maintenance = 0; # RELEASE MAINTENANCE MODE
}




sub exportFreelist{
my $app_id = 'sharebay.org';
my $appName = 'Sharebay';
my $appDesc = 'The Sharing Network';
my $date = &getW3CDate($now);

use XML::Writer;
my $x = XML::Writer->new(OUTPUT => 'self', DATA_MODE => 1, DATA_INDENT => 2, );
$x->xmlDecl('UTF-8', standalone => 'yes');
$x->pi('xml-stylesheet', 'href="' . $baseURL . '/XML-styles.xsl" type="text/xsl"');
$x->comment("These are the latest free offer listings from Sharebay.org which you are free to use as you wish providing that you a) Include backlinks to the originating site, and b) Do not use the data in any way other than to display free listing information. Use of this file signifies your acceptance of these terms.");
$x->startTag('freelist');
$x->startTag('header');
$x->startTag('appID'); $x->characters($app_id); $x->endTag();
$x->startTag('appName'); $x->characters($appName); $x->endTag();
$x->startTag('appDesc'); $x->characters($appDesc); $x->endTag();
$x->startTag('date'); $x->characters($date); $x->endTag();
$x->endTag();
$x->startTag('list');

my $getListings = $SBdb->prepare("SELECT p.id, p.title, p.description, p.quantity, p.physical, p.category, p.terms, p.image, p.tags, p.lat, p.lon, p.timestamp, c.category, c.transactable, m.city, m.region, m.country, m.country_iso, m.language FROM posts AS p JOIN categories AS c ON c.id = p.category JOIN members AS m ON m.id = p.lister WHERE p.type = 'offer' AND p.status = 'live' ORDER by p.id DESC");
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

use IO::Compress::Gzip qw(gzip $GzipError);
my $input = "$siteroot/freelist.xml";
my $output = "$siteroot/freelist.xml.gz";
gzip $input => $output;
}
 
 
sub createSnapshot{
my $lastDay = $now - 86400;
my $insert = $SBdb->prepare("INSERT INTO snapshot (timestamp, total_members, new_members, active_members, total_listings, new_listings, total_views, listing_views, profile_views, likes, comments, transactions, completed_transactions, reviews, conversations) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)");

my $total_members = int($SBdb->do("SELECT id FROM members WHERE activated = 1")) || 0;
my $new_members = int($SBdb->do("SELECT id FROM members WHERE activated = 1 AND joined > $lastDay")) || 0;
my $active_members = int($SBdb->do("SELECT id FROM members WHERE activated = 1 AND last_active > $lastDay")) || 0;
my $total_listings = int($SBdb->do("SELECT id FROM posts WHERE status = 'live'")) || 0;
my $new_listings = int($SBdb->do("SELECT id FROM posts WHERE status = 'live' AND timestamp > $lastDay")) || 0;
my $total_views = int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND timestamp > $lastDay")) || 0;
my $listing_views = int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND object_type = 'listing' AND actor_id REGEXP '^[0-9]+\$' AND timestamp > $lastDay")) || 0;
my $profile_views = int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND object_type = 'profile' AND actor_id REGEXP '^[0-9]+\$' AND timestamp > $lastDay")) || 0;
my $likes = int($SBdb->do("SELECT id FROM interactions WHERE action = 'like' AND timestamp > $lastDay")) || 0;
my $comments = int($SBdb->do("SELECT id FROM interactions WHERE action = 'comment' AND timestamp > $lastDay")) || 0;
my $transactions = int($SBdb->do("SELECT id FROM transactions WHERE timestamp > $lastDay")) || 0;
my $completed_transactions = int($SBdb->do("SELECT id FROM transactions WHERE status = 'delivered' AND timestamp > $lastDay")) || 0;
my $reviews = int($SBdb->do("SELECT id FROM reviews WHERE timestamp > $lastDay")) || 0;
my $conversations = int($SBdb->do("SELECT id FROM messages WHERE type = 'message' AND timestamp > $lastDay GROUP BY convo_id")) || 0;

$insert->execute($now, $total_members, $new_members, $active_members, $total_listings, $new_listings, $total_views, $listing_views, $profile_views, $likes, $comments, $transactions, $completed_transactions, $reviews, $conversations);
}



sub setRanking{
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
}



sub removeNonConfirmed{
## REMOVE OLD UNCONFIRMED REGISTRATIONS
my $grace_period = 30 * 24 * 60 * 60; # 30 DAYS
my $expired = $now - $grace_period;
my $sth = $SBdb->prepare("DELETE FROM members WHERE activated = 0 AND joined < $expired");
$sth->execute;
$sth->finish;
}


sub spamCop{
my $maxReports = 3;
# DELETE SPAM LISTINGS
my $getListings = $SBdb->prepare("SELECT object_id, COUNT(*) FROM spam_reports WHERE object_type = 'listing' AND action_taken = 0 GROUP BY object_id HAVING COUNT(*) >= $maxReports");
$getListings->execute;
while (my ($object_id, undef) = $getListings->fetchrow_array){
my $makeSpam = $SBdb->do("UPDATE posts SET status = 'spam' WHERE status != 'complete' AND id = $object_id LIMIT 1");
my $cancelTrans = $SBdb->do("UPDATE transactions SET status = 'admin-cancelled' WHERE status != 'delivered' AND listing_id = $object_id");
my $markAction = $SBdb->do("UPDATE spam_reports SET action_taken = 1 WHERE object_type = 'listing' AND object_id = $object_id");
}
$getListings->finish;
# DELETE SPAM PROFILES
my $getProfiles = $SBdb->prepare("SELECT object_id, COUNT(*) FROM spam_reports WHERE object_type = 'profile' AND action_taken = 0 GROUP BY object_id HAVING COUNT(*) >= $maxReports");
$getProfiles->execute;
while (my ($object_id, undef) = $getProfiles->fetchrow_array){
my $makeSpam = $SBdb->do("UPDATE members SET activated = -1 WHERE id = $object_id LIMIT 1");
my $spamListings = $SBdb->do("UPDATE posts SET status = 'spam' WHERE status != 'complete' AND lister = $object_id");
my $cancelTrans = $SBdb->do("UPDATE transactions SET status = 'admin-cancelled' WHERE status != 'delivered' AND (giver_id = $object_id OR getter_id = $object_id)");
my $markAction = $SBdb->do("UPDATE spam_reports SET action_taken = 1 WHERE object_type = 'profile' AND object_id = $object_id");
}
$getProfiles->finish;
}


sub removeUnusedImages{

{ ### DELETE UNREFERENCED PROFILE PICS
my $dir = "$siteroot/user_pics";
my @images = glob "$dir/*.*";
my $count = 0;
foreach my $image_ref (@images){
$image_ref =~ s/^.*(\\|\/)(.*)\.jpg$/$2/;
$image_ref =~ s/^(.*)_t$/$1/;
unless (my $sth = $SBdb->do("SELECT id FROM members WHERE image = '$image_ref'") > 0 || $image_ref eq 'q'){
$count++ if unlink "$dir/$image_ref\.jpg";
$count++ if unlink "$dir/$image_ref\_t.jpg";
}
}
print qq~$count unreferenced profile pics deleted.\n~ if $output;
}

{ ### DELETE UNREFERENCED LISTING PICS
my $dir = "$siteroot/listing_pics";
my @images = glob "$dir/*.*";
my $count = 0;
foreach my $image_ref (@images){
$image_ref =~ s/^.*(\\|\/)(.*)\.jpg$/$2/;
$image_ref =~ s/^(.*)_t$/$1/;
unless (my $sth = $SBdb->do("SELECT id FROM posts WHERE image = '$image_ref'") > 0 || $image_ref eq 'q'){
$count++ if unlink "$dir/$image_ref\.jpg";
$count++ if unlink "$dir/$image_ref\_t.jpg";
}
}
print qq~$count unreferenced listing pics deleted.\n~ if $output;
}
}


sub setMemberScores{
	##SET SCORES AND STRIPES
	
	my $stripe_1 = 1;
	my $stripe_2 = 4;
	my $stripe_3 = 12;	
	my $transactionValue = 4;
	
	my $getMembers = $SBdb->prepare("SELECT id FROM members WHERE activated = 1");
	$getMembers->execute;
	while (my $id = $getMembers->fetchrow_array){
		my $count = 0;
		my $getListings = $SBdb->do("SELECT * FROM posts WHERE lister = $id AND type = 'offer'");
		if ($getListings > 0){$count += $getListings;}
		if ($count > 3){$count = 3;}
		my $getCompleteOffers = $SBdb->do("SELECT * FROM transactions WHERE giver_id = '$id' AND status = 'delivered' GROUP BY getter_id");
		if ($getCompleteOffers > 0){$count += ($getCompleteOffers * $transactionValue);}
		
		if ($count > 0){
			# GIFTED TOTAL
			my $gifted = int($SBdb->do("SELECT id FROM transactions WHERE giver_id = '$id' AND status = 'delivered'"));
			
			# CALC BADGE LEVEL
			my $badge_level = 0;
			if ($count > 0 && $count < $stripe_2){$badge_level = 1}
			elsif ($count >= $stripe_2 && $count < $stripe_3){$badge_level = 2}
			elsif ($count >= $stripe_3){$badge_level = 3};
			
			# GET STAR RATING
			my $sth = $SBdb->prepare("SELECT stars FROM reviews WHERE target_id = '$id'");
			$sth->execute;		
			my $total = 0;
			my $rating = 0;
			my $no_reviews = $sth->rows;
			while (my $star = $sth->fetchrow_array){$total += $star;}
			$sth->finish;
			$rating = $total / $no_reviews if $no_reviews > 0;
			if ($rating > int($rating)){$rating = (int($rating) + 0.5)};
			
			# UPDATE MEMBER
			my $update = $SBdb->do("UPDATE members SET gifted = $gifted, trust_score = $count, badge_level = $badge_level, star_rating = $rating WHERE id = '$id'");
		}
		
	}
	$getMembers->finish;
	
	## SET MAX VALUES FOR TRUST, OFFERS, GAVE & GOT
	
	my $getMaxScore = $SBdb->prepare("SELECT MAX(trust_score) AS maximum FROM members WHERE trust_score > 0");
	$getMaxScore->execute;
	my $trust_max = $getMaxScore->fetchrow_array;
	$getMaxScore->finish;
	
	my $getOffersMax = $SBdb->prepare("SELECT COUNT(lister) c from posts WHERE type = 'offer' AND status = 'live' GROUP BY lister ORDER BY c DESC LIMIT 1");
	$getOffersMax->execute;
	my $offers_max = $getOffersMax->fetchrow_array;
	$getOffersMax->finish;	
	
	my $getGaveMax = $SBdb->prepare("SELECT COUNT(giver_id) c from transactions WHERE status = 'delivered' GROUP BY giver_id ORDER BY c DESC LIMIT 1");
	$getGaveMax->execute;
	my $gave_max = $getGaveMax->fetchrow_array;
	$getGaveMax->finish;	
	
	my $getGotMax = $SBdb->prepare("SELECT COUNT(getter_id) c from transactions WHERE status = 'delivered' GROUP BY getter_id ORDER BY c DESC LIMIT 1");
	$getGotMax->execute;
	my $got_max = $getGotMax->fetchrow_array;
	$getGotMax->finish;		
	
	my $updateAverages = $SBdb->do("UPDATE site_averages SET stripe_1 = $stripe_1, stripe_2 = $stripe_2, stripe_3 = $stripe_3, offers_max = $offers_max, gave_max = $gave_max, got_max = $got_max, trust_max = $trust_max WHERE id = 1");
	
}



sub createSiteMap{
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
print $fh qq~<url>
<loc>$baseURL/page?id=mission-statement</loc>
<lastmod>2023-01-25</lastmod>
</url>
<url>
<loc>$baseURL/page?id=terms-of-service</loc>
<lastmod>2022-12-16</lastmod>
</url>
<url>
<loc>$baseURL/page?id=privacy-policy</loc>
<lastmod>2022-12-16</lastmod>
</url>
~;
print $fh qq~</urlset>~;
close $fh;	
}

print qq~Done.~ if $output;

# Exeunt
