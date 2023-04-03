#!/usr/bin/perl
use cPanelUserConfig;

# THIS SCRIPT CONTAINS READABLE USER INFORMATION
# AND INSTRUCTIONS

# STANDARD FILE STRIPE INC SETTINGS AND SHARED VARIABLES
use strict;
use warnings;
use CGI::Carp qw( fatalsToBrowser );
require 'common.pl';
our (%FORM, $ip, $now, $salt, $admin, $notify, $newsletter, $domain, $baseURL, $siteroot, $root, $LOGGED_IN, $myID, $myName, $myImage, $myLang, $myTrans, $myLat, $myLon, $myAuth, $myModerator, $myAuthor, $myAdmin, $myJoined, $myListingCount, $a, $isModal, $SBdb, $HPdb, $maintenance, $version, $defaultImage);


my $id = $FORM{id};

if (!$id || $id eq 'about'){&showAbout();}
elsif ($id eq 'donate'){&showSupport();}
elsif ($id eq 'searches'){&showTopSearches();}
elsif ($id eq 'invited' && $myAdmin){&showInvitedMembers();}
elsif ($id eq 'tags'){&showTopTags();}
elsif ($id eq 'countries'){&showTopCountries();}
elsif ($id eq 'givers' && $myAdmin){&showTopGivers();}
elsif ($id eq 'media'){&showMedia();}
elsif ($id eq 'editor'){&editor();}
elsif ($id eq 'dump'){&dumpform();}
elsif ($id eq 'how-it-works'){&howItWorks();}
elsif ($id eq 'faqs'){&showFaqs();}
elsif ($id eq 'contact'){&showContact();}
elsif ($id eq 'stats'){&showStats();}
elsif ($id eq 'categories'){&showCategories();}
elsif ($id eq 'templates'){&showTemplates();}
elsif ($id eq 'privacy-policy'){&showPP();}
elsif ($id eq 'terms-of-service'){&showTerms();}
elsif ($id eq 'mission-statement'){&showMission();}
elsif ($id eq 'sandbox'){&sandbox();}
elsif ($id eq 'scroll'){&scrollTest();}
elsif ($id eq 'meeting'){&meeting();}


sub meeting{
&bounceNonLoggedIn;
my $title = "Meeting area";
my $desc = "Meeting area";

my $headerInject;


&header($title, $desc, undef, $headerInject, 'screen');

print qq~

<script src='https://meet.jit.si/external_api.js'></script>

<div id="videoCall" style="width:100%;height:100%;height: calc(100vh - 60px);"></div>
<script>
const callServer = 'meet.jit.si';
const options = {
    roomName: 'Sharebay_Common_Room',
    parentNode: document.querySelector('#videoCall'),
	userInfo: {
        displayName: '$myName'
    }
};
const api = new JitsiMeetExternalAPI(callServer, options);
</script>

~;

&bareFooter();
}



sub sandbox{
my $title = "Test area";
my $desc = "Code testing area";

my $headerInject;


&header($title, $desc, undef, $headerInject, 'page');



print qq~
<p id="location"></p>

    <div class="container">
    <h1>Emoji Picker Button Example</h1>
    <textarea class="text"></textarea>
    <button id="emoji-button">😀</button>
  </div>
    <script src="https://cdn.jsdelivr.net/npm/emoji-button\@0.6.0/dist/index.min.js"></script>
    <script>
      window.addEventListener('DOMContentLoaded', () => {
  EmojiButton(document.querySelector('#emoji-button'), function (emoji) {
    document.querySelector('.text').value += emoji;
  });
});
</script>

<script src='https://meet.jit.si/external_api.js'></script>

<div id="videoCall"></div>
<script>
const callServer = 'meet.jit.si';
const options = {
    roomName: 'zebedy13',
    width: '100%',
    height: '500px',
    parentNode: document.querySelector('#videoCall'),
	userInfo: {
        displayName: '$myName'
    }
};
const api = new JitsiMeetExternalAPI(callServer, options);
</script>

~;



my $footerInject = q~
<script>
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    //Get location by IP
  }

function showPosition(position) {
var lat = position.coords.latitude;
var lon = position.coords.longitude;
$('#location').html('Latitude: ' + position.coords.latitude + ', Longitude: ' + position.coords.longitude);
}
</script>

~;
&footer();
}


sub showContact{
my $title = "Got a question or idea? Get in touch!";
my $desc = "Let's talk.";

&header($title, $desc, undef, undef, 'page');
my $disabled;
my $email = '';
if ($LOGGED_IN){
	$email = &getEmail($myID);
	$disabled = 'disabled';
	}
print qq~
<h2>Got a question or idea? Get in touch!</h2>
<p>Yes, we've got real people ready to respond! We'd love to hear your thoughts, questions and ideas for making Sharebay great! We usually respond within a day.</p>~;
if ($LOGGED_IN){
print qq~<p class="smaller greyed">(Currently logged in as $myName) <a href="javascript:void(0);" class="logout">Log out?</a></p>~;
	}
print qq~
<form id="contact_form">
<input type="hidden" name="a" value="send_contact"/>
<input type="text" class="forminput $disabled" name="name" id="name" value="$myName" placeholder="Enter a name" />
<div id="name_E" class="inlineerror">! Please add your name</div>
<input type="email" class="forminput $disabled" name="email" id="email" value="$email" placeholder="Enter your email" />
<div id="email_E" class="inlineerror">! Please add a valid email address</div>
<textarea class="forminput" name="message" id="message" placeholder="What's on your mind?" rows="5"></textarea>
<div id="message_E" class="inlineerror">! Please enter a message</div>
<p class="center"><input type="submit" class="green-button" name="submit" value="Send!"/></p>
</form>
~;



&footer();
}



sub showMedia{

my $title = "Press and media kit";
my $desc = "Promotional materials and resources";

&header($title, $desc, undef, undef, 'page');
print qq~<h2>Media &amp; printables</h2>
<p>This page will soon contain a selection of resources and links to help promote Sharebay in your community.</p>~;
&footer;
}

sub showSupport{

my $title = "Support Sharebay";
my $desc = "Support Sharebay by becoming a patron today.";

&header($title, $desc, undef, undef, 'page');


my $patrons = $SBdb->do("SELECT id FROM members WHERE activated = 1 AND patronage != ''");

print qq~
<h2><i class="fas fa-award"></i> Become a Sharebay Patron!</h2>

<p>Sharebay is a 100% free service, made possible by our patrons.</p><p>Please consider joining our $patrons other patrons by donating as little as €2 per month, or making a one-off contribution to help us maintain a great service. Thank you.</p>~;
my $getPatrons = $SBdb->prepare("SELECT id, first_name, last_name, country, image FROM members WHERE activated = 1 AND patronage != ''");
$getPatrons->execute;
while(my ($id, $first_name, $last_name, $country, $image) = $getPatrons->fetchrow_array){
	print qq~<a href="$baseURL/profile?id=$id" title="$first_name $last_name, $country"><img src="$baseURL/user_pics/$image\_t.jpg" class="patron-pics"/></a>~;
}
$getPatrons->finish;
print qq~

<div id="funding-box" class="shadow">
<h2 class="center">Choose a monthly donation amount:</h2>
<div id="fund_opts" class="buttons center">
<div class="bigOnlyInline">
<input type="radio" name="amount" id="2" value="2" class="set_amount"/>
<label for="2">&euro;2</label> &nbsp;
</div>
<input type="radio" name="amount" id="5" value="5" class="set_amount" checked="checked"/>
<label for="5">&euro;5</label> &nbsp;
<input type="radio" name="amount" id="10" value="10" class="set_amount"/>
<label for="10">&euro;10</label> &nbsp;
<input type="radio" name="amount" id="25" value="25" class="set_amount"/>
<label for="25">&euro;25</label> &nbsp;
<div class="bigOnlyInline">
<input type="radio" name="amount" id="50" value="50" class="set_amount"/>
<label for="50">&euro;50</label> &nbsp;
<input type="radio" name="amount" id="100" value="100" class="set_amount"/>
<label for="100">&euro;100</label> &nbsp;
</div>
<input type="number" id="p_amount" name="p_amount" min="1" max="999" placeholder="&euro; ?"/>
</div>
<div class="clear center">
<input type="checkbox" name="p_type" id="single_pay" value="single"/>
<label for="single_pay">Just make a one-off payment</label>

<p class="center"><button id="p_submit" class="green-button">Checkout with Paypal</button></p>
</div>


<p class="center smaller">All payments are processed in Euro by Paypal.</p>
</div>~;

&footer;
}

