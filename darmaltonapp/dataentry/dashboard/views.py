from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from .models import *
from django.shortcuts import render
from .decorators import redirect_to_dashboard
from datetime import date
from datetime import datetime, timedelta
from django.db.models import Q
from django.db.models import Sum, F, ExpressionWrapper, IntegerField, Case, When
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test
from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count
from django.db import transaction
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
import xhtml2pdf.pisa as pisa
import tempfile
import os
from django.template.loader import get_template

from django.utils import timezone
from django.db.models.query import QuerySet
from itertools import chain
from django.contrib.auth.forms import PasswordChangeForm
from django.utils.translation import activate
from django.utils.translation import gettext as _
from django.utils.translation import get_language, activate, gettext
from django.utils import translation
from django.forms.models import modelform_factory



user_language = 'en'
translation.activate(user_language)
response = HttpResponse(...)
response.set_cookie(settings.LANGUAGE_COOKIE_NAME, user_language)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)



@csrf_protect
@redirect_to_dashboard
def login_view(request):
    error_message = None
    languages = settings.LANGUAGES

    if request.method == 'GET' and 'lang' in request.GET:
        lang_code = request.GET.get('lang')
        if lang_code in dict(languages):
            translation.activate(lang_code)
            request.session[translation.LANGUAGE_SESSION_KEY] = lang_code
            response = redirect(request.path)
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            return response
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = _('Invalid username or password.')
    else:
        error_message = _('Session expired.')
    context = {
        'error_message' : error_message,
        'languages' : languages,
    }
    return render(request, 'login/index.html', context)
    
