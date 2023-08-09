from django.db import models
import uuid


class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    link = models.CharField(max_length=500, null=True, blank=True)
    current_price = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
    last_price = models.DecimalField(max_digits=20, decimal_places=5, null=True, blank=True)
