Eve-Statsd
==========
.. image:: https://travis-ci.org/tarzan0820/Eve-Statsd.png?branch=master
    :target: https://travis-ci.org/tarzan0820/Eve-Statsd

An addon for Eve. Eve-Statsd automatically monitors active domains/resources, sending "Hit Counters" and "Timers" to your statsd instance

Features
--------

- For enabled resources, monitors api hits and response time to your statsd instance
- You can also use the statsd object at `app.statsd` to do custom timing  

License
-------
Eve-Statsd is `GPLv3 <http://www.gnu.org/licenses/gpl-3.0.txt>`_ licensed.

Install
-------

.. code-block:: bash

    $ pip install Eve-Statsd

Usage
-----
Example usage is show below.

.. code-block:: python

    from Eve import eve
    from eve_statsd import StatsD

    app = Eve()
    StatsD(app)

Config
------
There are 4 options for Eve-Statsd taken from ``app.config``:

- ``STATSD_HOST`` (default: ``'localhost'``)
- ``STATSD_PORT`` - (default: ``8125``)
- ``STATSD_PREFIX`` - (default: ``None``)
- ``STATSD_MONITORED_DOMAINS`` - (default: ``[]``)

STATSD_MONITORED_DOMAINS is a list of all domains that should be monitored. If none is provided all declare domians are monitored
