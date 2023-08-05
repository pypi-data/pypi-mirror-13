mezzanine-references
====================

Customer references page and slideshow on homepage.

Quick start
-----------

1. Install the app
2. Add ``mezzanine_references`` in your ``INSTALLED_APPS``
3. Run ``python manage.py syncdb`` to create new database tables

Optionally include ``mezzanine-references.css`` in your ``base.html`` template
or customize slideshow on your own.

.. code-block:: python

    {% block extra_css %}
    # Load stylesheet (optional)
    <link rel="stylesheet" href="{% static "css/mezzanine-references.css" %}">
    {% endblock %}

Usage
-----

First create page of type "References" in Mezzanine admin interface.

References as slideshow
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    {% load references_tags %}

    # Create slideshow of reference page with title "Reference"
    {% references_slideshow title="Reference" %}
