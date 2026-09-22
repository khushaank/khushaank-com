from django.contrib import admin
from django.utils.html import format_html
from .models import Elsewhere, Entry, Guide, GuideChapter, Link, Note, Quote, Series, Tag


class PublishableAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_draft", "published_at", "updated_at", "preview_link")
    list_filter = ("is_draft", "published_at", "tags")
    search_fields = ("title", "body")
    filter_horizontal = ("tags",)
    readonly_fields = ("created_at", "updated_at")
    def preview_link(self, obj):
        if isinstance(obj, Entry): return format_html('<a href="{}" target="_blank">Preview</a>', f"/admin-preview/{obj.pk}/")
        return "Publish to view publicly"
    preview_link.short_description = "Preview"


@admin.register(Entry)
class EntryAdmin(PublishableAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "is_draft", "is_featured", "published_at", "preview_link")
    list_editable = ("is_featured",)
    search_fields = ("title", "body", "excerpt")
    readonly_fields = ("created_at", "updated_at", "word_count")
    fieldsets = (("Writing", {"fields": ("title", "slug", "body", "excerpt", "series", "tags")}), ("Publication", {"fields": ("is_draft", "published_at", "is_featured", "hero_image")}), ("Search and sharing", {"fields": ("seo_title", "seo_description", "canonical_url")}), ("Record", {"fields": ("created_at", "updated_at", "word_count")}))


@admin.register(Link)
class LinkAdmin(PublishableAdmin):
    search_fields = ("title", "commentary", "url")


@admin.register(Quote)
class QuoteAdmin(PublishableAdmin):
    search_fields = ("quotation", "source", "commentary")


@admin.register(Note)
class NoteAdmin(PublishableAdmin):
    search_fields = ("title", "body")


class ChapterInline(admin.TabularInline):
    model = GuideChapter
    extra = 0


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    inlines = [ChapterInline]

admin.site.register([GuideChapter, Series, Tag, Elsewhere])
