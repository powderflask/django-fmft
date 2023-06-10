"""
Tables used for testing
"""
import django_tables2 as tables

from .models import Item


class ItemTable(tables.Table):
    flag = tables.BooleanColumn()
    order = tables.Column(
        linkify=True
    )  # Note: when order is rendered as form field, linkify is disabled.
    date_placed = tables.DateColumn()

    class Meta:
        model = Item
        fields = ("flag", "name", "sku", "price", "order", "status", "date_placed")
