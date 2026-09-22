import re
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self): return self.name


class Series(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    def __str__(self): return self.name


class PublishedQuerySet(models.QuerySet):
    def public(self): return self.filter(is_draft=False, published_at__lte=timezone.now())


class Publishable(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    is_draft = models.BooleanField(default=True, db_index=True)
    tags = models.ManyToManyField(Tag, blank=True)
    objects = PublishedQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ("-published_at",)

    @property
    def is_public(self): return not self.is_draft and self.published_at <= timezone.now()


class Entry(Publishable):
    title = models.CharField(max_length=180)
    slug = models.SlugField()
    body = models.TextField()
    excerpt = models.TextField(blank=True)
    series = models.ForeignKey(Series, null=True, blank=True, on_delete=models.SET_NULL, related_name="entries")
    is_featured = models.BooleanField(default=False, db_index=True)
    hero_image = models.ImageField(upload_to="entries/%Y/%m/", blank=True)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.TextField(blank=True)
    canonical_url = models.URLField(blank=True)
    word_count = models.PositiveIntegerField(default=0, editable=False)

    class Meta(Publishable.Meta):
        constraints = [models.UniqueConstraint(fields=("slug", "published_at"), name="unique_entry_slug_date")]
        indexes = [models.Index(fields=("is_draft", "published_at")), models.Index(fields=("is_featured", "published_at"))]

    def save(self, *args, **kwargs):
        self.word_count = len(re.findall(r"\w+", self.body))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("entry-detail", kwargs={"year": self.published_at.year, "month": self.published_at.strftime("%b").lower(), "day": self.published_at.day, "slug": self.slug})

    def __str__(self): return self.title


class Link(Publishable):
    title = models.CharField(max_length=180)
    url = models.URLField()
    commentary = models.TextField(blank=True)
    image = models.ImageField(upload_to="links/%Y/%m/", blank=True)
    slug = models.SlugField(blank=True)

    def __str__(self): return self.title


class Quote(Publishable):
    quotation = models.TextField()
    source = models.CharField(max_length=180)
    source_url = models.URLField(blank=True)
    commentary = models.TextField(blank=True)

    def __str__(self): return f"{self.source}: {self.quotation[:50]}"


class Note(Publishable):
    title = models.CharField(max_length=180, blank=True)
    body = models.TextField()
    image = models.ImageField(upload_to="notes/%Y/%m/", blank=True)
    video_url = models.URLField(blank=True)

    def __str__(self): return self.title or self.body[:60]


class Guide(models.Model):
    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    is_draft = models.BooleanField(default=True, db_index=True)
    published_at = models.DateTimeField(default=timezone.now, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True)
    seo_title = models.CharField(max_length=160, blank=True)
    seo_description = models.TextField(blank=True)

    def get_absolute_url(self): return reverse("guide-detail", kwargs={"slug": self.slug})
    def __str__(self): return self.title

    class Meta:
        ordering = ("-published_at",)


class GuideChapter(models.Model):
    guide = models.ForeignKey(Guide, on_delete=models.CASCADE, related_name="chapters")
    number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=180)
    slug = models.SlugField()
    body = models.TextField()
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ("number",)
        constraints = [models.UniqueConstraint(fields=("guide", "slug"), name="unique_chapter_slug_per_guide")]

    def get_absolute_url(self): return reverse("chapter-detail", kwargs={"guide_slug": self.guide.slug, "slug": self.slug})
    def __str__(self): return f"{self.guide}: {self.number}. {self.title}"


class Elsewhere(models.Model):
    class AppearanceType(models.TextChoices):
        PODCAST = "podcast", "Podcast"; INTERVIEW = "interview", "Interview"; ARTICLE = "article", "Article"; VIDEO = "video", "Video"; EVENT = "event", "Event"; OTHER = "other", "Other"
    title = models.CharField(max_length=180)
    url = models.URLField()
    date = models.DateField(db_index=True)
    description = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=AppearanceType.choices, default=AppearanceType.OTHER)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta: ordering = ("-date",)
    def __str__(self): return self.title
