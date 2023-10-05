# Django Filtered Model Formset Tables

[![PyPI Version](https://img.shields.io/pypi/v/django_fmft.svg)][1]
[![Docs Status](https://readthedocs.org/projects/django-fmft/badge/?version=latest)][2]
[![Tests](https://github.com/powderflask/django-fmft/actions/workflows/pytest.yaml/badge.svg)](https://github.com/powderflask/django-fmft/actions/workflows/pytest.yaml)

Re-usable Class-Based Views that integrate [django-filter][3] and
[django-tables2][4] with model formsets. Render and process a user-filterable, 
user-sortable modelformset in a table with just a few lines of code. Rainbows and
unicorns!

[1]: <https://pypi.python.org/pypi/django_fmft>
[2]: <https://django-fmft.readthedocs.io/en/latest>
[3]: <https://django-filter.readthedocs.io/en/stable/index.html>
[4]: <https://django-tables2.readthedocs.io/en/latest/index.html>

## Features

-   Use a [ModelForm][5] / [formset][6] to define editable fields, add / delete, extra 
    forms, etc.
-   Use a [FilterSet][7] to define filters the formset's queryset
-   Use a [Table][8] to lay out the formset, define paging, sorting, etc.
-   Render the [Table][9] with its filtered [formset][10] in just a few lines of 
    template code

[5]: <https://docs.djangoproject.com/en/dev/topics/forms/modelforms/>
[6]: <https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#model-formsets>
[7]: <https://django-filter.readthedocs.io/en/stable/guide/usage.html#the-filter>
[8]: <https://django-tables2.readthedocs.io/en/latest/index.html>
[9]: <https://django-tables2.readthedocs.io/en/latest/index.html>
[10]: <https://docs.djangoproject.com/en/dev/topics/forms/modelforms/#model-formsets>

### Views

-   FilteredTableView

    -   Mixes [FilterView][11] with [SingleTableMixin][12] for views that Filter tabular 
        data.


-   FilteredModelFormsetView

    -   Integrates [FilterView][13] with [ModelFormsetView][14] for views that Filter 
        the queryset used by a formset


-   ModelFormsetTableView

    -   Integrates [ModelFormsetView][15] with [SingleTableMixin][16] for views that 
        render a formset in a Table.


-   FilteredModelFormsetTableView

    -   Integrates [FilterView][17], [ModelFormsetView][18], and [SingleTableMixin][19] 
        for views that Filter the queryset used by a formset and render the formset in a
        Table.

[11]: <https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration>
[12]: <https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators>
[13]: <https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration>
[14]: <https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview>
[15]: <https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview>
[16]: <https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators>
[17]: <https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration>
[18]: <https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview>
[19]: <https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators>

*Note:*
Table.Column options `linkify` and `empty_values` are overridden for columns
rendered as form fields
 -   `linkify` is incompatible with a form field representation, so is disabled; 
 -   to ensure \'empty\' form fields are rendered, `empty_values` is set to () (i.e., render all values)

## Quick Start

1. Install the `django-fmft` package from PyPI
    ```bash
    $ pip install django-fmft
    ```

    > For other installation methods see [*Installation*](docs/source/installation.md).

2. Add `'fmft'` to `INSTALLED_APPS`:
    ```python
    INSTALLED_APPS = [
        ...,
        "fmft",
        "django_tables2",
        "django_filters",
        "extra_views",   # optional
           ...,
    ]
    ```

## Get Me Some of That
* [Source Code](https://github.com/powderflask/django-fmft)
* [Read The Docs](https://django-fmft.readthedocs.io/en/latest/)
* [Issues](https://github.com/powderflask/django-fmft/issues)
* [PyPI](https://pypi.org/project/django-fmft)

[MIT License](https://github.com/powderflask/django-fmft/blob/master/LICENSE)

### Check Out the Demo App

1. `pip install -e git+https://github.com/powderflask/django-fmft.git#egg=django-fmft`
2. `python manage.py migrate demo`
3. `python manage.py loaddata demo/fmft_fixture.json`
4. `python manage.py runserver`


### Acknowledgments
Special thanks to BC Hydro, [Chartwell](https://crgl.ca/),
and all [Contributors](https://github.com/powderflask/django-fmft/graphs/contributors)

#### Technology Colophon

This package just glues together the amazing functionality provided by 
[django-filter][20], [django-tables2][21], and [django-extra-views][22].

[20]: <https://django-filter.readthedocs.io/en/stable/index.html>
[21]: <https://django-tables2.readthedocs.io/en/latest/index.html>
[22]: <https://django-extra-views.readthedocs.io/en/latest/index.html>

    Python3, Django, HTML5, CSS3, JavaScript

## For Developers
   ```bash
   $  pip install -r reqirements_dev.txt
   ```

### Tests
   ```bash
   $ pytest
   ```
or
   ```bash
   $ tox
   ```

### Code Style / Linting
   ```bash
   $ isort
   $ black
   $ flake8
   ```

### Versioning
 * [Semantic Versioning](https://semver.org/)
   ```bash
   $ bumpver show
   ```

### Docs
 * [Sphinx](https://www.sphinx-doc.org/en/master/) + [MyST parser](https://myst-parser.readthedocs.io/en/latest/intro.html)
 * [Read The Docs](https://readthedocs.org/projects/django-fmft/)

### Build / Deploy Automation
 * [invoke](https://www.pyinvoke.org/)
   ```bash
   $ invoke -l
   ```
 * [GitHub Actions](https://docs.github.com/en/actions) (see [.github/workflows](https://github.com/powderflask/django-fmft/tree/master/.github/workflows))
 * [GitHub Webhooks](https://docs.github.com/en/webhooks)  (see [settings/hooks](https://github.com/powderflask/django-fmft/settings/hooks))

### TODO
My wish list...
 * write test for case where form field is not included in table
   E.g. as when DELETE field not included in export table
