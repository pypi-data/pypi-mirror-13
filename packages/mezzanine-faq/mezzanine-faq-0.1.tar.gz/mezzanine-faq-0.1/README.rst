mezzanine-faq
====================

Frequently Asked Questions page made simple.

Quick start
-----------

1. Install the app
2. Add ``mezzanine_faq`` in your ``INSTALLED_APPS``
3. Run ``python manage.py syncdb`` to create new database tables

Usage
-----

First create page of type "faq" in Mezzanine admin interface.

Include FAQ
~~~~~~~~~~~

You can also include FAQ on another page.

.. code-block:: python

    {% load faq_tags %}

    # Create list of page with title "myfaq"
    {% faq_list title="myfaq" %}
