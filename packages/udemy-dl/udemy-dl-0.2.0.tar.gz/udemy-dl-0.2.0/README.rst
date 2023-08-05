Python script to download a udemy.com course, for personal offline use.

Version
~~~~~~~

**0.2.0**

|PyPI version|

Windows Version
~~~~~~~~~~~~~~~

| A Windows version without any dependecies is available here
| https://github.com/nishad/udemy-dl-windows

You can get the lastest Windows release from here.

https://github.com/nishad/udemy-dl-windows/releases/latest

Download ``udemy-dl-win-X.X.X.zip``

Prerequisites
~~~~~~~~~~~~~

-  Python (2 or 3)
-  ``pip`` (Python Install Packager)
-  Python module ``requests``
-  If missing, they will be automatically installed by ``pip``

Preinstall
~~~~~~~~~~

If you don't have ``pip`` installed, look at their `install
doc <http://pip.readthedocs.org/en/latest/installing.html>`__. Easy
install (if you trust them) is to run their bootstrap installer directly
by using:

::

    sudo curl https://bootstrap.pypa.io/get-pip.py | python

Install
~~~~~~~

``udemy-dl`` can be installed using ``pip``

::

    pip install udemy-dl

``or``

::

    python -m pip install udemy-dl

Update
~~~~~~

``udemy-dl`` can be updated using ``pip``

::

    pip install --upgrade udemy-dl

``or``

::

    python -m pip install --upgrade udemy-dl

Usage
~~~~~

Simply call ``udemy-dl`` with the full URL to the course page.

::

    udemy-dl https://www.udemy.com/COURSE_NAME

``or``

::

    python -m udemy_dl https://www.udemy.com/COURSE_NAME

``udemy-dl`` will ask for your udemy username (email address) and
password then start downloading the videos.

By default, ``udemy-dl`` will create a subdirectory based on the course
name. If you wish to have the files downloaded to a specific location,
use the ``-o /path/to/directory/`` parameter.

If you wish, you can include the username/email and password on the
command line using the -u and -p parameters.

::

    udemy-dl -u user@domain.com -p $ecRe7w0rd https://www.udemy.com/COURSE_NAME

If you \`\`don't want to download but save links to a file\`\`\` for
later downloading with a different downloader

::

    python -m udemy_dl -s https://www.udemy.com/COURSE_NAME

For information about all available parameters, use the ``--help``
parameter

::

    udemy-dl --help

Advanced Usage
~~~~~~~~~~~~~~

::

    usage: udemy-dl [-h] [-u USERNAME] [-p PASSWORD]
                    [--lecture-start LECTURE_START] [--lecture-end LECTURE_END]
                    [-o OUTPUT_DIR] [-v]
                    link

    Fetch all the videos for a udemy course

    positional arguments:
      link                  Link for udemy course

    optional arguments:
      -h, --help            show this help message and exit
      -u USERNAME, --username USERNAME
                            Username/Email
      -p PASSWORD, --password PASSWORD
                            Password
      --lecture-start LECTURE_START
                            Lecture to start at (default is 1)
      --lecture-end LECTURE_END
                            Lecture to end at (default is last)
      -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                            Output directory
      -s, --save-links      Do not download but save links to a file
      -v, --version         Display the version of udemy-dl and exit

Uninstall
~~~~~~~~~

``udemy-dl`` can be uninstalled using ``pip``

::

    sudo pip uninstall udemy-dl

You may uninstall the required ``requests`` module too but be aware that
those might be required for other Python modules.

.. |PyPI version| image:: https://badge.fury.io/py/udemy-dl.svg
   :target: http://badge.fury.io/py/udemy-dl
