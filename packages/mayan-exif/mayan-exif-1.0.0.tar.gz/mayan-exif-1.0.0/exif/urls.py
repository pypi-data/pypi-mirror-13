from __future__ import unicode_literals

from django.conf.urls import patterns, url

from .views import DocumentVersionEXIFListView

urlpatterns = patterns(
    '',
    url(
        r'^document_version/(?P<pk>\d+)/exif/$',
        DocumentVersionEXIFListView.as_view(),
        name='document_version_exif_list'
    ),
)
