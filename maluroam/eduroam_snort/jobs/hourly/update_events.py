from django_extensions.management.jobs import HourlyJob
from django.db import connections
from maluroam.eduroam_snort.models import Blacklist, Event
"""
This updater script fetches events from the Snort database from the last
hour, matches events with authentication logs from Radius, and stores
the result in the platform database.
"""
from datetime import datetime
from dateutil.tz import tzutc

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

class Job(HourlyJob):
    help = "Update events from Snort db"
    
    def execute(self):
        script = Script.objects.get_or_create(
            name="updater.events.php",
            defaults={
                "updated":datetime.min.replace(tzinfo=tzutc()),
            }
        )
        now = datetime.now(tzutc())
        assert(script.updated < now)
        
        snort = connections['snort'].cursor()
        snort.execute(
            """
            SELECT INET_NTOA(ip_src) AS ip_src, INET_NTOA(ip_dst) AS ip_dst, MIN(e.timestamp) as start, MAX(e.timestamp) as finish, COUNT(e.cid) as alerts,
                s.sig_sid as rule, sc.sig_class_name AS rule_class, s.sig_gid as sig_gid
            FROM event e
            INNER JOIN signature s
                ON s.sig_id = e.signature
            INNER JOIN sig_class sc
                ON s.sig_class_id = sc.sig_class_id
            INNER JOIN iphdr ip
                ON e.cid = ip.cid
            WHERE
                (s.sig_gid = '136' OR sc.sig_class_name = 'trojan-activity')
                
                AND e.timestamp >= %s
                AND e.timestamp < %s
        
                AND INET_NTOA(ip_dst) NOT LIKE '152.78.3.%%'
                AND INET_NTOA(ip_src) NOT LIKE '152.78.3.%%'
            GROUP BY ip_src, ip_dst, DATE_FORMAT(e.timestamp, '%%Y-%%m-%%d %%H:00:00')
            ORDER BY e.timestamp ASC
            """,lastchecked.isoformat(), now.isoformat())
        # now is used to prevent overlap, it's explicit what we mean by
        # now rather than whatever is latest in the events db, we can
        # allways pick up events "missed" in the next call
        events = dictfetchall(snort)
        
        
        radius = connections['radius'].cursor()
        Blacklist.objects.all()
        
        


