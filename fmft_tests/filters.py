"""
Filters used for testing
"""
import django_filters as filters

from .models import Item


class ItemFilterSet(filters.FilterSet):
    class Meta:
        model = Item
        fields = [
            "name",
            "order",
            "status",
        ]
