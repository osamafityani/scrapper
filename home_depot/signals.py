from datetime import timedelta

from django.db.models.signals import post_save, post_delete
from .models import Product
from django.core.mail import send_mail
from scraper import settings


def update_product(sender, instance, created, **kwargs):
    product = instance

    if not created and product.last_price is not None:

        if 1 - (product.current_price - product.last_price) / product.current_price < 0.5:
            subject = 'check Product'
            message = f'check this product {product.link}\nlast price was: {product.last_price} and now price is {product.current_price}'
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                ['malek315@gmail.com'],
                fail_silently=False,
            )


post_save.connect(update_product, sender=Product)
