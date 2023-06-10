"""
Utilities for integrating tables that render formsets.
    Core Challenge:
        - Filter, ModelFormset, and Table all need to share the same queryset
        - Tables need special logic to render the form elements,
            and need the formset available at construct any "extra form" rows.
        - Formset data needs to be the [paged] table_data.
        Chicken meet Egg.

    Solution:
        - Subclass "normal" Table class by overriding form field Columns & adding DELETE column
        - Construct table with queryset as usual, and optionally paginate
        - Construct formset from table.paginated_rows.data, ensuring formset and table share queryset
        - Append pinned rows for any formset.extra_forms
        - Construct a FormAccessor for the formset and retrofit it into the FormFieldColumns in the table.
"""
from __future__ import annotations

from functools import cached_property
from itertools import chain
from typing import Callable, Iterable, Type

import django.forms
import django_tables2 as tables
from django.forms.formsets import DELETION_FIELD_NAME
from django.template import Context, Template
from django.template.loader import get_template

FormMap = Callable[[object], django.forms.Form]


# Queryset: get the paged data used by a bound table


def get_table_queryset(table):
    """If the table is paginated, the formset queryset is current page only, otherwise for all table rows."""
    try:
        return (
            table.page.object_list.data if hasattr(table, "page") else table.data.data
        )
        # return table.paginated_rows.data   # Maybe a better idea?
    except AttributeError:
        return None


# Table / Column configurations derived from a formset


def get_extra_columns(formset):
    """Return a list of 2-tuples suitable for Table(..., extra_columns) for extra columns needed for given formset"""
    return (
        [
            (
                DELETION_FIELD_NAME,
                tables.Column(verbose_name="Delete", orderable=False, empty_values=()),
            )
        ]
        if formset.can_delete
        else []
    )


def get_formset_table_kwargs(formset, **kwargs):
    """Add table kwargs required to accommodate the formset"""
    extra_columns = dict(get_extra_columns(formset)) | dict(
        kwargs.get("extra_columns", [])
    )
    kwargs["extra_columns"] = tuple(extra_columns.items())
    return kwargs


def add_extra_forms(formset, table):
    """Add formset.extra_forms as pinned_rows at the bottom of the table."""
    pinned_data = table.rows.pinned_data
    bottom = pinned_data.get("bottom", []) or []
    extra_forms = [f.instance for f in formset.extra_forms]
    pinned_data["bottom"] = list(bottom) + extra_forms
    # HACK: this statement uses table.rows internal API :-(
    table.rows.pinned_data = pinned_data


def set_table_forms(formset, table):
    """Hack the formset forms into any FormFieldsColumns in the table.
    This is the core black hackery in FMFT - at least it is contained to code defined in this module.
    Tightly Coupled to the `forms` attribute in FormFieldsColumn
    Caution: this mutates table.columns.column - only apply this to a dynamically generated Table class!
    """
    form_accessor = FormAccessor(formset)
    for bound_column in (
        c for c in table.columns if isinstance(c.column, FormFieldsColumn)
    ):
        bound_column.column.forms = form_accessor


class FormAccessor:
    """
    A simple API for accessing the forms & fields in a modelformset, indexed by the form.instance
    """

    def __init__(self, formset):
        """formset is a bound modelformset instance, bound to a queryset"""
        self.formset = formset
        self.sample_form = formset[0] if len(formset) else formset.empty_form

    def __getitem__(self, instance):
        """Get the form for a specific instance (or index) in the formset queryset"""
        try:
            return (
                self.formset[instance]
                if isinstance(instance, int)
                else self.form_map[id(instance)]
            )
        except KeyError:  # let IndexError pass to flag end of iter
            raise KeyError(
                "Formset does not have a form for the given record - probably a buggered pk in form data."
            )

    def __call__(self, instance):
        """return the Form for the given instance (or index).
        :param instance: a record with an assoiciated form in self.formset or an int index into self.formset
        Raises KeyError not instance in self.form_map
        """
        return self[instance]

    def __len__(self):
        return len(self.form_map)

    @cached_property
    def form_map(self):
        """A dict mapping model id(instance) to the related form in formset - treat as READ-ONLY"""
        return {id(form.instance): form for form in self.formset}

    @property
    def fields(self):
        """Return a generator of the names of all form fields"""
        return (name for name in self.sample_form.fields.keys())

    @property
    def visible_fields(self):
        """Return a generator of the names of all visible form fields"""
        return (f.name for f in self.sample_form.visible_fields())

    @property
    def hidden_fields(self):
        """Return a generator of the names of all hidden form fields"""
        return (name for name in set(self.fields) - set(self.visible_fields))


