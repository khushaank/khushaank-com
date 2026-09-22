from pathlib import Path
from urllib.parse import urlparse
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "development-only-change-me")
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if host.strip()]
TIME_ZONE = os.getenv("TIME_ZONE", "Asia/Kolkata")
USE_TZ = True
LANGUAGE_CODE = "en-us"

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "django.contrib.sites", "django.contrib.sitemaps", "django.contrib.postgres",
    "core", "blog", "media_library",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages", "core.context_processors.site_context",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"

def database_from_url(url):
    if not url:
        return {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
    parsed = urlparse(url)
    return {"ENGINE": "django.db.backends.postgresql", "NAME": parsed.path.lstrip("/"), "USER": parsed.username,
            "PASSWORD": parsed.password, "HOST": parsed.hostname, "PORT": parsed.port or 5432,
            "CONN_MAX_AGE": 60}

DATABASES = {"default": database_from_url(os.getenv("DATABASE_URL", ""))}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
if os.getenv("USE_S3_MEDIA", "False").lower() == "true":
    STORAGES = {"default": {"BACKEND": "storages.backends.s3.S3Storage", "OPTIONS": {
        "access_key": os.getenv("AWS_ACCESS_KEY_ID"), "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "bucket_name": os.getenv("AWS_STORAGE_BUCKET_NAME"), "endpoint_url": os.getenv("AWS_S3_ENDPOINT_URL"),
        "region_name": os.getenv("AWS_S3_REGION_NAME"), "custom_domain": os.getenv("MEDIA_CDN_DOMAIN") or None,
    }}, "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}}

SITE_ID = 1
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_URL = "/admin/login/"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
