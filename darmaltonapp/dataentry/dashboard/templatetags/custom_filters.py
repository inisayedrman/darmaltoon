from django import template
from django.apps import apps

register = template.Library()

@register.filter(name='get_model_name')
def get_model_name(obj):
    return obj._meta.model_name

# Add the following line at the end of the file:
register.filter('get_model_name', get_model_name)

@register.filter
def user_role(user):
    return user.profile.user_type

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def format_payment_method(value):
    words = value.split('_')
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)


@register.simple_tag
def get_current_language():
    # Your implementation here
    pass

@register.simple_tag
def getavailable_languages():
    # Your implementation here
    pass

@register.simple_tag
def get_language_info_list():
    # Your implementation here
    pass