import os
from .settings_secret import (
    MY_ALLOWED_HOSTS,
    MY_SECRET_KEY,
    PHONE_DATABASE_SETTINGS,
    PRIMARY_DATABASE_SETTINGS, 
)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = MY_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = False
ALLOWED_HOSTS = MY_ALLOWED_HOSTS

AUTH_USER_MODEL = 'authentication.CustomUser'


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'axes',
    'mptt',
    'polymorphic',
    'rest_framework',
    'sekizai',
    'sorl.thumbnail',
    'widget_tweaks',

    'website.apps.authentication',
    'website.apps.phone',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'website.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'website', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'sekizai.context_processors.sekizai',
            ],
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql_psycopg2',
       'NAME': PRIMARY_DATABASE_SETTINGS['name'],
       'USER': PRIMARY_DATABASE_SETTINGS['user'],
       'PASSWORD': PRIMARY_DATABASE_SETTINGS['password'],
       'HOST': 'localhost',
       'PORT': '5432',
   }
}


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/
LANGUAGE_CODE = 'en'
TIME_ZONE = 'Etc/UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')


LOGIN_URL = '/login/'


DATE_INPUT_FORMATS = [
    '%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y', # '2006-10-25', '25/10/2006', '25/10/06'
    '%b %d %Y', '%b %d, %Y',            # 'Oct 25 2006', 'Oct 25, 2006'
    '%d %b %Y', '%d %b, %Y',            # '25 Oct 2006', '25 Oct, 2006'
    '%B %d %Y', '%B %d, %Y',            # 'October 25 2006', 'October 25, 2006'
    '%d %B %Y', '%d %B, %Y',            # '25 October 2006', '25 October, 2006'
]



# AXES
AXES_USERNAME_FORM_FIELD = "email"
AXES_LOGIN_FAILURE_LIMIT = 5
AXES_BEHIND_REVERSE_PROXY = True
AXES_COOLOFF_TIME = 24
AXES_LOCKOUT_TEMPLATE = 'errors/axes_lockout.html'


# MAKE SESSION EXPIRE
SESSION_COOKIE_AGE = 60*60*1
SESSION_SAVE_EVERY_REQUEST = True


# PHONE DATABASE
PHONE_DATABASE = {
    'NAME': PHONE_DATABASE_SETTINGS['name'],
    'USER': PHONE_DATABASE_SETTINGS['user'],
    'PASSWORD': PHONE_DATABASE_SETTINGS['password'],
    'HOST': PHONE_DATABASE_SETTINGS['host'],
    'PORT': PHONE_DATABASE_SETTINGS['port'],
}

