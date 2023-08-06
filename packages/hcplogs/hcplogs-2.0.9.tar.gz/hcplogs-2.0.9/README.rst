HCP access log collection utility
=================================

Hitachi Content Platform (HCP) logs access to its REST-based interfaces on a
regular basis and keeps these logs for 30 days. While access to these logs
was possible by downloading the internal logs using the System
Management Console (SMC) since HCP version 7.0, it was a quite cumbersome
manual task to extract the logs from the provided zip-file.

HCP version 7.2 invented a Management API (MAPI) endpoint that allows to
selectively access parts (or all) of the internal logs.

The **HCP access log collection utility** tool concentrates on downloading the
access logs only, enabling users to collect (and archive) these logs
on a regular basis.


Features
--------

*   Collects access logs for the REST-based interfaces from HCP systems
*   Supports collection from multiple HCP systems in a single run
*   Stores them in a defined folder structure in a local folder and/or
    in an HCP Namespace for later processing

Dependencies
------------

You need to have at least Python 3.4.3 installed to run **hcplogs**.

It depends on these packages:

*   [hcpsdk](http://simont3.github.io/hcpsdk/) -  Used for access to
    HCP.

Documentation
-------------

To be found at [readthedocs.org](http://hcplogs.readthedocs.org)

Installation
------------

Install **hcplogs** by running::

    $ pip install hcplogs


-or-

get the source from [gitlab.com](https://gitlab.com/simont3/hcplogs),
unzip and run::

    $ python setup.py install


-or-

Fork at [gitlab.com](https://gitlab.com/simont3/hcplogs)

Contribute
----------

- [Source Code](https://gitlab.com/simont3/hcplogs)
- [Issue tracker](https://gitlab.com/simont3/hcplogs/issues)

Support
-------

If you've found any bugs, please let me know via the Issue Tracker;
if you have comments or suggestions, send an email to
[sw@snomis.de](mailto:sw@snomis.de).

License
-------

The MIT License (MIT)

Copyright (c) 2015 Thorsten Simons (sw@snomis.de)

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
