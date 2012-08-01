<?php
	
	/**
	 * file: index.php
	 * ------------------------------------------------------------------------------
	 * This is where all page requests for the web-based front-end should be routed 
	 * through. It includes all necessary classes and database connections for
	 * interactions with the Model.
	 */

	// Start / Load PHP Session
	session_start();
    
	// List of includes
	require_once('code/Page.class.php');
	require_once('code/Toolchest.class.php');
	include_once('code/Database.class.php');
	
	// Create a new Toolchest Object
	$tools = new Toolchest();

	// Create Smarty
	require('smarty/Smarty.class.php');
	$smarty = new Smarty();
    $tools->smarty($smarty);

	// -- Define Smarty variables / handlers / debugging
	$smarty->template_dir = '../templates';
	$smarty->compile_dir = '../cache';
	$smarty->cache_dir = '../cache';
	$tools->smarty_debugging();
	
	// Determine which Page class to load
	$_GET['page'] = (!isset($_GET['page']) || empty($_GET['page'])) ? 'dashboard' : $_GET['page'];
	$page = $_GET['page'];
	
	// Create the class name, attempt to load the PHP file
	$extendedClass = ucwords(strtolower($page)) . 'Page';
	$file = 'pages/' . ucwords(strtolower($page)) . '.page.php';
	
	// Check file exists before trying to open it...
	if(file_exists('../'.$file)){
		include_once($file);
	}
	
	// Create new page object for current page
	if(class_exists($extendedClass)){
		$page = new $extendedClass($smarty, $tools);
	} else {
		$page = new Page($smarty, $tools);
	}

?>