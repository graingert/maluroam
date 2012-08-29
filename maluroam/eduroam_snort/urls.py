from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from maluroam.eduroam_snort.views import UsersListView
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('maluroam.eduroam_snort.views',
    # Examples:
    url(r'^$', 'dashboard', name='dashboard'),
    url(
        r'^user/$',
        UsersListView.as_view(),
        name="users"
    ),
    url(
        r'^user/(?P<slug>[\w-]+)$',
        TemplateView.as_view(template_name="eduroam_snort/user.html"),
        name="user"
    ),

    url(r'^settings/$', 'settings', name="settings"),
    
    url(r'^blacklist/(?P<pk>\d+)?$', "route", kwargs={"name": "Blacklist"}, name="blacklist"),
    url(r'^rule/(?P<pk>\d+)?$', "route", kwargs={"name": "Rule"}, name="rule"),
    url(r'^script/(?P<pk>\d+)?$', "route", kwargs={"name": "Blacklist"}, name="script"),
)

urlpatterns += patterns('maluroam.eduroam_snort.api',
    url(r'^activity.json$', 'activity', name="activity-api"),
    url(r'^users.json$', 'users', name="users-api"),
)
