// $Id: editor4xml.js c06039273077 2015/11/20 14:56:55 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */
/*global setTimeout: true */
/*global setInterval: true */
/*global clearTimeout: true */
/*global XMLSerializer: true */
/*global codemirrors: true */

// ============================================================================
// Button structure:
//    op        : "source" , "parent", "edit", "clean", "delete", "toolbar",
//                "symbol", "tag", "action" or "separator"
//    label     : optional
//    tooltip   : optional
//    class     : optional, by default e4xElt-<element>
//    entries   : if op is "menu"
//    symbol    : if op is "symbol"
//    pattern   : if op is "tag" or "action"
//    xml       : if op is "tag" or "action"
//    insert    : if op is "tag" or "action"
//                null (wrap), "here", "sibling", "wrap-sibling", "first",
//                "last", "allover"
//    attribute : if op is "tag"
//    action    : if op is "action"
// ============================================================================

"use strict";

(function($) {


// ****************************************************************************
//                                 NAMESPACE LIBRARY
// ****************************************************************************

$.editor4xml = {};

// ----------------------------------------------------------------------------
// Default values
$.editor4xml.defaultButtons = [
    [
        { op: "source", tooltip: "Source", class: "e4xButtonSource" }
    ],
    [
        { op: "parent", tooltip: "Parent selection", class: "e4xButtonParent" },
        { op: "edit", tooltip: "Element editing", class: "e4xButtonEdit" },
        { op: "clean", tooltip: "Tag removal", class: "e4xButtonClean" },
        { op: "delete", tooltip: "Element deletion", class: "e4xButtonDelete" },
        // { op: "paste", tooltip: "Paste", class: "e4xButtonPaste" },
        { op: "pasteText", tooltip:"Paste as text", class:"e4xButtonPasteText"},
        { op: "pasteHtml", tooltip:"Paste from HTML", class:"e4xButtonPasteHtml"}
    ]
];

$.editor4xml.defaults = {
    schema: { root: {} },
    rootPattern: "root",
    buttons: $.editor4xml.defaultButtons,
    surfaceEditable: true,
    element2html: {},
    editPattern: {},
    keyboard: { 13: [] },
    clipboard2xml: {}
};

// ----------------------------------------------------------------------------
// Hide empty fields in metadata table.
$.editor4xml.metaHideEmptyFields = function($metaTable) {
    // Hide empty fields
    var fields = [];
    $metaTable.find("input[type='text'], input[type='checkbox'], textarea, select")
        .each(function() {
            var $this = $(this);
            if ((!$.trim($this.val())
                 || ($this.attr('type') == 'checkbox' && !$this.prop('checked')))
                && !$this.next(".error").length) {
                var $tr = $this.parents("tr");
                fields.push([$tr.prevAll("tr").length, $tr.children("th").text()]);
                $tr.hide();
            }
        });
    if (!(fields.length))
        return;

    // Hide and connect
    var $newTag = "<option/>";
    for (var i = 0 ; i < fields.length ; i++)
        $newTag += "<option value='" + fields[i][0] + "'>"
        + fields[i][1] + "</option>";
    $newTag = $(
        "<tr><td colspan='3'><select>"+$newTag+"</select></td></tr>");
    $newTag.find("select").change(function() {
        var $select = $(this);
        $metaTable.find("tr").eq($select.val()).show()
            .find("input").eq(0).focus();
        $select.children("option[value='"+ $select.val() + "']").remove();
        if ($select.children("option").length < 2)
            $select.parents("tr").remove();
        else
            $select.val('');
    });
    $metaTable.append($newTag);
};

// ----------------------------------------------------------------------------
// Protection and periodic checking and saving
$.editor4xml.protectAndAutoCheck = function($editing, exceptClass) {
    // Protect
    $("body").on("click", "a", function(event) {
        var $this = $(this);
        if (!$this.hasClass("e4xButton") && !$this.hasClass(exceptClass)
            && !confirm($.editor4xml.translate(
            "Do you really want to quit the editor?"))) {
            event.preventDefault();
        }
    });

    // Read checking values
    var $form = $("form");
    if (!$form.length || !$editing.length) return;
    var check = $editing.data("autocheck");
    if (!check) return;
    var cycles = parseInt(String(check).split(",")[1] || 0);
    check = parseInt(String(check).split(",")[0] || 0);
    if (!check) return;
    $editing.data("autocycle", cycles);

    // Set auto checking and saving
    setInterval(function() {
        var url, cycle = $editing.data("autocycle") - 1;
        if (cycle <= 0)
            $editing.data("autocycle", cycles);
        else
            $editing.data("autocycle", cycle);
        url = cycles && cycle <= 0 ? "/file/autosave" : "/file/autocheck";
        if (typeof(codemirrors) == 'object')
            for (var i = 0; i < codemirrors.length; i++)
                codemirrors[i].save();
        $.ajax({
            dataType: "json",
            url: $form.attr("action").replace(/\/file\/(write|edit)/, url),
            type: $form.attr("method"),
            data: $form.serialize(),
            success: function(data) {
                if (data && data.error)
                    $form
                    .find("#flash").remove().end()
                    .find("#content").prepend(
                        "<div id='flash' class='alert'><div>"
                            + data.error + "</div></div>")
                    .children("#flash.alert").hide().slideDown('slow')
                    .delay(12000).slideUp('slow');
            }
        });
    }, check * 1000);
};

// ----------------------------------------------------------------------------
// Convert a XML string into a jQuery object.
$.editor4xml.string2xml = function(xml) {
    return $($.parseXML(xml.replace(/ /g, "‧"))).children();
};

// ----------------------------------------------------------------------------
// Convert a XML jQuery object into a string.
$.editor4xml.xml2string = function($xml) {
    return (new XMLSerializer()).serializeToString($xml.get(0))
        .replace(/ xmlns="http:\/\/www.w3.org\/1999\/xhtml"/g, "")
        .replace(/ xmlns="http:\/\/www.w3.org\/1998\/Math\/MathML"/g, "")
        .replace(/ class=""/g, "");
};

// ----------------------------------------------------------------------------
// Convert a XML string or a XML jQuery object into a HTML jQuery object.
$.editor4xml.xml2html = function(xml, opts) {
    function parseXml($node, $tag) {
        switch($node.get(0).nodeType)
        {
        case 1: // Element
            var elt = $node.get(0).nodeName;
            var $newTag;

            if (opts.element2html[elt]
                && typeof(opts.element2html[elt].html) == "function") {
                $newTag = opts.element2html[elt].html($node, $tag, opts);
                if ($newTag)
                    $node.contents().each(function() {
                        parseXml($(this), $newTag);
                    });
            } else {
                var attrs = $node.get(0).attributes;
                $newTag =
                    (opts.element2html[elt]
                     && opts.element2html[elt].html || "div")
                    + ' class="e4xElt-' + elt.replace(":", "__") + '"';
                for (var i = 0 ; i < attrs.length ; i++)
                    $newTag += " data-" + attrs[i].nodeName.replace(":", "__")
                        + '="' + attrs[i].value + '"';
                $newTag = $("<"+ $newTag + "/>");
                $tag.append($newTag);
                $node.contents().each(function() {
                    parseXml($(this), $newTag);
                });
            }
            break;

        case 7: // PI
            if ($node.get(0).nodeName == "hold")
                $tag.append('<span class="e4xHold"/>');
            else
                $tag.append(
                    $('<span class="e4xPI e4xPI-'+ $node.get(0).nodeName
                      + '">' + $node.get(0).data + "</span>"));
            break;

        default: // Text, comment...
            $tag.append($node);
        }
    };

    var $html = $("<div/>");
    var xmlIsString = typeof(xml) == "string";
    if (xmlIsString)
        xml = $.editor4xml.string2xml("<root>" + xml + "</root>");
    parseXml(xml, $html);
    return xmlIsString ? $html.children().contents() : $html.contents();
};

// ----------------------------------------------------------------------------
// Convert a XHTML string into a XML string.
$.editor4xml.html2xml = function(html) {
    function parseHtml($tag, $node) {
        switch($tag.get(0).nodeType)
        {
        case 1:
            var newNode = $tag.attr("class");
            if (!newNode
                || (newNode.indexOf("e4xIgnore") != 0
                    && newNode.indexOf("e4xHold") != 0
                    && newNode.indexOf("e4xPI e4xPI-") != 0
                    && newNode.indexOf("e4xElt-") != 0)) {
                $tag.contents().each(function() {
                    parseHtml($(this), $node);
                });
                break;
            }

            if (newNode.indexOf("e4xIgnore") == 0)
                break;

            if (newNode.indexOf("e4xHold") == 0) {
                if ($tag.parent().children().length == 1
                    && $.trim(!$tag.parent().text())
                    && (!$tag.contents().length
                        || ($tag.contents().length == 1
                            && $tag.children("br").length)))
                    $node.append($('<pi__ id="hold"/>'));
                $tag.contents().each(function() {
                    parseHtml($(this), $node);
                });
                break;
            }

            if (newNode.indexOf("e4xPI e4xPI-") == 0) {
                $node.append($('<pi__ id="' + newNode.substring(12) + '">'
                               + $tag.text() + "</pi__>"));
                break;
            }

            newNode = newNode.substring(7).replace("__", ":");
            if ($.inArray(newNode, ["head", "table", "image", "math"]) != -1)
                newNode += "__";
            var attrs = $tag.get(0).attributes;
            for (var i = 0 ; i < attrs.length ; i++) {
                if (attrs[i].nodeName.indexOf("data-") == 0)
                    newNode += " "
                    + attrs[i].nodeName.substring(5).replace("__", ":")
                    + '="' + attrs[i].value + '"';
            }
            newNode = $("<" + newNode + "/>");
            $node.append(newNode);
            $tag.contents().each(function() {
                parseHtml($(this), newNode);
            });
            break;

        default:
            $node.append($tag);
        }
    };

    var $xml = $.editor4xml.string2xml("<root/>");
    parseHtml($("<div>" + html + "</div>"), $xml);
    return $.editor4xml.xml2string($xml).slice(6, -7)
        .replace(/<(\/?)(head|table|image|math)__/g, "<$1$2")
        .replace(/<pi__ id="([^"]+)" ?\/>/g, "<?$1?>")
        .replace(/<pi__ id="([^"]+)">/g, "<?$1 ").replace(/<\/pi__>/g, "?>")
        .replace(/ xmlns:NS\d=""/g, "").replace(/ NS\d:/g, " ");
};

