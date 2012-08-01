<?php 

/* Connect to 3yp database on local machine */
$db_3yp = mysql_connect('localhost', '3yp', '3yplatform+');	
if (!$db_3yp) {
    die('Could not connect: ' . mysql_error());
} else {
	mysql_select_db('3yp_platform', $db_3yp);
}

?>