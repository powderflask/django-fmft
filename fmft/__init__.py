"""Top-level package for Django Filtred-Model-Formset-Table """

__author__ = """Joseph Fall"""
__email__ = "powderflask@gmail.com"
__version__ = "0.1.0"

from .utils import add_form_kwargs
from .views import (
    FilteredModelFormsetTableView,
    FilteredModelFormsetView,
    FilteredTableView,
    ModelFormsetTableView,
)

__all__ = [
    "FilteredModelFormsetTableView",
    "FilteredModelFormsetView",
    "FilteredTableView",
    "ModelFormsetTableView",
    "add_form_kwargs",
]
