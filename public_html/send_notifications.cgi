#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR SENDING AND MANAGING USER
# NOTIFICATIONS

# use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );
my $active = 1; # 0 to disable
my $output = 1; # FOR TESTING
require '/home/sharebay/public_html/common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

if ($maintenance){$active = 0}; # DISABLE IN MAINTENANCE MODE
print qq~Content-type: text/plain; charset=utf-8\n\n~ if $output;

if ($active){

&sendMessages;
&sendActivationReminders;
&sendPostReminders;
&sendTransactionReminders;
&sendCompleteProfileReminders;
&sendSharebayEmail;
&sendCongrats;
&sendInvitePrompt;
&sendInviteCongrats;
# &sendReviewReminders;
&sendInteractions;
&sendUpdateListingReminders;

$SBdb->disconnect;
}



sub sendUpdateListingReminders{
my $count = 0;
my $getListings = $SBdb->prepare("SELECT id, lister, title, description, image, timestamp FROM posts WHERE status = 'live' AND ((timestamp BETWEEN ($now - 15552000) AND ($now - 15552300)) OR (timestamp BETWEEN ($now - 31536300) AND ($now - 31536000)))");
$getListings->execute;
if ($getListings->rows > 0){
while (my ($id, $lister, $title, $description, $image, $timestamp) = $getListings->fetchrow_array){
my $days = int($timestamp / 86400);
$title = substr($description, 0, 50) . '...' if !$title;
my $subject = qq~Your listing is $days days old. Would you like to review it?~;
my $body = qq~Hi there, we noticed your listing '$title' is $days days old and thought you might like the chance to review or cancel it. If you're still happy with your listing, then no action is required. All our listings remain live until completed or deleted.

If you'd like to amend your listing, please click the button below.

Thanks,
The Sharebay Team~;
my $call2act = 'Edit listing';
my $link = qq~$baseURL/listing?a=edit&id=$id~;
$count++ if &sendMail($lister, $notify, $subject, undef, $body, $call2act, $link, $image, undef);
}
print "$count update reminders sent.\n";
}
}


sub sendInteractions{	
my $count = 0;
my $getComments = $SBdb->prepare("SELECT i.id, i.actor_id, i.object_type, i.object_id, i.thread, i.timestamp, m.first_name, m.last_name FROM interactions AS i JOIN members AS m ON m.id = i.actor_id WHERE i.action = 'comment' AND i.status != 'seen' AND i.timestamp > ($now - 300)");

$getComments->execute;
if ($getComments->rows > 0){
	
## OK, FIND THE OWNER AND NOTIFY THEM.
while(my ($comment_id, $actor_id, $object_type, $object_id, $thread, $timestamp, $first_name, $last_name) = $getComments->fetchrow_array){
	
if ($comment_id eq $thread){
## IT'S A TOP LEVEL COMMENT. SEND COMMENT NOTIFICATIONS
	
if ($object_type eq 'listing'){
	
my $getLister = $SBdb->prepare("SELECT p.title, p.description, m.id, m.first_name, m.email FROM posts AS p JOIN members AS m ON p.lister = m.id WHERE p.id = '$object_id' LIMIT 1");
$getLister->execute;
if ($getLister->rows eq 1){
my ($listing_title, $listing_desc, $owner_id, $owner_name, $email) = $getLister->fetchrow_array;
unless ($actor_id eq $owner_id){
# SEND EMAIL IF COMMENT NOT FROM ME
$listing_title = substr($listing_desc, 0, 50) . '...' if !$listing_title;
my $subject = 'New comment on ' . $listing_title;
my $body = qq~$first_name $last_name just commented on your listing '$listing_title'.~;
my $call2act = "Read comment";
my $link = $baseURL . '/listing?id=' . $object_id;

# SEND EMAIL
$count++ if &sendMail($email, $notify, $subject, $owner_name, $body, $call2act, $link, undef, undef);
}
}
$getLister->finish;

}elsif($object_type eq 'profile'){
	
my $getProfile = $SBdb->prepare("SELECT first_name, email FROM members WHERE id = '$object_id' AND activated = 1 LIMIT 1");
$getProfile->execute;
my ($owner_name, $email) = $getProfile->fetchrow_array;
if ($getProfile->rows eq 1){
unless ($actor_id eq $object_id){
# SEND EMAIL
my $subject = $first_name . ' commented on your profile';
my $body = qq~$first_name $last_name just commented on your profile page.~;
my $call2act = "Read comment";
my $link = $baseURL . '/profile?id=' . $object_id;

# SEND EMAIL
$count++ if &sendMail($email, $notify, $subject, $owner_name, $body, $call2act, $link, undef, undef);
}
}
$getProfile->finish;
	
}elsif($object_type eq 'blog'){
	
my $getAuthor = $SBdb->prepare("SELECT b.title, b.slug, m.id, m.first_name, m.email FROM blog AS b JOIN members AS m ON b.author_id = m.id WHERE s.id = '$object_id' LIMIT 1");
$getAuthor->execute;
if ($getAuthor->rows eq 1){
my ($blog_title, $blog_slug, $owner_id, $owner_name, $email) = $getAuthor->fetchrow_array;
unless ($actor_id eq $owner_id){
# SEND EMAIL
my $subject = $first_name . ' commented on your article';
my $body = qq~$first_name $last_name just commented on your article '$blog_title'.~;
my $call2act = "Read comment";
my $link = $baseURL . '/blog/' . $blog_slug;

# SEND EMAIL
$count++ if &sendMail($email, $notify, $subject, $owner_name, $body, $call2act, $link, undef, undef);
 }
}
$getAuthor->finish;
	
}else{
## TYPE UNKNOWN - DO NOTHING

}
}else{
## IT'S A REPLY. SEND NOTIFICATIONS TO EVERYONE ELSE ON THREAD

my $getThreaders = $SBdb->prepare("SELECT i.id, m.first_name, m.email FROM interactions AS i JOIN members AS m ON m.id = i.actor_id WHERE i.action = 'comment' AND i.thread = '$thread' AND i.object_type = '$object_type' AND i.object_id = '$object_id' AND i.actor_id != '$actor_id' GROUP BY i.actor_id");
$getThreaders->execute;
if ($getThreaders->rows > 0){
while (my ($cid, $commenter_name, $email) = $getThreaders->fetchrow_array){
	
# SEND EMAIL
my $subject = $first_name . ' replied to a comment';
my $body = qq~$first_name $last_name just replied to a comment you're following on Sharebay.~;
my $call2act = "See reply";
my $link = $baseURL;
$link .= '/blog?id=' . $object_id if $object_type eq 'blog';
$link .= '/profile?id=' . $object_id if $object_type eq 'profile';
$link .= '/listing?id=' . $object_id if $object_type eq 'listing';

# SEND EMAIL
$count++ if &sendMail($email, $notify, $subject, $commenter_name, $body, $call2act, $link, undef, undef);

}
}
$getThreaders->finish;
}
}
}
$getComments->finish;
print "$count interaction alerts sent.\n";
}



