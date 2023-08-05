mezzanine-references
====================

Customer references page and slideshow on homepage.

Quick start
-----------

1. Install the app
2. Add ``mezzanine_references`` in your ``INSTALLED_APPS``
3. Run ``python manage.py syncdb`` to create new database tables

Usage
-----

First create page of type "References" in Mezzanine admin interface.

References as slideshow
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    {% load references_tags %}

    {% block extra_css %}
    # Load stylesheet (optional)
    <link rel="stylesheet" href="{% static "css/mezzanine-references.css" %}">
    {% endblock %}

    # Create slideshow of reference page with title "Reference"
    {% references_slideshow title="Reference" %}
