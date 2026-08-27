import time
import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

GetResponse = Callable[[HttpRequest], HttpResponse]


class TimingMiddleware:
    def __init__(self, get_response: GetResponse) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = time.perf_counter()
        # before view. request phase
        response = self.get_response(request)
        # after view. response phase
        elapsed_ms = (time.perf_counter() - start) * 1000
        response["X-Response-Time-ms"] = f"{elapsed_ms:.1f}"
        return response


class RequestIDMiddleware:
    def __init__(self, get_response: GetResponse) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request_id = uuid.uuid4().hex
        request.request_id = request_id  # type: ignore[attr-defined]
        response = self.get_response(request)
        response["X-Request-ID"] = request_id
        return response
