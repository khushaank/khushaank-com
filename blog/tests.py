from datetime import timedelta
import os
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from core.models import Page, SiteSettings
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
        self.assertEqual(response.context["site_settings"].site_title, "Khushaank's Blog")
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

    def test_about_page_uses_owner_copy(self):
        response = self.client.get("/about/")
        self.assertContains(response, "Hey, I’m Khushaank.")
        self.assertEqual(Page.objects.get(slug="about").title, "About")

    def test_ensure_superuser_only_creates_once(self):
        variables = {"DJANGO_SUPERUSER_USERNAME": "render-admin", "DJANGO_SUPERUSER_EMAIL": "admin@example.test", "DJANGO_SUPERUSER_PASSWORD": "first-safe-password"}
        previous = {key: os.environ.get(key) for key in variables}
        os.environ.update(variables)
        try:
            call_command("ensure_superuser")
            admin = User.objects.get(username="render-admin")
            self.assertTrue(admin.check_password("first-safe-password"))
            os.environ["DJANGO_SUPERUSER_PASSWORD"] = "do-not-overwrite"
            call_command("ensure_superuser")
            admin.refresh_from_db()
            self.assertTrue(admin.check_password("first-safe-password"))
        finally:
            for key, value in previous.items():
                if value is None: os.environ.pop(key, None)
                else: os.environ[key] = value
