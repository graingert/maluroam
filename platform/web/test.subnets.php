<?php

	/**
	 * file: test.subnets.php
	 * ------------------------------------------------------------------------------
	 * This page produces testing output. It fetches all IP addresses within the 
	 * University's subnet (152.78.0.0/16) associated with the username "Unknown", aka
	 * any events that could not be associated with a user. It then tests whether
	 * those IP addresses are within eduroam's subnets (.160.0/22, .204.0/22)
	 */
	
	// Define includes
	include_once('code/Database.class.php');
	require('Net/IPv4.php');
	
	// Define eduroam subnets
	$subnets = array(
		'152.78.160.0/22',
		'152.78.204.0/22'
	);
	
	// Print out header
	pre(sprintf('Test Harness for Unidentified IP Addresses<br/>Eduroam Subnets: %s', implode(', ',$subnets)));
	pre('----------------------------------------------------------------------');
	
	//////////////////////////////////////////
	// Fetch unique source IP addresses
	//////////////////////////////////////////
	// SQL for unique ip_src of Unknown users
	$sql = "
		SELECT DISTINCT(ip_src) as ip
		FROM event e
		WHERE
			username = 'Unknown' AND
			ip_src LIKE '152.78.%'
		ORDER BY ip ASC
	";
	
	// Execute result
	$rst = mysql_query($sql);
	
	// Add all IP addresses
	$i = 0;
	if($rst){
		while($row = mysql_fetch_assoc($rst)){
			$ips[$row['ip']] = $i;
			$i++;
		}
	} else {
		echo mysql_error();
	}
	
	
	//////////////////////////////////////////
	// Fetch unique destination IP addresses
	//////////////////////////////////////////
	// SQL for unique ip_dst of Unknown users
	$sql = "
		SELECT DISTINCT(ip_dst) as ip
		FROM event e
		WHERE
			username = 'Unknown' AND
			ip_dst LIKE '152.78.%'
		ORDER BY ip ASC
	";
	
	// Execute result
	$rst = mysql_query($sql);
	
	// Add any IPs from the result to the list that are not already there
	if($rst){
		while($row = mysql_fetch_assoc($rst)){
			if(!isset($ips[$row['ip']])){
				$ips[$row['ip']] = $i;
				$i++;
			}
		}
	} else {
		echo mysql_error();
	}
	
	// Flip array with keys
	$ips = array_flip($ips);
	
	// Loop through all IPs
	foreach($ips as $ip){
		$insubnet = false;
		$tsubnet = "";
		
		// Check against all subnets
		foreach($subnets as $subnet){
			$insubnet = (Net_IPv4::ipInNetwork($ip, $subnet));
			
			// Is in a subnet, so break out of loop
			if($insubnet){
				$tsubnet = $subnet;
				break;
			}
			
		}
		
		// Print out if IP is in a subnet or not
		if(!$insubnet){
			$msg = sprintf('User "Unknown", IP %-14s not in eduroam subnets', $ip);
		} else {
			$msg = sprintf('User "Unknown", IP %-14s in eduroam subnet: %s', $ip, $tsubnet);
		}
		
		pre($msg);
	}
	
function pre($data, $exit=false){
	echo "<pre style='padding:0px; margin: 0px;'>"; print_r($data); echo "</pre>";
	if($exit){
		exit;
	}
}	
	
?>