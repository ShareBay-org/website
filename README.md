# ShareBay.org website

## Run Locally

* Note that we don't have this fully working yet in an environment outside cPanel.

#### Instructions for a Mac:

* Follow [these instructions](https://discussions.apple.com/docs/DOC-250004361), with some tweaks if you want to point directly to this git-managed code:

  * In the `/etc/apache2/httpd.conf` file, I had to uncomment this line:

    `LoadModule cgi_module libexec/apache2/mod_cgi.so`

  * In the /etc/apache2/users/MYUSER.conf, I had to add this line:

    `AddHandler cgi-script .cgi .pl``

  * You can link directly under Sites to the `public_html` directory here; note that you'll have to set execute access permissions on the path of directories for Apache to access them.

  * It has this startup command:

    `sudo launchctl load -w /System/Library/LaunchDaemons/org.apache.httpd.plist`

* Here is the shutdown command (not included in that doc):

`sudo launchctl unload /System/Library/LaunchDaemons/org.apache.httpd.plist`
