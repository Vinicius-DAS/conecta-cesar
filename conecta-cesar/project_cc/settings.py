import os
from pathlib import Path

from django.core.management.utils import get_random_secret_key
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

TARGET_ENV = os.getenv('TARGET_ENV')
NOT_PROD = not (TARGET_ENV and TARGET_ENV.lower().startswith('prod'))

if NOT_PROD:
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True
    # Falls back to a freshly generated key so local dev works out of the
    # box with no setup; set SECRET_KEY in .env if you need it stable
    # across restarts (e.g. to keep sessions alive).
    SECRET_KEY = os.getenv('SECRET_KEY') or get_random_secret_key()
    ALLOWED_HOSTS = []
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = os.getenv('DEBUG', '0').lower() in ['true', 't', '1']
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(' ')
    CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS').split(' ')

    SECURE_SSL_REDIRECT = \
        os.getenv('SECURE_SSL_REDIRECT', '0').lower() in ['true', 't', '1']

    if SECURE_SSL_REDIRECT:
        SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DBNAME'),
            'HOST': os.environ.get('DBHOST'),
            'USER': os.environ.get('DBUSER'),
            'PASSWORD': os.environ.get('DBPASS'),
            'OPTIONS': {'sslmode': 'require'},
        }
    }

    # Render's free-plan disk isn't persistent across deploys, so
    # user-uploaded files (profile photos, atividades, etc.) would
    # otherwise vanish every time the service redeploys. Routing MEDIA
    # through an S3-compatible bucket (e.g. Neon Object Storage) keeps
    # them around. Optional: falls back to the local filesystem (and a
    # local media/ dir that doesn't survive redeploys) if these aren't
    # set, so a bare prod deploy without a bucket configured still works.
    # NOTE: the old `DEFAULT_FILE_STORAGE = '...'` switch no longer does
    # anything as of Django 6.1 — that legacy setting was dropped, with
    # no automatic bridge into the STORAGES dict. The actual backend
    # selection based on AWS_S3_ACCESS_KEY_ID happens down at STORAGES,
    # near MEDIA_ROOT/STATIC_ROOT (this flag just has to be read up here,
    # before DATABASES-adjacent env vars go out of scope for this branch).
    AWS_S3_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    if AWS_S3_ACCESS_KEY_ID:
        AWS_STORAGE_BUCKET_NAME = 'uploads'
        AWS_S3_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
        AWS_S3_ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL_S3')
        AWS_S3_REGION_NAME = os.environ.get('AWS_REGION')
        # No per-object ACL header: the bucket is already private at the
        # bucket level (set when it was created), and it's not confirmed
        # this S3-compatible provider supports per-object ACLs at all —
        # leaving AWS_DEFAULT_ACL unset avoids sending one.
        # Signed, temporary URLs on every read (bucket has no public access).
        AWS_QUERYSTRING_AUTH = True
        # Don't silently overwrite an existing object with the same name
        # (e.g. two different students both uploading "foto.png").
        AWS_S3_FILE_OVERWRITE = False

# Application definition

INSTALLED_APPS = [
    'app_cc.apps.AppCcConfig',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    #Adicionar whitenoise na lista de aplicativos instalados
    "whitenoise.runserver_nostatic",
    'users'
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Add whitenoise middleware after the security middleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

INTERNAL_IPS = []

# debug_toolbar was previously installed unconditionally, meaning it (and
# the debug pages it exposes) ran even when DEBUG was meant to be off.
# Only wire it in for real local development now — DISABLE_DEBUG_TOOLBAR
# additionally opts out even in DEBUG mode, since the toolbar's floating
# "Hide »" button overlaps nav elements and breaks Cypress's cy.click()
# (this is why the E2E suite has never actually passed against a normal
# dev server; the CI workflow sets this when running Cypress).
DISABLE_DEBUG_TOOLBAR = os.getenv('DISABLE_DEBUG_TOOLBAR', '0').lower() in ['true', 't', '1']
if DEBUG and not DISABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS.append('127.0.0.1')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages'

            ],
        },
    },
]

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


ROOT_URLCONF = 'project_cc.urls'

# Redirects back to the same page with a flash message instead of
# Django's default 403 page when a request fails CSRF validation
# (e.g. an expired session, or a form left open too long).
CSRF_FAILURE_VIEW = 'project_cc.views.csrf_failure'

WSGI_APPLICATION = 'project_cc.wsgi.application'

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

MEDIA_ROOT=os.path.join(BASE_DIR, 'media')
MEDIA_URL="media/"

FILE_UPLOAD_MAX_MEMORY_SIZE=2500000 #Padrão 2,5MB

# django-storages' individual AWS_S3_* settings above (bucket, keys,
# endpoint, region) are read directly by the S3 backend regardless of
# STORAGES — but which backend actually runs is decided here.
STORAGES = {
    "default": {
        "BACKEND": (
            "storages.backends.s3.S3Storage"
            if (not NOT_PROD and AWS_S3_ACCESS_KEY_ID)
            else "django.core.files.storage.FileSystemStorage"
        ),
    },
    # The compressed+hashed manifest storage requires collectstatic to
    # have already run (render.yaml's buildCommand does this) — its
    # manifest file doesn't exist for a plain local runserver/test run,
    # so only use it in prod. Dev falls back to Django's plain storage.
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
            if not NOT_PROD
            else "django.contrib.staticfiles.storage.StaticFilesStorage"
        ),
    },
}

LANGUAGE_CODE = 'pt'

LANGUAGES=(
    ('pt', u'Português'),
    ('en', u'Inglês'),
    ('es', u'Espanhol'),
)
LOCALE_PATHS=(
    os.path.join(BASE_DIR, 'locale/'),
)
TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Mensagens:
from django.contrib.messages import constants

MESSAGE_TAGS = {
    constants.ERROR: 'error',
    constants.SUCCESS: 'sucesso',
    constants.INFO: 'info',
    constants.WARNING: 'warning',
    constants.DEBUG: 'debug',
}
