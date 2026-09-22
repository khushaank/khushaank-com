from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from blog.models import Entry, Guide, GuideChapter, Link, Note, Quote, Series, Tag
from core.models import NavLink, Page, SiteSettings


class Command(BaseCommand):
    help = "Create original demo publishing content for local development."
    def handle(self, *args, **options):
        SiteSettings.load()
        for label, url, position in [("About", "/about/", 1), ("Subscribe", "/subscribe/", 2), ("TILs", "/notes/", 3), ("Tools", "/guides/", 4)]:
            NavLink.objects.get_or_create(label=label, defaults={"url": url, "position": position})
        tags = {name: Tag.objects.get_or_create(name=name.title(), slug=name)[0] for name in ("ai", "business", "chess", "technology")}
        series, _ = Series.objects.get_or_create(name="Notes on making", slug="notes-on-making")
        now = timezone.now()
        entry, _ = Entry.objects.get_or_create(slug="a-small-system-for-better-notes", published_at__date=now.date(), defaults={"title": "A small system for better notes", "body": "Writing in public works best when the friction is low.\n\n## The useful default\n\nKeep the idea, its source, and one next question.", "excerpt": "A practical, lightweight note-taking loop.", "is_draft": False, "published_at": now, "is_featured": True, "series": series})
        entry.tags.set([tags["technology"], tags["ai"]])
        for days, title in [(2, "Choosing useful constraints"), (9, "The case for public working notes"), (23, "A reading queue that stays small")]:
            stamp = now - timedelta(days=days)
            item, _ = Entry.objects.get_or_create(slug=title.lower().replace(" ", "-"), published_at__date=stamp.date(), defaults={"title": title, "body": "An original demo entry for this publishing system.", "excerpt": "A brief thought worth keeping.", "is_draft": False, "published_at": stamp})
            item.tags.set([tags["technology"]])
        for model, defaults in [(Link, {"title": "A clear essay about tools", "url": "https://example.com", "commentary": "A useful perspective on building calmly."}), (Note, {"title": "Small note", "body": "A good publishing system should make a small thought easy to share."}), (Quote, {"quotation": "Make the useful thing easy to find again.", "source": "An old notebook"})]:
            obj, _ = model.objects.get_or_create(published_at__date=now.date(), defaults={**defaults, "is_draft": False, "published_at": now})
            obj.tags.set([tags["technology"]])
        guide, _ = Guide.objects.get_or_create(slug="writing-on-the-web", defaults={"title": "Writing on the web", "description": "A short original guide to a useful publishing practice.", "is_draft": False, "published_at": now})
        GuideChapter.objects.get_or_create(guide=guide, slug="start-small", defaults={"number": 1, "title": "Start small", "body": "Publish a thought before you build a content machine."})
        Page.objects.get_or_create(slug="about", defaults={"title": "About", "body": "This is Khushaank Gupta's space for notes, essays and useful links.", "is_draft": False})
        self.stdout.write(self.style.SUCCESS("Demo content is ready."))