// ----------------------------------------------------------------------------
// Create tool bar buttons
$.editor4xml.createToolButtons = function($container, buttons, schema) {
    for (var i = 0; i < buttons.length; i++)
    {
        var $group = $('<div class="e4xButtonGroup"/>');
        for (var j = 0; j < buttons[i].length; j++) {
            var button = buttons[i][j];
            if (button.op == "separator") {
                $group.append('<span class="e4xButtonSeparator">|</span>');
                continue;
            }

            var html = '<a href="#" class="e4xButton';
            if (button.class || button.pattern)
                html += (button.class && (" " + button.class))
                || (" e4xButton-" + button.pattern.replace(".", "_"));
            html += '"';

            var tooltip = $.editor4xml.translate(button.tooltip);
            if (!tooltip && button.pattern)
                tooltip = "&lt;"
                + (schema[button.pattern] && schema[button.pattern].element
                   || button.pattern)
                + "&gt;";
            if (tooltip)
                html += ' title="' + tooltip + '"';
            html +=">";
            if (button.symbol)
                html += button.symbol;
            html += "</a>";
            $group.append($(html).data("context", button));
        }
        $container.append($group);
    }
};

// ----------------------------------------------------------------------------
// Show the main tool bar.
$.editor4xml.showMainToolbar = function($toolbar, buttons, schema) {
    // Update buttons
    if (buttons && schema) {
        var $container = $toolbar.children(".e4xButtons");
        $container.empty();
        $.editor4xml.createToolButtons($container, buttons, schema);
    }

    // Show
    $toolbar.show().parent().addClass("e4xFocus");
    var top = Math.max($toolbar.parent().offset().top,
                       $toolbar.parents("#content").offset().top + 1)
            - $toolbar.outerHeight() - 2;
    if (top < window.pageYOffset) top = window.pageYOffset + 2;
    if (top != $toolbar.offset().top)
        $toolbar
        .offset({left: $toolbar.parent().offset().left-20, top: top-20})
        .animate({left: "+=20", top: "+=20"}, "fast");
};

// ----------------------------------------------------------------------------
// Hide the main tool bar.
$.editor4xml.hideMainToolbar = function($toolbar) {
    $toolbar.next(".e4xMenu, .e4xSubToolbar").remove();
    $toolbar.hide().parent().removeClass("e4xFocus");
    window.getSelection().removeAllRanges();
};

// ----------------------------------------------------------------------------
// Open a dialog box.
$.editor4xml.dialogBox = function($editor, title, $body, $node, range) {
    var $main = $editor.parents("#main");
    $editor.children(".e4xDialogBox").remove();
    $editor.children(".e4xDialogBoxMask").remove();

    var $dialogBox = $(
        '<div class="e4xDialogBox">'
            + '<div class="e4xDialogBoxTitle">'
            + '<div class="first">' + title + "</div>"
            + '<div class="last"><a href="#"/></div></div>'
            + '<div class="e4xDialogBoxContent"/></div>');
    $dialogBox.keydown(function(event) {
        switch (event.keyCode)
        {
        case 13:
            event.preventDefault();
            $editor.children(".e4xDialogBox").find(".e4xOk").eq(0).click();
            break;
        case 27:
            event.preventDefault();
            $.editor4xml.boxClose($editor, $node, range);
            break;
        }
    });
    $dialogBox.children(".e4xDialogBoxContent").append($body);
    $.editor4xml.addDragEvents(
        $main, $dialogBox.children(".e4xDialogBoxTitle"));
    $dialogBox.children(".e4xDialogBoxTitle").find("a")
        .click(function(event) {
            event.preventDefault();
            $.editor4xml.boxClose($editor, $node, range);
        });

    $editor.prepend($dialogBox);
    $editor.prepend("<div class='e4xDialogBoxMask'/>");

    var left = $main.offset().left
            + ($main.innerWidth() - $dialogBox.outerWidth()) / 2;
    var top = (window.innerHeight - $dialogBox.outerHeight()) / 3;
    $dialogBox
        .offset({ left: $node.offset().left, top: $node.offset().top })
        .animate({ left: left, top: top })
        .children(".e4xDialogBoxContent").find("select, input").eq(0).focus();
};

