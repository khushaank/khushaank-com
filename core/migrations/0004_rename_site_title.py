from django.db import migrations, models


OLD_TITLES = ("Khushaank Gupta's Weblog", "Khushaank Gupta's Blog")
NEW_TITLE = "Khushaank's Blog"


def rename_site_title(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(pk=1, site_title__in=OLD_TITLES).update(site_title=NEW_TITLE)


def restore_site_title(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(pk=1, site_title=NEW_TITLE).update(site_title=OLD_TITLES[0])


class Migration(migrations.Migration):
    dependencies = [("core", "0003_add_khushaank_about_page")]
    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="site_title",
            field=models.CharField(default=NEW_TITLE, max_length=120),
        ),
        migrations.RunPython(rename_site_title, restore_site_title),
    ]
