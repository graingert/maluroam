$(function () {
    "use strict";
    window.dashboard = function () {
        var graph_data, histogram_options, pie_options, choiceContainer, rangeContainer, results, totals, graphlabel;
        graph_data = {
            results : {},
            total : {}
        };
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
        };
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
        choiceContainer = $("#overviewLegend");
        rangeContainer = $('#rangeSelector');
        results = "";
        totals = "";
        function updateLegend() {
            choiceContainer.html("");
            $.each(results, function (key, val) {
                var l, li;
                l = val.label;
                li = $('<li />').appendTo(choiceContainer);
                $('<input name="' + l + '" id="' + l + '" type="checkbox" checked="checked" />').appendTo(li);
                $('<label>', {
                    text: l,
                    'for': l
                }).appendTo(li);
            });
        }
        function updateLegendColours() {
            $('.legendColorBox > div').each(function (i) {
                $(this).clone().prependTo(choiceContainer.find("li").eq(i));
            });
        }
        function plotAccordingToChoices() {
            var data = [];
            choiceContainer.find("input:checked").each(function () {
                var key = this.name, i;
                for (i = 0; i < results.length; i++) {
                    if (results[i].label === key) {
                        data.push(results[i]);
                        return true;
                    }
                }
            });
            $.plot($("#chart1"), data, histogram_options);
        }
        function updateDashboardFromSelection() {
            var id = rangeContainer.find("input:checked").attr('id');
            graphlabel = rangeContainer.find("input:checked").attr('graphlabel');
            var text = rangeContainer.find('label[for="'+id+'"]').html();
        
            $('.updateRangeSpan span').html('<small>(' + text + ')</small>');
            
            results = graph_data.results[id];
            totals = graph_data.total[id];
            
            updateLegend();
            plotAccordingToChoices();
            updateLegendColours();
            choiceContainer.find("input").change(plotAccordingToChoices);
            $.plot($("#donut"), totals, pie_options);
        }
        return {
            setupCharts: function(data){
                for (var range in data){
                    if (data.hasOwnProperty(range)){
                        var range_data = data[range];
                        
                        graph_data.results[range] = range_data;
                        
                        var totals_data = Array();
                        
                        for (var i=0; i<range_data.length; i++){
                            totals_data.push(
                                {
                                    label : range_data[i].label,
                                    data : range_data[i].total,
                                    color : range_data[i].color
                                }
                            );
                        }
                        graph_data.total[range] = totals_data;
                    }
                }
                // Change those variables if buttonset changes
                rangeContainer.change(updateDashboardFromSelection);
                updateDashboardFromSelection();
                choiceContainer.find("input").change(plotAccordingToChoices);
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
                var previousPoint = null;
                $("#chart1").bind("plothover", function (event, pos, item) {
                    if (item) {
                        if (previousPoint != item.dataIndex) {
                            previousPoint = item.dataIndex;
                            $("#tooltip").remove();
                            var x = item.datapoint[0].toFixed(0),
                                y = item.datapoint[1].toFixed(0);
                            var thisdate = new Date(parseInt(x)-3600000);
                            if(graphlabel == "days"){
                                showTooltip(item.pageX, item.pageY, parseInt(y).toFixed(0) + " alerts on " + thisdate.format("j M"));
                            } else if(graphlabel == "months") {
                                showTooltip(item.pageX, item.pageY, parseInt(y).toFixed(0) + " alerts in " + thisdate.format("F"));
                            } else {
                                showTooltip(item.pageX, item.pageY, parseInt(y).toFixed(0) + " alerts @ " + thisdate.format("j M H") + ":XX");
                            }
                        }
                    }
                    else {
                        $("#tooltip").remove();
                        previousPoint = null;            
                    }
                });
                $('#donut').bind('plothover', function(event, pos, item) {
                    if (item) {
                        var percent = parseFloat(item.series.percent);
                        if ($(this).data('previous-post') != item.seriesIndex) {
                            $(this).data('previous-post', item.seriesIndex);
                        }
                        $("#tooltip").remove();
                        var msg = item.series.label + ": " + item.datapoint[1][0][1] + " alerts (" + percent + "%)"
                        showTooltip(pos.pageX, pos.pageY, msg);
                    } else {
                        $("#tooltip").remove();
                        previousPost = $(this).data('previous-post', -1);
                    }
                });
            }
        }
    }();
    $('#rangeSelector').buttonset();
    $.ajax({
        url : "/overviews.json",
        success: dashboard.setupCharts,
        dataType: "json"
    })
});
