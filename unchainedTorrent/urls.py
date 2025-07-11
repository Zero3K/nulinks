"""unchainedTorrent URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin

# for signup
from tuser import views as userViews
from files import views as viewsFiles

# for media
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^$', viewsFiles.index, name='home'),

    # url(r'/^$', viewsFiles.index, name='urlHome'),

    url(r'^profile/$', userViews.profile, name='profile'),
    url(r'^search/$', viewsFiles.search, name='search'),
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', userViews.myLogin, name='urlLogin'),
    url(r'^logout/$',userViews.myLogout,  name='urlLogout'),

    url(r'^register/$', userViews.signup, name='register'),
    # url(r'^upload/$', viewsFiles.model_form_upload, name='upload'),
    url(r'^upload/$', viewsFiles.get_name, name='upload'),
    url(r'^edit/(?P<file_id>[0-9]+)/$', viewsFiles.edit_torrent_file, name='edit_torrent_file'),

    # url(r'^search(?P<q>[0-9a-zA-Z+-_]+)', viewsFiles.search, name='search'),

    # url(r'^media(?P<q>[0-9a-zA-Z+-_]+)', viewsFiles.search, name='media'),
    # url(r'^search(?P<q>[a-zA-Z+-_]+)', viewsFiles.search, name='search'),
    # url(r'torrents/(P<torrentPath>)/', viewsFiles.torrentDownload, name = "torrentDownload"),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
