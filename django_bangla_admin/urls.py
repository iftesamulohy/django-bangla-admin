"""Standalone URLConf (optional).

Most projects mount the themed admin via ``sites.urls``. This module exposes
the non-admin auxiliary endpoints under the ``bangla_admin`` namespace for
projects that want to include them separately::

    path("ba/", include("django_bangla_admin.urls")),
"""

from django.urls import path

from . import i18n, views

app_name = "bangla_admin"

urlpatterns = [
    path("set-language/", i18n.set_language, name="ba_set_language"),
    path("chart-data/", views.chart_data, name="ba_chart_data"),
]
