# Views Quick Examples

[//]: # (TODO: Improve examples)

## FilteredTableView
Mixes
[FilterView](https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration)
with
[SingleTableMixin](https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators)
for views that Filter tabular data.
```python
from fmft.views import FilteredTableView

class SimpleFilteredTableView(FilteredTableView):
    template_name = "fmft/tests/filtered_table.html"
    filterset_class = ItemFilterSet
    table_class = ItemTable
```

---
## FilteredModelFormsetView
Integrates
[FilterView](https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration)
with
[ModelFormsetView](https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview)
for views that Filter the queryset used by a formset
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
Integrates
[ModelFormsetView](https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview)
with
[SingleTableMixin](https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators)
for views that render a formset in a Table.
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
Integrates
[FilterView](https://django-filter.readthedocs.io/en/stable/guide/usage.html#generic-view-configuration),
[ModelFormsetView](https://django-extra-views.readthedocs.io/en/latest/pages/formset-views.html#modelformsetview)
and
[SingleTableMixin](https://django-tables2.readthedocs.io/en/latest/pages/api-reference.html#views-view-mixins-and-paginators)
for views that Filter the queryset used by a formset and render
the formset in a Table.
```python
from fmft.views import FilteredModelFormsetTableView

class SimpleFilteredModelFormsetTableView(FilteredModelFormsetTableView):
    template_name = "fmft/tests/filtered_model_formset_table.html"
    model = Item
    filterset_class = ItemFilterSet
    table_class = ItemTable
    form_class = ItemForm

```
