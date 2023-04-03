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

if (!$FORM{id}){&showAllBlogs;}
elsif ($FORM{id} eq 'new'){&newBlog;}
else{&showBlog;}

sub newBlog{
	
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

sub showAllBlogs{
my $title = 'The Sharebay Blog';
my $desc = 'Stories, help and insights from the Sharebay world of sharing';	
&header($title, $desc, undef, undef, 'blog');
my $sth = $SBdb->prepare("SELECT title, slug, image, summary, author_id, DATE_FORMAT(FROM_UNIXTIME(timestamp), '%M %D, %Y') FROM blog ORDER BY id DESC");
$sth->execute;
print qq~<p>The latest articles and news from Sharebay.</p>~;
if ($sth->rows > 0){
	while (my($title, $slug, $image, $summary, $author_id, $timestamp) = $sth->fetchrow_array){
	print qq~<a href="$baseURL/blog/$slug" title="$title" class="link-block"><h2>$title</h2><img src="$image" style="max-width:300px;height:auto;"/><p>$summary<br/><span class="smaller">Posted: $timestamp</span></p></a>~;	
	}
}else{

print qq~<p>No blogs posted yet.</p>~;
}
&footer;
}


sub dumpform{
my $title = 'Result';
my $desc = 'A description of same';
my $headerInject;
&header($title, $desc, undef, $headerInject, 'blog');
print qq~$FORM{text}~;
&footer;
}


sub showBlog{
my $blog_id = $FORM{id};
my $sth = $SBdb->prepare("SELECT id, title, slug, image, summary, content, author_id, DATE_FORMAT(FROM_UNIXTIME(timestamp), '%M %D, %Y') FROM blog WHERE slug = '$blog_id' OR id = '$blog_id' LIMIT 1");
$sth->execute;
if ($sth->rows > 0){
while(my($id, $title, $slug, $image, $summary, $content, $author_id, $timestamp) = $sth->fetchrow_array){
&header($title, $summary, $image, undef, 'blog');
my $views = int($SBdb->do("SELECT id FROM interactions WHERE action = 'view' AND object_type = 'blog' AND object_id = '$id'"));
my $author_name = &getFullName($author_id);
print qq~<h1 style="margin-bottom:-10px">$title</h1><p class="smaller">Posted in <a href="$baseURL/blog" title="Blogs">blog</a> by <a href="$baseURL/profile?id=$author_id" title="$author_name">$author_name</a>, $timestamp. ~;
if ($myAdmin || $views > 20){
print qq~Read ~, &commafy($views), qq~ times~;
}
print qq~<p><img src="$image" alt="$title" class="full-width-image bottom20"/>$content<p class="smaller italic grey">Written by:</p>~;
&getUserCard($author_id);

&showSocial('blog',$id, "$baseURL/blog?id=$id");
&footer();
&saveView('blog',$id) if $author_id != $myID;
}
}else{
#NOTHING FOUND
&header('No blog found.', undef, undef, undef, 'blog');
print qq~<p class="error">No blog found.</p>~;
&footer;
}
}


 
 
$SBdb -> disconnect;
# Exeunt
