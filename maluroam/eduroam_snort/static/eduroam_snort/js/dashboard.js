/*! maluroam github.com/graingert/maluroam/ | github.com/graingert/maluroam/raw/master/COPYING */
function DashboardChartsCtrl($scope, $http, $templateCache) {
    "use strict";
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
    
    $scope.fetch = _.debounce(function(){
        $http.get('/activity.json',{
            params: {
                "earliest" : Date.parse($scope.earliest).toJSON(),
                "latest" : Date.parse($scope.latest).toJSON()
            },
            cache: $templateCache,
            transformResponse: function(data,headersGetter){
                return jQuery.parseJSON(data);
            }
        }).success(function(data,status){
            setupCharts(data);
        });
    }, 300);
    $scope.fetch();
}

$(function(){
    "use strict";
    $('#activity-range').livequery(
        function(){
            var form = $(this);
            form.find(".earliest, .latest").daterangepicker({
                "onChange" : function () {
                    form.find(".comms").change();
                }
            });
        },
        function(){
            
        }
    );
});
    