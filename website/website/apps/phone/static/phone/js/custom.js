(function ($) {
    var siteScripts = {
        /*
         * function onReady
         */
        onReady: function() {
            this.toggleMenu();
            this.navToggled();
            this.scrollToTop();
            this.datePicker();
            this.fastSelect();
        },

        toggleMenu: function(){
            $('#menu-toggle').on('click', function(e){
                e.preventDefault();
                $(".content-wrapper").toggleClass("toggled");
            });

            // need to resize charts when css transition completes
            $('#sidebar-wrapper').on('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend', function(){
                $('.chart').each(function() { 
                    if ($(this).highcharts()){
                        $(this).highcharts().reflow(); 
                    }
                });
            });
        },

        navToggled: function(){
            var ww = document.body.clientWidth;
            if (ww < 1000){
                $('.content-wrapper').addClass('toggled');
            };
        },

        scrollToTop: function () {
            $(window).scroll(function() {
                if ($(this).scrollTop() >= 50) {        // If page is scrolled more than 50px
                    $('#return-to-top').fadeIn(200);    // Fade in the arrow
                } else {
                    $('#return-to-top').fadeOut(200);   // Else fade out the arrow
                }
            });
            $('#return-to-top').click(function() {      // When arrow is clicked
                $('body,html').animate({
                    scrollTop : 0                       // Scroll to top of body
                }, 500);
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