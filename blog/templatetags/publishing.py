import re
import bleach
import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()
ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {"p", "h1", "h2", "h3", "h4", "pre", "code", "table", "thead", "tbody", "tr", "th", "td", "blockquote", "hr", "img", "figure", "figcaption", "video", "source"}
ALLOWED_ATTRS = {**bleach.sanitizer.ALLOWED_ATTRIBUTES, "*": ["class", "id"], "a": ["href", "title", "rel"], "img": ["src", "alt", "title", "width", "height", "loading"], "video": ["src", "controls", "poster", "preload"], "source": ["src", "type"]}


@register.filter
def markdownify(value):
    rendered = markdown.markdown(value or "", extensions=["fenced_code", "tables", "codehilite", "sane_lists"])
    return mark_safe(bleach.clean(rendered, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, protocols=["http", "https", "mailto"]))


@register.filter
def display_title(item):
    return getattr(item, "title", "") or ("Note" if hasattr(item, "body") else str(item))


@register.filter
def content_date(item):
    return getattr(item, "published_at", getattr(item, "date", None))


@register.filter
def archive_counts(counts):
    labels = {"entry": ("entry", "entries"), "link": ("link", "links"), "quote": ("quote", "quotes"), "note": ("note", "notes")}
    return ", ".join(f"{count} {labels[kind][count != 1]}" for kind, count in counts.items() if count)


@register.filter
def video_embed(url):
    if not url: return ""
    match = re.search(r"(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)", url)
    if match:
        return mark_safe(f'<iframe class="video-embed" src="https://www.youtube-nocookie.com/embed/{match.group(1)}" title="Embedded YouTube video" loading="lazy" allowfullscreen></iframe>')
    match = re.search(r"vimeo\.com/(\d+)", url)
    if match:
        return mark_safe(f'<iframe class="video-embed" src="https://player.vimeo.com/video/{match.group(1)}" title="Embedded Vimeo video" loading="lazy" allowfullscreen></iframe>')
    return ""
