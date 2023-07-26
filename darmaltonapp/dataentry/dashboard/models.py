from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.http import HttpRequest
# from ckeditor.fields import richtextfield
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, F
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from decimal import Decimal, ROUND_DOWN
from django.utils.translation import gettext_lazy as _
import random
import string

def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))


def user_directory_path(instance, filename):
    return 'users/avatars/{0}/{1}'.format(instance.user.id, filename)


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_directory_path, default='user/avatar.png')
    # Add fields specific for user types
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default="moderator")

    # Password reset token field
    password_reset_token = models.CharField(max_length=32, default=generate_token, editable=False)

    def __str__(self):
        return self.user.username
    


@ receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)



class Company(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    description = models.TextField(max_length=150)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE , null=True)
    def __str__(self):
        return self.name


class CompanyLog(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    edited_at = models.DateTimeField(default=timezone.now)
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Company: {self.company.name}, Edited at: {self.edited_at}, Edited by: {self.edited_by.username}"




class MedicalType(models.Model):
    name = models.CharField(max_length=20, unique=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    added_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class MedicalTypeLog(models.Model):
    name = models.ForeignKey(MedicalType, on_delete=models.CASCADE)
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    edited_on = models.DateTimeField(default=timezone.now)



class Medicine(models.Model):
    class Meta:
        verbose_name = _('Medicine')  # Use gettext_lazy to translate the model name
    name = models.CharField(max_length=100)
    type = models.ForeignKey(MedicalType, on_delete=models.CASCADE)
    buy_price = models.DecimalField(max_digits=10, decimal_places=2)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2)
    exp_date = models.DateField()
    mfg_date = models.DateField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    description = models.TextField()
    in_stock_total = models.IntegerField()
    qty_in_strip = models.IntegerField()
    added_on = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE , null=True)
    edit_logs = models.ManyToManyField('MedicineEditLog', related_name='medicines', blank=True,)


    def save(self, *args, **kwargs):
        if self.in_stock_total < 0:
            raise ValidationError("Stock quantity cannot be less than 0.")
        # Set the added_by field to the current logged-in user
        if not self.pk and not self.added_by:
            raise ValueError("The 'added_by' field must be set before saving the object.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    def get_display_name(self):
        # Logic to determine the display name
        return f"Medicine - {self.name}"
    
    def save(self, *args, **kwargs):
        if self.in_stock_total < 0:
            raise ValidationError("Stock quantity cannot be less than 0.")
        # Set the added_by field to the current logged-in user
        if not self.pk:
            # Set the time zone explicitly before saving the object
            self.added_on = timezone.now()
        if not self.pk and not self.added_by:
            raise ValueError("The 'added_by' field must be set before saving the object.")


        
        super().save(*args, **kwargs)

    def can_sell(self):
        return self.in_stock_total > 0
        
class MedicineEditLog(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    edited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    edited_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.medicine} edited by {self.edited_by} at {self.edited_at}"


class Customer(models.Model):
    class Meta:
        verbose_name = _('Customer')  # Use gettext_lazy to translate the model name
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact = models.CharField(max_length=20)
    email = models.CharField(max_length=100)
    added_on = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Set the added_by field to the current logged-in user
        if not self.pk and not self.added_by:
            raise ValueError("The 'added_by' field must be set before saving the object.")
        super().save(*args, **kwargs)


class InvoiceRequest(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('cash', 'Cash'),
        ('pay_later', 'Pay Later'),
        ('split', 'Split')
    )

    customer = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    request_date = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default="cash", blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    cash_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    pay_later_payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)

    
   
        
       
        
        
        
            
        
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate custom invoice number
            last_invoice = InvoiceRequest.objects.order_by('-id').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            self.invoice_number = 'INV{:04d}'.format(new_number)


         # Set the added_by field to the current logged-in user
        if not self.pk and not self.added_by:
            raise ValueError("The 'added_by' field must be set before saving the object.")



        # Calculate total amount based on related InvoiceItems
        if self.total_amount > 0:
            total_amount = self.invoiceitem_set.aggregate(sum_total=Sum(F('sub_total')))['sum_total']
            if total_amount:
                self.total_amount = total_amount
            else:
                self.total_amount = 0

        # Update payment amounts based on payment method
        if self.payment_method == 'cash':
            self.cash_payment_amount = self.total_amount
            self.pay_later_payment_amount = 0
            self.split_payment_amount1 = 0
            self.split_payment_amount2 = 0
        elif self.payment_method == 'pay_later':
            self.cash_payment_amount = 0
            self.pay_later_payment_amount = self.total_amount
            self.split_payment_amount1 = 0
            self.split_payment_amount2 = 0
            
        elif self.payment_method == 'split':
            # If both cash_payment_amount and pay_later_payment_amount are entered by the user
            # Use the custom amounts provided by the user for split_payment_amount1 and split_payment_amount2
            if self.cash_payment_amount and self.pay_later_payment_amount:
                total_cash_and_pay_later = self.cash_payment_amount + self.pay_later_payment_amount

                if total_cash_and_pay_later != self.total_amount:
                    # Adjust the amounts to ensure they add up to the total_amount_after_discount
                    ratio = self.total_amount / total_cash_and_pay_later
                    self.cash_payment_amount *= ratio
                    self.pay_later_payment_amount *= ratio

                self.split_payment_amount1 = self.cash_payment_amount
                self.split_payment_amount2 = self.pay_later_payment_amount

            # If cash_payment_amount or pay_later_payment_amount is not provided by the user
            # Split the remaining amount equally between cash and pay later
            else:
                split_amount = self.total_amount / 2
                self.split_payment_amount1 = split_amount
                self.split_payment_amount2 = split_amount


        super().save(*args, **kwargs)
        
        



    def update_total_amount(self):
        # Calculate total amount based on related InvoiceItems' sub_total field
        total_amount = self.invoiceitem_set.aggregate(sum_total=Sum('sub_total'))['sum_total'] or 0

        # Update the total_amount field in the InvoiceRequest model
        self.total_amount = total_amount
        self.save()
    
    def __str__(self):
        return self.invoice_number


class InvoiceItem(models.Model):
    invoice  = models.ForeignKey(InvoiceRequest, on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    sub_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # New field for sub_total
    added_on = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        # Calculate and update the sub_total field before saving
        self.sub_total = self.total_price - (self.discount * self.quantity)
        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.invoice)
    
    def delete(self, *args, **kwargs):
        # Update the medicine stock when deleting the invoice item
        self.medicine.in_stock_total += self.quantity
        self.medicine.save()
        super().delete(*args, **kwargs)
    
@receiver(post_save, sender=InvoiceItem)
@receiver(post_delete, sender=InvoiceItem)
def update_invoice_total_amount(sender, instance, **kwargs):
    instance.invoice.update_total_amount()