"""Settings for the django-bangla-admin demo project.

Mirrors the target end-user experience from the build spec: add the app before
django.contrib.admin, configure BANGLA_ADMIN, set up i18n the Django 4.2+ way.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-demo-key-not-for-production"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django_bangla_admin",          # BEFORE django.contrib.admin
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "shop",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",        # after Session, before Common
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_bangla_admin.middleware.HtmxShellMiddleware",  # strips shell on HX-Request
]

ROOT_URLCONF = "example_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django_bangla_admin.context_processors.bangla_admin",
            ],
        },
    },
]

WSGI_APPLICATION = "example_project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []

# --- i18n (Bangla default, cookie-based switching) ---
USE_I18N = True
USE_TZ = True
TIME_ZONE = "Asia/Dhaka"
LANGUAGE_CODE = "bn"
LANGUAGES = [("bn", "বাংলা"), ("en", "English")]

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- django-bangla-admin configuration ---
BANGLA_ADMIN = {
    "site_title": "Demo Shop Admin",
    "site_header": "Demo Shop",
    "site_brand": {"bn": "ডেমো শপ", "en": "Demo Shop"},
    "welcome_sign": {"bn": "স্বাগতম, ডেমো শপ অ্যাডমিনে", "en": "Welcome to Demo Shop Admin"},
    "default_language": "bn",
    "theme": "dark",
    "menu": [
        {"section": {"bn": "প্রধান", "en": "Main"}},
        {"label": {"bn": "ড্যাশবোর্ড", "en": "Dashboard"},
         "icon": "layout-dashboard", "url": "bangla_admin:index"},
        {"label": {"bn": "পণ্য", "en": "Products"}, "icon": "package", "model": "shop.Product"},
        {"label": {"bn": "ক্যাটাগরি", "en": "Categories"}, "icon": "tag", "model": "shop.Category"},
        {"label": {"bn": "অর্ডার", "en": "Orders"}, "icon": "shopping-cart", "model": "shop.Order"},
        {"section": {"bn": "সিস্টেম", "en": "System"}},
        {"label": {"bn": "ব্যবহারকারী", "en": "Users"}, "icon": "users", "model": "auth.User"},
        {"label": {"bn": "গ্রুপ", "en": "Groups"}, "icon": "shield", "model": "auth.Group"},
    ],
}
