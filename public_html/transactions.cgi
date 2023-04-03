#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT CONTAINS TRANSACTIONS DATA

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );

require 'common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

;
&showTransactions;


sub showTransactions{
my $resultsPP = 50;
my $user_id = $FORM{id};
my $user_name = &getFullName($user_id) if ($user_id);
my $title = 'Sharebay Transaction Record';
my $desc = 'View the latest transactions on Sharebay public transaction record';
my $query = 'SELECT t.listing_id, t.listing_type, t.giver_id, t.getter_id, t.status, t.timestamp, p.title, p.description FROM transactions AS t LEFT JOIN posts AS p ON p.id = t.listing_id WHERE';
if ($myAdmin || $myModerator){$query .= qq~ t.status LIKE '%'~;}else{$query .= qq~ t.status = 'delivered'~;}
if ($user_id){
$title .= ' for ' . $user_name;
$query .= qq~ AND (t.giver_id = $user_id OR t.getter_id = $user_id)~;
}
my $num_results = $SBdb->do($query);
if ($num_results < 1){$num_results = 0;}
$query .= qq~ ORDER BY t.timestamp DESC LIMIT $resultsPP~;
my $start = $FORM{start} || 0;
$query .= qq~ OFFSET $start~;
my $prevURL = qq~transactions?id=$user_id&start=~ . ($start - $resultsPP);
my $nextURL = qq~transactions?id=$user_id&start=~ . ($start + $resultsPP);
my $heading;

if ($num_results > 0){
	my $resultsTo;
	if (($start + $resultsPP) > $num_results){$resultsTo = $num_results}else{$resultsTo = $start + $resultsPP};
	$heading = qq~Showing ~ . ($start + 1) . qq~ to ~ . $resultsTo . qq~ of $num_results records~;
}else{
$heading = qq~No results found~;
}
if ($user_id){
	$heading .= qq~ for $user_name~;
}

my $sth = $SBdb->prepare($query);
$sth->execute;
&header($title, $desc, undef, undef, 'page');
#~ $myAdmin = 0;
print qq~<h2>$title</h2>~;

if ($LOGGED_IN){&pendingActions;}

    print qq~<p>$heading</p><table class="trans-table"><tr><th width="25%" class="center">Item shared</th><th width="25%" class="center">Given by</th><th width="25%" class="center">Received by</th><th width="25%" class="center">Status</th></tr>~;
while (my ($listing_id, $listing_type, $giver_id, $getter_id, $status, $timestamp, $listing_title, $listing_desc) = $sth->fetchrow_array){
$status = ucfirst($status);
my $giver = $LOGGED_IN ? '<a href="profile?id=' . $giver_id . '" class="notranslate">' . &getFullName($giver_id) . '</a>' : 'Member from ' . &getRegion($giver_id);
my $getter = $LOGGED_IN ? '<a href="profile?id=' . $getter_id . '" class="notranslate">' . &getFullName($getter_id) . '</a>' : 'Member from ' . &getRegion($getter_id);
my $when = getDate($timestamp);
$listing_title = &descTitle($listing_title, $listing_desc);
if (!$listing_title){$listing_title = '[LISTING REMOVED]';}
print qq~<tr><td><a href="listing?a=showlisting&id=$listing_id">$listing_title</a></td><td>$giver</td><td>$getter</td><td class="smaller">$status, $when</td></tr>~;

}
print qq~</table>~;
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


$SBdb -> disconnect;
# Exeunt
