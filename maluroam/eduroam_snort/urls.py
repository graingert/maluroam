from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('eduroam_snort.views',
    # Examples:
    url(r'^$', 'dashboard', name='dashboard'),
    url(r'^overviews.json$', 'overview', name="overviews"),
    
    url(
        r'^user/(?P<slug>[\w-]+)$',
        TemplateView.as_view(template_name="eduroam_snort/user.html"),
        name="user"
    ),
    url(
        r'^user/$',
        TemplateView.as_view(template_name="eduroam_snort/users.html"),
        name="users"
    ),
    url(
        r'^settings/$',
        TemplateView.as_view(template_name="eduroam_snort/settings.html"),
        name="settings"
    ),
)
