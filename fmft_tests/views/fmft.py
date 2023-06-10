"""
Filtered ModelFormset Table Views
"""
from fmft import views

from ..filters import ItemFilterSet
from ..forms import InlineItemForm, ItemForm
from ..models import Item
from ..tables import ItemTable


class SimpleFilteredTableView(views.FilteredTableView):
    template_name = "fmft/tests/filtered_table.html"
    filterset_class = ItemFilterSet
    table_class = ItemTable

    table_pagination = False

    def get_table_kwargs(self):
        kwargs = super().get_table_kwargs()
        kwargs[
            "empty_text"
        ] = "No Items were found matching given filter criteria. Revise your filter."
        return kwargs


class SimpleFilteredModelFormsetView(views.FilteredModelFormsetView):
    template_name = "fmft/tests/filtered_model_formset.html"
    model = Item
    filterset_class = ItemFilterSet
    form_class = ItemForm

    table_pagination = False


class SimpleModelFormsetTableView(views.ModelFormsetTableView):
    template_name = "fmft/tests/model_formset_table.html"
    model = Item
    table_class = ItemTable
    form_class = ItemForm

    table_pagination = False


class PaginatedModelFormsetTableView(SimpleModelFormsetTableView):
    table_pagination = None
    paginate_by = 2  # 2 per page


class DeletableModelFormsetTableView(SimpleModelFormsetTableView):
    factory_kwargs = dict(can_delete=True, extra=False)
    form_class = InlineItemForm


class ExtrasModelFormsetTableView(SimpleModelFormsetTableView):
    factory_kwargs = dict(extra=3)


class SimpleFilteredModelFormsetTableView(views.FilteredModelFormsetTableView):
    template_name = "fmft/tests/filtered_model_formset_table.html"
    model = Item
    filterset_class = ItemFilterSet
    table_class = ItemTable
    form_class = ItemForm

    table_pagination = False

    def get_table_kwargs(self):
        kwargs = super().get_table_kwargs()
        kwargs[
            "empty_text"
        ] = "No Items were found matching given filter criteria. Tevise your filter."
        return kwargs


class PaginatedFilteredModelFormsetTableView(SimpleFilteredModelFormsetTableView):
    table_pagination = None
    paginate_by = 2  # 2 per page