@login_required
def user_logout(request):
    
        
    logout(request)
    
        
    request.session.flush()
    response = redirect('/user/login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def count_medicines_current_month():
    current_month = date.today().month
    medicines_count_this_month = Medicine.objects.filter(added_on__month=current_month).count()
    return medicines_count_this_month

# expiration peroid function

def get_expiring_soon_medicines():
    today = datetime.now()
    expiration_limit = today + timedelta(days=180)  # Six months from today
    expired_medicines = get_expired_medicines()
    expiring_this_month = get_expiring_this_month_medicines()
    expiring_soon_medicines = Medicine.objects.filter(exp_date__lte=expiration_limit, exp_date__gte=today).exclude(id__in=expired_medicines).exclude(id__in=expiring_this_month)

    return expiring_soon_medicines

def get_expiring_this_month_medicines():
    today = datetime.now()
    expiration_limit = today + timedelta(days=30)  # 30 days from today
    expired_medicines = get_expired_medicines()
    expiring_this_month_medicines = Medicine.objects.filter(exp_date__lte=expiration_limit, exp_date__gt=today).exclude(id__in=expired_medicines)

    return expiring_this_month_medicines

def get_expired_medicines():
    today = datetime.now()

    expired_medicines = Medicine.objects.filter(exp_date__lt=today)

    return expired_medicines 

# end expiration period function

# thid month recorded
def retrieve_this_month_medicine_records():
    # Get the current month and year from the system date
    today = date.today()
    current_month = today.month
    current_year = today.year

    # Get the first day of the current month
    first_day_of_month = date(current_year, current_month, 1)

    # Get the first day of the next month
    if current_month == 12:
        first_day_of_next_month = date(current_year + 1, 1, 1)
    else:
        first_day_of_next_month = date(current_year, current_month + 1, 1)

    # Query the medicine records added within the current month
    medicine_records = Medicine.objects.filter(
        Q(added_on__gte=first_day_of_month) & Q(added_on__lt=first_day_of_next_month)
    )

    return medicine_records 
# end this month recorded

# total investment
def calculate_total_investment():
    total_investment = Medicine.objects.aggregate(
        total=Sum(ExpressionWrapper(
            F('buy_price') * F('in_stock_total'),
            output_field=IntegerField()
        ))
    )['total']

    if total_investment is None:
        total_investment = 0

    formatted_total_investment = '{:,.2f}'.format(total_investment)  # Format with commas
    return formatted_total_investment
# end total inverstment

def get_medicine_data():
    medicine_added_by_admin = retrieve_medicines().filter(added_by='admin').count()
    medicine_added_by_mod = retrieve_medicines().filter(added_by='moderator').count()

    response = f"{medicine_added_by_admin},{medicine_added_by_mod}"
    return HttpResponse(response, content_type='text/plain')

def recent_actions():
    recent_actions = LogEntry.objects.select_related('content_type', 'user').order_by('-action_time')[:10]
    return {'recent_actions': recent_actions}

def retrieve_medicine_sold():
    sold_items = InvoiceItem.objects.all()
    return sold_items

def retrieve_earnings():
    earnings = InvoiceRequest.objects.aggregate(total_sum=Sum('total_amount'))

    total_sum = earnings['total_sum'] or 0  # If there are no invoices, set the total sum to 0
    return total_sum

# Calculate earnings for the current month
def earnings_this_month():
    current_month = timezone.now().strftime('%Y-%m')
    

    earnings_this_month = InvoiceRequest.objects.filter(
        request_date__startswith=current_month
    ).aggregate(total_sum=Sum('total_amount'))
    total_sum_this_month = earnings_this_month['total_sum'] or 0
    return total_sum_this_month

# Calculate earnings for the current year
def earnings_this_year():
    current_year = timezone.now().year
    earnings_this_year = InvoiceRequest.objects.filter(
        request_date__year=current_year
    ).aggregate(total_sum=Sum('total_amount'))
    total_sum_this_year = earnings_this_year['total_sum'] or 0
    return total_sum_this_year

from django.db.models.functions import TruncMonth


def calculate_earnings_today():
    today = timezone.now().date()
    earnings_today = InvoiceRequest.objects.filter(request_date__date=today).aggregate(total_sum=Sum('total_amount'))
    total_sum_today = earnings_today['total_sum'] or 0
    return total_sum_today


@login_required
def dashboard (request, language_code=None):
    cash_amount = InvoiceRequest.objects.aggregate(total=Sum('cash_payment_amount'))['total'] or 0
    pay_later_amount = InvoiceRequest.objects.aggregate(total=Sum('pay_later_payment_amount'))['total'] or 0
    
    # cash_amount = InvoiceRequest.objects.filter(payment_method='cash').aggregate(total=Sum('cash_payment_amount'))['total'] or 0
    # pay_later_amount = InvoiceRequest.objects.filter(payment_method='pay_later').aggregate(total=Sum('pay_later_payment_amount'))['total'] or 0
    
    
    # split_amount = 0

    # # Calculate split amount based on the specified conditions
    # if InvoiceRequest.objects.filter(payment_method='split').exists():
    #     split_amount = InvoiceRequest.objects.filter(payment_method='split').aggregate(
    #         total=ExpressionWrapper(Sum(F('cash_payment_amount') + F('pay_later_payment_amount')), output_field=models.DecimalField())
    #     )['total'] or 0
    
    # print("Dashboard view called")
    
    user_type = request.user.profile.user_type
    user_count = User.objects.all().count()
    Medicine_count = retrieve_medicines().count()
    Medicine_count_month = count_medicines_current_month()
    admin_count = Profile.objects.filter(user_type='admin').count()
    mod_count = Profile.objects.filter(user_type='moderator').count()
    expiring_soon = get_expiring_soon_medicines().count()
    expiring_this_month = get_expiring_this_month_medicines().count()
    expired = get_expired_medicines().count()
    invoice_count= retrieve_invoices_data().count()
    customer_count= retrieve_customer_data().count()
    medicine_added_by_admin = retrieve_medicines().filter(added_by__profile__user_type='admin').count()
    medicine_added_by_mod = retrieve_medicines().filter(added_by__profile__user_type='moderator').count()
    
    if Medicine_count == 0:
        percentage_admin = 0
        percentage_mod = 0
    else:
        percentage_admin = (medicine_added_by_admin / Medicine_count) * 100
        percentage_mod = (medicine_added_by_mod / Medicine_count) * 100
    
    recorded_this_month = retrieve_this_month_medicine_records().count()
    total_investment = calculate_total_investment()
    sold_items_count = retrieve_medicine_sold().count()
    earnings = retrieve_earnings()
    earnings_monthly = earnings_this_month()
    earnings_anually = earnings_this_year()
    earnings_daily = calculate_earnings_today()



    context = {
        "user_type": user_type,
        "user_count": user_count,
        "admin_count": admin_count,
        "mod_count" : mod_count,
        "Medicine_count" : Medicine_count,
        "Medicine_count_month" : Medicine_count_month,
        "expiring_soon" : expiring_soon,
        "expiring_this_month" : expiring_this_month,
        "expired" : expired,
        "invoice_count" : invoice_count,
        "medicine_added_by_admin" : medicine_added_by_admin,
        "medicine_added_by_mod" : medicine_added_by_mod,
        "recorded_this_month" : recorded_this_month,
        "total_investment" : total_investment,
        "sold_items_count" : sold_items_count,
        "customer_count" : customer_count,
        "earnings" : earnings,
        "earnings_monthly" : earnings_monthly,
        "earnings_anually" : earnings_anually,
        "earnings_daily" : earnings_daily,
        "percentage_admin" : percentage_admin,
        "percentage_mod" : percentage_mod,
        
        'cash_amount': cash_amount,
        'pay_later_amount': pay_later_amount,
    }
    return render(request, 'dashboard/dashboard.html', context)


@user_passes_test(lambda u: u.is_superuser)
def action_records_view(request):
    # Get all action records
    action_records = LogEntry.objects.all()

    for record in action_records:
        content_type = ContentType.objects.get_for_id(record.content_type_id)
        record.model_name = content_type.model

    # Sort the action records in descending order based on action_time
    action_records = sorted(action_records, key=lambda x: x.action_time, reverse=True)

    # Render the template and pass the action_records to it
    return render(request, 'dashboard/action_records.html', {'action_records': action_records})



@login_required
def avatar(request):
    user = User.objects.get(username=request.user)
    avatar = uprofile.objects.get(user=user)
    context = {
        "avatar": avatar,
    }
    return context

@login_required
@never_cache
def uprofile(request):
    # Get the current logged-in user
    current_user = request.user

    # Fetch the count of records added by the current user for Medicine model
    medicine_records_count = current_user.medicine_set.count()

    # Fetch the count of records added by the current user for Customer model
    customer_records_count = current_user.customer_set.count()

    # Fetch the count of records edited by the current user for MedicineEditLog model
    medicine_edit_records_count = current_user.medicineeditlog_set.count()

    # Calculate the total records count for each model
    total_medicine_records = Medicine.objects.count()
    total_customer_records = Customer.objects.count()
    total_medicine_edit_records = MedicineEditLog.objects.count()

    # Calculate the average percentages for each model
    average_percentages = {
        'Medicine': (medicine_records_count / total_medicine_records) * 100 if total_medicine_records > 0 else 0,
        'Customer': (customer_records_count / total_customer_records) * 100 if total_customer_records > 0 else 0,
        'MedicineEditLog': (medicine_edit_records_count / total_medicine_edit_records) * 100 if total_medicine_edit_records > 0 else 0,
    }
    
    
    
    
    
    
    

    # Render the template with the average percentages
    context = {
        'average_percentages': average_percentages,
    }
    return render(request, 'dashboard/profile.html', context)



import random
import string
from django.core.mail import send_mail


@redirect_to_dashboard
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        # Check if the email address exists in the database
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Handle the case where the email address is not found in the database
            return render(request, 'login/forget.html', {'message': 'Email not found'})

        # Generate a random password reset token
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

        # Save the token in the user's profile or in a separate model for password reset tokens
        # For simplicity, let's assume we are saving the token in the user's profile
        user.profile.password_reset_token = token
        user.profile.save()

        # Send the password reset email to the user
        subject = 'Password Reset Request'
        message = f'Please click on the following link to reset your password: http://localhost:8000/en/resetpassword/?token={token}'
        from_email = 'budibangg@gmail.com'
        recipient_list = [email]

        try:
            send_mail(subject, message, from_email, recipient_list)
            print(f"Password reset email sent to {email}")
        except Exception as e:
            print(f"Failed to send password reset email to {email}: {e}")

        # Display a success message to the user
        return render(request, 'login/forget.html', {'message': 'Password reset email sent'})

    return render(request, 'login/forget.html')



def reset_password(request):
    if request.method == 'GET':
        token = request.GET.get('token')

        # Check if the token exists in the database
        try:
            user = User.objects.get(profile__password_reset_token=token)
        except User.DoesNotExist:
            # Handle the case where the token is not found in the database
            return render(request, 'login/reset_password.html', {'message': 'Invalid token'})

        # Render the password reset form
        return render(request, 'login/reset_password.html', {'token': token})

    elif request.method == 'POST':
        token = request.POST.get('token')
        password = request.POST.get('password')

        # Check if the token exists in the database
        try:
            user = User.objects.get(profile__password_reset_token=token)
        except User.DoesNotExist:
            # Handle the case where the token is not found in the database
            return render(request, 'login/reset_password.html', {'message': 'Invalid token'})

        # Reset the user's password
        user.set_password(password)
        user.save()

        # Clear the password reset token from the user's profile
        user.profile.password_reset_token = ''
        user.profile.save()

        # Display a success message to the user
        return render(request, 'login/reset_password.html', {'message': 'Password reset successful'})

    return render(request, 'login/reset_password.html')




@login_required
def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.avatar = request.FILES.get('avatar')
            profile.save()
            messages.success(request, 'User Added successfully!')  # Success message
            return redirect('usersdetails')  # Replace 'usersdetails' with the name of your success page or URL
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')  # Error message
    else:
        form = RegistrationForm()
    context = {
        'form': form,
        'user_choices' : Profile.USER_TYPE_CHOICES
    }
    return render(request, 'dashboard/register.html', context)

@login_required
def userdetails (request):
    users = User.objects.all()
    users_profile = Profile.objects.select_related('user')
    no_users = users.exists() > 0
    user_type = request.user.profile.user_type
    user_type_choices = Profile.USER_TYPE_CHOICES

    # combines user and profile table into one table all_users
    combined_user_profile = []
    for profile_row  in users_profile:
        users_row = profile_row.user
        combined_user_profile.append({
            'id' : users_row.id,
            'username' : users_row.username,
            'first_name' : users_row.first_name,
            'last_name' : users_row.last_name,
            'email' : users_row.email,
            'date_joined' : users_row.date_joined,
            'last_login' : users_row.last_login,
            'avatar' : profile_row.avatar,
            'user_type' : profile_row.user_type,
        })

    context = {
        "users" : users, 
        "no_users" : no_users,
        "userdata" : combined_user_profile,
        "user_type": user_type,
        "user_type_choices" : user_type_choices,
    }

    return render(request, 'dashboard/usersdetails.html' , context)

@login_required
def update_user(request, record_id):
    user = get_object_or_404(User, id=record_id)
    profile = get_object_or_404(Profile, user=user)
    user_type_choices = Profile.USER_TYPE_CHOICES

    UserForm = modelform_factory(User, form=UserUpdateForm, exclude=['password'])
    ProfileForm = modelform_factory(Profile, form=ProfileUpdateForm)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'User data updated successfully.')
            return redirect('usersdetails')
        else:
            messages.error(request, 'Failed to update user data. Please correct the errors.')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_type_choices': user_type_choices,
    }

    return render(request, 'dashboard/updateuser.html', context)
