# Khushaank Gupta's Weblog

A fast, server-rendered personal publishing system: Django templates, PostgreSQL search, plain CSS and a small theme-toggle script. Content is authored in Django Admin using Markdown; public pages work without JavaScript.

## Run locally

### Docker (recommended)

1. Copy `.env.example` to `.env` and replace `SECRET_KEY` before deploying.
2. Run `docker compose up --build`.
3. Open <http://localhost:8000/>. Demo data is added automatically.
4. In another terminal run `docker compose exec web python manage.py createsuperuser`, then sign in at <http://localhost:8000/admin/>.

### Python on Windows

PostgreSQL is the supported production database. For a quick local preview, the app uses `db.sqlite3` when `DATABASE_URL` is unset:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

To use local PostgreSQL, set `DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/weblog` before `migrate`. The Docker setup is the easiest way to get it running.

## Publishing

In `/admin/`, choose **Entries → Add Entry**. Add a title, Markdown body, tags and a publication time. Leave **Is draft** enabled while writing; clear it to publish. A published item appears on the home page only when its publish date is in the current month, but is always available from its dated URL and archive.

Upload images or videos under **Media assets**. Images require alt text. For Markdown images, copy the media URL and use `![descriptive alt](url)`. Use normal Markdown for headings, links, lists, tables, quotes and fenced code. Uploaded videos are served from configured media storage; for very large video, use YouTube/Vimeo and link or embed through a provider. Configure `USE_S3_MEDIA=True` and the `AWS_*` / `MEDIA_CDN_DOMAIN` variables for S3, R2 or compatible production media.

Tags are managed under **Tags** and are automatically indexed at `/tags/`. Year and month archives, footer years, RSS/Atom, sitemap, and feeds update from published timestamps without manual edits. Search uses PostgreSQL full-text ranking in production; the SQLite development fallback provides case-insensitive search.

## Test and deploy

Run `python manage.py test`. The suite covers current-month visibility, draft exclusion, archive grouping/counts, footer years, tags, search, feeds, dated URLs, sitemap and admin protection.

For production set `DEBUG=False`, a unique `SECRET_KEY`, `ALLOWED_HOSTS`, `SITE_URL`, `DATABASE_URL`, HTTPS at your proxy/platform, and object-storage variables if media is uploaded. Run:

```sh
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

Cloudflare may cache anonymous public HTML (the app sends a short public cache policy) but must bypass `/admin/` and authenticated preview/admin traffic. WhiteNoise serves static files; uploaded media belongs in object storage in production.

## Deploy on Render with Supabase

This repository deploys as a **Render Web Service** using its `Dockerfile`. GitHub is source control only; Render runs the Django application.

1. Create a Supabase project and a **public** Storage bucket, for example `blog-media`. Public is intentional here: this site uses stable public URLs for published images and videos. Do not put private uploads in this bucket. Generate server-only S3 access keys in Supabase Storage settings; never expose them in browser code.
2. In Supabase **Connect**, select **Shared pooler → Session mode** and copy its port-`5432` connection string. Render is commonly IPv4-only, while Supabase's direct endpoint is IPv6-only without its IPv4 add-on. Keep `sslmode=require` in the URL and percent-encode special characters in the password.
3. Create a Render Web Service from this GitHub repository using the Docker runtime. Add these secret environment variables in Render:

   ```text
   DEBUG=False
   SECRET_KEY=<long random secret>
   ALLOWED_HOSTS=<your-render-hostname>,<your-domain>
   SITE_URL=https://<your-domain-or-render-hostname>
   DATABASE_URL=postgresql://postgres.<project-ref>:<password>@<shared-pooler-host>:5432/postgres?sslmode=require
   USE_S3_MEDIA=True
   AWS_ACCESS_KEY_ID=<Supabase S3 access key>
   AWS_SECRET_ACCESS_KEY=<Supabase S3 secret>
   AWS_STORAGE_BUCKET_NAME=blog-media
   AWS_S3_ENDPOINT_URL=https://<project-ref>.storage.supabase.co/storage/v1/s3
   AWS_S3_REGION_NAME=<Supabase project region>
   AWS_S3_ADDRESSING_STYLE=path
   MEDIA_CDN_DOMAIN=<project-ref>.supabase.co/storage/v1/object/public/blog-media
   ```

4. Optionally set `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL`, and `DJANGO_SUPERUSER_PASSWORD` once. On every deploy, startup runs migrations, then creates that user only when the username does not already exist; it never changes an existing password. Omit all three to create admins manually.

Render supplies `PORT`; the container starts Gunicorn on it automatically. It runs migrations but never runs `seed_demo` in production. Keep the existing `docker compose up --build` workflow for local development; it continues to use local PostgreSQL and filesystem media by default.

Supabase Storage S3 credentials bypass Storage RLS, so keep them only in Render's server-side environment. This Django app talks directly to PostgreSQL and does not need its tables exposed through the Supabase Data API.
