$(function(){
    "use strict";
    function setupCharts(data){
        var graph_data = {
            results : {},
            total : {}
        },
        histogram_options = {
            xaxis: { mode: "time" },
            series: {
                bars: {
                    show: true,
                    fill: true,
                    steps: false
                },
                points: {
                    show: true
                }
            },
            grid: { hoverable: true, clickable: true },
            legend: {
                show: true,
                position: "ne",
                margin: [-130, 0]
            }
        },
        pie_options = {
            series: {
                pie: {
                    innerRadius: 0.5,
                    show: true
                }
            },
            grid: { hoverable: true },
            legend: {
                show: true,
                position: "ne",
                margin: [-10, 0]
            }
        };
        $.plot($("#chart1"), data, histogram_options);
                
        var totals = Array();
        
        
        _.each(data, function(item, i, data){
            item.total = 0;
            _.each(item.data, function(point){
                item.total += point[1];
            });
            totals.push(
                {
                    label : item.label,
                    data : item.total,
                    color : item.color
                }
            );
        });
        
        console.log(totals);
        $.plot($("#donut"), totals, pie_options);
    }
    
    var xdate = new XDate(),
        max = xdate.getTime(),
        min = xdate.clone().addYears(-1,true).getTime();
    
    $( "#slider-range" ).slider({
        range: true,
        min: min,
        max: max,
        values : [min, max],
        slide: function ( event,ui ) {
            $("#id_earliest").val(new XDate(ui.values[0]).toJSON());
            $("#id_latest").val(new XDate(ui.values[1]).toJSON());
        },
        change: function( event, ui ) {
            $(this).slider("option", "max", new XDate().getTime());
            $.get(
                "/activity.json",
                {
                    earliest : new XDate(ui.values[0]).toJSON(),
                    latest : new XDate(ui.values[1]).toJSON()
                },
                setupCharts,
                "json"
            );
        }
    });
});
    