sub showFaqs{
my $title = "Frequently Asked Questions";
my $desc = "What our members are asking about Sharebay";
my $headerInject;

&header($title, $desc, undef, $headerInject, 'page');

print qq~
<h2>Frequently asked questions</h2>

<p class="question"><a href="javascript:void(0)" onclick="toggleAns(1);" title="Click to show answer">
Is Sharebay a barter site?</a></p>
<div class="clear answer" id="ans1">
<p>No. You have no obligation to reciprocate with the person you transact with, and in fact we advise against it.</p>
<p>Sharebay uses an implicit trade system where acts are not necessarily reciprocated by the same person or to the same value. Think of it as a ‘walled community’ of sharers where favours are reciprocated over time.</p></div>

<p class="question"><a href="javascript:void(0)" onclick="toggleAns(2);" title="Click to show answer">
Do I have to offer something to be a member?</a></p>
<div class="clear answer" id="ans2">
<p>No, but you will have access to considerably more offers by offering at least one item or service. Remember, Sharebay is a community library and relies on its members to provide useful items and services for other members.</p></div>

<p class="question"><a href="javascript:void(0)" onclick="toggleAns(3);" title="Click to show answer">
But I don't have anything to offer...</a></p>
<div class="clear answer" id="ans3">
<p>Everyone has some item or service they could offer another person. It could be as basic as offering to move boxes or just lending a listening ear.</p>
<p>Check out our <a href="$baseURL/page?id=templates" title="View templates">templates page</a> for some inspiration on easy offers. You'd be surprised what you have that could be of great value to someone else.</p></div>


<p class="question"><a href="javascript:void(0)" onclick="toggleAns(4);" title="Click to show answer">
Why should I give my stuff away for free?</a></p>
<div class="clear answer" id="ans4">
<p>Sharebay provides an alternative way of doing business and getting resources outside the traditional trade model. Trade demands that you exchange like-for-like with the person you trade with - which is not always easy and can be limiting. Sharebay uses an implicit trading model, where, acts of generosity are reciprocated across the community over time instead of directly with the giver.</p></div>

<p class="question"><a href="javascript:void(0)" onclick="toggleAns(5);" title="Click to show answer">
What if someone profits from my generosity?</a></p>
<div class="clear answer" id="ans5">
<p>The majority of users on Sharebay are people who genuinely want to help. But we also have various safeguards in place to ensure that members adhere to their original registration pledge.</p>
<p>The Trust Stripes tell you how much a member contributes. Also, you can read their transaction history in the Transaction Record on their profile page. Suspicious users and listings can be reported by anyone. When numerous reports are received their data is taken down immediately.</p>
<p class="italic">We always recommend checking a member’s profile before choosing to deal with someone you don't know.</p></div>

<p class="question"><a href="javascript:void(0)" onclick="toggleAns(6);" title="Click to show answer">
What is the Transaction Record and why is it important?</a></p>
<div class="clear answer" id="ans6">
<p>Sharebay operates on reputation. Every time you complete a transaction, it gets added to the <a href="$baseURL/transactions" title="Public Transaction Record">Public Transaction Record</a>. The transaction record just shows who gave, who got, what they got and when they got it. This record is important to help users gain site reputation, and help users make informed decisions about who they deal with on the site. You can see the Public Transaction Record of a specific user by clicking on the green/red arrow scores displayed under the name in their profile or listing.</p>
<p>Every member also has a <a href="$baseURL/transactions?id=$myID" title="My transactions">private Transaction Record</a> where they can view all their current and previous transactions. (This record is only visible to you)</p></div>

<p class="question"><a href="javascript:void(0)" onclick="toggleAns(7);" title="Click to show answer">
The item I want is in another country. How can I arrange delivery?</a></p>
<div class="clear answer" id="ans7">
<p>Where collection is not possible, it is the responsibility  of the recipient to organise and pay for collection / delivery of the item. Most givers will happily package and send the item if you agree to pay the delivery costs. We recommend using Paypal to send money internationally.</p><p class="bold italic">Under no circumstances should you expect the giver to pay shipping costs.</p></div>


<p class="question"><a href="javascript:void(0)" onclick="toggleAns(8);" title="Click to show answer">
The giver has not responded to my request. What can I do?</a></p>
<div class="clear answer" id="ans8">
<p>When you request an item, we notify the giver straight away. If they don't respond, we send them up to three reminders. There is no need for you to send reminder messages. If the giver does not respond within 60 days, the transaction is automatically cancelled.</p></div>


<p class="question"><a href="javascript:void(0)" onclick="toggleAns(9);" title="Click to show answer">
I've given more than once or have many live offers. Why is my trust stripe still low?</a></p>
<div class="clear answer" id="ans9">
<p>The trust stripes are calculated using the unique number of times you gave to different members. Giving more than once to a single member only gets counted as one 'give', whereas giving to two members is counted as two gives, etc. This is to protect the community from would-be abusers.</p>
<p>For the same reason, we limit the number of trust stripe points a member can get by just listing an offer. You get one point for a live offer up to a maximum of three points for three offers. Further offers don't get counted towards your trust stripe. (Note, these restrictions only apply to your trust stripe level. Your full score of gives and offers can still be seen on your profile under the 'trust' bar)</p></div>


<p>Got a question? <a href="$baseURL/contact">Get in touch</a>.</p>~;

&generalCTA;

&footer;
}




if ($a eq 'showallnotifications'){
&bounceNonLoggedIn;
my $title = "My notifications";
my $desc = $title;
my $headerInject = q~
<script>
var page = 1;
var loading = 0;

$(document).on('scroll', function() {
	console.log($(this).scrollTop() + ' : ' + $(this).innerHeight()/8);
        if(($(this).scrollTop() > ($(this).innerHeight()/8)) && loading == 0) {
		loading = 1;
		$('.page-loader').removeClass('hidden');
	    $.ajax({
        url: baseURL + '/ajax.cgi?a=getnotifications&page=' + page,
        success: function(result) {
			$('#notifications_page').append(result);
            $('.page-loader').addClass('hidden');
			page++;
			loading = 0;
        },
        error: function(xhr) {
			$('#notifications_page').append('Communication error! [Details: ' + xhr.status + ' - ' + xhr.responseText + ']');
            $('.page-loader').addClass('hidden');
			loading = 0;
        }
    })
        }
    })
</script>
~;

&header($title, $desc, undef, $headerInject, 'page');
print qq~<h2>My notifications</h2><div id="notifications_page">~;
print &getNotifications;
print qq~</div>~;
&footer;
}


