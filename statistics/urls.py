from django.conf.urls import patterns, include, url
from django.views.generic.base import RedirectView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='stream/', permanent=True), name='frontpage'),
    url(r'^stream/(?P<show>[^/]+)', 'livestream.views.show', name='stream_show_detail'),
    url(r'^stream/', 'livestream.views.overview', name='stream_overview'),
    url(r'^podcast/', 'podcast.views.podcast', name='podcast_overview'),
    url(r'^api/listeners', 'livestream.views.stream_listeners', name='stream_listeners'),
    url(r'^admin/', include(admin.site.urls)),
)
