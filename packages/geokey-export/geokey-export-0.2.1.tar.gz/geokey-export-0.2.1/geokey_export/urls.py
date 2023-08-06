from django.conf.urls import include, url

from rest_framework.urlpatterns import format_suffix_patterns

from views import (
    IndexPage,
    ExportOverview,
    ExportCreate,
    ExportDelete,
    ExportToRenderer,
    ExportGetCategories,
    ExportGetContributions
)

datapatterns = [
    url(
        r'^admin/export/(?P<urlhash>[\w-]+)$',
        ExportToRenderer.as_view(),
        name='export_to_renderer')
]
datapatterns = format_suffix_patterns(datapatterns, allowed=['json', 'kml'])


urlpatterns = [
    url(
        r'^admin/export/$',
        IndexPage.as_view(),
        name='index'),
    url(
        r'^admin/export/(?P<export_id>[0-9]+)/$',
        ExportOverview.as_view(),
        name='export_overview'),
    url(
        r'^admin/export/(?P<export_id>[0-9]+)/delete/$',
        ExportDelete.as_view(),
        name='export_delete'),
    url(
        r'^admin/export/create/$',
        ExportCreate.as_view(),
        name='export_create'),
    url(
        r'^admin/export/projects/(?P<project_id>[0-9]+)/categories/$',
        ExportGetCategories.as_view(),
        name='export_get_categories'),
    url(
        r'^admin/export/projects/(?P<project_id>[0-9]+)/categories/(?P<category_id>[0-9]+)/$',
        ExportGetContributions.as_view(),
        name='export_get_contributions'),
    url(
        r'^', include(datapatterns))
]