sub showAbout{

my $title = "Sharebay is a free, community library of anything";
my $desc = "Sharebay is a free, community library of anything, where members can share goods, knowledge and talents freely with other members.";
my $headerInject;

&header($title, $desc, "$baseURL/i/freeworlder-network-icons-no-text-flat.jpg", $headerInject, 'page');

print qq~

<h2>About us</h2>
<!-- div class="videoWrapper">
<iframe width="560" height="315" src="https://www.youtube.com/embed/-V15S7vLDNE?rel=0&amp;controls=0&amp;showinfo=0wmode=transparent" frameborder="0"  allowfullscreen></iframe>
</div -->

<img src="$baseURL/i/freeworlder-network-icons-no-text-flat.jpg" class="full-width-image">

<p>Sharebay is a global gifting network where members can share their goods, skills and knowledge freely with other members. You could think of it like Ebay or Fiverr&mdash;but without the money part!</p>

<p>We&apos;re on a mission to see how far humans can go on generosity alone. All registered members are free to give and take as much as they can from the network.</p>
<p>Founded on the principles of an <a href="https://openaccesseconomy.org" target="_blank" rel="noopener">Open Access Economy</a>, we want to show that a global community based on sharing goods and services can thrive, help reduce our planetary consumption, and maybe some day challenge the very notion of trade itself.</p>

<p>Sharebay was launched in 2017 and already has many thousands of members worldwide sharing their goods and services. It was founded and is currently maintained by Irish author <a href="$baseURL/profile?id=30">Colin R. Turner</a>.</p>~;

&generalCTA;

&showSocial('about', 1);

&footer;
}


sub showPP{

my $title = "Privacy Policy";
my $desc = "How Sharebay collects and uses your data";

&header($title, $desc, undef, undef, 'page');

print qq~
<h1>$title</h1>
<p>Here's how we use your data:</p>
<p>Firstly, be aware that most information you add to your personal profile or listings is publicly visible on our site and will most likely be indexed by search engines such as Google, Bing, etc. We strongly recommend that you don't post any private or sensitive information on your profile or in your listings. The only exceptions are email address, street address, postcode and telephone number which are always private;</p>
<p>We collect data on how you use the site via cookies and session login to help match you with more of the things you're interested in. This usage data is never shared with any third party;</p>
<p>Sharebay doesn't host advertising or any other third party tracking software, however our site uses Google Analytics and Google Maps. Google may collect data from you via these APIs according to their <a href="https://cloud.google.com/maps-platform/terms">privacy policy</a>;</p>
<p>We may syndicate or advertise Sharebay listings on other networks. This shared data is limited to listings only. We do not share any contact or personally-identifying information with third parties, with the exception of HonorPay.org (see below);</p>
<p>HonorPay.org is a site affiliated with Sharebay.org that resides on our servers and administers the Honor awards system. On registering, you are given the choice to opt-in to HonorPay.org as well. If you opt-in, we will share your name, location, email and log-in password once with HonorPay.org via a secure, internal database link, so that you can log in to HonorPay.org separately. If you don't opt-in, no data is shared with HonorPay;</p>
<h2>Data handling and destruction</h2>
<p>All user data is stored on a secure database server hosted by our partners <a href="https://wildhost.co.uk">wildhost.co.uk</a>. In the unlikely event of a data breach, we will contact all our members within three days to inform them of the breach, what data was exposed and what steps they can take to secure their information;</p>
<p>If you choose to delete your Sharebay account, all data, including your image, personal information, site preferences, browsing history, listings and listing images are permanently deleted and cannot be restored. You can delete your account using the link at the bottom of your 'Edit Profile &amp; Settings' page. You don't need to contact us to remove your data, but you can optionally email us at <a href="mailto:hello\@sharebay.org">hello\@sharebay.org</a>&nbsp;requesting same using the same email address you use to log in to Sharebay.</p>
<p>We keep backups of all user data on our secure servers, so it may take up to 30 days for your data to be completely removed from all our systems. Please also note that any indexing of your data by search engines like Google or Bing may take time to be refreshed. Even though we provide daily sitemaps, we can't ultimately control what data they keep and when it's deleted. As a general rule, it may take 2-3 weeks for search engines to update their index of our site.</p>
<p>If you choose to opt-out of HonorPay, you can do so via your 'Edit Profile &amp; Settings' page by unchecking the 'Connect to HonorPay' box. This will disconnect HonorPay from Sharebay, but will not delete your HonorPay account. To delete your HonorPay account, log in to HonorPay separately and select 'delete account' from your profile settings. Your data is then permanently removed.</p>
<p>All our data policies are GDPR compliant.</p>
<p>Use of Sharebay is subject to our <a href="$baseURL/page?id=terms-of-service">terms of service</a>.</p>

<h2>More information</h2>
<p>If you would like more information on how to use this service, please check out our <a href="https://www.sharebay.org/how-it-works">How It Works</a> page, check our <a href="https://www.sharebay.org/faqs">FAQs</a>, or email your query to&nbsp;<a href="mailto:hello\@sharebay.org">hello\@sharebay.org</a>.</p>
<p class="smaller grey">Updated: 2022-12-16</p>~;

&footer;
}


sub showTerms{

my $title = "Terms of Service";
my $desc = "House rules and terms of service for using Sharebay";

&header($title, $desc, undef, undef, 'page');

print qq~
<h1>$title</h1>
<p>Sharebay's mission is to connect people who would like to share goods, services and knowledge freely with each other. To do this effectively, we have a few house rules and some required legal disclaimer stuff:</p>

<h2>House rules</h2>
<p class="bold">Rule #1: Be kind or leave.</p>
<p class="bold">Rule #2: Share things freely with others as much as you can.</p>
<p class="bold">Rule #3: No selling, no scams, no spam, no porn, no illegal activity.</p>
<p class="bold">Rule #4: No spectators. Get involved by posting an offer or request.</p>
<p class="bold">Rule #5: Don't exhaust yourself helping others. Be kind to you too.</p>
<p class="helper">In general, we extend an open policy to all members, but, due to the precarious nature of free giving in a competitive world, we also exercise zero tolerance of any member who seeks to break trust and abuse others' generosity. Offending profiles and listings will be removed without notice.</p>
<p></p>
<hr/>
<h2>Legal stuff</h2>
<p>1. Sharebay.org does not guarantee the quality of any goods, services, transactions or relationships that arise from using our service. Though we employ basic checks to ensure high quality listings, members avail of offers and services from other members entirely at their own risk;</p>
<p>2. Sharebay.org is not liable for any breakages, accidents, injuries, or criminal activity that may arise as a result of using our service;</p>
<p>3. Sharebay.org uses a SafePay system where requesting members can pay for item shipping once a shipping cost has been agreed by both parties. Sharebay.org acts as intermediary to this transaction and retains the requester's payment until the item has been confirmed as delivered. Once delivery is confirmed the shipping payment is then disbursed to the sender. Sharebay.org charges the requester a fee of 4\% + &euro;1 to cover admin and card processing costs. If any issues arise with shipping payment or delivery, Sharebay will investigate the issues. Members who participate in the SafePay scheme agree to use the service in good faith and help us expedite any investigation for a speedy resolution;</p>
<p>4. Sharebay.org does not employ or endorse any third party shipping service to deliver goods. Members must arrange their own shipping and do so at their own risk;</p>
<p>5. We reserve the right to remove inappropriate content without notice. We do not tolerate abuse of our service. Profiles and listings that promote hate, violence, or are created for the purposes of stealing, money-laundering, scams, attacking our servers, identity theft or providing other dangerously misleading information will be removed without notice;</p>
<p>6. We endeavour to provide a high quality, free service to help match people's wants and needs. If for any reason we need to withdraw or close the service, we will provide 30 days notice to all members.</p>
<p>7. All data is stored according to our <a href="$baseURL/page?id=privacy-policy">privacy policy</a>.</p>

<h2>More information</h2>
<p>If you would like more information on how to use this service, please check out our <a href="https://www.sharebay.org/how-it-works">How It Works</a> page, check our <a href="https://www.sharebay.org/faqs">FAQs</a>, or email your query to&nbsp;<a href="mailto:hello\@sharebay.org">hello\@sharebay.org</a>.</p>
<p class="smaller grey">Updated: 2022-12-16</p>~;

&footer;
}



