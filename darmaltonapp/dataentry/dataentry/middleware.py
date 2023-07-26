from django.utils import timezone

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'django_timezone' in request.session:
            timezone.activate(request.session['django_timezone'])
        else:
            timezone.deactivate()
        response = self.get_response(request)
        return response
