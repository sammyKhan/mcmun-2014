from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('mcmobile.views',
    url(r'^itinerary', 'schedule', name='schedule_mob'),
    url(r'^committees-list', 'committees', name='committees_mob'),
    url(r'^social', 'social_media', name='socialmedia_mob'),
    url(r'^sponsors', 'sponsors', name='sponsors_mob'),
    url(r'^food', 'food', name='food_mob'),
    url(r'^contact', 'contact', name='contact_mob'),
    url(r'^map', 'map', name='map_mob'),
)