sub showMission{

my $title = "Our Mission Statement";
my $desc = "Why we do what we do";

&header($title, $desc, undef, undef, 'page');

print qq~
<h1>$title</h1>
<p>We believe that humans are kind and generous by nature, and thrive on the joy of giving and receiving. However, too often our kindness goes unrewarded in a society that demands only trade or payment. We want to push the envelope of generosity and help expand the range of human possibilities through acts of sharing.</p>
<p>We aim to provide a safe space where people can share their resources and talents freely, without fear of lack or of malicious intent. Sharebay is a place of mutual trust where everyone gives a little, gets a lot, and meets others who share in its gifting principle.</p>
<p>By tapping into the power of the collective, we hope to make the world a kinder place and to do our part to tackle global inequality by offering alternative ways for people to access vital goods and services within their community and beyond.</p>
<p>In doing so, we also aim to mitigate environmental damage and promote sustainable practices through the reduction of production and waste made possible through the sharing and lending of physical goods, while also maintaining a minimal environmental footprint in our business activities.</p>
<p>Also, we aim to connect everyone who shares our goals.</p>

<h2>More information</h2>
<p>If you would like more information on how to use this service, please check out our <a href="https://www.sharebay.org/how-it-works">How It Works</a> page, check our <a href="https://www.sharebay.org/faqs">FAQs</a>, or email your query to&nbsp;<a href="mailto:hello\@sharebay.org">hello\@sharebay.org</a>.</p>
<p class="smaller grey">Updated: 2023-01-25</p>~;

&footer;
}


sub showInvitedMembers{

my $title = "Members invited on Sharebay";
my $desc = "Who invited who on Sharebay";
my $headerInject;
&header($title, $desc, undef, $headerInject, 'page');

my $sth = $SBdb->prepare("SELECT id, first_name, last_name, invited_by FROM members WHERE invited_by != '' AND activated = 1 ORDER BY id DESC LIMIT 100");

$sth->execute;

print qq~<h2>Latest invited members</h2>
<div class="cat_columns"><ol>~;

while(my ($id, $first_name, $last_name, $invited_by) = $sth->fetchrow_array){
my $getInviter = $SBdb->prepare("SELECT id, first_name, last_name FROM members WHERE authcode LIKE '$invited_by%' LIMIT 1");
$getInviter->execute;
my ($i_id, $i_first_name, $i_last_name) = $getInviter->fetchrow_array;
$getInviter->finish;

print qq~<li><a href="$baseURL/profile?id=$id" title="$first_name $last_name" rel="nofollow">$first_name $last_name</a> was invited by <a href="$baseURL/profile?id=$i_id" title="$i_first_name $i_last_name" rel="nofollow">$i_first_name $i_last_name</a></li>~;
}
print qq~</ol></div>~;
&footer;
}


sub showTopSearches{

my $title = "Top searches on Sharebay";
my $desc = "What people are searching for on Sharebay";
my $headerInject;
&header($title, $desc, undef, $headerInject, 'page');

my $sth = $SBdb->prepare("SELECT query, COUNT(DISTINCT user_id) as num FROM searches GROUP BY query HAVING num > 1 ORDER by num DESC, query LIMIT 100");

$sth->execute;

print qq~<h2>Most searched items on Sharebay</h2>
<div class="cat_columns"><ol>~;

while(my ($query, $num) = $sth->fetchrow_array){
print qq~<li><a href="$baseURL/?search=$query" title="Search for &apos;$query&apos;" rel="nofollow">$query~; if ($myAdmin || $myModerator){print qq~ ($num)~;} print qq~</a></li>~;
# print qq~$query ($num)<br/>~;
}
print qq~</ol></div>~;
&footer;
}


sub showTopGivers{

my $title = "Top givers on Sharebay";
my $desc = "Most generous givers on Sharebay";
my $headerInject;
&header($title, $desc, undef, $headerInject, 'page');

my $sth = $SBdb->prepare("SELECT m.id, m.first_name, m.last_name, COUNT(t.id) AS num FROM members AS m JOIN transactions AS t ON t.giver_id = m.id WHERE t.status = 'delivered' GROUP BY t.giver_id ORDER by num DESC LIMIT 100");

$sth->execute;

print qq~<h2>Most giving members on Sharebay</h2>
<div class="cat_columns"><ol>~;

while(my ($profile_id, $first_name, $last_name, $num) = $sth->fetchrow_array){
print qq~<li><a href="$baseURL/profile?id=$profile_id" title="$first_name $last_name" rel="nofollow">$first_name $last_name ($num)</a></li>~;
}
print qq~</ol></div>~;
&footer;
}



sub showTopTags{

my $title = "Most used tags on Sharebay";
my $desc = "Most popular tags on Sharebay";
my $headerInject;
&header($title, $desc, undef, $headerInject, 'page');

my $sth = $SBdb->prepare("SELECT tag, used FROM dictionary ORDER BY used DESC LIMIT 100");

$sth->execute;

print qq~<h2>Top 100 tags on Sharebay</h2>
<div class="cat_columns"><ol>~;

while(my ($tag, $num) = $sth->fetchrow_array){
print qq~<li><a href="$baseURL/?search=$tag" title="Search for &apos;$tag&apos;" rel="nofollow">$tag ($num)</a></li>~;
}
print qq~</ol></div>~;
&footer;
}



sub showTopCountries{

my $title = "Top member countries represented";
my $desc = "Top member countries represented";
my $headerInject;
&header($title, $desc, undef, $headerInject, 'page');

my $total_members = $SBdb->do("SELECT id FROM members WHERE activated = 1");
my $sth = $SBdb->prepare("SELECT country, COUNT(id) AS used FROM members WHERE activated = 1 GROUP BY country_iso ORDER BY used DESC LIMIT 100");

$sth->execute;

print qq~<h2>Top 100 member countries on Sharebay</h2>
<div class="cat_columns"><ol>~;

while(my ($tag, $num) = $sth->fetchrow_array){
my $percent = sprintf("%.1f", ($num / $total_members) * 100);
print qq~<li><a href="$baseURL/?search=$tag" title="Search for &apos;$tag&apos;" rel="nofollow">$tag ($num / $percent\%)</a></li>~;
}
print qq~</ol></div>~;
&footer;
}


sub showCategories{
my $title = 'Browse Sharebay Categories';
my $desc = 'The complete list of Sharebay categories';
my $headerInject;

my $orderBy = qq~ORDER by c.category~;
if ($FORM{order} eq 'popular'){$orderBy = qq~ORDER by num_listings DESC~;}
if ($FORM{order} eq 'id'){$orderBy = qq~ORDER by c.id ASC~;}

my $categories = $SBdb->prepare("SELECT c.id, c.category, IFNULL(SUM(CASE WHEN c.id = p.category AND p.status = 'live' THEN 1 END), 0) AS num_listings FROM categories AS c LEFT JOIN posts AS p ON c.id = p.category GROUP by c.category $orderBy");


$categories->execute;

&header($title, $desc, undef, $headerInject, 'page');
print qq~<h2>$title</h2>
<div class="cat_columns">~;
while (my($cat_id, $category, $listings) = $categories->fetchrow_array){
	print qq~<p><a href="$baseURL/?search&filter=cat_$cat_id" title="Browse $category listings"><img src="$baseURL/category_pics/cat$cat_id\_t.jpg" class="tiny-icon" alt="$category" /></a>&nbsp;<a href="$baseURL/?search&filter=cat_$cat_id" title="Browse $category listings">$category ($listings)</a></p>~;
}
print qq~</div>~;
&footer;
$categories->finish;
}



