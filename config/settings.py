from pathlib import Path
import os
import sys
import dj_database_url

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

DATABASES = {"default": dj_database_url.config(
    default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
    conn_max_age=60,
    conn_health_checks=True,
)}
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
WHITENOISE_MANIFEST_STRICT = not DEBUG
WHITENOISE_USE_FINDERS = DEBUG
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage" if "test" in sys.argv else "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
if os.getenv("USE_S3_MEDIA", "False").lower() == "true":
    STORAGES["default"] = {"BACKEND": "storages.backends.s3.S3Storage", "OPTIONS": {
        "access_key": os.getenv("AWS_ACCESS_KEY_ID"), "secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "bucket_name": os.getenv("AWS_STORAGE_BUCKET_NAME"), "endpoint_url": os.getenv("AWS_S3_ENDPOINT_URL"),
        "region_name": os.getenv("AWS_S3_REGION_NAME"), "signature_version": "s3v4",
        "addressing_style": os.getenv("AWS_S3_ADDRESSING_STYLE", "path"),
        "querystring_auth": False, "file_overwrite": False,
        "custom_domain": os.getenv("MEDIA_CDN_DOMAIN") or None,
    }}

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