sub sendMessages{
# EMAIL UNSEEN MESSAGES TO USER

my $count = 0;
my $sth = $SBdb->prepare("SELECT GROUP_CONCAT(id SEPARATOR ','), sender, recipient, convo_id, type, timestamp, GROUP_CONCAT(message SEPARATOR 'QjQ') FROM messages WHERE status = 'sent' GROUP BY sender, recipient ORDER BY id ASC");

$sth->execute;
if ($sth->rows > 0){
while (my ($message_ids, $sender, $recipient, $convo_id, $type, $timestamp, $message) = $sth->fetchrow_array){
my $rec_email = &getEmail($recipient);
my ($rec_fname, $rec_lname) = &getNames($recipient);
my ($sndr_fname, $sndr_lname) = &getNames($sender);
my $subject;
my @MESSAGES = split('QjQ', $message);
if ($type eq 'alert'){
$subject = $MESSAGES[0];
$subject =~ s/<[^>]+>//g; #REMOVE HTML
}else{
$subject = qq~Message from $sndr_fname $sndr_lname~;
}
# SPLIT MESSAGES WITH HR
my $body .= join('<hr/>', @MESSAGES);
$subject = substr($subject, 0, 100) . '...' if length($subject) > 100;

my $call2act = qq~Reply to $sndr_fname~;
my $link = $baseURL . '/messages?id=' . $convo_id;

# SEND EMAIL
$count++ if &sendMail($rec_email, $notify, $subject, undef, $body, $call2act, $link, undef, undef);

# MARK MESSAGES AS SENT
my $markNotified = $SBdb->do("UPDATE messages SET status = 'notified' WHERE id IN ($message_ids)");
}
}
$sth->finish;
print "$count message alerts sent.\n";
}


