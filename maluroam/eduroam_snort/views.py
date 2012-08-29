from django.shortcuts import render
from django.db.models import Q, Count, Sum, Min, Max
from django.core.urlresolvers import reverse

from maluroam.eduroam_snort.models import Event, Blacklist, Rule, Script
from maluroam.eduroam_snort.aggregates import Concatenate, parse_concat
from maluroam.eduroam_snort.utils import getGrouping
from maluroam.eduroam_snort.forms import FilterForm, ActivityRangeForm

import json
from django.http import HttpResponse, Http404

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dateutil.tz import tzutc

from django.template.defaultfilters import slugify
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView


def dashboard(request):
    users = Event.objects.filter(
        #Q(rule__hide=False) | Q(blacklist__hide=False),
        #start__gte = (datetime.now(tzutc()) + relativedelta(days=-7)),
    ).values("username").annotate(Count('id'), Sum("alerts")).order_by("-id__count","-alerts__sum")
    return render(request, "eduroam_snort/dashboard.html", dict(users=users, activityRangeForm=ActivityRangeForm()))
    
def user(request, slug):
    
    if not Event.objects.filter(username = slug).exists():
        raise Http404()
    
    events = False
        
    
    """
    public function displayUser(){
        // Is there a user in the $_GET?
        if(!isset($_GET['user']) || empty($_GET['user'])){
            // display error
            return;			
        } else {
            // Clean the input, and determine if they exist
            $user = mysql_real_escape_string($_GET['user']);
            $usercheck = mysql_query(sprintf("SELECT username FROM event WHERE username = '%s' LIMIT 1;", $user));
            
            if(mysql_num_rows($usercheck) != 1){
                // display error
                return;
            }
        }
    
        // Send data to Smarty
        $this->assign('user', array(
            'user' => $user,
            'statistics' => $this->fetchUserStatistics($user),
            'events' => $this->fetchUserEvents($user),
            'l28d' => $this->tools->getCache('getUsersLast28Days', 60, array($user), $this)
        ));
        
        return;
    }
    """
    
    return render(
        request=request,
        template_name = "eduroam_snort/user.html",
        dictionary = {
            "name" : slug,
            "events" : events,
        }
    )

class UsersListView(ListView):
    model = Event
    template_name = "eduroam_snort/users.html"
    context_object_name = "users"
    paginate_by = 20
    
    def get_queryset(self):
        filters = Q()
        self.filter_form = FilterForm(self.request.GET)
        
        if self.filter_form.is_valid():
            rules = self.filter_form.cleaned_data['rule']
            blacklists = self.filter_form.cleaned_data['blacklist']
            earliest = self.filter_form.cleaned_data['earliest']
            latest = self.filter_form.cleaned_data['latest']
            
            if rules:
                filters = filters & Q(rule__in = rules)
            if blacklists:
                filters = filters & Q(rule__in = blacklists)
            if earliest:
                filters = filters & Q(start__gte = earliest)
            if latest:
                filters = filters & Q(finish__lte = latest)
            
        return self.model.objects.filter(filters).values("username").annotate(
                Concatenate("blacklist__name"),
                Concatenate("rule__name"),
                Count('id'),
                packets = Sum('alerts'),
                earliest = Min("start"),
                latest = Max("finish")
            ).order_by("-id__count")
        
    def get_context_data(self, **kwargs):
        context = super(UsersListView, self).get_context_data(**kwargs)

        for obj in context["object_list"]:
            obj["blacklists"] = parse_concat(obj["blacklist__name__concatenate"])
            obj["rules"] = parse_concat(obj["rule__name__concatenate"])
        
        context["filter_form"] = self.filter_form
        query = self.request.GET.copy()
        query.pop("page", None)
        
        for key, value in query.items():
            if not value:
                del(query[key])
                
            if key not in set(("rule", "blacklist", "earliest", "latest")):
                del(query[key])
        
        context["querystring"] = '?'
        if query:
            context["querystring"] += (query.urlencode() + '&')
        return context
    
def settings(request):
    return render(
        request = request,
        template_name = "eduroam_snort/settings.html",
        dictionary = {
            "rules" : Rule.objects.all(),
            "blacklists" : Blacklist.objects.all(),
            "scripts" : Script.objects.all()
        }
    )

class CRUDMixin(object):
    template_name = "eduroam_snort/generic_form.html"
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

class CreateView(CRUDMixin, CreateView):
    pass
class DeleteView(CRUDMixin, DeleteView):
    pass
class UpdateView(CRUDMixin, UpdateView):
    pass

def route(request, name, pk=None):
    """
    Route to the correct view based on Method or the existance of
    pk.
    """
    model = {
        "Script" : Script,
        "Rule" : Rule,
        "Blacklist" : Blacklist
    }[name]
    
    if request.method == 'DELETE':
        return DeleteView.as_view(model=model)(request=request, pk=pk)
    else:
        if pk:
            return UpdateView.as_view(model=model)(request=request, pk=pk)
        else:
            return CreateView.as_view(model=model)(request=request)
