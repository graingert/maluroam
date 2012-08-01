<?php

/**
 * class: Toolchest
 * ------------------------------------------------------------
 * This is a basic class for general functions used across the
 * website. Can be accessed on any page through $this->tools
 */
class Toolchest {

	// Instance Variables
	public $smarty;


	// Constructor
	public function __construct(){}

	
	/**
	 * function : smarty
	 * ------------------------------------------------------------
	 * Define the smarty variable
	 */
	public function smarty(){
		global $smarty;
		$this->smarty = $smarty;
	}

	/**
	 * function : redirect
	 * ------------------------------------------------------------
	 * Wrapper function for the header(Location) function in php.
	 * Makes coding easier.
	 */
	public function redirect($redirection, $statusCode = '301'){
		switch($statusCode){
			case '301':
				header('HTTP/1.1 ' . $statusCode . 'Moved Permanently');
				break;

			case '401':
				header('HTTP/1.1 ' . $statusCode . 'Unauthorized');
				break;
		}

		header('Location: ' . $redirection);
		exit;
	}


	/**
	 * function : getCacheDirectory
	 * ------------------------------------------------------------
	 * Determine the cache directory location
	 */
    public function getCacheDirectory(){
        $dir = getcwd();
		
		$d = DIRECTORY_SEPARATOR;

        $dir = explode($d,$dir);
        unset($dir[count($dir)-1]);
        $dir = implode($d, $dir);
        $dir = $dir . $d . 'cache' . $d;
		
        return $dir;
    }


	/**
	 * function : getCache
	 * ------------------------------------------------------------
	 * This function either caches or returns the cached result of
	 * the desired function and arguments provided. Support for 
	 * custom objects is included, however, the functions need to be
	 * public in order to be accessed by this object.
	 */
    public function getCache($function, $time, $params = '', $obj = null){
    	// Determine cache directory, filename (function_md5(arguments) and filepath
        $dir = $this->getCacheDirectory();
        $filename = $function . "_" . md5(serialize($params));
        $path = $dir . $filename;

		// Is debugging on and caching off?
        if($this->smarty->debugging && isset($_GET['nocache'])){
            $data = call_user_func_array(array($this, $function), $params);
        // Else check if cache file exists, and when it was last updated
        } else if(file_exists($path) && (time() - filemtime($path)) < ($time * 60)){
        	// Within cache time, so unserialise the result and return data
            $data = unserialize(file_get_contents($path));
			if(is_a($data, "stdClass") && $data->type == "SimpleXMLElement"){
				$xml = $data->data;
				$data = simplexml_load_string($xml);
			}
		// Else file doesn't exist, or cache has expired. Call function and store result
        } else {
        	// Call function
        	$data = call_user_func_array(array((is_null($obj) ? $this : $obj), $function), $params);
        	
        	// If data is a SimpleXMLElement, encode as a Standard class and store
			if(is_a($data, "SimpleXMLElement")){
				$xml = new stdClass();
				$xml->type = "SimpleXMLElement";
				$xml->data = $data->asXML();
				file_put_contents($path, serialize($xml));
			} else {
				// Else just store serialised version
            	file_put_contents($path, serialize($data));
			}
        }
		
		// Return data
        return $data;
    }

	/**
	 * function : smarty_debugging
	 * ------------------------------------------------------------
	 * Sets the smarty debugging to true or false, depending on
	 * the session/get variables. If debugging enabled, this will
	 * display a pop-up window with the data held within the Smarty
	 * object.
	 */
	public function smarty_debugging(){
		if(isset($_GET['debugging']) && $_GET['debugging'] == "off"){
			$_SESSION['debugging'] = FALSE;
			$this->smarty->debugging = FALSE;
		} elseif(isset($_GET['debugging'])){
			$_SESSION['debugging'] = TRUE;
			$this->smarty->debugging = TRUE;
		} elseif(isset($_SESSION['debugging']) && $_SESSION['debugging'] == TRUE){
			$this->smarty->debugging = TRUE;
		}
	}
	
	
	/**
	 * function : getOverview
	 * ------------------------------------------------------------
	 * This function provides overview data from between two dates,
	 * with support to provide a username. The returned data is
	 * grouped by alert/blacklist, encoded into JSON data with UTC
	 * timestamps.
	 */
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
	
	/**
	 * function : fetchRules
	 * ------------------------------------------------------------
	 * This function returns all rules and associated rule names
	 * from the platform database.
	 */
	public function fetchRules(){
		// Execute SQL
		$query = mysql_query("SELECT DISTINCT(rule), rule_name AS name FROM event e LEFT JOIN rules r ON e.rule = r.rule_id WHERE r.hide = 0");
		$rules = array();
		
		// Fetch query results
		if($query){
			while($rule = mysql_fetch_assoc($query)){
				$rules[] = $rule;
			}
		}
		
		// Return rules
		return $rules;
	}
	
	/**
	 * function : fetchBlacklists
	 * ------------------------------------------------------------
	 * This function returns all blacklists and associated names
	 * from the platform database.
	 */
	public function fetchBlacklists(){
		// Execute SQL
		$query = mysql_query("SELECT DISTINCT(blacklist) AS id, bl.name FROM event e LEFT JOIN blacklists bl ON e.blacklist = bl.bl_id WHERE bl.hide = 0");
		$blacklists = array();
		
		// Fetch query results
		if($query){
			while($blacklist = mysql_fetch_assoc($query)){
				$blacklists[] = $blacklist;
			}
		}
		
		// Return blacklists
		return $blacklists;
	}
	
	/**
	 * function : pre
	 * ------------------------------------------------------------
	 * Outputs data in a <pre> (preformatted text) HTML element.
	 * Useful for analysing array structures when debugging.
	 */
	public function pre($data, $exit=false){
		// Output data in <pre> tags
		echo "<pre>"; print_r($data); echo "</pre><br/>";
		
		// Does the call want to exit after output sent?
		if($exit){
			exit;
		}
	}
}


?>