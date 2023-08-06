catscan, or mindgrep
=======

Forgot where you put that file? Forgot what you were working on?

Wish you could grep against a file you forgot about?

Installation
------------

From the project root directory::

    $ pip install catscan

or::

    $ python setup.py install


Usage
-----

Simply run it with something that might be in the file, and it will check through files you worked with in your bash history::

    # Find files you worked on that have the search string 'install' in them.
    $ catscan 'install'
    /home/johannestaas/dev/catscan/catscan/install.py
    /home/johannestaas/dev/catscan/setup.py
    /home/johannestaas/dev/catscan/README.rst
    /home/johannestaas/dev/catscan/catscan/install.py
    /home/johannestaas/dev/mkpip/setup.py

Use --help/-h to view info on the arguments::

    $ catscan --help

More complex scan behavior is also available::

    # search using regex (python format)
    $ catscan -r '201[56]-\d+-\d+'

    # limit to files less than 1 megabyte
    $ catscan -m 1 'foo'

    # limit to files less than ~100 kilobytes 
    $ catscan -m 0.1 'foo'

    # case insensitive search
    $ catscan -i 'foo'

    # Look for files that are not necessarily ASCII (using file magic)
    $ catscan -a 'CAFEBABE'

    # Quit after finding the first matching file
    $ catscan -q 1 'foo'


Release Notes
-------------

:0.0.6:
    Removed start/end features to simplify runtime requirements
:0.0.3:
    bugfree (enough) version for release
:0.0.2:
    Finished main features
:0.0.1:
    Project created
