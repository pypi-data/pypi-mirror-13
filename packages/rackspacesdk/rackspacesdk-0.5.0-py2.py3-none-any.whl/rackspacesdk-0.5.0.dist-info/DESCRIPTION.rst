Rackspace Plugin for the OpenStack SDK
======================================

.. image:: https://travis-ci.org/rackerlabs/rackspace-sdk-plugin.svg?branch=master
    :target: https://travis-ci.org/rackerlabs/rackspace-sdk-plugin

This plugin enables support for Rackspace authentication and services
with the
`OpenStack SDK <https://pypi.python.org/pypi/python-openstacksdk>`_.

Usage
-----

The following example connects to the Rackspace Public Cloud and lists
containers stored in Cloud Files within the IAD datacenter. ::

   from rackspace import connection
   conn = connection.Connection(username="my_user",
                                api_key="123abc456def789ghi",
                                region="IAD")

   for container in conn.object_store.containers():
       print(container.name)

Documentation
-------------

Rackspace-specific documentation is not currently available.

Documentation for the OpenStack SDK is available at
http://python-openstacksdk.readthedocs.org/en/latest/

Requirements
------------

* Python 2.7+, Python 3.4+
* openstacksdk>=0.6

License
-------

Apache 2.0



