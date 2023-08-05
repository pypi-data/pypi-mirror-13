==============
LFS Compropago
==============

`Django LFS <http://getlfs.com/>`_ payment processor plugin for `Compropago <https://compropago.com/>`_, a Payment gateway that accepts payments in well known convenience stores across Mexico.

Installation
============

Modify ``buildout.cfg``. Add ``lfs-compropago`` to ``develop`` and ``eggs``::

    [buildout]
    ....
    develop =
        src/lfs-compropago
    eggs =
        django-lfs
        ...
        lfs-compropago

Modify your ``settings.py``
---------------------------

First add ``CompropagoProcessor`` to the list of available payment processors.
It should look like this:

.. code:: python

    LFS_PAYMENT_METHOD_PROCESSORS = [
        ...
        ["lfs_compropago.CompropagoProcessor", _(u"Compropago")],
    ]

Also add it to ``INSTALLED_APPS``:

.. code:: python

    INSTALLED_APPS = (
        ...
        'lfs_compropago',
    )

Now add settings for your compropago account:

.. code:: python

    COMPROPAGO_API_KEY = "UwG9SYdHvh7bZ6eFA3242xxyyzz"

Finally, add url routingsin your ``urls.py``:

.. code:: python

    urlpatterns += patterns("",
        ...
        (r'^compropago/', include('lfs_compropago.urls')),
    )

Restart Django.

After restart, go to "Manage -> Payment methods", add a new one, and select
"Compropago" on "Module" field.

Contributing
============

Submit bugs and issues to the   `GitHub repository <https://github.com/tzicatl/lfs-compropago>`_.

AUTHORS
=======

If you have contributed to this package feel free to add your name and email to the list.

* Noe Nieto <nnieto@noenieto.com>

=======
CHANGES
=======

0.3 (2016-01-17)
----------------

* Compatibility with API version 1.1


0.2 (2015-12-27)
----------------

* Improve documentation and packaging.

0.1 (2015-12-01)
----------------

* Initial release to PyPI.
* Functional Payment processor.



