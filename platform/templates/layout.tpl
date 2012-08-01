{strip}
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html>
	<head>
		{include file="html-header.tpl"}
	</head>
	<body>
		<div id="container">
			<div id="inner-wrapper">
				<h1 id="sitetitle"><a href="/">eduroam Wireless Malware Monitoring</a></h1>
				<span id="lastupdated"><strong>Last Updated:</strong> {$lastupdated}</span>
				
				<div id="menu-search">
					<ul id="menu">
						<li><a href="/">Dashboard</a></li> |&nbsp;
						<li><a href="/index.php?page=users">Users</a></li> |&nbsp;
						<li><a href="/index.php?page=settings">Settings</a></li>
					</ul>
					
					<div id="search" class="ui-widget">
						<div id="user-search">
							<label for="usersearch">Search for User:</label><input type="text" id="usersearch" name="user" value="" style="width: 250px; padding: 5px;" />
						</div>
						
						<div id="date-search">
							<form method="get" action="/index.php">
								<input type="hidden" name="page" value="users" />
								<input type="hidden" name="action" value="filter" />
								<input type="hidden" name="rules[all]" value="1" />
								<input type="hidden" name="blacklists[all]" value="1" />
								
								<label for="searchfrom">Search from:</label>
								<input type="text" id="searchfrom" name="date[from]" value="" />
								<label for="searchto">to</label>
								<input type="text" id="searchto" name="date[to]" value="" />
								<input type="submit" class="button" value="Search" />
							</form>
						</div>
					</div>
					
					<div id="log">
					</div>
				</div>
				{$content}
			</div>
			
			<div id="footer">This is a 3rd Year Project by Jon Hargest (<a href="mailto:jh4g09@ecs.soton.ac.uk">jh4g09@ecs.soton.ac.uk</a>)</div>
		</div>
	</body>
</html>
{/strip}