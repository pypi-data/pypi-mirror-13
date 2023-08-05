Django Church Contact
=====================

Simple contact form for Django Church sites.


Installation
------------

.. _pip: http://www.pip-installer.org/

Install the package with pip_::

    pip install djangochurch-contact

Add ``djangochurch_contact`` to ``INSTALLED_APPS``::

    INSTALLED_APPS = [
        ...
        'djangochurch_contact',
    ]

Add the URL include to ``urlpatterns``::

    urlpatterns = [
        ...

        # Contact form
        url(r'^contact/', include('djangochurch_contact.urls', namespace='contact')),
    ]
