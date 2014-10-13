Hooked
======

Run command on GitHub and BitBucket POST request hooks.

Install
-------

You can install `hooked` in a virtualenv (with `virtualenvwrapper` and `pip`)::

    $ mkvirtualenv hooked
    (hooked) $ pip install hooked

Or if you want to contribute some patches to `hooked`::

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

Note that the `[server]` section is optional, the defaults are::

    [server]
    host = localhost
    port = 8888
    server = wsgiref
    debug = false

Run
---

Run the hooked server by running the following command::

    (hooked) $ hooked path/to/config.cfg

Then visit http://localhost:8888/, it should return the current configuration
for this `hooked` server.
If this works, you are ready to configure GitHub and BitBucket POST request web
hooks to your `hooked` server listening address, for example:
http://localhost:8888/.

See:

- https://confluence.atlassian.com/display/BITBUCKET/POST+hook+management
- https://developer.github.com/webhooks/

Release
-------

To make a new release, do the following steps::

    $ vi setup.py  # bump version
    $ git add setup.py
    $ git commit -m "bump version to X.X.X"
    $ git tag vX.X.X
    $ git push --tags
    $ python setup.py sdist upload

Thanks
------

Thanks to the `hook-server <https://github.com/iocast/hook-server>`_ and
`githook <https://github.com/brodul/githook>`_ projects for inspiration.
