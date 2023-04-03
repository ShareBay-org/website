#!/usr/bin/perl
use cPanelUserConfig;
use DBI;
my $active = 0;

# THIS SCRIPT IS FOR PROCESSING BOUNCED EMAILS

my @input = <STDIN>;

if ($active){
	
my $email = join('', @input);


## CONNECT TO SHAREBAY (REMOTE) DATABASE
my $SBdb = DBI->connect("DBI:mysql:database=sbdata_dbase;host=localhost;mysql_local_infile=1", 'sbdata_user', ']YsrC~4&mvHQ',{RaiseError => 1, PrintError => 1});

my $update = $SBdb->prepare("UPDATE members SET badmail = badmail + 1 WHERE email LIKE ? LIMIT 1");

if (
$email =~ m/status: 5\.\d\.\d/i ||
$email =~ m/action: failed/i ||
$email =~ m/reason: 5\.\d\.\d/i ||
$email =~ m/MAILER-DAEMON/i ||
$email =~ m/mailbox does not exist/i ||
$email =~ m/no such user/i ||
$email =~ m/delivery to the following recipients failed/i ||
$email =~ m/recipient address rejected/i ||
$email =~ m/host or domain name not found/i ||
$email =~ m/mailbox unavailable/i
){
my @addrs;
foreach (@input) {
$_ =~ s/^.*?([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+).*?$/$1/i;
push (@addrs, $1);
}
my @unique = &uniq(@addrs);
foreach my $e (@unique) {
$update->execute("$e");
}
}
$update->finish;
}


sub uniq {
my %seen;
grep !$seen{$_}++, @_;
}

# Exeunt
