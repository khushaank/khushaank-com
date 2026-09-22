from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path
from blog.sitemaps import sitemaps
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls), path("", include("blog.urls")),
    path("robots.txt", core_views.robots, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
