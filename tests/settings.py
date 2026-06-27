"""Minimal settings for running the django-bangla-admin test suite."""

SECRET_KEY = "test-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django_bangla_admin",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django_bangla_admin.middleware.HtmxShellMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django_bangla_admin.context_processors.bangla_admin",
            ],
        },
    },
]

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

USE_I18N = True
USE_TZ = True
LANGUAGE_CODE = "bn"
LANGUAGES = [("bn", "বাংলা"), ("en", "English")]
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

BANGLA_ADMIN = {
    "site_title": "Test Admin",
    "menu": [
        {"section": {"bn": "প্রধান", "en": "Main"}},
        {"label": {"bn": "ড্যাশবোর্ড", "en": "Dashboard"}, "icon": "layout-dashboard", "url": "bangla_admin:index"},
        {"label": {"bn": "ব্যবহারকারী", "en": "Users"}, "icon": "users", "model": "auth.User"},
    ],
}