<?php
	
	/**
	 * Updater: Events
	 * ----------------------------------------------------------------------
	 * This updater script fetches events from the Snort database from the 
	 * last hour, matches events with authentication logs from Radius, and
	 * stores the result in the platform database.
	 */

	
	// Fetch blacklists
	$blacklist_sql = "SELECT * FROM blacklists";
	$blacklist_rst = mysql_query($blacklist_sql, $db_3yp);
	
	if(!is_null($blacklist_rst)){
		while($bl = mysql_fetch_assoc($blacklist_rst)){
			$bl['serialized'] = unserialize($bl['serialized']);
			$blacklists[] = $bl;
		}
	}
	unset($blacklist_rst);
	
	// Fetch events from snort database
	$sql = sprintf("
		SELECT INET_NTOA(ip_src) AS ip_src, INET_NTOA(ip_dst) AS ip_dst, MIN(e.timestamp) as start, MAX(e.timestamp) as finish, COUNT(e.cid) as alerts,
			s.sig_sid as rule, sc.sig_class_name AS rule_class, s.sig_gid as sig_gid
		FROM event e
		INNER JOIN signature s
			ON s.sig_id = e.signature
		INNER JOIN sig_class sc
			ON s.sig_class_id = sc.sig_class_id
		INNER JOIN iphdr ip
			ON e.cid = ip.cid
		WHERE
			(s.sig_gid = '136' OR sc.sig_class_name = 'trojan-activity')
			
			AND e.timestamp >= '%s'
			AND e.timestamp < '%s'

			AND INET_NTOA(ip_dst) NOT LIKE '152.78.3.%%'
			AND INET_NTOA(ip_src) NOT LIKE '152.78.3.%%'
		GROUP BY ip_src, ip_dst, DATE_FORMAT(e.timestamp, '%%Y-%%m-%%d %%H:00:00')
		ORDER BY e.timestamp ASC
	", $lastchecked, $datelimit);
	
	$rst = mysql_query($sql, $db_snort);
	
	// Fetch number of events, echo out for log_3yp.
	$numevents = mysql_num_rows($rst);
	log_3yp("Number of events from Snort: " . $numevents);
	
	if($numevents == 0){
		log_3yp($sql);
	}
	
	// Check there was a result
	if(!is_null($rst) && $numevents > 0){
	
		// Loop through results
		while($alert = mysql_fetch_assoc($rst)){
			$rows[] = $alert;
			
			// Check if beginning of IP starts with 152.78. prefix
			$ipsrc_chk = stripos($alert['ip_src'], '152.78.');
			$ipdst_chk = stripos($alert['ip_dst'], '152.78.');
			
			// Determine which IPs need to be looked up in radius database as some
			// events have both source and destination IP addresses as 152.178.x.x
			$ip_where = ( ($ipsrc_chk !== FALSE && $ipsrc_chk == 0) && ($ipdst_chk !== FALSE && $ipdst_chk == 0) )
				? sprintf("(framedipaddress = '%s' OR framedipaddress = '%s')", $alert['ip_src'], $alert['ip_dst'] )
				: ($ipsrc_chk !== FALSE && $ipsrc_chk == 0)
					? sprintf("framedipaddress = '%s'", $alert['ip_src'] )
					: sprintf("framedipaddress = '%s'", $alert['ip_dst'] );
			
			// Create MySQL statement to fetch user details from radius server
			$radius_sql = sprintf("
				SELECT *
				FROM ecs_radacct
				WHERE
					%s
					AND acctstarttime <= '%s'
					AND (
						acctstoptime >= '%s'
						OR acctstoptime IS NULL
					)
					AND DATE_FORMAT(acctstarttime, '%%Y-%%m-%%d') = '%s'
				GROUP BY username
				ORDER BY acctstarttime DESC
				LIMIT 1
			", $ip_where, $alert['start'], $alert['finish'], date('Y-m-d', strtotime($alert['start'])) );
			
			$radius_rst = mysql_query($radius_sql, $db_radius);
			
			// Check there was a result
			if(!is_null($radius_rst)){
				// Check number of users returned
				$num_users = mysql_num_rows($radius_rst);
				
				// If none returned, we don't know who it was
				if($num_users == 0){
					$user['username'] = 'Unknown';
				} else {
					// If a row was returned, we do!
					$user = mysql_fetch_assoc($radius_rst);
				}				
				
			}
			unset($radius_rst);
			
			
			// If a blacklist alert, determine which blacklist...
			if($alert['sig_gid'] == '136'){
				// Check which IP to match against blacklists
				$iptocheck = ($ipsrc_chk !== FALSE && $ipsrc_chk == 0)
					? $alert['ip_dst']
					: $alert['ip_src'];
				
				// Loop through blacklists
				foreach($blacklists as $blacklist){
					if(in_array($iptocheck, $blacklist['serialized'])){
						$alert['blacklist'] = $blacklist['bl_id'];
						break;
					}
				}
			} else {
				// Wasn't a blacklisted event
				$alert['blacklist'] = '0';
			}
			
			// Create MySQL insert format
			$alert_entries[] =
				sprintf("('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')",
					$user['username'],
					$user['radacctid'],
					$user['acctsessionid'],
					( ( $user['username'] != "Unknown" ) ? serialize($user) : "" ),
					$alert['ip_src'],
					$alert['ip_dst'],
					$alert['start'],
					$alert['finish'],
					$alert['alerts'],
					$alert['blacklist'],
					$alert['rule'],
					$alert['rule_class']
				);
			
			unset($user);
			unset($alert);
		}
	}
	
	if(count($alert_entries) > 0){
		// Insert events into platform database
		$insert_sql = sprintf("
			INSERT INTO event
			(`username`,`radius_account_id`,`radius_session_id`,`radius_info`,`ip_src`,`ip_dst`,`start`,`finish`,`alerts`,`blacklist`,`rule`,`rule_class`)
			VALUES %s
		", implode(',', $alert_entries));
		
		log_3yp('Attempted to insert following SQL : ' . PHP_EOL . $insert_sql);
		
		// Execute SQL and fetch affected row count
		$insert_rst = mysql_query($insert_sql, $db_3yp);
		$affected = mysql_affected_rows($db_3yp);
		
		// log_3yp rows affected
		$success = ($affected == -1)
			? log_3yp("Unsuccessful Inserts (".$affected." rows affected)")
			: log_3yp("Successful Inserts (".$affected." rows affected)");
	} else {
		log_3yp("No alerts found");
	}
	
	// Update date checked
	$lstchk_rst = mysql_query(sprintf("UPDATE scripts SET lastupdated = '%s' WHERE name = '%s'", date('Y-m-d H:i:s', gmmktime()), $thisscript), $db_3yp);
	if(mysql_affected_rows($db_3yp) > 0){
		log_3yp("Script Updated in Database: " . $datelimit . ", " . $thisscript);
	}
	
	
	function pre($array){echo "<pre>"; print_r($array); echo "</pre><br/>";}
	function log_3yp($msg){
		echo $msg . PHP_EOL . PHP_EOL;
	}
?>
