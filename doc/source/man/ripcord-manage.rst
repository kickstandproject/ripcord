==============
ripcord-manage
==============

--------------------------
Control and manage ripcord
--------------------------

:Author: paul.belanger@polybeacon.com
:Date: |today|
:Copyright: PolyBeacon, Inc
:Version: |version|
:Manual section: 1

SYNOPSIS
========

  ripcord-manage <category> <action> [<args>]

DESCRIPTION
===========

ripcord-manage is a CLI tool to control ripcord

OPTIONS
=======

 **General options**

ripcord DB
~~~~~~~~~~

``ripcord-manage db sync``

     Sync the database up to the most recent version.

``ripcord-manage db version``

     Print the current database version.

FILES
=====

* /etc/ripcord/ripcord.conf

SEE ALSO
========

* `ripcord <https://github.com/kickstandproject/ripcord>`__

BUGS
====

* Ripcord is sourced in Github so you can view current bugs at `ripcord <https://github.com/kickstandproject/ripcord>`__
