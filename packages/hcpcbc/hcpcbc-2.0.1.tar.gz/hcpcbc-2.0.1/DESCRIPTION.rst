HCP Chargeback Collection utility
=================================

This tool collects chargeback reports from Hitachi Content Platform systems.

Chargeback reports are a good source of information for system analysis,
enabling you to adjust storage and bandwidth allocations based on usage
patterns. These reports can also serve as input to billing systems that need to
determine charges for capacity and bandwidth usage at the tenant or namespace
level.

Features
--------

*   Stores chargeback reports on local disk and/or to an HCP Namespace (with
    retention added, if required).
*   Builds up a report repository over an HCPs lifetime, if run regularly.
*   Remembers the last collection time per Tenant, so that subsequent runs
    will collect newer reports, only.
*   Highly configurable through a config file.


Dependencies
------------

You need to have at least Python 3.4.3 installed to run **hcplogs**.

It depends on `hcpsdk <http://simont3.github.io/hcpsdk/>`_, used to access HCP.

Documentation
-------------

To be found at `readthedocs.org <http://hcpcbc.readthedocs.org>`_

Installation
------------

Install **hcpcbc** by running::

    $ pip install hcpcbc


-or-

get the source from `gitlab.com <https://gitlab.com/simont3/hcpcbc>`_,
unzip and run::

    $ python setup.py install


-or-

Fork at `gitlab.com <https://gitlab.com/simont3/hcpcbc>`_

Contribute
----------

- Source Code: `<https://gitlab.com/simont3/hcpcbc>`_
- Issue tracker: `<https://gitlab.com/simont3/hcpcbc/issues>`_

Support
-------

If you've found any bugs, please let me know via the Issue Tracker;
if you have comments or suggestions, send an email to `<sw@snomis.de>`_

License
-------

The MIT License (MIT)

Copyright (c) 2012-2016 Thorsten Simons (sw@snomis.de)

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
