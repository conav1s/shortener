import json

import pytest
from django.test import Client
from django.urls import reverse
from pytest_mock import MockerFixture

from .. import services
from ..models import Link


@pytest.mark.django_db
def test_create_link_returns_201(client: Client) -> None:
    response = client.post(
        path="/api/links",
        data=json.dumps({"original_url": "https://example.com"}),
        content_type="application/json",
    )

    assert response.status_code == 201
    body = response.json()
    assert body["original_url"] == "https://example.com"
    assert len(body["short_code"]) == 7
    assert Link.objects.count() == 1


@pytest.mark.django_db
def test_create_link_rejects_invalid_url(client: Client) -> None:
    response = client.post(
        path="/api/links",
        data=json.dumps({"original_url": "not-a-url"}),
        content_type="application/json",
    )

    assert response.status_code == 400
    assert Link.objects.count() == 0


@pytest.mark.django_db
def test_redirect_increments_click_count(client: Client) -> None:
    Link.objects.create(original_url="https://example.com", short_code="clk001")

    response = client.get("/clk001")

    assert response.status_code == 302
    assert response["Location"] == "https://example.com"
    link = Link.objects.get(short_code="clk001")
    assert link.click_count == 1


@pytest.mark.django_db
def test_create_view_calls_service(client: Client, mocker: MockerFixture) -> None:
    spy = mocker.spy(services, "create_link")

    client.post(
        # path="/api/links",
        path=reverse("links:create"),
        data='{"original_url": "https://example.com"}',
        content_type="application/json",
    )

    spy.assert_called_once_with("https://example.com")
