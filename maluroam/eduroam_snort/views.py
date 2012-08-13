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

def settings(request):
    return render(
        request = request,
        template_name = "eduroam_snort/settings.html",
        dictionary = {
            "rules" : Rule.objects.all(),
            "blacklists" : Blacklist.objects.all()
        }
    )

class CRUDMixin(object):

    def get_success_url(self):
        """
        Whenever an object is created or updated successfully this will
        return the user to the settings page with the object they just
        messed with highlighted
        """
        
        if self.object:
            return reverse('settings') + '#{model}-{pk}'.format(
                model = slugify(self.model._meta.verbose_name),
                pk = self.object.pk
            )
        else:
            return reverse('settings')


class BlacklistCRUDMixin(CRUDMixin):
    model = Blacklist
class BlacklistCreateView(BlacklistCRUDMixin, CreateView):
    pass
class BlacklistDeleteView(BlacklistCRUDMixin, DeleteView):
    pass
class BlacklistUpdateView(BlacklistCRUDMixin, UpdateView):
    pass
    
class RuleCRUDMixin(CRUDMixin):
    model = Rule
class RuleCreateView(RuleCRUDMixin, CreateView):
    pass
class RuleDeleteView(RuleCRUDMixin, DeleteView):
    pass
class RuleUpdateView(RuleCRUDMixin, UpdateView):
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
