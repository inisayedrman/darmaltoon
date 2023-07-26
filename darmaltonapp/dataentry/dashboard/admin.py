from django.contrib import admin
from . import models
from django import forms
from django.contrib.auth import get_user_model
from .models import Medicine, MedicineEditLog, InvoiceRequest, InvoiceItem
from django.contrib.admin.models import LogEntry
admin.site.register(LogEntry)
from django.forms import inlineformset_factory
from .forms import InvoiceItemForm


# Register your models here.

admin.site.register(models.Profile)
admin.site.register(models.Company)
admin.site.register(models.Medicine)
admin.site.register(models.Customer)
admin.site.register(models.MedicineEditLog)
admin.site.register(models.InvoiceRequest)
admin.site.register(models.InvoiceItem)
admin.site.register(models.MedicalType)
admin.site.site_header= "Darmaltoon Admin Panel"
admin.site.site_title = "Darmaltoon"


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        fields = ['name', 'type', 'buy_price', 'sell_price', 'exp_date', 'mfg_date', 'company', 'description', 'in_stock_total', 'qty_in_strip', 'added_by']
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['added_by'].initial = self.fields['added_by'].initial or self.request.user

class MedicineAdmin(admin.ModelAdmin):
    form = MedicineForm

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.save()
    def save_model(self, request, obj, form, change):
        if not obj.added_by:
            obj.added_by = request.user
        obj.save()

        if change:
            edit_log = MedicineEditLog.objects.create(
                medicine=obj,
                edited_by=request.user
            )
            obj.edit_logs.add(edit_log)
        else:
            edit_log = MedicineEditLog.objects.create(
                medicine=obj,
                edited_by=request.user
            )
            obj.edit_logs.add(edit_log)

admin.site.unregister(Medicine)
admin.site.register(Medicine, MedicineAdmin)

admin.site.unregister(InvoiceRequest)
class InvoiceRequestAdmin(admin.ModelAdmin):
    readonly_fields = ('invoice_number',)

    def get_readonly_fields(self, request, obj=None):
        # Make invoice_number read-only for existing objects
        if obj:
            return self.readonly_fields + ('customer', 'request_date', 'added_by')
        return self.readonly_fields

admin.site.register(InvoiceRequest, InvoiceRequestAdmin)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    form = InvoiceItemForm
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['medicine'].queryset = Medicine.objects.filter(stock__gt=0)
        return formset

class InvoiceRequestAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline]


InvoiceItemFormSet = inlineformset_factory(
    InvoiceRequest,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=1,
    can_delete=True,
)