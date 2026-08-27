import pytest
from pytest_mock import MockerFixture

from ..services import create_link, preview_link
from ..models import Link
from ..exceptions import InvalidURLError, LinkNotFoundError


@pytest.mark.django_db
def test_create_link_persists_and_generates_code() -> None:
    link = create_link("https://example.com")

    assert link.pk is not None
    assert len(link.short_code) == 7
    assert Link.objects.count() == 1


@pytest.mark.django_db
def test_create_link_rejects_invalid_url() -> None:
    with pytest.raises(InvalidURLError):
        create_link("not-a-url")

    assert Link.objects.count() == 0


@pytest.mark.django_db(transaction=True)
async def test_preview_link_extract_title(mocker: MockerFixture) -> None:
    await Link.objects.acreate(original_url="https://example.com", short_code="prev01")

    mocker.patch(
        "shortener.apps.links.services._fetch_html",
        return_value="<html><head><title> Example Domain </title></head></html>",
    )

    result = await preview_link("prev01")

    assert result["title"] == "Example Domain"
    assert result["short_code"] == "prev01"


@pytest.mark.django_db(transaction=True)
async def test_preview_link_missing_returns_not_found() -> None:
    with pytest.raises(LinkNotFoundError):
        await preview_link("nope999")


@pytest.mark.django_db(transaction=True)
async def test_preview_link_propagates_http_error(mocker: MockerFixture) -> None:
    import httpx

    await Link.objects.acreate(original_url="https://example.com", short_code="prev02")
    mocker.patch(
        "shortener.apps.links.services._fetch_html", side_effect=httpx.ConnectError("boom")
    )

    with pytest.raises(httpx.HTTPError):
        await preview_link("prev02")
