====================
nethserver-blacklist
====================

``nethserver-blacklist`` provides two kinds of blacklists: `IP blacklist`_ and `DNS blacklist`_.
The former blocks connections from/towards a set if IP addresses, while the latter blocks DNS requests to a set of domains.

IP blacklist
============

Configuration
-------------

IP blacklist is managed by properties of ``blacklist`` key inside ``configuration`` database:

* ``status``: can be ``enabled`` or ``disabled``, if ``enabled`` selected ``Categories`` will be blocked using ipsets
* ``Categories``: a comma-separeted list of blacklist categories, a valid category must have a corresponding file inside ``/usr/share/nethserver-blacklist/ipsets``.
  Example: given the category ``test``, a file named ``/usr/share/nethserver-blacklist/ipsets/test.netset`` or ``/usr/share/nethserver-blacklist/ipsets/test.ipset`` must exist
* ``Url``: the GIT URL from where blacklists will be downloaded
* ``Whitelist``: a comma-separated list of hosts excluded from the blacklists. The host can be an IP, a CIDR, an host object or a CIDR object
* ``MaxElem`` : It does define the maximal number of elements which can be stored in the set, default 131072. You have to stop shorewall before to destroy the set, the shorewall service start will created it again with the new value.

::

 config setprop blacklist MaxElem 262144
 systemctl stop shorewall
 for S in $(ipset -L -name | grep '^bl-'); do : ; ipset destroy  $S; done
 systemctl start shorewall

Example: ::

 blacklist=configuration
    Categories=category1
    Url=https://my.nethserver.org/git/myrepo
    Whitelist=
    status=disabled


Blacklists
----------

Blacklist implementation is based on ipset:

* download ipset-based blacklist from a remote GIT repository
* block access from/to black listed IPs
* support whitelisting
* lists are updated every 20 minute, ipsets are reloaded on change
* all blocked IPs are logged inside ``/var/log/firewall.log``

GIT repository
^^^^^^^^^^^^^^

The remote GIT repository may contain one or more files with ``.netset`` or ``.ipset`` using `Firehol iplists format <http://iplists.firehol.org/>`_,
each file represent a category.

In addition to Firhol file format, the files can contain a ``Confidence`` tag inside the header. Example: ::

  # ...
  # Category        : attacks
  # Version         : 18
  # Confidence      : 8
  # ...

The confidence is a number between ``0`` and ``10``, a higher number means less false positives.
Lists with a confidence greater than 8, should be safe for production.

The repository can also contain a special file named ``whitelist.global`` which is a special netset that
can be used to quickly remove false positive from a blacklist.

Setup a blacklist server
^^^^^^^^^^^^^^^^^^^^^^^^

You can build your own server to distribute blacklists based on Firehol iplists.
First install a clean NethServer, then follow the below steps.

Install required packages: ::

yum install https://github.com/firehol/packages/releases/download/2021-01-01-1948/firehol-3.1.7-11.el7.noarch.rpm https://github.com/firehol/packages/releases/download/2021-01-01-1948/iprange-1.0.4-2.el7.x86_64.rpm

yum install https://repo.ius.io/ius-release-el7.rpm

yum install -y git224-core --enablerepo=ius

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

  mkdir -p /var/www/html/git/ipsets
  git -C /var/www/html/git/ipsets init
  /usr/sbin/update-ipsets enable dshield feodo fullbogons spamhaus_drop spamhaus_edrop sslbl zeus_badips ransomware_rw firehol_level1
  /usr/sbin/update-ipsets run dshield feodo fullbogons spamhaus_drop spamhaus_edrop sslbl zeus_badips ransomware_rw firehol_level1


Set up a cron to regularly update the ipsets: ::

  cat << EOF >> /etc/cron.d/update-ipsets
  */19 * * * * root update-ipsets
  EOF



See also https://github.com/firehol/blocklist-ipsets/wiki/downloading-ip-lists


DNS blacklist
=============

DNS blacklist uses `Pi-Hole FTLDNS <https://docs.pi-hole.net/ftldns/>`_ under the hood.

Configuration
-------------

DNS blacklist is managed by properties of ``ftl`` key inside ``configuration`` database:

