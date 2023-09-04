"""Top-level package for Django Filtered-Model-Formset-Table """

__author__ = """Joseph Fall"""
__email__ = "powderflask@gmail.com"
__version__ = "0.2.0"

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
]
