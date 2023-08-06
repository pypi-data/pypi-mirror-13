/**
 * @projectDescription audio_player.js
 * Plugin for custom player audio.
 *
 * @author prismallia.fr
 * @version 0.1
 * $Id: audio_player.js 199887c8ebb8 2016/01/25 18:51:32 Sylvain $
 */

/**
 *
 * Copyright (C) Prismallia, Paris, 2015. All rights reserved.
 *
 * This program is free software. You can redistribute it and/or modify
 * it under the terms of the GNU General Public License version 2 as
 * published by the Free Software Foundation.
 *
 * This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
 * WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
 *
 */

/*jshint globalstrict: true*/
/*global jQuery: true */


(function ($) {

"use strict";

$.fn.player = function(options, args) {

    var defaults = {
        timeLineWidth: -1,
        durationFormat: "m:ss / m:ss",
    };

    var $this = this;
    var opts = $.extend( {}, defaults, options);

    /**********************************************************************
     *                          Library function
     *********************************************************************/

    /**
     * Configure player audio
     *
     * @param {Object} $player, object jquery playerAudio.
     * @return {int} player timeline width.
     */
    function configure($player) {
        var $playerDuration = $player.children().filter("[data-player=\"duration\"]");
        var $playerButtonPlay = $player.children().filter("[data-player=\"button-play\"]");
        var $playerButtonStop = $player.children().filter("[data-player=\"button-stop\"]");
        var $playerTimeLine = $player.children().filter("[data-player=\"timeline\"]");
        var $playerCursor = $playerTimeLine.children().filter("[data-player=\"cursor\"]");

        if (opts.timeLineWidth != -1 ) {
            $playerTimeLine.css("width",opts.timeLineWidth+"px");
            var buttonsWidth = $playerButtonPlay.width();
            if ($playerButtonStop) {
                buttonsWidth += $playerButtonStop.width() + 2;
                $playerTimeLine.css("left",(buttonsWidth + 5)+"px");
            }
            $playerDuration.css("margin-left", (opts.timeLineWidth+buttonsWidth-$playerDuration.width())+"px");
        } else {
            var width = $playerDuration.width() -
                ( $playerButtonPlay.width() +
                  parseInt($playerButtonPlay.css("margin-right").replace("px",""), 10) );
            $playerTimeLine.css("width",width+"px");
            $playerDuration.css("margin-left", width+"px");
        }
        var timelineWidth = $playerTimeLine.width() - $playerCursor.width();
        return timelineWidth;
    }

    /**
     * Read audio metadata
     *
     * @param {Object} $player, object jquery playerAudio.
     */
    function audioMetaData($player) {
        var $source = $player.find("audio");
        var $playerDuration = $player.children().filter("[data-player=\"duration\"]");

        $source.unbind("loadedmetadata");
        $source.unbind("canplaythrough");

        var duration = $source[0].duration;
        var minutes = Math.floor(duration / 60);
        var seconds = Math.round(duration - minutes * 60);
        seconds = ("0" + seconds).slice(-2);

        if (opts.durationFormat == "m:ss / m:ss")
            $playerDuration.text("0:00 / "+minutes+":"+seconds);
        if (opts.durationFormat == "m:ss")
            $playerDuration.text("0:00");
    }

    /**
     * Event timeupdate, update cursor position and duration info.
     *
     * @param {Object} $player, object jquery playerAudio.
     * @param {int} timelineWidth, player timeline width.
     */
    function onTimerUpdate($player, timelineWidth) {
        var $source = $player.find("audio");
        var $playerDuration = $player.children().filter("[data-player=\"duration\"]");
        var $playerButtonPlay = $player.children().filter("[data-player=\"button-play\"]");
        var $playerTimeLine = $player.children().filter("[data-player=\"timeline\"]");
        var $playerCursor = $playerTimeLine.children().filter("[data-player=\"cursor\"]");

        // Source duration
        var duration = $source[0].duration;
        var minutes = Math.floor(duration / 60);
        var seconds = Math.round(duration - minutes * 60);
        seconds = ("0" + seconds).slice(-2);

        // Update duration
        var time = $source[0].currentTime;
        var m = Math.floor(time / 60);
        var s = Math.round(time - m * 60);
        s = ("0" + s).slice(-2);
        if (opts.durationFormat == "m:ss / m:ss")
            $playerDuration.text(m+":"+s+" / "+minutes+":"+seconds);
        if (opts.durationFormat == "m:ss")
            $playerDuration.text(m+":"+s);

        // Update player cursor position
        var position = timelineWidth * (time / duration);
        $playerCursor.css("margin-left", position + "px");
        if ($source[0].currentTime == duration) {
            var img = $playerButtonPlay.find("img")[0];
            var src = img.src;
            img.src = src.replace("pause", "play");
        }
    }

    /**
     * Get click position in player time line
     *
     * @params {Object} ev: Event object.
     * @param {Object} $player, object jquery playerAudio.
     * @param {int} timelineWidth, player timeline width.
     * @return {int} position.
     */
    function clickPercent(ev, $player, timelineWidth) {
        var $playerTimeLine = $player.children().filter("[data-player=\"timeline\"]");
        var $playerCursor = $playerTimeLine.children().filter("[data-player=\"cursor\"]");
        var posX = null;

        if (ev.originalEvent.changedTouches) {
            var touch = ev.originalEvent.changedTouches[0];
            posX = touch.pageX;
        } else {
            posX = ev.pageX;
        }

        return ((posX - $playerTimeLine.offset().left - ($playerCursor.width()/2)) * 100) / timelineWidth;
    }

    /**
     * Event click on audio button for play and pause.
     *
     * @param {Object} $player, object jquery playerAudio.
     */
    function playAudio($player) {
        var $source = $player.find("audio");
        var $playerButtonPlay = $player.children().filter("[data-player=\"button-play\"]");
        var img = $playerButtonPlay.find("img")[0];
        var src = img.src;

        if ($source[0].paused) {
            var classList = $player.attr("class").split(/\s+/);
            $($.find("."+classList[0])).each( function() {
                var $_player = $(this);
                var $_source = $_player.find("audio");
                var $_playerButtonPlay = $_player.children().filter("[data-player=\"button-play\"]");
                var _img = $_playerButtonPlay.find("img")[0];
                var _src = _img.src;
                $_source[0].pause();
                _img.src = _src.replace("pause", "play");
            });

            $source[0].play();
            img.src = src.replace("play", "pause");
        } else {
            $source[0].pause();
            img.src = src.replace("pause", "play");
        }
    }

    /**
     * Event click on audio button for stop.
     *
     * @param {Object} $player, object jquery playerAudio.
     */
    function stopAudio($player) {
        var $source = $player.find("audio");

        // Stop the player
        $source[0].pause();
        $source[0].currentTime = 0;

        // Set correct image for play button
        var $playerButtonPlay = $player.children().filter("[data-player=\"button-play\"]");
        var img = $playerButtonPlay.find("img")[0];
        var src = img.src;
        $source[0].pause();
        img.src = src.replace("pause", "play");
    }

    /**
     * Event when mouse down on player cursor.
     *
     * @param {Object} $player, object jquery playerAudio.
     * @param {int} timelineWidth, player timeline width.
     */
    function onPlayerCursorMouseDown($player, timelineWidth) {
        var $source = $player.find("audio");

        // unbind
        var moveCursor = true;
        $source.unbind("timeupdate");

        // events
        var evtMove = "mousemove touchmove";
        var evtEnd = "mouseup touchend";
        $player.bind(evtMove, function(ev) {
            ev.preventDefault();
            movePlayerCursor(ev, $player, timelineWidth);
        });
        $player.bind(evtEnd, function(ev) {
            ev.preventDefault();
            if (moveCursor) {
                $player.unbind(evtMove);
                movePlayerCursor(ev, $player, timelineWidth);
                $source.on({
                    timeupdate: function() {
                        onTimerUpdate($player, timelineWidth);
                    }
                });
            }
            moveCursor = false;
        });
    }

    /**
     * Move player cursor, when mouse down.
     *
     * @params {Object} ev: Event object.
     * @param {Object} $player, object jquery playerAudio.
     * @param {int} timelineWidth, player timeline width.
     */
    function movePlayerCursor(ev, $player, timelineWidth) {
        var $source = $player.find("audio");
        var $playerTimeLine = $player.children().filter("[data-player=\"timeline\"]");
        var $playerCursor = $playerTimeLine.children().filter("[data-player=\"cursor\"]");
        var duration = $source[0].duration;
        var posX = null;

        if (ev.originalEvent.changedTouches) {
            var touch = ev.originalEvent.changedTouches[0];
            posX = touch.pageX;
        } else {
            posX = ev.pageX;
        }

        var newMargLeft = posX - $playerTimeLine.offset().left - ($playerCursor.width()/2);
        if (newMargLeft >= 0 && newMargLeft <= timelineWidth) {
            $playerCursor.css("margin-left", newMargLeft + "px");
            $source[0].currentTime = (duration * clickPercent(ev, $player, timelineWidth)) / 100;
            onTimerUpdate($player, timelineWidth);
        } else if (newMargLeft < 0) {
            $playerCursor.css("margin-left", "0px");
        } else {
            $playerCursor.css("margin-left", timelineWidth + "px");
        }
    }


    /**********************************************************************
     *                          Plug-in main function
     *********************************************************************/

    return $this.each( function() {
        var $player = $(this);
        var hasPlayOneOnce = false;
        var $source = $player.find("audio");

        // Can play type
        var canPlayType = false;
        $source.find("source").each( function() {
            var ext = this.src.split(".").pop();
            var type = "";
            switch (ext) {
                case "mp3":
                    type = "audio/mpeg";
                    break;
                case "ogg":
                    type = "audio/ogg";
                    break;
                case "m4a":
                case "aac":
                    type = "audio/aac";
                    break;
                case "wav":
                    type = "audio/wav";
                    break;
                case "webm":
                    type = "audio/webm";
                    break;
            }
            if ($source[0].canPlayType(type) !== "") {
                canPlayType = true;
                return false;
            }
            return true;
        });
        if (!canPlayType) {
            $source.parent().children().each(function() {
                var $this = $(this);
                $this.addClass("hidden");
                $this.children().addClass("hidden");
            });
            $source.parent().text("(Audio format not supported)");
            return $player;
        }

        // Configure
        var timelineWidth = configure($player);


        /**********************************************************************
         *                              Events
         *********************************************************************/

        var $playerDuration = $player.children().filter("[data-player=\"duration\"]");
        var $playerButtonPlay = $player.children().filter("[data-player=\"button-play\"]");
        var $playerButtonStop = $player.children().filter("[data-player=\"button-stop\"]");
        var $playerTimeLine = $player.children().filter("[data-player=\"timeline\"]");
        var $playerCursor = $playerTimeLine.children().filter("[data-player=\"cursor\"]");

        // Source event
        $source.on({
            canplaythrough: function() {
                audioMetaData($player);
            },
            loadedmetadata: function() {
                audioMetaData($player);
            },
            ended: function() {
                var img = $playerButtonPlay.find("img")[0];
                var src = img.src;
                img.src = src.replace("pause", "play");
            },
            timeupdate: function() {
                onTimerUpdate($player, timelineWidth);
            }
        });

        // Timeline event
        $playerTimeLine.click( function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var duration = $source[0].duration;
            $source[0].currentTime = (duration * clickPercent(ev, $player, timelineWidth)) / 100;
        });

        // Player buttons click event
        $playerButtonPlay.click( function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            hasPlayOneOnce = true;
            playAudio($player);
        });
        if ($playerButtonStop) {
            $playerButtonStop.click( function(ev) {
                ev.preventDefault();
                ev.stopPropagation();
                stopAudio($player);
            });
        }

        // PLayer cursor event
        var evtStart = "mousedown touchstart";
        $playerCursor.bind(evtStart, function(ev) {
            if (!hasPlayOneOnce)
                return;
            onPlayerCursorMouseDown($player, timelineWidth);
        });
    });
};


}(jQuery));
