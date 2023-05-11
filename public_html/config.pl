#!/usr/bin/perl
#use cPanelUserConfig;

# THIS SCRIPT CONTAINS BASIC CONFIGURATION AND CREDENTIALS

# GLOBAL VARIABLES
our $domain = 'sharebay.org';
our $baseURL = 'https://' . $domain;
our $siteroot = '/home/sharebay/public_html';
our $root = '/home/sharebay/_private';
our $salt = '...'; # FOR PASSWORD ENCRYPTION
our $dbName = 'sharebay_dbase';
our $dbHost = 'localhost';
our $dbUser = 'sharebay_user';
our $dbPass = '...';
our $emailPW = '...';
our $HP_dbName = 'honorpay_dbase';
our $HP_dbHost = 'localhost';
our $HP_dbUser = 'honorpay_user';
our $HP_dbPass = '...';

1;
