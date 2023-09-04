"""
    Test suite for Filtered-ModelFormset-Table (FMFT) package.
"""
import random
import uuid
from decimal import Decimal as D

import django_tables2 as tables
from django.forms import modelformset_factory
from django.test import RequestFactory, TestCase

from demo.forms import InlineItemForm, ItemForm
from demo.models import STATUS_CHOICES, Item, Order
from demo.tables import ItemTable
from demo.views import (
    DeletableModelFormsetTableView,
    ExtrasModelFormsetTableView,
    PaginatedFilteredModelFormsetTableView,
    PaginatedModelFormsetTableView,
    SimpleFilteredModelFormsetTableView,
    SimpleFilteredModelFormsetView,
    SimpleFilteredTableView,
    SimpleModelFormsetTableView,
)
from fmft.formset_tables import (
    FormAccessor,
    get_formset_table,
    get_formset_table_kwargs,
    get_table_queryset,
)

# Rendered field content have are dependent on form_field.html

DELETE_INPUT_TAG = (
    '<input type="checkbox" name="form-{n}-DELETE" id="id_form-{n}-DELETE">'
)
STATUS_SELECT_TAG = """
    <select name="form-{n}-status" id="id_form-{n}-status">
      <option value="0" {0}>Placed</option>
      <option value="1" {1}>Charged</option>
      <option value="2" {2}>Shipped</option>
      <option value="3" {3}>Cancelled</option>
    </select>
"""


def get_status_tag(instance, n):
    """Return formatted STATUS_SELECT_TAG for form n with selected value matching instance"""
    selected = ("selected" * (instance.status == i) for i in range(4))
    return STATUS_SELECT_TAG.format(*selected, n=n)


###############
# Test Fixtures
###############


def get_item(i=0, **kwargs):
    """Return an unsaved Item instance"""
    order = kwargs.get("order", None) or Order.objects.create(
        name="Dummy Order"
    )  # avoid creating extra Orders
    kwargs.setdefault("name", f"Item {i}")
    kwargs.setdefault("sku", str(uuid.uuid4())[:13])
    kwargs.setdefault("price", D(f"{i}.99"))
    kwargs.setdefault("order", order)
    kwargs.setdefault("status", random.choice([c for c, v in STATUS_CHOICES]))
    return Item(**kwargs)


def create_item(i=0, **kwargs):
    """Create and return persistent Item instance"""
    item = get_item(i, **kwargs)
    item.save()
    return item


def create_item_fixture(n, order_name="Dummy Order"):
    """Create and return n persistent Items"""
    order = Order.objects.create(name=order_name)
    items = [get_item(i, order=order) for i in range(n)]
    Item.objects.bulk_create(items)
    return items


def create_testing_data_fixture():
    """Create a random set of orders and related items, primarily used to load DB for
    interactive testing"""
    for n, name in zip((11, 5, 3, 7), ("Order A", "Order B", "Order C")):
        create_item_fixture(n, name)


def get_request(path="/some/path/"):
    return RequestFactory().get(path)


def get_table_row(table, index):
    """Fetch a table row, agnostic to whether it is a "real" row or a "pinned" row"""
    assert 0 <= index <= len(table.paginated_rows)
    return list(table.paginated_rows)[index]


class BaseViewTest(TestCase):
    n_records = 10

    def setUp(self):
        create_item_fixture(self.n_records)


############
# Test Views
############


class FilteredTableViewTests(BaseViewTest):
    view = SimpleFilteredTableView

    def test_integrity(self):
        """Test the view responds"""
        # Use this syntax for class-based views.md.
        response = self.view.as_view()(get_request())
        self.assertEqual(response.status_code, 200)

    def test_shared_qs(self):
        """Check that table and filter share same qs - won't be true for paginated or
        sorted tables!"""
        response = self.view.as_view()(get_request())
        self.assertIn("table", response.context_data)
        self.assertIn("filter", response.context_data)
        table = response.context_data["table"]
        filter = response.context_data["filter"]
        self.assertEqual(table.data.data, filter.qs)