// ----------------------------------------------------------------------------
// Add events to drag a box inside a container.
$.editor4xml.addDragEvents = function($container, $titleBar) {
    $titleBar.mousedown(function(event) {
        var $box = $(this).parent();
        var boxWidth = $box.outerWidth();
        var boxHeight = $box.outerHeight();
        var boxOffsetX = event.pageX - $box.offset().left;
        var boxOffsetY = event.pageY - $box.offset().top;
        var cntnrLeft = $container.offset().left;
        var cntnrTop = $container.offset().top;
        var cntnrWidth = $container.innerWidth();
        var cntnrHeight = $container.innerHeight();

        $container
            .mousemove(function(event) {
                var left = event.pageX - boxOffsetX;
                var top = event.pageY - boxOffsetY;
                if (left < cntnrLeft)
                    left = cntnrLeft;
                else if (left + boxWidth > cntnrLeft + cntnrWidth - 4)
                    left = cntnrLeft + cntnrWidth - boxWidth - 4;
                if (top < cntnrTop)
                    top = cntnrTop;
                else if (top + boxHeight > cntnrTop + cntnrHeight)
                    top = cntnrTop + cntnrHeight - boxHeight;
                $box.offset({top: top, left: left});
            })
            .on("mouseup mouseleave", function() {
                $(this).unbind("mousemove mouseup mouseleave");
            });;
    });
};

// ----------------------------------------------------------------------------
// Create a tool bar for a dialog box.
$.editor4xml.boxToolbar = function(buttons) {
    var $buttonGroup = $('<div class="e4xButtonGroup"/>');
    var $button;
    for (var i = 0 ; i < buttons.length ; i++) {
        if (buttons[i].op == "separator") {
            $button = $('<span class="e4xButtonSeparator">|</span>');
        } else {
            $button = $(
                '<a href="#" class="e4xButton ' + buttons[i].class + '"'
                    + ' title="' + $.editor4xml.translate(buttons[i].tooltip)
                    + '"/>');
            if (buttons[i].action)
                $button.click(buttons[i].action);
        }
        $buttonGroup.append($button);
    }

    return $buttonGroup;
};

// ----------------------------------------------------------------------------
// Return a jQuery div tag with fields to edit attributes
$.editor4xml.divAttributes = function(attributes, values) {
    var item, $div = $('<div/>');
    for (var attr in attributes) {
        item = '<span class="e4xAttrName">' + attr + "</span>"
            + " = <span>";
        if (attributes[attr]) {
            item += '<select class="e4xAttrValue" data-id="'
                + attr.replace(":", "__") + '"><option/>';
            for (var value, i = 0 ; i < attributes[attr].length ; i++) {
                value = attributes[attr][i];
                item += "<option";
                if (value == values[attr])
                    item += ' selected="selected"';
                item += ">" + value + "</option>";
            }
            item += "</select>";
        }
        else {
            item += '<input class="e4xAttrValue" type="text" value="'
                + (values[attr] || "") + '" data-id="'
                + attr.replace(":", "__") + '"/>';
        }
        item += "</span>";
        $div.append('<div class="e4xAttribute">' + item + "</div>");
    }
    return $div;
};

// ----------------------------------------------------------------------------
// Return a jQuery div tag with available resources.
$.editor4xml.divResources = function(media, idAttr) {
    var url = window.location.pathname
            .replace(/\/file\/(write|edit)/, "/file/resources/files")
            + "?type=" + media;
    var $html = $(
        '<table class="e4xResources">'
            + '<tr><td class="e4xRsrcDirs"><div/></td>'
            + '<td class="e4xRsrcFiles" rowspan="2"><div/></td></tr>'
            + '<tr><td class="e4xRsrcMedia" rowspan="2"/></tr>'
            + '<tr><td class="e4xRsrcAll"/></tr></table>');
    var $dirs = $html.find(".e4xRsrcDirs").children();
    var $media = $html.find(".e4xRsrcMedia");
    var $files = $html.find(".e4xRsrcFiles").children();
    var $all = $html.find(".e4xRsrcAll");

    // Function to refresh media
    var refreshMedia = function(id) {
        $media.empty();
        if (!id) return;
        $.getJSON(
            url.replace("/resources/files", "/media"), { id: id },
            function(data) {
                switch (media) {
                case "image":
                    $media.append('<img src="'+data.src+'" alt="'+id+'"/>');
                    break;
                case "audio":
                    $media.append('<audio controls="">'
                                  + ' <source src="'+data.src+'"/></audio>');
                    break;
                case "video":
                    $media.append('<video controls="">'
                                  + ' <source src="'+data.src+'"/></video>');
                    break;
                }
            }
        );
    };

    // Function to refresh file list
    var refreshFiles = function(path) {
        $files.empty();
        $.getJSON(
            url,
            { all: $all.children("input").prop("checked"), path: path },
            function (data) {
                $.each(data.files, function(index, value) {
                    $("<div>" + value + "</div>").click(function() {
                        var $file = $(this);
                        var id = $file.text();
                        id = id.substring(0, id.lastIndexOf("."));
                        $file.siblings().removeClass("e4xSelected");
                        $file.addClass("e4xSelected")
                            .parents(".e4xDialogBoxContent")
                            .find("input[data-id="+ idAttr +"]").val(id);
                        refreshMedia(id);
                    }).appendTo($files);
                });
            }
        );
    };

    // Directories
    $.getJSON(
        url.replace('files', 'dirs'),
        function(data) {
            $.each(data.dirs, function(index, value) {
                var item = "<div"+(!index?' class="e4xSelected">':">")
                        + value + "</div>";
                $(item).click(function() {
                    var $dir = $(this);
                    var $resources = $dir.parents(".e4xResources");
                    $dir.siblings().removeClass("e4xSelected");
                    $dir.addClass("e4xSelected");
                    refreshFiles($dir.text());
                }).appendTo($dirs);
            });
            if (data.dirs.length)
                refreshFiles(data.dirs[0]);
            refreshMedia($dirs.parents(".e4xDialogBoxContent")
                         .find("input[data-id='id']").val());
        }
    );

    // All check box
    $all.append('<input type="checkbox"/>'
                + " " + $.editor4xml.translate("All") + "</div>");
    $all.children().click(function() {
        refreshFiles($dirs.find(".e4xSelected").text());
    });

    return $html;
};

