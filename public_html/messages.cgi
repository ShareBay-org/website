#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT IS FOR SENDING, DISPLAYING
# AND MANAGING USER MESSAGING

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );

require 'common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);

my $imgur_client_id = '6d646b286568d4d';
my $imgur_client_secret = 'e917d151b4620eaff1c27d44dc28a7ddc62d485c';

# HTTP HEADER

if (!$FORM{id} && !$a){&showAllMessages();}
if ((!$a || $a eq 'showmessage') && $FORM{id}){&showMessage($FORM{id});}


sub showAllMessages{
&bounceNonLoggedIn('Please log in to view your messages.');

my $title = 'My conversations';
my $desc = 'My conversations';
my $image = "$baseURL/i/sharebay-network-icons-no-text-flat.jpg";
my $headerInject;


my $query = qq~SELECT messages.* FROM (SELECT id, sender, recipient, convo_id, message, status, max(timestamp) AS timestamp FROM messages~;
if ($FORM{filter} eq 'unseen'){
	$query .= qq~ WHERE recipient = $myID AND status != 'seen'~;
}else{
	$query .= qq~ WHERE (sender = $myID OR recipient = $myID)~;
}
my $blocked = &getBlockedIds;
if ($blocked){
$query .= qq~ AND sender NOT IN ($blocked) AND recipient NOT IN ($blocked)~;
}
$query .= qq~ GROUP BY convo_id) AS t JOIN messages USING (convo_id, timestamp) GROUP BY convo_id, timestamp ORDER BY id DESC LIMIT 50~;
my $sth = $SBdb->prepare($query);

$sth->execute;

my ($unseen_class, $all_class);
if ($FORM{filter} eq 'unseen'){$unseen_class = 'bold'; $all_class;}else{$unseen_class; $all_class = 'bold';}

&header($title, $desc, $image, $headerInject, 'page');

print qq~<h2>My conversations</h2>
<p class="smaller"><a class="$all_class" href="$baseURL/messages">ALL</a>&nbsp;|&nbsp;<a class="$unseen_class" href="$baseURL/messages?filter=unseen">UNSEEN</a><a class="right" href="javascript:void();" onclick="markAllMessagesSeen()">Mark all as seen</a></p>~;
if ($sth->rows > 0){
while (my ($id, $sender, $recipient, $convo_id, $message, $type, $status, $timestamp) = $sth->fetchrow_array){
my $contact;
my $xClass; #FOR OPTIONAL EXTRA CLASSES
if ($sender eq $myID){$contact = $recipient; $xClass .= ' notranslate from-me';}else{$contact = $sender};
if ($status != 'seen'){$xClass .= ' bold';}
my ($contact_first_name, $contact_last_name, $imageRef, $contact_gifted, $contact_trust_score, $contact_badge_level, $contact_is_admin) = &getNameRecord($contact);
my $time = &getWhen($timestamp);
$imageRef = 'q' if !$imageRef;
use Digest::MD5 qw( md5_hex );
my $convo_color = 'hsl(' . int(substr(sprintf("%f", hex(md5_hex($convo_id))), 2, 3) * 360 / 1000) . ', 90%, 96%)';
$message =~ s!<br/>! !g;
$message =~ s/^(.{0,100}).*$/$1.../sg if length($message) > 100;
print qq~
<div class="conversation" style="background:$convo_color"><div class="chat-user-card notranslate"><a href="$baseURL/profile?id=$contact"><img src="$baseURL/user_pics/$imageRef\_t.jpg" class="chat-user-card-image" title="$contact_first_name $contact_last_name"/></a> <a href="$baseURL/profile?id=$contact">$contact_first_name $contact_last_name~;
print qq~ ($contact_gifted)~ if $contact_gifted;
&printBadge($contact_first_name, $contact_badge_level);
print qq~</a></div><div class="convo-time grey smaller">$time</div>
<div class="convo-message$xClass"><a href="messages?id=$convo_id">$message</a></div></div>~;
}
}else{
print qq~<span class="grey">No conversations yet. To start a conversation search for a user's profile on the <a href="$baseURL/search">Sharebay map</a> and send them a message.</span>~;
}

&footer();
}


sub showMessage{
&bounceNonLoggedIn('Please log in to view this message.');

my $convo_id = shift;

my $blocked = &getBlockedIds;
my $notBlocked;
if ($blocked){
$notBlocked = qq~ AND sender NOT IN ($blocked) AND recipient NOT IN ($blocked)~;
}

# GET CONTACT INFO
my $contact;
my $getContact = $SBdb->prepare("SELECT id, sender, recipient FROM messages WHERE convo_id LIKE '$convo_id%'  AND (sender = $myID OR recipient = $myID) $notBlocked ORDER BY id DESC LIMIT 1");
$getContact->execute;
if ($getContact->rows > 0){
my ($last_id, $sender, $recipient) = $getContact->fetchrow_array;
if ($sender eq $myID){$contact = $recipient}else{$contact = $sender};
my ($contact_first_name, $contact_last_name, $imageRef, $contact_stripe_image, $contact_stripe_legend, $contact_honors, $contact_HP_id) = &getNameRecord($contact);

my $title = 'Conversation with ' . $contact_first_name . ' ' . $contact_last_name;
my $desc = $title;

my $headerInject = qq~
<style>
#add_offer{
	display: none !important;
}
</style>
~;

my $footerInject = q~
<script>
scrollChat();
$('body').scrollTop(0);
markSeen('$convo_id');
$('#messageBox').focus();

var page = 1;
var loading = 0;

$('#chat-window').on('scroll', function() {
	console.log(page);
        if(($(this).scrollTop() < ($(this).innerHeight()/3)) && loading == 0) {
		loading = 1;
		$('.page-loader').removeClass('hidden');
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=getmessages&screen=' + $(document).width() + '&convo_id=' + $('#convo_id').val() + '&page=' + page,
        success: function(result) {
			$('#chat-window').prepend(result);
            $('.page-loader').addClass('hidden');
			page++;
			loading = 0;
        },
        error: function(xhr) {
			$('#chat-window').prepend('Communication error! [Details: ' + xhr.status + ' - ' + xhr.responseText + ']');
            $('.page-loader').addClass('hidden');
			loading = 0;
        }
    })
        }
    })

function update(){
    updateChat();
    setTimeout(update, 10000);
}
update();

</script>~;

&header($title, $desc, undef, $headerInject, 'chat');

&getUserCard($contact);

print qq~<div style="float:right; border-radius: 50%; background: transparent; text-align:center; color: grey;"></div><div id="chat-window">~;

print &getMessages($convo_id);

&pendingActions($contact);

print qq~</div>~;

# REPLY AND PENDING ACTIONS AREA
print qq~
<div class="chat-reply-container">
<form id="send-chat">
<input type="hidden" id="convo_id" name="convo_id" value="$convo_id"/>
<input type="hidden" id="last_id" name="last_id" value="$last_id"/>
<input type="hidden" name="a" value="sendchat"/>
<textarea class="forminput" id="messageBox" name="message" placeholder="Write message to $contact_first_name..."></textarea>
<button type="submit" class="send_button" id="send" title="SEND"><i class="fas fa-paper-plane"></i></button></form>
<p class="tiny clear">Messaging is unencrypted. Do not send private information.</p>
<div class="chat-status-message"></div>~;

print qq~</div>~;

&bareFooter($footerInject);

}else{
# NO CONVERSATION FOUND
&errorCatcher("No conversation found!");
}

}

$SBdb -> disconnect;
# Exeunt
