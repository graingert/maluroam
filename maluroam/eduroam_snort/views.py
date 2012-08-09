from django.shortcuts import render
from django.db.models import Q, Count, Sum

from maluroam.eduroam_snort.models import Event
from maluroam.eduroam_snort.utils import getOverviews
import json
from django.http import HttpResponse

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc


def dashboard(request):
    events = Event.objects.filter(
        #Q(rule__hide=False) | Q(blacklist__hide=False),
        start__gte = (datetime.now(tzutc()) + relativedelta(days=-7)),
    )
    
    users = events.values("username").annotate(Count('event_id'), Sum("alerts")).order_by("-event_id__count","-alerts__sum")
    
    return render(request, "eduroam_snort/dashboard.html", dict(users=users))

def overview(request):
    return HttpResponse(json.dumps(getOverviews()), content_type="application/json")
    
def user(request):
    return render(request, "eduroam_snort/user.html")
