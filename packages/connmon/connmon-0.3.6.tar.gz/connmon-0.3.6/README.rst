=======
connmon
=======

A "top"-like tool that monitors database connections across many processes
and servers.   The initial use case is that of tracking the large numbers
of Python processes and database connections used by Openstack, however
the system works with any SQLAlchemy application.


Setup
=====

First, install connmon with pip.

Connmon has a config file which by default is in ``/etc/connmon.cfg``.
A simple file looks like::

	# sample config, listen on 0.0.0.0:5800 and clients
	# will connect to 192.168.1.205:5800
	[connmon_service_default]
	name: default

	nodes:
	    node1 hostname=192.168.1.205:5800

This file is consulted by the connmon daemon as well as all client connections
in order to establish in what location(s) the daemon is running.

If testing only on a single host, connmon can be used without a config file;
if the file isn't present, a default config that looks like the following
is used::

	# default config if no /etc/connmon.cfg and no
	# --config <file> option is passed
	[connmon_service_default]
	name: default

	nodes:
	    node1 hostname=localhost:5800 bind=0.0.0.0

Then, the connmon daemon may be started::

	connmond

This daemon listens for clients which will give it information about how many
connections they're using.  It stores this state in memory and can then report
on it.   If the daemon is stopped or becomes unavailable to clients, each client
keeps track of its state locally and will continue to try and reconnect
to the daemon.  When it does, it will bring the daemon up to date with its
connection status.

To configure a stats client, connmon provides a plugin to the SQLAlchemy
engine.   To enable usage of the plugin in an application that talks
to the database, use a URL like this::

	mysql+pymysql_connmon://root:sa@127.0.0.1/neutron?charset=utf8&connmon_service=default

The URL format above will get a little simpler in SQLAlchemy 1.1 where we'll
add some more portable ways to bundle "plugins" with a database URL.

Finally, we can view current connections using the console::

	connmon

Then start up the applications that use the database.
Everyone with the config will establish a TCP
connection to the console at "192.168.1.205:5800".

See the screenshot.png included.

Connecting without Config
=========================

The URL can also specify a specific host/port::

	mysql+pymysql_connmon://root:sa@127.0.0.1/neutron?charset=utf8&connmon_addr=192.168.1.205:5800

Configuring an HA Cluster
=========================

Multiple nodes can be configured to each run ``connmon listen`` such that
they form a cluster; start up a server on each node with
``connmond --node <nodename>``::


	[connmon_service_default]
	name: default

	nodes:
	    node1 hostname=192.168.1.205:5800
	    node2 hostname=192.168.1.206:5800
	    node3 hostname=192.168.1.207:5800

In the above model, all nodes contact each other and share all events.  Connecting
to the "default" servicename without a node name will cause the client to connect
to a random node in the cloud.  It will try each node until it finds one
that connects.

Using With Devstack
===================

Here are the magic incantations to add connmon to a devstack setup.  First
install connmon globally.  Then in local.conf (note the double slash escapes)::

	[[post-config|$NOVA_CONF]]

	[database]
	connection = mysql+pymysql_connmon://root:sa@127.0.0.1/nova?charset=utf8\\&connmon_service=default

	[api_database]
	connection = mysql+pymysql_connmon://root:sa@127.0.0.1/nova_api?charset=utf8\\&connmon_service=default

	[[post-config|$NEUTRON_CONF]]

	[database]
	connection = mysql+pymysql_connmon://root:sa@127.0.0.1/neutron?charset=utf8\\&connmon_service=default

	[[post-config|$KEYSTONE_CONF]]

	[database]
	connection = mysql+pymysql_connmon://root:sa@127.0.0.1/keystone?charset=utf8\\&connmon_service=default


	[[post-config|$CINDER_CONF]]

	[database]
	connection = mysql+pymysql_connmon://root:sa@127.0.0.1/cinder?charset=utf8\\&connmon_service=default

	[[post-config|$GLANCE_API_CONF]]

	[database]
	connection = mysql+pymysql_connmon://root:sa@127.0.0.1/glance?charset=utf8\\&connmon_service=default


