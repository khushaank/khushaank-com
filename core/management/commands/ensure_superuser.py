import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the configured superuser once, without changing an existing account."

    def handle(self, *args, **options):
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        if not all((username, email, password)):
            self.stdout.write("Superuser environment variables are absent; skipped.")
            return

        user_model = get_user_model()
        if user_model.objects.filter(username=username).exists():
            self.stdout.write("Configured superuser already exists; skipped.")
            return

        user_model.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS("Configured superuser created."))
