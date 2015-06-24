import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.staticfiles',

    'django_select2',
    'tests.testapp',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

SITE_ID = 1
ROOT_URLCONF = 'tests.testapp.urls'

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, "templates"),
)

SECRET_KEY = '123456'

USE_L10N = True

AUTO_RENDER_SELECT2_STATICS = False