class FilteredModelFormsetViewTests(BaseViewTest):
    view = SimpleFilteredModelFormsetView

    def test_integrity(self):
        """Test the view responds"""
        # Use this syntax for class-based views.md.
        response = self.view.as_view()(get_request())
        self.assertEqual(response.status_code, 200)

    def test_shared_qs(self):
        """Check that filter and formset share same qs"""
        response = self.view.as_view()(get_request())
        self.assertIn("formset", response.context_data)
        self.assertIn("filter", response.context_data)
        formset = response.context_data["formset"]
        filter = response.context_data["filter"]
        self.assertEqual(formset.queryset, filter.qs)

    def test_filtered_table(self):
        create_item(i=101, name="match")
        create_item(i=102, name="match")
        response = self.view.as_view()(get_request("/path/?name=match"))
        formset = response.context_data["formset"]
        filter = response.context_data["filter"]
        self.assertEqual(len(filter.qs), 2)
        self.assertEqual(len(formset), 2)
        self.assertEqual(set(filter.qs), set(form.instance for form in formset))


class ModelFormsetTableViewTests(BaseViewTest):
    view = SimpleModelFormsetTableView

    def test_integrity(self):
        """Test the view responds"""
        # Use this syntax for class-based views.md.
        response = self.view.as_view()(get_request())
        self.assertEqual(response.status_code, 200)

    def test_shared_qs(self):
        """Check that table and formset share same qs - won't be true for paginated or
        sorted tables!"""
        response = self.view.as_view()(get_request())
        self.assertIn("formset", response.context_data)
        self.assertIn("table", response.context_data)
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        self.assertEqual(formset.queryset, table.data.data)

    def test_table_class(self):
        """the table class used in the view is generated dynamically - check that went
        well"""
        response = self.view.as_view()(get_request())
        the_table = response.context_data["table"]
        table_class = type(the_table)
        self.assertEqual(
            table_class.__name__, f"FormFields{self.view.table_class.__name__}"
        )
        self.assertTrue(issubclass(table_class, self.view.table_class))
        self.assertSetEqual(
            set(table_class._meta.fields), set(self.view.table_class._meta.fields)
        )

    def test_render_form_fields(self):
        response = self.view.as_view()(get_request())
        table = response.context_data["table"]
        instance = table.data[3]
        status_tag = get_status_tag(instance, n=3)
        self.assertContains(response, status_tag, html=True)
        self.assertInHTML(status_tag, table.rows[3].get_cell("status"))
        self.assertEqual(
            table.rows[3].get_cell_value("status"),
            instance.get_status_display(),
        )

    def test_sorted_table(self):
        response = self.view.as_view()(get_request("/path/?sort=-price"))
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        instances = list(row.record for row in table.rows)
        neighbours = zip((i.price for i in instances), (i.price for i in instances[1:]))
        self.assertTrue(all(i > j for i, j in neighbours))
        self.assertSetEqual(set(form.instance for form in formset), set(instances))


class ExtrasModelFormsetTableViewTests(BaseViewTest):
    view = ExtrasModelFormsetTableView
    extra = view.factory_kwargs["extra"]

    def test_extras_table(self):
        """Test that formset tables can handle multiple extras"""
        response = self.view.as_view()(get_request())
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        self.assertEqual(formset.extra, self.extra)
        self.assertEqual(len(formset), self.n_records + self.extra)
        self.assertEqual(len(formset), len(table.rows))
        self.assertEqual(
            len(table.rows), self.n_records + self.extra
        )  # 'pinned' row added to table.
        self.assertEqual(
            table.rows.pinned_data["bottom"],
            [form.instance for form in formset.extra_forms],
        )  # with the extra instance


