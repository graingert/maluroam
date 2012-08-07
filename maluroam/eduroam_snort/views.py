from django.shortcuts import render
from eduroam_snort.models import Event
from django.db.models import Q, Count, Sum
from datetime import datetime, timedelta
from collections import defaultdict

def dashboard(request):
    events = Event.objects.filter(
        Q(rule__hide=False) | Q(blacklist__hide=False),
        start__gte = (datetime.now() - timedelta(days=-30)),
    )
    
    users = events.values("username").annotate(Count('event_id'), Sum("alerts"))
    
    #$rst = mysql_query(sprintf("
        #SELECT username, COUNT(e.event_id) as alerts, SUM(e.alerts) as packets
        #FROM event e
        #LEFT JOIN blacklists bl
            #ON bl.bl_id = e.blacklist
        #LEFT JOIN rules r
            #ON r.rule_id = e.rule
        #WHERE
            #e.start >= '%s'
            #AND (
                #r.hide = 0 OR bl.hide = 0
            #)
        #GROUP BY username
        #ORDER BY alerts DESC
        #LIMIT 10
    #", date('Y-m-d', strtotime(date('Y-m-d', gmmktime()) . ' -7days')) ));
    #$users = array();
    
    return render(request, "eduroam_snort/dashboard.html", dict(users=users))
    
#<?php

#/**
 #* Page : DashboardPage extends Page class
 #* ------------------------------------------------------------
 #* This page is designed to provide an overview of current 
 #* event levels over specified periods of time.
 #*/
#class DashboardPage extends Page {

	#// Constructor
	#public function __construct($smarty, $tools){
		#parent::__construct($smarty, $tools);
	#}

	#// Overide executePage function
	#public function executePage() {
		#// Fetch overview data, cache for 10 minutes
		#$overviews = $this->tools->getCache('getOverviews', 10, array(), $this);
		
		#// Establish colours for all alerts so that they are
		#// consistent for all graphs in the View
		#$colours = array();
		#foreach($overviews as $range){
			#foreach($range as $group){
				#if(!in_array($group['name'], $colours)){
					#$colours[] = $group['name'];
				#}
			#}
		#}
		#$colours = array_flip($colours);
		
		#// Assign results to Smarty (View)
		#$this->assign('overviews', $overviews);
		#$this->assign('alert_colours', $colours);
		#$this->assign('users', $this->fetchTopUsers());
	#}
	
	#/**
	 #* function : getOverviews
	 #* ----------------------------------------------------------------------
	 #* Cacheable function that returns 5 different time span overviews of
	 #* malicious network activity
	 #*/
	#public function getOverviews(){
		#$now = date('Y-m-d H:00:00', gmmktime());
	
		#return array(
			#'l24h'	=> $this->tools->getOverview(date('Y-m-d H:00:00', strtotime($now.' -24 hours')), $now),
			#'l3d'	=> $this->tools->getOverview(date('Y-m-d H:00:00', strtotime($now.' -3 days')),$now),
			#'l7d'	=> $this->tools->getOverview(date('Y-m-d', strtotime($now .' -7 days')), $now),
			#'l28d'	=> $this->tools->getOverview(date('Y-m-d', strtotime($now .' -28 days')), $now),
			#'l12m'	=> $this->tools->getOverview(date('Y-m', strtotime($now .' -12 months')), $now)
		#);
	#}
	
	#/**
	 #* function : fetchTopUsers
	 #* ----------------------------------------------------------------------
	 #* This will return the top 10 users triggering alerts/blacklists in the
	 #* past 7 days.
	 #*/
	#public function fetchTopUsers(){
		#// Execute Query
		#$rst = mysql_query(sprintf("
			#SELECT username, COUNT(e.event_id) as alerts, SUM(e.alerts) as packets
			#FROM event e
			#LEFT JOIN blacklists bl
				#ON bl.bl_id = e.blacklist
			#LEFT JOIN rules r
				#ON r.rule_id = e.rule
			#WHERE
				#e.start >= '%s'
				#AND (
					#r.hide = 0 OR bl.hide = 0
				#)
			#GROUP BY username
			#ORDER BY alerts DESC
			#LIMIT 10
		#", date('Y-m-d', strtotime(date('Y-m-d', gmmktime()) . ' -7days')) ));
		#$users = array();
		
		#// Loop through results and put into array
		#if($rst){
			#while($user = mysql_fetch_assoc($rst)){
				#$users[] = $user;
			#}
		#} else {
			#// 
			#echo mysql_error();
		#}
		
		#// Return array of users
		#return $users;
	#}
