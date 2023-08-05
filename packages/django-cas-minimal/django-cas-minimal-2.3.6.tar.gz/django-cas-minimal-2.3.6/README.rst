=============================
django-cas
=============================

.. image:: https://badge.fury.io/py/django-cas-minimal.png
    :target: https://badge.fury.io/py/django-cas-minimal

.. image:: https://travis-ci.org/ParthKolekar/django-cas.png?branch=master
    :target: https://travis-ci.org/ParthKolekar/django-cas

A Django CAS library for version 1.7.4 which actually works

Documentation
-------------

The full documentation is at https://django-cas.readthedocs.org.

Quickstart
----------

Install django-cas::

    pip install django-cas-minimal

Then use it in a project::

    import django_cas

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements-test.txt
    (myenv) $ python runtests.py

Credits
---------

Credits to https://bitbucket.org/cpcc/django-cas

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
