=================
Django-Speedboost
=================

Replaces select Django modules with Cython-compiled versions for great speed.

Rationale
---------

Code always has bottlenecks, and Django is no exception. By selectively compiling the hot spots in Django with Cython,
we can make it go faster. Django-Speedboost is a drop-in module that when installed replaces parts of Django with its
Cython-based versions.

Requirements
------------

* Python: 2.7
* Django: 1.8.8

Django-Speedboost's test suite runs the Django test suite after installation to verify that it doesn't do anything
incompatible.

Installation
------------

Django-Speedboost is currently compiled for Django 1.8.8 only. Install with:

.. code-block:: bash

    pip install django_speedboost

If you get missing header compilation errors, install your distribution's python library development headers, for
example on Ubuntu:

.. code-block:: bash

    sudo apt-get install libpython-dev

How It Works
------------

Django-Speedboost includes a ``.pth`` file that allows it to import itself at the point the Python interpreter loads.
It uses this to install an import hook that detects the loading of Django submodules to replace them.

Currently replaced modules:

* ``django.template.context``
* ``django.template.context_processors``
* ``django.template.base``
* ``django.template.defaulttags``

Results
=======

Setting Django with WSGI behind Apache 2, ab shows a consistent 13% reduction in load times on an Admin page with loads
of inlines and fields:

.. code-block:: bash

    (venv)ddalex@watson ~/Projects/backend(T7569)$ diff --side-by-side without_so.txt with_so.txt
    This is ApacheBench, Version 2.3 <$Revision: 1604373 $>		This is ApacheBench, Version 2.3 <$Revision: 1604373 $>
    Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.ze	Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.ze
    Licensed to The Apache Software Foundation, http://www.apache	Licensed to The Apache Software Foundation, http://www.apache

    Benchmarking guest (be patient).....done			Benchmarking guest (be patient).....done


    Server Software:        Apache/2.4.7				Server Software:        Apache/2.4.7
    Server Hostname:        guest					Server Hostname:        guest
    Server Port:            80					Server Port:            80

    Document Path:          /admin/model/object/57/		Document Path:          /admin/model/object/57/
    Document Length:        619067 bytes				Document Length:        619067 bytes

    Concurrency Level:      2					Concurrency Level:      2
    Time taken for tests:   15.724 seconds			      |	Time taken for tests:   13.932 seconds
    Complete requests:      20					Complete requests:      20
    Failed requests:        0					Failed requests:        0
    Total transferred:      12390600 bytes				Total transferred:      12390600 bytes
    HTML transferred:       12381340 bytes				HTML transferred:       12381340 bytes
    Requests per second:    1.27 [#/sec] (mean)		      |	Requests per second:    1.44 [#/sec] (mean)
    Time per request:       1572.402 [ms] (mean)		      |	Time per request:       1393.243 [ms] (mean)
    Time per request:       786.201 [ms] (mean, across all concur |	Time per request:       696.621 [ms] (mean, across all concur
    Transfer rate:          769.54 [Kbytes/sec] received	      |	Transfer rate:          868.49 [Kbytes/sec] received

    Connection Times (ms)						Connection Times (ms)
                  min  mean[+/-sd] median   max			              min  mean[+/-sd] median   max
    Connect:        0    0   0.1      0       1		      |	Connect:        0    0   0.0      0       0
    Processing:   624 1570 723.5   2008    2313		      |	Processing:   585 1391 578.5   1764    1991
    Waiting:      621 1566 722.6   1999    2311		      |	Waiting:      572 1381 578.2   1741    1988
    Total:        624 1570 723.5   2008    2313		      |	Total:        585 1391 578.5   1764    1991

    Percentage of the requests served within a certain time (ms)	Percentage of the requests served within a certain time (ms)
      50%   2008						      |	  50%   1764
      66%   2106						      |	  66%   1845
      75%   2237						      |	  75%   1917
      80%   2263						      |	  80%   1936
      90%   2288						      |	  90%   1981
      95%   2313						      |	  95%   1991
      98%   2313						      |	  98%   1991
      99%   2313						      |	  99%   1991
     100%   2313 (longest request)				      |	 100%   1991 (longest request)
