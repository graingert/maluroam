$(document).ready(function(){
	user = function(){
		
		function showTooltip(x, y, contents) {
	        $('<div id="tooltip">' + contents + '</div>').css( {
	            position: 'absolute',
	            display: 'none',
	            top: y + 15,
	            left: x + 15,
	            border: '1px solid #fdd',
	            padding: '2px',
	            'background-color': '#fee',
	            opacity: 0.80
	        }).appendTo("body").fadeIn(200);
	    }
	    		
		return {
			setupUser: function(){
				line_options = {
					xaxis: { mode: "time" },
					series: {
						lines: {
							show: true,
							fill: true,
							steps: false
						},
						points: {
							show: true
						},
					},
					grid: { hoverable: true },
					legend: {
					    show: true,
					    position: "ne",
					    margin: [-115,0]
					}
				};
				$.plot($("#l28d #chart"), l28d_data, line_options);
				
				var previousPoint = null;
		
				$("#l28d #chart").bind("plothover", function (event, pos, item) {
					
			        if (item) {
			            if (previousPoint != item.dataIndex) {
			                previousPoint = item.dataIndex;
			                
			                $("#tooltip").remove();
			                var x = item.datapoint[0].toFixed(2),
			                    y = item.datapoint[1].toFixed(2);
			                var thisdate = new Date(parseInt(x)-3600000);
		                	showTooltip(item.pageX, item.pageY, parseInt(y).toFixed(0) + " alerts on " + thisdate.format("j M"));
			            }
			        }
			        else {
			            $("#tooltip").remove();
			            previousPoint = null;            
			        }
			    });
				
				$('#tabs').tabs();
			}
		}
	
	}();
	
	$('#user-events').accordion({
		active: false,
		collapsible: true,
		header: "h2",
		autoHeight: false
	});
	
	$('.month-events').accordion({
		active: false,
		collapsible: true,
		header: "h3",
		autoHeight: false
	});
	
	$('.radiusButton').button();
	$('.radiusButton').click(function(){
		var thisbutton = $(this).find('span');
		var thisRow = $(this).parent().parent();
		var radiusInfo = thisRow.next();
		
		if(!radiusInfo.hasClass('activeBottom')){
			thisRow.addClass('activeTop');
			radiusInfo.addClass('activeBottom');
			thisbutton.html('Hide');
		} else {
			thisRow.removeClass('activeTop');
			radiusInfo.removeClass('activeBottom');
			thisbutton.html('Display');
		}
		
		radiusInfo.toggle();
	});
});