sub sendActivationReminders{
## SEND ACTIVATION REMINDERS ONE DAY AND FOUR DAYS LATER
my $count = 0;
my $sth = $SBdb->prepare("SELECT id, email, authcode FROM members WHERE joined > 0 AND activated = 0 AND (joined BETWEEN $now - 86400 AND $now - 86100 OR joined BETWEEN $now - 345600 AND $now - 345300)");
$sth->execute;
if ($sth->rows > 0){
while (my ($id, $email, $authcode) = $sth->fetchrow_array){
my $subject = qq~Reminder to set up your Sharebay account~;
my $body = qq~Remember to activate your Sharebay account so you can start enjoying free goods and services - and offering them too!\n\nClick here to activate your account:~;
my $call2act = qq~Continue~;
my $link = qq~$baseURL/edit?token=$authcode~;
$count++ if &sendMail($email, $notify, $subject, undef, $body, $call2act, $link, undef, undef);
}
}
$sth->finish;
print "$count activation reminders sent.\n";
}


sub sendInviteCongrats{
## CONGRATULATE MEMBERS ON SUCCESSFUL INVITE 90 MINUTES AFTER JOINING

my $sth = $SBdb->prepare("SELECT id, first_name, last_name, email, image, mailme, badmail, invited_by FROM members WHERE activated = 1 AND invited_by != '' AND joined BETWEEN $now - 5400 AND $now - 5100");
$sth->execute;
if ($sth->rows > 0){
while (my ($id, $first_name, $last_name, $email, $image, $mailme, $badmail, $invited_by) =  $sth->fetchrow_array){

my $getInviter = $SBdb->prepare("SELECT id, first_name, last_name, email, image, mailme, badmail FROM members WHERE authcode LIKE '$invited_by%' LIMIT 1");
$getInviter->execute;
if ($getInviter->rows eq 1){
my ($i_id, $i_first_name, $i_last_name, $i_email, $i_image, $i_mailme, $i_badmail) = $getInviter->fetchrow_array;

if ($i_mailme eq 1 && $i_badmail eq 0){
## SEND EMAIL TO INVITER...
my $call2act = 'Welcome ' . $first_name;
my $link = $baseURL . '/profile?id=' . $id;
$image = "$baseURL/user_pics/$image\.jpg" if $image;
my $subject = qq~$first_name $last_name accepted your invitation!~;
my $body = qq~Hey $i_first_name, we're delighted to say that $first_name $last_name just accepted your invitation and is now a member of Sharebay! Thank you for helping us build a wider network, and we hope you and $first_name can make good use of our giving community.

Why not check out their profile and say hi?
~;
&sendMail($email, $notify, $subject, undef, $body, $call2act, $link, $image, undef);
}

if ($mailme eq 1 && $badmail eq 0){
## SEND EMAIL TO INVITEE...
my $call2act = 'Say hi to ' . $i_first_name;
my $link = $baseURL . '/profile?id=' . $i_id;
$i_image = "$baseURL/user_pics/$i_image\.jpg" if $i_image;
my $subject = qq~Say hi to $i_first_name $i_last_name!~;
my $body = qq~Hey $first_name, we thought you might like to say hi to $i_first_name $i_last_name and thank them for bringing you on board!

Thank you for helping us build a wider network, and we hope you and $i_first_name can make good use of our giving community.
~;
&sendMail($i_email, $notify, $subject, undef, $body, $call2act, $link, $i_image, undef);
}
}
$getInviter->finish;
}
}
$sth->finish;
}


sub sendCompleteProfileReminders{
## ENCOURAGE MEMBERS TO ADD PROFILE DETAILS 3 DAYS AFTER JOINING

my $count = 0;

## TESTING...
# my $sth = $SBdb->prepare("SELECT id, first_name, email FROM members WHERE id = 30");

my $sth = $SBdb->prepare("SELECT id, first_name, email FROM members WHERE mailme = 1 AND activated = 1 AND badmail = 0 AND ((LENGTH(about_me) + LENGTH(tags)) < 20) AND joined BETWEEN $now - 259300 AND $now - 259000");

$sth->execute;
if ($sth->rows > 0){

my $body = qq~Hey there stranger, thank you again for joining our wonderful little sharing network. But...we don't know very much about you! :/\n\nSharebay uses information from people's profiles, searches and views to get an idea what sort of things you like and what to show you.\n\nWhy not take a couple of minutes to write a little more about yourself?\n\nYou can write a short bio, tell us what you're good at and what things interest you. The more we know about you, the more we can bring you the things you like.\n\n<a href="$baseURL/edit">Click here</a> to edit your profile:~;
my $call2act = 'Edit profile';
my $link = $baseURL . '/edit';
my $image = $baseURL . '/i/stranger.png';
while (my ($id, $first_name, $email) =  $sth->fetchrow_array){
my $subject = qq~$first_name, we'd love to know more about you~;
$count++ if &sendMail($email, $notify, $subject, undef, $body, $call2act, $link, $image, undef);
}
}
$sth->finish;
print "$count complete profile reminders sent.\n";
}