# Table Columns


class ExtensibleTemplateColumn(tables.TemplateColumn):
    """Adds ability to dynamically extend render context for TemplateColumn"""

    # TODO: contribute this back to django-tables2 in PR
    #      minor re-factor to factor out get_row_context, does not change API or behaviour at all
    def get_row_context(self, record, table, value, bound_column, bound_row):
        """Return a dict of context for given record"""
        context = {
            "default": bound_column.default,
            "column": bound_column,
            "record": record,
            "value": value,
            "row_counter": bound_row.row_counter,
        }
        context.update(self.extra_context)
        return context

    def render(self, record, table, value, bound_column, **kwargs):
        """A copy of TemplateColumn.render with get_row_context factored out make it more extensible"""
        context = getattr(table, "context", Context())
        additional_context = self.get_row_context(
            record, table, value, bound_column, kwargs["bound_row"]
        )
        with context.update(additional_context):
            if self.template_code:
                return Template(self.template_code).render(context)
            else:
                return get_template(self.template_name).render(context.flatten())


class FormFieldsColumn(ExtensibleTemplateColumn):
    """A Column that renders its contents as a form field - for very simple use-cases, this might do.
    Given the template requires a bound form field, the formset usually needs be constructed ahead of table...
    but for Table features like paging and sorting to work, formset needs to be constructed from table data...
    yet, to supply the `fields` context, need the formset constructed - chicken meet egg
    Use get_table and get_formset to do this bit of black-hackery for you.
    This class is coupled to some private API details about table Columns.
    """

    def __init__(
        self,
        forms: FormMap,
        form_fields: Iterable["str"] = None,
        template_code: str = None,
        template_name: str = "fmft/form_fields.html",
        extra_context: dict = None,
        **extra,
    ):
        """Provide a callable that returns the Form for a given object, so form fields can be passed in template context
        :param forms: a Callable that takes a record as input, return the Form to use to collect/edit that record
        :param form_fields: a tuple of form field names to render in column or None to render the accessor form field
        """
        super().__init__(
            template_code=template_code,
            template_name=template_name,
            extra_context=extra_context,
            **extra,
        )
        self.link = False  # sorry, you just can't linkify a form field.
        self.forms = forms
        self.form_fields = form_fields

    def get_row_context(self, record, table, value, bound_column, bound_row):
        """Add `fields` to context - a tuple of form fields to render in this column for given record"""
        context = super().get_row_context(record, table, value, bound_column, bound_row)
        form = self.forms(record)
        fields = (bound_column.name,) if self.form_fields is None else self.form_fields
        context["fields"] = tuple(form[f] for f in fields)
        return context

    def value(self, record, value):
        """Just the value Ma'am"""
        return value

    @classmethod
    def from_column(
        cls,
        forms: FormMap,
        other: tables.Column,
        form_fields: Iterable["str"] = None,
        **kwargs,
    ):
        """Return a FormFieldsColumn that is otherwise configured the same as other"""
        config = dict(
            verbose_name=other.verbose_name,
            accessor=str(other.accessor),
            default=other._default,  # HACK - access to table protected member
            visible=other.visible,
            orderable=other.orderable,
            attrs=other.attrs,
            order_by=None
            if other.order_by is None
            else tuple(other.order_by),  # Coupling to table internal API
            # empty_values=(),  # Don't "inherit" from other column - empty form fields should still be rendered
            localize=other.localize,
            footer=other._footer,  # HACK - access to table protected member
            exclude_from_export=other.exclude_from_export,
            linkify=False,  # Always disable linkify
            initial_sort_descending=other.initial_sort_descending,
        )
        config.update(**kwargs)
        return cls(forms=forms, form_fields=form_fields, **config)


