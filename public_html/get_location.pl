#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT RETURNS LOCATION DATA FROM IP ADDRESS

sub getIPLocation{
my $ip = shift;

use LWP::UserAgent;
use JSON::PP;
my $this = time();

## DEFAULT VALUES:
my $lat = 51.42;
my $lon = 0;
my $city = 'London';
my $region = 'London';
my $country = 'United Kingdom';
my $country_iso = 'GB';


my $ua = LWP::UserAgent->new;
$ua->agent('Mozilla/5.0');
$ua->default_header('Accept-Encoding' => scalar HTTP::Message::decodable());
$ua->timeout(20);

## START LOOP TO CHECK FOR LOCK FILE
for (my $i=1; $i<10; $i++){
if (-e "/home/sharebay/IPLOC_$this"){
sleep 2;
}else{
## OK, CREATE LOCK FILE
open (my $LOCK, '>', "/home/sharebay/IPLOC_$this");
close ($LOCK);

## GET DATA

my $url = 'http://ip-api.com/json/' . $ip;
my $req = $ua->get($url);
if ($req->is_success){
my $content = $req->decoded_content;
my $IPDATA = decode_json($content);
$lat = $IPDATA->{'lat'};
$lon = $IPDATA->{'lon'};
$city = $IPDATA->{'city'};
$region = $IPDATA->{'regionName'};
$country = $IPDATA->{'country'};
$country_iso = $IPDATA->{'countryCode'};
}

unlink ("/home/sharebay/IPLOC_$this");
last;
}
}
return ($lat, $lon, $city, $region, $country, $country_iso);
};

1;
# EXEUNT;
