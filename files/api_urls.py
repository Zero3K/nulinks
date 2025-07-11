from django.conf.urls import url
from . import api_views

urlpatterns = [
    url(r'^auth/login/$', api_views.api_login, name='api_login'),
    url(r'^links/$', api_views.TorrentFileListCreateView.as_view(), name='api_links'),
    url(r'^links/bulk/$', api_views.bulk_create_links, name='api_bulk_links'),
    url(r'^categories/$', api_views.CategoryListView.as_view(), name='api_categories'),
    url(r'^info/$', api_views.api_info, name='api_info'),
]