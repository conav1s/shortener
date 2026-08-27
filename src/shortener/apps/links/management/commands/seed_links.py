from typing import Any

from django.core.management.base import BaseCommand

from shortener.apps.links.models import Link


class Command(BaseCommand):
    help = "Init DB"

    def handle(self, *args: Any, **options: Any) -> None:
        Link.objects.all().delete()

        samples = [
            ("https://docs.astral.sh/ruff/", "ruff01"),
            ("https://www.djangoproject.com/", "djng01"),
        ]
        for url, code in samples:
            Link.objects.create(original_url=url, short_code=code)

        self.stdout.write(self.style.SUCCESS(f"Created several links: {Link.objects.count()}"))
