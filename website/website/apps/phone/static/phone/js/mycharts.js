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