#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR VIEWING AND WRITING TRANSACTION REVIEWS

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );

require 'common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

# ;

if (!$a || $a eq 'read'){&showReviews;}
elsif ($a eq 'write'){&writeReview;}
elsif ($a eq 'myreviews'){&myReviews;}
elsif ($a eq 'showreview'){&showReview;}


sub showReview{
my $review_id = $FORM{id};
my $title = 'Member review';
my $desc;

my $sth = $SBdb->prepare("SELECT r.id, r.reviewer_id, r.target_id, r.trans_id, r.stars, r.comment, r.timestamp, t.listing_id, p.title, p.description FROM reviews AS r LEFT JOIN transactions AS t ON t.id = r.trans_id LEFT JOIN posts AS p ON p.id = t.listing_id WHERE r.id = '$review_id' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
	
my ($id, $reviewer_id, $target_id, $trans_id, $star_rating, $comment, $timestamp, $listing_id, $listing_title, $listing_desc) = $sth->fetchrow_array;
my $stars = &renderStars($star_rating);
my $reviewer_name = &getFullName($reviewer_id);
my $target_name = &getFullName($target_id);
$title = qq~$star_rating star review for $target_name~;
$desc =  qq~$reviewer_name left a $star_rating star review for $target_name~;
my $when = getWhen($timestamp);
$listing_title = &descTitle($listing_title, $listing_desc);
$listing_title = 'DELETED LISTING' if !$listing_title;

&header($title, $desc, undef, undef, 'page');
print qq~<h2>$title</h2>~;

print qq~<div class="review-box clearfix">
$stars<span class="smaller right grey">For: <a href="listing?id=$listing_id">$listing_title</a><br/>$when</span>~;
if ($comment){print qq~<p><span class="bigger">&#8220;</span>$comment<span class="bigger">&#8221;</span></p>~;}
print qq~<div class="right clear">~;
&getUserCard($reviewer_id);
print qq~</div></div>~;

my $link = qq~$baseURL/review?id=$review_id~;
&showSocial('review', $review_id, $link);


}else{
	# NOTHING FOUND

&header($title, $desc, undef, undef, 'page');
print qq~<p class="error">Nothing found! This review has been removed or you may have typed the wrong URL.</p>~;
}


$sth->finish;
&footer;
}


sub showReviews{
my $resultsPP = 50;
my $user_id = $FORM{id};
my ($user_first_name, $user_last_name) = &getNames($user_id);
my $title = $user_first_name . ' ' . $user_last_name . "'s Sharebay Reviews";
my $desc = 'Read what people are saying about ' . $user_first_name . ' on Sharebay';
my $getStars = $SBdb->prepare("SELECT stars FROM reviews WHERE target_id = '$user_id'");
$getStars->execute;
my $totalStars = 0;
my $starRating = 0;
my $num_results = 0;
while (my $stars = $getStars->fetchrow_array){
$num_results++;
$totalStars += $stars;
}
$getStars->finish;
if ($num_results < 1){
$num_results = 0;
$starRating = 0;
}else{
$starRating = int(($totalStars / $num_results) + .5);
}


my $query = qq~SELECT r.id, r.reviewer_id, r.trans_id, r.stars, r.comment, r.timestamp, t.listing_id, p.title, p.description FROM reviews AS r LEFT JOIN transactions AS t ON t.id = r.trans_id LEFT JOIN posts AS p ON p.id = t.listing_id WHERE r.target_id = '$user_id' ORDER BY r.timestamp DESC~;
my $num_results = $SBdb->do($query);
if ($num_results < 1){$num_results = 0;}
my $start = $FORM{start} || 0;
$query .= qq~ LIMIT $resultsPP OFFSET $start~;
my $prevURL = qq~reviews?id=$user_id&start=~ . ($start - $resultsPP);
my $nextURL = qq~reviews?id=$user_id&start=~ . ($start + $resultsPP);
my $heading;

if ($num_results > 0){
	my $resultsTo;
	if (($start + $resultsPP) > $num_results){$resultsTo = $num_results}else{$resultsTo = $start + $resultsPP};
	$heading = qq~Showing ~ . ($start + 1) . qq~ to ~ . $resultsTo . qq~ of $num_results reviews~;
}else{
$heading = qq~No reviews found~;
}
if ($user_id){
	$heading .= qq~ for $user_first_name $user_last_name~;
}

my ($transactions, $reviews, $pending);
if ($LOGGED_IN){
$transactions = $SBdb->do("SELECT id FROM transactions WHERE (giver_id = '$myID' OR getter_id = '$myID') AND status = 'delivered'");
$reviews = $SBdb->do("SELECT id FROM reviews WHERE reviewer_id = '$myID'");
$pending = $transactions - $reviews;
}

my $overall_rating = &showStars($user_id);

my $sth = $SBdb->prepare($query);
$sth->execute;
&header($title, $desc, undef, undef, 'page');
print qq~<h2>$title</h2>
<p>$overall_rating</p>
<p>$heading</p>~;

if ($LOGGED_IN){
if ($pending > 0){
print qq~<p class="helper">You have <a href="$baseURL/reviews?a=myreviews">$pending transactions to review</a>.</p>~;
}
}
	
while (my ($id, $reviewer_id, $trans_id, $star_rating, $comment, $timestamp, $listing_id, $listing_title, $listing_desc) = $sth->fetchrow_array){
my $stars = &renderStars($star_rating);
my $reviewee_name = &getFullName($user_id);
my $when = getWhen($timestamp);
$listing_title = &descTitle($listing_title, $listing_desc);
$listing_title = 'DELETED LISTING' if !$listing_title;


print qq~<div class="review-box clearfix">
$stars<span class="smaller right grey">For: <a href="listing?a=showlisting&id=$listing_id">$listing_title</a><br/>$when</span>~;
if ($comment){print qq~<p><span class="bigger">&#8220;</span>$comment<span class="bigger">&#8221;</span></p>~;}
print qq~<div class="right clear">~;
&getUserCard($reviewer_id);
print qq~</div></div>~;
}

if ($num_results > $resultsPP){
print qq~
<p class="center clear top20">
<a class="nav-button~; if ($start <= 0){print qq~ disabled~;} print qq~" href="$prevURL" title="Previous page"><i class="fas fa-chevron-circle-left fa-3x"></i></a>&nbsp;&nbsp;
<a class="nav-button~; if (($start + $resultsPP) >= $num_results){print qq~ disabled~;} print qq~" href="$nextURL" title="Next page"><i class="fas fa-chevron-circle-right fa-3x"></i></a>
</p>~;
}
$sth->finish;
&footer;
}


sub writeReview{
&bounceNonLoggedIn('Please log in to leave a review!');
my $trans_id = $FORM{trans_id};
my $getData = $SBdb->prepare("SELECT t.giver_id, t.getter_id, t.listing_id, t.timestamp, p.title, p.description FROM transactions AS t LEFT JOIN posts AS p ON p.id = t.listing_id WHERE t.id = $trans_id AND (t.giver_id = '$myID' OR t.getter_id = '$myID') AND t.status = 'delivered' LIMIT 1");
$getData->execute;
if ($getData->rows != 1){
&errorCatcher("No result found, or you might not have access to view it.");
}else{
my ($giver_id, $getter_id, $listing_id, $timestamp, $listing_title, $listing_desc) = $getData->fetchrow_array;
$getData->finish;
my $user_id = ($giver_id eq $myID ? $getter_id : $giver_id);
$listing_title = &descTitle($listing_title, $listing_desc);
$listing_title = 'DELETED LISTING' if !$listing_title;
my $when = &getWhen($timestamp);
my ($stars, $comment);

## CHECK FOR EXISTING REVIEW
my $getReview = $SBdb->prepare("SELECT stars, comment FROM reviews WHERE trans_id = $trans_id AND reviewer_id = '$myID' AND target_id = $user_id LIMIT 1");
$getReview->execute;
if ($getReview->rows eq 1){($stars, $comment) = $getReview->fetchrow_array};
$getReview->finish;
my ($check1, $check2, $check3, $check4, $check5, $update);
if ($stars){
	if ($stars eq 1){$check1 = 'checked'}
	elsif ($stars eq 2){$check2 = 'checked'}
	elsif ($stars eq 3){$check3 = 'checked'}
	elsif ($stars eq 4){$check4 = 'checked'}
	elsif ($stars eq 5){$check5 = 'checked'}
	$update = 1;
}
my ($user_first_name, $user_last_name) = &getNames($user_id);
my $title = ($stars ? 'Edit your' : 'Write a');
$title .= ' review for ' . $user_first_name . ' ' . $user_last_name;
my $desc = qq~Please rate your experience with $user_first_name~;

my $inject = qq~~;

&header($title, $desc, undef, $inject, 'page');
print qq~<h2>$title</h2>
<form id="write_review">
<input type="hidden" name="a" value="postreview"/>
<input type="hidden" name="update" value="$update"/>
<input type="hidden" name="user_id" value="$user_id"/>
<input type="hidden" name="trans_id" value="$trans_id"/>
<p>Please rate your experience with $user_first_name for &apos;<a href="$baseURL/listing?id=$listing_id" target="_blank">$listing_title</a>&apos;, confirmed $when:</p>
    <p class="star-rating">
        <input disabled checked class="rating_input rating_input-none" name="rating" id="rating-none" value="0" type="radio">
        <label aria-label="1 star" class="rating_label" for="rating-1"><i class="rating_icon rating_icon-star fa fa-star"></i></label>
        <input class="rating_input" name="rating" id="rating-1" value="1" type="radio" $check1>
        <label aria-label="2 stars" class="rating_label" for="rating-2"><i class="rating_icon rating_icon-star fa fa-star"></i></label>
        <input class="rating_input" name="rating" id="rating-2" value="2" type="radio" $check2>
        <label aria-label="3 stars" class="rating_label" for="rating-3"><i class="rating_icon rating_icon-star fa fa-star"></i></label>
        <input class="rating_input" name="rating" id="rating-3" value="3" type="radio" $check3>
        <label aria-label="4 stars" class="rating_label" for="rating-4"><i class="rating_icon rating_icon-star fa fa-star"></i></label>
        <input class="rating_input" name="rating" id="rating-4" value="4" type="radio" $check4>
        <label aria-label="5 stars" class="rating_label" for="rating-5"><i class="rating_icon rating_icon-star fa fa-star"></i></label>
        <input class="rating_input" name="rating" id="rating-5" value="5" type="radio" $check5>
    </p>
	<p>How would you describe the transaction?</p>
<textarea name="comment" class="review-text">$comment</textarea>~;

if (!$update){
	print qq~
<input type="checkbox" name="notify_member" id="notify_member" value="1" checked/><label for="notify_member"> Notify $user_first_name of your review?</label>~;
}

print qq~

<p><input type="submit" value="Post Review" id="post_review" class="green-button"/></p>
</form>
~;

}
&footer;
}



sub myReviews{
&bounceNonLoggedIn('Please log in to see your reviews!');
my $resultsPP = 20;

my $title = 'My Reviews';
my $desc = 'Read and write my reviews';

my $query = qq~SELECT t.id, t.giver_id, t.getter_id, t.listing_id, r.stars, r.comment, r.timestamp, p.title, p.description FROM transactions AS t LEFT JOIN reviews AS r ON t.id = r.trans_id AND r.reviewer_id = '$myID' LEFT JOIN posts AS p ON p.id = t.listing_id WHERE (t.giver_id = '$myID' OR t.getter_id = '$myID') AND t.status = 'delivered' ORDER BY t.timestamp DESC, r.timestamp DESC~;

my $reviews = $SBdb->do("SELECT id FROM reviews WHERE reviewer_id = '$myID'");

my $num_results = $SBdb->do($query);
if ($num_results < 1){$num_results = 0;}
my $pending = $num_results - $reviews;
my $start = $FORM{start} || 0;
$query .= qq~ LIMIT $resultsPP OFFSET $start~;
my $prevURL = qq~reviews?a=myreviews&start=~ . ($start - $resultsPP);
my $nextURL = qq~reviews?a=myreviews&start=~ . ($start + $resultsPP);
my $heading;

if ($num_results > 0){ 
	my $resultsTo;
	if (($start + $resultsPP) > $num_results){$resultsTo = $num_results}else{$resultsTo = $start + $resultsPP};
	$heading = qq~Showing ~ . ($start + 1) . qq~ to ~ . $resultsTo . qq~ of $num_results reviews~;
}else{
$heading = qq~Nothing to review!~;
}

my $getTransactions = $SBdb->prepare($query);
$getTransactions->execute;

&header($title, $desc, undef, undef, 'page');

print qq~<h2>$title~; 
if ($pending > 0){print qq~ ($pending pending)~;} print qq~</h2>
<p>$heading</p>~;

if ($getTransactions->rows > 0){
while (my ($trans_id, $giver_id, $getter_id, $listing_id, $star_rating, $comment, $review_timestamp, $listing_title, $listing_desc) = $getTransactions->fetchrow_array){
my $user_id = ($giver_id eq $myID ? $getter_id : $giver_id);
my $reviewee_name = &getFullName($user_id);
$listing_title = &descTitle($listing_title, $listing_desc);
$listing_title = 'DELETED LISTING' if !$listing_title;
if ($star_rating){
my $stars = &renderStars($star_rating);
my $when = getWhen($review_timestamp);


print qq~<div class="review-box clearfix">
<p><a href="profile?id=$user_id">$reviewee_name</a> $stars<span class="smaller right grey">For: <a href="listing?a=showlisting&id=$listing_id">$listing_title</a><br/>$when</span></p>~;
if ($comment){print qq~
<p><span class="bigger">&#8220;</span>$comment<span class="bigger">&#8221;</span></p>~;
}
print qq~<p class="right smaller"><a href="$baseURL/reviews?a=write&trans_id=$trans_id"><i class="far fa-edit"></i> EDIT</a></p></div>~;
}else{
	
print qq~<p class="review-box"><a href="$baseURL/reviews?a=write&trans_id=$trans_id"><i class="fas fa-exclamation-circle"></i> Leave a review for $reviewee_name for $listing_title?</a></p>~;
}


}

if ($num_results > $resultsPP){
print qq~
<p class="center clear top20">
<a class="nav-button~; if ($start <= 0){print qq~ disabled~;} print qq~" href="$prevURL" title="Previous page"><i class="fas fa-chevron-circle-left fa-3x"></i></a>&nbsp;&nbsp;
<a class="nav-button~; if (($start + $resultsPP) >= $num_results){print qq~ disabled~;} print qq~" href="$nextURL" title="Next page"><i class="fas fa-chevron-circle-right fa-3x"></i></a>
</p>~;
}
$getTransactions->finish;

}

&footer;

}


$SBdb -> disconnect;
# Exeunt
