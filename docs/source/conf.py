# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath("../../"))

django_settings = "demo.settings"

project = "Django Filtered Model Formset Tables"
copyright = "2023, powderflask"
author = "Joseph Fall"

# The short X.Y version.
version = "0.3.3"
# The full version, including alpha/beta/rc tags.
release = "0.3.3"

# The master toctree document.
master_doc = "index"

# The suffix(es) of source filenames.
source_suffix = [".rst", ".md"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinxcontrib_django",
]

templates_path = ["_templates"]
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
