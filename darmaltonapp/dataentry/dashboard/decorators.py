from django.shortcuts import redirect
from django.urls import reverse

def redirect_to_dashboard(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.path != reverse('dashboard'):
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
