=========
 hatcher
=========

Surprisingly, a client to talk to the brood server.


Getting started for development
===============================

In order to run tests, the development requirements are required::

    $ pip install -r dev_requirements.txt


Basic Usage
===========

When used in production, the latest **release** tag must be used. For
example, a tag such as ``v0.3.0`` must be used, rather than
``v0.4.0.dev419``.  In all of the following examples, the
``http://brood-dev`` URL must be substituted with a valid server URL.

To get a basic idea of usage::

    hatcher --help

To list the repositories to which the authenticated user has access::

    hatcher --url http://brood-dev user repositories

To upload an egg::

    # Upload a free rh5-x86 egg
    hatcher --url http://brood-dev eggs upload enthought dev rh5-x86 dummy-1.0.1-1.egg

To list existing eggs in a repo::

    # List eggs in the enthought/dev repository for rh5-x86_64 platform (CPython 2.7).
    hatcher --url http://brood-dev eggs list enthought dev rh5-x86_64 cp27

To create a new repository and upload eggs to it::

    # List the repositories (requires administrative permissions on the organization)
    hatcher --url http://brood-dev repositories list enthought
    # Create a new repository (requires administrative permissions on the organization)
    hatcher --url http://brood-dev repositories create enthought \
        geocanopy_dev "the official geocanopy_dev repository"
    # Push some new eggs (requires upload permissions on the repository)
    hatcher --url http://brood-dev eggs batch-upload enthought \
        geocanopy_dev win-x86 egg1-1.0.1-1.egg [egg2 ...]
