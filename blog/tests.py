from datetime import timedelta
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from core.models import SiteSettings
from .models import Entry, Link, Note, Tag


class PublishingTests(TestCase):
    def setUp(self):
        self.now = timezone.now()
        self.tag = Tag.objects.create(name="AI", slug="ai")
        self.current = Entry.objects.create(title="Current published entry", slug="current", body="Useful searchable words", is_draft=False, published_at=self.now)
        self.current.tags.add(self.tag)
        self.old = Entry.objects.create(title="Old published entry", slug="old", body="Past", is_draft=False, published_at=self.now - timedelta(days=40))
        self.draft = Entry.objects.create(title="Secret draft", slug="secret", body="Private searchable words", is_draft=True, published_at=self.now)

    def test_home_shows_only_current_month_and_no_drafts(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, self.current.title)
        self.assertNotIn(self.old, [item for group in response.context["day_groups"] for item, _ in group[1]])
        self.assertNotContains(response, self.draft.title)

    def test_year_and_month_archives(self):
        response = self.client.get(reverse("year-archive", args=[self.now.year]))
        self.assertContains(response, self.current.title)
        month = self.now.strftime("%b").lower()
        self.assertContains(self.client.get(reverse("month-archive", args=[self.now.year, month])), self.current.title)

    def test_footer_years_are_automatic(self):
        settings = SiteSettings.load(); settings.start_year = self.now.year - 2; settings.save()
        response = self.client.get(reverse("home"))
        self.assertContains(response, str(self.now.year - 2))
        self.assertContains(response, str(self.now.year))

    def test_tag_search_feed_sitemap_and_dated_url(self):
        self.assertContains(self.client.get(reverse("tag-detail", args=["ai"])), self.current.title)
        self.assertContains(self.client.get(reverse("search"), {"q": "searchable"}), self.current.title)
        self.assertNotContains(self.client.get(reverse("search"), {"q": "Private"}), self.draft.title)
        self.assertContains(self.client.get(reverse("feed")), self.current.title)
        self.assertNotContains(self.client.get(reverse("feed")), self.draft.title)
        self.assertContains(self.client.get(reverse("sitemap")), self.current.get_absolute_url())
        self.assertEqual(self.client.get(self.current.get_absolute_url()).status_code, 200)

    def test_anonymous_admin_redirects(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)
