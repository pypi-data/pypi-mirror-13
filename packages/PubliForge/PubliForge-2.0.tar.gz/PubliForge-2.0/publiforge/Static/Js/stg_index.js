// $Id: stg_index.js 426fef1184df 2015/09/06 15:14:26 Patrick $

/*global jQuery: true */
/*global setTimeout: true */

"use strict";

jQuery(document).ready(function($) {
    // Possibly, stop meta refresh
    var refresh = $("#refresh").data("refresh");
    var queryString = window.location.search;
    if (refresh && queryString.indexOf("ajax") == -1) {
        setTimeout(function() {
            window.location = queryString ? queryString + "&ajax" : "?ajax";
        }, 1000);
        return;
    }

    // Request for progress
    if (refresh) {
        (function request() {
            $.ajax({
                url: window.location.pathname,
                dataType: "json",
                success: function(data) {
                    if (!data.working) {
                        window.location = window.location.pathname;
                        return;
                    }
                    $("img.wait").each(function() {
                        var $this = $(this);
                        var path = $this.attr("src").substring(
                            0, $this.attr("src").indexOf("Images/") + 7);
                        if (data.status[$this.attr("id")] == "run")
                            $this.attr("src", path + "wait_synchro.gif");
                        else
                            $this.attr("src", path + "action_synchronize_one.png");
                    });
                    refresh = data.refresh;
                },
                complete: function() {
                    setTimeout(request, 1000 * refresh);
                }
            });
        })();
    }
});
