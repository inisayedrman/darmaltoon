

from django.urls import path
from .views import *
from django.conf.urls.i18n import i18n_patterns
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('' , dashboard, name="dashboard"),
    path('user/profile', uprofile, name="profile"),
    path('user/login', CustomLoginView.as_view(), name="login"),
    path('user/logout', user_logout, name="logout"),
    path('user/forget/password', forgot_password, name="forget"),
    path('user/reset/password', reset_password, name="resetpassword"),
    path('user/confirm/identity', confirm_change_password, name="confirmpassword"),
    path('user/change/password', changepassword, name="changepassword"),
    path('user/signup', signup, name="signup"),
    path('users/details', userdetails, name="usersdetails"),
    path('users/update/<int:record_id>/', update_user, name="updateuserdata"),
    path('users/delete/<int:user_id>/', delete_user, name="deleteuser"),
    path('users/admins', admindetails, name="admindetails"),
    path('users/moderators', moddetails, name="moddetails"),
    path('404', logged_in_404, name="logged_in_404"),
    path('error', logged_out_404, name="logged_out_404"),
    path('medicine/stock/list', viewmedicine, name="medicinelist"),
    path('medicine/stock/update/<int:record_id>/', update_medicine, name="updatemedicine"),
    path('medicine/stock/update/history', update_medicine_history, name="medicinehistory"),
    path('medicine/stock/month', viewmedicine_thismonth, name="medicinemonth"),
    path('medicine/add', addmedicine, name="addmedicine"),
    path('medicaltype/update/<int:record_id>/', update_medical_type, name="updatemedicaltype"),
    path('medicaltype/view', view_medical_type, name="viewmedicaltype"),
    path('medicaltype/add', add_medical_type, name="addmedicaltype"),
    path('manufacturer/add', add_company, name="addcompany"),
    path('manufacturer/list', viewcompany, name="viewcompany"),
    path('manufacturer/update/<int:record_id>/', update_company, name="updatecompany"),
    path('manufacturer/stock/update/history', update_company_history, name="companylog"),
    path('medicine/expired', expiredmidicine, name="expired"),
    path('medicine/expire/soon', expiresoon, name="soon"),
    path('medicine/expire/thismonth', expirethismonth, name="thismonth"),
    path('customers/details', customers, name="customers"),
    path('customers/add', addcustomer, name="addcustomer"),
    path('customers/update/<int:record_id>/', updatecustomer, name="updatecustomer"),
    path('customers/delete/<int:record_id>/', deletecustomer, name="deletecustomer"),
    path('invoice/request', customer_invoice_request, name="invoicerequest"),
    path('invoice/add/items', add_invoice_items, name="additemstoinvoice"),
    path('invoice/item/delete/<int:invoice_item_id>/', delete_invoice_item, name='delete_invoice_item'),
    path('invoice/delete/<int:invoice_id>/', delete_invoice, name='delete_invoice'),
    path('invoice/all', viewinvoices, name="viewinvoices"),
    path('invoice/current/month', viewinvoicesmonth, name="viewinvoicesmonth"),
    path('invoice/current/year', viewinvoicesyear, name="viewinvoicesyear"),
    path('invoice/edit/<int:invoice_id>/', edit_invoice, name="invoiceedit"),
    path('invoice/items/<int:invoice_id>/', view_invoice_items, name="invoiceitems"),
    path('invoice/pdf/<int:invoice_id>/', invoicetopdf, name="invoicepdf"),
    path('invoice/pdf/generate/<int:invoice_id>/', generate_pdf_invoice, name='invoice_pdf'),
    path('invoice/print/<int:invoice_id>/', print_invoice, name='print_invoice'),
    path('invoice/download/<int:invoice_id>/', download_invoice, name='download_invoice'),
    path('medicine/sold', soldmedicine, name="soldmedicine"),
    path('actions/record', action_records_view, name="actionrecord"),
    path('medicine_price/', get_medicine_price, name='medicine_price'),
    path('search/result', global_search, name='globalsearch'),
    path('generate/report', generate_report, name='generate_report'),

]


