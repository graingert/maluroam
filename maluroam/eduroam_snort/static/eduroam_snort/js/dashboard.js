function OrderedSet(){
    this.dict = {}
    this.items = 0;
    this.get_color = function(url){
        if(!(this.dict.hasOwnProperty(url))){
            this.items++;
            this.dict[url] = this.items;
        }
        return this.dict[url];
    }
}

$(function(){
    "use strict";
    
    var xdate = new XDate(),
        max = xdate.getTime(),
        min = xdate.clone().addYears(-1,true).getTime(),
        orderedSet = new OrderedSet();
    
    $( "#slider-range" ).livequery(
        function(){
            $(this).slider({
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
        },
        function(){
            $(this).slider("destroy");
        }
    );
    
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
                    steps: false,
                    barWidth: 0
                },
                points: {
                    show: false
                },
                lines: {
                    show: false
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
        
        var barWidth = Infinity;
        var total_widths = 0;
        var totals = Array();
        _.each(data, function(item, i, data){
            item.total = 0;
            item.color = orderedSet.get_color(item.uri);
            _.each(item.data, function(point){
                item.total += point[1];
                barWidth = Math.min(point[2], barWidth);
                point.splice(2,1);
            });
            totals.push(
                {
                    label : item.label,
                    data : item.total,
                    color : item.color
                }
            );
        });
        
        histogram_options.series.bars.barWidth = barWidth;
        
        $.plot($("#chart1"), data, histogram_options);
        $.plot($("#donut"), totals, pie_options);
    }
});
    
