from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"), path("search/", views.search, name="search"),
    path("feed/", views.AllContentFeed(), name="feed"), path("atom/", views.AtomContentFeed(), name="atom"),
    path("feed/entries/", views.EntryFeed(), name="entry-feed"), path("subscribe/", views.subscribe, name="subscribe"),
    path("tags/", views.tag_list, name="tag-list"), path("tags/<slug:slug>/", views.tag_detail, name="tag-detail"),
    path("guides/", views.guides, name="guides"), path("guides/<slug:slug>/", views.guide_detail, name="guide-detail"),
    path("guides/<slug:guide_slug>/<slug:slug>/", views.chapter_detail, name="chapter-detail"),
    path("entries/", views.content_list, {"kind": "entries"}, name="entries"), path("links/", views.content_list, {"kind": "links"}, name="links"), path("quotes/", views.content_list, {"kind": "quotes"}, name="quotes"), path("notes/", views.content_list, {"kind": "notes"}, name="notes"), path("elsewhere/", views.content_list, {"kind": "elsewhere"}, name="elsewhere"),
    path("admin-preview/<int:pk>/", views.entry_preview, name="entry-preview"),
    path("<int:year>/<str:month>/<int:day>/<slug:slug>/", views.EntryDetailView.as_view(), name="entry-detail"),
    path("<int:year>/<str:month>/", views.month_archive, name="month-archive"), path("<int:year>/", views.year_archive, name="year-archive"),
    path("<slug:slug>/", views.page_detail, name="page-detail"),
]
