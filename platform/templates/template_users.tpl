{strip}
<div id="users">	
	{include file="users.pagination.tpl"}
	
	{include file="users.filters.tpl"}
	
	{if $users eq false}
		<div class="error">
			<span>No users were returned. Please check your filters or go back to <a href="/index.php?page=users">the first page</a>.</span>
		</div>
	{else}		
		<div class="table">
			<div class="table-header ui-accordion-header ui-helper-reset ui-state-default ui-state-active ui-corner-top">
				<span class="col1">Username</span></span>
				<span class="col2">Rules</span>
				<span class="col3">Blacklists</span>
				<span class="col4">Alerts</span>
				<span class="col5">Packets</span>
				<span class="col6">Earliest Alert</span>
				<span class="col7">Latest Alert</span>
			</div>
			{foreach from=$users item=user name=users}
				<div class="table-row{if $smarty.foreach.users.iteration is odd} odd{/if}">
					<span class="col1"><a href="/index.php?page=user&user={$user.username}">{$user.username}</a></span>
					<span class="col2">{if $user.rules eq ""}-{else}{$user.rules}{/if}</span>
					<span class="col3">{if $user.blacklists eq ""}-{else}{$user.blacklists}{/if}</span>
					<span class="col4">{$user.alerts}</span>
					<span class="col5">{$user.packets}</span>
					<span class="col6">{$user.earliest}</span>
					<span class="col7">{$user.latest}</span>
					<span class="col8"><a class="viewuser" href="/index.php?page=user&user={$user.username}">></a></span>
				</div>
			{/foreach}
		</div>
	{/if}
	
	{include file="users.pagination.tpl"}
</div>
{/strip}