LibrePlanet schedule generator
==============================

Get it
------

Install `virtualenv` and `python-dev` package.

On a Debian based distribution, do::

  # aptitude install virtualenv python-dev

  $ cd path/to/lpschedule-generator
  $ virtualenv .

Activate virtual environment
----------------------------

::

   $ cd path/to/lpschedule-generator
   $ source bin/activate

Heads up! Always activate the virtual environment before executing any
of the commands in the following sections.

Install script
--------------

::

   $ python setup.py install

Upgrade script
--------------

::

   $ git pull origin master
   $ python setup.py install

Usage
-----

::

   $ lps_gen YEAR path/to/lp-schd.md > path/to/program-schedule.html

Replace `YEAR` with LP year; for example, for generating LP 2016
schedule, the command will be::

  $ lps_gen 2016 path/to/lp-schd.md > path/to/program-schedule.html
