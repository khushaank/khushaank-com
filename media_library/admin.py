from django.contrib import admin
from .models import MediaAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("__str__", "kind", "uploaded_at")
    list_filter = ("kind",)
    search_fields = ("title", "alt_text", "caption")
