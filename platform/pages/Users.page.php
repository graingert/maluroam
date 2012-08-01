<?php

/**
 * Page : UsersPage extends Page class
 * ------------------------------------------------------------
 * This page is designed for interactions through the view to
 * do with users. It will return an entire list of users
 * for searching via the View, and will also filter users and
 * events 
 */
class UsersPage extends Page {

	// Instance Variables
	public $users_per_page = 20;

	// Constructor
	public function __construct($smarty, $tools){
		parent::__construct($smarty, $tools);
	}

	// Overide executePage function
	protected function executePage() {
		if(!isset($_SESSION['filters'])){
			$this->resetFilters();
		}
	
		switch($_GET['action']){
			
			// AJAX search request -- ALWAYS EXIT
			case 'search':
				$this->tools->getCache('fetchUserList', 30, array($_GET['term']), $this); exit;
			
			// Filters have been changed
			case 'filter':
				$this->loadFilters(); break;
				
			// Reste filters
			case 'resetfilters':
				$this->resetFilters(); break;
				
			// Default action is to load users
			default:
				$filters = (isset($_SESSION['filters']))
					? $_SESSION['filters']
					: array();
				$this->loadUsers($filters); break;
		}
				
		// Send data to Smarty
		$this->assign('rules', $this->tools->getCache('fetchRules', 0, array()) );
		$this->assign('blacklists', $this->tools->getCache('fetchBlacklists', 0, array()));
		
		return;
	}
	
	/**
	 * function : resetFilters
	 * ----------------------------------------------------------------------
	 * A function to reset all filters currently applied by the user.
	 */
	public function resetFilters(){
		$_GET['date'] = array(
			'from' => '',
			'to' => ''
		);
		$_GET['rules']['all'] = "1";
		$_GET['blacklists']['all'] = "1";
		$this->loadFilters();
	}
	
	/**
	 * function : loadFilters
	 * ----------------------------------------------------------------------
	 * Apply filters that the user has selected and applied.
	 */
	public function loadFilters(){
		$filters = array();
	
		// Determine if a date range was selected
		if(isset($_GET['date'])){
			foreach($_GET['date'] as $key => $date){
				$filters[mysql_real_escape_string($key)] = sprintf("%s",mysql_real_escape_string($date));
			}
		}
		
		// Determine what rules are to be displayed
		if(isset($_GET['rules'])){
			// If all rules hasn't been selected...
			if($_GET['rules']['all'] != 1){
				foreach($_GET['rules'] as $rule => $on){
					if($on == 1){
						$rules[sprintf("%s",mysql_real_escape_string($rule))] = 1;
					}
				}
				$filters['rules'] = $rules;
			// Else display all rules
			} else {
				$filters['rules'] = "all";
			}
		// Else display NO rules
		} else {
			$filters['rules'] = false;
		}
		
		// Determine what blacklists are to be displayed
		if(isset($_GET['blacklists'])){
			// If all blacklists hasn't been selected
			if($_GET['blacklists']['all'] != 1){
				foreach($_GET['blacklists'] as $blacklist => $on){
					if($on == 1){
						$blacklists[sprintf("%s",mysql_real_escape_string($blacklist))] = 1;
					}
				}
				$filters['blacklists'] = $blacklists;
			// Else display all blacklists
			} else {
				$filters['blacklists'] = "all";
			}
		// Else display NO blacklists
		} else {
			$filters['blacklists'] = false;
		}
		
		// Save filter selections to the $_SESSION variable
		$_SESSION['filters'] = $filters;
	
		// Redirect user, so that they cannot interfere with $_GET variables.
		$this->tools->redirect('/index.php?page=users', 301);exit;
	}
	
