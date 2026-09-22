from datetime import date
from .models import NavLink, SiteSettings


def site_context(request):
    settings = SiteSettings.load()
    return {"site_settings": settings, "nav_links": NavLink.objects.filter(enabled=True),
            "footer_years": range(settings.start_year, max(date.today().year, settings.start_year) + 1)}