sub sendPostReminders{
## SEND REMINDERS TO EMPTY LISTERS TO POST 1 DAY, 4 DAYS, 7 DAYS AND 17 DAYS AFTER JOINING

my $count = 0;
## USE FOR TESTING...
# my $sth = $SBdb->prepare("SELECT m.id, m.first_name, m.email, COUNT(p.id) AS listing_count FROM members AS m LEFT JOIN posts AS p ON m.id = p.lister WHERE m.mailme = 1 AND m.activated = 1 AND m.badmail = 0  AND m.id = 30");

my $sth = $SBdb->prepare("SELECT m.id, m.first_name, m.email, COUNT(p.id) AS listing_count FROM members AS m LEFT JOIN posts AS p ON m.id = p.lister WHERE m.mailme = 1 AND m.activated = 1 AND m.badmail = 0  AND (
m.joined BETWEEN $now - 86400 AND $now - 86100 OR 
m.joined BETWEEN $now - 345600 AND $now - 345300 OR 
m.joined BETWEEN $now - 604800 AND $now - 604500 OR 
m.joined BETWEEN $now - 1468800 AND $now - 1468500
) GROUP BY m.id HAVING listing_count = 0");

my @subjects = (
"Wait! Something's missing...",
"What skills can you bring to Sharebay?",
"Have you got something you'd like to offer?",
"Sharebay is looking for your unused items",
"Help build our network with a great offer",
"Add your listing to Sharebay"
);

my $subject = $subjects[rand @subjects];

my @bodies = (
"It's great that you're here! But we noticed that you haven't offered anything yet. Why not help us build a great sharing network by offering something that someone else here might appreciate?",
"Thanks for being here. As you know, Sharebay is a sharing network, but we're only as good as the items on offer from our members. You haven't added anything yet. Is there something that you'd like to add to our amazing inventory of free goods and services?",
"We noticed that you haven't added any offers yet on Sharebay. Have you got an item or a service that you can share with someone who could really use it?",
"It's really easy to get started on Sharebay with a simple offer of any item or skill that you can spare. Would you like to add your first listing?",
"Thank you for joining our amazing sharing network. Obviously a network like this relies on the generosity of its members to succeed. If you're unsure what to offer, don't worry, everyone has something of value to share. Try one of our <a href=\"$baseURL/page?id=templates\">offer templates</a> to inspire you!",
"Have you got something useful or cool that you'd like to share on our network? Sharebay is a growing community and we rely on the generosity of our members to create a great inventory for everyone. Why not add an offer now and see what amazing people you'll meet?"
);

my $body = $bodies[rand @bodies];

$body .= qq~\n\nClick here to post an offer:~;

$sth->execute;
if ($sth->rows > 0){
while (my ($id, $first_name, $email, $listings) = $sth->fetchrow_array){
$body = qq~Hey $first_name!\n\n~ . $body;
my $call2act = qq~Add offer~;
my $link = qq~$baseURL/post~;
&sendMail($email, $notify, $subject, undef, $body, $call2act, $link, undef, undef);
}
}
$sth->finish;
print "$count post reminders sent.\n";
}



