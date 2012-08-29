from django.shortcuts import render
from django.db.models import Q, Count, Sum, Min, Max
from django.core.urlresolvers import reverse

from maluroam.eduroam_snort.models import Event, Blacklist, Rule, Script
from maluroam.eduroam_snort.aggregates import Concatenate, parse_concat
from maluroam.eduroam_snort.utils import getGrouping
from maluroam.eduroam_snort.forms import FilterForm, RangeForm, ActivityRangeForm

import json
from django.http import HttpResponse, Http404

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dateutil.tz import tzutc

def activity(request):
    arForm = ActivityRangeForm(request.GET)
    if arForm.is_valid():
        return HttpResponse(json.dumps(getGrouping(**arForm.cleaned_data)), content_type="application/json")
    else:
        response = {
            "success":False,
            "general_message":"Invalid request",
            "errors":dict(arForm.errors.items())
        }
        return HttpResponse(json.dumps(response), status=400, content_type="application/json")

def users(request):
    rangeForm = RangeForm(request.GET)
    
    filters = Q()
    
    if rangeForm.is_valid():
        earliest = rangeForm.cleaned_data.get('earliest', None)
        latest = rangeForm.cleaned_data.get('latest', None)
        
        if earliest:
            filters = filters & Q(start__gte = earliest)
        if latest:
            filters = filters & Q(finish__lte = latest)
    
        users = Event.objects.filter(
            filters,
            #Q(rule__hide=False) | Q(blacklist__hide=False),
            #start__gte = (datetime.now(tzutc()) + relativedelta(days=-7)),
        ).values("username").annotate(Count('id'), Sum("alerts")).order_by("-id__count","-alerts__sum")
        
        for user in users:
            user["uri"] = reverse(
                "user",
                "eduroam_snort.urls",
                (),
                {"slug":user["username"]}
            )
        
        return HttpResponse(json.dumps(tuple(users)), content_type="application/json")
    else:
        response = {
            "success":False,
            "general_message":"Invalid request",
            "errors":dict(rangeForm.errors.items())
        }
        return HttpResponse(json.dumps(response), status=400, content_type="application/json")
