(function ($) {
    var siteScripts = {
        /*
         * function onReady
         */
        onReady: function () {
            this.slideNav();
        },

        slideNav: function () {
            $('.has-sub-nav').on('click', function(e){
                e.preventDefault();
                $(this).toggleClass('selected');
                $(this).siblings('.sub-nav').slideToggle(300);
            })
        }
    };


    $().ready(function () {
        siteScripts.onReady();
    });

})(jQuery);