#}

#?>

def getOverview(start, finish, username=None):
    delta = end - finish;
    
    if delta <= timedelta(days=4):
        interval = timedelta(hour=1)
        sqldateformat = r'%Y-%m-%d %H:00:00'
    else if delta <= timedelta(months=3):
        interval = timedelta(day=1)
        sqldateformat = r'%Y-%m-%d'
    else if delta <= timedelta(years = 3):
        interval = timedelta(month=1)
        sqldateformat = r'%Y-%m'
    else:
        interval = timedelta(year=1)
        sqldateformat = r'%Y'
        
    events = Event.objects.filter(
        Q(rule__hide=False) | Q(blacklist__hide=False),
        start__gte = start,
        finish__lte = finish,
    ).extra(
        select={
            'timestamp': "DATE_FORMAT(event.start, %s)",
            'users' : "COUNT(DISTINCT(event.username))",
        },
        select_params = (sqldateformat,),
    ).values("timestamp", "blacklist", "rule").annotate(Count('event_id')).order_by("rule", "blacklist__name", "start")
    
    if username:
        events = events.filter(username=username)
    
    grouping = defaultdict(dict)
    
    for event in events:
        """
        Determine if event is a blacklist or rule, and if a rule
        check whether a rule name has been set for it. Store events in alertinfo
        """
        
        event.alertinfo
        if event.blacklist.bl_id > 0:
            grouping[event.blacklist][event.timestamp] = event.alerts
        else if event.rulename != "":
            grouping[
                "{rule_name}[{rule}]".format(
                    rule_name = event.rule_name, rule = event.rule
                )
            ][event.timestamp] = event.alerts;
        else:
            grouping["snort_" + event.rule][event.timestamp] = event.alerts
    
    grouping = dict(grouping)

