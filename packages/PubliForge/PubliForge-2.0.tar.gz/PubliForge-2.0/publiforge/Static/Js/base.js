// $Id: base.js 08ea42baa1d1 2015/06/12 15:26:17 Patrick $

/*global jQuery: true */
/*global setTimeout: true */
/*global clearTimeout: true */

"use strict";

jQuery(document).ready(function($) {
    // ------------------------------------------------------------------------
    // Initialization
    // ------------------------------------------------------------------------

    var shortDelay = 12000;
    var longDelay = 20000;
    var panelMinWidth = 20;
    var panelTransition = ".6s";
    var idx = {panelClosed: 0, panelWidth: 1, menuClosed: 2, tabUser: 3,
               tabGroup: 4, tabStorage: 5, tabIndexer: 6, tabProject: 7,
               tabRole: 8, tabProcessing: 9, tabTask: 10, tabPack: 11,
               tabJob: 12};
    var state = jQuery.cookie('PF_STATE');
    if (!state)
        state = '0|22|0|tab0|tab0|tab0|tab0|tab0|tab0|tab0|tab0|tab0|tab0';
    state = state.split('|');

    // ------------------------------------------------------------------------
    // Left panel
    // ------------------------------------------------------------------------

    var $content1 = $("#content1");
    var $content2 = $("#content2");
    var $leftPanel = $("#leftPanel");
    var $leftContent = $("#leftContent");
    var $rightPanel = $("#rightPanel");
    var $menu = $("#menu");
    var $selection = $("#selection");
    var panelWidth = parseInt(state[idx["panelWidth"]]);
    if (!$("#leftClose").length) {
        $('<div id="panelResize"/>').prependTo($rightPanel);
        $('<div id="leftClose"><span>«</span></div>').prependTo($leftPanel);
        $('<div id="leftOpen"><span>»</span></div>').prependTo($rightPanel);
    }

    $content2.css("right", (100-panelWidth)+"%");
    $leftPanel.css({width: panelWidth+"%", left: (100-panelWidth)+"%"});
    $rightPanel.css({width: (100-panelWidth)+"%", left: (100-panelWidth)+"%"});

    if (state[idx["panelClosed"]] == 1) {
        $leftPanel.hide();
        $content2.css({right: "100%"});
        $rightPanel.css({left: "100%", width: "100%"});
        $("#panelResize").hide();
        $("#leftOpen").show();
    }

    $("#leftClose").click(function() {
        if (state[idx["panelClosed"]] == 0) {
            $("#panelResize").hide();
            $content2.animate(
                {"margin-left": -$leftPanel.outerWidth(true)}, "slow",
                function() {
                    $leftPanel.hide();
                    $content2.css({right: "100%", "margin-left": ""});
                    $rightPanel.css("left", "100%")
                        .animate({width: "100%"}, "fast");
                    $("#leftOpen").show("slow");
                });
            state[idx["panelClosed"]] = 1;
            $.cookie("PF_STATE", state.join("|"), {path: "/"});
        }
    });

    $("#leftOpen").click(function() {
        if (state[idx["panelClosed"]] == 1) {
            var panelWidthPx = $leftPanel.outerWidth(true);
            $("#leftOpen").hide("fast");
            $rightPanel.animate(
                {width: "-=" + panelWidthPx}, "fast",
                function() {
                    $rightPanel.css({
                        width: (100-panelWidth)+"%",
                        left: (100-panelWidth)+"%"});
                    $leftPanel.css({
                        width: panelWidth+"%",
                        left: (100-panelWidth)+"%"
                    }).show();
                    $content2.css({
                        "margin-left": -panelWidthPx,
                        right: (100-panelWidth)+"%"
                    }).animate({"margin-left": 0}, "slow");
                    if ($selection.length)
                        $leftContent.css(
                            "height", Math.max(
                                $menu.outerHeight(true),
                                $selection.outerHeight(true))
                                + $("#leftClose").outerHeight(true));
                });
            $("#panelResize").show();
            state[idx["panelClosed"]] = 0;
            $.cookie("PF_STATE", state.join("|"), {path: "/"});
        }
    });

    $("#panelResize").mousedown(function(event) {
        event.preventDefault();
        $content1.mousemove(function(event) {
            panelWidth = Math.round(event.pageX / $content2.outerWidth()*100);
            if (panelWidth < panelMinWidth) panelWidth = panelMinWidth;
            if (panelWidth > 100 - panelMinWidth)
                panelWidth = 100 - panelMinWidth;
            $content2.css("right", (100-panelWidth)+"%");
            $leftPanel.css({
                width: panelWidth+"%", left: (100-panelWidth)+"%"});
            $rightPanel.css({
                width: (100-panelWidth)+"%", left: (100-panelWidth)+"%"});
        });
    });

    $content1.mouseup(function() {
        if (!$._data($content1[0]).events["mousemove"])
            return;
        $content1.off("mousemove");
        if ($selection.length)
            $leftContent.css(
                "height",
                Math.max($menu.outerHeight(true), $selection.outerHeight(true))
                    + $("#leftClose").outerHeight(true));
        state[idx["panelWidth"]] = panelWidth;
        $.cookie("PF_STATE", state.join("|"), {path: "/"});
    });

    $.updateLeftHeight = function() {
        $leftContent.css(
            "height",
            Math.max($menu.outerHeight(true), $selection.outerHeight(true))
                + $("#leftClose").outerHeight(true));
    };

    // ------------------------------------------------------------------------
    // Selection
    // ------------------------------------------------------------------------

    if ($selection.length) {
        if (state[idx["menuClosed"]] == 1)
            $leftContent.addClass("showSelection");

        $menu.addClass("flip")
            .children("ul").children("li").eq(0).children("ul")
            .prepend("<li><span class='selection'>"
                     + $selection.children("legend").text()
                     + " (" + $selection.find(".selectionFile").length
                     + ")</span></li>")
            .children("li").eq(0).click(function() {
                $selection.css("transition", panelTransition);
                $menu.css("transition", panelTransition);
                $leftContent.addClass("showSelection");
                state[idx["menuClosed"]] = 1;
                $.cookie("PF_STATE", state.join("|"), {path: "/"});
            });

        $selection.addClass("flip")
            .children("legend").append("<strong/>")
            .click(function() {
                $selection.css("transition", panelTransition);
                $menu.css("transition", panelTransition);
                $leftContent.removeClass("showSelection");
                state[idx["menuClosed"]] = 0;
                $.cookie("PF_STATE", state.join("|"), {path: "/"});
            })
            .end().find(".selectionTool").each(function () {
                var $this = $(this);
                $this.replaceWith(
                    "<span class='selectionTool'"
                        + " title='" + $this.attr("title") + "'"
                        + " data-href='" + $this.attr("href") + "'>"
                        + $this.html() + "</span>");
                $this.remove();
            })
            .end().on("click", ".selectionTool", function() {
                var $img = $(this).children("img");
                if ($img.attr("src").indexOf("remove") != -1
                    && $img.attr("src").indexOf("remove_one") != -1) {
                    $img.attr("src", $img.attr("src").replace("one", "sure"));
                    return;
                }
                $.ajax({
                    url: $(this).data("href"),
                    dataType: "json",
                    cache: false,
                    success: function(data) {
                        $("#selectionFiles").html(data);
                        var $size = $menu.find(".selection");
                        $size.text($size.text().replace(
                                /\d+/, $selection.find(".selectionFile").length));
                        $.updateLeftHeight();
                        setTimeout($.updateLeftHeight, 1000);
                    }});
            }).on("click", ".selectAll", function() {
                var $this= $(this);
                $this.parent().nextAll("ul").find("input")
                    .prop("checked", $this.prop("checked"));
            });

        var toSelection = false;
        $(".selectable")
            .attr("draggable", "true")
            .on("dragstart", function(event) {
                event.originalEvent.dataTransfer.effectAllowed = "move";
                event.originalEvent.dataTransfer.setData(
                    "text", $(this).data("path"));
                toSelection = true;
            })
            .on("dragend", function() {
                $("#selectionFiles").css("background-color", "transparent");
                toSelection = false;
            });

        $("#selectionFiles")
            .on("dragover", function(event) {
                if (toSelection)
                    $(this).css("background-color", $selection.data("color"));
                event.preventDefault();
            })
            .on("dragleave", function(event) {
                $(this).css("background-color", "transparent");
            })
            .on("drop", function(event) {
                var url = "/selection/add/"
                        + event.originalEvent.dataTransfer.getData("text");
                $.ajax({
                    url: url,
                    dataType: "json",
                    cache: false,
                    success: function(data) {
                        $("#selectionFiles").html(data);
                        var $size = $menu.find(".selection");
                        $size.text($size.text().replace(
                                /\d+/, $selection.find(".selectionFile").length));
                        $.updateLeftHeight();
                        setTimeout($.updateLeftHeight, 1000);
                    }});
                return false;
            })
            .on("dragstart", ".selectionFile", function(event) {
                event.originalEvent.dataTransfer.effectAllowed = "move";
                event.originalEvent.dataTransfer.setData(
                    "text", $(this).data("path"));
                toSelection = false;
            })
            .on("dragend", ".selectionFile", function() {
                $(".container").css("background-color", "transparent");
            });

        $(".container")
            .on("dragover", function(event) {
                if (!toSelection)
                    $(this).css("background-color", $selection.data("color"));
                event.preventDefault();
            })
            .on("dragleave", function(event) {
                $(this).css("background-color", "transparent");
            })
            .on("drop", function(event) {
                $(this).css("background-color", "transparent");
                var path = event.originalEvent.dataTransfer.getData("text");
                if (path.search(/(https?|file):\/\//) == 0)
                    return false;
                var qs = window.location.search;
                var url = (qs ? qs + "&" : "?") + "get!"
                        + ($(this).data("target") || '') + ".x&~" + path;
                $.getJSON(url, function() {
                    window.location = window.location.pathname;
                });
                return false;
            });

        $.updateLeftHeight();
    }

    // ------------------------------------------------------------------------
    // Flash
    // ------------------------------------------------------------------------

    var $flash = $("#flash");
    $flash.hide().slideDown("slow").delay(shortDelay)
        .slideUp("slow", function() { $.updateContentHeight(-1); });

    // ------------------------------------------------------------------------
    // Content zone
    // ------------------------------------------------------------------------

    var $window = $(window);
    var $content = $("#content");
    var $footer = $("#footer");

    $.updateContentHeight = function(delta) {
        if ($content.length && $footer.length &&
            $content.offset().top < $window.height() * .3) {
            $content.css("height", "");
            var leftHeight = $content2.offset().top + $leftPanel.outerHeight()
                    + $footer.outerHeight();
            if (leftHeight < $window.height()) {
                delta = delta || 0;
                var contentHeight = $window.height() - $content.offset().top
                        - ($("div.listPager").outerHeight(true) || 0)
                        - ($("div.listFooter").outerHeight(true) || 0)
                        - $footer.outerHeight() - 12 + delta;
                if (delta != -1 && $flash.length)
                    contentHeight -= 70;
                if (contentHeight > 50)
                    $content.css("height", contentHeight + "px");
            }
            var $current = $("#current");
            if ($current.length && $current.offset().top > $window.height()) {
                $content.animate({
                    scrollTop: $current.offset().top-$content.offset().top-20
                });
            }
        }
    };
    $.updateContentHeight();

    if ($content.length && $footer.length) {
        var timer = null;
        $window.resize(function() {
            clearTimeout(timer);
            timer = setTimeout($.updateContentHeight, 200);
        });
    }

    // ------------------------------------------------------------------------
    // Tab set
    // ------------------------------------------------------------------------

    $(".tabs li a").click(function() {
        var $this = $(this);
        $(".tabs li").removeClass("tabCurrent");
        $this.parent().addClass("tabCurrent");
        $(".tabContent").hide();
        $("#tabContent" + $this.attr("id").replace("tab", "")).show();
        state[idx[$this.parent().parent().attr("id")]] = $this.attr("id");
        $.cookie("PF_STATE", state.join("|"), {path: "/"});
        return false;
    });

    $(".tabs").each(function() {
        var tab = window.location.hash.replace("#", "");
        if (tab.substring(0, 3) != "tab")
            tab = state[idx[$(this).attr("id")]];
        $("#" + tab).click();
    });

    // ------------------------------------------------------------------------
    // Tool tip
    // ------------------------------------------------------------------------

    $(".toolTip").removeAttr("title").click(function() { return false; });

    $("table.tableToolTip .toolTip").mouseenter(function() {
        var $icon = $(this);
        $("#toolTipContent").remove();
        $('<div id="toolTipContent">...</div>')
            .width($icon.parent().parent().width() - $icon.parent().width() - 15)
            .hide()
            .insertAfter($icon)
            .load("?" + $icon.attr("name") + ".x=10", function() {
                var $toolTip = $(this);
                if ($toolTip.text().length)
                    $toolTip.show().offset({
                        left: $icon.parents("tr").offset().left + 5,
                        top: $icon.offset().top - $toolTip.outerHeight()
                    });
            });
    });

    $("div.formItemToolTip .toolTip").mouseenter(function() {
        var $icon = $(this);
        $("#toolTipContent").remove();
        $('<div id="toolTipContent">...</div>')
            .hide()
            .insertAfter($icon)
            .load("?" + $icon.attr("name") + ".x=10", function() {
                var $toolTip = $(this);
                if ($toolTip.text().length)
                    $toolTip.show().offset({
                        left: $icon.parent().offset().left,
                        top: $icon.offset().top - $toolTip.outerHeight()
                    });
            });
    });

    $(".toolTip").mouseleave(function() {
        $("#toolTipContent").remove();
    });

    $("table.list").mouseleave(function() {
        $("#toolTipContent").remove();
    });

    // ------------------------------------------------------------------------
    // Buttons
    // ------------------------------------------------------------------------

    // Check all
    $("#check_all")
        .removeAttr("id")
        .prepend($('<input id="check_all" name="check_all" type="checkbox" value="1"/>'))
        .find("#check_all").click(function() {
            $("input.listCheck").prop("checked", $(this).prop("checked"));
        });

    // Slow button
    var slowImgUrl = "/Static/Images/wait_slow.gif";
    var $slowImg = $('<img src="' + slowImgUrl + '" alt="slow"/>');
    $("a.slow").click(function() {
        var $this = $(this);
        if ($this.children("img").length)
            $this.children("img").attr("src", slowImgUrl);
        else
            $this.append(" ").append($slowImg);
    });
    $("input.slow").click(function() {
        var $this = $(this);
        if ($this.attr("src"))
            $this.attr("src", slowImgUrl);
        else
            $this.append(" ").append($slowImg);
    });

    // ------------------------------------------------------------------------
    // Parameters for action
    // ------------------------------------------------------------------------

    $("#actionParams").hide().slideDown("slow", function() {
        $.updateContentHeight();
    });
});
