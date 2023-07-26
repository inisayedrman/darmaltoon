from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import models
from .models import InvoiceItem, InvoiceRequest

@receiver([post_save, post_delete], sender=InvoiceItem)
def update_medicine_stock(sender, instance, **kwargs):
    total_quantity = sender.objects.filter(medicine=instance.medicine).aggregate(total_quantity=models.Sum('quantity'))['total_quantity']
    if total_quantity is None:
        total_quantity = 0

    print("Medicine Stock Quantity Before Update:", instance.medicine.in_stock_total)
    print("Total Quantity:", total_quantity)

    # Update the medicine stock
    instance.medicine.in_stock_total = instance.medicine.in_stock_total - total_quantity
    instance.medicine.save()

    print("Medicine Stock Quantity After Update:", instance.medicine.in_stock_total)

