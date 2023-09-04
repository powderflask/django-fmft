from django.urls import path
from django.views.generic import RedirectView, TemplateView

from .formsets import AddressFormSet
from .views import (
    AddressFormSetView,
    AddressFormSetViewKwargs,
    AddressFormSetViewNamed,
    DeletableModelFormsetTableView,
    EventCalendarView,
    ExtrasModelFormsetTableView,
    FormAndFormSetOverrideView,
    ItemModelFormSetExcludeView,
    ItemModelFormSetView,
    OrderCreateNamedView,
    OrderCreateView,
    OrderItemFormSetView,
    OrderTagsView,
    OrderUpdateView,
    PagedModelFormSetView,
    PaginatedFilteredModelFormsetTableView,
    PaginatedModelFormsetTableView,
    SearchableItemListView,
    SimpleFilteredModelFormsetTableView,
    SimpleFilteredModelFormsetView,
    SimpleFilteredTableView,
    SimpleModelFormsetTableView,
    SortableItemListView,
)

urlpatterns = [
    path("formset/simple/", AddressFormSetView.as_view()),
    path("formset/simple/named/", AddressFormSetViewNamed.as_view()),
    path("formset/simple/kwargs/", AddressFormSetViewKwargs.as_view()),
    path(
        "formset/simple_redirect/",
        AddressFormSetView.as_view(success_url="/formset/simple_redirect/valid/"),
    ),
    path(
        "formset/simple_redirect/valid/",
        TemplateView.as_view(template_name="extra_views/success.html"),
    ),
    path("formset/custom/", AddressFormSetView.as_view(formset_class=AddressFormSet)),
    path("modelformset/simple/", ItemModelFormSetView.as_view()),
    path("modelformset/exclude/", ItemModelFormSetExcludeView.as_view()),
    path("modelformset/custom/", FormAndFormSetOverrideView.as_view()),
    path("modelformset/paged/", PagedModelFormSetView.as_view()),
    path("inlineformset/<int:pk>/", OrderItemFormSetView.as_view()),
    path("inlines/<int:pk>/new/", OrderCreateView.as_view()),
    path("inlines/new/", OrderCreateView.as_view()),
    path("inlines/new/named/", OrderCreateNamedView.as_view()),
    path("inlines/<int:pk>/", OrderUpdateView.as_view()),
    path("genericinlineformset/<int:pk>/", OrderTagsView.as_view()),
    path("sortable/<str:flag>/", SortableItemListView.as_view()),
    path("events/<int:year>/<str:month>/", EventCalendarView.as_view()),
    path("searchable/", SearchableItemListView.as_view()),
    path(
        "searchable/predefined_query/",
        SearchableItemListView.as_view(define_query=True),
    ),
    path("searchable/exact_query/", SearchableItemListView.as_view(exact_query=True)),
    path("searchable/wrong_lookup/", SearchableItemListView.as_view(wrong_lookup=True)),
    # FMFT
    path("", RedirectView.as_view(url="filteredtable/simple/")),
    path("filteredtable/simple/", SimpleFilteredTableView.as_view()),
    path("filteredmodelformset/simple/", SimpleFilteredModelFormsetView.as_view()),
    path("modelformsettable/simple/", SimpleModelFormsetTableView.as_view()),
    path("modelformsettable/deletable/", DeletableModelFormsetTableView.as_view()),
    path("modelformsettable/extra_forms/", ExtrasModelFormsetTableView.as_view()),
    path("modelformsettable/paginated/", PaginatedModelFormsetTableView.as_view()),
    path(
        "filteredmodelformsettable/simple/",
        SimpleFilteredModelFormsetTableView.as_view(),
    ),
    path(
        "filteredmodelformsettable/paginated/",
        PaginatedFilteredModelFormsetTableView.as_view(),
    ),
]
