from django.db import models


class SiteSettings(models.Model):
    site_title = models.CharField(max_length=120, default="Khushaank's Blog")
    short_description = models.CharField(max_length=255, default="Notes, essays and useful things by Khushaank Gupta.")
    author_name = models.CharField(max_length=120, default="Khushaank Gupta")
    start_year = models.PositiveSmallIntegerField(default=2026)
    base_url = models.URLField(default="http://localhost:8000")
    default_seo_description = models.TextField(blank=True)
    default_social_image = models.ImageField(upload_to="site/", blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    newsletter_url = models.URLField(blank=True)
    footer_disclosure = models.TextField(blank=True)
    colophon = models.TextField(blank=True)

    class Meta:
        verbose_name = "site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.get_or_create(pk=1)[0]

    def __str__(self):
        return self.site_title


class NavLink(models.Model):
    label = models.CharField(max_length=40)
    url = models.CharField(max_length=255)
    position = models.PositiveSmallIntegerField(default=0)
    enabled = models.BooleanField(default=True)

    class Meta:
        ordering = ("position", "label")

    def __str__(self): return self.label


class SponsorMessage(models.Model):
    sponsor_name = models.CharField(max_length=120)
    message = models.CharField(max_length=300)
    url = models.URLField(blank=True)
    active_from = models.DateTimeField(null=True, blank=True)
    active_until = models.DateTimeField(null=True, blank=True)
    enabled = models.BooleanField(default=True)
    color_scheme = models.CharField(max_length=20, default="blue")

    def __str__(self): return self.sponsor_name


class Page(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    is_draft = models.BooleanField(default=False)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self): return self.title
