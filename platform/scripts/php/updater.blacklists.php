<?php
	
	/**
	 * Updater: Blacklists
	 * ----------------------------------------------------------------------
	 * This updater script fetches and updates all blacklists stored within
	 * the platform database. All blank and comment lines are removed.
	 */
	
	/* Connect to 3yp database on local machine */
	$db_3yp = mysql_connect('localhost', '3yp', '3yplatform+');	
	if (!$db_3yp) {
	    log_3yp('Could not connect: ' . mysql_error());
	    die();
	} else {
		mysql_select_db('3yp_platform', $db_3yp);
	}
	
	$rst = mysql_query("SELECT * FROM blacklists", $db_3yp);
	
	// Create an array of blacklists
	if(!is_null($rst)){
		while($bl = mysql_fetch_assoc($rst)){
			$bls[] = $bl;
		}
	}
	
	// Loop through all blacklists
	foreach($bls as $blacklist){
	
		// Fetch blacklist, remove comments and blank lines using wget and sed
		$command_fetchlists = sprintf("wget --quiet -O - '%s' | sed -e '/^\#/d' -e '/^$/d' > /etc/snort/blacklists/%s", $blacklist['url'], $blacklist['name']);
		exec($command_fetchlists);
		
		// Open File
		$file = fopen("/etc/snort/blacklists/".$blacklist['name'], "r");
		
		// If file has opened without errors
		if ($file) {
			// Loop through each line and create an array of IPs
		    while (($ip = fgets($file, 4096)) !== false) {
	    	    $ips[] = preg_replace('/\s/', '', $ip);
		    }
		    
		    // If it is not the end of the file after loops, error out.
		    if (!feof($file)) {
		        log_3yp("Error: unexpected fgets() fail");
		    }
		    
		    // Close file
		    fclose($file);
		    
		    // Serialise the array of IP addresses
		    $serialized = serialize($ips);
		    
		    // Check the differences with currently stored blacklist
		    if($blacklist['serialized'] != $serialized){
		    
		    	// Create UPDATE SQL
		    	$sql = sprintf("
		    		UPDATE blacklists
		    		SET
		    			serialized = '%s',
		    			updated = '%s'
		    		WHERE bl_id = '%s'
		    	", $serialized, date('Y-m-d H:i:s', gmmktime()), $blacklist['bl_id']);
		    	
		    	// Execute
		    	$rst = mysql_query($sql, $db_3yp);
		    	
		    	// If 1 affected row, success
		    	if(mysql_affected_rows($db_3yp) == 1){
		    		log_3yp($blacklist['name'] . ": Successfully updated");
		    	} else {
		    		log_3yp($blacklist['name'] . ": Failed to update. (".$sql.")");
		    	}
		    } else {
		    	// No need to update
		    	log_3yp($blacklist['name'] . ": Not updated");
		    }
		    unset($ips);
		}
	}
	
	// Kill Snort
	$command_killall = sprintf("killall -v snort");
	exec($command_killall, $ouput);
	print_r($output); echo PHP_EOL . PHP_EOL;
	
	// Start Snort
	$command_restart = sprintf("/usr/local/bin/snort -c /etc/snort/snort.conf -i p3p1 -D");
	exec($command_restart, $ouput);
	print_r($output);
	
	
	function log_3yp($msg){echo $msg . PHP_EOL . PHP_EOL;}
?>