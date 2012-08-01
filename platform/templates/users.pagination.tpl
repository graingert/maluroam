{strip}
<div class="pagination ui-accordion-header ui-helper-reset ui-state-default ui-state-active">
	{if $info.page neq 1}
	<span class="prev">
		<a class="prev" href="/index.php?page=users&pg={$info.page-1}">&laquo; Prev</a>
	</span>
	{/if}
	
	<span class="center bold">Page {$info.page} of {$info.max_pages} ({$info.total_users} Users)</span>
	
	{if $info.page lt $info.max_pages}
	<span class="next">
		<a class="next" href="/index.php?page=users&pg={$info.page+1}">Next &raquo;</a>
	</span>
	{/if}
</div>
{/strip}