from django.contrib.auth.models import User
@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('usersdetails')
    return redirect('usersdetails')


@login_required
def admindetails (request):
    users = User.objects.all()
    users_profile = Profile.objects.filter(user_type='admin')
    no_users = users.exists() > 0
    user_type = request.user.profile.user_type

    # combines user and profile table into one table all_users
    combined_user_profile = []
    for profile_row  in users_profile:
        users_row = profile_row.user
        combined_user_profile.append({
            'id' : users_row.id,
            'username' : users_row.username,
            'first_name' : users_row.first_name,
            'last_name' : users_row.last_name,
            'email' : users_row.email,
            'date_joined' : users_row.date_joined,
            'last_login' : users_row.last_login,
            'avatar' : profile_row.avatar,
            'user_type' : profile_row.user_type,
        })

    context = {
        "users" : users, 
        "no_users" : no_users,
        "userdata" : combined_user_profile,
        "user_type": user_type,

    }
    return render(request, 'dashboard/usersadmin.html', context)

@login_required
def moddetails (request):
    users = User.objects.all()
    users_profile = Profile.objects.filter(user_type='moderator')
    no_users = users.exists() > 0
    user_type = request.user.profile.user_type

    # combines user and profile table into one table all_users
    combined_user_profile = []
    for profile_row  in users_profile:
        users_row = profile_row.user
        combined_user_profile.append({
            'id' : users_row.id,
            'username' : users_row.username,
            'first_name' : users_row.first_name,
            'last_name' : users_row.last_name,
            'email' : users_row.email,
            'date_joined' : users_row.date_joined,
            'last_login' : users_row.last_login,
            'avatar' : profile_row.avatar,
            'user_type' : profile_row.user_type,
            
        })

    context = {
        "users" : users, 
        "no_users" : no_users,
        "userdata" : combined_user_profile,
        "user_type": user_type,

    }
    return render(request, 'dashboard/usersmod.html', context)

@login_required
def logged_in_404(request, exception=None):
      
    return render(request, 'dashboard/404.html', {})

def logged_out_404(request, exception=None):
      
    return render(request, 'dashboard/404main.html', {})

def retrieve_medicines():
    medicines = Medicine.objects.all()
    return medicines

from django.shortcuts import get_object_or_404

