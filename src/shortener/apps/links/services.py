import secrets
import string

import httpx
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import IntegrityError
from django.db.models import F
from django.utils import timezone

from .exceptions import CodeGenerationError, InvalidURLError, LinkExpiredError, LinkNotFoundError
from .models import Link

ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 7
MAX_ATTEMPTS = 5
PREVIEW_TIMEOUT = 5.0


def create_link(original_url: str) -> Link:
    _validate_url(original_url)

    for _ in range(MAX_ATTEMPTS):
        code = _generate_code()
        try:
            return Link.objects.create(original_url=original_url, short_code=code)
        except IntegrityError:
            continue

    raise CodeGenerationError()


def visit_link(code: str) -> str:
    link = Link.objects.filter(short_code=code).first()

    if link is None:
        raise LinkNotFoundError(code)
    if link.is_expired:
        raise LinkExpiredError(code)

    Link.objects.filter(pk=link.pk).update(click_count=F("click_count") + 1)

    return link.original_url


async def preview_link(code: str) -> dict[str, str]:
    link = await Link.objects.filter(short_code=code).afirst()
    if link is None:
        raise LinkNotFoundError(code)
    if link.expires_at <= timezone.now():
        raise LinkExpiredError(code)

    html = await _fetch_html(link.original_url)

    title = _extract_title(html) or link.original_url

    return {"short_code": code, "original_url": link.original_url, "title": title}


def _generate_code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))


def _validate_url(url: str) -> None:
    try:
        URLValidator()(url)
    except ValidationError as exc:
        raise InvalidURLError(url) from exc


async def _fetch_html(url: str) -> str:
    async with httpx.AsyncClient(timeout=PREVIEW_TIMEOUT, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text


def _extract_title(html: str) -> str | None:
    import re

    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None
