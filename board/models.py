from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=120)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20, default="kg")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