def get_table_class(
    base: Type[tables.Table],
    extra_columns: Iterable[tuple[str, tables.Column]],
    forms: FormAccessor,
) -> type:
    """Return a subclass of base Table class, adding extra_columns
    and overriding forms' visible field columns with FormFieldColumns
    """
    table_columns = dict(extra_columns) | base.base_columns
    visible_column_fields = tuple(
        name for name in forms.visible_fields if name in table_columns
    )

    attrs = {}
    hidden_fields = False
    for name, column in chain(base.base_columns.items(), extra_columns):
        if name in visible_column_fields:
            fields = (
                tuple(chain(forms.hidden_fields, (name,)))
                if not hidden_fields
                else None
            )
            attrs[name] = FormFieldsColumn.from_column(forms, column, fields)
            hidden_fields = True
    if hasattr(base, "Meta"):
        attrs["Meta"] = type("Meta", (base.Meta,), {})
    return type(f"FormFields{base.__name__}", (base,), attrs)


def get_table(
    queryset,
    base_class: Type[tables.Table],
    table_kwargs: dict,
    formset_class,
    formset_kwargs: dict,
) -> tables.Table:
    """Return a table object that will play together nicely with the given formset.
      - adds a Table mixins to handle "extra" forms and "Delete" column, as needed
      - overrides columns defined by form fields with FormFieldColumn
    Note: the matching formset should be created with get_formset to finish stitching the forms themselves into table
    """
    # an empty FormAccessor - we don't have the actual forms until the formset is constructed.
    formset_kwargs["queryset"] = queryset.none()
    form_accessor = FormAccessor(formset_class(**formset_kwargs))

    # add table configuration needed to accomodate formset
    table_kwargs = get_formset_table_kwargs(formset_class, **table_kwargs)
    extra_columns = table_kwargs.pop(
        "extra_columns", []
    )  # we'll add 'em directly to the Table class

    # create a FormFieldsTable subclass, replacing all form field Columns with FormFieldColumns, et voila
    table_class = get_table_class(base_class, extra_columns, form_accessor)
    return table_class(data=queryset, **table_kwargs)


def get_formset(table: tables.Table, formset_class, formset_kwargs: dict):
    """Return a formset instance populated with the table's (paginated) queryset.
    - adds "extra" forms as pinned_rows at bottom of table;
    - hacks 'forms' into all FormFieldColumns in the table;
    """
    formset_kwargs["queryset"] = get_table_queryset(table)
    formset = formset_class(**formset_kwargs)
    # hack the formset forms into the table
    set_table_forms(formset, table)
    add_extra_forms(formset, table)
    return formset


def get_formset_table(
    queryset, formset_class, formset_kwargs, table_class, table_kwargs, paginate=None
):
    """
    Return an integrated table, formset pair that play together nicely.
    :param paginate: dict of kwargs to pass through to table.paginate
    Shortcut for building the table, pagination, and formset together, mainly intended for testing.
    """
    # Step 1: build a form-ready table subclass based on the formset and instantiate the table
    table = get_table(
        queryset, table_class, table_kwargs, formset_class, formset_kwargs
    )
    if paginate:
        table.paginate(**paginate)

    # Step 2: build the formset using the table's data and stitch the forms back into the table
    formset = get_formset(table, formset_class, formset_kwargs)

    return formset, table
