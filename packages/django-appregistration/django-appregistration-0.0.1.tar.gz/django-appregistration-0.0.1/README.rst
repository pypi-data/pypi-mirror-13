|PyPI version| |Build Status| |Coverage Status| |Downloads| |Supported
Python versions| |License| |Codacy Badge|

django-appregistration
======================

This app provides a base class to easily realize django apps that allow
other apps to register parts in it.

Requirements:
-------------

-  Django >= 1.6

Quick start
-----------

1. Install django-appregistration

   -  From the pip repository: ``pip install django-appregistration``
   -  or directly from github:
      \`\ ``pip install git+git://github.com/NB-Dev/django-apregistration.git``

UNFINISHED
==========

Running the tests
-----------------

The included tests can be run standalone by running the
``tests/runtests.py`` script. You need to have Django and mock installed
for them to run. If you also want to run coverage, you need to install
it before running the tests

v.0.0.1
~~~~~~~

-  Initial implementation of ``MultiTypePartRegistry`` and
   ``SingleTypePartRegistry``

ToDos:
------

-  Document functionality

Maintainers
-----------

This Project is maintaned by `Northbridge Development Konrad & Schneider
GbR <http://www.northbridge-development.de>`__ Softwareentwicklung

.. |PyPI version| image:: https://img.shields.io/pypi/v/django-appregistration.svg
   :target: http://badge.fury.io/py/django-appregistration
.. |Build Status| image:: https://travis-ci.org/NB-Dev/django-appregistration.svg?branch=master
   :target: https://travis-ci.org/NB-Dev/django-appregistration
.. |Coverage Status| image:: https://coveralls.io/repos/NB-Dev/django-appregistration/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/NB-Dev/django-appregistration?branch=master
.. |Downloads| image:: https://img.shields.io/pypi/dm/django-appregistration.svg
   :target: https://pypi.python.org/pypi/django-appregistration/
.. |Supported Python versions| image:: https://img.shields.io/pypi/pyversions/django-appregistration.svg
   :target: https://pypi.python.org/pypi/django-appregistration/
.. |License| image:: https://img.shields.io/pypi/l/django-appregistration.svg
   :target: https://pypi.python.org/pypi/django-appregistration/
.. |Codacy Badge| image:: https://api.codacy.com/project/badge/grade/e9e55c2658d54801b6b29a1f52173dcf
   :target: https://www.codacy.com/app/tim_11/django-appregistation
