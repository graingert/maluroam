$(document).ready(function(){

		$('#usersearch').autocomplete({
			source: "/index.php?page=users&action=search",
			minLength: 2,
			select: function( event, ui ) {
				if( ui.item ){
					var href = "/index.php?page=user&user=" + ui.item.value;
					window.location.href = href;
				}
			}
		});
		
		$('#date-search .button').button();
		$('#date-search #searchfrom, #date-search #searchto').datetimepicker({
			dateFormat: 'yy-mm-dd'
		});
		
        $('#tabs').tabs();
        $('.button').button();
});
