from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, SalesRecord

@receiver(post_save, sender=Order)
def record_sale(sender, instance, created, **kwargs):
    if not created:  # Ensure this only runs on update
        if instance.order_status == 'Order Completed' and instance.payment_completed:
            for order_item in instance.cart.cartitems.all():  # I'm assuming you have a related_name set or default for CartItems in Cart model
                product = order_item.product
                vendor = product.vendor

                # Create a new SalesRecord
                SalesRecord.objects.create(
                    product=product,
                    vendor=vendor,
                    quantity_sold=order_item.quantity,
                    sale_date=instance.created_at
                )
