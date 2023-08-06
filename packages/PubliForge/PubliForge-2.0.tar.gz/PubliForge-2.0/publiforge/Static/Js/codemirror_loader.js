// $Id: codemirror_loader.js 8f791c7639c1 2015/03/15 15:31:54 Patrick $

/*global jQuery: true */
/*global CodeMirror: true */

var codemirrors = [];

jQuery(document).ready(function($) {
    $(".editor").each(function() {
        if (this.tagName == "TEXTAREA") {
            codemirrors.push(CodeMirror.fromTextArea(this, {
                lineNumbers: true
            }));
        }
    });
});
