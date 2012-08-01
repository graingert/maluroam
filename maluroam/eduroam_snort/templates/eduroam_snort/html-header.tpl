<title>eduroam Wireless Malware Monitoring - {$template|ucwords}</title>
{* Include jQuery & jQuery UI *}
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.7.1/jquery.min.js"></script>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.18/jquery-ui.min.js"></script>
<link href="/css/start/jquery-ui-1.8.18.custom.css" rel="stylesheet" type="text/css">
<link href="/css/site.css" rel="stylesheet" type="text/css">
{* Include Flot & Flot Plugins *}
<script type="text/javascript" src="/js/jquery.flot.min.js"></script>
<script type="text/javascript" src="/js/jquery.colorhelpers.min.js"></script>
<script type="text/javascript" src="/js/jquery.flot.crosshair.min.js"></script>
<script type="text/javascript" src="/js/jquery.flot.fillbetween.min.js"></script>
<script type="text/javascript" src="/js/jquery.flot.image.min.js"></script>
<script type="text/javascript" src="/js/jquery.flot.navigate.min.js"></script>
<script type="text/javascript" src="/js/jquery.flot.pie.min.js"></script>
<script type="text/javascript" src="/js/jquery.flot.resize.min.js"></script>
<script type="text/javascript" src="/js/jquery.flot.selection.min.js"></script>
<script type="text/javascript" src="/js/jquery.flot.stack.min.js"></script>
<script type="text/javascript" src="/js/jquery.flot.symbol.min.js"></script>
<script type="text/javascript" src="/js/jquery.flot.threshold.min.js"></script>
<script type="text/javascript" src="/js/misc.js"></script>
{if $template eq "dashboard"}
    <script type="text/javascript" src="/js/page.dashboard.js"></script>
{elseif $template eq "user"}
    <script type="text/javascript" src="/js/page.user.js"></script>
{elseif $template eq "users"}
    <script type="text/javascript" src="/js/page.users.js"></script>
{elseif $template eq "settings"}
    <script type="text/javascript" src="/js/page.settings.js"></script>
{/if}
