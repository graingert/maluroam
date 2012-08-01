<?php

/**
 * Class: Page
 * ----------------------------------------------------------------------
 * This class defines the default behaviours that any page of the front
 * end should contain, while also setting up default instance variables
 * for access to the Smarty and Toolchest objects.
 */
class Page {

	// Instance variables
	public $template;
	public $smarty;
	public $tools;
	public $display_template;

	// Constructor
	public function __construct($smarty, $tools){
		global $db_3yp;
		
		// Create access to Smarty & Toolchest objects, define default display template
		$this->smarty = $smarty;
		$this->tools = $tools;
		$this->display_template = 'layout';

		// Determine when the events table was last updated.
		$lstchk_rst = mysql_query("SELECT lastupdated FROM scripts WHERE name = 'updater.events.php'");
		if(!is_null($lstchk_rst)){
			$lastchecked = mysql_fetch_assoc($lstchk_rst);
			$this->assign('lastupdated', date('j M, H:i:s', strtotime($lastchecked['lastupdated'])) );
		} else {
			$this->assign('lastupdated', "Database Connection Error");
		}
		
		// Generic Values		
		$this->template = 'template_' . $_GET['page'];
		$this->assign('prefix', 'http://' . $_SERVER['HTTP_HOST'] . '/');
		$this->assign('template', $_GET['page']);
		$this->assign('menu', substr($_GET['page'],0,4));
		$this->assign('date', date('Y', time()));

		$this->display();
	}
	
	/**
	 * function : executePage
	 * ------------------------------------------------------------
	 * This function is to be overidden by child classes for any
	 * custom Controller logic needed.
	 */
	protected function executePage(){
		return;
	}

	/**
	 * function : _executePage
	 * ------------------------------------------------------------
	 * This is a core function that shouldn't need to be changed by
	 * child classes. It determines the template that needs to be
	 * displayed in the "{$content}" variable in the main template
	 * file for the website.
	 */
	protected function _executePage(){
		$executed = $this->executePage();
		
		// Did a custom template get returned?
		if($executed != ""){
			$this->template = $executed;
		}
		
		return $this->fetch($this->template);
	}

	/**
	 * function : display
	 * ------------------------------------------------------------
	 * Attempts to display the view to the user.
	 */
	protected function display(){
		// Try to display templates
		try {
			$this->smarty->assign('content', $this->_executePage());
			$this->smarty->display($this->display_template . '.tpl');
		} catch(Exception $e) {
			// Something crashed
			while (1 < ob_get_level()) {
				ob_end_clean();
			}
			
			// Echo error
			echo $e;
		}
	}
	
	/**
	 * function : assign
	 * ------------------------------------------------------------
	 * Wrapper function to assign key-value pairs to Smarty object.
	 */
	protected function assign($key, $value){
		$this->smarty->assign($key, $value);
	}
	
	/**
	 * function : fetch
	 * ------------------------------------------------------------
	 * Wrapper function to fetch Smarty templates.
	 */
	public function fetch($template){
		return $this->smarty->fetch($template. '.tpl');
	}
	
	/**
	 * function : pre
	 * ------------------------------------------------------------
	 * Wrapper function to call pre() function in Toolchest
	 */
	public function pre($data, $exit=false){
		$this->tools->pre($data, $exit);
	}

}

?>