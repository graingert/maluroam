<div id="dashboard">
	<h1 class="title">Dashboard</h1>
	<form style="display: block; text-align: center; font-size: 10px;" >
		<div id="rangeSelector">
			<input type="radio" id="l24h" graphlabel="hours" name="radio" checked=checked /><label for="l24h">Last 24 hrs</label>
			<input type="radio" id="l3d" graphlabel="hours" name="radio" /><label for="l3d">Last 3 days</label>
			<input type="radio" id="l7d" graphlabel="days" name="radio" /><label for="l7d">Last 7 days</label>
			<input type="radio" id="l28d" graphlabel="days" name="radio" /><label for="l28d">Last 28 days</label>
			<input type="radio" id="l12m" graphlabel="months" name="radio" /><label for="l12m">Last 12 months</label>
		</div>
	</form>
	
	<h2 class="title updateRangeSpan">Suspected Malicious Activity<span></span></h2>
	<div class="graph hideLegend" style="position: relative;">
		<div id="chart1" style="display: block; margin: 10px 200px 25px 0; height: 450px;position: relative;"></div>
		<ul id="overviewLegend"></ul>
	</div>
	
	<div class="wrapper" style="display: block; padding: 25px;">
		<div class="box" style="width: 400px; padding-right: 50px;">
			<h2 class="title updateRangeSpan">Alert Totals Comparisons<span></span></h2>
			<div id="donut" style="display: inline-block; width: 400px; height:300px;position: relative;"></div>
		</div>
		
		<div class="box" id="users_overview">
			<h2 class="title">Last 7 Days  - Users</h2>
			<div id="users_overview" class="table" style="width: 450px;">
				<div class="table-header ui-accordion-header ui-helper-reset ui-state-default ui-state-active ui-corner-top">
					<span class="col1">Username</span>
					<span class="col2">Events</span>
					<span class="col3">Packets</span>
				</div>
				{foreach from=$users item=user name=users}
					<div class="table-row">
						<span class="col1"><a href="/index.php?page=user&user={$user.username}">{$user.username}</a></span>
						<span class="col2">{$user.alerts}</span>
						<span class="col3">{$user.packets}</span>
					</div>
				{/foreach}
			</div>
		</div>
	</div>
	{* Provide JSON data for graphs *}
	<script type="text/javascript">
		$(document).ready(function(){ldelim}
			$('#rangeSelector').buttonset();
			{foreach from=$overviews item=range name=ranges key=range_key}
				results_{$range_key} = [
					{foreach from=$range item=group name=time}
						{ldelim}
							"label": "{$group.name}",
							"data": {$group.json},
							"color": {$alert_colours[$group.name]}
						{rdelim},
					{/foreach}
				];
			{/foreach}
			
			{foreach from=$overviews item=range name=ranges key=range_key}
				total_{$range_key} = [
					{foreach from=$range item=group name=time}
						{ldelim}
							"label": "{$group.name}",
							"data": {$group.total},
							"color": {$alert_colours[$group.name]}
						{rdelim},
					{/foreach}
				];
			{/foreach}
			
			dashboard.setupCharts();
		{rdelim});
	</script>
</div>