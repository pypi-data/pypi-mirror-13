from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r'^croco_document/(?P<uuid>[-\w]+)$',
        views.CrocoDocumentView.as_view(redirect=True),
        name='croco_document_url',
    ),
    url(
        r'^croco_document_content/(?P<uuid>[-\w]+)$',
        views.CrocoDocumentView.as_view(),
        name='croco_document_content_url',
    ),
    url(
        r'^croco_document_download/(?P<uuid>[-\w]+)$',
        views.CrocoDocumentDownload.as_view(),
        name='croco_document_download',
    ),
    url(
        r'^croco_thumbnail_download/(?P<uuid>[-\w]+)$',
        views.CrocoThumbnailDownload.as_view(),
        name='croco_thumbnail_download',
    ),
    url(
        r'^croco_text_download/(?P<uuid>[-\w]+)$',
        views.CrocoTextDownload.as_view(),
        name='croco_text_download',
    ),
]