sub sendTransactionReminders{
# CHECK FOR PENDING TRANSACTIONS
# REMINDERS @ 2.5, 5, 8.5 & 20 days, DELETE 90+ DAYS

my $count = 0;

my $transactions = $SBdb->prepare("SELECT id, listing_id, listing_type, giver_id, getter_id, status, timestamp FROM transactions WHERE (status = 'applied' OR status = 'accepted' OR status = 'granted' OR status = 'sent') AND (
timestamp BETWEEN $now - 216300 AND $now - 216000 OR 
timestamp BETWEEN $now - 432300 AND $now - 432000 OR 
timestamp BETWEEN $now - 734600 AND $now - 734300 OR
timestamp BETWEEN $now - 1728300 AND $now - 1728000 OR
timestamp < $now - 7776300
) ORDER by timestamp");
$transactions->execute;

if ($transactions->rows > 0){

while (my ($id, $listing_id, $listing_type, $giver_id, $getter_id, $status, $timestamp) = $transactions->fetchrow_array){

if ($timestamp < $now - 7776150){
# CANCEL TRANSACTIONS 90 DAYS OLD OR MORE AND NOTIFY BOTH USERS

my $delete = $SBdb->do("UPDATE transactions SET status = 'auto-cancelled' WHERE id = '$id' LIMIT 1");

my $getter_name = &getFullName($getter_id);
my $giver_name = &getFullName($giver_id);
my $listing_title = &getListingTitle($listing_id);
my $when = &getWhen($timestamp);
my $message1 = qq~Transaction has been cancelled~;
my $message2 = qq~Your transaction with $getter_name for $listing_title from $when has been cancelled due to non-activity.~;
my $message3 = qq~Your transaction with $giver_name for $listing_title from $when has been cancelled due to non-activity.~;
&sendMessage($getter_id, $giver_id, $message1, 'alert');
&sendMessage($getter_id, $giver_id, $message2, 'alert');
&sendMessage($giver_id, $getter_id, $message1, 'alert');
&sendMessage($giver_id, $getter_id, $message3, 'alert');
}



elsif ($listing_type eq 'offer' && $status eq 'applied'){

# OFFER + APPLIED = REMIND GIVER TO ACCEPT
# SOMEONE APPLIED TO YOUR LISTING OFFER - ACCEPT?

my $getter_name = &getFullName($getter_id);
my $listing_title = &getListingTitle($listing_id);
my $when = &getWhen($timestamp);
my $message1 = qq~Reminder: $getter_name is waiting to hear from you.~;
my $message2 = qq~$getter_name applied to your offer of '$listing_title' $when and is waiting for your response. You need to accept their application to proceed with your offer. (Please note pending transaction are automatically deleted after 60 days)~;
&sendMessage($getter_id, $giver_id, $message1, 'alert');
&sendMessage($getter_id, $giver_id, $message2, 'alert');
}




elsif ($listing_type eq 'offer' && $status eq 'accepted'){

# OFFER + ACCEPTED = REMIND GIVER TO SEND
# SOMEONE ACCEPTED YOUR APPLICATION TO THEIR OFFER - SEND ITEM?

my $getter_name = &getFullName($getter_id);
my $listing_title = &getListingTitle($listing_id);
my $when = &getWhen($timestamp);
my $message1 = qq~Reminder to send '$listing_title' to $getter_name.~;
my $message2 = qq~$getter_name is waiting for you to send '$listing_title'. Please confirm as soon as you have sent the item. (Please note all pending transaction are deleted after 60 days)~;
&sendMessage($getter_id, $giver_id, $message1, 'alert');
&sendMessage($getter_id, $giver_id, $message2, 'alert');
}




elsif ($listing_type eq 'offer' && $status eq 'sent'){

# OFFER + SENT = REMIND GETTER TO CONFIRM DELIVERY
# SOMEONE SENT YOUR ITEM - CONFIRM DELIVERY?
my $giver_name = &getFullName($giver_id);
my $listing_title = &getListingTitle($listing_id);
my $when = &getWhen($timestamp);
my $message1 = qq~Reminder: $giver_name is waiting to hear from you.~;
my $message2 = qq~$giver_name sent '$listing_title' $when and is waiting for you to confirm delivery. Please confirm delivery to ensure that the final transaction is recorded. (Please note all pending transaction are deleted after 60 days)~;
&sendMessage($giver_id, $getter_id, $message1, 'alert');
&sendMessage($giver_id, $getter_id, $message2, 'alert');
}




elsif ($listing_type eq 'request' && $status eq 'applied'){

# REQUEST + APPLIED = REMIND GETTER TO ACCEPT
# SOMEONE APPLIED TO YOUR LISTING REQUEST - ACCEPT?
my $giver_name = &getFullName($giver_id);
my $listing_title = &getListingTitle($listing_id);
my $when = &getWhen($timestamp);
my $message1 = qq~Reminder: $giver_name is waiting to hear from you.~;
my $message2 = qq~$giver_name offered to grant your request for '$listing_title' $when and is waiting for you to accept their offer. You need to accept their offer to proceed with this transaction. (Please note all pending transaction are deleted after 60 days)~;
&sendMessage($giver_id, $getter_id, $message1, 'alert');
&sendMessage($giver_id, $getter_id, $message2, 'alert');
}




elsif ($listing_type eq 'request' && $status eq 'accepted'){

# REQUEST + ACCEPTED = REMIND GIVER TO GRANT REQUEST
# SOMEONE ACCEPTED YOUR OFFER TO GRANT REQUEST - GRANT REQUEST?
my $getter_name = &getFullName($getter_id);
my $listing_title = &getListingTitle($listing_id);
my $when = &getWhen($timestamp);
my $message1 = qq~Reminder: $getter_name is waiting to hear from you.~;
my $message2 = qq~$getter_name accepted your offer to grant their request for '$listing_title' $when and is waiting for you grant their request. Please grant the request to proceed with this transaction. (Please note all pending transaction are deleted after 60 days)~;
&sendMessage($getter_id, $giver_id, $message1, 'alert');
&sendMessage($getter_id, $giver_id, $message2, 'alert');
}




elsif ($listing_type eq 'request' && $status eq 'granted'){

# REQUEST + GRANTED = REMIND GETTER TO CONFIRM DELIVERY
# SOMEONE GRANTED YOUR REQUEST - CONFIRM DELIVERY?
my $giver_name = &getFullName($giver_id);
my $listing_title = &getListingTitle($listing_id);
my $when = &getWhen($timestamp);
my $message1 = qq~Reminder: $giver_name is waiting to hear from you.~;
my $message2 = qq~$giver_name granted your request for '$listing_title' $when and is waiting for you to confirm delivery. Please confirm delivery to ensure that the final transaction is recorded. (Please note all pending transaction are deleted after 60 days)~;
&sendMessage($giver_id, $getter_id, $message1, 'alert');
&sendMessage($giver_id, $getter_id, $message2, 'alert');
}
}
}
$transactions->finish;


## SEND A REVIEW REMINDER 24 HOURS LATER
my $getCompleteTrans = $SBdb->prepare("SELECT t.id, t.giver_id, t.getter_id, p.title FROM transactions AS t LEFT JOIN posts AS p ON p.id = t.listing_id WHERE t.status = 'delivered' AND t.timestamp BETWEEN $now - 86550 AND $now - 86250");

$getCompleteTrans->execute;
if ($getCompleteTrans->rows > 0){
while(my ($id, $giver_id, $getter_id, $listing_title) = $getCompleteTrans->fetchrow_array){
	
if ($SBdb->do("SELECT id FROM reviews WHERE reviewer_id = $giver_id AND trans_id = '$id'") != 1){
my $getter_name = &getFullName($getter_id);
	
my $message = qq~Tell us about your recent experience sharing '$listing_title' with $getter_name. Member reviews are a key part of building trust on our site and help others to make informed choices.~;

my $subject = "Leave a review for $getter_name";
my $call2act = 'Leave a review';
my $link = "$baseURL/reviews?a=write&trans_id=$id";
my $image = "$baseURL/i/five-stars.jpg";

# SEND EMAIL
$count++ if &sendMail($giver_id, $notify, $subject, undef, $message, $call2act, $link, $image, undef);
}
	
if ($SBdb->do("SELECT id FROM reviews WHERE reviewer_id = $getter_id AND trans_id = '$id'") != 1){
my $giver_name = &getFullName($giver_id);
	
my $message = qq~Tell us about your recent experience getting '$listing_title' from $giver_name. Member reviews are a key part of building trust on our site and help others to make informed choices.~;

my $subject = "Leave a review for $giver_name";
my $call2act = 'Leave a review';
my $link = "$baseURL/reviews?a=write&trans_id=$id";
my $image = "$baseURL/i/five-stars.jpg";

# SEND EMAIL
$count++ if &sendMail($getter_id, $notify, $subject, undef, $message, $call2act, $link, $image, undef);
}
}
}
print "$count review reminders sent.\n";
}


