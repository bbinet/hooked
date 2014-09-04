Hooked
======

Run command on GitHub and BitBucket POST request hooks.

Install
-------

To install `hooked`, do the following steps::

    $ git clone git@github.com:bbinet/hooked.git
    $ cd hooked/
    $ mkvirtualenv hooked
    (hooked) $ python setup.py develop

Configure
---------

Create a configuration file that looks like::

    $ cat path/to/config.cfg

    [server]
    host = 0.0.0.0
    port = 8080
    server = cherrypy
    debug = true

    [hook-myrepo]
    repository = myrepo
    branch = master
    command = /path/to/script.sh
    [hook-all]
    #repository = # will match all repository
    #branch = # will match all branches
    command = /path/to/other/script.sh

Note that the `[server]` section is optionnal, the defaults are::

    [server]
    host = localhost
    port = 8888
    server = wsgiref
    debug = false

Run
---

Run the hooked server by running the following command::

    (hooked) $ hooked path/to/config.cfg

Release
-------

To make a new release, do the following steps::

    $ vi setup.py  # bump version
    $ git add setup.py
    $ git commit -m "bump version to X.X.X"
    $ git tag vX.X.X
    $ git push --tags
    $ python sdist upload
