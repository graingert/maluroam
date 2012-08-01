{strip}
<form method="get" action="/index.php?page=users">
<input type="hidden" value="users" name="page" />
<input type="hidden" value="filter" name="action" />
<div id="filters">
	<div id="date">
		<h3 class="title">Date</h3>
		<div class="filter">
			<label for="date[from]">From:</label>
			<input name="date[from]" value="{$filters.from}" type="text" class="datepicker" />
			<a class="clear" href="#">x</a>
		</div>
		
		<div class="filter">
			<label for="date[to]">To:</label>
			<input name="date[to]" value="{$filters.to}" type="text" class="datepicker" />
			<a class="clear" href="#">x</a>
		</div>
	</div>
	
	<div id="rules" class="checkboxes">
		<h3 class="title">Rules</h3>
		<div class="filter all">
			<label for="rules[all]">All Rules:</label> <input name="rules[all]" type="checkbox" value="1" class="all" {if $filters.rules eq "all"}checked=checked{/if} />
		</div>
		{foreach from=$rules item=rule name=rulefilter}
			<div class="filter">
				<label for="rules[{$rule.rule}]">{$rule.name}[{$rule.rule}]:</label> <input name="rules[{$rule.rule}]" type="checkbox" value="1" {if $filters.rules[$rule.rule] eq 1}checked=checked{/if} />
			</div>		
		{/foreach}
	</div>
	
	<div id="blacklists" class="checkboxes">
		<h3 class="title">Blacklists</h3>
		<div class="filter all">
			<label for="blacklists[all]">All Blacklists:</label> <input name="blacklists[all]" type="checkbox" class="all" value="1" {if $filters.blacklists eq "all"}checked=checked{/if} />
		</div>
		{foreach from=$blacklists item=blacklist name=blacklistfilter}
			<div class="filter">
				<label for="blacklists[{$blacklist.bl_id}]">{$blacklist.name}:</label> <input name="blacklists[{$blacklist.id}]" type="checkbox" value="1" {if $filters.blacklists[$blacklist.id] eq 1}checked=checked{/if} />
			</div>		
		{/foreach}
	</div>
	
	<div id="apply">
		<input class="button" type="submit" value="Apply Filters" />
		<a class="button" href="/index.php?page=users&action=resetfilters">Reset Filters</a>
	</div>
</div>
</form>
{/strip}