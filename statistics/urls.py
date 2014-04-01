from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'frontpage.views.frontpage', name='frontpage'),
    url(r'^api/listeners', 'livestream.views.stream_listeners', name='stream_listeners'),
    url(r'^admin/', include(admin.site.urls)),
)
