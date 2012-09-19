#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  urls.py
#  
#  Copyright 2012 Thomas Grainger <tagrain@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation; version 3.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#  
#  You should have received a copy of the GNU Affero General Public
#  License along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#

from django.conf.urls import patterns, include, url

from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from maluroam.eduroam_snort.models import Blacklist, Rule, Script
from maluroam.eduroam_snort.views import UsersListView
from maluroam.eduroam_snort.forms import ActivityRangeForm
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('maluroam.eduroam_snort.views',
    # Examples:
    url(r'^$', 
        FormView.as_view(
            template_name = "eduroam_snort/dashboard.html",
            form_class = ActivityRangeForm
        ),
        name='dashboard'
    ),
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
    
    url(r'^blacklist/(?P<pk>\d+)?$', "route", kwargs={"view_kwargs": {"model":Blacklist}}, name="blacklist"),
    url(r'^rule/(?P<pk>\d+)?$', "route", kwargs={"view_kwargs": {"model":Rule}}, name="rule"),
    url(r'^script/(?P<pk>\d+)?$', "route", kwargs={"view_kwargs": {"model":Script}}, name="script"),
)

urlpatterns += patterns('maluroam.eduroam_snort.api',
    url(r'^activity.json$', 'activity', name="activity-api"),
    url(r'^users.json$', 'users', name="users-api"),
)
