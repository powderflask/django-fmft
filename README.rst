====================================
Django Filtered Model Formset Tables
====================================


.. image:: https://img.shields.io/pypi/v/django_fmft.svg
        :target: https://pypi.python.org/pypi/django_fmft

.. image:: https://img.shields.io/travis/powderflask/django_fmft.svg
        :target: https://travis-ci.com/powderflask/django_fmft

.. image:: https://readthedocs.org/projects/django-fmft/badge/?version=latest
        :target: https://django-fmft.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status


.. image:: https://pyup.io/repos/github/powderflask/django_fmft/shield.svg
     :target: https://pyup.io/repos/github/powderflask/django_fmft/
     :alt: Updates



Re-usable Class-Based Views that integrate django-filter_ and django-tables2_ with model formsets.
Render and process a user-filterable, user-sortable modelformset in a table with just a few lines of code.
Rainbows and unicorns!


* Free software: MIT license
* Source: https://github.com/powderflask/django-fmft
* Documentation: https://django-fmft.readthedocs.io.


Features
--------
* use a ModelForm_ / formset_ to define editable fields, add / delete, extra forms, etc.;
* use a FilterSet_ to define filters the formset's queryset;
* use a Table_ to layout each record, define paging, sorting, etc.;
* render the Table_ with its filtered formset_ in just a few lines of template code.

Views
=====
* FilteredTableView
    Mixes FilterView_ with SingleTableMixin_ for views that Filter tabular data.

* FilteredModelFormsetView
    Integrates FilterView_ with ModelFormsetView_ for views that Filter the queryset used by a formset

* ModelFormsetTableView
    Integrates ModelFormsetView_ with SingleTableMixin_ for views that render a formset in a Table.

* FilteredModelFormsetTableView
    Integrates FilterView_, ModelFormsetView_ and SingleTableMixin_ for views that Filter the queryset used by a formset
    and render the formset in a Table.

Quick Start
-----------
* ``pip install django-fmft``
* ``INSTALLED_APPS = [... 'fmft', ...]``
* optionally, override ``fmft/form_field.html`` with preferred form rendering template
* write some Views

Test App
========
* ``pip install -e  git+https://github.com/powderflask/django-fmft.git``
* ``python fmft_tests/manage.py migrate fmft_tests``
* ``python fmft_tests/manage.py loaddata fmft_fixture``
* ``python fmft_tests/manage.py runserver``


Credits
-------

This package just glues together the amazing functionality provided by
django-filter_, django-tables2_, and django-extra-views_

Package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _queryset: https://docs.djangoproject.com/en/dev/ref/models/querysets/
.. _ModelForm: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/
.. _formset: https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#model-formsets
.. _django-tables2: https://django-tables2.readthedocs.io/en/latest/index.html
.. _Table: https://django-tables2.readthedocs.io/en/latest/index.html
.. _SingleTableMixin: https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators
.. _django-filter: https://django-filter.readthedocs.io/en/stable/index.html
.. _FilterSet: https://django-filter.readthedocs.io/en/stable/guide/usage.html#the-filter
.. _FilterView: https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration
.. _django-extra-views: https://django-extra-views.readthedocs.io/en/latest/index.html
.. _ModelFormsetView: https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


Notes for Documentation:

Column options ``linkify`` and ``empty_values`` are overridden for columns rendered as form fields

    * ``linkify`` is incompatible with a form field representation, so is disabled;
    * to ensure 'empty' form fields are rendered, ``empty_values`` is set to () (i.e., render all values)
