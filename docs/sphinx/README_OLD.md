
Django Filtered Model Formset Tables
=======================

[![image](https://img.shields.io/pypi/v/django_fmft.svg)](https://pypi.python.org/pypi/django_fmft)

[![image](https://img.shields.io/travis/powderflask/django_fmft.svg)](https://travis-ci.com/powderflask/django_fmft)

[![Documentation Status](https://readthedocs.org/projects/django-fmft/badge/?version=latest)](https://django-fmft.readthedocs.io/en/latest/?version=latest)

Re-usable Class-Based Views that integrate
[django-filter](https://django-filter.readthedocs.io/en/stable/index.html)
and
[django-tables2](https://django-tables2.readthedocs.io/en/latest/index.html)
with model formsets. Render and process a user-filterable, user-sortable
modelformset in a table with just a few lines of code. Rainbows and
unicorns!

-   Free software: MIT license
-   Source: <https://github.com/powderflask/django-fmft>
-   Documentation: <https://django-fmft.readthedocs.io>.
___

## Features

-   use a
    [ModelForm](https://docs.djangoproject.com/en/dev/topics/forms/modelforms/)
    /
    [formset](https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#model-formsets)
    to define editable fields, add / delete, extra forms, etc.;
-   use a
    [FilterSet](https://django-filter.readthedocs.io/en/stable/guide/usage.html#the-filter)
    to define filters the formset\'s queryset;
-   use a
    [Table](https://django-tables2.readthedocs.io/en/latest/index.html)
    to layout each record, define paging, sorting, etc.;
-   render the
    [Table](https://django-tables2.readthedocs.io/en/latest/index.html)
    with its filtered
    [formset](https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#model-formsets)
    in just a few lines of template code.
___

### Views

-   FilteredTableView

    :   Mixes
        [FilterView](https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration)
        with
        [SingleTableMixin](https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators)
        for views that Filter tabular data.

-   FilteredModelFormsetView

    :   Integrates
        [FilterView](https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration)
        with
        [ModelFormsetView](https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview)
        for views that Filter the queryset used by a formset

-   ModelFormsetTableView

    :   Integrates
        [ModelFormsetView](https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview)
        with
        [SingleTableMixin](https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators)
        for views that render a formset in a Table.

-   FilteredModelFormsetTableView

    :   Integrates
        [FilterView](https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration),
        [ModelFormsetView](https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview)
        and
        [SingleTableMixin](https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators)
        for views that Filter the queryset used by a formset and render
        the formset in a Table.

___


## Quick Start

Install the django-fmft package from PyPI

        $ pip install django-fmft
    For other installation methods see the [*installation doc*](installation.md).

Add `'django_fmft'` to `INSTALLED_APPS`:

        INSTALLED_APPS = [
        ...
        'django_fmft',
        ...
        ]

```{include} example_views.md
```

### Test App

* `pip install -e  git+https://github.com/powderflask/django-fmft.git`
* `python fmft_tests/manage.py migrate fmft_tests`
* `python fmft_tests/manage.py loaddata fmft_fixture`
* `python fmft_tests/manage.py runserver`

## Credits

This package just glues together the amazing functionality provided by
[django-filter](https://django-filter.readthedocs.io/en/stable/index.html),
[django-tables2](https://django-tables2.readthedocs.io/en/latest/index.html),
and
[django-extra-views](https://django-extra-views.readthedocs.io/en/latest/index.html)


Notes for Documentation:

Column options `linkify` and `empty_values` are overridden for columns
rendered as form fields

> -   `linkify` is incompatible with a form field representation, so is
>     disabled;
> -   to ensure \'empty\' form fields are rendered, `empty_values` is
>     set to () (i.e., render all values)
