<?php

/**
 * Page : UserPage extends Page class
 * ------------------------------------------------------------
 * This page provides both an overview and detailed level of
 * analysis of user alerts and acitivty.
 */
class UserPage extends Page {

	// Constructor
	public function __construct($smarty, $tools){
		parent::__construct($smarty, $tools);
	}

	// Override executePage function
	public function executePage() {
		$this->displayUser();
	}
	
	/**
	 * function : displayUser
	 * ----------------------------------------------------------------------
	 * Core function of the page, fetches relevant information about a user
	 * and sends it to Smarty.
	 */
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
	
	/**
	 * function : getUsersLast28Days
	 * ----------------------------------------------------------------------
	 * Cacheable function that fetches an overview of the specific user's
	 * last 28 days of activity for use with Flot.
	 */
	public function getUsersLast28Days($user){
		$nowdate = date('Y-m-d H:00:00', gmmktime());
		return $this->tools->getOverview(date('Y-m-d', strtotime($now.' -28 days')), $nowdate, $user);
	}	
	
	/**
	 * function : fetchUserStatistics
	 * ----------------------------------------------------------------------
	 * Fetch all relevant statistics to do with the associated user.
	 */
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

	
	/**
	 * function : fetchUserEvents
	 * ----------------------------------------------------------------------
	 * A function to reset all filters currently applied by the user.
	 */
	public function fetchUserEvents($user){
		$sql = sprintf("
			SELECT e.*, bl.name as blacklist_name, DATE_FORMAT(e.start, '%%Y-%%m') as month, DATE_FORMAT(e.start, '%%Y-%%m-%%d') as day
			FROM event e
			LEFT JOIN blacklists bl
				ON bl.bl_id = e.blacklist
			LEFT JOIN rules r
				ON r.rule_id = e.rule
			WHERE
				username = '%s'
				AND (r.hide = 0 OR bl.hide = 0)
			ORDER BY month DESC, day DESC, e.start ASC
		", $user);
		
		$rst = mysql_query($sql);
		
		if($rst){
			while($row = mysql_fetch_assoc($rst)){
				$rows[$row['month']][$row['day']][] = $row;
			}
		} else {
			echo mysql_error();
		}
		unset($rst);
		
		// Loop through all rows (months)
		foreach($rows as &$month){
			// Loop through all days
			foreach($month as $key => &$day){
				// Loop through each alert for that day 
				for($i = 0; $i < count($day); $i++){
					// Work out various intervals
					$thisevent = strtotime($day[$i]['start']);
					$nextevent = strtotime($day[$i+1]['start']);
					$eventafter = strtotime($day[$i+2]['start']); 
					
					// Get event information for current day
					$info = $day[$i];
					
					// Remove unrequired information
					unset($info['event_id']);
					unset($info['username']);
					
					// Determine if adjacent events are to the same IP address
					if($day[$i]['ip_src'] == $day[$i+1]['ip_dst'] && $day[$i]['ip_dst'] == $day[$i+1]['ip_src'] ){
						// Have they happened within 30 seconds
						if( abs($nextevent - $thisevent) < 30 ){
						
							// Combine information
							$info['alerts'] = array(
								'to' => $day[$i]['alerts'],
								'from' => $day[$i+1]['alerts'],
								'total' => $day[$i]['alerts'] + $day[$i+1]['alerts']
							);
							
							// Set that the event was traffic going two ways
							$info['twoway'] = true;
							
							// Get minimum start time
							if($day[$i+1]['start'] < $info['start']){
								$info['start'] = $dat[$i+1]['start'];
							}
							
							// Get maximum finish time
							if($day[$i+1]['finish'] > $info['finish']){
								$info['finish'] = $day[$i+1]['finish'];
							}
							
							// Unset merged event and reset key values for the day
							unset($day[$i+1]);
							$day = array_values($day);
							$merged++;
						}
					// Is there an event after next event to the same IP within 30 seconds
					} elseif($day[$i]['ip_src'] == $day[$i+2]['ip_dst'] && $day[$i]['ip_dst'] == $day[$i+2]['ip_src'] ){
						if( abs($nextevent - $eventafter) < 30 ){
							// The following logic is the same as above
							$info['alerts'] = array(
								'to' => $day[$i]['alerts'],
								'from' => $day[$i+1]['alerts'],
								'total' => $day[$i]['alerts'] + $day[$i+2]['alerts']
							);
							$info['twoway'] = true;
							
							if($day[$i+1]['start'] < $info['start']){
								$info['start'] = $dat[$i+2]['start'];
							}
							
							if($day[$i+1]['finish'] > $info['finish']){
								$info['finish'] = $day[$i+2]['finish'];
							}
							
							unset($day[$i+2]);
							$day = array_values($day);
							$merged++;
						}
					} else {
						// Else it was only a one way thing
						$info['twoway'] = false;
					}			
					
					// Convert start and finish times to reasonable representations (Hour:Minute:Second)
					$info['start'] = date('H:i:s', strtotime($info['start']));
					$info['finish'] = date('H:i:s', strtotime($info['finish']));
					
					// Unserialise radius information
					$info['radius_info'] = unserialize($info['radius_info']);
					
					// Keep tally of number of events
					$total += $info['alerts']['total'];
					$day[$i] = $info;
					
					// Unset variables
					unset($info);
					unset($nextevent);
				}
				
				// Create an array of information for the day
				$day = array(
					'label' => date('D jS', $thisevent),
					'events' => $day,
					'total' => count($day),
					'packets' => $total
				);
				$total = 0;
			}
			
			// Create an array of information for the month
			$month = array(
				'label' => date('F Y', strtotime($key)),
				'events' => $month,
				'total' => count($month)
			);
		}
		
		// Return data
		return $rows;
	}
}

?>