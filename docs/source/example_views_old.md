# Views Quick Examples

[//]: # (TODO: Improve examples)

## FilteredTableView
Define a `FilteredTableView`, a view which combines
`django-tables2` and `django-filters` to provide a
filtered table view with a customizable base queryset.

```python
from fmft.views import FilteredTableView

class SimpleFilteredTableView(FilteredTableView):
    template_name = "fmft/tests/filtered_table.html"
    filterset_class = ItemFilterSet
    table_class = ItemTable
```

---
## FilteredModelFormsetView
Define a `FilteredModelFormsetView`, a view which
combines a filtered object list with a model formset,
allowing for the construction, validation,
and saving of the formset using the filtered data.
```python
from fmft.views import FilteredModelFormsetView

class SimpleFilteredModelFormsetView(FilteredModelFormsetView):
    template_name = "fmft/tests/filtered_model_formset.html"
    model = Item
    filterset_class = ItemFilterSet
    form_class = ItemForm
```

---
## ModelFormsetTableView
Define a `ModelFormsetTableView`, a view which combines
a ModelFormset with a table to display and interact
with model instances, allowing customization of form
fields and table layout in code rather than templates.
```python
from fmft.views import ModelFormsetTableView

class SimpleModelFormsetTableView(ModelFormsetTableView):
    template_name = "fmft/tests/model_formset_table.html"
    model = Item
    table_class = ItemTable
    form_class = ItemForm

```

---
## FilteredModelFormsetTableView
Define a `FilteredModelFormsetTableView`, a view which
combines a filtered model formset with a table, allowing
customization of form fields, table columns, and queryset,
and supports data export using an ExportMixin.
```python
from fmft.views import FilteredModelFormsetTableView

class SimpleFilteredModelFormsetTableView(FilteredModelFormsetTableView):
    template_name = "fmft/tests/filtered_model_formset_table.html"
    model = Item
    filterset_class = ItemFilterSet
    table_class = ItemTable
    form_class = ItemForm

```
