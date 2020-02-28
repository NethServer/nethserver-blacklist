=====================
nethserver-blacklist
====================

Configuration
=============

Properties of ``blacklist`` key inside ``configuration`` database:

* ``status``: can be ``enabled`` or ``disabled``, if ``enabled`` selected ``BlackListCategories`` will be blocked using ipsets
* ``Categories``: a comma-separeted list of blacklist categories, a valid category must have a corresponding file inside ``/usr/share/blacklists/ipsets``.
  Example: given the category ``test``, a file named ``/usr/share/blacklists/ipsets/test.netset`` or ``/usr/share/blacklists/ipsets/test.ipset`` must exists
* ``Url``: the GIT URL from where blacklists will be downloaded
* ``Whitelist``: a comma-separated list of hosts excluded from the blacklists. The host can be an IP, a CIDR, an host object or a CIDR object

Blacklists
==========

Blacklist implementation is based on ipset:

* download ipset-based blacklist from a remote GIT repository
* block access from/to black listed IPs
* support whitelisting
* lists are updated every 20 minute, ipsets are reloaded on change
* all blocked IPs are logged inside ``/var/log/firewall.log``

GIT repository
--------------

The remote GIT repository must contain one or more files with ``.netset`` or ``.ipset`` using `Firehol iplists format <http://iplists.firehol.org/>`_,
each file represent a category.

In addition to Firhol file format, the files can contain a ``Confidence`` tag inside the header. Example: ::

  # ...
  # Category        : attacks
  # Version         : 18
  # Confidence      : 8
  # ...

The confidence is a number between ``0`` and ``10``, an higher number means less false positives.
Lists with a confidence greater than 8, should be safe for production.

Setup a blacklist server
------------------------

You can build your own server to distribute blacklists based on Firehol iplists.
First install a clean NethServer, then follow the below steps.

Install required packages: ::

  yum install -y https://github.com/firehol/packages/releases/download/2020-02-18-0552/firehol-3.1.6-12.el7.noarch.rpm https://github.com/firehol/packages/releases/download/2020-02-18-0552/iprange-1.0.4-2.el7.x86_64.rpm unzip https://centos7.iuscommunity.org/ius-release.rpm
  yum install -y git216-core --enablerepo=ius

Create the git repository and serve it using Apache:

::

  cat << EOF >> /etc/httpd/conf.d/git.conf
  SetEnv GIT_PROJECT_ROOT /var/www/html/git/
  SetEnv GIT_HTTP_EXPORT_ALL
  ScriptAlias /git/ /usr/libexec/git-core/git-http-backend/

  <Directory "/usr/libexec/git-core/">
      <Files "git-http-backend">
          Options +ExecCGI
          Require all granted
      </Files>
  </Directory>
  EOF

  systemctl restart httpd

Configure and enable ``update-ipsets``: ::

  cat << EOF > /etc/firehol/update-ipsets.conf
  BASE_DIR=/var/www/html/git/ipsets
  HISTORY_DIR=/var/www/html/git/ipsets/history
  ERRORS_DIR=/var/www/html/git/ipsets/errors
  GIT_CMD=/usr/bin/git
  EOF

  mkdir /var/www/html/git/ipsets
  git -C /var/www/html/git/ipsets init
  /usr/sbin/update-ipsets enable dshield feodo fullbogons spamhaus_drop spamhaus_edrop sslbl zeus_badips ransomware_rw firehol_level1
  /usr/sbin/update-ipsets run dshield feodo fullbogons spamhaus_drop spamhaus_edrop sslbl zeus_badips ransomware_rw firehol_level1


Set up a cron to regularly update the ipsets: ::

  cat << EOF >> /etc/cron.d/update-ipsets
  */19 * * * * root update-ipsets
  EOF



See also https://github.com/firehol/blocklist-ipsets/wiki/downloading-ip-lists

