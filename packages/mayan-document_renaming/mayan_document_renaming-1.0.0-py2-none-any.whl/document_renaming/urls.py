from __future__ import unicode_literals

from django.conf.urls import patterns, url

from .views import (
    SequenceListView, SequenceCreateView, SequenceDeleteView, SequenceEditView,
    DocumentTypeRenamingTemplateEditView
)

urlpatterns = patterns(
    '',
    url(
        r'^sequence/list/$', SequenceListView.as_view(),
        name='sequence_list'
    ),
    url(
        r'^sequence/create/$', SequenceCreateView.as_view(),
        name='sequence_create'
    ),
    url(
        r'^sequence/(?P<pk>\d+)/edit/$', SequenceEditView.as_view(),
        name='sequence_edit'
    ),
    url(
        r'^sequence/(?P<pk>\d+)/delete/$', SequenceDeleteView.as_view(),
        name='sequence_delete'
    ),
    url(
        r'^document_type/(?P<pk>\d+)/renaming_template/edit/$',
        DocumentTypeRenamingTemplateEditView.as_view(),
        name='renaming_template_edit'
    ),
)
