# ShareBay.org website

The development server is at https://sharebay-dev.org

## Run Locally

We're still working on full functionality outside our dev server.

#### Instructions for a Mac

* Set up Apache & Perl

  Follow [these instructions](https://discussions.apple.com/docs/DOC-250004361), with some tweaks if you want to point directly to this git-managed code:

  * In the `/etc/apache2/httpd.conf` file, I had to uncomment this line:

    `LoadModule cgi_module libexec/apache2/mod_cgi.so`

  * In the /etc/apache2/users/MYUSER.conf, I had to add this line:

    `AddHandler cgi-script .cgi .pl``

  * You can link directly under Sites to the `public_html` directory next to this file; note that you'll have to set execute access permissions on the path of directories for Apache to access them.

  * It has this startup command:

    `sudo launchctl load -w /System/Library/LaunchDaemons/org.apache.httpd.plist`

  * Here is the shutdown command (not included in the doc):

    `sudo launchctl unload /System/Library/LaunchDaemons/org.apache.httpd.plist`

  At this point. you should see some page (with Perl errors) at http://localhost/~USERNAME/index.cgi

* Install Perl modules

  * Install easy modules

  ```
  sudo cpan MIME::Lite
  sudo cpan ExtUtils::PkgConfig
  brew install gd
  sudo cpan Image::Resize
  sudo cpan CGI::Carp
  sudo cpan DBI
  sudo cpan LWP::UserAgent
  ```

  * Install DBD::mysql

  Download from https://metacpan.org/pod/DBD::mysql, then:

  ```
  perl Makefile.PL --libs="-L/opt/homebrew/Cellar/mysql/8.0.33/lib -lmysqlclient"
  make
  make test
  make install
  ```

* Configure MySQL

  * Set a password for the `sharebay_user` in public_html/config.pl

  * Log in to mysql (eg. `mysql -u root`) and then:

    * `CREATE USER sharebay_user IDENTIFIED BY '...';` <- fill in password

    * `CREATE DATABASE IF NOT EXISTS 'sharebay_dbase' DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;`

  * Then from a terminal: `mysql -u sharebay_user -p sharebay_dbase < sharebay_dbase-blank.sql`

* Try it out. http://localhost/~USERNAME/index.cgi

  * Do the following to remove `perl -p -i -e "s|use cPanelUserConfig|use cPanelUserConfig|" public_html/*`

  * Edit public_html/common.pl and find lines with the words "bypass HonorPay" as instructed.

  * You may find that `/usr/bin/perl` doesn't work. I do the following to use my own install from brew: `perl -p -i -e "s|/usr/bin/perl|/opt/homebrew/bin/perl|" public_html/*`

  * Remember to undo those changes before committing.
