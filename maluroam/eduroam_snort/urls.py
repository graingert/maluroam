from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('eduroam_snort.views',
    # Examples:
    url(r'^dashboard/$', 'dashboard', name='dashboard'),
    url(r'^overviews.json$', 'overview', name="overviews"),
)
