|PyPI version| |Build Status| |Coverage Status| |Downloads| |Supported
Python versions| |License| |Codacy Badge|

django-appregistration
======================

This app provides a base class to easily realize django apps that allow
other apps to register parts in it.

Requirements:
-------------

-  Django >= 1.6

Installation
------------

-  From the pip repository: ``pip install django-appregistration``
-  or directly from github:
   ``pip install git+git://github.com/NB-Dev/django-apregistration.git``

Usage
-----

django-appregistration provides two base classes for the registration of
modules from other apps: ``MultiListPartRegistry`` and
``SingleListPartRegistry``. While both have the same basic
functionality, in the ``MultiListPartRegistry`` multiple distinct lists
of objects can be collected, the ``SingleListPartRegistry`` only
contains a single list.

To implement a ``...PartRegistry`` in your app, create a subclass of the
``...PartRegistry`` or your choice in a convenient place in your
application. There are some attributes you can overwrite in your
Subclass:

-  ``part_class`` (required): The (parent) class of the objects that are
   allowed to be inserted into your Registry

-  ``call_function_subpath`` (required): The subpath to the function
   that is to be called by the registry on load (details, see below)

-  ``ignore_django_namespace``\ (default: True): If true, any app that
   starts with ``django.`` in your ``INSTALLED_APPS`` will be ignored on
   load time.

To prevent arbitrary items to be inserted into your Registry the
``...PartRegistry`` classes check each added element to be an instance
of the class that is set as the ``part_class`` attribute of the your
Registry.

When the Registry tries to load elements from the ``INSTALLED_APPS``, it
iterates over the apps and tries, for each to get the sub module /
function that is defined in the ``call_function_subpath``. It then
checks if the retrieved object is callable and calls it if so passing
the Registry itself as only call parameter.

To register elements with the Registry you therefore need to implement
the appropriate function at ``call_function_subpath`` in an app that is
listed in the ``INSTALLED_APPS``. The implemented function then needs to
call the ``add_item`` function on the passed registry.

MultiListPartRegistry(object)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following functions are available:

add\_part(list, part)
^^^^^^^^^^^^^^^^^^^^^

Adds the part given by the ``part`` parameter to the list with the name
given by the ``list`` parameter.

get(list)
^^^^^^^^^

Returns the parts in the list with the name given by the ``list``
parameter. The elements are sorted before they are returned.

sort\_parts(parts)
^^^^^^^^^^^^^^^^^^

Can be overwritten to define a custom ordering of the parts. The default
function simply returns the list unordered.

load()
^^^^^^

When called, the class is initialized and loads the available parts into
its list cache. Does nothing if the ``load()`` was already called. Is
called automatically by the ``get()`` function. There is no need to call
it explicitly unless you want to initialize the class before the first
list is retrieved.

reset()
^^^^^^^

Resets the Registry to its initial state so that the parts will be
reloaded the next time the ``load()`` function is called. Usually there
is no need to call this as it only adds extra overhead when the parts
need to be loaded again.

SingleListPartRegistry(MultiListPartRegistry)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following functions are additionally available:

add\_part(part)
^^^^^^^^^^^^^^^

Adds the part given by the ``part`` parameter to the list.

get()
^^^^^

Returns the parts in the list. The elements are sorted before they are
returned.

Example
-------

Here is an implementation example with a Registry implemented in the
``extendable_app`` app and an app ``extending_app`` that extends the
Registry

File: extendable\_app.registry.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    from django_appregistration import MultiListPartRegistry

    class MyRegisterable(object):
       pass

    class MyRegistry(MultiListPartRegistry):
       part_class = MyRegisterable
       call_function_subpath = 'registerable.register'

File: extending\_app.registerable.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    def register(registry):
       # import inside the function so that the import is only needed if the registry is used
       # and the package is therefore available
       from extendable_app.registry import MyRegisterable
       
       registry.add_part('default', MyRegisterable())
       registry.add_part('other', MyRegisterable())

Like this the ``extending_app`` registers two parts when the registry is
loaded, one in the list ``default`` and one in the list ``other``.

The objects can be retrieved like so:

::

    from extendable_app.registry import MyRegistry
    default_parts = MyRegistry.get('default') # retrieves the `default` list
    other_parts = MyRegistry.get('other') # retrieves the `other` list

Running the tests
-----------------

The included tests can be run standalone by running the
``tests/runtests.py`` script. You need to have Django and mock installed
for them to run. If you also want to run coverage, you need to install
it before running the tests

v.0.0.2
~~~~~~~

-  Bugfix: Using a metaclass to separate the lists for each subclass of
   ``MultiListPartRegistry``. Before each registry used the same list
   resulting in element mixtures if more than one registry was used

v.0.0.1a
~~~~~~~~

-  Rename ``Type`` to ``List`` in classes

v.0.0.1
~~~~~~~

-  Initial implementation of ``MultiTypePartRegistry`` and
   ``SingleTypePartRegistry``

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
