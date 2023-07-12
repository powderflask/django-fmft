# Installation


## Stable release

From PyPI using pip.
```bash
$ pip install django_fmft
```
*This is the preferred method to install Django Filtered Model Formset Tables,
as it will always install the most recent stable release.*

---
## From sources

The sources for Django Filtered Model Formset Tables can be downloaded from the `Github repo`.

You can either clone the [public repository](https://github.com/powderflask/django-fmft):
```bash
$ git clone git://github.com/powderflask/django-fmft
```
Or download the [*tarball*](https://github.com/powderflask/django-fmft/tarball/master):
```bash
$ curl -OJL https://github.com/powderflask/django-fmft/tarball/master
```
Once you have a copy of the source, you can install it with:
```bash
$ pip install {PATH-TO-PACKAGE-DIRECTORY}
```
---
Once installed, add `django-fmft` to your `INSTALLED_APPS`.
```python
INSTALLED_APPS = [
    ...
    'django_fmft',
    ...
]
```

