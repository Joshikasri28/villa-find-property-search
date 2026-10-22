
from django.db import models


class Property(models.Model):
    title = models.CharField(max_length=200)
    bhk = models.PositiveIntegerField()
    property_type = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    garden = models.BooleanField(default=False)
    parking_spaces = models.PositiveIntegerField(default=0)
    amenities = models.TextField(blank=True)

    def __str__(self):
        return self.title
