from django.db.models import Q, Count, Sum

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from dateutil.parser import parse as dateparse

from collections import defaultdict

from maluroam.eduroam_snort.models import Event

from bintrees import FastBinaryTree as sorteddict


def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=tzutc())
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return int(unix_time(dt) * 1000.0)

def getEvents(
        start=datetime.min.replace(tzinfo=tzutc()),
        finish=datetime.now(tzutc()),
        delta=None, username=None):
    
    assert start < finish
    if not delta:
        delta = finish - start;
    
    """
    Determine the best interval for the graph, and sqldateformat to
    group by.
    """
    
    if delta <= timedelta(days=4):
        interval = relativedelta(hours=1)
        sqldateformat = r'%Y-%m-%dT%H:00:00Z'
    elif delta <= timedelta(weeks=4*3):
        interval = relativedelta(days=1)
        sqldateformat = r'%Y-%m-%dT00:00:00Z'
    elif delta <= timedelta(days = 3*365):
        interval = relativedelta(months=1)
        sqldateformat = r'%Y-%m-01T00:00:00Z'
    else:
        interval = relativedelta(years=1)
        sqldateformat = r'%Y-01-01T00:00:00Z'
    
    """
    here we asssume that blacklist__name and rule__name are disjoint
    """
    events = Event.objects.filter(
        Q(rule__hide=False) | Q(blacklist__hide=False),
        start__gte = start,
        finish__lte = finish,
    ).extra(
        select={
            'timegroup': "DATE_FORMAT(event.start, %s)",
        },
        select_params = (sqldateformat,),
    ).values("timegroup", "blacklist", "blacklist__name", "rule", "rule__name").annotate(alerts=Count('event_id')).order_by("rule", "blacklist__name", "start")
    
    if username:
        events = events.filter(username=username)
    
    return events
    
def getGrouping(*args, **kwargs):
    """
    return groups structured as such:
    
        [
            {
                "label": "abuse_ch_palevo",
                "data": [
                    [1333238400000, 839]
                ],
                "total" : 839,
                "color" : 4
            },
            {
                "label": "abuse_ch_spyeye",
                "data": [
                    [
                        1333238400000,
                        795
                    ],
                    [
                        1335830400000,
                        310
                    ],
                    [
                        1338508800000,
                        34
                    ]
                ],
                "total": 1139,
                "color": 2
            }
        ]
    """
    
    events = getEvents(*args, **kwargs)
    grouping = defaultdict(sorteddict)
    colors = {}
    
    """
    Loop through each event, and group on a key chosen by blacklist__name
    rule__name or rule.
    """
    
    for event in events:
        event["datetime"] = dateparse(event["timegroup"])
        event["timestamp"] = unix_time_millis(event["datetime"])
        
        if event["blacklist__name"]:
            key = event["blacklist__name"]
        elif event["rule__name"]:
            key = "{rule_name}[{rule}]".format(
                rule_name = event["rule__name"],
                rule = event["rule"]
            )
        else:
            key = [ "snort_" + event["rule"] ]
        colors[key] = 0;
        grouping.setdefault(key, sorteddict())[event["timestamp"]] = event["alerts"]
    
    for key, num in zip(colors,range(len(colors))):
        colors[key] = num

    return map(
        lambda group: {
            "label" : group[0],
            "data" : tuple(group[1].items()),
            "color" : colors[group[0]]
        },
        grouping.items()
    )
    
def getOverviews():
    now = datetime.now(tzutc());
    return {
        'l24h' : getGrouping(now+relativedelta(hours= -24)),
        'l3d'  : getGrouping(now+relativedelta(days=   -3)),
        'l7d'  : getGrouping(now+relativedelta(days=   -7)),
        'l28d' : getGrouping(now+relativedelta(days=  -28)),
        'l12m' : getGrouping(now+relativedelta(months=-12)),
    }
