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

Release
-------

To make a new release, do the following steps::

    $ vi setup.py  # bump version
    $ git add setup.py
    $ git commit -m "bump version to X.X.X"
    $ git tag vX.X.X
    $ git push --tags
    $ python sdist upload
