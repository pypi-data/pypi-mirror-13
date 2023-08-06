// $Id: prc_edit.js 48397bb0c3a4 2015/04/06 21:13:16 Patrick $

/*global jQuery: true */

"use strict";

jQuery(document).ready(function($) {
    $('div.formItemToolTip .toolTip.processor').mouseenter(function() {
        var $icon = $(this);
        $('#toolTipContent').remove();
        $('<div id="toolTipContent">...</div>')
            .hide()
            .insertAfter($icon)
            .load('?'+$icon.attr('name')+'.x=10&processor_id='+$('#processor_id').val(), function() {
                var $toolTip = $(this);
                if ($toolTip.text().length)
                    $toolTip.show().offset({
                        left: $icon.parent().offset().left,
                        top: $icon.offset().top - $toolTip.outerHeight()
                    });
            });
    });
});
