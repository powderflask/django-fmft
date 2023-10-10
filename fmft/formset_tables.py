"""
Utilities for integrating tables that render formsets.
    Core Challenge:
        - Filter, ModelFormset, and Table all need to share the same queryset
        - Tables need special logic to render the form elements
            and need the formset available to construct any "extra form" rows.
        - Formset data needs to be the [paged] table_data.
        Chicken meet Egg.

    Solution:
        - Subclass "normal" Table class by overriding form field Columns & adding
          DELETE column
        - Construct table with queryset as usual, and optionally paginate
        - Construct formset from table.paginated_rows.data, ensuring formset and table
          share queryset
        - Append pinned rows for any formset.extra_forms
        - Construct a FormAccessor for the formset and retrofit it into the
          FormFieldColumns in the table.
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


class BaseModelFormSet(django.forms.models.BaseModelFormSet):
    """Extends BaseModelFormSet to add non-form error report suited to formsets displayed in a table"""
    def all_non_field_errors(self):
        error_list = self.non_form_errors().copy()
        for form in self:
            error_list.extend(form.non_field_errors())
        return error_list


# Queryset: get the paged data used by a bound table


def get_table_queryset(table):
    """
    Get the queryset used by a bound table.

    If the table is paginated, the formset queryset is for the current page only.
    Otherwise, it includes all table rows.

    Args:
        table (Table): The table object.

    Returns:
        QuerySet or None: The queryset used by the table, or None if not available.
    """
    try:
        return (
            table.page.object_list.data if hasattr(table, "page") else table.data.data
        )
        # return table.paginated_rows.data   # Maybe a better idea?
    except AttributeError:
        return None


# Table / Column configurations derived from a formset
def get_extra_columns(formset):
    """
    Return a list of 2-tuples suitable for Table(..., extra_columns) for extra columns
    needed for the given formset.

    Args:
        formset (FormSet): The formset object.

    Returns:
        List: A list of 2-tuples, where each tuple contains the column name and its
        corresponding Table Column.
    """
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
    """
    Add table kwargs required to accommodate the formset.

    Args:
        formset (FormSet): The formset object.
        **kwargs: Additional keyword arguments for the table.

    Returns:
        dict: A dictionary containing the modified keyword arguments for the table.
    """
    extra_columns = {
        **dict(get_extra_columns(formset)),
        **dict(kwargs.get("extra_columns", [])),
    }
    kwargs["extra_columns"] = tuple(extra_columns.items())
    return kwargs


def add_extra_forms(formset, table):
    """
    Add formset.extra_forms as pinned_rows at the bottom of the table.

    Args:
        formset (FormSet): The formset object.
        table (Table): The table object.
    """
    pinned_data = table.rows.pinned_data
    bottom = pinned_data.get("bottom", []) or []
    extra_forms = [f.instance for f in formset.extra_forms]
    pinned_data["bottom"] = list(bottom) + extra_forms
    # HACK: this statement uses table.rows internal API :-(
    table.rows.pinned_data = pinned_data


def set_table_forms(formset, table):
    """
    Hack the formset forms into any FormFieldsColumns in the table.

    This is the core black hackery in FMFT - at least it is contained to code defined in
    this module.
    Tightly Coupled to the `forms` attribute in FormFieldsColumn.
    Caution: this mutates table.columns.column - only apply this to a dynamically
    generated Table class!

    Args:
        formset (FormSet): The formset object.
        table (Table): The table object.
    """
    form_accessor = FormAccessor(formset)
    for bound_column in (
        c for c in table.columns if isinstance(c.column, FormFieldsColumn)
    ):
        bound_column.column.forms = form_accessor


class FormAccessor:
    """
    A simple API for accessing the forms & fields in a modelformset, indexed by the
    form.instance
    """

    def __init__(self, formset):
        """
        Initialize the FormAccessor with the given formsetformset.

        Args:
            formset (FormSet): The formset object.
        """
        self.formset = formset
        self.sample_form = formset[0] if len(formset) else formset.empty_form

    def __getitem__(self, instance):
        """
        Get the form for a specific instance (or index) in the formset queryset.

        Args:
            instance (int or object): The index or instance of the form in the formset.

        Returns:
            Form: The form object.

        Raises:
            KeyError: If the form for the given instance is not found in the formset.
        """
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
        """
        Return the form for the given instance (or index).

        Args:
            instance (int or object): The index or instance of the form in the formset.

        Returns:
            Form: The form object.

        Raises:
            KeyError: If the form for the given instance is not found in the formset.
        """
        return self[instance]

    def __len__(self):
        """
        Return the number of forms in the formset.

        Returns:
            int: The number of forms in the formset.
        """
        return len(self.form_map)

    @cached_property
    def form_map(self):
        """
        Return a dictionary mapping model id(instance) to the related form in the formset.

        Returns:
            dict: A dictionary mapping model ids to form objects.
        """
        return {id(form.instance): form for form in self.formset}

    @property
    def fields(self):
        """
        Return a generator of the names of all form fields.

        Yields:
            str: The name of a form field.
        """
        return (name for name in self.sample_form.fields.keys())

    @property
    def visible_fields(self):
        """
        Return a generator of the names of all visible form fields.

        Yields:
            str: The name of a visible form field.
        """
        return (f.name for f in self.sample_form.visible_fields())

    @property
    def hidden_fields(self):
        """
        Return a generator of the names of all hidden form fields.

        Yields:
            str: The name of a hidden form field.
        """
        return (name for name in set(self.fields) - set(self.visible_fields))


# Table Columns


class ExtensibleTemplateColumn(tables.TemplateColumn):
    """Adds ability to dynamically extend render context for TemplateColumn"""

    # TODO: contribute this back to django-tables2 in PR -- minor re-factor to factor
    #       out get_row_context, does not change API or behaviour at all
    def get_row_context(self, record, table, value, bound_column, bound_row):
        """
        Return a dictionary of context for the given record.

        Args:
            record (object): The record object.
            table (Table): The table object.
            value: The column value.
            bound_column (BoundColumn): The bound column object.
            bound_row (BoundRow): The bound row object.

        Returns:
            dict: The context dictionary.
        """
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
        """
        Render the column value for the given record.

        Args:
            record (object: The record object.
            table (Table): The table object.
            value: The column value.
            bound_column (BoundColumn): The bound column object.

        Returns:
            str: The rendered column value.
        """
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
    """A Column that renders its contents as a form field - for very simple use-cases,
    this might do.

    Given the template requires a bound form field, the formset usually needs be
    constructed ahead of table... but for Table features like paging and sorting to
    work, formset needs to be constructed from table data... yet, to supply the `fields`
    context, the formset needs to be constructed - chicken meet egg

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
        """
        Initialize the FormFieldsColumn.

        Args:
            forms (callable): A callable that returns the Form for a given object.
            form_fields (Iterable[str], optional): A tuple of form field names to render
                in the column. Defaults to None.
            template_code (str, optional): The template code for rendering the column.
                Defaults to None.
            template_name (str, optional): The template name for rendering the column.
                Defaults to "fmft/form_fields.html".
            extra_context (dict, optional): Additional context to pass to the template.
                Defaults to None.
            **extra: Additional keyword arguments to pass to the parent class.
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
        """Add `fields` to context - a tuple of form fields to render in this column for
        a given record

        Args:
            record (object): The record object.
            table (Table): The table object.
            value: The column value.
            bound_column (BoundColumn): The bound column object.
            bound_row (BoundRow): The bound row object.

        Returns:
            dict: The context dictionary.
        """
        context = super().get_row_context(record, table, value, bound_column, bound_row)
        form = self.forms(record)
        fields = (bound_column.name,) if self.form_fields is None else self.form_fields
        context["fields"] = tuple(form[f] for f in fields)
        return context

    def value(self, record, value):
        """Just the value Ma'am

        Args:
            record (object): The record object.
            value: The column value.

        Returns:
            str: The column value.
        """
        return value

    @classmethod
    def from_column(
        cls,
        forms: FormMap,
        other: tables.Column,
        form_fields: Iterable["str"] = None,
        **kwargs,
    ):
        """
        Create a FormFieldsColumn that is configured the same as other

        Args:
            forms (callable): A callable that returns the Form for a given object.
            other (Column): Another column to base the FormFieldsColumn on.
            form_fields (Iterable[str], optional): A tuple of form field names to render
            in the column. Defaults to None.
            **kwargs: Additional keyword arguments to pass to the FormFieldsColumn
            constructor.

        Returns:
            FormFieldsColumn: The created FormFieldsColumn object.
        """
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
            # empty_values=(),  # Don't "inherit" from other column - empty form fields
            # should still be rendered
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
    """Return a subclass of the base Table class, adding extra_columns
    and overriding forms' visible field columns with FormFieldColumns.

    Args:
        base (Type[tables.Table]): The base Table class.
        extra_columns (Iterable[Tuple[str, tables.Column]]): Extra columns to add.
        forms (FormAccessor): Form accessor object.

    Returns:
        Type[tables.Table]: A subclass of the base Table class.

    """
    table_columns = {
        **dict(extra_columns),
        **base.base_columns,
    }
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

    Note: the matching formset should be created with get_formset to finish stitching
          the forms themselves into the table.

    Args:
        queryset: The queryset for the table object.
        base_class (Type[tables.Table]): The base Table class.
        table_kwargs (Dict[str, Any]): Additional keyword arguments for the table.
        formset_class: The formset class.
        formset_kwargs (Dict[str, Any]): Additional keyword arguments for the formset.

    Returns:
        tables.Table: A table object.

    """
    # an empty FormAccessor - we don't have the actual forms until the formset is
    # constructed.
    formset_kwargs["queryset"] = queryset.none()
    form_accessor = FormAccessor(formset_class(**formset_kwargs))

    # add table configuration needed to accomodate formset
    table_kwargs = get_formset_table_kwargs(formset_class, **table_kwargs)
    extra_columns = table_kwargs.pop(
        "extra_columns", []
    )  # we'll add 'em directly to the Table class

    # create a FormFieldsTable subclass, replacing all form field Columns with
    # FormFieldColumns, et voila
    table_class = get_table_class(base_class, extra_columns, form_accessor)
    return table_class(data=queryset, **table_kwargs)


def get_formset(table: tables.Table, formset_class, formset_kwargs: dict):
    """
    Return a formset instance populated with the table's (paginated) queryset.
    - adds "extra" forms as pinned_rows at the bottom of the table;
    - hacks 'forms' into all FormFieldColumns in the table.

    Args:
        table (tables.Table): The table object.
        formset_class: The formset class.
        formset_kwargs (Dict[str, Any]): Additional keyword arguments for the formset.

    Returns:
        formset_class: A formset instance populated with the table's queryset.

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

    Args:
        queryset: The queryset for the table object.
        formset_class: The formset class.
        formset_kwargs: Additional keyword arguments for the formset.
        table_class: The table class.
        table_kwargs: Additional keyword arguments for the table.
        paginate (Optional[Dict[str, Any]]): Optional pagination arguments for the table.

    Returns:
        Tuple[formset_class, tables.Table]: An integrated formset and table pair.

    Shortcut for building the table, pagination, and formset together, mainly intended
    for testing.

    """
    # Step 1: build_old a form-ready table subclass based on the formset and instantiate
    # the table
    table = get_table(
        queryset, table_class, table_kwargs, formset_class, formset_kwargs
    )
    if paginate:
        table.paginate(**paginate)

    # Step 2: build_old the formset using the table's data and stitch the forms back
    # into the table
    formset = get_formset(table, formset_class, formset_kwargs)

    return formset, table
