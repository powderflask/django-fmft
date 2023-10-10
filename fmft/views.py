"""
Filtered Model Formset Table views.md
    - re-useable integrations of FilterView, ModelFormsetView, and SingleTableMixin
Purpose:
    - sef of abstract class-based views.md that provide a declarative syntax to hide
      the integration details
Core Problem:
    - Filters, ModelFormsets, and Tables all need a queryset
    - in a F-MF-T view, they need to share the same queryset - getting the MRO right
      is essential!
    - Tables need special logic to render a formset, and need the formset available at
      construct any "extra" rows.
    - Formset data need to be the [paged] table_data.  Chicken meet Egg.
"""

import django_filters.views as filters
import django_tables2 as tables
from django.views.generic.list import (
    MultipleObjectMixin,
    MultipleObjectTemplateResponseMixin,
)
from django_tables2 import RequestConfig
from extra_views.formsets import (
    BaseFormSetFactory,
    ModelFormSetMixin,
    ModelFormSetView,
    ProcessFormSetView,
)

from . import formset_tables


class FilteredTableView(tables.SingleTableMixin, filters.FilterView):
    """
    Too easy - this one is batteries included.  Thanks django-tables2 and
    django-filters, you are awesome.

    How does it work:
    - concrete view provides the base queryset
    - FilterView.get() sets self.object_list = a filtered version of the base queryset
    - SingleTableMixin looks for self.object_list, thus loading the filtered queryset
    - Template should render the filterset and the table (see template
      filtered_table.html)

    """

    # Minimal configuration:
    filterset_class = None
    table_class = None
    # queryset, or get_queryset() as defined by MultipleObjectMixin to customize base
    # queryset for filtered data


class FilterViewMixin(filters.FilterMixin, MultipleObjectMixin):
    """
    Logic factored out from BaseFilterView so it can be mixed in, e.g., with a
    modelformset view
    """

    def configure_filterset(self):
        """configure the filterset, and return its object_list"""
        # Code duplicated directly from django_filters.BaseFilterView.get
        filterset_class = self.get_filterset_class()
        self.filterset = self.get_filterset(filterset_class)
        if (
            not self.filterset.is_bound
            or self.filterset.is_valid()
            or not self.get_strict()
        ):
            object_list = self.filterset.qs
        else:
            object_list = self.filterset.queryset.none()
        return object_list

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            filter=self.filterset, object_list=self.object_list, **kwargs
        )


class BaseModelFormSetView(
    MultipleObjectTemplateResponseMixin, ModelFormSetMixin, ProcessFormSetView
):
    """A Base class that emulates formsets.ModelFormSetView, but without its request
    handlers"""
    formset_class = formset_tables.BaseModelFormSet

    pass


class FilteredModelFormsetView(FilterViewMixin, BaseModelFormSetView):
    """
    A Filtered Formset View.
    Not sure how useful this is without a Table, but hey, maybe you just love writing
    table template logic :-P
    Core Problem:
    - need filtered object_list to construct formset, but that logic is buried in
      FilterView.get()

    Solution: re-write .get() / .post() so the two views.md play nicely together, with
    formset.queryset=filterset.qs

    How does it work:
    - FilterViewMixin.configure_filterset duplicates logic from BaseFilterView to
      build_old the object_list
    - custom get(), post() mix that logic in with the get() / post() logic from
      ModelFormSetView to handle constructing, validating, and saving the modelformset

    """

    # Minimal configuration:
    model = None
    filterset_class = None
    form_class = None
    factory_kwargs = dict(extra=0)
    # queryset, or get_queryset() as defined by MultipleObjectMixin to customize base
    # queryset for filtered data

    def get_formset_kwargs(self):
        kwargs = super().get_formset_kwargs()
        kwargs[
            "queryset"
        ] = self.object_list  # use filterset.qs as the formset queryset
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object_list = self.configure_filterset()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object_list = self.configure_filterset()
        return super().post(request, *args, **kwargs)


