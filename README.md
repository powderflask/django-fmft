# Django Filtered Model Formset Tables

[![PyPI Version](https://img.shields.io/pypi/v/django_fmft.svg)](https://pypi.python.org/pypi/django_fmft)
[![Documentation Status](https://readthedocs.org/projects/django-fmft/badge/?version=latest)](https://django-fmft.readthedocs.io/en/latest/?version=latest)

Version: 0.1.0

Re-usable Class-Based Views that integrate
[django-filter](https://django-filter.readthedocs.io/en/stable/index.html) and
[django-tables2](https://django-tables2.readthedocs.io/en/latest/index.html)
with model formsets. Render and process a user-filterable, user-sortable
modelformset in a table with just a few lines of code. Rainbows and
unicorns!

Documentation: <https://django-fmft.readthedocs.io>

Django Filtered Model Formset Tables is free software distributed under the MIT License.


## Features

-   Use a
    [ModelForm](https://docs.djangoproject.com/en/dev/topics/forms/modelforms/)
    /
    [formset](https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#model-formsets)
    to define editable fields, add / delete, extra forms, etc.
-   Use a
    [FilterSet](https://django-filter.readthedocs.io/en/stable/guide/usage.html#the-filter)
    to define filters the formset's queryset
-   Use a
    [Table](https://django-tables2.readthedocs.io/en/latest/index.html)
    to lay out each record, define paging, sorting, etc.
-   Render the
    [Table](https://django-tables2.readthedocs.io/en/latest/index.html)
    with its filtered
    [formset](https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#model-formsets)
    in just a few lines of template code


### Views

-   FilteredTableView

    -   Mixes
        [FilterView](https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration)
        with
        [SingleTableMixin](https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators)
        for views that Filter tabular data.


-   FilteredModelFormsetView

    -   Integrates
        [FilterView](https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration)
        with
        [ModelFormsetView](https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview)
        for views that Filter the queryset used by a formset


-   ModelFormsetTableView

    -   Integrates
        [ModelFormsetView](https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview)
        with
        [SingleTableMixin](https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators)
        for views that render a formset in a Table.


-   FilteredModelFormsetTableView

    -   Integrates
        [FilterView](https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration),
        [ModelFormsetView](https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview)
        and
        [SingleTableMixin](https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators)
        for views that Filter the queryset used by a formset and render
        the formset in a Table.


## Quick Start

1. Install the django-fmft package from PyPI
   ```bash
   $ pip install django-fmft
   ```

   > For other installation methods see [*Installation*](docs/source/installation.md).

2. Add `'django_fmft'` to `INSTALLED_APPS`:
   ```python
   INSTALLED_APPS = [
       ...
       'django_fmft',
       ...
   ]
   ```

### Try Out the Test App

1. `pip install -e git+https://github.com/powderflask/django-fmft.git#egg=django-fmft`
2. `python fmft_tests/manage.py migrate fmft_tests`
3. `python fmft_tests/manage.py loaddata fmft_fixture`
4. `python fmft_tests/manage.py runserver`


## Credits

This package just glues together the amazing functionality provided by
[django-filter](https://django-filter.readthedocs.io/en/stable/index.html),
[django-tables2](https://django-tables2.readthedocs.io/en/latest/index.html),
and
[django-extra-views](https://django-extra-views.readthedocs.io/en/latest/index.html).

<br>

#### *Notes for Documentation*:

Column options `linkify` and `empty_values` are overridden for columns
rendered as form fields

> -   `linkify` is incompatible with a form field representation, so is
>     disabled;
> -   to ensure \'empty\' form fields are rendered, `empty_values` is
>     set to () (i.e., render all values)
