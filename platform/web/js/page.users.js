$(document).ready(function(){	
	$('a.viewuser').button();
	
	
	$('#date a.clear').button();
	$('#date a.clear').click(function(){
		$(this).parent().find('input').val('');
		return false;
	});
	
	$('.datepicker').datetimepicker({
		dateFormat: 'yy-mm-dd'
	});
	$('#apply a, #apply input').button();
	
	$('#filters .checkboxes input').change(function(){
		curr = $(this);
		group = curr.parent().parent();
		checked = group.find('input:checked');
		
		if(!curr.hasClass('all') && curr.is(':checked')){
			group.find('input.all').prop("checked", false);
		}
		
		if(curr.hasClass('all') && curr.is(':checked')){
			group.find('input:checked').each(function(){
				ce = $(this);
				if(!ce.hasClass('all')){
					ce.prop("checked",false);
				}
			})
		}
	});
});