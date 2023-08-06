.. contents::

Introduction
============

See the doc of http://pypi.python.org/pypi/five.z2monitor


Use zc.monitor and additional plugins to fetch probes via another thread than the one defined in Zope.

Once the instance is running zc.monitor thread listen to another port (127.0.0.1:8888 in this buildout). You can query values using simple python script or nc.

Example::

    echo 'uptime' | nc -i 1 localhost 8888


Or (when instance is up)::

    bin/instance monitor stats

Or::

    telnet 127.0.0.1 8888

    dbsize



Probes
======

Currently supported probes:

- cache_size -- cache sizes informations
- check_smtp -- Check if SMTP is initialize, return number of errors found. 
- check_upgrade_steps -- Check if all upgrade steps are ran.
- conflictcount -- number of all conflict errors since startup
- count_users -- the total amount of users in your plone site
- count_valid_users -- Count all users connected since 90 days
- cpu_times -- ?
- creation_date_plonesite -- Get creation date of plonesite object. Default return unix_time (defaut=True) if you want ISO time call 'False' attr.
- dates -- Return all date probes
- dbactivity -- number of load, store and connections on database (default=main) for the last x minutes (default=5)
- dbinfo -- Get database statistics
- dbsize -- size of the database (default=main) in bytes
- errorcount -- number of error present in error_log (default in the root).
- help -- Get help about server commands
- interactive -- Turn on monitor's interactive mode
- last_login_time -- Get last login time user. Default return unix_time (defaut=True) if you want ISO time call 'False' attr.
- last_modified_plone_object_time -- Get last modified plone object time. Default return unix_time (defaut=True) if you want ISO time call 'False' attr.
- last_modified_zope_object_time -- Get last modified zope object time. Default return unix_time (defaut=True) if you want ISO time call 'False' attr.
- logstats -- ?
- memory_percent -- ?
- monitor -- Get general process info
- objectcount -- number of object in the database (default=main)
- quit -- Quit the monitor
- refcount -- the total amount of object reference counts
- requestqueue_size -- number of requests waiting in the queue to be handled by zope threads
- stats -- Stats of all information Products.ZNagios know
- threads -- Dump current threads execution stack
- unresolved_conflictcount -- number of all unresolved conflict errors since startup
- uptime -- uptime of the zope instance in seconds
- zeocache -- Get ZEO client cache statistics
- zeostatus -- Get ZEO client status information

How it works
============

This package use differents package

- five.z2monitor
- Products.ZNagios 
- munin.zope
- zc.z3monitor
- zc.monitorcache
- zc.monitorlogstats

Add lines on your buildout::

    [instance]
    ...
    zope-conf-additional =
      <product-config five.z2monitor>
        bind 127.0.0.1:8888
      </product-config>

