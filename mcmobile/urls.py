from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('mcmobile.views',
    url(r'^itinerary', 'schedule', name='schedule_mob'),
    url(r'^committees-list', 'committees', name='committees_mob'),
    url(r'^socialmedia', 'social_media', name='socialmedia_mob'),
)
