<div id="user">
    <h1 class="title">User: {$user.user}</h1>
    
    <div id="tabs">
        <ul>
            <li><a href="#ips">Malicious IPs</a></li>
            <li><a href="#alerts">Alert Totals</a></li>
            <li><a href="#l28d">Last 28 Days</a></li>
        </ul>
        
        <div id="ips">
            <div class="table">
                <div class="table-header ui-accordion-header ui-helper-reset ui-state-default ui-state-active ui-corner-top">
                    <span class="col1">IP Address</span>
                    <span class="col2">Blacklist / Rule</span>
                    <span class="col3">Alerts</span>
                    <span class="col4">Packets</span>
                    <span class="col5">Earliest Interaction</span>
                    <span class="col6">Latest Interaction</span>
                </div>
                {foreach from=$user.statistics.ip_occ item=stat}
                    <div class="table-row">
                        <span class="col1">{$stat.ip}</span>
                        <span class="col2">
                            {if $stat.blacklist neq ""}
                                {$stat.blacklist}
                            {elseif $stat.rule_name neq ""}
                                {$stat.rule_name}[{$stat.rule}]
                            {else}
                                {$stat.rule}
                            {/if}
                        </span>
                        <span class="col3">{$stat.alerts}</span>
                        <span class="col4">{$stat.packets}</span>
                        <span class="col5">{$stat.earliest}</span>
                        <span class="col6">{$stat.latest}</span>
                    </div>
                {/foreach}
            </div>
        </div>
    
        <div id="alerts">
            <div class="table">
                <div class="table-header ui-accordion-header ui-helper-reset ui-state-default ui-state-active ui-corner-top">
                    <span class="col1">Blacklist / Rule</span>
                    <span class="col2">Total %</span>
                    <span class="col3">Alerts</span>
                    <span class="col4">Packets</span>
                    <span class="col5">Earliest Interaction</span>
                    <span class="col6">Latest Interaction</span>
                </div>
                {foreach from=$user.statistics.alert_occ item=stat}
                    <div class="table-row">
                        <span class="col1">
                            {if $stat.blacklist neq ""}
                                {$stat.blacklist}
                            {elseif $stat.rule_name neq ""}
                                {$stat.rule_name}[{$stat.rule}]
                            {else}
                                {$stat.rule}
                            {/if}
                        </span>
                        <span class="col2">{math equation="(alert/total)*100" format="%.2f" alert=$stat.alerts total=$user.statistics.total_alerts}%</span>
                        <span class="col3">{$stat.alerts}</span>
                        <span class="col4">{$stat.packets}</span>
                        <span class="col5">{$stat.earliest}</span>
                        <span class="col6">{$stat.latest}</span>
                    </div>
                {/foreach}
            </div>
        </div>
        
        <div id="l28d" style="display: block;">
            <div id="chart" style="margin: 25px 125px 25px 25px; height: 450px;">
            
            </div>
        </div>
    </div>
    
    
    <h2 class="title">All User Events</h2>
    <div id="user-events">
        {foreach from=$user.events item=month key=month_date}
            <h2><a href="#">{$month.label} ({$month.total} days of activity)</a></h2>
            <div class="month-events" style="display: inline-block;">
                {foreach from=$month.events item=day key=day_date}
                    <h3><a href="#">{$day.label} ({$day.total} events, {$day.packets} packets)</a></h2>
                    
                    <div class="day-events" style="display: inline-block;">
                        <table width="864" class="hover">
                            <thead>
                                <th>Src. IP</th>
                                <th>Flow</th>
                                <th>Dst. IP</th>
                                <th class="left">Time</th>
                                <th class="left">Blacklist / Rule</th>
                                <th class="left">Packets</th>
                                <th>More Info</th>
                            </thead>
                        
                            <tbody style="font-family: 'Courier New';">
                                {foreach from=$day.events item=event}
                                <tr class="entry">
                                    <td align="center">{$event.ip_src}</td>
                                    <td align="center">{if $event.twoway == true}<->{else}->{/if}</td>
                                    <td align="center">{$event.ip_dst}</td>
                                    <td>{$event.start}</td>
                                    <td>{if $event.blacklist_name neq ""}{$event.blacklist_name}{else}{$event.rule}{/if}</td>
                                    <td>{if $event.twoway == true}{$event.alerts.total}{else}{$event.alerts}{/if}</td>
                                    <td align="center"><button class="radiusButton">Display</button></td>
                                </tr>
                                <tr class="radius-info-row" style="display:none;">
                                    <td colspan=7 align="left">
                                        {if $event.twoway eq true}
                                            <div class="radius-row">
                                                <strong>Packets To: </strong> {$event.alerts.to}
                                                <strong>Packets From: </strong> {$event.alerts.from}
                                            </div>
                                        {/if}
                                        <div class="radius-row">
                                            <strong>Account Unique ID:</strong> {$event.radius_info.acctuniqueid}   
                                        </div>
                                        <div class="radius-row">
                                            <strong>Account Session ID:</strong> {$event.radius_info.acctsessionid} 
                                        </div>
                                        {*
                                        <div class="radius-row">
                                            <strong>Account Session Time:</strong> {math equation="floor(seconds / (60*60))" seconds=$event.radius_info.acctsessiontime}h {math equation="floor((seconds % (60*60))/60)" seconds=$event.radius_info.acctsessiontime}m {math equation="(seconds % (60*60)) % 60" seconds=$event.radius_info.acctsessiontime}s
                                        </div>
                                        *}
                                        <div class="radius-row">
                                            <strong>Realm:</strong> {$event.radius_info.realm}  
                                        </div>
                                        <div class="radius-row">
                                            <strong>Called Station ID:</strong> {$event.radius_info.calledstationid} <strong>Calling Station ID:</strong> {$event.radius_info.callingstationid}
                                        </div>
                                    </td>
                                </tr>
                                {/foreach}
                            </tbody>
                        </table>
                    </div>
                {/foreach}
            </div>
        {/foreach}
    </div>
</div>
<script type="text/javascript">
    $(document).ready(function(){ldelim}
        l28d_data = [
        {foreach from=$user.l28d item=group name=time}
            {ldelim}
                "label": "{$group.name}",
                "data": {$group.json},
                "color": {$smarty.foreach.time.iteration-1}
            {rdelim},
        {/foreach}
        ];
        user.setupUser();
    {rdelim});
</script>
