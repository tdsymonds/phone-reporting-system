(function ($) {
    var siteScripts = {
        /*
         * function onReady
         */
        onReady: function() {
            this.toggleMenu();
            this.datePicker();
            this.fastSelect();
        },

        toggleMenu: function(){
            $("#menu-toggle").click(function(e) {
                e.preventDefault();
                $(".content-wrapper").toggleClass("toggled");
            });
        },

        datePicker: function(){
            if ($('.datepicker').length){
                $('.datepicker').daterangepicker({
                    "ranges": {
                        'Today': [moment(), moment()],
                        'Yesterday': [moment().subtract(1, 'days'), moment().subtract(1, 'days')],
                        'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                        'Last 30 Days': [moment().subtract(29, 'days'), moment()],
                        'This Month': [moment().startOf('month'), moment().endOf('month')],
                        'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
                    },
                    "locale": {
                        "format": "DD/MM/YYYY",
                        "separator": " - ",
                    },
                    "startDate": moment().subtract(14, 'days'),
                    "endDate": moment()
                });
            }
        },

        fastSelect: function(){
            if ($('.multipleSelect').length){
                $('.multipleSelect').fastselect({
                    placeholder: 'Add filters',
                    searchPlaceholder: 'Search filters'
                });
            }
        }
    };


    $().ready(function () {
        siteScripts.onReady();
    });

})(jQuery);