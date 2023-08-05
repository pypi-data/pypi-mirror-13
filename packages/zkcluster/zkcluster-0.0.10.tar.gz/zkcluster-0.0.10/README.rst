===========
ZK Cluster
===========

This library provides a framework for writing clustered services.

Currently, it is derived from the basis used in HAAlchemy, and is
intended to be used with `HAAlchemy <https://bitbucket.org/zzzeek/haalchemy>`_
and `Connmon <https://bitbucket.org/zzzeek/connmon>`_.

The core of the framework is a clusterable service which can connect
with other clusterable services using a p2p system, and within the p2p
system a partial implementation of the RAFT consensus algorithm may
also be used for "leader" selection.

Messaging is performed using a simple RPC scheme.
Applications which use the system only work with RPC message objects.

The file ``demo.py`` illustrates some use of the API.

The ZKCluster API is very specific to its current use cases, and is likely
not useful as a general use RPC / clustering library.