sub sendSharebayEmail{
# SEND NEWS ALERTS AND SITE UPDATES

my $count = 0;

## USE FOR TESTING
# my $sth = $SBdb->prepare("SELECT m.id, m.first_name, m.email, m.authcode, COUNT(p.id) AS listing_count FROM members AS m LEFT JOIN posts AS p ON m.id = p.lister WHERE m.id = 'x' GROUP BY m.id");

## USE FOR LEGAL / IMPORTANT NOTIFICATIONS
my $sth = $SBdb->prepare("SELECT id, first_name, email, authcode, 0 FROM members WHERE mailme_sent = 0 AND activated = 1 AND badmail = 0");

## USE FOR ALL OPT-IN MEMBERS
# my $sth = $SBdb->prepare("SELECT id, first_name, email, authcode, 0 FROM members WHERE mailme = 1 AND mailme_sent = 0 AND activated = 1 AND badmail = 0");

## USE FOR ALL NON-ACTIVATED MEMBERS
# my $sth = $SBdb->prepare("SELECT id, first_name, email, authcode, 0 FROM members WHERE activated = 0 AND mailme_sent = 0 AND badmail = 0");

## MEMBERS WHO HAVE NO LISTING
# my $sth = $SBdb->prepare("SELECT m.id, m.first_name, m.email, m.authcode, COUNT(p.id) AS listing_count FROM members AS m LEFT JOIN posts AS p ON m.id = p.lister WHERE m.mailme = 1 AND m.mailme_sent = 0 AND m.activated = 1 AND m.badmail = 0 GROUP BY m.id HAVING listing_count = 0");

$sth->execute;
if ($sth->rows > 0){
	
while (my ($id, $name, $email, $authcode, $listing_count) = $sth->fetchrow_array){

#SEND EMAIL
my $to = $email;
my $from = $admin;
my $iCode = substr($authcode, 0, 6);

# my $subject = qq~Now you can invite your friends to Sharebay!~;

# my $body = qq~Hi $name, I'm excited to announce a long-overdue feature - Sharebay friend invitations.

# This is the perfect way to kickstart the network in your area - or with friends anywhere!

# We've created a custom invite page for you which you can share via email, Whatsapp, Messenger or Telegram. When your friends join we'll let you know.

# Check out your custom invite and let's get more people sharing! If everyone invited just one other person, our network would double overnight! So don't be shy about asking. I've just sent out 20 to friends and family. ;)

# Colin + Sharebay Team~;

my $subject = qq~IMPORTANT: New Terms of Service and Privacy Policy for Sharebay~;

my $body = qq~Dear $name,

We're instituting a Terms Of Service and Privacy Policy effective as of March 1st, 2023. <strong>Please note: Use of our site after this date indicates your acceptance of these terms.</strong> Please review the documents below carefully to ensure that you're happy to continue using Sharebay in the future.

As you probably know, we've been trying to keep things as simple and open as possible on Sharebay. But as the site has grown - and looks set for even more growth this year - we've had to put some of our 'unspoken' rules down in writing and lay out a privacy policy - to protect users as much as ourselves from any issues that may arise from using this service.

Please read and review the following documents:
<a href="$baseURL/page?id=terms-of-service">Terms Of Service</a>
<a href="$baseURL/page?id=privacy-policy">Privacy Policy</a>

If you're happy with them, great! There's nothing else for you to do. Happy sharing!

If for some reason you aren't happy, or you need further clarification of any point, please <a href="$baseURL/page?id=contact">contact us here</a> and we'll be happy to discuss.

If for some reason you can't accept our new terms, you can close your account via the link at the bottom of your <a href="$baseURL/edit">profile editor</a>. Of course we hope you'll stay, but understand if you have to go. Please note that if you close your account, all your data will be permanently deleted and cannot be restored.

Thanks all and here's to even safer sharing!

Colin + Sharebay Team~;

my $call2act = "BROWSE POPULAR OFFERS";
my $link = $baseURL . '/?search=&filter=offers&order=popular';
my $image = '';

# SEND EMAIL
$count++ if &sendMail($to, $from, $subject, undef, $body, $call2act, $link, $image, undef);

# MARK SENT
my $markSent = $SBdb->do("UPDATE members SET mailme_sent = 1 WHERE id = '$id'");
}
}
$sth->finish;
print "$count news emails sent.\n";
}



