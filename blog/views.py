from calendar import month_abbr, month_name
from datetime import datetime, timedelta
from itertools import chain
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.decorators.cache import cache_control
from django.views.generic import DetailView, ListView
from django.contrib.syndication.views import Feed
from django.contrib.admin.views.decorators import staff_member_required
from core.models import Page, SponsorMessage
from .models import Elsewhere, Entry, Guide, GuideChapter, Link, Note, Quote, Tag
from .services import TIMELINE_MODELS, group_by_day, month_counts, public_timeline, tag_counts


def month_number(value):
    try: return [x.lower() for x in month_abbr].index(value.lower())
    except ValueError: raise Http404("Unknown month")


def active_sponsor():
    now = timezone.now()
    return SponsorMessage.objects.filter(enabled=True).filter(Q(active_from__isnull=True) | Q(active_from__lte=now)).filter(Q(active_until__isnull=True) | Q(active_until__gte=now)).first()


def timeline_sort_date(pair):
    item = pair[0]
    return item.published_at if hasattr(item, "published_at") else timezone.make_aware(datetime.combine(item.date, datetime.min.time()))


@cache_control(public=True, max_age=300)
def home(request):
    now = timezone.localtime()
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    important_tags = sorted(tag_counts(), key=lambda item: (-item[1], item[0].name))[:int(request.GET.get("tag_limit", 8))]
    featured = list(Entry.objects.public().filter(is_featured=True)[:8])
    if len(featured) < 8:
        seen = {entry.pk for entry in featured}
        featured += list(Entry.objects.public().exclude(pk__in=seen)[:8 - len(featured)])
    return render(request, "blog/home.html", {"day_groups": group_by_day(public_timeline(start=start, end=now + timedelta(seconds=1))), "important_tags": important_tags, "highlights": featured, "sponsor": active_sponsor(), "current_month": now})


@cache_control(public=True, max_age=600)
def year_archive(request, year):
    months = []
    for month in range(1, 13):
        start = timezone.make_aware(datetime(year, month, 1))
        end = timezone.make_aware(datetime(year + (month == 12), (month % 12) + 1, 1))
        items = public_timeline(start, end)
        elsewhere = Elsewhere.objects.filter(date__gte=start.date(), date__lt=end.date()).prefetch_related("tags")
        if items or elsewhere:
            months.append({"name": month_name[month], "number": month, "counts": month_counts(year, month), "items": sorted(items + [(x, "elsewhere") for x in elsewhere], key=timeline_sort_date)})
    return render(request, "blog/year_archive.html", {"archive_year": year, "months": months})


@cache_control(public=True, max_age=600)
def month_archive(request, year, month):
    number = month_number(month)
    start = timezone.make_aware(datetime(year, number, 1))
    end = timezone.make_aware(datetime(year + (number == 12), (number % 12) + 1, 1))
    prev_value = (start - timedelta(days=1))
    next_value = end
    return render(request, "blog/month_archive.html", {"archive_month": start, "counts": month_counts(year, number), "day_groups": group_by_day(public_timeline(start, end)), "previous": prev_value, "next": next_value})


class EntryDetailView(DetailView):
    template_name = "blog/entry_detail.html"
    context_object_name = "entry"
    def get_queryset(self): return Entry.objects.public().prefetch_related("tags")
    def get_object(self, queryset=None):
        return get_object_or_404(self.get_queryset(), slug=self.kwargs["slug"], published_at__year=self.kwargs["year"], published_at__month=month_number(self.kwargs["month"]), published_at__day=self.kwargs["day"])
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = self.object
        context["previous_entry"] = Entry.objects.public().filter(published_at__lt=entry.published_at).first()
        context["next_entry"] = Entry.objects.public().filter(published_at__gt=entry.published_at).last()
        context["related"] = Entry.objects.public().filter(tags__in=entry.tags.all()).exclude(pk=entry.pk).distinct()[:4]
        return context


@staff_member_required
def entry_preview(request, pk):
    entry = get_object_or_404(Entry.objects.prefetch_related("tags"), pk=pk)
    return render(request, "blog/entry_detail.html", {"entry": entry, "preview": True})


def content_list(request, kind):
    models = {"entries": Entry, "links": Link, "quotes": Quote, "notes": Note, "elsewhere": Elsewhere}
    model = models.get(kind)
    if not model: raise Http404
    objects = model.objects.public() if hasattr(model.objects, "public") else model.objects.all()
    return render(request, "blog/content_list.html", {"kind": kind, "items": objects.prefetch_related("tags")})


def tag_list(request): return render(request, "blog/tag_list.html", {"tag_counts": sorted(tag_counts(), key=lambda row: row[0].name.lower())})


def tag_detail(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    return render(request, "blog/tag_detail.html", {"tag": tag, "day_groups": group_by_day(public_timeline(tag=tag)), "count": len(public_timeline(tag=tag))})


def guides(request): return render(request, "blog/guides.html", {"guides": Guide.objects.filter(is_draft=False, published_at__lte=timezone.now()).prefetch_related("tags")})


def guide_detail(request, slug):
    return render(request, "blog/guide_detail.html", {"guide": get_object_or_404(Guide, slug=slug, is_draft=False, published_at__lte=timezone.now())})


def chapter_detail(request, guide_slug, slug):
    return render(request, "blog/chapter_detail.html", {"chapter": get_object_or_404(GuideChapter, guide__slug=guide_slug, guide__is_draft=False, slug=slug)})


def search(request):
    query = request.GET.get("q", "").strip()
    content_type = request.GET.get("type", "")
    result_groups = []
    if query:
        for model, kind in TIMELINE_MODELS:
            if content_type and content_type != kind: continue
            base = model.objects.public().prefetch_related("tags")
            if connection.vendor == "postgresql":
                vector = SearchVector("title", weight="A") if kind in {"entry", "link", "note"} else SearchVector("source", weight="B")
                body_field = "body" if kind in {"entry", "note"} else "commentary"
                rows = base.annotate(rank=SearchRank(vector + SearchVector(body_field, weight="C"), SearchQuery(query))).filter(rank__gt=0).order_by("-rank", "-published_at")
            else:
                fields = Q(tags__name__icontains=query)
                for field in ("title", "body", "commentary", "quotation", "source"):
                    if any(field == f.name for f in model._meta.fields): fields |= Q(**{f"{field}__icontains": query})
                rows = base.filter(fields).distinct()
            result_groups.extend((row, kind) for row in rows)
        result_groups.sort(key=lambda row: row[0].published_at, reverse=request.GET.get("sort") == "date")
    return render(request, "blog/search.html", {"query": query, "results": result_groups, "result_count": len(result_groups)})


def page_detail(request, slug):
    return render(request, "blog/page.html", {"page": get_object_or_404(Page, slug=slug, is_draft=False)})


def subscribe(request): return render(request, "blog/subscribe.html")


class AllContentFeed(Feed):
    title = "Khushaank's Blog"
    link = "/"
    description = "Recent writing and notes."
    def items(self): return [item for item, _ in public_timeline()[:30]]
    def item_title(self, item): return getattr(item, "title", None) or getattr(item, "source", "Note")
    def item_description(self, item): return getattr(item, "excerpt", "") or getattr(item, "body", "") or getattr(item, "commentary", "") or getattr(item, "quotation", "")
    def item_link(self, item): return item.get_absolute_url() if hasattr(item, "get_absolute_url") else "/"
    def item_pubdate(self, item): return item.published_at


class EntryFeed(AllContentFeed):
    def items(self): return Entry.objects.public()[:30]


class AtomContentFeed(AllContentFeed):
    feed_type = "atom"
