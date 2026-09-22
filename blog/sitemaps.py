from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Entry, Guide


class EntrySitemap(Sitemap):
    changefreq = "weekly"
    def items(self): return Entry.objects.public()
    def lastmod(self, obj): return obj.updated_at

class GuideSitemap(Sitemap):
    changefreq = "monthly"
    def items(self): return Guide.objects.filter(is_draft=False)
    def lastmod(self, obj): return obj.updated_at

class StaticSitemap(Sitemap):
    def items(self): return ["home", "tag-list", "guides", "subscribe"]
    def location(self, item): return reverse(item)

sitemaps = {"entries": EntrySitemap, "guides": GuideSitemap, "static": StaticSitemap}