def user_is_admin(user):
    return user.is_authenticated and user.is_superuser



@login_required
@user_passes_test(user_is_admin)
def update_medicine(request, record_id):
    medicine = get_object_or_404(Medicine, id=record_id)
    company_list = Company.objects.all()
    medical_type = MedicalType.objects.all()

    if request.method == 'POST':
        form = EditMedicineForm(request.POST, instance=medicine, edited_by=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicine record updated successfully.", extra_tags='success edit')
            return redirect('medicinelist')
        else:
            error_message = "Failed to update medicine record. Please check the form fields."
            for field, errors in form.errors.items():
                error_message += f'\n- {field.capitalize()}: {", ".join(errors)}'
            messages.error(request, error_message, extra_tags='edit')
    else:
        form = EditMedicineForm(instance=medicine, edited_by=request.user)

    context = {
        'form': form,
        'company_list': company_list,
        'selected_company': medicine.company.id,
        'selected_type': medicine.type.id,
        'medical_type' : medical_type,
    }
    return render(request, 'dashboard/updatemedicine.html', context)



@login_required
def update_medicine_history(request,):
    medicine_log = MedicineEditLog.objects.all()
    no_medicine = medicine_log.exists() > 0

    context = {
        "medicine_log" : medicine_log,
        "no_medicine" : no_medicine,
    }
    return render(request, 'dashboard/viewmedicinelog.html', context)


@login_required
def viewmedicine(request):
    all_medicines = retrieve_medicines()
    user_type = request.user.profile.user_type
    no_medicine = all_medicines.exists() > 0
    expiredmidicine = get_expired_medicines()
    expiring_this_month = get_expiring_this_month_medicines()
    expiring_soon = get_expiring_soon_medicines()
    company_list = Company.objects.values_list('name', flat=True).distinct()
        
    context = {
        "all_medicines": all_medicines,
        "user_type": user_type,
        "no_medicine": no_medicine,
        "expiredmidicine": expiredmidicine,
        "expiring_this_month": expiring_this_month,
        "expiring_soon": expiring_soon,
        "company_list": company_list,
    }
    return render(request, 'dashboard/viewmedicine.html', context)


@login_required
def viewmedicine_thismonth(request):
    med_this_month = retrieve_this_month_medicine_records()
    context = {
        "med_this_month" : med_this_month
    }
    return render(request, 'dashboard/viewmedicinemonth.html', context)


@login_required
@user_passes_test(user_is_admin)
def add_medical_type(request):
    if request.method == 'POST':
        form = MedicalTypeForm(request.POST)
        if form.is_valid():
            medical_type = form.save(commit=False)
            medical_type.added_by = request.user  # Set the 'added_by' field value
            medical_type.added_on = datetime.now()  # Set the 'added_on' field value to the current system date and time
            medical_type.save()
            # Optionally, perform any additional actions upon successful form submission
        else:
            # Form is not valid, render the form template with errors
            return render(request, 'dashboard/addmedicaltype.html', {'form': form})
    else:
        form = MedicalTypeForm()

    return render(request, 'dashboard/addmedicaltype.html', {'form': form})



@login_required
def view_medical_type(request):
    type_list = MedicalType.objects.all()
    no_type = type_list.exists() > 0
    user_type = request.user.profile.user_type
    context = {
        "type_list" : type_list,
        "no_type" : no_type,
        "user_type" : user_type,
    }
    return render(request, 'dashboard/viewtype.html', context)



@login_required
@user_passes_test(user_is_admin)
def update_medical_type(request, record_id):
    medical_type = get_object_or_404(MedicalType, id=record_id)

    if request.method == 'POST':
        form = EditMedicalTypeForm(request.POST, instance=medical_type, edited_by=request.user)
        if form.is_valid():
            instance = form.save()
            # Create MedicalTypeLog entry
            log_entry = MedicalTypeLog.objects.create(name=instance, edited_by=request.user)
            messages.success(request, "Medical Type record updated successfully.", extra_tags='success')
            return redirect('viewmedicaltype')
        else:
            error_message = "Failed to update Medical Type record. Please check the form fields."
            for field, errors in form.errors.items():
                error_message += f'\n- {field.capitalize()}: {", ".join(errors)}'
            messages.error(request, error_message, extra_tags='edit')
    else:
        form = EditMedicalTypeForm(instance=medical_type, edited_by=request.user)

    context = {
        'form': form,
    }
    return render(request, 'dashboard/updatetype.html', context)




@login_required
def add_company(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to companylist URL
            return redirect('viewcompany')
    else:
        form = CompanyForm()
    return render(request, 'dashboard/addcompany.html', {'form': form}) 


@login_required
def viewcompany(request):
    company_list = Company.objects.all()
    no_company = company_list.exists() > 0
    user_type = request.user.profile.user_type
    context = {
        "company_list" : company_list,
        "no_company" : no_company,
        "user_type" : user_type,
    }
    return render(request, 'dashboard/viewcompany.html', context)


@login_required
@user_passes_test(user_is_admin)
def update_company(request, record_id):
    company = get_object_or_404(Company, id=record_id)
    company_list = Company.objects.all()

    if request.method == 'POST':
        form = EditCompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            # Create CompanyLog entry
            log_entry = CompanyLog(company=company, edited_by=request.user)
            log_entry.save()
            messages.success(request, "Company record updated successfully.", extra_tags='success')
            return redirect('viewcompany')
        else:
            error_message = "Failed to update company record. Please check the form fields."
            for field, errors in form.errors.items():
                error_message += f'\n- {field.capitalize()}: {", ".join(errors)}'
            messages.error(request, error_message, extra_tags='edit')
    else:
        form = EditCompanyForm(instance=company)

    context = {
        'form': form,
        'company_list': company_list,
    }
    return render(request, 'dashboard/updatecompany.html', context)


@login_required
def update_company_history(request,):
    company_log = MedicineEditLog.objects.all()
    no_company = company_log.exists() > 0

    context = {
        "company_log" : company_log,
        "no_company" : no_company,
    }
    return render(request, 'dashboard/viewcompanylog.html', context)


@login_required
def addmedicine(request):
    companies = Company.objects.all()
    medical_type = MedicalType.objects.all()
    
    if request.method == 'POST':
        form = AddMedicineForm(request.POST)
        if form.is_valid():
            form.save(added_by=request.user)  # Pass the current user as added_by
            messages.success(request, 'Medicine added successfully.', extra_tags='add')
            return redirect('medicinelist')
        else:
            messages.error(request, 'Error adding medicine. Please check the form fields.' , extra_tags='add')

    else:
        form = AddMedicineForm()
    
    context = {
        'form': form,
        'companies': companies,
        'medical_type' : medical_type,
    }
    
    return render(request, 'dashboard/addmedicine.html', context)


@login_required
def expiredmidicine(request):
    expiredmidicine = get_expired_medicines()
    context = {
        "expiredmidicine" : expiredmidicine,
    }

    return render(request, 'dashboard/expiredmedicine.html', context)

@login_required
def expiresoon(request):
    expiring_soon = get_expiring_soon_medicines()
    context = {
       "expiring_soon" : expiring_soon,
    }
    return render(request, 'dashboard/expiresoon.html', context)

@login_required
def expirethismonth(request):
    expiring_this_month = get_expiring_this_month_medicines()

    context = {
       "expiring_this_month" : expiring_this_month,
    }

    return render(request, 'dashboard/expirethismonth.html', context)

def retrieve_customer_data():
    customer_data = Customer.objects.all()

    return customer_data

@login_required
def customers(request):
    customer_data = retrieve_customer_data()
    user_type = request.user.profile.user_type
    context = {
        "customer_data" : customer_data,
        "user_type" : user_type
    }
    return render(request, 'dashboard/customers.html', context)

@login_required
def addcustomer(request):
    if request.method == 'POST':
        form = AddCustomerForm(request.POST, request=request)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer added successfully.')
            return redirect('customers')  # Redirect to the customer list page
        else:
            messages.error(request, 'Error occurred while submitting the form.')
    else:
        form = AddCustomerForm(request=request)
    return render(request, 'dashboard/addcustomer.html', {'form': form} )


@login_required
def updatecustomer (request, record_id):
    customer = get_object_or_404(Customer, id=record_id)
    if request.method == 'POST':
        form = UpdateCustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer details updated successfully.')
            return redirect('customers')

    else:
        form = UpdateCustomerForm(instance=customer)
    context = {
        'customer' : customer,
        'form' : form,
    }
    return render(request, 'dashboard/updatecustomer.html', context)

@login_required
def deletecustomer(request, record_id):
    customer = get_object_or_404(Customer, id=record_id)

    if request.method == 'POST':
        keep_invoices = request.POST.get('keep_invoices')
        if keep_invoices == 'on':
            # Keep invoices
            messages.info(request, 'Customer deleted. Invoices kept.')
        else:
            # Delete invoices (assuming there is a foreign key relationship between Customer and Invoice models)
            InvoiceRequest.objects.filter(customer=customer).delete()
            messages.success(request, 'Customer and associated invoices deleted successfully.')
        
        customer.delete()
        return redirect('customers')  # Replace 'customers' with the appropriate URL name

    return redirect('customers')  # Redirect to customers page if the request method is not POST



@login_required
def get_medicine_price(request):
    medicine_name = request.GET.get('medicine')
    try:
        medicine = Medicine.objects.get(name=medicine_name)
        response = {
            'price': medicine.price,
            'stock': medicine.stock,
        }
        return JsonResponse(response)
    except Medicine.DoesNotExist:
        return JsonResponse({'error': 'Medicine not found'})


# retrieve invoices

def retrieve_invoices_data():
    invoices_record = InvoiceRequest.objects.all()
    return invoices_record

def retrieve_invoice_items(invoice_id):
    invoice_items = InvoiceItem.objects.filter(invoice_id=invoice_id)
    return invoice_items

@login_required
def customer_invoice_request(request):
    customers = retrieve_customer_data()

    if request.method == 'POST':
        form = CustomerInvoiceRequestForm(request.POST)
        if form.is_valid():
            invoice_request = form.save(commit=False)

            # Generate the invoice number only if it's a new object
            if not invoice_request.pk:
                last_invoice = InvoiceRequest.objects.order_by('-id').first()
                if last_invoice:
                    last_number = int(last_invoice.invoice_number[3:])
                    new_number = last_number + 1
                else:
                    new_number = 1
                invoice_request.invoice_number = 'INV{:04d}'.format(new_number)

            # Set the added_by field to the current logged-in user
            invoice_request.added_by = request.user
            invoice_request.save()

            messages.success(request, 'Invoice request created successfully!')
            return redirect(viewinvoices)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in field "{form.fields[field].label}": {error}')
    else:
        form = CustomerInvoiceRequestForm()

    # Populate the invoice_number field in the form data
    last_invoice = InvoiceRequest.objects.order_by('-id').first()
    if last_invoice:
        last_number = int(last_invoice.invoice_number[3:])
        new_number = last_number + 1
    else:
        new_number = 1
    initial_data = {'invoice_number': 'INV{:04d}'.format(new_number)}
    form = CustomerInvoiceRequestForm(initial=initial_data)

    context = {
        "customers": customers,
        "form": form,
    }
    return render(request, 'dashboard/customer_invoice_request.html', context)


def delete_invoice(request, invoice_id):
    invoice = get_object_or_404(InvoiceRequest, id=invoice_id)

    if request.method == 'POST':
        return_stock = request.POST.get('return_stock', False) == 'True'

        # Delete the invoice and handle the return stock option
        with transaction.atomic():
            invoice_items = invoice.invoiceitem_set.all()
            if return_stock:
                # Add the invoice items' stock back to the medicine stock
                for item in invoice_items:
                    item.medicine.in_stock_total += item.quantity
                    item.medicine.save()

            # Delete the invoice and related invoice items
            invoice_items.delete()
            invoice.delete()
            messages.success(request, 'Invoice deleted successfully!')

    return redirect('viewinvoices')



@login_required
def viewinvoices(request):
    invoices = retrieve_invoices_data()
    no_invoices = retrieve_invoices_data().exists() > 0
    user_type = request.user.profile.user_type

    context = {
        "invoices" : invoices,
        "no_invoices" : no_invoices,
        "user_type" : user_type,
    }
    return render(request, 'dashboard/viewinvoice.html', context)

@login_required
def viewinvoicesmonth(request):
    invoices = retrieve_invoices_data()
    no_invoices = retrieve_invoices_data().exists() > 0
    user_type = request.user.profile.user_type

    context = {
        "invoices" : invoices,
        "no_invoices" : no_invoices,
        "user_type" : user_type,
    }
    return render(request, 'dashboard/viewinvoicemonth.html', context)


@login_required
def viewinvoicesyear(request):
    invoices = retrieve_invoices_data()
    no_invoices = retrieve_invoices_data().exists() > 0
    user_type = request.user.profile.user_type

    context = {
        "invoices" : invoices,
        "no_invoices" : no_invoices,
        "user_type" : user_type,
    }
    return render(request, 'dashboard/viewinvoiceanuall.html', context)

@login_required
def edit_invoice(request, invoice_id):
    invoice = get_object_or_404(InvoiceRequest, id=invoice_id)
    
    if request.method == 'POST':
        form = InvoiceRequestForm(request.POST, instance=invoice)
        if form.is_valid():
            try:
                # Calculate total amount based on related InvoiceItems
                total_amount = invoice.invoiceitem_set.aggregate(sum_total=Sum(F('unit_price') * F('quantity')))['sum_total'] or 0

                # Update payment amounts based on payment method
                cash_payment_amount = form.cleaned_data['cash_payment_amount']
                pay_later_payment_amount = form.cleaned_data['pay_later_payment_amount']

                if cash_payment_amount and pay_later_payment_amount:
                    # Validate if the input amounts exceed the total amount
                    if cash_payment_amount + pay_later_payment_amount > total_amount:
                        raise ValueError("The sum of cash and pay later amounts cannot exceed the total amount.")
                else:
                    # Divide the total amount equally between cash and pay later
                    cash_payment_amount = total_amount / 2
                    pay_later_payment_amount = total_amount / 2

                # Update the invoice object with the calculated or user input amounts
                invoice.total_amount = total_amount
                invoice.cash_payment_amount = cash_payment_amount
                invoice.pay_later_payment_amount = pay_later_payment_amount

                # Save the form and redirect
                form.save()
                return redirect('viewinvoices')
            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = InvoiceRequestForm(instance=invoice)

    context = {
        'invoice': invoice,  # Ensure that invoices is passed to the context
        'invoice_id': invoice_id,
        'form': form,
        'payment_choices': InvoiceRequest.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'dashboard/editinvoice.html', context)


@login_required
def add_invoice_items(request):
    medicines = retrieve_medicines()
    invoices = retrieve_invoices_data()

    if request.method == 'POST':
        form = InvoiceItemForm(request.POST, request=request)  # Pass the request object to the form
        if form.is_valid():
            invoice_item = form.save(commit=False)
            invoice_item.added_by = request.user  # Assign the logged-in user
            invoice_number = form.cleaned_data['invoice']
            medicine_name = form.cleaned_data['medicine']
            try:
                invoice = get_object_or_404(InvoiceRequest, invoice_number=invoice_number)
                medicine = get_object_or_404(Medicine, name=medicine_name)

                # Check if the requested quantity exceeds the available stock
                requested_quantity = invoice_item.quantity
                if requested_quantity > medicine.in_stock_total:
                    error_message = f"Requested quantity exceeds available stock. Available stock: {medicine.in_stock_total}"
                    messages.error(request, error_message)
                else:
                    invoice_item.invoice = invoice
                    invoice_item.medicine = medicine
                    invoice_item.save()
                    invoice_id = invoice_item.invoice.id
                    messages.success(request, 'Invoice item added successfully.')
                    # Update medicine stock only if the quantity is positive
                    if requested_quantity > 0:
                        medicine.in_stock_total -= requested_quantity
                        medicine.save()
                    return redirect('invoiceitems', invoice_id=invoice_id)
            except (InvoiceRequest.DoesNotExist, Medicine.DoesNotExist):
                pass

        error_message = 'Failed to add the invoice item. Please check the form.'
        messages.error(request, error_message)
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    else:
        form = InvoiceItemForm(request=request)  # Pass the request object to the form

    context = {
        'form': form,
        'medicines': medicines,
        'invoices': invoices,
    }
    return render(request, 'dashboard/add_invoice_items.html', context)

def delete_invoice_item(request, invoice_item_id):
    invoice_item = get_object_or_404(InvoiceItem, id=invoice_item_id)
    
    # Update the stock and delete the invoice item
    invoice_item.delete()
    
    # Add success message
    messages.success(request, 'Invoice item deleted successfully.')
    
    # Redirect back to the invoice details page
    return redirect('invoiceitems', invoice_id=invoice_item.invoice.id)


def view_invoice_items(request, invoice_id):
    invoice_items = retrieve_invoice_items(invoice_id)
    no_items = invoice_items.exists() > 0
    user_type = request.user.profile.user_type

    # Fetch the invoice number
    if invoice_items.exists():
        invoice_number = invoice_items[0].invoice.invoice_number
    else:
        invoice_number = None

    context = {
        "invoice_items": invoice_items,
        "no_items": no_items,
        "user_type": user_type,
        "invoice_number": invoice_number,
    }
    return render(request, 'dashboard/viewinvoiceitems.html', context)



@login_required
def invoicetopdf(request, invoice_id):
    # Retrieve invoice and related data
    invoice = InvoiceRequest.objects.get(id=invoice_id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    total_discount = invoice_items.filter(discount__gt=0).aggregate(total_discount=models.Sum(models.F('discount') * models.F('quantity')))
    total_discount_amount = total_discount['total_discount'] if total_discount['total_discount'] is not None else 0
    sub_total = sum(item.total_price for item in invoice_items)
    final_total = sub_total - total_discount_amount
    if total_discount_amount is None or total_discount_amount == 0:
        final_total = sub_total
    else:
        final_total = sub_total - total_discount_amount
    customer = invoice.customer
    issue_date = invoice.request_date
    added_by = invoice.added_by
    p_method = invoice.payment_method
    cash = invoice.cash_payment_amount
    pay_later = invoice.pay_later_payment_amount
    # Prepare the template context
    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'customer': customer,
        'issue_date' : issue_date,
        'added_by' : added_by, 
        'total_discount_amount' : total_discount_amount,
        'sub_total' : sub_total,
        'final_total' : final_total,
        'p_method' : p_method,
        'cash' : cash,
        'pay_later' : pay_later,

    }

    return render(request, 'dashboard/invoicetopdf.html', context)


    
def generate_pdf_invoice(request, invoice_id):
   # Retrieve invoice and related data
    invoice = InvoiceRequest.objects.get(id=invoice_id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    total_discount = invoice_items.filter(discount__gt=0).aggregate(total_discount=models.Sum(models.F('discount') * models.F('quantity')))
    total_discount_amount = total_discount['total_discount'] if total_discount['total_discount'] is not None else 0
    sub_total = sum(item.total_price for item in invoice_items)
    final_total = sub_total - total_discount_amount
    if total_discount_amount is None or total_discount_amount == 0:
        final_total = sub_total
    else:
        final_total = sub_total - total_discount_amount
    p_method = invoice.payment_method
    cash = invoice.cash_payment_amount
    pay_later = invoice.pay_later_payment_amount

    customer = invoice.customer
    issue_date = invoice.request_date
    added_by = invoice.added_by

    # Prepare the template context
    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'customer': customer,
        'issue_date' : issue_date,
        'added_by' : added_by, 
        'total_discount_amount' : total_discount_amount,
        'sub_total' : sub_total,
        'final_total' : final_total,
        'p_method' : p_method,
        'cash' : cash,
        'pay_later' : pay_later,

    }
    
    

 # Render the HTML template with the invoice data
    html_string = render_to_string('dashboard/invoicetopdftemplate.html', context)


    # Generate the file path for saving the PDF in the Downloads folder
    file_name = f'invoice_{invoice.invoice_number}.pdf'
    download_folder = os.path.expanduser('~/Downloads')
    file_path = os.path.join(download_folder, file_name)

    # Create a file-like object to receive PDF data
    pdf_file = tempfile.NamedTemporaryFile(delete=True)

    # Create the PDF using xhtml2pdf
    with open(file_path, 'wb') as pdf_file:
        pisa.CreatePDF(html_string, dest=pdf_file)

    # Retrieve the PDF file contents
    pdf_data = open(pdf_file.name, 'rb').read()

    # Close the PDF file
    pdf_file.close()

    # Return the PDF file as a response
    with open(file_path, 'rb') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={file_name}'
        return response
    


@login_required
def print_invoice(request, invoice_id):
    # Retrieve invoice and related data
    invoice = InvoiceRequest.objects.get(id=invoice_id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    total_discount = invoice_items.filter(discount__gt=0).aggregate(total_discount=models.Sum(models.F('discount') * models.F('quantity')))
    total_discount_amount = total_discount['total_discount'] if total_discount['total_discount'] is not None else 0
    sub_total = sum(item.total_price for item in invoice_items)
    final_total = sub_total - total_discount_amount
    if total_discount_amount is None or total_discount_amount == 0:
        final_total = sub_total
    else:
        final_total = sub_total - total_discount_amount

    customer = invoice.customer
    issue_date = invoice.request_date
    added_by = invoice.added_by
    p_method = invoice.payment_method
    cash = invoice.cash_payment_amount
    pay_later = invoice.pay_later_payment_amount

    # Prepare the template context
    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'customer': customer,
        'issue_date' : issue_date,
        'added_by' : added_by, 
        'total_discount_amount' : total_discount_amount,
        'sub_total' : sub_total,
        'final_total' : final_total,
        'p_method' : p_method,
        'cash' : cash,
        'pay_later' : pay_later,

    }

    return render(request, 'dashboard/invoicetopdfprint.html', context)

@login_required
def download_invoice(request, invoice_id):
    # Retrieve invoice and related data
    invoice = InvoiceRequest.objects.get(id=invoice_id)
    invoice_items = InvoiceItem.objects.filter(invoice=invoice)
    total_discount = invoice_items.filter(discount__gt=0).aggregate(total_discount=models.Sum(models.F('discount') * models.F('quantity')))
    total_discount_amount = total_discount['total_discount'] if total_discount['total_discount'] is not None else 0
    sub_total = sum(item.total_price for item in invoice_items)
    final_total = sub_total - total_discount_amount
    if total_discount_amount is None or total_discount_amount == 0:
        final_total = sub_total
    else:
        final_total = sub_total - total_discount_amount

    customer = invoice.customer
    issue_date = invoice.request_date
    added_by = invoice.added_by
    p_method = invoice.payment_method
    cash = invoice.cash_payment_amount
    pay_later = invoice.pay_later_payment_amount

    # Prepare the template context
    context = {
        'invoice': invoice,
        'invoice_items': invoice_items,
        'customer': customer,
        'issue_date' : issue_date,
        'added_by' : added_by, 
        'total_discount_amount' : total_discount_amount,
        'sub_total' : sub_total,
        'final_total' : final_total,
        'p_method' : p_method,
        'cash' : cash,
        'pay_later' : pay_later,

    }

    return render(request, 'dashboard/invoicetopdfdownload.html', context)



@login_required
def soldmedicine(request):
    sold_units = retrieve_medicine_sold()
    no_sold_units = sold_units.exists() > 0

    context = {
        "sold_units": sold_units,
        "no_sold_units" : no_sold_units
    }
    return render(request, 'dashboard/viewsold.html', context)



@login_required
def confirm_change_password(request):
    if request.method == 'POST':
        confirm_password = request.POST['confirm_password']

        if confirm_password == "":
            messages.error(request, 'Confirm password field is required.')
            return redirect('dashboard')  # Redirect back to the dashboard with an error message

        if request.user.check_password(confirm_password):
            request.session['confirm_password'] = confirm_password  # Store the confirm password in the session
            return redirect('changepassword')  # Redirect to the change password page
        else:
            messages.error(request, 'Incorrect current password or password confirmation failed.')
            return redirect('dashboard')  # Redirect back to the dashboard with an error message

    return redirect('dashboard')  # Redirect back to the dashboard if accessed without a POST request


def changepassword(request):
    print('Reached the changepassword view')
    confirm_password = request.session.pop('confirm_password', None)  # Retrieve and remove the confirm password from the session

    if not confirm_password or not request.user.check_password(confirm_password):
        return redirect('dashboard')  # Redirect to the dashboard if confirm password is not provided or does not match
    
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            new_password1 = form.cleaned_data['new_password1']
            new_password2 = form.cleaned_data['new_password2']

            if new_password1 != new_password2:
                messages.error(request, 'Passwords do not match.')
                print('Passwords do not match:', new_password1, new_password2)
            else:
                user = form.save()
                update_session_auth_hash(request, user)  # Update the session to prevent logout
                messages.success(request, 'Password successfully changed.')
                return redirect('dashboard')  # Redirect to the dashboard after password change
        else:
            print('Form errors:', form.errors)
    else:
        form = PasswordChangeForm(request.user)
    

    return render(request, 'dashboard/changepassword.html', {'form': form})

from django.urls import reverse
from django.http import QueryDict
from urllib.parse import urlparse

def set_language(request, language_code):
    request.session['django_language'] = language_code
    print(f"Language code stored in session: {request.session['django_language']}")
    activate(language_code)

    # Get the referer URL and replace any existing 'lang' query parameter
    redirect_url = request.META.get('HTTP_REFERER', reverse('dashboard'))
    parsed_url = urlparse(redirect_url)
    query_params = QueryDict(parsed_url.query, mutable=True)
    query_params['lang'] = language_code
    parsed_url = parsed_url._replace(query=query_params.urlencode())
    redirect_url = parsed_url.geturl()

    return redirect(redirect_url)

def global_search(request):
    if request.method == 'GET':
        form = GlobalSearchForm(request.GET)
        if form.is_valid():
            search_query = form.cleaned_data['search_query']
            # Perform the search query across all models
            medicine_results = Medicine.objects.filter(name__icontains=search_query)
            customer_results = Customer.objects.filter(name__icontains=search_query)
            invoice_results = InvoiceRequest.objects.filter(invoice_number__icontains=search_query)
            user_results = User.objects.filter(username__icontains=search_query)

            # Create a list of dictionaries with model name and results
            all_results = []
            for result in medicine_results:
                all_results.append({'model': 'Medicine', 'result': result.name})
            for result in customer_results:
                all_results.append({'model': 'Customer', 'result': result.name})
            for result in invoice_results:
                all_results.append({'model': 'Invoice', 'result': result.invoice_number})
            for result in user_results:
                all_results.append({'model': 'User', 'result': result.username})

            return render(request, 'dashboard/global_search.html', {'results': all_results})
    else:
        form = GlobalSearchForm()

    return render(request, 'dashboard/global_search.html', {'form': form})

from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import letter

def generate_report(request):
    # Fetch data from all models
    medicines = Medicine.objects.all()
    customers = Customer.objects.all()
    invoices = InvoiceRequest.objects.all()
    users = User.objects.all()

    # Create a response object to return the PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="my_report.pdf"'

    # Create a PDF document
    p = canvas.Canvas(response, pagesize=letter)

    try:
        # Load the TrueType font and set it as the font for the PDF
        font_path = '/path/to/your/NotoSansArabic-Regular.ttf'  # Replace with the actual path to the "Noto Sans Arabic" font file
        pdfmetrics.registerFont(TTFont('NotoSansArabic', font_path))
        p.setFont("NotoSansArabic", 12)
    except Exception as e:
        # If the TrueType font cannot be loaded, use the "Helvetica" font as a fallback
        p.setFont("Helvetica", 12)

    # Set initial y position for the top of the page
    y = p._pagesize[1] - 50

    # Add the medicines to the PDF
    p.drawString(50, y, _("Medicine Report:"))
    p.line(50, y - 20, p._pagesize[0] - 50, y - 20)
    y -= 30

    for medicine in medicines:
        # Draw the medicine name
        p.drawString(50, y, _("Medicine: ") + medicine.name)

        # Draw the description using Unicode
        description = _("Description: ") + medicine.description
        p.drawString(50, y - 20, description)

        # Add a horizontal line as a separator
        p.line(50, y - 30, p._pagesize[0] - 50, y - 30)

        # Update the y position for the next medicine
        y -= 40

        # Move to the next page if needed
        if y < 50:
            p.showPage()
            y = p._pagesize[1] - 50

    # Add other models to the PDF
    models_data = [
        (customers, "Customer Report:"),
        (invoices, "Invoice Report:"),
        (users, "User Report:")
    ]

    for model_data, model_title in models_data:
        y -= 40
        p.drawString(50, y, _(model_title))
        p.line(50, y - 20, p._pagesize[0] - 50, y - 20)
        y -= 30

        for model_obj in model_data:
            # Draw the object details (change this based on your model fields)
            p.drawString(50, y, str(model_obj))
            y -= 20

            # Move to the next page if needed
            if y < 50:
                p.showPage()
                y = p._pagesize[1] - 50

    p.save()
    return response