class ModelFormsetTableViewWithLinkifiedRelationTests(BaseViewTest):
    """the trick is instance on "extra" forms may have no relation - verify that doesn't
    break linkify"""

    class ModelFormsetTableInlineFormsView(SimpleModelFormsetTableView):
        form_class = InlineItemForm
        factory_kwargs = dict(extra=2, can_delete=True)

    view = ModelFormsetTableInlineFormsView
    extra = view.factory_kwargs["extra"]

    def test_linkify_relation(self):
        response = self.view.as_view()(get_request())
        table = response.context_data["table"]
        self.assertEqual(len(table.rows), self.n_records + self.extra)
        self.assertContains(response, '<a href="/inlines/1/">Dummy Order</a>')


class DeletableModelFormsetTableViewTests(BaseViewTest):
    view = DeletableModelFormsetTableView

    def test_deletable_table(self):
        response = self.view.as_view()(get_request())
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        self.assertTrue(formset.can_delete)
        self.assertTrue("DELETE" in formset[0].fields)
        self.assertTrue("DELETE" in [c.name for c in table.columns])
        delete_input = DELETE_INPUT_TAG.format(n=0)
        self.assertInHTML(
            delete_input,
            table.rows[0].get_cell("DELETE"),
        )
        response.render()
        self.assertContains(response, delete_input, html=True)


class PaginatedModelFormsetTableViewTests(BaseViewTest):
    view = PaginatedModelFormsetTableView

    def test_paginated_table(self):
        response = self.view.as_view()(get_request())
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        self.assertEqual(len(table.paginated_rows), self.view.paginate_by)
        self.assertEqual(len(formset), self.view.paginate_by)
        self.assertEqual(
            list(form.instance for form in formset),
            list(row.record for row in table.paginated_rows),
        )

    def test_sorted_paginated_table(self):
        response = self.view.as_view()(get_request("/path/?sort=-sku"))
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        self.assertEqual(len(table.paginated_rows), self.view.paginate_by)
        self.assertEqual(len(formset), self.view.paginate_by)
        instances = list(row.record for row in table.paginated_rows)
        neighbours = zip((i.sku for i in instances), (i.sku for i in instances[1:]))
        self.assertTrue(all(i > j for i, j in neighbours))
        self.assertEqual(list(form.instance for form in formset), instances)


class FilteredModelFormsetTableViewTests(BaseViewTest):
    view = SimpleFilteredModelFormsetTableView

    def test_integrity(self):
        """Test the view responds"""
        # Use this syntax for class-based views.md.
        response = self.view.as_view()(get_request())
        self.assertEqual(response.status_code, 200)

    def test_shared_qs(self):
        """Check that table, filter, and formset all share same qs - won't be true for
        paginated or sorted tables!"""
        response = self.view.as_view()(get_request())
        self.assertIn("formset", response.context_data)
        self.assertIn("table", response.context_data)
        self.assertIn("filter", response.context_data)
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        filter = response.context_data["filter"]
        self.assertEqual(formset.queryset, table.data.data)
        self.assertEqual(set(table.data.data), set(filter.qs))

    def test_filtered_table(self):
        n_matches = 3
        for i in range(n_matches):
            create_item(i=100 + i, name="match")

        response = self.view.as_view()(get_request("/path/?name=match"))
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        filter = response.context_data["filter"]
        self.assertEqual(len(filter.qs), n_matches)
        self.assertEqual(len(table.data.data), n_matches)
        self.assertEqual(len(formset), n_matches)
        self.assertEqual(set(filter.qs), set(form.instance for form in formset))
        self.assertEqual(set(filter.qs), set(row.record for row in table.rows))

    def test_render_form_fields(self):
        response = self.view.as_view()(get_request())
        table = response.context_data["table"]
        instance = table.data[0]
        status_tag = get_status_tag(instance, n=0)
        self.assertContains(response, status_tag, html=True)
        self.assertInHTML(status_tag, table.rows[0].get_cell("status"))

        self.assertEqual(
            table.rows[0].get_cell_value("status"), instance.get_status_display()
        )

    def test_sorted_table(self):
        response = self.view.as_view()(get_request("/path/?sort=-price"))
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        filter = response.context_data["filter"]
        instances = list(row.record for row in table.rows)
        neighbours = zip((i.price for i in instances), (i.price for i in instances[1:]))
        self.assertTrue(all(i > j for i, j in neighbours))
        self.assertSetEqual(set(form.instance for form in formset), set(instances))
        self.assertEqual(
            set(filter.qs), set(instances)
        )  # filter.qs is unsorted - same qs, different sort order.


