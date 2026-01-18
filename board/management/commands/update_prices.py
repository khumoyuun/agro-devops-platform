from decimal import Decimal
from django.core.management.base import BaseCommand
from board.models import Product, PriceHistory

class Command(BaseCommand):
    help = "Update product prices by percentage (e.g. 5 for +5%, -5 for -5%)"

    def add_arguments(self, parser):
        parser.add_argument("percent", type=float)

    def handle(self, *args, **options):
        percent = Decimal(str(options["percent"])) / Decimal("100")

        for p in Product.objects.all():
            old = p.price
            new = (old * (Decimal("1") + percent)).quantize(Decimal("0.01"))
            if new != old:
                PriceHistory.objects.create(product=p, old_price=old, new_price=new)
                p.price = new
                p.save(update_fields=["price", "updated_at"])
                self.stdout.write(self.style.SUCCESS(f"{p.name}: {old} -> {new}"))

        self.stdout.write(self.style.SUCCESS("Done."))