sub sendInvitePrompt{
# PROMPT PEOPLE TO INVITE OTHERS AFTER THEY JOIN

my $count = 0;
## USE FOR TESTING
# my $sth = $SBdb->prepare("SELECT id, first_name, email, city, authcode FROM members WHERE id = 30");

## USE FOR ALL MEMBERS 2 HOURS AFTER JOINING
my $sth = $SBdb->prepare("SELECT id, first_name, email, city, authcode FROM members WHERE mailme = 1 AND activated = 1 AND badmail = 0 AND joined BETWEEN $now - 7500 AND $now - 7200");

$sth->execute;

while (my ($id, $name, $email, $city, $authcode) = $sth->fetchrow_array){

#SEND EMAIL
my $to = $email;
my $from = $admin;
my $iCode = substr($authcode, 0, 6);

my $subject = qq~Hey $name, want to invite your friends to Sharebay?~;

my $body = qq~Hi $name, we're working hard to build the world's largest sharing network and we're really glad that you're here.

If you joined and don't find much happening in $city, why not invite some of your neighbours and friends to join as well?

We've created a custom invite page just for you which you can share via email, Whatsapp, Messenger or Telegram. And when your friends join we'll let you know. Could be a great way to set up a vibrant sharing community right on your doorstep!

Check out your custom invite and let's get more people sharing! 👍

Sharebay Team~;

my $call2act = "INVITE FRIENDS";
my $link = $baseURL . '/?invite=' . $iCode;
my $image = 'https://www.sharebay.org/i/invite-a-friend.jpg';

# SEND EMAIL
$count++ if &sendMail($to, $from, $subject, undef, $body, $call2act, $link, $image, undef);

}
$sth->finish;
print "$count invite reminders sent.\n";
}




