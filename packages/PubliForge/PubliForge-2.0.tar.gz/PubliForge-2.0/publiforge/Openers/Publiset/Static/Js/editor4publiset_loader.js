// $Id: editor4publiset_loader.js 6c0205d1c1d7 2015/06/10 16:19:09 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */

"use strict";


jQuery(document).ready(function($) {
    $.editor4xml.defaults.schema = $.publiset.schema;
    $.editor4xml.defaults.element2html = $.publiset.e4x.element2html;
    $.editor4xml.defaults.editPattern = $.publiset.e4x.editPattern;
    $.editor4xml.defaults.keyboard = $.publiset.e4x.keyboard;

    $.editor4xml.metaHideEmptyFields($(".pdocMeta"));
    $.editor4xml.protectAndAutoCheck($("#content").children("[data-autocheck]"));

    $(".editor.cast-composition").editor4xml({
        rootPattern: ".composition",
        buttons: $.editor4xml.defaultButtons.concat([
            $.publiset.e4x.buttonsInline,
            $.publiset.e4x.buttonsHead,
            $.publiset.e4x.buttonsCompositionDivision
        ]),
        surfaceEditable: false,
        surfaceInitialize: $.publiset.e4x.surfaceInitialize
    });

    $(".editor.cast-selection").editor4xml({
        rootPattern: ".selection",
        buttons: $.editor4xml.defaultButtons.concat([
            $.publiset.e4x.buttonsInline,
            $.publiset.e4x.buttonsHead,
            $.publiset.e4x.buttonsSelectionDivision
        ]),
        surfaceEditable: false,
        surfaceInitialize: $.publiset.e4x.surfaceInitialize
    });
});