class BaseModelFormSetSingleTableMixin(BaseFormSetFactory, tables.SingleTableMixin):
    """
    A version of SingleTableMixin that injects the formset into the view's Table class,
    mixed with a BaseFormSetFactory that fetches formset from table rather than
    constructing one itself.
    """

    model = None
    request = None
    formset_class = formset_tables.BaseModelFormSet
    _table = None
    _formset = None

    def get_formset_and_table(self):
        """Table and formset need to be constructed together - formset needs table's qs,
        table needs forms"""
        if not (self._table and self._formset):
            formset_class = self.get_formset()
            formset_kwargs = self.get_formset_kwargs()
            table = formset_tables.get_table(
                self.get_table_data(),
                self.get_table_class(),
                self.get_table_kwargs(),
                formset_class,
                formset_kwargs,
            )
            table = RequestConfig(
                self.request, paginate=self.get_table_pagination(table)
            ).configure(
                table
            )  # duplicates code from SingleTableMixin.get_table

            self._formset = formset_tables.get_formset(
                table, formset_class, formset_kwargs
            )
            self._table = table
        return self._formset, self._table

    @property
    def the_table(self):
        """There should be only one table, one table to rule them all!"""
        _, table = self.get_formset_and_table()
        return table

    def get_table(self, **kwargs):
        """Fake! kwargs are ignored, cached value returned instead"""
        return self.the_table

    @property
    def the_formset(self):
        """Critically, there may only be one formset built with data from the one
        table."""
        formset, _ = self.get_formset_and_table()
        return formset

    def construct_formset(self):
        """Fake! don't construct another formset, just use the one integrated with
        the table."""
        return self.the_formset

    def get_table_data(self):
        """Override to use the view's object_list, which we assume is available,
        from somewhere"""
        # Note: don't use this qs to populate formset - the table further
        #       sorts/paginates this queryset, so essential that the formset uses the
        #       table's modified version.

        # a formset qs must be ordered, and BaseFormSet will add order_by clause if not,
        #  which will crash if the table has already added a pagination slice.
        # Head that off here by preempting that logic on the table's base queryset...
        qs = super().get_table_data()
        if hasattr(qs, "_query") and not qs.ordered:
            qs = qs.order_by(self.model._meta.pk.name)
        return qs


class ModelFormsetTableView(BaseModelFormSetSingleTableMixin, ModelFormSetView):
    """
    A ModelFormset View loaded into a table.
    Mix-and-match form fields with non-form fields and customize layout in code instead
    of in template logic.

    How does it work:
    - form defines which table fields are rendered as form fields, other table columns
      rendered as usual;
    ProcessFormsetView does the heavy lifting in post()

    """

    # Minimal configuration:
    model = None
    table_class = None
    form_class = None
    factory_kwargs = dict(extra=0)
    # queryset, or get_queryset() as defined by MultipleObjectMixin to customize base
    # queryset for filtered data
    # Note: A ModelFormset queryset MUST be ordered;
    #       a default ordering will be applied if it is not.  Recommend: add order_by
    #       clause to view's base queryset.
    # if you want to export data, mixin an ExportMixin as usual.


class FilteredModelFormsetTableView(
    BaseModelFormSetSingleTableMixin, FilteredModelFormsetView
):
    """
    The whole enchilada - A Filtered Model Formset View loaded into a table.
    Mix and match from above to get it all.
    How does it work:
    form defines which table fields are rendered as form fields, other table columns
    rendered as usual;
    ProcessFormsetView does the heavy lifting in post()

    """

    # Minimal configuration:
    model = None
    filterset_class = None
    table_class = None
    form_class = None
    factory_kwargs = dict(extra=0)
    # queryset, or get_queryset() as defined by MultipleObjectMixin to customize base
    # queryset for filtered data
    # Note: A ModelFormset queryset MUST be ordered;
    #       a default ordering will be applied if it is not.  Recommend: add order_by
    #       clause to view's base queryset.
    # if you want to export data, mixin an ExportMixin as usual.
