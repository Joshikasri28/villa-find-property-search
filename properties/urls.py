
from django.urls import path
from . import views

urlpatterns = [
    path("", views.property_search, name="property_search"),
]
