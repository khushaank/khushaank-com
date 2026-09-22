from django.db import migrations


def create_defaults(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    NavLink = apps.get_model("core", "NavLink")
    SiteSettings.objects.get_or_create(pk=1)
    for label, url, position in [("About", "/about/", 1), ("Subscribe", "/subscribe/", 2), ("TILs", "/notes/", 3), ("Tools", "/guides/", 4)]:
        NavLink.objects.get_or_create(label=label, defaults={"url": url, "position": position})


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]
    operations = [migrations.RunPython(create_defaults, migrations.RunPython.noop)]
