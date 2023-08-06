HCP Tool
========

HCP Tool (**hcpt**) offers some a few functions that might be useful when
working with Hitachi Content Platform (HCP).

Features
--------

*   Calculate the access token needed to access an authenticated namespace or the Management API
*   Load HCP with test data
*   List the content of a namespace (or parts of it)
*   Change the retention of objects within HCP
*   Delete objects from HCP, supporting Purge and Privileged Delete


Dependencies
------------

You need to have at least Python 3.4.3 installed to run **hcpt**.

It depends on the `hcpsdk <http://hcpsdk.readthedocs.org/en/latest/>`_ to
access HCP.

Documentation
-------------

To be found at `readthedocs.org <http://hcpt.readthedocs.org>`_

Installation
------------

Install **hcpt** by running::

    $ pip install hcpt


-or-

get the source from `gitlab.com <https://gitlab.com/simont3/hcptool>`_,
unzip and run::

    $ python setup.py install


-or-

Fork at `gitlab.com <https://gitlab.com/simont3/hcptool>`_

Contribute
----------

- Source Code: `<https://gitlab.com/simont3/hcptool>`_
- Issue tracker: `<https://gitlab.com/simont3/hcptool/issues>`_

Support
-------

If you've found any bugs, please let me know via the Issue Tracker;
if you have comments or suggestions, send an email to `<sw@snomis.de>`_

License
-------

The MIT License (MIT)

Copyright (c) 2011-2016 Thorsten Simons (sw@snomis.de)

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
