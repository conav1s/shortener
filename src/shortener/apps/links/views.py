import json

import httpx
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseGone, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import services
from .exceptions import CodeGenerationError, InvalidURLError, LinkExpiredError, LinkNotFoundError


def redirect_to_original(request: HttpRequest, code: str) -> HttpResponse:
    try:
        target = services.visit_link(code)
    except LinkNotFoundError:
        raise Http404("No such link") from None
    except LinkExpiredError:
        return HttpResponseGone("This link has expired")

    return redirect(target)


@csrf_exempt
@require_POST
def create_link(request: HttpRequest) -> HttpResponse:
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    original_url = payload.get("original_url")
    if not original_url:
        return JsonResponse({"error": "original_url is required"}, status=400)

    try:
        link = services.create_link(original_url)
    except InvalidURLError:
        return JsonResponse({"error": "original_url is not a valid URL"}, status=400)
    except CodeGenerationError:
        return JsonResponse({"error": "Could not generate a unique code"}, status=500)

    short_url = request.build_absolute_uri(reverse("links:redirect", args=[link.short_code]))

    return JsonResponse(
        {"short_code": link.short_code, "short_url": short_url, "original_url": link.original_url},
        status=201,
    )


async def preview_link(request: HttpRequest) -> HttpResponse:
    code = request.GET.get("code", "")
    if not code:
        return JsonResponse({"error": "code is required"}, status=400)

    try:
        data = await services.preview_link(code)
    except LinkNotFoundError:
        return JsonResponse({"error": "No such link"}, status=404)
    except LinkExpiredError:
        return JsonResponse({"error": "This link has expired"}, status=410)
    except httpx.HTTPError:
        return JsonResponse({"error": "Could not fetch the target page"}, status=502)

    return JsonResponse(data)


def index(request: HttpRequest) -> HttpResponse:
    short_url, error = None, None

    if request.method == "POST":
        original_url = request.POST.get("original_url", "")
        try:
            link = services.create_link(original_url)
            short_url = request.build_absolute_uri(f"/{link.short_code}")
        except InvalidURLError:
            error = "It seems an invalid link"

    return render(
        request=request,
        template_name="links/index.html",
        context=
            {
                "short_url": short_url,
                "error": error
            }
    )
