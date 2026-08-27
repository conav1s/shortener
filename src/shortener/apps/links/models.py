from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone


def default_expiry() -> datetime:
    return timezone.now() + timedelta(days=30)


class Link(models.Model):
    original_url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=10, unique=True)
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)

    def __str__(self) -> str:
        return f"{self.short_code} -> {self.original_url}"

    @property
    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at