sub sendReviewReminders{

my $count = 0;

## FIND MEMBERS WITH COMPLETED TRANSACTIONS
my $sth = $SBdb->prepare("SELECT m.id, m.first_name, m.email FROM members AS m JOIN transactions AS t ON (t.giver_id = m.id OR t.getter_id = m.id) WHERE m.mailme = 1 AND m.mailme_sent = 0 AND m.activated = 1 AND m.badmail = 0 AND (t.status = 'delivered' OR t.status = 'auto-cancelled') GROUP BY m.id");

$sth->execute;

while (my ($id, $name, $email) = $sth->fetchrow_array){
# IF THEY HAVE MORE TRANSACTIONS THAN REVIEWS, REMIND THEM
	if ($SBdb->do("SELECT id FROM transactions WHERE status = 'delivered' AND (giver_id = '$id' OR getter_id = '$id')") > $SBdb->do("SELECT id FROM reviews WHERE reviewer_id = '$id'")){

#SEND EMAIL

my $to = $email;
my $from = $admin;
my $subject = qq~$name, you have reviews pending..~;

my $body = qq~Hi $name,

We noticed that you've made transactions on Sharebay and thought you might like to leave a review for the members who've helped you, or who you helped.

Reviews are a great way of building community trust, so please do take a minute to rate and leave a few words about your experience. 

Thanks a million for being a part of it!~;

my $call2act = "LEAVE REVIEWS";
my $link = $baseURL . '/reviews?a=myreviews';
my $image = $baseURL . '/i/five-stars.jpg';

# SEND EMAIL
$count++ if &sendMail($to, $from, $subject, undef, $body, $call2act, $link, $image, undef);

# MARK SENT
my $markSent = $SBdb->do("UPDATE members SET mailme_sent = 1 WHERE id = '$id'");
}
}
$sth->finish;
print "$count review reminders sent.\n";
}



sub sendCongrats{
# CONGRATULATE AND PROMPT FURTHER ACTTON TO COMPLETERS

my $count = 0;
## FIND TRANSACTIONS COMPLETED TWO HOURS AGO
my $sth = $SBdb->prepare("SELECT t.giver_id, t.getter_id, p.title, p.description, p.physical FROM transactions AS t JOIN posts AS p ON p.id = t.listing_id WHERE t.status = 'delivered' AND t.timestamp BETWEEN $now - 7500 AND $now - 7200");

# USE FOR TESTING
# my $sth = $SBdb->prepare("SELECT id, id, 'Parboiled Scotch Egg', 1, 1 FROM members WHERE id = 30");

$sth->execute;

while (my ($giver_id, $getter_id, $l_title, $l_desc, $l_physical) = $sth->fetchrow_array){
my $title = &descTitle($l_title, $l_desc);

#SEND GIVER EMAIL IF ALLOWED
if ($SBdb->do("SELECT id FROM members WHERE id = $giver_id AND mailme = 1 LIMIT 1") > 0){
my $getter_name = &getFullName($getter_id);
my $to = $giver_id;
my $from = $notify;
my $subject = qq~You are awesome!~;
my $body = qq~Thank you for sharing '$title' with $getter_name, and for helping bring more kindness and generosity into the world.

It’s acts of kindness like yours that show us that another way is possible, so thank you sincerely for that. When many of us do this, who knows what kind of world we might create!

Now, is there anything that you need? If so, don’t be afraid to reach out and ask our members by posting a request:
~;

my $call2act = "POST REQUEST";
my $link = $baseURL . '/listing?a=edit&type=request';
$link .= '&physical=yes' if $l_physical;
my $image = $baseURL . '/i/giving-balloon-02.png';

$count++ if &sendMail($to, $from, $subject, undef, $body, $call2act, $link, $image, undef);
}

#SEND GETTER EMAIL IF ALLOWED
if ($SBdb->do("SELECT id FROM members WHERE id = $getter_id AND mailme = 1 LIMIT 1") > 0){
my $giver_name = &getFullName($giver_id);
my $to = $getter_id;
my $from = $notify;
my $subject = qq~Congratulations!~;
my $body = qq~Thank you for using Sharebay and we hope that '$title' you got from $giver_name proves useful to you.

It’s acts of kindness like these that show us that another way is possible, so we thank you for being a part of that. When many of us do this, who knows what kind of world we might create!

Why not spread the love a little? Is there anything that you’d like to share with other Sharebay members? If so, why not create a post offer:
~;

my $call2act = "POST OFFER";
my $link = $baseURL . '/listing?a=edit&type=offer';
$link .= '&physical=yes' if $l_physical;
my $image = $baseURL . '/i/giving-balloon-01.png';

$count++ if &sendMail($to, $from, $subject, undef, $body, $call2act, $link, $image, undef);
}

}
$sth->finish;
print "$count congratulation emails sent.\n";
}


# Exeunt
