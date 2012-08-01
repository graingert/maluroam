<?php

/**
 * Page : SettingsPage extends Page class
 * ------------------------------------------------------------
 * This page provides information to blacklists and rules,
 * providing the ability to attach names to rules to make them
 * more easily identifiable on the website, and also an overview
 * of blacklists and when they were last updated.
 *
 * The ability to hide rules or blacklists is also available, so
 * that they are not displayed in results across the website.
 */
class SettingsPage extends Page {

	// Constructor
	public function __construct($smarty, $tools){
		parent::__construct($smarty, $tools);
	}

	// Overide executePage function
	public function executePage() {
		
		// Check if any data has been submitted
		if(isset($_POST)){
			// Determine what has been updated
			switch($_GET['update']){
				case 'rule':
					if(isset($_GET['id']) && $_GET['id'] != ""){
						$rule = mysql_real_escape_string($_GET['id']);
						$this->updateRule($rule);
					}
					break;
					
				case 'blacklist':
					if(isset($_GET['id']) && $_GET['id'] != ""){
						$blacklist = mysql_real_escape_string($_GET['id']);
						$this->updateBlacklist($blacklist);
					}
					break;
			}
		}
	
		// Fetch rules
		$sql = "
			SELECT DISTINCT(e.rule), rule_name, hide
			FROM event e
			LEFT JOIN rules r
				ON r.rule_id = e.rule
			WHERE
				blacklist = 0
		";
		
		$rst = mysql_query($sql);
		
		if($rst){
			while($row = mysql_fetch_assoc($rst)){
				$alerts[] = $row;
			}
		}
		unset($rst);
		
		// Fetch blacklists
		$rst = mysql_query("SELECT * FROM blacklists");
		if($rst){
			while($row = mysql_fetch_assoc($rst)){
				$blacklists[] = $row;
			}
		}
		
		// Send data to Smarty
		$this->assign('rules', $alerts);
		$this->assign('blacklists', $blacklists);
		
		return;
	}
	
	/**
	 * function : updateBlacklist
	 * ----------------------------------------------------------------------
	 * Update a blacklist as to whether it should be hidden or not
	 */
	private function updateBlacklist($blacklist){
		$hide = (isset($_POST['hide']) && $_POST['hide'] == 1)
			? 1
			: 0;
			
		$sql = sprintf("
			UPDATE blacklists
			SET
				hide = '%s'
			WHERE bl_id = '%s'
		", $hide, $blacklist);
		
		$rst = mysql_query($sql);
		
		return mysql_affected_rows();
	}
	
	/**
	 * function : updateBlacklist
	 * ----------------------------------------------------------------------
	 * Update a rule, toggle visibility or change the rule name
	 */
	private function updateRule($rule){
		// Check whether the rule exists in any events
		$sql = sprintf("
			SELECT COUNT(e.event_id) as events
			FROM event e
			WHERE rule = '%s'", $rule);
		
		$rst = mysql_query($sql);
		$numevents = mysql_fetch_assoc($rst);
		$numevents = $numevents['events'];
		unset($rst);
		
		// If the rule exists...
		if($numevents > 0){
		
			// Check whether the rule exists in the rule table
			$sql = sprintf("
				SELECT rule_id
				FROM rules r
				WHERE rule_id = '%s'", $rule);
			$rst = mysql_query($sql);
			
			// Determine whether the user wants to hide it or not
			$hide = (isset($_POST['hide']) && $_POST['hide'] == 1)
				? 1
				: 0;
			
			// If it currently exists, update the row
			if(mysql_num_rows($rst) == 1){
				$sql = sprintf("
					UPDATE rules
					SET
						rule_name = '%s',
						hide = '%s'
					WHERE rule_id = '%s'
				", mysql_real_escape_string($_POST['rulename']), $hide, $rule);
			
			// Otherwise insert a new row
			} else {
				$sql = sprintf("
					INSERT INTO rules (`rule_id`,`rule_name`,`hide`)
					VALUES ('%s','%s',%s)
				", $rule, mysql_real_escape_string($_POST['rulename']), $hide);
			}
			
			// Execute the query
			$rst = mysql_query($sql);
			
			return mysql_affected_rows();
		} else {
			return false;
		}
	}
}

?>