* ``status``: can be ``enabled`` or ``disabled``, if ``enabled`` selected ``Categories`` will be blocked using FTLDNS
* ``Categories``: a comma-separeted list of blacklist categories. Valid categories have a corresponding file inside ``/usr/share/nethserver-blacklist/dnss``
  Example: given the category ``test``, a file named ``/usr/share/nethserver-blacklist/dnss/test.dns`` must exist
* ``Url``: the GIT URL from where blacklists will be downloaded
* ``Bypass``: a comma-separated list of hosts whose DNS requests are always allowed. A host can be an IP, a CIDR, an host object or a CIDR object
* ``Roles``: a comma-separated list of firewall zones where DNS blacklist is enabled
* ``UDPPorts``, ``TCPPorts``: the ports FTLDNS is listening to
* ``access``: the zones ``ftl`` systemd service has access to

Example: ::

  ftl=service
      Bypass=
      Categories=category1,category2
      Roles=green
      TCPPorts=1153
      UDPPorts=1153
      Url=https://my.nethserver.org/git/myrepo
      access=green
      status=disabled


Blacklists
----------

Blacklist implementation is based on Pi-Hole gravity database:

* download DNS blacklists from a remote GIT repository and insert them into gravity database
* block DNS requests for listed domains
* support bypass
* lists are updated every 20 minute, ipsets are reloaded on change
* configuration process is logged inside ``/var/log/pihole-FTL.log``
* blocked requests and other statistics are available through `FTLDNS telnet API <https://docs.pi-hole.net/ftldns/telnet-api/>`_

GIT repository
^^^^^^^^^^^^^^

The remote GIT repository may contain one or more files with ``.dns`` extension listing domains to block. Each file represents a category. Category files can contain ``Maintainer``, ``Category`` and ``Confidence`` tag inside the header. ``Confidence`` is a number between ``0`` and ``10``, a higher number means less false positives.
Lists with a confidence greater than ``8`` should be safe for production.

Example content: ::

  #
  # Maintainer      : John Doe
  # Category        : Malware
  # Confidence      : 6
  #
  
  unwanted.domain.com
  dangerousdomain.net
  malwaresite.net
  ...

GEOIP blacklist
===============

Configuration
-------------

GEOIP blacklist is managed by properties of ``geoip`` key inside ``configuration`` database:

* ``status``: can be ``enabled`` or ``disabled``, if ``enabled`` selected ``Categories`` will be blocked using ipsets
* ``Categories``: a comma-separeted list of geoip blacklist categories, a valid category must have a corresponding file inside ``/usr/share/nethserver-blacklist/geoips`` without the extensions ``netset``.
  Example: given the category ``fr.netset``, a file named ``/usr/share/nethserver-blacklist/geoips/fr.netset``must exist
* ``Url``: the GIT URL from where blacklists will be downloaded (default ipdeny.com)
* ``Whitelist``: a comma-separated list of hosts excluded from the blacklists. The host can be an IP, a CIDR, an host object or a CIDR object
* ``MaxElem`` : It does define the maximal number of elements which can be stored in the set, default 131072. You have to stop shorewall before to destroy the set, the shorewall service start will created it again with the new value.

::

 config setprop geoip MaxElem 262144
 systemctl stop shorewall
 for S in $(ipset -L -name | grep '^geo-'); do : ; ipset destroy  $S; done
 systemctl start shorewall

Example: ::

 geoip=configuration
    Categories=fr,es
    Url=https://www.ipdeny.com/ipblocks/data/countries/all-zones.tar.gz
    Whitelist=
    status=disabled


blacklist
---------

Geoip blacklist implementation is based on ipset:

* download geoip blacklist from the website ipdeny.com
* block access from/to black listed IPs
* support whitelisting
* lists are updated each night, ipsets are reloaded on change
* all blocked IPs are logged inside ``/var/log/firewall.log``


Example
-------

The geoip list must be enabled manually: ::

 config setprop geoip status enabled
 signal-event nethserver-blacklist-save geoips

Once downloaded you can enable the geo banning by the command line: ::

 config setprop geoip status enabled Categories es,fr Whitelist '195.234.41.0/24,195.234.42.3'
 signal-event nethserver-blacklist-save geoips

The command above takes care to whitelist a CIDR network or a specific IP
