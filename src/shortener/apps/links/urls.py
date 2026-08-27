from django.urls import path

from . import views


app_name = "links"

urlpatterns = [
    path("api/links", views.create_link, name="create"),
    path("preview", views.preview_link, name="preview"),
    path("<str:code>", views.redirect_to_original, name="redirect"),
]
