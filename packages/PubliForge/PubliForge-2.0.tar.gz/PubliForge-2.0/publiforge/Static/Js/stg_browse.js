// $Id: stg_browse.js d3444980e5e2 2015/07/23 17:02:22 Patrick $

/*global jQuery: true */
/*global setTimeout: true */
/*global FormData: true */

"use strict";

jQuery(document).ready(function($) {
    // ------------------------------------------------------------------------
    // Description
    // ------------------------------------------------------------------------

    var $descriptionContent = $('#browseDescriptionContent').hide();
    $('<a href="#" class="toggle"><img src="/Static/Images/open_false.png" alt="toggle"/></a>')
        .prependTo($('#browseDescription').show())
        .click(function() {
            var $imageToggle = $(this).children('img');
            if ($descriptionContent.is(':visible')) {
                $descriptionContent.slideUp(function() {
                    $imageToggle.attr('src', '/Static/Images/open_false.png');
                    $.updateContentHeight();
               });
            } else {
                $.updateContentHeight(-$descriptionContent.outerHeight());
                $descriptionContent.slideDown(function() {
                    $imageToggle.attr('src', '/Static/Images/open_true.png');
                });
            }
            return false;
        });
    $.updateContentHeight();

    // ------------------------------------------------------------------------
    // Actions
    // ------------------------------------------------------------------------

    $("input[name='ccl!']").click(function(event) {
        $("#actionParams").slideUp("slow", function() {
            $("#actionParams").remove();
        });
        return false;
    });

    $(".actionParamsDirRen, .actionParamsDirDel, .actionParamsFilRen,"
      + " .actionParamsFilDel, .actionParamsFilUpl").click(function(event) {
          $("#actionPgarams").remove();
          var $parent = $(this).parent();
          var $actionParams = $("#" + $(this).attr("class")).clone();
          var name = $actionParams.children(".button").attr("name")
                  .substring(0, 4) + $parent.data("id") + ".x";
          $actionParams
              .attr("id", "actionParams")
              .children(".button").attr("name", name)
              .end().find("input[type='text'], input[type='file']")
              .attr("name", function(idx, attr) { return attr.substring(7); })
              .end().find("input[name='new_name']")
              .attr("value", $parent.data("id"))
              .end().find("input[name='ccl!']")
              .click(function(event) {
                  $("#actionParams").slideUp("slow", function() {
                      $("#actionParams").remove();
                  });
                  return false;
              })
              .end()
              .insertAfter($parent)
              .hide().slideDown("slow")
              .parents("tr").attr("id", "current");
          return false;
      });

    // ------------------------------------------------------------------------
    // Drag and drop
    // ------------------------------------------------------------------------

    $(".container").unbind("drop").on("drop", function(event) {
        event.stopPropagation();
        event.preventDefault();
        $(this).css("background-color", "transparent");
        var path = event.originalEvent.dataTransfer.getData("text");
        if (path.search(/https?:\/\//) == 0)
            return false;

        var files = event.originalEvent.dataTransfer.files;
        if (files.length) {
            var formData = new FormData($("form").get(0));
            var found = false;
            formData.append("upl!.x", "1");
            for (var i = 0; i < files.length; i++) {
                if (files[i].size > 0) {
                    formData.append("upload_file" + i, files[i]);
                    found = true;
                }
            }
            if (!found) return false;
            var $sync = $("[name='syn!']");
            $sync.attr("src", $sync.attr("src")
                       .replace("action_synchronize.png", "wait_synchro.gif"));
            $.ajax({
                type: "POST",
                contentType: false,
                processData: false,
                cache: false,
                data: formData,
                success: function() {
                    window.location = window.location.pathname;
                }
            });
            return false;
        }

        var qs = window.location.search;
        var url = (qs ? qs + "&" : "?") + "get!"
                + ($(this).data("target") || '') + ".x&~" + path;
        $.getJSON(url, function() {
            window.location = window.location.pathname;
        });
        return false;
    });


});