"""
public function getOverview($from, $to, $username=""){
		
		// Work out the length of time between two dates
		$diff = strtotime($to) - strtotime($from);
		
		// Work out the date format, SQL date format and interval
		// period between the points.
		// ---
		// If under 4 days, show hourly intervals
		if ($diff <= (60*60*24*4)){
			$dateformat = 'Y-m-d H:00:00';
			$sqldateformat = '%Y-%m-%d %H:00:00';
			$interval = "1 hour";
		// If under 3 months, show daily intervals
		} elseif ($diff <= (60*60*24*31*3)) {
			$dateformat = 'Y-m-d';
			$sqldateformat = '%Y-%m-%d';
			$interval = "1 day";
		// If under 3 years, show monthly intervals
		} elseif ($diff <= (60*60*24*31*12*3)) {
			$dateformat = 'Y-m';
			$sqldateformat = '%Y-%m';
			$interval = "1 month";
		// Else yearly intervals
		} else {
			$dateformat = 'Y';
			$sqldateformat = '%Y';
			$interval = "1 year";
		}
		
		// Set start and end times, in timestamp form
		$start = strtotime( date($dateformat, strtotime($from) ) );
		$end = strtotime( date($dateformat, strtotime($to) ) );
		
		// Add SQL WHERE clause for username, if one was passed into the argument
		$user_where = ($username != "")
			? sprintf("AND username = '%s'", $username)
			: "";
		
		// Generate required SQL query for data
		$sql = sprintf("
			SELECT DATE_FORMAT(e.start, '%s') as timestamp, COUNT(e.event_id) as alerts, bl.name as blacklist, rule, rule_name, rule_class, COUNT(DISTINCT(e.username)) as users
			FROM event e
			LEFT JOIN blacklists bl
				ON e.blacklist = bl.bl_id
			LEFT JOIN rules r
				ON r.rule_id = e.rule
			WHERE
				e.start >= '%s'
				AND e.finish <= '%s'
				AND (r.hide = 0 OR bl.hide = 0)
				%s
			GROUP BY DATE_FORMAT(e.start, '%s'), bl.bl_id, rule
			ORDER BY rule ASC, bl.name ASC, e.start ASC
		", $sqldateformat, $from, $to, $user_where, $sqldateformat);
		
		// Fetch result
		$rst = mysql_query($sql);
		$grouping = array();
		
		// If a result exists, loop through results
		if($rst){
			while($row = mysql_fetch_assoc($rst)){
				// Convert datetime to timestamp
				$row['timestamp'] = strtotime($row['timestamp']);
				
				// Determine if event is a blacklist or rule, and if a rule
				// check whether a rule name has been set for it. Store events
				// in an array timestamp=>alertinfo
				if(!is_null($row['blacklist']) || $row['blacklist'] > 0){
					$grouping[$row['blacklist']][$row['timestamp']] = $row['alerts'];
				} elseif(!is_null($row['rule_name']) && $row['rule_name'] != ''){
					$grouping[$row['rule_name'].'['.$row['rule'].']'][$row['timestamp']] = $row['alerts'];
				} else {
					$grouping['snort_' . $row['rule']][$row['timestamp']] = $row['alerts'];
				}
			}
		} else {
			// Else chuck out errors
			mysql_error();
		}
		
		// Unset MySQL result, no longer needed
		unset($rst);
		
		// Loop through each alert/blacklist group of alerts
		foreach($grouping as $key => $group){
			// Work out the total number of alerts within current group
			$totals[$key] = array_sum($group);
			
			$unset = 0;
			
			// Loop through each alert
			foreach($group as $timestamp => $alert){
				// Set dates for previous, current and next points
				$date = $timestamp;
				$prev = strtotime(date($dateformat, $date) . ' -' . $interval);
				$next = strtotime(date($dateformat, $date) . ' +' . $interval);
				
				// Check previous interval, set to 0 if not set
				if ( !isset( $grouping[$key][$prev] ) && $prev > $start){
					if($unset == 0){
						$grouping[$key][$prev] = 0;
						$set = true;
					}
				}
				
				// Check next interval, set to 0 if not set
				if ( !isset( $grouping[$key][$next] ) && $next < $end){
					$grouping[$key][$next] = 0;
					$unset = 0;
					$set = true;
				}
				
				// If previous and next points have been set...
				if(!$set){
					// If 3 points in a row are the same
					if( $grouping[$key][$prev] == $grouping[$key][$next] && $grouping[$key][$prev] == $alert){
						// unset current point
						unset($grouping[$key][$timestamp]);
						$unset = $grouping[$key][$prev];
					} elseif($unset == $grouping[$key][$next] && $unset == $alert ){
						// unset current point
						unset($grouping[$key][$timestamp]);
					} else {
						$unset = 0;
					}
				}
				
				// Reset the set variable
				$set = false;
			}

			// Add starting point
			if(!isset($grouping[$key][$start])){
				$grouping[$key][$start] = 0;
			}
			
			// Add ending point
			$checkend = ($interval == "1 hour")
				? ($end - 3600)
				: $end;
			
			// Add end point if not set
			if(!isset($grouping[$key][$checkend]) ){
				$grouping[$key][$checkend] = 0;
			}
			
			// Sort array by key value (timestamp)
			ksort($grouping[$key]);
		}
		
		// Loop through entire arary again, offsetting timestamps for Flot
		// which only accepts UTC timestamps!
		foreach($grouping as $key => $group){
			foreach($group as $time => $alerts){
				$return[] = '[' . (($time+3600)*1000) . ',' . $alerts . ']';
			}
			
			// Generate information for rule/blacklist
			$grouping[$key] = array(
				'name' => $key,
				'json' => '[' . implode(', ', $return) . ']',
				'total' => $totals[$key]
			);
			unset($return);
		}
		
		// Return data
		return $grouping;
	}
"""
