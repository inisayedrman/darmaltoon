"""
Django settings for dataentry project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path
import os
from django.utils import timezone





# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-nq@izqwqwp*kie6$2_uak9c$wf=j+=375t3ucf%#1#3=)zuc0i'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
CSRF_COOKIE_SECURE = True

ALLOWED_HOSTS = ['127.0.0.1']

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SESSION_COOKIE_AGE = 5000


# Application definition

INSTALLED_APPS = [
    'dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    #custom apps

    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dataentry.middleware.TimezoneMiddleware',
    'dashboard.middleware.PreventLoginAfterAuthenticationMiddleware',
    

]


CSRF_COOKIE_DOMAIN = None



ROOT_URLCONF = 'dataentry.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dataentry.context_processors.recent_actions',
                'dataentry.context_processors.new_action_count',
                'django.template.context_processors.i18n',
            ],

            'libraries': {
                'humanize': 'django.contrib.humanize.templatetags.humanize',
            },
        },
    },
]



WSGI_APPLICATION = 'dataentry.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]



# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en'

from django.utils.translation import gettext as _

LANGUAGES = [
    ('en', 'English'),
    ('ps', 'پښتو'),
    ('fa', 'دری'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]



# settings.py

TIME_ZONE = 'Asia/Jakarta'


# # Get the current time zone
# current_time_zone = timezone.get_current_timezone()


# TIME_ZONE = current_time_zone


USE_TZ = True




USE_I18N = True




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

# STATIC_URL = 'static/'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CKEDITOR_UPLOAD_PATH = "media/uploads/"


STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
    
]

# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static', 'dashboard', 'img'),
# ]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'




# CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"




# Specify the character encoding used in your translation files
# Adjust the encoding based on your specific needs
# For example, if your translation files are UTF-8 encoded:
DEFAULT_CHARSET = 'utf-8'

# Specify the character encoding used in Python source files
# Adjust the encoding based on your source code's encoding
# For example, if your source code files are UTF-8 encoded:
FILE_CHARSET = 'utf-8'

# Specify the character mapping function for translation strings
# Add mappings for characters that may cause confusion
def custom_translation_string_character_mapping(string):
    return string.replace('\u0627', '\uFE8E')


TRANSLATION_STRING_CHARACTER_MAPPING_FUNCTION = custom_translation_string_character_mapping



# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'dashboard'

LOGIN_URL = 'login'