sub showTemplates{
my $title = 'Offer templates';
my $desc = qq~Not sure what to offer? Here's some suggestions for commonly shared goods and services to get you started.~;
my $headerInject;

my $interests = &getInterests();

my $resultsPP = 10;
my $sth;
if ($interests){
$sth= "SELECT id, title, description, tags, category, MATCH (title, description, tags) AGAINST ('$interests') AS rank FROM listing_templates ORDER BY rank DESC, uses DESC";
}else{
$sth = "SELECT id, title, description, tags, category, 0 AS rank FROM listing_templates ORDER BY uses DESC, title"
}
my $num_results = $SBdb->do($sth);
if ($num_results < 1){$num_results = 0;}
$sth .= qq~ LIMIT $resultsPP~;

my $start = $FORM{start} || 0;
$sth .= qq~ OFFSET $start~;
my $prevURL = qq~page?id=templates&start=~ . ($start - $resultsPP);
my $nextURL = qq~page?id=templates&start=~ . ($start + $resultsPP);

my $templates = $SBdb->prepare($sth);
$templates->execute;

&header($title, $desc, undef, $headerInject, 'page');
print qq~<h2>$title</h2>
<p>$desc</p>~;
while (my($id, $title, $description, $tags, $category, $rank) = $templates->fetchrow_array){
	print qq~<a class="template" href="$baseURL/listing?a=edit&from_template=$id" title="Offer $title"><img src="$baseURL/category_pics/cat$category\_t.jpg" class="medium-icon" alt="$title" />&nbsp;&nbsp;$title<span class="bigOnlyInline"> / $description</span></a>~;
}

if ($num_results > $resultsPP){
print qq~
<p class="center clear top20">
<a class="nav-button~; if ($start <= 0){print qq~ disabled~;} print qq~" href="$prevURL" title="Previous page"><i class="fas fa-chevron-circle-left fa-3x"></i></a>&nbsp;&nbsp;
<a class="nav-button~; if (($start + $resultsPP) >= $num_results){print qq~ disabled~;} print qq~" href="$nextURL" title="Next page"><i class="fas fa-chevron-circle-right fa-3x"></i></a>
</p>~;
}

&footer;
$templates->finish;
}


sub editor{
	
my $title = 'Write text';
my $desc = 'Write something cool';
my $headerInject = qq~<script type="text/javascript" src="$baseURL/js/nicEdit.js?v=$version"></script> <script type="text/javascript">
//<![CDATA[
	bkLib.onDomLoaded(function() { nicEditors.allTextAreas();
	\$('.nicEdit-panelContain').parent().width('102%');
	\$('.nicEdit-panelContain').parent().next().width('100%');
	\$('.nicEdit-panelContain').parent().next().css('background-color' , 'white');
	\$('.nicEdit-main').width('98%');
	});  
  //]]>
  </script>~;
&header($title, $desc, undef, $headerInject, 'page');
 print qq~ 
  <form method="post" action="about" class="notranslate" style="Width:100%;">
  <input type="hidden" name="a" value="dump"/>
    <textarea id="mytextarea" name="text" class="notranslate"></textarea>
    <input type="submit" name="submit"/>
  </form>~;
  
&footer;
	
}


sub dumpform{
	my $title = 'Result';
	my $desc = 'A description of same';
	my $headerInject;
&header($title, $desc, undef, $headerInject, 'page');
print qq~$FORM{text}~;
&footer;
}

