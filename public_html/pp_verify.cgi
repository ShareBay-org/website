#!/usr/bin/perl
use cPanelUserConfig;

# THIS IS A BACKGROUND SCRIPT FOR PROCESSING PAYPAL PAYMENTS
# INCLUDING DONATIONS AND OTHER SALE ITEMS

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
# use strict;
# use warnings;
# use CGI::Carp qw( fatalsToBrowser );

require 'common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);
our $buffer; # ADDED TO ENABLE SHARING QUERY STRING FROM COMMON.PL

# FOR RETURNING CONFIRMATIONS AND ERRORS (DEPRECATED)
my $mailprog = '/usr/sbin/sendmail';
my $adminMail = 'colinrturner@gmail.com';

# TO CONSTRUCT RESPONSE TO PAYPAL IPN
my $query = $buffer;
my %variable;
my $return = 'cmd=_notify-validate&' . $buffer;

# RESPOND TO PAYPAL USING LWP
use LWP::UserAgent;
my $ua = LWP::UserAgent->new(ssl_opts => { verify_hostname => 1 });
my $req = HTTP::Request->new('POST', 'https://www.paypal.com/cgi-bin/webscr');
$req->content_type('application/x-www-form-urlencoded');
$req->header(Host => 'www.paypal.com');
$req->content($return);
my $res = $ua->request($req);

# PROCESS FORM DATA
my @pairs = split(/&/, $query);
foreach my $pair (@pairs) {
my ($name, $value) = split(/=/, $pair);
$value =~ tr/+/ /;
$value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
$variable{$name} = $value;
}

my $error;

# CREATE VARIABLES FROM FORM INPUT
my $item_name = $variable{'item_name'};
my $first_name = $variable{'first_name'};
my $last_name = $variable{'last_name'};
my $item_number = $variable{'item_number'};
my $payment_status = $variable{'payment_status'};
my $payment_amount = $variable{'mc_gross'};
my $payment_currency = $variable{'mc_currency'};
my $buyer_email = $variable{'payer_email'};
my $txn_id = $variable{'txn_id'};

if ($res->is_error){
# LWP RESULT OR CONNECTION ERROR
$error = "LWP communication error";
&error;}

elsif ($res->content eq 'VERIFIED'){
# TRANSACTION VERIFIED

if ($payment_status eq "Completed"){
# PAYMENT SUCCESSFULLY COMPLETED, CHECK NAME, AMOUNT AND UPDATE TRANSACTION:

if ($item_name eq 'Sharebay item shipping'){
my $getCost = $SBdb->prepare("SELECT giver_id, getter_id, listing_id, shipping_cost FROM transactions WHERE id = '$item_number' LIMIT 1");
$getCost->execute;
my ($giver_id, $getter_id, $listing_id, $shipping_cost) = $getCost->fetchrow_array;
$getCost->finish;

my $expected_total = sprintf("%.2f", ($shipping_cost + &processingFee($shipping_cost)));
if ($payment_amount eq $expected_total){
	
# GOOD TO GO. MARK TRANSACTION PAID AND SEND MESSAGE
my $getter_name = &getFullName($getter_id);
my $title = &getListingTitle($listing_id);
my $titleLink = qq~<a href="$baseURL/listing?id=$listing_id">$title</a>~;
my $alert = qq~$getter_name has paid \$$shipping_cost for the delivery of $titleLink~;
my $update = $SBdb->do("UPDATE transactions SET status = 'paid' WHERE id = '$item_number' LIMIT 1");
&sendMessage($getter_id, $giver_id, $alert, 'alert');
}else{
# AMOUNT MISMATCH
$error = "Wrong amount paid for Transaction $item_number: $payment_amount Paid. Should have been $expected_total";
&error;
}

}else{
# UNKNOWN ITEM
$error = "Unknown item: $item_name";
&error;
}

}else{
# PAYMENT NOT COMPLETED
$error = "Payment not completed. Payment status returned was: " . $payment_status;
&error;
}
}

elsif ($res->content eq 'INVALID'){
# PAYPAL REJECTED RESPONSE
$error = "Paypal rejected IPN response with 'INVALID'.";
&error;
}
else{
# PAYPAL DIDN'T VERIFY CONTENT
$error = "Content not verified.";
&error;
}


sub error{
# PROCESS ERRORS

# WRITE TO ERROR LOG
open (LOG, ">>$root/errorlog");
print LOG "$now|$error|$item_name|$item_number|$buyer_email|$payment_amount|$txn_id\n";
close (LOG);
open(MAIL, "|$mailprog $adminMail") || die "Can't open $mailprog!";
print MAIL "To: $adminMail\nFrom: $adminMail\n";
print MAIL "Subject: Paypal Payment Error!\n\n";
print MAIL "Error: $error\n\nPP Query: $query\n\nReturned: $return\n\nTransaction ID: $txn_id\n\nCustomer Email: $buyer_email\n\n$now";
close (MAIL);
}


print "Content-Type: text/html; charset=utf-8\n\n";

$SBdb->disconnect;
# Exeunt