class PaginatedFilteredModelFormsetTableViewTests(BaseViewTest):
    view = PaginatedFilteredModelFormsetTableView

    def test_paginated_table(self):
        response = self.view.as_view()(get_request())
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        filter = response.context_data["filter"]
        instances = list(row.record for row in table.paginated_rows)
        self.assertSetEqual(set(form.instance for form in formset), set(instances))
        # paginated instances are first N of filter queryset
        N = self.view.paginate_by
        self.assertEqual(list(filter.qs[:N]), instances)

    def test_paginated_filtered_table(self):
        n_matches = 5
        for i in range(n_matches):
            create_item(i=100 + i, name="match")
        response = self.view.as_view()(get_request("/path/?name=match"))
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        filter = response.context_data["filter"]
        self.assertEqual(len(filter.qs), n_matches)
        self.assertEqual(len(table.paginated_rows), self.view.paginate_by)
        self.assertEqual(len(formset), self.view.paginate_by)
        instances = list(row.record for row in table.paginated_rows)
        self.assertEqual(list(form.instance for form in formset), instances)
        # paginated instances are first N of filtered instances
        N = self.view.paginate_by
        self.assertEqual(list(filter.qs[:N]), instances)

    def test_sorted_paginated_filtered_table(self):
        n_matches = 3
        for i in range(n_matches):
            create_item(i=100 + i, name="match")
        response = self.view.as_view()(get_request("/path/?sort=-price&name=match"))
        formset = response.context_data["formset"]
        table = response.context_data["table"]
        filter = response.context_data["filter"]
        self.assertEqual(len(filter.qs), n_matches)
        self.assertEqual(len(table.paginated_rows), self.view.paginate_by)
        self.assertEqual(len(formset), self.view.paginate_by)
        instances = list(row.record for row in table.paginated_rows)
        neighbours = zip((i.price for i in instances), (i.price for i in instances[1:]))
        self.assertTrue(all(i > j for i, j in neighbours))
        self.assertEqual(list(form.instance for form in formset), instances)
        # paginated instances are first N of simiilarly sorted filtered instances
        N = self.view.paginate_by
        self.assertEqual(list(filter.qs.order_by("-price")[:N]), instances)


##############################
# Test formset_table functions
##############################


class FormsetTableTestMixin(TestCase):
    n_forms = 8
    extra_forms = 2

    def setUp(self):
        create_item_fixture(self.n_forms)

        self.qs = Item.objects.all().order_by(
            "name",
        )
        self.form_class = ItemForm
        self.formset_class = modelformset_factory(
            Item, form=ItemForm, can_delete=True, extra=self.extra_forms
        )


class EmptyFormsetTableTests(FormsetTableTestMixin):
    n_forms = 0
    extra_forms = 2

    def setUp(self):
        super().setUp()
        self.formset, self.table = get_formset_table(
            self.qs, self.formset_class, {}, ItemTable, {}
        )

    def test_render_form_fields(self):
        row = get_table_row(self.table, 1)
        status = row.get_cell("status")
        status_tag = STATUS_SELECT_TAG.format("selected", "", "", "", n=1)
        self.assertInHTML(status_tag, status)
        delete = row.get_cell("DELETE")
        delete_input = DELETE_INPUT_TAG.format(n=1)
        self.assertInHTML(delete_input, delete)

    def test_paginated_extra_rows(self):
        self.assertEqual(len(self.qs), 0)
        self.assertEqual(len(self.table.paginated_rows), self.extra_forms)
        self.assertEqual(len(self.formset), len(self.table.paginated_rows))

    def test_fields_rendered(self):
        request = get_request()
        rendered = self.table.as_html(request)
        status_tag = STATUS_SELECT_TAG.format("selected", "", "", "", n=1)
        self.assertInHTML(status_tag, rendered)
        delete_input = DELETE_INPUT_TAG.format(n=1)
        self.assertInHTML(delete_input, rendered)