sub howItWorks{

my $title = "How It Works";
my $desc = "Find out how to get the most out of the world's fastest growing sharing library";
my $image = $baseURL . '/i/giving-balloon-OG-image.png'; 

&header($title, $desc, $image, undef, 'page');
print qq~

<h1>How it works</h1>
<p>Sharebay is a completely free, goods and services sharing network.</p>
<div class="clearfix">
<div class="half center"><img src="$baseURL/i/giving-balloon-01.svg" style="width:100%;"/>
</div>
<div class="half center"><img src="$baseURL/i/giving-balloon-02.svg" style="width:100%;"/>
</div>
</div>

<p>Avail of thousands of free goods and services offered by members all over the world and offer yours too.</p>
<hr class="spacer"/>

<h2>Free to use, and always will be</h2>
<div class="clearfix">
<div class="half center"><img src="$baseURL/i/flying-dove2.svg" style="width:80%;margin: 0 auto;"/><p>We don&rsquo;t advertise, we don&rsquo;t track you. There&rsquo;s no catch&mdash;just a community of thoughtful people who believe that sharing goods and services is good for you, and good for the world.</p></div>
<div class="half round green-white"><p>How Sharebay is good for the world:</p>
<ul>
<li aria-level="1">Reduces waste and encourages reuse of resources</li>
<li aria-level="1">Promotes collaboration and sharing</li>
<li aria-level="1">Builds connection and trust in local areas and around the world</li>
<li aria-level="1">Helps organise community programs</li>
<li aria-level="1">Helps you meet like-minded people in your area</li>
<li aria-level="1">Helps organise meetups, find friends and more with our map and member searching system</li>
<li aria-level="1">Supports an Open Access Economy. Find out more <a href="https://openaccesseconomy.org/doku.php">here</a>.</li>
</ul></div></div>
<hr class="spacer"/>

<h2>Getting started</h2>
<div class="clearfix">
<div class="half">
<p>To get started, just<a href="https://www.sharebay.org/join"> create your account</a>, make an <a href="https://www.sharebay.org/post">offer listing</a> and start sharing free goods and services with other members. That's it!</p>
<p>For best results, add as much information about yourself as you can, so we can better match you with things you might be interested in.</p>
</div>
<div class="half center">
<img src="$baseURL/i/rocket.svg" style="width:80%;margin: 0 auto;"/>
</div></div>
<hr class="spacer"/>

<h2>What to offer</h2>
<div class="clearfix">
<div class="half center">
<img src="$baseURL/i/gift-box.svg" style="width:80%;margin: 0 auto;"/>
<p>You can offer anything on Sharebay as long as it is genuinely free, legal and yours to give. Please just respect our Do's and Don'ts guidelines &#8594;</p>
<p>You can also request an <a href="https://www.sharebay.org/listing?a=edit&amp;type=request&amp;physical=yes">item</a> or <a href="https://www.sharebay.org/listing?a=edit&amp;type=request&amp;physical=">service</a> that another member might be able to help you with.</p>
</div>
<div class="half round green-white">
<h4>Do:</h4>
<ul>
<li aria-level="1">Do offer complete, working items</li>
<li aria-level="1">Do offer services that you can provide to a reasonable standard</li>
<li aria-level="1">Be courteous and give timely responses to queries</li>
</ul>
<h4>Don&rsquo;t:</h4>
<ul>
<li aria-level="1">Don't offer faulty or incomplete items unless issues or missing parts are clearly stated</li>
<li aria-level="1">Don't offer items or services that may be illegal in yours or the recipient&rsquo;s country</li>
<li aria-level="1">Don't use Sharebay to advertise paid products or services &dagger;</li>
<li aria-level="1">Don't offer items or services that may cause offence or bring Sharebay.org into disrepute *</li>
</ul>
</div>
</div>
<p></p>
<p class="helper">If you&rsquo;re not sure what to offer, check out our <a href="https://www.sharebay.org/page?id=templates">listing templates</a> for some commonly offered items and services.</p>

<p class="smaller">&dagger; You may post offers that promote a paid product as long as the item on offer is fully free.<br/>
* Offers that do meet these criteria will be removed, and members may be banned from the site.</p>
<hr class="spacer"/>

<div class="hidden">
<h2 id="trust-system">The Trust System</h2>
<div class="clearfix">
<div class="half center">
<img src="$baseURL/i/stripe_3.svg" style="width:80%;margin: 0 auto;"/>
<p>Sharebay uses a three level &lsquo;stripe&rsquo; system that denotes the overall trust and giving activity of a member. </p>
</div>
<div class="half round green-white">
<p>These Trust Levels are as follows:</p>
<p><img src="$baseURL/i/stripe_1.svg" class="badge" alt="Trust badge"/> Contributing Member (has at least one live offer listed)</p>
<p><img src="$baseURL/i/stripe_2.svg" class="badge" alt="Trust badge"/> Active Contributor (has given at least once)</p>
<p><img src="$baseURL/i/stripe_3.svg" class="badge" alt="Trust badge"/> Prolific Contributor (has given to at least three other members)</p>
<p><img src="$baseURL/i/stripe_0.svg" class="badge" alt="Trust badge"/> Denotes a member who hasn&rsquo;t yet listed or completed an offer</p>
</div></div>
<p>Trust Stripes are awarded daily based on the total number of offers and completed transactions a member has made using this simple point system:</p>
<ul>
<li aria-level="1">1 point for every offer listed *</li>
<li aria-level="1">4 points for every offer completed</li>
</ul>
<p class="helper">Higher Stripe Members can choose to limit access to their offers based on a respondent's Trust Score. This acts as a safeguard for those who may prefer to offer higher value items.</p>
<p class="smaller">* Up to a maximum of 3 points. Offers must be live. Request listings are not counted, however fulfilling another member&rsquo;s request is counted as a completed offer</p>
<hr class="spacer"/>
</div>

<h2>The Transaction Record</h2>
<div class="clearfix">
<div class="half">
<p>Sharebay logs every transaction that happens. This transaction record is<a href="https://www.sharebay.org/transactions"> public</a> and helps to ensure transparency and trust on the site. Each completed transaction is recorded as a &lsquo;gave&rsquo; and &lsquo;got&rsquo; score to giver and receiver respectively. These totals are displayed in every member&rsquo;s profile page, along with a link to view their site transactions.</p>
<p>The Trust Score, Transaction Record and offer counters help you make an informed choice about who you want to share or have contact with.</p>
</div>
<div class="half center">
<img src="$baseURL/i/spreadsheet.svg" style="width:100%;margin: 0 auto;"/>
</div></div>
<p>The transaction system works like this:</p>
<table class="explainer-table">
<tbody>
<tr>
<td>You request a member&rsquo;s offer</td>
<td>&#9658;</td>
<td>They are notified and a pending transaction is created</td>
</tr>
<tr>
<td>They agree to fulfill offer</td>
<td>&#9658;</td>
<td>You are notified and transaction is updated</td>
</tr>
<tr>
<td>You confirm delivery of item or service</td>
<td>&#9658;</td>
<td>They are notified and a completed transaction is registered</td>
</tr>
</tbody>
</table>
<p>In the case of responding to a request, it&rsquo;s slightly different:</p>
<table class="explainer-table">
<tbody>
<tr>
<td>You offer to fulfill request</td>
<td>&#9658;</td>
<td>They are notified and a pending transaction is created</td>
</tr>
<tr>
<td>They agree for you to fulfill request</td>
<td>&#9658;</td>
<td>You are notified and transaction is updated</td>
</tr>
<tr>
<td>You fulfill request</td>
<td>&#9658;</td>
<td>They are notified and transaction is updated</td>
</tr>
<tr>
<td>They confirm delivery</td>
<td>&#9658;</td>
<td>You are notified and a completed transaction is registered</td>
</tr>
</tbody>
</table>
<p></p>
<p class="helper">A pending transaction can be cancelled at any time by either member.</p>
<hr class="spacer"/>

<h2>HonorPay</h2>
<div class="clearfix">
<div class="half center">
<img src="https://honorpay.org/i/honor.png" style="width: 90%; margin: 0 auto;" alt="HonorPay"/>
</div>
<div class="half">
<p>Sharebay uses HonorPay - an independent award app that allows you to send virtual awards to show your gratitude and appreciation to any other member.&nbsp;</p>
<p>When you register for Sharebay, you have the option to create a linked HonorPay account as well. HonorPay is a free service and you can log in using the same email and password as for Sharebay. Find out more about HonorPay<a href="https://honorpay.org/how-it-works"> here</a>.</p>
<p>A member's Honor score is displayed beside their name. If you are especially pleased with a transaction, you can award the member an Honor via their profile page.</p>
</div></div>
<hr class="spacer"/>

<h2><img src="$baseURL/i/warning.svg" style="height:1.5em;vertical-align: -0.3em"/> Member safety </h2>
<p>There are a number of measures that we use to make our site as safe as possible for members:</p>
<ul>
<li aria-level="1">Spam or offensive content reporting. Every listing has a link at the bottom to report it anonymously and safely. Our site actively follows up reports and removes inappropriate content.</li>
<li aria-level="1">Profile reporting. You can report another member who behaves inappropriately or who is abusing the site using the link at the bottom of their profile. Reports are anonymous and all are followed up.</li>
<li aria-level="1">Member blocking. If you no longer wish to hear from or see content from a member, you can block them using the link below a member&rsquo;s profile. When you block a member, neither of you will be able to send messages or view each other&rsquo;s content.</li>
</ul>
<p style="padding-left: 30px;"><em>NB When arranging to meet other members to collaborate or exchange goods, be sensible at all times. Arrange to meet in a public place, or bring someone with you. Never meet someone you don&rsquo;t know alone in a strange place.</em></p>
<hr class="spacer"/>

<h2>Automatic translations</h2>
<div class="clearfix">
<div class="half">
<p>Because Sharebay is an international site, we have added optional automatic translations by Google. To set up translation, just set your preferred language and enable automatic translations in your<a href="https://www.sharebay.org/edit"> Edit profile &amp; settings</a> page.</p>
<p>Note: Accuracy of translations vary according to language.</p>
</div>
<div class="half center">
<img src="$baseURL/i/translation-world.svg" style="width:80%;margin: 0 auto;"/>
</div>
</div>
<hr class="spacer"/>
<p class="center"><a class="grey tiny" href="https://openclipart.org">Graphics from OpenClipArt.org</a></p>
~;

&generalCTA;

&showSocial('how-it-works', 1);

&footer;
}



