from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, SalesRecord
from .views import handle_sales_record

@receiver(post_save, sender=Order)
def record_sale(sender, instance, created, **kwargs):
    if not created:  # Ensure this only runs on update
        if instance.order_status == 'Order Completed' and instance.payment_completed:
            sale_date = instance.created_at.date()  # Extract the date from the Order's created_at field
            for order_item in instance.order_items.all():  # Adjust based on your related_name setup
                handle_sales_record(order_item, instance.vendor, sale_date)
