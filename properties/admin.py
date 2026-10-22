
from django.contrib import admin
from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "bhk",
        "property_type",
        "location",
        "price",
        "garden",
        "parking_spaces",
    )
    search_fields = ("title", "location", "property_type")
    list_filter = ("property_type", "location", "garden")
