from django.apps import apps

def get_verbose_name(model_name):
    model = apps.get_model(model_name)
    if model:
        return model._meta.verbose_name
    return None