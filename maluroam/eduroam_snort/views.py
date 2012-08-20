from django.shortcuts import render
from django.db.models import Q, Count, Sum, Min, Max

from maluroam.eduroam_snort.models import Event, Blacklist, Rule
from maluroam.eduroam_snort.aggregates import Concatenate, parse_concat
from maluroam.eduroam_snort.utils import getOverviews
from maluroam.eduroam_snort.forms import FilterForm

import json
from django.http import HttpResponse, Http404

from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
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
        filter_form = FilterForm(self.request.GET)
        if filter_form.is_valid():
            if filter_form["rule"].value():
                filters = filters & Q(rule__in = filter_form["rule"].value())
            if filter_form["blacklist"].value():
                filters = filters & Q(rule__in = filter_form["blacklist"].value())
            earliest = filter_form["earliest"].value()
            latest = filter_form["latest"].value()
            
            if earliest:
                filters = filters & Q(start__gte = earliest)
            if latest:
                filters = filters & Q(finish__lte = latest)
            
        return self.model.objects.filter(filters).values("username").annotate(
                Concatenate("blacklist__name"),
                Concatenate("rule__name"),
                Count('event_id'),
                packets = Sum('alerts'),
                earliest = Min("start"),
                latest = Max("finish")
            ).order_by("-event_id__count")
        
        """
        SELECT username, GROUP_CONCAT(DISTINCT(rule) SEPARATOR ',') as rules, GROUP_CONCAT(DISTINCT(bl.name) SEPARATOR ',') as blacklists, COUNT(e.event_id) as alerts, SUM(e.alerts) as packets, MIN(DATE_FORMAT(e.start,'%%Y-%%m-%%d')) as earliest, MAX(DATE_FORMAT(e.finish,'%%Y-%%m-%%d')) as latest
            FROM event e
            LEFT JOIN blacklists bl
                ON bl.bl_id = e.blacklist
            LEFT JOIN rules r
                ON r.rule_id = e.rule
            WHERE
                %s
                AND (r.hide = 0
                OR bl.hide = 0)
            GROUP BY username
        """
        
    def get_context_data(self, **kwargs):
        context = super(UsersListView, self).get_context_data(**kwargs)

        for obj in context["object_list"]:
            obj["blacklists"] = parse_concat(obj["blacklist__name__concatenate"])
            obj["rules"] = parse_concat(obj["rule__name__concatenate"])
        
        context["filter_form"] = FilterForm(self.request.GET)
        return context
    

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