class FormsetTableTests(FormsetTableTestMixin):
    n_forms = 8

    def setUp(self):
        super().setUp()
        self.formset, self.table = get_formset_table(
            self.qs, self.formset_class, {}, ItemTable, {}
        )

    def test_shared_qs(self):
        """Check that table and formset share same qs"""
        self.assertEqual(
            self.formset.queryset, self.table.data.data
        )  # only true for unsorted, non-paginated
        self.assertSetEqual(
            {item for item in self.formset.queryset},
            {item for item in self.table.paginated_rows.data},
        )

    def test_shared_forms(self):
        table_forms = self.table.columns["status"].column.forms
        self.assertSetEqual({f for f in self.formset}, {f for f in table_forms})
        self.assertListEqual(
            [f for f in self.formset], [table_forms(f.instance) for f in self.formset]
        )

    def test_render_form_fields(self):
        status = self.table.rows[1].get_cell("status")
        status_tag = get_status_tag(self.table.data[1], n=1)
        self.assertInHTML(status_tag, status)
        delete = self.table.rows[1].get_cell("DELETE")
        delete_input = DELETE_INPUT_TAG.format(n=1)
        self.assertInHTML(delete_input, delete)

    def test_get_table_queryset(self):
        table = ItemTable(data=self.qs)
        self.assertEqual(len(get_table_queryset(table)), self.n_forms)
        table.paginate(per_page=3)
        self.assertEqual(len(get_table_queryset(table)), 3)

    def test_get_formset_table_kwargs(self):
        kwargs = get_formset_table_kwargs(
            self.formset_class,
            other="args",
            extra_columns=[
                ("a", tables.Column()),
            ],
        )
        delete = [t for t in kwargs["extra_columns"] if t[0] == "DELETE"][0]
        self.assertEqual(type(delete), tuple)
        self.assertEqual(len(delete), 2)
        self.assertEqual(type(delete[1]), tables.Column)

    def test_FormAccessor(self):
        formset = self.formset_class(queryset=self.qs)
        forms = FormAccessor(formset)
        self.assertEqual(len(forms), len(formset))
        form = formset[4]
        self.assertEqual(forms[form.instance], form)
        self.assertEqual(forms[1], formset[1])


class TableFormCellTests(FormsetTableTestMixin):
    """Test that form field cells are correctly rendered"""

    n_forms = 8
    per_page = 5

    def setUp(self):
        super().setUp()
        self.formset, self.table = get_formset_table(
            self.qs,
            self.formset_class,
            {},
            ItemTable,
            {},
            paginate=dict(per_page=self.per_page),
        )

    def test_pinned_row_renders(self):
        instance = self.formset[6].instance
        status_tag = STATUS_SELECT_TAG.format("selected", "", "", "", n=6)
        # Pinned rows can't be accessed using indexing via public API, so iterate to it.
        pinned_row = get_table_row(self.table, 6)
        self.assertInHTML(status_tag, pinned_row.get_cell("status"))
        self.assertEqual(
            pinned_row.get_cell_value("status"),
            # self.table.columns["status"].value(value=instance.status, record=instance),
            instance.get_status_display(),
        )

    def test_pk_rendered(self):
        request = get_request()
        pk_input = '<input type="hidden" name="form-1-id" value="2" id="id_form-1-id">'
        self.assertInHTML(pk_input, self.table.as_html(request))

    def test_paginated_extra_rows(self):
        self.assertEqual(
            len(self.table.paginated_rows), self.per_page + self.extra_forms
        )
        self.assertEqual(len(self.formset), len(self.table.paginated_rows))
