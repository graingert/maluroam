from django.shortcuts import render
from eduroam_snort.models import Event
from django.db.models import Q
from datetime import datetime, timedelta
from django.db.models import Count, Sum

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
