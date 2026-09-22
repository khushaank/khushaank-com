from pathlib import Path
from django.core.exceptions import ValidationError
from django.db import models


def validate_media_file(value):
    allowed = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".webm", ".mov"}
    if Path(value.name).suffix.lower() not in allowed:
        raise ValidationError("Upload a JPEG, PNG, WebP, GIF, MP4, WebM, or MOV file.")


class MediaAsset(models.Model):
    class Kind(models.TextChoices): IMAGE = "image", "Image"; VIDEO = "video", "Video"
    file = models.FileField(upload_to="uploads/%Y/%m/", validators=[validate_media_file])
    kind = models.CharField(max_length=8, choices=Kind.choices, default=Kind.IMAGE)
    title = models.CharField(max_length=180, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.TextField(blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    poster = models.ImageField(upload_to="uploads/posters/%Y/%m/", blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        if self.kind == self.Kind.IMAGE and not self.alt_text:
            raise ValidationError({"alt_text": "Alt text is required for images."})

    def __str__(self): return self.title or self.file.name
