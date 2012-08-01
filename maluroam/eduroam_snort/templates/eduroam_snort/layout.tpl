<!DOCTYPE html>
<html>
    <head>
        <title>eduroam Wireless Malware Monitoring - {% block title %} Untitled {%block title %}</title>
            <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
            <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.18/jquery-ui.min.js"></script>
            
            <link href="{{ STATIC_URL }}/css/start/jquery-ui-1.8.18.custom.css" rel="stylesheet" type="text/css">
            <link href="{{ STATIC_URL }}/css/site.css" rel="stylesheet" type="text/css">
            
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.colorhelpers.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.crosshair.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.fillbetween.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.image.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.navigate.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.pie.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.resize.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.selection.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.stack.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.symbol.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/jquery.flot.threshold.min.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/misc.js"></script>
            
            <script type="text/javascript" src="{{ STATIC_URL }}/js/page.dashboard.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/page.user.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/page.users.js"></script>
            <script type="text/javascript" src="{{ STATIC_URL }}/js/page.settings.js"></script>

    </head>
    <body>
        <div id="container">
            <div id="inner-wrapper">
                <h1 id="sitetitle"><a href="/">eduroam Wireless Malware Monitoring</a></h1>
                <span id="lastupdated"><strong>Last Updated:</strong> {{lastupdated}}</span>
                
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
                {% block content %}
                {% endblock content %}
            </div>
            
            <div id="footer">This is a 3rd Year Project by Jon Hargest (<a href="mailto:jh4g09@ecs.soton.ac.uk">jh4g09@ecs.soton.ac.uk</a>)</div>
        </div>
    </body>
</html>
