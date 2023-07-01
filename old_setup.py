#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["Django>=3.2", "django-tables2", "django-filter", "django-extra-views"]

test_requirements = []

setup(
    author="Joseph Fall",
    author_email="powderflask@gmail.com",
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    description="Class-based Views that integrate django-filters and django-tables2 with model formsets.",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="Django Filtered Model Formset Tabular Class-based Views django-filter django-tables",
    name="django-fmft",
    packages=find_packages(include=["fmft", "fmft.*"]),
    test_suite="fmft_tests",
    tests_require=test_requirements,
    url="https://github.com/powderflask/django-fmft",
    version="0.1.0",
    zip_safe=False,
)
