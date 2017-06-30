(function($){

    var methods = {

        init: function(){
            methods.destroy.apply( this );
        },

        columnChart: function(options){
            var selector = this.selector;

            $.getJSON( options.url, function( json ) {

                var series = json['series'],
                    categories = json['categories'];

                var barOptions = {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: options.title
                    },
                    xAxis: {
                        categories: categories,
                        crosshair: true
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Count'
                        }
                    },
                    tooltip: {
                        headerFormat: '<b>{point.x}</b><br/>',
                        pointFormat: '{series.name}: {point.y}'
                    },
                    series: series
                };

                $(selector).highcharts(barOptions).removeClass('loader');
            })
        },

        stackedChart: function(options){
            var selector = this.selector;

            $.getJSON( options.url, function( json ) {

                var series = json['series'],
                    categories = json['categories'];

                var barOptions = {
                    chart: {
                        type: 'column'
                    },
                    title: {
                        text: options.title
                    },
                    xAxis: {
                        categories: categories,
                        crosshair: true
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: 'Count'
                        },
                        stackLabels: {
                            enabled: true,
                        }
                    },
                    tooltip: {
                        headerFormat: '<b>{point.x}</b><br/>',
                        pointFormat: '{series.name}: {point.y}<br/>Total: {point.stackTotal}'
                    },
                    plotOptions: {
                        column: {
                            stacking: 'normal'
                        }
                    },
                    series: series
                };
            
                $(selector).highcharts(barOptions).removeClass('loader');
            });

        },

        donut: function(options){
            var selector = this.selector;

            $.getJSON( options.url, function( data ) {
                var pieOptions = {
                    chart: {
                        type: 'pie',
                    },
                    title: {
                        text: options.title
                    },
                    tooltip: {
                        pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                    },
                    plotOptions: {
                        pie: {
                            allowPointSelect: true,
                            innerSize: '50%',
                            center: ['50%', '50%'],
                            cursor: 'pointer',
                            dataLabels: {
                                enabled: false,
                                format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                            },
                            showInLegend: true
                        }
                    },
                    legend: {
                        align: 'right',
                        layout: 'vertical',
                        verticalAlign: 'middle',
                        itemStyle: {
                            fontSize: '16px',
                            fontWeight: 'normal'

                        },
                        labelFormatter: function() {
                            return '<div style="text-align: left; width:130px;float:left;">' + this.name 
                                + '</div><div style="width:40px; float:left;text-align:right;">: ' + this.y + '</div>';
                        }

                    },
                    series: [{
                        data: data
                    }]
                };

                $(selector).highcharts(pieOptions).removeClass('loader');              
            })
        },

        destroy: function(){
            // have to loop as otherwise only destroys one
            $(this.selector).each(function(i, obj) {
                var $this = $(this);
                if ($this.highcharts() !== undefined){
                    $this.highcharts().destroy();
                }
                // show loader
                $this.addClass('loader');
            });
        }
        
    };

    $.fn.mycharts = function(methodOrOptions) {
        if ( methods[methodOrOptions] ) {
            return methods[ methodOrOptions ].apply( this, Array.prototype.slice.call( arguments, 1 ));
        } else if ( typeof methodOrOptions === 'object' || ! methodOrOptions ) {
            // Default to "init"
            return methods.init.apply( this, arguments );
        } else {
            $.error( 'Method ' +  methodOrOptions + ' does not exist on jQuery.mycharts' );
        }    
    };

})(jQuery);