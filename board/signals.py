import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

logger = logging.getLogger()  # root logger

@receiver(post_save, sender=Order)
def order_created_notification(sender, instance, created, **kwargs):
    if created:
        logger.info(
            "NEW ORDER: product=%s customer=%s email=%s qty=%s",
            instance.product.name,
            instance.customer_name,
            instance.customer_email,
            instance.quantity,
        )
