/*! maluroam github.com/graingert/maluroam/ | github.com/graingert/maluroam/raw/master/COPYING */
function DashboardChartsCtrl($scope, $q, $http, $templateCache) {
    "use strict";
    $scope.earliest='Last Year';
    $scope.latest='Today';
    $scope.users = [];
    $scope.loading = false;
    var orderedSet = new function () {
        this.dict = {}
        this.items = 0;
        this.get_color = function(url){
            if(!(url in this.dict)){
                this.items++;
                this.dict[url] = this.items;
            }
            return this.dict[url];
        }
    }()

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
                show: false
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
        $scope.legend = [];
        _.each(data, function(item, i, data){
            item.total = 0;
            item.color = orderedSet.get_color(item.uri);
            item.show = true;
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
        
        $scope.charts = {
            "histogram_options" : histogram_options,
            "data" : data,
            "pie_options" : pie_options,
            "totals" : totals
        }
        
        $scope.plot();
    }
    
    $scope.plot = function () {
        var ch = $scope.charts;
        
        var data = $.plot(
            $("#histogram"),
            JSONSelect.match(":has(:root > .show:expr(x=true))", $scope.charts),
            ch.histogram_options
        ).getData();
        
        console.log(data)
        
        var colors = JSONSelect.match(":has(:root > .uri) > .color", data);
        var color_index = 0;
        
        _.each($scope.charts.data, function (item, i, data) {
            if (item.show == true){
                data[i].csscolor = colors[color_index];
                color_index++;
            }
        })
        $.plot($("#donut"), ch.totals, ch.pie_options);
    }
    
    $scope.fetch = function(){
        $scope.loading = true;
        var params = {
                "earliest" : Date.parse($scope.earliest).toJSON(),
                "latest" : Date.parse($scope.latest).toJSON()
        }
        
        var activity = $http.get('/activity.json',{
            params: params,
            cache: $templateCache,
            transformResponse: function(data,headersGetter){
                return jQuery.parseJSON(data);
            }
        }).success(function(data,status){
            setupCharts(data);
        });
        
        var users = $http.get('/users.json',{
            params: params,
            cache: $templateCache,
            transformResponse: function(data,headersGetter){
                return jQuery.parseJSON(data);
            }
        }).success(function (data,status) {
            $scope.users = data;
        });
        
        $q.all([activity,users]).then(function(){
            $scope.loading = false;
        });
    }
    
    $('#activity-range').find(".earliest, .latest").daterangepicker({
        "onChange" : _.debounce(function () {
            $scope.$broadcast('event:force-model-update');
            $scope.fetch();
        })
    });
    
    $scope.fetch();
}

/*
 * from http://people.iola.dk/olau/flot/examples/interacting.html
 */

$(function(){
    "use strict";
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
    
    $("#histogram").on("plothover", function (event, pos, item) {
        
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

    $('#donut').on('plothover', function(event, pos, item) {
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

});
