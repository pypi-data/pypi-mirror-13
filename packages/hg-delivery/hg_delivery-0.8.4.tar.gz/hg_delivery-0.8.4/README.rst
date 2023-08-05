hg_delivery README
==================

A one-click deployment tool written in python with `pyramid <http://www.pylonsproject.org>`_ web framework

**current release : v_0_7**

Global overview
---------------

hg_delivery is a web application who aims to simplify the delivery of small projects and helping people to quickly
revert to a previous stable release if something's wrong. This project targets people bothered by command line, looking
for a nice and simple web interface, able to manage multiple remote repositories. 

inspired from :

  - `like banana project <https://github.com/sniku/Likebanana>`_


features list :

  - remote repository access *ssh only*

  - add/delete/edit project items

  - clip project on dashboard

  - display remote project summarize (last commit, current revision ...)

  - display the state of repository

  - update to a specific revision for remote repository

  - one/one repository compare

  - pushing or pulling on/from a remote repository

  - add additional task when updating a repository (*usefull for flushing the cache* or *for gracefull apache*)

  - responsive design (thanks to bootstrap)

  - a scheduler is available to close ssh pool connection if none are used, it leaves clean connections, *thx to pyramid-scheduler*

  - a diff viewer or merge style *thx to mergely* 

Made for what ?
---------------

hg_delivery has been designed to simplify developper daily work.

 - If you developp php application, this can be usefull to deliver your project (no reload expected)

 - In fact any other webapps made with other languages is suitable too.

 - If you need fine grain delivery and or immediate rollback

 - If you whish to manage external repository and change branch one a click

Licensing
---------

Copyright (C) 2014  Stéphane Bard <stephane.bard@gmail.com>

hg_delivery is free software; you can redistribute it and/or modify it under the terms of the M.I.T License. The
original author name should always be reminded as the original author.

Getting Started
---------------

.. code-bloc::bash

    hg clone https://bitbucket.org/tuck/hg_delivery
    cd hg_delivery
    $VENV/bin/python setup.py develop
    $VENV/bin/initialize_hg_delivery_db development.ini
    $VENV/bin/pserve development.ini

.. note:: please use production.ini file for production purpose :)

Sample usage
------------


.. image:: documentation/repositories_hg.gif


Changelog
---------

  - v_0_1 :
    - first True release
    - known bug : cannot push/pull with another password than current node

  - v_0_2 :
    - casperjs use
    - known bug : cannot push/pull with another password than current node

  - v_0_3 :
    - fix bug with node password when push or pull

  - v_0_4 :
    - bug and typo fixes

  - v_0_5 :
    - add task feature with acl control

  - v_0_7 :
    - reuse logs to display delivery date
    - pypi delivery
