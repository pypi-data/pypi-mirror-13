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

Add the compropago app to ``INSTALLED_APPS``. Do not forget to also list ``django.contrib.humanize``:

.. code:: python

    INSTALLED_APPS = (
        'django.contrib.humanize',
        ...
        'lfs_compropago',
    )

Now add settings for your compropago account:

.. code:: python

    LFS_COMPROPAGO_PRIVATE_API_KEY='pk_test_95a6ded8c854153ff'
    LFS_COMPROPAGO_CONVERT_FROM_USD = True
    LFS_COMPROPAGO_OPENXCHANGE_API_KEY='skdd_test_5c8658531ec449283'

The default currency for LFS is USD but Compropago only uses MXN. I use `OpenExchangeRates.org <https://openexchangerates.org>`_ 
to get an updated conversion
``LFS_COMPROPAGO_CONVERT_FROM_USD`` to True if you want 

Finally, add url routingsin your ``urls.py``:

.. code:: python

    urlpatterns += patterns("",
        ...
        (r'^compropago/', include('lfs_compropago.urls')),
    )

Restart Django.

After restart, go to "Manage -> Payment methods", add a new one, and select
"Compropago" on "Module" field.