// ----------------------------------------------------------------------------
// Add main buttons on dialog box.
$.editor4xml.boxButtons = function($editor, $body, $node, range, onOk) {
    if (!onOk)
        onOk = $.editor4xml.boxUpdateAttrAndClose;

    var $buttons = $('<div class="e4xDialogBoxButtons"/>');
    var $button = $('<a href="#" class="e4xCancel">'
                + $.editor4xml.translate("Cancel")+ "</a>");
    $button.click(function(event) {
        event.preventDefault();
        $.editor4xml.boxClose($editor, $node, range);
    });
    $buttons.append($button);
    $button = $('<a href="#" class="e4xOk">'
                + $.editor4xml.translate("OK")+ "</a>");
    $button.click(function(event) {
        event.preventDefault();
        onOk($editor, $(this).parents(".e4xDialogBoxContent"), $node, range);
    });
    $buttons.append($button);
    $body.append($buttons);
};

// ----------------------------------------------------------------------------
// Update attributes and close dialog box.
$.editor4xml.boxUpdateAttrAndClose = function($editor, $body, $node, range) {
    // Update attributes
    $body.find(".e4xAttrValue").each(function() {
        var $this = $(this);
        var attr = "data-" + $this.data("id");
        var value = $this.val();
        if (value) $node.attr(attr, value);
        else       $node.removeAttr(attr);
    });

    // Close dialog box
    $.editor4xml.boxClose($editor, $node, range);
};

// ----------------------------------------------------------------------------
// Close dialog box.
$.editor4xml.boxClose = function($editor, $node, range) {
    // Close dialog box
    $editor.children(".e4xDialogBox").remove();
    $editor.children(".e4xDialogBoxMask").remove();

    // Update surface
    var $surface = $editor.children(".e4xSurface");
    var selection = window.getSelection();
    var $hold = $node.find(".e4xHold");
    $surface.focus();
    if (range) {
        selection.removeAllRanges();
        selection.addRange(range);
        selection.collapseToEnd();
    } else if ($hold.length) {
        $.editor4xml.setCursor($hold);
    } else if ($node.length) {
        range = document.createRange();
        range.selectNodeContents($node.get(0));
        selection.removeAllRanges();
        selection.addRange(range);
        selection.collapseToEnd();
   }
    $surface.trigger("refresh");
    $.editor4xml.scrollTo($node);
};

// ----------------------------------------------------------------------------
// Create a root tag for complex "XML element to HTML" transformation.
$.editor4xml.htmlRootTag = function($node, tag) {
    var element = $node.get(0).nodeName;
    var rootTag = "<" + tag + ' class="e4xElt-' + element + '"';
    var attrs = $node.get(0).attributes;
    for (var i = 0 ; i < attrs.length ; i++)
        rootTag += " data-" + attrs[i].nodeName + '="' + attrs[i].value + '"';
    rootTag += "/>";
    return $(rootTag);
};

// ----------------------------------------------------------------------------
// Set place holders and set focus where the attribute data-e4x="here" is.
$.editor4xml.setHoldAndFocus = function($tag) {
    $tag.find("[data-e4x='hold']")
        .removeAttr("data-e4x")
        .append('<span class="e4xHold"/>');
    $tag = $tag.find("[data-e4x='here']")
        .removeAttr("data-e4x")
        .append('<span class="e4xHold"/>');
    if (!$tag.length)
        return;

    $tag.focus();
    $.editor4xml.setCursor($tag.children(".e4xHold"));
    $tag.parents(".e4xSurface").trigger("refresh");
};

// ----------------------------------------------------------------------------
// Find the smartest place for the cursor.
$.editor4xml.setCursor = function($here) {
    var range;
    if (!$here || !$here.length) {
        range = $.editor4xml.getRange();
        if (!range) return;
        $here = $($.editor4xml.getNode(range)).find(".e4xHold");
    }
    if (!$here.length)
        return;

    range = document.createRange();
    range.selectNodeContents($here.get(0));
    range.collapse(false);
    window.getSelection().removeAllRanges();
    window.getSelection().addRange(range);
};

// ----------------------------------------------------------------------------
// Scroll to show the $here node.
$.editor4xml.scrollTo = function($here) {
    if (!$here || !$here.length) return;
    var $content = $("#content");
    var scrollTop;
    if ($content.get(0).scrollHeight > $content.get(0).clientHeight) {
        scrollTop = $here.offset().top + $content.scrollTop()
            - $content.offset().top;
        if (scrollTop < $content.scrollTop()
            || $content.scrollTop() + $content.innerHeight() < scrollTop)
            $content.scrollTop(scrollTop - 30);
    } else {
        scrollTop = $here.offset().top;
        if (scrollTop < window.pageYOffset
            || window.pageYOffset + window.innerHeight < scrollTop)
            $(window).scrollTop(scrollTop - 80);
    }
};

// ----------------------------------------------------------------------------
// Return the dictionary of attributes of the given node.
$.editor4xml.getAttributes = function(node) {
    if (!node) return {};

    // Find the first element corresponding to an XML element
    while (!node.className
           || (node.className.indexOf("e4xElt-") != 0
               && node.className.indexOf("e4xSurface") != 0))
        node = node.parentNode;
    if (node.className.indexOf("e4xSurface") == 0)
        return {};

    // Browse  attributes
    var attributes = {};
    for (var attr in node.dataset)
        attributes[attr.replace("__", ":")] = node.dataset[attr];
    return attributes;
};

// ----------------------------------------------------------------------------
// Get current node.
$.editor4xml.getNode = function(range) {
    var node = range.cloneContents().childNodes;

    if ((node.length == 1 && node[0].nodeType == 1)
        || (node.length == 2 && node[0].nodeType == 1
            && node[1].nodeType == 3 && !node[1].length)) {
        node = node[0];
        range.deleteContents();
        range.insertNode(node);
        return node;
    }

    if (node.length == 3
        && node[0].nodeType == 3 && !node[0].length
        && node[1].nodeType == 1
        && node[2].nodeType == 3 && !node[2].length) {
        node = node[1];
        range.deleteContents();
        range.insertNode(node);
        return node;
    }

    return range.commonAncestorContainer;
};

// ----------------------------------------------------------------------------
// Get current range.
$.editor4xml.getRange = function() {
    if (!window.getSelection) // Before IE 9
        return null;
    var selection = window.getSelection();
    if (!selection.rangeCount)
        return null;
    return selection.getRangeAt(0);
};

// ----------------------------------------------------------------------------
// Translation
$.editor4xml.i18n = {};
$.editor4xml.translate = function(message) {
    return $.editor4xml.i18n[message] || message;
};


// ****************************************************************************
//                                    PLUG-IN
// ****************************************************************************