	/**
	 * function : loadUsers
	 * ----------------------------------------------------------------------
	 * This function is the default action of the page. It will fetch all
	 * users and their related alert information. It will automatically detect
	 * any applied filters for the page.
	 */
	public function loadUsers($filters=array()){
	
		// Fetch cached total number of users in database (30 minute cache)
		$total_users = $this->tools->getCache('getNumberOfUsers', 0, array($filters), $this);
		
		// If a page is not set, set to 1
		if(!isset($_GET['pg'])){
			$_GET['pg'] = 1;
		}
		
		// Determine if the page will return anything
		$page = ( $_GET['pg'] > 0 && $_GET['pg'] <= ceil($total_users / $this->users_per_page) )
			? $_GET['pg']
			: false;
		
		// If page is out of range...
		if(!$page){
			$this->assign( 'users', false);
		} else {
			$this->assign( 'users', $this->displayUsers($page, $filters) );
		}
		
		// Assign all information to Smarty
		$this->assign( 'info', array(
			'page' => $page,
			'total_users' => $total_users,
			'max_pages' => ceil($total_users / $this->users_per_page),
			'users_per_page' => $this->users_per_page
		));
		
		$this->assign( 'filters', $_SESSION['filters']);
	}
	
	
	/**
	 * function : displayUsers
	 * ----------------------------------------------------------------------
	 * Core function of the page, to fetch a list of users with any saved
	 * filter selections.
	 */
	public function displayUsers($page, $filters=array(), $order="ORDER BY alerts DESC"){
		// Determine the limit required for the query (essentially what page)
		$limit = sprintf('LIMIT %s, %s', (($page-1)*$this->users_per_page), $this->users_per_page );
		
		// Get the SQL required for any filters...
		$filters_sql = $this->getFilterSQL($filters);
		
		// Create the SQL to fetch list of users
		$sql = sprintf("
			SELECT username, GROUP_CONCAT(DISTINCT(rule) SEPARATOR ',') as rules, GROUP_CONCAT(DISTINCT(bl.name) SEPARATOR ',') as blacklists, COUNT(e.event_id) as alerts, SUM(e.alerts) as packets, MIN(DATE_FORMAT(e.start,'%%Y-%%m-%%d')) as earliest, MAX(DATE_FORMAT(e.finish,'%%Y-%%m-%%d')) as latest
			FROM event e
			LEFT JOIN blacklists bl
				ON bl.bl_id = e.blacklist
			LEFT JOIN rules r
				ON r.rule_id = e.rule
			WHERE
				%s
				AND (r.hide = 0
				OR bl.hide = 0)
			GROUP BY username
			%s
			%s
		", $filters_sql, $order, $limit);

		$rst = mysql_query($sql);
		
		
		// If query executed successfully
		if($rst){
			// Loop through all users
			while($user = mysql_fetch_assoc($rst)){
				
				// Determine rules
				$user['rules'] =  explode(',', $user['rules']);
				foreach($user['rules'] as $key => $rule){
					if($rule == 1){
						unset($user['rules'][$key]);
						break;
					}
				}
				
				// Create a list for the view
				$user['rules'] = implode('<br/>', $user['rules']);
				$user['blacklists'] =  implode('<br/>', explode(',', $user['blacklists']));
				
				// Assign user information to an array of users
				$users[] = $user;
			}
		} else {
			// Query errored, display error.
			mysql_error();
		}
		
		return $users;
	}
	
	/**
	 * function : getNumberOfUsers
	 * ----------------------------------------------------------------------
	 * This function determines the total number of users with selected filters
	 */
	public function getNumberOfUsers($filters){
		
		// Fetch required SQL for the filter
		$filters_sql = $this->getFilterSQL($filters);
	
		// Create query
		$sql = sprintf("
			SELECT COUNT(DISTINCT(username)) AS total_users
			FROM event e
			LEFT JOIN blacklists bl
				ON bl.bl_id = e.blacklist
			LEFT JOIN rules r
				ON r.rule_id = e.rule
			WHERE
				%s
				AND (r.hide = 0
				OR bl.hide = 0)", $filters_sql);
		
		$rst = mysql_query($sql);
		
		// Fetch results or return 0 rows
		if($rst){
			$num_users = mysql_fetch_assoc($rst);
			$return = $num_users['total_users'];
		} else {
			$return = 0;
		}
		
		return $return;
	}
	
	/**
	 * function : getFilterSQL
	 * ----------------------------------------------------------------------
	 * Generates the required SQL clauses to apply filters to any queries
	 * fetching a list of users
	 */
	public function getFilterSQL($filters){
		$sql = array();
		
		// Determine if any filters are actually applied
		if(count($filters) > 0){
			// Date from
			if(isset($filters['from']) && $filters['from'] != '' ){
				$sql[] = sprintf("e.start >= '%s:00'", $filters['from']);
			}
			
			// Date to
			if(isset($filters['to']) && $filters['to'] != '' ){
				$sql[] = sprintf("e.finish < '%s:00'", $filters['to']);
			}
			
			// Rules
			if(isset($filters['rules']) ){
			
				// -- all rules
				if($filters['rules'] == "all"){
					$rsql = "e.rule != 1";
				// -- selected rules
				} else if(is_array($filters['rules'])) {
					foreach($filters['rules'] as $rule => $on){
						$rules[] = sprintf("'%s'", $rule);
					}
					$rsql = 'e.rule IN (' . implode(',', $rules) . ')';
				// -- no rules
				} elseif($filters['rules'] === false) {
					$rsql = 'e.rule = 0';
				}
			} else {
				// no rules
				$rsql = "e.rule != 1";
			}
			
			// Blacklists
			if(isset($filters['blacklists'])){
				// -- all blacklists
				if($filters['blacklists'] == "all"){
					$blsql = "e.blacklist != 0";
				// -- selected blacklists
				} else if(is_array($filters['blacklists'])) {
					foreach($filters['blacklists'] as $blacklist => $on){
						$blacklists[] = sprintf("'%s'", $blacklist);
					}
					$blsql = 'e.blacklist IN (' . implode(',', $blacklists) . ')';
				// -- no blacklists
				} elseif($filters['blacklists'] === false) {
					$blsql = 'e.blacklist = -1';
				}
			} else {
				// no blacklists
				$blsql = "e.blacklist = -1";
			}
			
			// Glue together rule & blacklist SQL components
			$sql[] = sprintf("( (%s) OR (%s) )", $rsql, $blsql);
		}
		
		// Return glued together SQL where clauses
		return implode(' AND ', $sql);
	}
	
	/**
	 * function : fetchUserList
	 * ----------------------------------------------------------------------
	 * Function called when searching for a user
	 */
	public function fetchUserList($term = ""){
		// Has a term (beginning of username) been sent?
		$where = ($term != "")
			? "AND username LIKE '" . mysql_real_escape_string($term) . "%'"
			: "" ;
			
		// Generate SQL
		$sql = sprintf("
			SELECT DISTINCT(username)
			FROM event e
			LEFT JOIN blacklists bl
				ON bl.bl_id = e.blacklist
			LEFT JOIN rules r
				ON r.rule_id = e.rule
			WHERE
				(r.hide = 0
				OR bl.hide = 0)
				%s
		", $where);
		
		$rst = mysql_query($sql);
		
		// Fetch any rows
		if($rst){
			while($row = mysql_fetch_assoc($rst)){
				$users[] = '"' . $row['username'] . '"';
			}
			
			if(is_array($users)){
				echo '[' . implode(',', $users) . ']';
			}
		}
	}

}

?>
