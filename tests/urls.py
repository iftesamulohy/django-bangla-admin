from django.urls import path

from django_bangla_admin.sites import urls as ba_urls

urlpatterns = [path("admin/", ba_urls)]
