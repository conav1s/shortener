import pytest

from django.test import Client


@pytest.mark.django_db
def test_request_id_header_present(client: Client) -> None:
    response = client.get("/clk001")

    assert "X-Request-ID" in response
    assert "X-Response-Time-ms" in response