sub showStats{
my $title = "Sharebay Statistics";
my $desc = "Basic member statistics at a glance";
my $noMembers = $SBdb->do("SELECT id FROM members WHERE activated = 1");
my $noListings = $SBdb->do("SELECT id FROM posts WHERE status = 'live'");
my $noOffers = $SBdb->do("SELECT id FROM posts WHERE status = 'live' AND type = 'offer'");
my $noOfferItems = $SBdb->do("SELECT id FROM posts WHERE status = 'live' AND type = 'offer' AND physical = 1");
my $noOfferSkills = $SBdb->do("SELECT id FROM posts WHERE status = 'live' AND type = 'offer' AND physical = 0");
my $noRequests = $SBdb->do("SELECT id FROM posts WHERE status = 'live' AND type = 'request'");
my $noRequestItems = $SBdb->do("SELECT id FROM posts WHERE status = 'live' AND type = 'request' AND physical = 1");
my $noRequestSkills = $SBdb->do("SELECT id FROM posts WHERE status = 'live' AND type = 'request' AND physical = 0");

&header($title, $desc, undef, undef, 'page');

print qq~<H1>Site Statistics</H1>
<table class="stat-table">
<tr>
<td class="left bold">Total members:</td>
<td class="right">$noMembers</td>
</tr>~;

if ($myAdmin || $myModerator){
	
my $getData = $SBdb->prepare("SELECT DATE_FORMAT(FROM_UNIXTIME(timestamp), '%Y-%m-%d'), total_members, new_members, active_members, total_listings, new_listings, total_views, listing_views, profile_views, likes, comments, transactions FROM snapshot WHERE timestamp BETWEEN ($now - (86400*180)) AND $now");
$getData->execute;

my $dates;
my $total_members;
my $new_members;
my $active_members;
my $total_listings;
my $new_listings;
my $total_views;
my $listing_views;
my $profile_views;
my $likes;
my $comments;
my $actions;

while (my ($date, $total_member, $new_member, $active_member, $total_listing, $new_listing, $total_view, $listing_view, $profile_view, $like, $comment, $action) = $getData->fetchrow_array){
	$dates .= '"' . $date . '",';
	$total_members .= $total_member . ',';
	$new_members .= $new_member . ',';
	$active_members .= $active_member . ',';
	$total_listings .= $total_listing . ',';
	$new_listings .= $new_listing . ',';
	$total_views .= $total_view . ',';
	$listing_views .= $listing_view . ',';
	$profile_views .= $profile_view . ',';
	$likes .= $like . ',';
	$comments .= $comment . ',';
	$actions .= $action . ',';
}
print qq~


<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<p class="helper">This page updates once every 24 hours.</p>
<h2>Member growth</h2>
<div>
  <canvas id="memberChart"></canvas>
</div>

<h2>Listings growth</h2>
<div>
  <canvas id="listingsChart"></canvas>
</div>

<h2>Interactions</h2>

<div>
  <canvas id="socialChart"></canvas>
</div>
<h2>Total page views</h2>

<div>
  <canvas id="totalViewsChart"></canvas>
</div>

<script>
  const labels = [
$dates
  ];

  const social_data = {
    labels: labels,
    datasets: [{
      label: 'Active Members',
      backgroundColor: 'rgb(100, 30, 220)',
      borderColor: 'rgb(100, 30, 220)',
      data: [$active_members],
    },{
      label: 'Listing Views',
      backgroundColor: 'rgb(150, 0, 132)',
      borderColor: 'rgb(150, 0, 132)',
      data: [$listing_views],
	  hidden: true,
	},{
      label: 'Profile Views',
      backgroundColor: 'rgb(150, 150, 132)',
      borderColor: 'rgb(150, 150, 132)',
      data: [$profile_views],
	  hidden: true,
	},{
      label: 'Likes',
      backgroundColor: 'rgb(255, 99, 132)',
      borderColor: 'rgb(255, 99, 132)',
      data: [$likes],
	  hidden: true,
    },{
      label: 'Comments',
      backgroundColor: 'rgb(0, 0, 132)',
      borderColor: 'rgb(0, 0, 132)',
      data: [$comments],
	  hidden: true,
	},{
      label: 'Actions',
      backgroundColor: 'rgb(0, 180, 0)',
      borderColor: 'rgb(0, 180, 0)',
      data: [$actions],
	  hidden: true,
	}
	]
  };

  const social_data_config = {
    type: 'line',
    data: social_data,
    options: {}
  };
  
  const social_chart = new Chart(
    document.getElementById('socialChart'),
    social_data_config
  );
  
  
  const member_data = {
    labels: labels,
    datasets: [{
      label: 'Total members',
      backgroundColor: 'rgb(150, 0, 132)',
      borderColor: 'rgb(150, 0, 132)',
      data: [$total_members],
	},{
      label: 'New members',
      backgroundColor: 'rgb(0, 180, 80)',
      borderColor: 'rgb(0, 180, 80)',
      data: [$new_members],
	  hidden: true,
	}
	]
  };
  const member_data_config = {
    type: 'line',
    data: member_data,
    options: {}
  };
  const member_chart = new Chart(
    document.getElementById('memberChart'),
    member_data_config
  );
  
  
  const listings_data = {
    labels: labels,
    datasets: [{
      label: 'Total listings',
      backgroundColor: 'rgb(150, 0, 132)',
      borderColor: 'rgb(150, 0, 132)',
      data: [$total_listings],
	},{
      label: 'New listings',
      backgroundColor: 'rgb(0, 180, 80)',
      borderColor: 'rgb(0, 180, 80)',
      data: [$new_listings],
	  hidden: true,
	}
	]
  };
  const listings_data_config = {
    type: 'line',
    data: listings_data,
    options: {}
  };
  const listings_chart = new Chart(
    document.getElementById('listingsChart'),
    listings_data_config
  );

 
  const total_views_data = {
    labels: labels,
    datasets: [{
      label: 'Total page views',
      backgroundColor: 'rgb(220, 0, 0)',
      borderColor: 'rgb(220, 0, 0)',
      data: [$total_views],
	}
	]
  };
  const total_views_data_config = {
    type: 'line',
    data: total_views_data,
    options: {}
  };
  
  const total_views_chart = new Chart(
    document.getElementById('totalViewsChart'),
    total_views_data_config
  );

</script>

~;


	
my $noNonActivated = $SBdb->do("SELECT id FROM members WHERE activated = 0") || 0;
my $mailMembers = $SBdb->do("SELECT id FROM members WHERE activated = 1 AND mailme = 1");
my $badMailMembers = $SBdb->do("SELECT id FROM members WHERE activated = 1 AND mailme = 1 AND badmail > 0");
my $liveMailList = $mailMembers - $badMailMembers;
my $currentMailQueue = int($SBdb->do("SELECT id FROM members WHERE activated = 1 AND mailme = 1 AND badmail = 0 AND mailme_sent = 0")) || 0;
my $matchMembers = $SBdb->do("SELECT id FROM members WHERE activated = 1 AND matchme = 1");
my $invitedMembers = $SBdb->do("SELECT id FROM members WHERE activated = 1 AND invited_by != ''");
my $invitingMembers = $SBdb->do("SELECT id FROM members WHERE invited_by != '' GROUP BY invited_by");
my $ActiveLastDay = $SBdb->do("SELECT id FROM members WHERE activated = 1 AND last_active > UNIX_TIMESTAMP(NOW() - INTERVAL 1 DAY)");
my $ActiveLastWeek = $SBdb->do("SELECT id FROM members WHERE activated = 1 AND last_active > UNIX_TIMESTAMP(NOW() - INTERVAL 1 WEEK)");
my $ActiveLastMonth = $SBdb->do("SELECT id FROM members WHERE activated = 1 AND last_active > UNIX_TIMESTAMP(NOW() - INTERVAL 1 MONTH)");
my $ActiveLastYear = $SBdb->do("SELECT id FROM members WHERE activated = 1 AND last_active > UNIX_TIMESTAMP(NOW() - INTERVAL 1 YEAR)");
my $inactiveMembers = $total_members - $ActiveLastYear;
my $listingMembers = int($SBdb->do("SELECT id FROM posts WHERE status = 'live' GROUP by lister")) || 0;
my $noSearchers = int($SBdb->do("SELECT id FROM searches WHERE user_id REGEXP '^[0-9]+\$' GROUP by user_id")) || 0;
my $getStripes = $SBdb->prepare("SELECT stripe_1, stripe_2, stripe_3 FROM site_averages WHERE id = 1");
$getStripes->execute;
my ($stripe_1, $stripe_2, $stripe_3) = $getStripes->fetchrow_array;
$getStripes->finish;
my $two_stripes = $SBdb->do("SELECT id FROM members WHERE trust_score >= $stripe_2 AND trust_score < $stripe_3");
my $three_stripes = $SBdb->do("SELECT id FROM members WHERE trust_score >= $stripe_3");

print qq~
<tr>
<td class="left bold">Registrations pending:</td>
<td class="right">$noNonActivated</td>
</tr>
<tr>
<td class="left bold">Mail subscribed:</td>
<td class="right">$mailMembers</td>
</tr>
<tr>
<td class="left bold">Mail blocked:</td>
<td class="right">$badMailMembers</td>
</tr>
<tr>
<td class="left bold">Live mailing list:</td>
<td class="right">$liveMailList</td>
</tr>
<tr>
<td class="left bold">Current mail queue:</td>
<td class="right">$currentMailQueue</td>
</tr>
<tr>
<td class="left bold">Successfully invited members:</td>
<td class="right">$invitedMembers</td>
</tr>
<tr>
<td class="left bold">Inviting members:</td>
<td class="right">$invitingMembers</td>
</tr>
<tr>
<td class="left bold">Digest subscribed:</td>
<td class="right">$matchMembers</td>
</tr>
<tr>
<td class="left bold">Silver members:</td>
<td class="right">$two_stripes</td>
</tr>
<tr>
<td class="left bold">Gold members:</td>
<td class="right">$three_stripes</td>
</tr>
<tr>
<td class="left bold">Members active in last month:</td>
<td class="right">$ActiveLastMonth</td>
</tr>
<tr>
<td class="left bold">Members active in last 7 days:</td>
<td class="right">$ActiveLastWeek</td>
</tr>
<tr>
<td class="left bold">Members active in last day:</td>
<td class="right">$ActiveLastDay</td>
</tr>
<tr>
<td class="left bold">Members active in last year:</td>
<td class="right">$ActiveLastYear</td>
</tr>
<tr>
<td class="left bold">Members with at least 1 listing:</td>
<td class="right">$listingMembers</td>
</tr>
<tr>
<td class="left bold">Members who searched at least once:</td>
<td class="right">$noSearchers</td>
</tr>
<tr>
<td class="left bold">Inactive members:</td>
<td class="right">$inactiveMembers</td>
</tr>~;
}
print qq~
<tr>
<td class="left bold"><a href="$baseURL/?search">Listings:</a></td>
<td class="right">$noListings</td>
</tr>
<tr>
<td class="left">&nbsp;&nbsp;&nbsp;&nbsp;<a href="$baseURL/?search&filter=offers&physical=1">Items offered:</a></td>
<td class="right">$noOfferItems</td>
</tr>
<tr>
<td class="left">&nbsp;&nbsp;&nbsp;&nbsp;<a href="$baseURL/?search&filter=requests&physical=1">Items requested:</a></td>
<td class="right">$noRequestItems</td>
</tr>
<tr>
<td class="left">&nbsp;&nbsp;&nbsp;&nbsp;<a href="$baseURL/?search&filter=offers&physical=0">Skills offered:</a></td>
<td class="right">$noOfferSkills</td>
</tr>
<tr>
<td class="left">&nbsp;&nbsp;&nbsp;&nbsp;<a href="$baseURL/?search&filter=requests&physical=0">Skills requested:</a></td>
<td class="right">$noRequestSkills</td>
</tr>
<tr>
<td class="left bold"><a href="$baseURL/?search&filter=offers">Total offers:</a></td>
<td class="right">$noOffers</td>
</tr>
<tr>
<td class="left bold"><a href="$baseURL/?search&filter=requests">Total requests:</a></td>
<td class="right">$noRequests</td>
</tr>~;

if ($myAdmin || $myModerator){
	
my $noListers = $SBdb->do("SELECT DISTINCT(lister) FROM posts WHERE status = 'live'");
my $spamListings = $SBdb->do("SELECT id FROM posts WHERE status = 'spam'");
my $noTotalTrans = $SBdb->do("SELECT id FROM transactions");
my $noComplete = $SBdb->do("SELECT id FROM transactions WHERE status = 'delivered'");
my $noPending = $SBdb->do("SELECT id FROM transactions WHERE status != 'cancelled' AND status != 'auto-cancelled' AND status != 'delivered'");
my $noCancelTrans = $SBdb->do("SELECT id FROM transactions WHERE status = 'cancelled'");
my $noAutoCancelTrans = $SBdb->do("SELECT id FROM transactions WHERE status = 'auto-cancelled'");
my $transSuccess = sprintf("%.1f", ($noComplete / ($noComplete + $noCancelTrans + $noAutoCancelTrans)) * 100);
my $noConversations = $SBdb->do("SELECT COUNT(*) c FROM messages WHERE sender != 30 AND recipient != 30 GROUP BY convo_id HAVING c > 1");
my $noMessages = $SBdb->do("SELECT id FROM messages WHERE sender != 30 AND recipient != 30");
my $noLikes = $SBdb->do("SELECT id FROM interactions WHERE action = 'like'");
my $noComments = $SBdb->do("SELECT id FROM interactions WHERE action = 'comment'");
my $averageOffersPerMember = sprintf("%.2f", ($noOffers / $noMembers));
my $averageRequestsPerMember = sprintf("%.2f", ($noRequests / $noMembers));
my $averageTransPerMember = sprintf("%.2f", ($noComplete / $noMembers));
	
print qq~
<tr>
<td class="left bold">Unique listers:</td>
<td class="right">$noListers</td>
</tr>
<tr>
<td class="left bold">Spammed listings:</td>
<td class="right">$spamListings</td>
</tr>
<tr>
<td class="left bold">Average no. offers per member:</td>
<td class="right">$averageOffersPerMember</td>
</tr>
<tr>
<td class="left bold">Average no. requests per member:</td>
<td class="right">$averageRequestsPerMember</td>
</tr>
<tr>
<td class="left bold">Total transactions:</td>
<td class="right">$noTotalTrans</td>
</tr>
<tr>
<td class="left">&nbsp;&nbsp;&nbsp;&nbsp;Successfully completed:</td>
<td class="right">$noComplete</td>
</tr>
<tr>
<td class="left">&nbsp;&nbsp;&nbsp;&nbsp;Pending:</td>
<td class="right">$noPending</td>
</tr>
<tr>
<td class="left">&nbsp;&nbsp;&nbsp;&nbsp;Cancelled:</td>
<td class="right">$noCancelTrans</td>
</tr>
<tr>
<td class="left">&nbsp;&nbsp;&nbsp;&nbsp;Automatically cancelled:</td>
<td class="right">$noAutoCancelTrans</td>
</tr>
<tr>
<td class="left">&nbsp;&nbsp;&nbsp;&nbsp;Transaction success rate:</td>
<td class="right">$transSuccess\%</td>
</tr>
<tr>
<td class="left">&nbsp;&nbsp;&nbsp;&nbsp;Average no. transactions per member:</td>
<td class="right">$averageTransPerMember</td>
</tr>
<tr>
<td class="left bold">Conversations:</td>
<td class="right">$noConversations</td>
</tr>
<tr>
<td class="left bold">Total messages:</td>
<td class="right">$noMessages</td>
</tr>
<tr>
<td class="left bold">Total likes:</td>
<td class="right">$noLikes</td>
</tr>
<tr>
<td class="left bold">Total comments:</td>
<td class="right">$noComments</td>
</tr>~;
}
print qq~
</table>
~;
&footer();
}

$SBdb -> disconnect;
# Exeunt
