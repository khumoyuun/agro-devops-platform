from django.test import TestCase
from .models import Product

class ProductModelTest(TestCase):
    def test_product_str(self):
        p = Product.objects.create(name="Potato", quantity=1, unit="kg", price="1000.00")
        self.assertEqual(str(p), "Potato")
