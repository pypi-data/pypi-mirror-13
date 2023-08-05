LibrePlanet schedule generator
==============================

Installation
------------

On a Debian based distribution, do::

  # aptitude install virtualenv python-setuptools

  $ mkdir lpschedule-generator
  $ virtualenv .
  $ source bin/activate

  $ pip install --pre lpschedule-generator


Activating virtual environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Always activate the virtual environment before using the ``lps_gen``
command::

   $ cd path/to/lpschedule-generator
   $ source bin/activate


Usage
-----

::

   $ lps_gen YEAR path/to/lp-schd.md > path/to/program-schedule.html

Replace ``YEAR`` with LP year; for example, for generating LP 2016
schedule, the command will be::

  $ lps_gen 2016 path/to/lp-schd.md > path/to/program-schedule.html


Source
------

::

   $ git clone https://notabug.org/rsd/lpschedule-generator.git
