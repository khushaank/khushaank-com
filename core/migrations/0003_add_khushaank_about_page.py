from django.db import migrations


ABOUT_BODY = """Hey, I’m Khushaank.

I’m usually somewhere between studying finance, messing around with AI, building random things on the internet, and writing thoughts in a notebook that nobody else will probably ever read.

I like understanding how things work — businesses, money, people, technology, even myself sometimes. I tend to observe a lot, overthink a little, and get randomly obsessed with ideas until I end up trying to build something out of them.

Outside of that, I’m into good food, chess, music, books, late-night thinking, and conversations that actually go somewhere.

I don’t really have everything figured out yet, and I’m not pretending to. This blog is a place for whatever I’m learning, thinking about, building, questioning, or finding interesting at the time.

That’s pretty much it."""


def add_about_page(apps, schema_editor):
    Page = apps.get_model("core", "Page")
    Page.objects.update_or_create(
        slug="about",
        defaults={
            "title": "About",
            "body": ABOUT_BODY,
            "is_draft": False,
            "seo_title": "About Khushaank Gupta",
            "seo_description": "A little about Khushaank Gupta and this weblog.",
        },
    )


class Migration(migrations.Migration):
    dependencies = [("core", "0002_default_settings_and_nav")]
    operations = [migrations.RunPython(add_about_page, migrations.RunPython.noop)]