$.fn.editor4xml = function(options) {
    // Update option values
    var opts = $.extend({}, $.editor4xml.defaults, options);

    // Compute element/named patterns dictionary
    var patterns4element = patterns4elementMap(opts.schema);

    // Environment
    var timer = null;
    var env;
    resetEnvironment();


    // ========================================================================
    //                               Plug-in library
    // ========================================================================

    // ------------------------------------------------------------------------
    // Refresh the toolbar state.
    function refreshToolbar($toolbar) {
        resetEnvironment();
        if (!$toolbar.is(":visible"))
            return;
        $toolbar.next(".e4xMenu, .e4xSubToolbar").remove();

        // Update environment
        var range = $.editor4xml.getRange();
        if (!range) return;
        var currentNode = $.editor4xml.getNode(range);
        updateEnvironment(currentNode);

        // Update tag trail
        if (env.elements.length) {
            var attributes = "";
            var attrs = $.editor4xml.getAttributes(currentNode);
            for (var key in attrs)
                attributes += " " + key + '="' + attrs[key] + '"';
            $toolbar.children(".e4xElementTrail").text(
                env.elements.join(" > ") + attributes);
        }
        else $toolbar.children(".e4xElementTrail").empty();

        // Update selection status
        var allow =  env.contents[env.contents.length - 1];
        var allowFull = [];
        for (var i = 0 ; i < env.contents.length ; i++)
            allowFull = allowFull.concat(env.contents[i]);

        // Update button states
        var collapsed = range ? range.collapsed : true;
        $toolbar.find(".e4xButton").each(function() {
            var pattern;
            var $button = $(this);
            var context = $button.data("context");

            switch (context.op)
            {
            case "edit":
                pattern = env.patterns[env.patterns.length-1];
                $button.toggleClass(
                    "e4xButtonDisabled",
                    env.patterns.length < env.elements.length  ||
                        (!opts.editPattern[pattern] &&
                         (!env.patterns.length
                          || !opts.schema[pattern]
                          || !opts.schema[pattern].attributes)));
                break;
            case "clean":
            case "delete":
                $button.toggleClass("e4xButtonDisabled", collapsed);
                break;
            case "symbol":
            case "paste":
            case "pasteText":
            case "pasteHtml":
                $button.toggleClass(
                    "e4xButtonDisabled", !collapsed || !env.canWrite);
                break;
            case "tag":
            case "action":
                pattern = context.pattern;
                $button.toggleClass(
                    "e4xButtonActive", $.inArray(pattern, env.patterns) > -1);
                $button.toggleClass(
                    "e4xButtonDisabled",
                    Boolean(
                        context.insert != "allover" &&
                            ((collapsed && !context.insert)
                             || (!collapsed && context.insert
                                 && context.insert != "wrap-sibling")
                             || ((!context.insert || context.insert == "here")
                                 && $.inArray(pattern, allow) == -1)
                             || (context.insert && context.insert != "here"
                                 && $.inArray(pattern, allowFull) == -1))));
                break;
            }
        });
    }

    // ------------------------------------------------------------------------
    // Keyboard management
    function onKeyDown(event, $toolbar, $surface)
    {
        var range;
        switch(event.keyCode)
        {
        case 8: // Backspace
            if (!env.canWrite) {
                event.preventDefault();
                break;
            }
            var $node = $(env.nodes.slice(-1));
            $node.children("br").remove();
            if ($node.contents().length == 1
                && $node.text().trim().length == 1) {
                $node.html("<span class='e4xHold'/>");
                event.preventDefault();
            }
            break;
        case 13: // Enter
            event.preventDefault();
            range = $.editor4xml.getRange();
            var oldRange = range.cloneRange();
            var context;
            for (var i = 0 ; i < opts.keyboard[13].length ; i++) {
                context = opts.keyboard[13][i];
                if (setInsertionPoint(event, range, context.pattern,
                                      context.insert || "sibling")) {
                    insertTag($surface, context, oldRange, range);
                    break;
                }
            }
            break;
        case 27: // Escape
            if (!$surface.prev(".e4xMenu").remove().length &&
                !$toolbar.next(".e4xSubToolbar").remove().length)
                $surface.blur();
            break;
        case 33: case 34: case 35: case 36: // Moves
        case 37: case 39: case 40:
            break;
        case 38: // Up
            if (event.ctrlKey) {
                event.preventDefault();
                actionSelectParent($.editor4xml.getRange());
            }
            break;
        case 46: // Del
            range = $.editor4xml.getRange();
            if (!range || range.collapsed) {
                if (!env.canWrite)
                    event.preventDefault();
                break;
            }
            event.preventDefault();
            actionDelete(range);
            break;
        default:
            if (!env.canWrite)
                event.preventDefault();
        }
    }

    // ------------------------------------------------------------------------
    // Operation on the current button.
    function onToolButtonClick(event, $toolbar, $button, $surface)
    {
        var context = $button.data("context");
        event.preventDefault();
        $toolbar.next(".e4xMenu, .e4xSubToolbar").remove();
        if ($button.hasClass("e4xButtonDisabled"))
            return;

        var $newTag;
        var range = $.editor4xml.getRange();
        var $editor = $toolbar.parent();
        switch(context.op)
        {
        case "source":
            actionToggleSource($toolbar, $surface, $surface.next());
            break;
        case "parent":
            actionSelectParent(range);
            refreshToolbar($toolbar);
            break;
        case "edit":
            actionEditPattern($editor, range);
            break;
        case "clean":
            actionCleanTags(range);
            refreshToolbar($toolbar);
            break;
        case "delete":
            actionDelete(range);
            refreshToolbar($toolbar);
            break;
        case "pasteText":
            actionPasteAsText($editor, range);
            break;
        case "pasteHtml":
            actionPasteFromHtml(event, $editor, range);
            break;
        case "toolbar":
            actionSubToolbar(event, $toolbar, $button, $surface, context);
            break;
        case "symbol":
            actionSymbol(context, range);
            $editor.children(".e4xMenu, .e4xSubToolbar").remove();
            break;
        case "tag":
            if (context.attribute) {
                actionTagAttribute(event, $surface, $button, context, range);
                break;
            }
            $newTag = actionTag(event, $surface, $button, context, range);
            if ($newTag) {
                $editor.children(".e4xMenu, .e4xSubToolbar").remove();
                editTag($editor, context, $newTag);
                refreshToolbar($editor.children(".e4xToolbar"));
            }
            break;
        case "action":
            updateEnvironment($.editor4xml.getNode(range));
            $newTag = context.action(event, context, range, opts, env);
            if ($newTag) {
                $editor.children(".e4xMenu, .e4xSubToolbar").remove();
                editTag($editor, context, $newTag);
                refreshToolbar($editor.children(".e4xToolbar"));
            }
            break;
        }
    }

    // ------------------------------------------------------------------------
    // Toggle visibility between surface and source.
    function actionToggleSource($toolbar, $surface, $source) {
        if ($source.is(":visible")) {
            $toolbar
                .find(".e4xButtonGroup").show()
                .eq(0).children().removeClass("e4xButtonActive");
            $source.hide();
            $surface.show().focus();
            $.editor4xml.setCursor($surface.find(".e4xHold"));
            refreshToolbar($toolbar);
        } else {
            $toolbar
                .children(".e4xElementTrail").empty()
                .end().find(".e4xButtonGroup").hide()
                .eq(0).show()
                .children().addClass("e4xButtonActive");
            $surface.hide();
            $source.show().focus();
        }
    }

    // ------------------------------------------------------------------------
    // Select the parent element of the current selection.
    function actionSelectParent(range) {
        if (!range) return;
        var node = $.editor4xml.getNode(range);
        if (!node) return;

        while (node.nodeType == 1
               && (!node.className
                   || (node.className.indexOf("e4xElt-") != 0
                       && node.className.indexOf("e4xSurface") != 0)))
            node = node.parentNode;
        if (!node) return;

        node = node.parentNode;

        while (node && (!node.className
                        || (node.className.indexOf("e4xElt-") != 0
                            && node.className.indexOf("e4xSurface") != 0)))
            node = node.parentNode;

        if (!node || node.className.indexOf("e4xSurface") == 0)
            return;

        range.selectNodeContents(node);
        if (node != $.editor4xml.getNode(range))
            range.selectNode(node);

        var selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
    }

    // ------------------------------------------------------------------------
    // Edit pattern (only attributes by default).
    function actionEditPattern($editor, range) {
        // Get current node and pattern
        if (!range) return;
        var node, element, pattern;
        updateEnvironment($.editor4xml.getNode(range));
        if (env.nodes.length == 0 || env.patterns.length == 0)
            return;
        node = env.nodes[env.nodes.length - 1];
        element = env.elements[env.elements.length - 1];
        pattern = env.patterns[env.patterns.length - 1];

        // Special edition
        if (opts.editPattern[pattern]) {
            opts.editPattern[pattern]($editor, pattern, node, opts);
            return;
        }
        if (!opts.schema[pattern] || !opts.schema[pattern].attributes)
            return;

        // Create attribute zone and buttons
        var $node = $(node);
        var $body = $.editor4xml.divAttributes(
            opts.schema[pattern].attributes, $.editor4xml.getAttributes(node));
        $.editor4xml.boxButtons($editor, $body, $node);

        // Open dialog box
        $.editor4xml.dialogBox(
            $editor,
            $.editor4xml.translate("Properties") + " &lt;"+element+"&gt;",
            $body.children(), $node, range);
    }

    // ------------------------------------------------------------------------
    // Remove the tags inside the selection.
    function actionCleanTags(range) {
        if (!range || range.collapsed) return;
        var currentNode = $.editor4xml.getNode(range);
        updateEnvironment(currentNode);

        if (currentNode.childNodes.length
            == range.cloneContents().childNodes.length) {
            if (env.contents.length < 2
                || $.inArray(".text", env.contents[env.contents.length-2])==-1)
                return;
            range.selectNode(currentNode);
        }
        else if (!env.canWrite)
            return;

        var textNode = document.createTextNode(range.toString());
        // if (!window.confirm($.editor4xml.translate("sure?")))
        //     return;
        range.deleteContents();
        range.insertNode(textNode);
        var selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        selection.collapseToEnd();
    }

    // ------------------------------------------------------------------------
    // Delete a piece of DOM.
    function actionDelete(range) {
        if (!range || range.collapsed) return;
        var currentNode = $.editor4xml.getNode(range);
        updateEnvironment(currentNode);

        if (currentNode.childNodes.length
            == range.cloneContents().childNodes.length) {
            if (env.patterns.length == 1 && env.patterns[0].charAt(0) != ".")
                return;
            var $tag = $(currentNode);
            if ($tag.attr("contenteditable") == "true"
                || $tag.find("[contenteditable='true']").length)
                return;
            if ((env.contents.length < 2
                 || $.inArray(".text", env.contents[env.contents.length-2])==-1)
                && !window.confirm($.editor4xml.translate("sure?")))
                return;
            range.selectNode(currentNode);
            range.deleteContents();
        }
        else if (env.canWrite) {
            range.deleteContents();
        }
    }

    // ------------------------------------------------------------------------
    // Copy content of clipboard as a text.
    function actionPasteAsText($editor, range) {
        var onOk = function($editor, $body, $node, range) {
            var $clipboard = $body.find(".e4xClipboard");
            $clipboard.find("style").remove();
            range.insertNode(document.createTextNode(
                $clipboard.text().replace(/ /g, "‧").replace(/\s+/g, " ")));
            $.editor4xml.boxUpdateAttrAndClose($editor, $body, $node, range);
        };
        dialogBoxPaste($editor, range, "Paste as text", onOk);
    }

    // ------------------------------------------------------------------------
    // Copy content of clipboard from a HTML source.
    function actionPasteFromHtml(event, $editor, range) {
        var onOk = function($editor, $body, $node, range) {
            var $clipboard = $body.find(".e4xClipboard");
            $clipboard.find("style").remove()
                .end().find("*").removeAttr("style class align");
            $clipboard = $($.editor4xml.xml2string($clipboard)
                           .replace(/ /g, "‧").replace(/\s+/g, " "));
            for (var tag in opts.clipboard2xml) {
                $clipboard.find(tag)
                    .addClass("e4xElt-" + opts.clipboard2xml[tag]);
            }

            var nodes;
            if ($clipboard.children().length == 0) {
                range.insertNode(document.createTextNode($clipboard.text()));
            } else if ($clipboard.children().length == 1) {
                nodes = $clipboard.children().contents().get();
                $.each(nodes.reverse(), function(index, node) {
                    range.insertNode(node);
                });
            } else {
                updateEnvironment($.editor4xml.getNode(range));
                nodes = $clipboard.contents().get();
                $.each(nodes.reverse(), function(index, chunk) {
                    var $chunk = $(chunk);
                    if ($chunk.text().trim()) {
                        var element = $chunk.attr("class");
                        if (!element || element.indexOf("e4xElt-") != 0)
                            range.insertNode(chunk);
                        else if (setInsertionPoint(event, range,
                                                   element.substring(7), "sibling"))
                            range.insertNode(chunk);
                    }
                });
            }
            $.editor4xml.boxUpdateAttrAndClose($editor, $body, $node, range);
        };
        dialogBoxPaste($editor, range, "Paste from a HTML source", onOk);
    }

    // ------------------------------------------------------------------------
    // Copy content of clipboard according to `convertClipboard()` function.
    function dialogBoxPaste($editor, range, title, onOk) {
        if (!range.collapsed || !env.canWrite)
            return;
        var $node = $(env.nodes[env.nodes.length - 1]);
        var $clipboard = $(
            '<div class="e4xClipboard" contenteditable="true"/>');
        var $body = $(
            '<div><div class="e4xClipboardWarning">' + $.editor4xml.translate(
                "For security reasons, paste here.") + '</div></div>');
        $body.append($clipboard);
        $.editor4xml.boxButtons($editor, $body, $node, range, onOk);
        $.editor4xml.dialogBox(
            $editor, $.editor4xml.translate(title), $body, $node, range);
        $.editor4xml.setCursor($clipboard);
    }

    // ------------------------------------------------------------------------
    // Open a sub tool bar to choose an action.
    function actionSubToolbar(event, $toolbar, $button, $surface, context) {
        // Create tool bar
        var $subtoolbar = $("<div/>");
        $.editor4xml.createToolButtons(
            $subtoolbar, context.entries, opts.schema);
        $subtoolbar.attr("unselectable", "on")
            .addClass("e4xSubToolbar")
            .on("selectstart mousedown", false)
            .find(".e4xButton").click(function() {
                onToolButtonClick(event, $subtoolbar, $(this), $surface);
            });

        // Set tool bar
        $subtoolbar.insertAfter($toolbar)
            .offset({
                left: $button.offset().left - $subtoolbar.outerWidth()/2 + 24,
                top: $button.offset().top + $button.outerHeight() + 2
            });
        refreshToolbar($subtoolbar);
    }

    // ------------------------------------------------------------------------
    // Insert a symbol.
    function actionSymbol(context, range) {
        if (!range.collapsed || !env.canWrite || !context.symbol)
            return;
        var textNode = document.createTextNode(
            context.symbol.replace(/ /g, "‧"));
        range.insertNode(textNode);
        window.getSelection().collapseToEnd();
    }

    // ------------------------------------------------------------------------
    // Process action for a simple tag operation.
    function actionTag(event, $surface, $button, context, range, attributes) {
        if (!context.pattern || !range
            || (range.collapsed && !context.insert)
            || (!range.collapsed && context.insert
                && context.insert != "wrap-sibling")) {
            window.getSelection().collapseToEnd();
            return null;
        }
        updateEnvironment($.editor4xml.getNode(range));

        // Set the insertion point
        var oldRange = range.cloneRange();
        if (!setInsertionPoint(event, range, context.pattern, context.insert))
            return null;

        // Create a new tag with attributes
        return insertTag($surface, context, oldRange, range, attributes);
    }

    // ------------------------------------------------------------------------
    // Open a drop down menu to choose the value of an attribute.
    function actionTagAttribute(event, $surface, $button, context, range) {
        // Create menu
        var schema = opts.schema[context.pattern];
        var $menu = $(
            '<div class="e4xMenu" unselectable="on">'
                + '<div class="e4xMenuKey">' + context.attribute + "</div>"
                + '<div class="e4xMenuValues"></div></div>');
        $menu.on("selectstart mousedown", false);
        var $values = $menu.children(".e4xMenuValues");
        for (var i = 0; i < schema.attributes[context.attribute].length; i++) {
            var $entry = $('<a href="#">'
                           + schema.attributes[context.attribute][i] + "</a> ");
            $entry.click(function() {
                var attributes = {};
                attributes[context.attribute] = $(this).text();
                actionTag(event, $surface, $button, context, range, attributes);
                $menu.remove();
            });
            $values.append($entry);
        }

        // Set menu
        $menu.insertBefore($surface)
            .offset({
                left: $button.offset().left,
                top: $button.offset().top + $button.outerHeight()
            });
    }

    // ------------------------------------------------------------------------
    // Insert tag with attributes around selection.
    function insertTag($surface, context, oldRange, range, attributes) {
        // Create a new tag
        var $html;
        var xml = context.xml || (opts.schema[context.pattern] &&
                                  opts.schema[context.pattern].seed);
        if (xml) {
            $html = $.editor4xml.xml2html(xml, opts);
        } else {
            xml = opts.schema[context.pattern] &&
                opts.schema[context.pattern].element || context.pattern;
            for (var attr in attributes)
                xml += " " + attr + '="' + attributes[attr] + '"';
            $html = $.editor4xml.xml2html("<"+xml+' e4x="here"/>', opts);
        }

        // Manage "hold" and "here"
        $html.find("[data-e4x='hold']").addBack("[data-e4x='hold']")
            .append('<span class="e4xHold"/>')
            .removeAttr("data-e4x");
        if (oldRange.collapsed && range.collapsed)
            $html.find("[data-e4x='here']").addBack("[data-e4x='here']")
            .append('<span class="e4xHold"/>');
        else
            $html.find("[data-e4x='here']").addBack("[data-e4x='here']")
            .append($("<div/>").append(oldRange.extractContents()).contents());

        // Insert the new tag
        range.insertNode($html.get(0));
        var $here = $surface.find("[data-e4x='here']").removeAttr("data-e4x");
        if ($here.length)
            range.selectNodeContents($here.get(0));
        range.collapse(false);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        $.editor4xml.scrollTo($here);

        return $html;
    };

    // ------------------------------------------------------------------------
    // Edit a newly inserted tag.
    function editTag($editor, context, $tag) {
        if (context.delayedition)
            return;
        if (!$tag || $tag.find(".e4xEdit").click().length)
            return;
        if (opts.editPattern[context.pattern])
            opts.editPattern[context.pattern](
                $editor, context.pattern, $tag.get(0), opts);
        else if (!context.attribute && !context.xml
                 && opts.schema[context.pattern].attributes)
            actionEditPattern($editor, $.editor4xml.getRange());
    }

    // ------------------------------------------------------------------------
    // Find the right place for insertion.
    function setInsertionPoint(event, range, pattern, insertMode) {
        if (!env.contents.length)
            return false;

        if (!insertMode || insertMode == "here" || !env.nodes.length) {
            if ($.inArray(pattern, env.contents[env.contents.length-1]) == -1)
                return false;
            if (insertMode == "here")
                range.collapse(false);
            return true;
        }

        var i = env.contents.length - 1;
        while (i >= 0 && $.inArray(pattern, env.contents[i]) == -1) i--;
        if (i < 0) return false;
        if (i > 0 && event.shiftKey) {
            var j = i - 1;
            while (j >= 0 && $.inArray(pattern, env.contents[j]) == -1) j--;
            if (j >= 0) i = j;
        }
        if (env.nodes.length < env.contents.length) i--;

        switch(insertMode)
        {
        case "first":
            if (i < 0) {
                range.setStartBefore(env.nodes[i + 1]);
                range.setEndBefore(env.nodes[i + 1]);
            } else {
                range.setStart(env.nodes[i], 0);
                range.setEnd(env.nodes[i], 0);
            }
            break;
        case "last":
            if (i < 0) {
                range.setStartAfter(env.nodes[i + 1]);
                range.setEndAfter(env.nodes[i + 1]);
            } else {
                range.setStart(env.nodes[i], env.nodes[i].childNodes.length);
                range.setEnd(env.nodes[i], env.nodes[i].childNodes.length);
            }
            break;
        case "wrap-sibling":
        case "sibling":
            if (i == env.nodes.length - 1) {
                if (event.ctrlKey) {
                    range.setStart(env.nodes[i], 0);
                    range.setEnd(env.nodes[i], 0);
                 } else {
                     range.setStart(
                         env.nodes[i], env.nodes[i].childNodes.length);
                     range.setEnd(env.nodes[i], env.nodes[i].childNodes.length);
                 }
            } else {
                if (event.ctrlKey) {
                    range.setStartBefore(env.nodes[i + 1]);
                    range.setEndBefore(env.nodes[i + 1]);
                } else {
                    range.setStartAfter(env.nodes[i + 1]);
                    range.setEndAfter(env.nodes[i + 1]);
                }
            }
            break;
        default:
            return false;
        }

        return true;
    }

    // ------------------------------------------------------------------------
    // Clean the environment structure
    function resetEnvironment() {
        env = {
            nodes: [],
            elements: [],
            patterns: [],
            contents: [],
            canWrite: false
        };
    }

    // ------------------------------------------------------------------------
    // Update the environment structure
    function updateEnvironment(node) {
        resetEnvironment();
        if (!node) return;

        // Find the first element corresponding to an XML element
        while (node && (!node.className
                        || (node.className.indexOf("e4xElt-") != 0
                            && node.className.indexOf("e4xSurface") != 0)))
            node = node.parentNode;

        // Browse  ancestors elements
        while (node &&
               (!node.className || node.className.indexOf("e4xSurface"))!=0) {
            if (node.className && node.className.indexOf("e4xElt-") == 0) {
                env.nodes.unshift(node);
                env.elements.unshift(
                    node.className.substring(7).replace('__', ':'));
            }
            node = node.parentNode;
        }

        // Find root container
        var content = opts.rootPattern.charAt(0) == "."
                ? opts.schema[opts.rootPattern]
                  && opts.schema[opts.rootPattern].content
                : [[opts.rootPattern]];
        if (!content) return;

        // Element path
        var i, j, pattern;
        env.patterns =
            opts.rootPattern.charAt(0) == "." ? [opts.rootPattern]: [];
        for (i = 0 ; i < env.elements.length ; i++) {
            if (!patterns4element[env.elements[i]]) {
                env.patterns.push(env.elements[i]);
                env.contents.push([]);
                return;
            }
            for (j = 0 ; j < content.length ; j++) {
                pattern = arrayIntersection(
                    content[j], patterns4element[env.elements[i]]);
                if (pattern.length != 1)
                    continue;
                pattern = pattern[0];
                env.patterns.push(pattern);
                env.contents.push(content[j]);
                content =
                    opts.schema[pattern] && opts.schema[pattern].content || [];
                break;
            }
            if (!pattern.length)
                break;
        }

        // Find last level content
        if (env.patterns.length) {
            if (opts.rootPattern.charAt(0) != ".")
                env.contents.shift();
            var lastContent = [];
            for (i = 0 ; i < content.length ; i++)
                for (j = 0 ; j < content[i].length ; j++)
                    if ($.inArray(content[i][j], lastContent) == -1)
                        lastContent.push(content[i][j]);
            env.contents.push(lastContent);
        }

        // Ability to write text
        env.canWrite = $.inArray(
            ".text", env.contents[env.contents.length - 1]) != -1;
    }

    // ------------------------------------------------------------------------
    // Dictionary of correspondences between element and named patterns.
    function patterns4elementMap(schema) {
        var element, elements = {};
        for (var pattern in schema) {
            element = schema[pattern].element || pattern;
            if (elements[element])
                elements[element].push(pattern);
            else
                elements[element] = [pattern];
        }
        return elements;
    }

    // ------------------------------------------------------------------------
    // Compute the intersection between 2 arrays.
    function arrayIntersection(array1, array2) {
        return $.grep(array1, function(i) {
            return $.inArray(i, array2) > -1;
        });
    }


    // ========================================================================
    //                            Plug-in main function
    // ========================================================================

    return this.each(function() {
        if (this.tagName != "TEXTAREA" && this.tagName != "INPUT")
            return;

        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        //                          Structure creation
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        // --------------------------------------------------------------------
        var $e4xSource = $(this);
        $e4xSource.addClass("e4xSource").hide();
        $e4xSource.val($e4xSource.val().replace(/ /g, "‧"));

        // --------------------------------------------------------------------
        $e4xSource.wrap(
            '<div class="e4x e4xCast-' + $e4xSource.data("cast") + '"/>');
        var $e4x = $e4xSource.parent();

        // --------------------------------------------------------------------
        var $e4xSurface = $(
            '<div class="e4xSurface e4x'
                + (this.tagName == "INPUT" ? "Input" : "Textarea") + '"/>')
                .append($.editor4xml.xml2html($e4xSource.val(), opts));
        if (opts.surfaceEditable)
            $e4xSurface.attr("contenteditable", "true");
        if (opts.surfaceInitialize)
            opts.surfaceInitialize($e4xSurface, opts);
        $e4x.prepend($e4xSurface);

        // --------------------------------------------------------------------
        var $e4xToolbar = $('<div class="e4xToolbar" unselectable="on">' +
                            '<div class="e4xElementTrail"></div>' +
                            '<div class="e4xButtons"></div></div>');
        $e4xToolbar.on("selectstart mousedown", false);
        $.editor4xml.addDragEvents(
            $("#main"), $e4xToolbar.children(".e4xElementTrail"));
        $.editor4xml.createToolButtons(
            $e4xToolbar.children(".e4xButtons"), opts.buttons, opts.schema);
        $e4x.prepend($e4xToolbar);

        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        //                                Events
        // ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        // --------------------------------------------------------------------
        $e4xToolbar.on("click", ".e4xButton", function(event) {
            onToolButtonClick(event, $e4xToolbar, $(this), $e4xSurface);
            return false;
        });

        // --------------------------------------------------------------------
        $e4xSurface
        // Update source
            .on("updateSource", function() {
                $e4xSource.val($.editor4xml.html2xml($e4xSurface.html()));
            })
            .on("refresh", function() {
                $e4xSurface.trigger("updateSource");
                refreshToolbar($e4xToolbar);
            })
        // Focus events
            .focusin(function() {
                $.editor4xml.showMainToolbar($e4xToolbar);
                $.editor4xml.setCursor();
            })
            .focusout(function() {
                $e4xSurface.trigger("updateSource");
                $.editor4xml.hideMainToolbar($e4xToolbar);
            })
        // Mouse events
            .mouseup(function() {
                refreshToolbar($e4xToolbar);
            })
            .on("drop", function(event) {
                event.preventDefault();
            })
        // Keyboard events
            .keyup(function() {
                clearTimeout(timer);
                timer = setTimeout(function() {
                    refreshToolbar($e4xToolbar); }, 200);
            })
            .keydown(function(event) {
                onKeyDown(event, $e4xToolbar, $e4xSurface);
            });

        // --------------------------------------------------------------------
        $e4xSource
            .on("updateSurface", function() {
                $e4xSurface.empty().append(
                    $.editor4xml.xml2html($e4xSource.val(), opts));
            })
            .focusin(function() {
                $.editor4xml.showMainToolbar($e4xToolbar);
            })
            .focusout(function() {
                $e4xSource.trigger("updateSurface");
                $.editor4xml.hideMainToolbar($e4xToolbar);
            })
            .keydown(function(event) {
                switch(event.keyCode)
                {
                case 27: // Escape
                    $e4xSource.blur();
                    break;
                }
            });
     });
};


})(jQuery);
