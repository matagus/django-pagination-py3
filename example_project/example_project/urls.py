"""
URL configuration for example_project project.
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("music_app.urls", namespace="music_app")),
    path("admin/", admin.site.urls),
]
