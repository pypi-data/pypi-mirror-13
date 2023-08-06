// $Id: editor4publiset.js c06039273077 2015/11/20 14:56:55 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */

"use strict";

(function($) {


if (!$.publiset)     $.publiset = {};
if (!$.publiset.e4x) $.publiset.e4x = {};

$.publiset.e4x.NOTFOUND = "/Static/Images/notfound.jpg";


// ****************************************************************************
//                            ELEMENT2HTML FOR PUBLISET
// ****************************************************************************

// ----------------------------------------------------------------------------
// Create or convert an XML division head element into a jQuery HTML object.
$.publiset.e4x.html4head = function($node, $tag, opts, $division) {
    var $html = $node.length ? $.editor4xml.htmlRootTag($node, "div")
            : $('<div class="e4xElt-head"/>');

    // Element title
    if (!$division)
        $division = $node.parents("division").eq(0);
    $.publiset.e4x.html4title(
        $node.children("title"), $html, opts, $division);

    // Attributes
    var $table = $("<table/>");
    var done = ["title", "date", "source"];
    var $newTag;
    var attrs = $node.length ? $node.get(0).attributes : [];
    for (var i = 0 ; i < attrs.length ; i++) {
        var pattern = "@" + attrs[i].nodeName;
        $table.append($.publiset.e4x.html4headPatternRow(
            pattern, attrs[i].value, opts));
        done.push(pattern);
    }

    // Other elements
    $node.children().each(function() {
        var $node = $(this);
        var pattern = $node.get(0).nodeName;
        if (pattern == "identifier" && $node.attr("type"))
            pattern += "." + $node.attr("type");
        if ($.inArray(pattern, done) == -1) {
            $table.append($.publiset.e4x.html4headPatternRow(
                pattern, $node, opts));
            done.push(pattern);
        }
    });

    // Event to delete item
    $table.on("click", ".e4xDelete", function() {
        if (!window.confirm($.editor4xml.translate("sure?")))
            return;
        var $item = $(this).parents("tr").children("td").eq(1);
        var $table = $item.parents("table");
        var pattern = $item.data("pattern");
        if (pattern.charAt(0) == "@")
            $item.parents(".e4xElt-head").removeAttr(
                "data-" + pattern.slice(1));
        $(this).parents("tr").remove();
        $.publiset.e4x.html4headUpdateSelect($table, opts);
        $table.parents(".e4xSurface").trigger("updateSource");
    });

    // Combobox
    $.publiset.e4x.html4headUpdateSelect($table, opts, done);

    $html.append($table);
    $tag.append($html);
};

// ----------------------------------------------------------------------------
// Return a jQuery object for a head pattern (attribute or element).
$.publiset.e4x.html4headPatternRow = function(pattern, value, opts) {
    // Attribute
    var $newTag;
    if (pattern.indexOf("@") == 0) {
        $newTag = $(
            "<tr class='e4xIgnore'><td class='e4xAttribute'"
                + " data-pattern='" + pattern + "'>" + value + "</td></tr>");
        $newTag.children("td").click(function() {
            var $head = $(this).parents(".e4xElt-head");
            var $editor = $head.parents(".e4x");
            $.publiset.e4x.editHead(
                $editor, ($editor.hasClass("e4xCast-selection")
                          ? "selection" : "composition") + ".head",
                $head.get(0), opts);
        });
        $newTag
            .prepend("<td> = </td>")
            .prepend("<th><span class='e4xDelete'/>"
                     + $.editor4xml.translate(pattern) + "</th>");
        return $newTag;
    }

    // Element
    $newTag = $.editor4xml.xml2html(value, opts);
    $newTag.attr("contenteditable", "true");
    $newTag = $newTag
        .wrap("<tr><td data-pattern='" + pattern + "'/></tr>")
        .parent().parent()
        .prepend("<td class='e4xIgnore'> = </td>")
        .prepend("<th class='e4xIgnore'><span class='e4xDelete'/>"
                 + $.editor4xml.translate(pattern) + "</th>");
    return $newTag;
};

// ----------------------------------------------------------------------------
// Update meta head combobox.
$.publiset.e4x.html4headUpdateSelect = function($table, opts, done) {
    $table.find("select").parents("tr").remove();

    // Visible items
    if (!done) {
        done = ["title", "date", "source"];
        $table.find("tr").each(function() {
            done.push($(this).children("td").eq(1).data("pattern"));
        });
    }

    // <option> to add attributes
    var headSchema = opts.schema[opts.rootPattern.slice(1)+".head"];
    var $select = $("<select><option/></select>");
    if (headSchema.attributes)
        $.each(headSchema.attributes, function(attr) {
            if ($.inArray("@" + attr, done) == -1)
                $select.append(
                    '<option value="@' + attr + '">'
                        + $.editor4xml.translate("@" + attr) + "</option>");
        });

    // <option> to add elements
    $.each(headSchema.content[0], function(index, pattern) {
        if ($.inArray(pattern, done) == -1)
            $select.append('<option value="' + pattern + '">'
                    + $.editor4xml.translate(pattern) + "</option>");
    });

    // <select> in the table
    if ($select.children().length > 1) {
        $select.change(function() {
            var $row, pattern = $select.val();
            $select.val("");
            if ((pattern == "shorttitle" || pattern == "subtitle")
                && !$select.parents(".e4xElt-head").find(".e4xElt-title")
                .text().trim())
                return;
            if (pattern.charAt(0) == "@") {
                $row = $.publiset.e4x.html4headPatternRow(
                    pattern, '', opts);
                $table.prepend($row);
                $row.children("td").eq(1).click();
            } else {
                $row = $.publiset.e4x.html4headPatternRow(
                    pattern,
                    opts.schema[pattern].seed ||
                        ("<"+(opts.schema[pattern].element||pattern)+" e4x='here'/>"),
                    opts);
                if (!$table.find("tr").eq(-1).before($row).length)
                    $table.prepend($row);
                $row.find("[contenteditable]").focus();
                $.editor4xml.setHoldAndFocus($row);
                $row.find(".e4xEdit").click();
            }

            var $option = $select.children(
                "option[value='"+ pattern + "']");
            $option.remove();
            if ($select.children("option").length < 2)
                $select.parents("tr").remove();
        }).wrap("<tr class='e4xIgnore'><td colspan='3'/></tr>");
        $table.append($select.parent().parent());
    }
};

// ----------------------------------------------------------------------------
// Convert an XML image element into a jQuery HTML object.
$.publiset.e4x.html4image = function($node, $tag, opts) {
    var $html = $.editor4xml.htmlRootTag($node.removeAttr("e4x"), "span");
    $html.append(
        '<img src="'+$.publiset.e4x.NOTFOUND+'" alt="'+$node.attr("id")+'"'
            + '" title="'+$node.attr("id")+'"/>');
    $('<span class="e4xEdit"/>').appendTo($html).click(function() {
        $.publiset.e4x.editCoverImage(
            $(this).parents(".e4x"), "image", $(this).parent().get(0), opts);
    });

    $.getJSON(
        window.location.pathname.replace(/\/file\/(write|edit)/, "/file/media"),
        { type: "image", id: $node.attr("id") },
        function(data) {
            if (data.src)
                $html.children("img").attr("src", data.src);
        }
    );

    $tag.append($html);
};

// ----------------------------------------------------------------------------
// Convert an XML title element into a jQuery HTML object.
$.publiset.e4x.html4title = function($node, $tag, opts, $division) {
    var $html = $node.length ? $.editor4xml.htmlRootTag($node, "span")
            : $('<span class="e4xElt-title"><span class="e4xHold"/></span>');
    $html.attr("contenteditable", "true");

    // Add content
    $node.contents().each(function() {
        $html.append($.editor4xml.xml2html($(this), opts));
    });

    // Edit function
    var edit = function($division) {
        var $editor = $division.parents(".e4x");
        $.publiset.e4x.editDivision(
            $editor, ($editor.hasClass("e4xCast-selection")
                      ? "selection" : "composition") + ".division",
            $division.get(0), opts);
    };

    // Add edit button
    $html = $html.wrap("<h2/>").parent()
        .prepend("<span class='e4xAttributes'/>");
    $html.children(".e4xAttributes").click(function() {
        edit($(this).parents(".e4xElt-division"));
    });

    // Add selection button
    if (!$division)
        $division = $node.parents("division").eq(0);
    if (!$division.children("division").length) {
        $html.prepend("<span class='e4xSelectionGet'/>");
        $html.children(".e4xSelectionGet").click(function() {
            var $file = null;
            var $division = $tag.parent();
            $("#selection").find("input[name]").each(function() {
                var $input = $(this);
                if (!$input.prop("checked")) return;
                $file = $.publiset.e4x.newFile(
                    $division,
                    decodeURIComponent($input.attr("name").slice(1)), opts);
                $division.append($file);
            });
            $tag.parents(".e4xSurface").trigger("updateSource");
        });
    }

    // Add delete button
    $html.prepend("<span class='e4xDelete'/>");
    $html.children(".e4xDelete").click(function() {
        if (!window.confirm($.editor4xml.translate("sure?")))
            return;
        var $division = $(this).parents(".e4xElt-division");
        if ($division.length < 2)
            return;
        var $surface = $division.eq(0).parents(".e4xSurface");
        $division.eq(0).remove();
        $surface.trigger("updateSource");
    });

    // Add attributes
    var attrStr = "";
    var attrs = $division.get(0).attributes;
    for (var i = 0 ; i < attrs.length ; i++)
        attrStr += (i ? ", " : "") + attrs[i].nodeName+'="'+attrs[i].value+'"';
    if (attrStr)
        $html.append(
            $("<em class='e4xIgnore'>" + attrStr + "</em>").click(function() {
                $(this).parents("h2").children(".e4xElt-title").focus();
            }));

    $tag.append($html);
};

// ----------------------------------------------------------------------------
// Convert an XML division element into a jQuery HTML object.
$.publiset.e4x.html4division = function($node, $tag, opts) {
    var $html = $.editor4xml.htmlRootTag($node, "div");
    if (!$node.children("head").length)
        $.publiset.e4x.html4head($(""), $html, opts, $node);
    $tag.append($html);
    return $html;
};

// ----------------------------------------------------------------------------
// Convert an XML file element into a jQuery HTML object.
$.publiset.e4x.html4file = function($node, $tag, opts) {
    // Edit function
    var edit = function($file) {
        var $editor = $file.parents(".e4x");
        $.publiset.e4x.editFile(
            $editor, ($editor.hasClass("e4xCast-selection")
                      ? "selection" : "composition") + ".file",
            $file.get(0), opts);
    };

    // Absolute path
    var attrStr = $.publiset.e4x.absolutePath(
        $.publiset.e4x.rootPath(), $node, "path")
            .concat([$node.text().trim()]).join("/");

    // Create <div> tag
    var $html = $('<div class="e4xFile" data-fullname="' + attrStr + '">'
                  + '<span class="e4xTools">'
                  + '<span class="e4xHandle" draggable="true"/>'
                  + '<span class="e4xRemove"/>'
                  + '<span class="e4xAttributes"/></span></div>');
    var file = '<span class="e4xElt-file"';
    var attrs = $node.get(0).attributes;
    attrStr = "";
    for (var i = 0 ; i < attrs.length ; i++) {
        file += " data-" + attrs[i].nodeName + '="' + attrs[i].value + '"';
        attrStr += (i ? ", " : "") + attrs[i].nodeName+'="'+attrs[i].value+'"';
    }
    file += ">" + $node.text() + "</span>";
    $html.append(file);
    if (attrStr) {
        $html.append("<strong class='e4xIgnore'> | </strong>");
        $html.append($("<em class='e4xIgnore'>" + attrStr + "</em>"));
    }

    // Add events
    $html
        .on("selectstart mousedown", ".e4xRemove, .e4xAttributes", false)
        .click(function() {
            $(this).parents(".e4xElt-division").eq(0)
                .find(".e4xElt-title").focus();
        })
        .find(".e4xRemove")
        .click(function() {
            var $file = $(this).parents(".e4xFile");
            if (!window.confirm($.editor4xml.translate("sure?")))
                return;
            var $surface = $file.parents(".e4xSurface");
            $file.remove();
            $surface.trigger("updateSource");
        })
        .end().find(".e4xAttributes")
        .click(function() {
            edit($(this).parent().parent().children(".e4xElt-file"));
        });

    $tag.append($html);
};

// ----------------------------------------------------------------------------
$.publiset.e4x.element2html = {
    head: { html: $.publiset.e4x.html4head },
    title: { html: $.publiset.e4x.html4title },
    shorttitle: { html: "span" },
    subtitle: { html: "span" },
    identifier: { html: "span" },
    copyright: { html: "span" },
    collection: { html: "span" },
    source: { html: "span" },
    cover: { html: "span" },
    image: { html: $.publiset.e4x.html4image },
    label: { html: "strong" },

    division: { html: $.publiset.e4x.html4division },
    file: { html: $.publiset.e4x.html4file },

    sup: { html: "sup" },
    sub: { html: "sub" },
    highlight: { html: "strong" },
    emphasis: { html: "em" },
    name: { html: "em" },
    link: { html: "span" }
};


// ****************************************************************************
//                         EDITOR4XML BUTTONS FOR PUBLISET
// ****************************************************************************

// ----------------------------------------------------------------------------
// Action for division button
$.publiset.e4x.actionDivision = function(event, context, range, opts, env) {
    if (!range) return null;
    var element = opts.schema[context.pattern].element || context.pattern;
    var i = env.elements.length - 1;
    while (i >= 0 && element != env.elements[i]) i--;
    var $node = i < 0 ? $($.editor4xml.getNode(range)) : $(env.nodes[i]);

    // Create division
    var $division = $.editor4xml.xml2html(
        context.xml || opts.schema[context.pattern].seed
            || ("<"+element+"  e4x='here'/>"), opts);
    $division.find("[data-e4x='hold']").addBack("[data-e4x='hold']")
        .append('<span class="e4xHold"/>').removeAttr("data-e4x");

    // Insert a sub division
    if (i < 0 || event.shiftKey) {
        if ($.trim($node.children(".e4xElt-file, .e4xElt-link").text()))
            return null;
        $node.children(".e4xElt-file, .e4xElt-link").remove();
        if (event.ctrlKey)
            $node.prepend($division);
        else
            $node.append($division);
    }
    // Insert a sibling division
    else {
        if (event.ctrlKey)
            $node.before($division);
        else
            $node.after($division);
    }

    // Manage "here"
    $division.find("[data-e4x='here']").addBack("[data-e4x='here']")
        .append('<span class="e4xHold"/>');
    $.editor4xml.setCursor(
        $division.find("[data-e4x='here']").addBack("[data-e4x='here']")
            .removeAttr("data-e4x"));
    $.editor4xml.scrollTo($division);

    return $division;
};

// ----------------------------------------------------------------------------
$.publiset.e4x.buttonsSymbols = [
    [
        { op: "symbol", symbol: "‧", tooltip: "Non-breaking space" },
        { op: "symbol", symbol: "« "}, { op: "symbol", symbol: " »" },
        { op: "symbol", symbol: "¡" }, { op: "symbol", symbol: "¿" },
        { op: "symbol", symbol: "©" }, { op: "symbol", symbol: "®" },
        { op: "symbol", symbol: "™" }
    ], [
        { op: "symbol", symbol: "–" }, { op: "symbol", symbol: "—" },
        { op: "symbol", symbol: "•" }, { op: "symbol", symbol: "‣" },
        { op: "symbol", symbol: "→" }, { op: "symbol", symbol: "←" },
        { op: "symbol", symbol: "↑" }, { op: "symbol", symbol: "↓" }
    ], [
        { op: "symbol", symbol: "á" }, { op: "symbol", symbol: "í" },
        { op: "symbol", symbol: "ß" }, { op: "symbol", symbol: "Ñ" },
        { op: "symbol", symbol: "ñ" }, { op: "symbol", symbol: "ó" },
        { op: "symbol", symbol: "Œ" }, { op: "symbol", symbol: "œ" }
    ]
];

$.publiset.e4x.buttonsInline = [
    { op: "toolbar", entries: $.publiset.e4x.buttonsSymbols,
      class: "e4xButtonSymbols", tooltip: "Symbols" },
    { op: "tag", pattern: "sup", tooltip: "Exponent" },
    { op: "tag", pattern: "sub", tooltip: "Subscript" },
    { op: "tag", pattern: "highlight", tooltip: "Highlighting" },
    { op: "tag", pattern: "emphasis", tooltip: "Emphasis" },
    { op: "tag", pattern: "name", attribute: "of", tooltip: "Name" }
];

$.publiset.e4x.buttonsHead = [
    { op: "tag", pattern: "contributor", insert: "sibling",
      tooltip: "Contributor" },
    { op: "tag", pattern: "keyword", insert: "sibling", tooltip: "Keyword" },
    { op: "tag", pattern: "subject", insert: "sibling", tooltip: "Subject" },
    { op: "tag", pattern: "p", insert: "wrap-sibling", tooltip: "Paragraph" }
];

$.publiset.e4x.buttonsCompositionDivision = [
    { op: "action", action: $.publiset.e4x.actionDivision,
      pattern: "composition.division", insert: "sibling", delayedition: true,
      tooltip: "Division (↑ for sub division)", class: "e4xButton-division" }
];
$.publiset.e4x.buttonsSelectionDivision = [
    { op: "action", action: $.publiset.e4x.actionDivision,
      pattern: "selection.division", insert: "sibling", delayedition: true,
      tooltip: "Division (↑ for sub division)", class: "e4xButton-division" }
];


// ****************************************************************************
//                           PATTERN EDITION FOR PUBLISET
// ****************************************************************************

// ----------------------------------------------------------------------------
// Edit a division head element.
$.publiset.e4x.editHead = function($editor, pattern, node, opts) {
    var $body = $.editor4xml.divAttributes(
        opts.schema[pattern].attributes, $.editor4xml.getAttributes(node));

    // Function to edit attribute
    var editAttribute = function($head) {
        var $editor = $head.parents(".e4x");
        $.publiset.e4x.editHead(
            $editor, ($editor.hasClass("e4xCast-selection")
                      ? "selection" : "composition") + ".head",
            $head.get(0), opts);
    };

    // OK button
    var onOk = function($editor, $body, $node) {
        $.editor4xml.boxUpdateAttrAndClose($editor, $body, $node);
        $node.find(".e4xAttribute").parents("tr").remove();
        var $table = $node.find("table");
        var attrs = $node.get(0).attributes;
        for (var i = 0 ; i < attrs.length ; i++) {
            if (attrs[i].nodeName.indexOf("data-") != 0)
                continue;
            pattern = "@" + attrs[i].nodeName.slice(5);
            $table.prepend($.publiset.e4x.html4headPatternRow(
                pattern, attrs[i].value, opts));
        }
        $.publiset.e4x.html4headUpdateSelect($table, opts);
    };

    // Open dialog box
    var $node = $(node);
    $.editor4xml.boxButtons($editor, $body, $node, null, onOk);
    $.editor4xml.dialogBox(
        $editor,
        $.editor4xml.translate("Properties") + " &lt;head&gt;",
        $body.children(), $node);
};

// ----------------------------------------------------------------------------
// Edit an image element.
$.publiset.e4x.editCoverImage = function($editor, pattern, node, opts) {
    // Create attribute zone
    var $body = $.editor4xml.divAttributes(
        opts.schema[pattern].attributes, $.editor4xml.getAttributes(node));

    // Create resources zone
    $body.append($.editor4xml.divResources("image", "id"));

    // Add main buttons
    var onOk = function($editor, $body, $node) {
        var id = $body.find("[data-id='id']").val();
        $.getJSON(
            window.location.pathname.replace(
                    /\/file\/(write|edit)/, "/file/media"),
            { type: "image", id: id },
            function(data) {
                if (data.src)
                    $node.children("img").attr("src", data.src);
                else
                    $node.children("img").attr("src", $.publiset.e4x.NOTFOUND);
                $node.children("img").attr("alt", id).attr("title", id);
            }
        );
        $.editor4xml.boxUpdateAttrAndClose($editor, $body, $node);
    };

    // Open dialog box
    var $node = $(node);
    $.editor4xml.boxButtons($editor, $body, $node, null, onOk);
    $.editor4xml.dialogBox(
        $editor, $.editor4xml.translate("Cover"), $body.children(), $node);
};

// ----------------------------------------------------------------------------
// Edit a division element.
$.publiset.e4x.editDivision = function($editor, pattern, node, opts) {
    var $body = $.editor4xml.divAttributes(
        opts.schema[pattern].attributes, $.editor4xml.getAttributes(node));

    // OK button
    var onOk = function($editor, $body, $node) {
        $.editor4xml.boxUpdateAttrAndClose($editor, $body, $node);
        $node.children(".e4xFile").each(function() {
            $.publiset.e4x.updateFile($(this), "data-path", opts);
        });
        var attrStr = '';
        var attrs = $node.get(0).attributes;
        for (var i = 0 ; i < attrs.length ; i++)
            if (attrs[i].nodeName.indexOf("data-") == 0)
                attrStr += (attrStr ? ", " : "") + attrs[i].nodeName.slice(5)
                + '="' + attrs[i].value + '"';
        $node = $node.children(".e4xElt-head").children("h2");
        $node.children("em.e4xIgnore").remove();
        if (attrStr)
            $node.append(
                $("<em class='e4xIgnore'>"+attrStr+"</em>").click(function() {
                    var $division = $(this).parents(".e4xElt-division");
                    var $editor = $division.parents(".e4x");
                    $.publiset.e4x.editDivision(
                        $editor, ($editor.hasClass("e4xCast-selection")
                                  ? "selection" : "composition") + ".division",
                        $division.get(0), opts);
                }));
        $node.children(".e4xElt-title").focus();
        $.editor4xml.setCursor($node.find(".e4xHold"));
    };

    // Open dialog box
    var $node = $(node);
    $.editor4xml.boxButtons($editor, $body, $node, null, onOk);
    $.editor4xml.dialogBox(
        $editor,
        $.editor4xml.translate("Properties") + " &lt;division&gt;",
        $body.children(), $node);
};

// ----------------------------------------------------------------------------
// Edit a file element.
$.publiset.e4x.editFile = function($editor, pattern, node, opts) {
    var $body = $.editor4xml.divAttributes(
        opts.schema[pattern].attributes, $.editor4xml.getAttributes(node));

    // OK button
    var onOk = function($editor, $body, $node) {
        $.editor4xml.boxUpdateAttrAndClose($editor, $body, $node);
        $.publiset.e4x.updateFile($node.parent(), null, opts);
    };

    // Open dialog box
    var $node = $(node);
    $.editor4xml.boxButtons($editor, $body, $node, null, onOk);
    $.editor4xml.dialogBox($editor, $node.text(), $body.children(), $node);
};

// ----------------------------------------------------------------------------
$.publiset.e4x.editPattern = {
    "composition.head": $.publiset.e4x.editHead,
    "selection.head": $.publiset.e4x.editHead,
    image: $.publiset.e4x.editCoverImage,
    "composition.division": $.publiset.e4x.editDivision,
    "selection.division": $.publiset.e4x.editDivision,
    "composition.file": $.publiset.e4x.editFile,
    "selection.file": $.publiset.e4x.editFile
};


// ****************************************************************************
//                         KEYBOARD MANAGEMENT FOR PUBLISET
// ****************************************************************************

$.publiset.e4x.keyboard = {
    // Enter
    13: [{ pattern: "keyword" }, { pattern: "subject" }, { pattern: "p" }]
};


// ****************************************************************************
//                        SURFACE INITIALIZATION FOR PUBLISET
// ****************************************************************************

// ----------------------------------------------------------------------------
// Surface initialization with drag & drop events
$.publiset.e4x.surfaceInitialize = function($surface, opts) {
    var $dragging;
    var selectionColor = $("#selection").data("color");

    $surface
        .on("dragstart", ".e4xHandle", function(event) {
            $dragging = $(this).parent().parent();
            event.originalEvent.dataTransfer.effectAllowed = "move";
            event.originalEvent.dataTransfer.setData(
                "text", $dragging.data("fullname"));
            $dragging.addClass("e4xDragging");
        })
        .on("dragend", ".e4xHandle", function() {
            $dragging.removeClass("e4xDragging");
            $dragging = null;
        })
        .on("dragenter dragover", ".e4xElt-division", function(event) {
            // From selection
            var $drop = $(this);
            if (!$dragging) {
                if (!$drop.children(".e4xElt-division").length)
                    $drop.css("background-color", selectionColor);
                return false;
            }
            // From editor
            if (event.originalEvent.pageY-$drop.offset().top < $drop.innerHeight()/2) {
                if (!$drop.children(".e4xElt-head").after($dragging).length)
                    $drop.prepend($dragging);
            } else {
                $drop.append($dragging);
            }
            return false;
        })
        .on("dragenter dragover", ".e4xFile", function() {
            // From selection
            var $drop = $(this);
            if (!$dragging) {
                $drop.parent().css("background-color", selectionColor);
                return false;
            }
            // From editor
            if (!$drop.is($dragging))
                $drop[$dragging.index() < $drop.index()
                      ? "after" : "before"]($dragging);
            return false;
        })
        .on("dragleave", ".e4xElt-division", function() {
            $(this).css("background-color", "transparent");
        })
        .on("drop", ".e4xElt-division", function(event) {
            var $division = $(this);
            $division.css("background-color", "transparent");
            var fullname = event.originalEvent.dataTransfer.getData("text");
            if (fullname.search(/https?:\/\//) == 0)
                return false;
            if ($dragging)
                $.publiset.e4x.updateFile($dragging, "data-path", opts);
            else
                $division.append($.publiset.e4x.newFile(
                    $division, decodeURIComponent(fullname), opts));
            $surface.trigger("updateSource");
            return false;
        })
        .on("drop", ".e4xFile", function(event) {
            var $file = $(this);
            var $division = $file.parent();
            $division.css("background-color", "transparent");
            var fullname = event.originalEvent.dataTransfer.getData("text");
            if (fullname.search(/https?:\/\//) == 0)
                return false;
            if ($dragging)
                $.publiset.e4x.updateFile($dragging, "data-path", opts);
            else
                $file.after($.publiset.e4x.newFile(
                    $division, decodeURIComponent(fullname), opts));
            $surface.trigger("updateSource");
            return false;
        });
};

// ----------------------------------------------------------------------------
// Return the root path as an array
$.publiset.e4x.rootPath = function() {
    var path = window.location.pathname;
    return path.slice(path.indexOf("/edit/") + 6) .split("/").slice(0, -1);
};

// ----------------------------------------------------------------------------
// Return the item absolute path as an array
$.publiset.e4x.absolutePath = function(rootPath, $item, pathAttr) {
    var path = $item.parents("["+pathAttr+"]").addBack("["+pathAttr+"]")
            .eq(-1).attr(pathAttr);
    if (!path)
        path = $("#composition_head_path, #selection_head_path").val();
    path = path ? rootPath.concat(path.split("/")) : rootPath;

    var itemPath = [];
    for (var i = 0 ; i < path.length ; i++)
        if (path[i] == "..")
            itemPath.pop();
        else if (path[i] != ".")
            itemPath.push(path[i]);
    return itemPath;
};

// ----------------------------------------------------------------------------
// Return the relative to $division path as an array
$.publiset.e4x.relativePath = function($division, fullname, pathAttr) {
    // Root, division and file absolute paths as arrays
    var rootPath = $.publiset.e4x.rootPath();
    var divPath = $.publiset.e4x.absolutePath(rootPath, $division, pathAttr);
    var filePath = fullname.split("/").slice(0, -1);

    // No need for path
    if (filePath.join("/") == divPath.join("/"))
        return [];

    // Create the relative path
    var i = 0;
    while (i < filePath.length && i < rootPath.length
           && filePath[i] == rootPath[i])
        i++;
    var path = [];
    for (var j = i ; j < rootPath.length ; j++)
        path.push("..");
    path = path.concat(filePath.slice(i));
    if (!path.length && divPath != rootPath) path = ["."];

    return path;
};

// ----------------------------------------------------------------------------
// Update file path
$.publiset.e4x.updateFile = function($file, pathAttr, opts) {
    if (pathAttr) {
        pathAttr = $.publiset.e4x.relativePath(
            $file.parent(), $file.data("fullname"), pathAttr).join("/");
        $file.children(".e4xElt-file").removeAttr("data-path");
        if (pathAttr)
            $file.children(".e4xElt-file").attr("data-path", pathAttr);
    }

    var attrStr = '';
    var attrs = $file.children(".e4xElt-file").get(0).attributes;
    for (var i = 0 ; i < attrs.length ; i++)
        if (attrs[i].nodeName.indexOf("data-") == 0)
            attrStr += (attrStr ? ", " : "") + attrs[i].nodeName.slice(5)
        + '="' + attrs[i].value + '"';
    $file.children("em.e4xIgnore, strong.e4xIgnore").remove();
    if (attrStr) {
        $file.append("<strong class='e4xIgnore'> | </strong>");
        $file.append(
            $("<em class='e4xIgnore'>"+attrStr+"</em>").click(function() {
                var $file = $(this).parent().children(".e4xElt-file");
                var $editor = $file.parents(".e4x");
                $.publiset.e4x.editFile(
                    $editor, ($editor.hasClass("e4xCast-selection")
                              ? "selection" : "composition") + ".file",
                    $file.get(0), opts);
            }));
    }
};

// ----------------------------------------------------------------------------
// Return a file jQuery object according to path
$.publiset.e4x.newFile = function($division, fullname, opts) {
    if (!fullname) return "";

    var name = fullname.split("/").slice(-1);
    var path = $.publiset.e4x.relativePath($division, fullname, "data-path");
    if (path.length) path = ' path="' + path.join("/") +'"';

    var $file = $.editor4xml.xml2html("<file"+path+">"+name+"</file>", opts);
    $file.attr("data-fullname", fullname);
    return $file;
};


})(jQuery);
