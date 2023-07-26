from django import forms
from .models import *
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.db import transaction




def user_directory_path(instance, filename):
    return 'users/avatars/{0}/{1}'.format(instance.user.id, filename)



class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)


class RegistrationForm(forms.ModelForm):
    repeat_password = forms.CharField(widget=forms.PasswordInput())
    avatar = forms.ImageField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'repeat_password', 'avatar']

    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
    )
    user_type = forms.TypedChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        repeat_password = cleaned_data.get('repeat_password')

        if password and repeat_password and password != repeat_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['repeat_password'])
        if commit:
            user.save()

            # Create or update the associated profile
            profile, created = Profile.objects.get_or_create(user=user)
            profile.avatar = self.cleaned_data['avatar']
            profile.user_type = self.cleaned_data['user_type']
            profile.save()

        return user

     


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user_type']









class MedicalTypeForm(forms.ModelForm):
    class Meta:
        model = MedicalType
        exclude = ['added_by', 'added_on']  # Exclude the 'added_by' and 'added_on' fields

class EditMedicalTypeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        edited_by = kwargs.pop('edited_by', None)  # Retrieve the 'edited_by' parameter
        super().__init__(*args, **kwargs)

        if edited_by:
            self.instance.edited_by = edited_by

    class Meta:
        model = MedicalType
        fields = ['name']
        exclude = ['added_by']

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.pk is None:
            # If the instance is being created, set the added_by value
            if hasattr(self.instance, 'edited_by'):
                instance.added_by = self.instance.edited_by
        else:
            # If the instance is being edited, preserve the added_by value
            instance.added_by = MedicalType.objects.get(pk=instance.pk).added_by

        if commit:
            instance.save()

            if instance.pk is not None:
                # If the instance is being edited, update the edit log entry
                edit_log = MedicalTypeLog.objects.create(
                    name=instance,
                    edited_by=self.instance.edited_by,
                    edited_on=timezone.now()
                )

        return instance





class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'

class EditCompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'contact', 'email', 'description']


class AddMedicineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.all()

    class Meta:
        model = Medicine
        fields = '__all__'
        exclude = ['edit_logs']  # Exclude the edit_logs field
        widgets = {
            'name': forms.TextInput(attrs={'name': 'name', 'class': 'form-control form-control-user', 'placeholder': 'Medicine Name'}),
            'type': forms.TextInput(attrs={'name': 'type', 'class': 'form-control form-control-user', 'placeholder': 'Medical Type'}),
            'buy_price': forms.TextInput(attrs={'name': 'buy_price', 'class': 'form-control form-control-user', 'placeholder': 'Buy Price'}),
            'sell_price': forms.TextInput(attrs={'name': 'sell_price', 'class': 'form-control form-control-user', 'placeholder': 'Sell Price'}),
            'exp_date': forms.DateInput(attrs={'name': 'exp_date', 'class': 'form-control form-control-user', 'placeholder': 'Expiration Date'}),
            'mfg_date': forms.DateInput(attrs={'name': 'mfg_date', 'class': 'form-control form-control-user', 'placeholder': 'Manufacture Date'}),
            'company': forms.Select(attrs={'name': 'company', 'class': 'form-select form-control', 'placeholder': 'Company'}),
            'description': forms.TextInput(attrs={'name': 'description', 'class': 'form-control form-control-user', 'placeholder': 'Description'}),
            'in_stock_total': forms.TextInput(attrs={'name': 'in_stock_total', 'class': 'form-control form-control-user', 'placeholder': 'In Stock Total'}),
            'qty_in_strip': forms.TextInput(attrs={'name': 'qty_in_strip', 'class': 'form-control form-control-user', 'placeholder': 'Quantity In Strip'}),
        }

    def save(self, commit=True, added_by=None):
        instance = super().save(commit=False)
        if added_by:
            instance.added_by = added_by  # Set the added_by value
        instance.added_on = timezone.now()  # Set the added_on value
        if commit:
            instance.save()
            self.save_m2m()  # Save the many-to-many fields, if any
        return instance
    

class EditMedicineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        edited_by = kwargs.pop('edited_by', None)
        super().__init__(*args, **kwargs)
        self.fields['company'].queryset = Company.objects.all()
        self.edited_by = edited_by  # Store the 'edited_by' value

    class Meta:
        model = Medicine
        fields = '__all__'
        exclude = ['added_by', 'added_on']

    def save(self, commit=True):
        instance = super().save(commit=False)

        if instance.pk is None:
            # If the instance is being created, set the added_by value
            if self.edited_by:
                instance.added_by = self.edited_by
        else:
            # If the instance is being edited, preserve the added_by value
            instance.added_by = Medicine.objects.get(pk=instance.pk).added_by

        if commit:
            instance.save()

            if instance.pk is not None:
                # If the instance is being edited, update the edit log entry
                edit_log = MedicineEditLog.objects.create(
                    medicine=instance,
                    edited_by=self.edited_by,
                    edited_at=timezone.now()
                )

        return instance










    

class AddCustomerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(AddCustomerForm, self).__init__(*args, **kwargs)

    class Meta:
        model = Customer
        fields = ['name', 'address', 'contact', 'email']

    def save(self, commit=True):
        instance = super(AddCustomerForm, self).save(commit=False)
        if self.request:
            instance.added_by = self.request.user
            instance.added_on = timezone.now()
        if commit:
            instance.save()
        return instance

class UpdateCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        exclude = ['added_on', 'added_by']

class CustomPasswordChangeForm(PasswordChangeForm):
    new_password1 = forms.CharField(label='New Password', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Repeat New Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if not new_password1:
            self.add_error('new_password1', 'Please enter a new password.')

        if not new_password2:
            self.add_error('new_password2', 'Please enter the new password again.')

        if new_password1 and new_password2 and new_password1 != new_password2:
            self.add_error('new_password2', 'The two password fields must match.')

        return cleaned_data







class CustomerInvoiceRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = InvoiceRequest
        exclude = ['invoice_number']
        fields = ['customer', 'payment_method', 'total_amount', 'cash_payment_amount', 'pay_later_payment_amount']
        widgets = {
            'invoice_number': forms.TextInput(),
        }

    def save(self, commit=True, request=None):
        instance = super(CustomerInvoiceRequestForm, self).save(commit=False)
        
        # Set the request_date to the current date
        instance.request_date = timezone.now().date()
        
        # Set the added_by field to the current logged in user
        if request and request.user.is_authenticated:
            instance.added_by = request.user
        else:
            instance.added_by = None
        
        # Generate the invoice number
        with transaction.atomic():
            last_invoice = InvoiceRequest.objects.select_for_update().filter(customer=instance.customer).order_by('-id').first()
            if last_invoice:
                last_number = int(last_invoice.invoice_number[3:])
                new_number = last_number + 1
            else:
                new_number = 1
            instance.invoice_number = 'INV{:04d}'.format(new_number)
            
            if commit:
                instance.save()
        return instance
    


class InvoiceItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = InvoiceItem
        fields = ['invoice', 'medicine', 'quantity', 'discount', 'unit_price']

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        medicine = cleaned_data.get('medicine')

        if quantity and medicine:
            if quantity > medicine.in_stock_total:
                raise ValidationError('Requested quantity exceeds available stock.')

        return cleaned_data
    

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.request:
            instance.added_by = self.request.user
        if commit:
            instance.save()
        return instance


class InvoiceRequestForm(forms.ModelForm):
    class Meta:
        model = InvoiceRequest
        fields = ['total_amount', 'payment_method', 'cash_payment_amount', 'pay_later_payment_amount']
        
        
class GlobalSearchForm(forms.Form):
    search_query = forms.CharField(max_length=100)