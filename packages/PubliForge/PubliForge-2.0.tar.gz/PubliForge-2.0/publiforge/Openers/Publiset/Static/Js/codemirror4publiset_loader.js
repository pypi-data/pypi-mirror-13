// $Id: codemirror4publiset_loader.js 8f791c7639c1 2015/03/15 15:31:54 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */
/*global CodeMirror: true */
/*global schema2tags: true */
/*global completeAfter: true */
/*global completeIfAfterLt: true */
/*global completeIfInTag: true */
/*global protectAndAutoCheck: true */

"use strict";

var tags = schema2tags(
    jQuery.publiset.schema, [
        "division", "file",
        "!--", "keyword", "subject"
    ]);
var codemirrors = [];

jQuery(document).ready(function($) {
    protectAndAutoCheck($("#content").children("[data-autocheck]"));
    $(".editor").each(function() {
        if (this.tagName == "TEXTAREA") {
            codemirrors.push(CodeMirror.fromTextArea(this, {
                lineNumbers: true,
                mode: "xml",
                extraKeys: {
                    "'<'": completeAfter,
                    "'/'": completeIfAfterLt,
                    "' '": completeIfInTag,
                    "'='": completeIfInTag,
                    "Alt-Enter": function(cm) {
                        CodeMirror.showHint(
                            cm, CodeMirror.xmlHint, {schemaInfo: tags});
                    }
                }
            }));
        }
    });
});
