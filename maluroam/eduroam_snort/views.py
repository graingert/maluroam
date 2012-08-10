from django.shortcuts import render
from django.db.models import Q, Count, Sum

from maluroam.eduroam_snort.models import Event, Blacklist, Rule
from maluroam.eduroam_snort.utils import getOverviews
import json
from django.http import HttpResponse

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc

from django.template.defaultfilters import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView


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


class CRUDMixin(object):
    """
    Mixin that holds common methods and properties for all the CRUD
    operations on the Feed model
    """
    def get_success_url(self):
        """
        Whenever a feed is created or updated successfully this will
        return the user to the publishnews page with the feed they just
        messed with highlighted
        """
        
        if self.object:
            return reverse('settings') + '#{model}-{pk}'.format(
                model = slugify(self.model.verbose_name),
                pk = blacklist.pk
            )
        else:
            return reverse('settings')


class BlacklistCRUDMixin(CRUDMixin):
    model = Blacklist
class BlacklistDetailView(BlacklistCRUDMixin, DetailView):
    pass
class BlacklistCreateView(BlacklistCRUDMixin, CreateView):
    pass
class BlacklistDeleteView(BlacklistCRUDMixin, DeleteView):
    pass
class BlacklistUpdateView(BlacklistCRUDMixin, UpdateView):
    pass
    
class RuleCRUDMixin(CRUDMixin):
    model = Rule
class RuleDetailView(BlacklistCRUDMixin, DetailView):
    pass
class RuleCreateView(BlacklistCRUDMixin, CreateView):
    pass
class RuleDeleteView(BlacklistCRUDMixin, DeleteView):
    pass
class RuleUpdateView(BlacklistCRUDMixin, UpdateView):
    pass

def route(request, name, pk=None):
    """
    Route to the correct view based on Method or the existance of
    pk.
    """
    if request.method == 'DELETE':
        return globals()[name + "DeleteView"].as_view()(request=request, pk=pk)
    else:
        if pk:
            return globals()[name + "UpdateView"].as_view()(request=request, pk=pk)
        else:
            return globals()[name + "CreateView"].as_view()(request=request)
