=====
Kobin
=====

.. image:: https://travis-ci.org/c-bata/kobin.svg?branch=master
    :target: https://travis-ci.org/c-bata/kobin

**This library is a pre-release. Expect missing docs and breaking API changes.**

A lightweight web application framework for python3.5.

* Routing
* Request and Response object
* Template loader for Jinja2
* Static files server

Getting Started
===============

Installation
------------

::

    $ pip install kobin

Usage
-----

.. code-block:: python

    from kobin import Kobin

    app = Kobin()

    @app.route('^/$')
    def index():
        return "Hello Kobin!"


    @app.route('^/user/(?P<name>\w+)/$')
    def hello(name: str):
        return "Hello {}".format(name)

    if __name__ == '__main__':
        app.run()


Requirements
============

* Supported python version is 3.5 only.

License
=======

This software is licensed under the MIT License.

Resources
=========

* `Github <http://https://github.com/c-bata/kobin>`_
* `PyPI <https://pypi.python.org/pypi/kobin>`_


CHANGES
=======

0.0.3 (2016-02-08)
------------------

* Request and Response object.
* tox and Travis-CI Integration.

0.0.2 (2015-12-03)
------------------

* Publish on PyPI.

0.0.0 (2015-09-14)
------------------

* Create this project.


