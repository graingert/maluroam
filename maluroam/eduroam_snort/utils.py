#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  utils.py
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

from django.db.models import Q, Count, Sum

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from dateutil.tz import tzutc
from dateutil.parser import parse as dateparse

from collections import defaultdict

from maluroam.eduroam_snort.models import Event

from bintrees import FastBinaryTree as sorteddict
from itertools import starmap

from maluroam.eduroam_snort.models import Blacklist, Rule


def unix_time(dt):
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=tzutc())
    delta = dt - epoch
    return delta.total_seconds()

def unix_time_millis(dt):
    return int(unix_time(dt) * 1000.0)

def getEvents(
        earliest=datetime.min.replace(tzinfo=tzutc()),
        latest=datetime.now(tzutc()),
        delta=None, username=None):
    assert earliest < latest
    if not delta:
        delta = latest - earliest;
    
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
        start__gte = earliest,
        finish__lte = latest,
    ).extra(
        select={
            'timegroup': "DATE_FORMAT(event.start, %s)",
        },
        select_params = (sqldateformat,),
    ).values(
        "timegroup", "blacklist", "blacklist__name", "rule", "rule__name"
    ).annotate(
        alerts=Count('id')
    ).order_by("rule", "blacklist__name", "start")
    
    if username:
        events = events.filter(username=username)
    
    return (events, interval)
    
def getGrouping(*args, **kwargs):
    """
    return groups structured as such:
    
        [
            {
                "label": "abuse_ch_palevo",
                "data": [
                    [1333238400000, 839]
                ],
                "source" : {
                    "class" : "blacklist",
                    "pk" : 2
                }
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
                ]
            }
        ]
    """
    
    events, interval = getEvents(*args, **kwargs)
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
            key = Blacklist(pk=event["blacklist"], name=event["blacklist__name"])
        elif event["rule__name"]:
            key = Rule(pk=event["rule"], name=event["rule__name"])
        else:
            key = Rule(pk=event["rule"], name="snort")
            
        grouping[key][event["timestamp"]] = {
            "alerts" : event["alerts"],
            "width" : unix_time_millis(event["datetime"] + interval) - event["timestamp"]
        }
        
    return tuple(starmap(
        lambda model, data: {
            "label" : str(model),
            "uri" : model.get_absolute_url(),
            "data" : [(time, plot["alerts"], plot["width"]) for time, plot in data.items()],
        },
        grouping.items()
    ))
    
def fetchUserStatistics(username):
    
    events = Event.objects.filter(
        Q(rule__hide=False) | Q(blacklist__hide=False),
        username = username,
    ).exclude(
        ip_src__startswith = "152.78."
    )
    
    events_src = events.values(
        "username", "ip_src", "blacklist__name", "rule__name"
    ).annotate(
        Count('pk'),
        packets = Sum("alerts"),
        earliest = Min("start"),
        latest = Min("latest")
    )
    
    events_dst = events.values(
        "username", "ip_dst"
    ).annotate(
        Count('pk'),
        packets = Sum("alerts"),
        earliest = Min("start"),
        latest = Min("latest")
    )
    """
    public function fetchUserStatistics($user){
        // Fetch BAD IP stats
        $ip_sql = sprintf("
            SELECT ip, SUM(alerts) as alerts, SUM(packets) as packets, blacklist, rule, rule_name, MIN(earliest) as earliest, MAX(latest) as latest
            FROM (
                SELECT e.event_id, ip_src as ip, COUNT(e.event_id) as alerts, SUM(e.alerts) as packets, bl.name as blacklist, rule, rule_name, MIN(e.start) AS earliest, MAX(e.finish) as latest
                FROM event e
                LEFT JOIN blacklists bl
                    ON bl.bl_id = e.blacklist
                LEFT JOIN rules r
                    ON r.rule_id = e.rule
                WHERE
                    ip_src NOT LIKE '152.78.%%'
                    AND username = '%s'
                    AND (r.hide = 0 OR bl.hide = 0)
                GROUP BY username, ip_src
                
                UNION
                
                SELECT e.event_id, ip_dst as ip, COUNT(e.event_id) as alerts, SUM(e.alerts) as packets, bl.name as blacklist, rule, rule_name, MIN(e.start) AS earliest, MAX(e.finish) as latest
                FROM event e
                LEFT JOIN blacklists bl
                    ON bl.bl_id = e.blacklist
                LEFT JOIN rules r
                    ON r.rule_id = e.rule
                WHERE
                    ip_dst NOT LIKE '152.78.%%'
                    AND username = '%s'
                    AND (r.hide = 0 OR bl.hide = 0)
                GROUP BY username, ip_dst
            ) as tmp
            GROUP BY ip
            ORDER BY alerts DESC
        ", $user, $user);
        
        $ip_rst = mysql_query($ip_sql);
        
        if($ip_rst){
            // Loop through all IP addresses and create an array of them
            while($ip = mysql_fetch_assoc($ip_rst)){
                $ips[] = $ip;
            }
        } else {
            // Something broke
            echo mysql_error();exit;
        }
        unset($ip_rst);
        
        // Fetch Alert Occurance Stats
        $ao_sql = sprintf("
            SELECT username, rule, rule_name, bl.name as blacklist, COUNT(e.event_id) as alerts, SUM(e.alerts) as packets, MIN(e.start) as earliest, MAX(e.finish) as latest
            FROM event e
            LEFT JOIN blacklists bl
                ON bl.bl_id = e.blacklist
            LEFT JOIN rules r
                ON r.rule_id = e.rule
            WHERE
                username = '%s'
                AND (r.hide = 0 OR bl.hide = 0)
            GROUP BY
                e.rule,
                e.blacklist
            ORDER BY
                alerts DESC
        ", $user);
        
        // Fetch alert occurances
        $ao_rst = mysql_query($ao_sql);
        if($ao_rst){
            while($ao = mysql_fetch_assoc($ao_rst)){
                // Add alert occurance to an array, keep a tally of total events
                $aos[] = $ao;
                $totals += $ao['alerts'];
            }
        } else {
            // Something broke
            echo mysql_error();exit;
        }
        unset($ao_rst);
        
        // Return an array of useful information
        return array(
            'ip_occ' => $ips,
            'alert_occ' => $aos,
            'total_alerts' => $totals
        );
    }
    """
