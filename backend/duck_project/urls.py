"""URL routing for duck_project."""

from django.urls import include, path

urlpatterns = [
    path("api/", include("backend.duck_api.urls")),
]
