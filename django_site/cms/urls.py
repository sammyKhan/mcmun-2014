from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
	url(r'(?P<name>[a-zA-Z0-9-]+)/?', 'cms.views.main'),
)
