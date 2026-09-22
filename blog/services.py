from collections import defaultdict
from datetime import datetime
from django.db.models import Count, Q
from django.utils import timezone
from .models import Elsewhere, Entry, Link, Note, Quote, Tag


TIMELINE_MODELS = ((Entry, "entry"), (Link, "link"), (Quote, "quote"), (Note, "note"))


def public_timeline(start=None, end=None, tag=None):
    items = []
    for model, kind in TIMELINE_MODELS:
        query = model.objects.public().prefetch_related("tags")
        if start: query = query.filter(published_at__gte=start)
        if end: query = query.filter(published_at__lt=end)
        if tag: query = query.filter(tags=tag)
        items.extend((item, kind) for item in query)
    return sorted(items, key=lambda pair: pair[0].published_at, reverse=True)


def group_by_day(items):
    groups = defaultdict(list)
    for item, kind in items:
        groups[timezone.localtime(item.published_at).date()].append((item, kind))
    return [(day, groups[day]) for day in sorted(groups, reverse=True)]


def tag_counts():
    # A compact aggregation avoids a per-tag query while counting every public timeline type.
    counts = defaultdict(int)
    for model, _ in TIMELINE_MODELS:
        for row in model.objects.public().values("tags").annotate(total=Count("pk")):
            if row["tags"]: counts[row["tags"]] += row["total"]
    tags = Tag.objects.in_bulk(counts.keys())
    return [(tags[pk], total) for pk, total in counts.items()]


def month_counts(year, month):
    start = timezone.make_aware(datetime(year, month, 1))
    end = timezone.make_aware(datetime(year + (month == 12), (month % 12) + 1, 1))
    return {kind: model.objects.public().filter(published_at__gte=start, published_at__lt=end).count() for model, kind in TIMELINE_MODELS}
