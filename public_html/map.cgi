#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR DISPLAYING THE SEARCH MAP

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );

require 'common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

&showMap;

sub showMap{

&bounceNonLoggedIn('Map view is only available to members. Please register or log in to continue.');


if (!$LOGGED_IN){
($myLat, $myLon, undef, undef, undef, undef) = &getCurrentLocation;
}
if ($FORM{myLat}){$myLat = $FORM{myLat};}
if ($FORM{myLon}){$myLon = $FORM{myLon};}
my $zoom;
if ($FORM{zoom}){$zoom = $FORM{zoom}}else{$zoom = 9};

my $title = 'Sharebay Map';
my $desc = "See what's available and who's in your area with our searchable map";
my $image;
my $headerInject = qq~
<script type="text/javascript">
var myLat = $myLat;
var myLon = $myLon;
var myZoom = $zoom;
var mapN = '$FORM{n}';
var mapS = '$FORM{s}';
var mapE = '$FORM{e}';
var mapW = '$FORM{w}';
var query = '$FORM{query}';
</script>~;

my $footerInject = qq~
<script type="text/javascript" src="$baseURL/js/map.js?v=$version"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/OverlappingMarkerSpiderfier/1.0.3/oms.min.js"></script>
<!-- script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?v=3&key=AIzaSyD4zc3ELJ8ZgqLMZqLhLGv7beewD6wN9eU"></script -->~;


&header($title, $desc, $image, $headerInject, 'map');

my ($memberCheck, $offersCheck, $requestsCheck, $sharepointsCheck);
if ($FORM{in}){
if ($FORM{in} =~ m/offers/){$offersCheck = 'checked'};
if ($FORM{in} =~ m/requests/){$requestsCheck = 'checked'};
if ($FORM{in} =~ m/members/){$memberCheck = 'checked'};
if ($FORM{in} =~ m/sharepoints/){$sharepointsCheck = 'checked'};
}else{
$offersCheck = 'checked';
$requestsCheck = 'checked';
#~ $memberCheck = 'checked';
#~ $sharepointsCheck = 'checked';
}

my ($strictCheck, $nolimitCheck, $last7check);
if ($FORM{strict} eq 'tags'){$strictCheck = 'checked';}
if ($FORM{last7} eq 'y'){$last7check = 'checked';}
if ($FORM{showall} eq 'y'){$nolimitCheck = 'checked';}


print qq~
<div id="mapbar">
<div class="filter-block">
<input type="checkbox" id="offers" class="map-filter" name="offers" $offersCheck/><label for="offers" title="Search offers only">Offers</label>
</div>
<div class="filter-block">
<input type="checkbox" id="requests" class="map-filter" name="requests" $requestsCheck/><label for="requests" title="Search requests only">Requests</label>
</div>~;
if ($myAdmin || $myModerator){
print qq~
<div class="filter-block">
<input type="checkbox" id="members" class="map-filter" name="members" $memberCheck/><label for="members" title="Search members only">Members</label>
</div>~;
}
print qq~
<div class="bigOnlyInline">
<div class="filter-block">
<input type="checkbox" id="sharepoints" class="map-filter" name="sharepoints" $sharepointsCheck/><label for="sharepoints" title="Search sharepoints / libraries / resource banks only">Share Points</label>
</div>
<div class="filter-block">
<input type="checkbox" id="strict" class="map-filter" name="strict" value="tags" $strictCheck/><label for="strict" title="Strict search mode. Only matches tags">Search tags only</label>
</div>~;
if ($myAdmin || $myModerator){
print qq~
<div class="filter-block">
<input type="checkbox" id="last7" class="map-filter" name="last7" value="y" $last7check/><label for="last7" title="Show only results from the last seven days">Last 7 Days</label>
</div>
<div class="filter-block">
<input type="checkbox" id="showall" class="map-filter" name="showall" value="y" $nolimitCheck/><label for="showall" title="By default only a maximum of 100 results are shown. Click to remove this limit">Unlimited results</label>
</div>~;
}

print qq~
<div class="filter-block">
<a href="javascript:void(0);" id="list-view" title="List view">LIST VIEW</a>
</div>

</div>
</div>
<div id="map_div"></div>
<div id="map_results"><span id="total"></span></div>~;

&bareFooter($footerInject);
}

$SBdb -> disconnect;
# Exeunt
