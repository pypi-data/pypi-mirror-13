/**
 * @projectDescription publiquiz.js
 * Javascript for quiz on library jquery, define namespace publiquiz,
 * publiquiz.action and publiquiz.question
 *
 * @author prismallia.fr
 * @version 0.1
 * $Id: publiquiz.js 998083592483 2016/01/26 16:19:04 Tien $
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
/*global setTimeout: true */
/*global clearTimeout: true */


(function ($) {

"use strict";

/*****************************************************************************
 *                  Define namespace publiquiz if not exist
 ****************************************************************************/

if (!$.publiquiz)
    $.publiquiz = {};


/*****************************************************************************
 *                  Define defaults options
 ****************************************************************************/

$.publiquiz.defaults =  {
    prefix: "pquiz",
    verifyDuration: 0,
    timerValidation: 0,
    // wrongAnswers can be set to "color", "clear" or "correct"
    wrongAnswers: "color"
};


/*****************************************************************************
 *                  Define namespace publiquiz.action
 ****************************************************************************/

$.publiquiz.action = {

    /**
     * Method call when click on validate button.
     *
     * @param {Object} $action, jquery Object action.
     */
    validate: function($action) {
        var $this = this;
        var scenario = $action.scenario.validate;
        var acts = scenario[$action.idxValidate];
        if (!acts)
            return;

        $this.doActions($action, "validate", acts);
    },

    /**
     * Method call when click on verify button.
     *
     * @param {Object} $action, jquery Object action.
     */
    verify: function($action) {
        var $this = this;
        var scenario = $action.scenario.verify;
        var acts = scenario[$action.idxVerify];
        if (!acts)
            return;

        $this.doActions($action, "verify", acts);
    },

    /**
     * Method call when click on retry button.
     *
     * @param {Object} $action, jquery Object action.
     */
    retry: function($action) {
        var $this = this;
        var scenario = $action.scenario.retry;
        var acts = scenario[$action.idxRetry];
        if (!acts)
            return;

        $this.doActions($action, "retry", acts);
    },

    /**
     * Method call when click on redo button.
     *
     * @param {Object} $action, jquery Object action.
     */
    redo: function($action) {
        var $this = this;
        var scenario = $action.scenario.redo;
        var acts = scenario[$action.idxRetry];
        if (!acts)
            return;

        $this.doActions($action, "redo", acts);
    },

    /**
     * Method call when click on show user answer button.
     *
     * @param {Object} $action, jquery Object action.
     */
    userAnswer: function($action) {
        var $this = this;
        var scenario = $action.scenario.userAnswer;
        var acts = scenario[$action.idxUserAnswer];
        if (!acts)
            return;

        $this.doActions($action, "userAnswer", acts);
    },

    /**
     * Method call when click on show right answer button.
     *
     * @param {Object} $action, jquery Object action.
     */
    rightAnswer: function($action) {
        var $this = this;
        var scenario = $action.scenario.rightAnswer;
        var acts = scenario[$action.idxRightAnswer];
        if (!acts)
            return;

        $this.doActions($action, "rightAnswer", acts);
    },


    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Action library function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Hide element by this id.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} funcName, name of function to call.
     * @param {Array} acts, array of actions.
     */
    doActions: function($action, funcName, acts) {
        var $this = this;
        var args = "";
        $(acts).each( function() {
            var actName = this.match(new RegExp("^([^(]+)"));
            if (!actName)
                return true;
            actName = actName[0];
            var actArgs = this.replace(actName, "")
                                .replace("(", "")
                                .replace(")", "")
                                .replace(/ /g, "");
            if (actArgs)
                actArgs = actArgs.split(",");
            else
                actArgs = [];

            if (actName === "validate") {
                $this.actionValidate($action);
            } else if (actName === "retry") {
                $this.actionRetry($action);
            } else if (actName === "redo") {
                $this.actionRedo($action);
            } else if (actName === "showMessage") {
                $this.actionShowMessage($action);
            } else if (actName === "answerText") {
                $this.actionAnswerText($action);
            } else if (actName === "rightAnswer") {
                $this.actionRightAnswer($action);
            } else if (actName === "userAnswer") {
                $this.actionUserAnswer($action);
            } else if (actName === "score") {
                $this.actionScore($action);
            } else if (actName === "userColor") {
                $this.actionUserColor($action);
            } else if (actName === "rightColor") {
                $this.actionRightColor($action);
            } else if (actName === "fullColor") {
                $this.actionFullColor($action);
            } else if (actName === "hide") {
                $this.actionHide($action, actArgs);
            } else if (actName === "show") {
                $this.actionShow($action, actArgs);
            } else if (actName === "goto") {
                return $this.actionGoTo($action, funcName, actArgs);
            } else if (actName === "set") {
                $this.actionSet($action, actArgs);
            } else if (actName === "setif") {
                $this.actionSetIf($action, actArgs);
            } else if (actName === "timerAnswerColor") {
                $this.actionTimerAnswerColor($action);
            } else {
                $this.actionCustom($action, actName, actArgs);
            }

            return true;
        });
    },

    /**
     * Action custom, use for manage customs action.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} actName, action name.
     * @param {Array} actArgs, action args.
     */
    actionCustom: function($action, actName, actArgs) {
        console.log("This action is not defined, used method 'actionCustom' for manage it: '" + actName + "'");
    },

    /**
     * Hide element by this id.
     *
     * @param {Object} $action, jquery Object action.
     * @param {Array} args, list of argument.
     */
    actionHide: function($action, args) {
        if (!args)
            return;

        var prefix = $.publiquiz.defaults.prefix;
        $.each(args, function() {
            var elemName = this;
            $action.find("."+prefix+elemName).addClass("hidden");
        });
    },

    /**
     * Show element by this id.
     *
     * @param {Object} $action, jquery Object action.
     * @param {Array} args, list of argument.
     */
    actionShow: function($action, args) {
        var prefix = $.publiquiz.defaults.prefix;
        $.each(args, function() {
            var elemName = this;
            $action.find("."+prefix+elemName).removeClass("hidden");
        });
    },

    /**
     * Action validate
     *
     * @param {Object} $action, jquery Object action.
     */
    actionValidate: function($action) {
        var $questions = $action.questions;

        // Call publiquiz plugin function
        $questions.publiquiz("disable");
        $questions.publiquiz("insertUserAnswers");
    },

    /**
     * Action retry
     *
     * @param {Object} $action, jquery Object action.
     */
    actionRetry: function($action) {
        var prefix = $.publiquiz.defaults.prefix;
        var $questions = $action.questions;
        $action.nbRetryQuiz -= 1 ;

        // Hide message
        $action.find("."+prefix+"GlobalMessage").hide();

        // Call publiquiz plugin function
        $questions.publiquiz("retry");
        $questions.publiquiz("enable");
    },

    /**
     * Action redo
     *
     * @param {Object} $action, jquery Object action.
     */
    actionRedo: function($action) {
        location.reload(true);
    },

    /**
     * Action show message, display message by score.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionShowMessage: function($action) {
        // Get score
        var prefix = $.publiquiz.defaults.prefix;
        var res = $.publiquiz.question.computeGlobalScore($action.questions);
        var percent = (res.score*100)/res.total;

        // Get the good message
        $action.find("."+prefix+"Message").each( function() {
            var $message = $(this);
            var range = $message.data("score-range").split("-");
            if (percent >= range[0] && percent <= range[1]) {
                // Get text without children text
                var text = $message.clone().children().remove().end().text().trim();
                text = text.split("|");
                // Random display text
                var rnd = 0;
                if (text.length > 1)
                    rnd = Math.floor(Math.random() * text.length);
                // Audio
                var $audioMessages = $message.find("."+prefix+"AudioMessage");
                if ($audioMessages.length > 0) {
                    var $audioMessage = $($audioMessages[rnd]);
                    var $audio = $audioMessage.find("audio");
                    if ($audio.length > 0)
                        $audio[0].play();
                }
                // Display message
                var $gMessage = $action.find("."+prefix+"GlobalMessage");
                var $container = $gMessage.find("."+prefix+"GlobalMessageContent");
                var $txt = $container.find("."+prefix+"GlobalMessageText");
                if ($txt.length === 0 ) {
                    $txt = $("<div>")
                        .addClass(prefix+"GlobalMessageText");
                    $container.append($txt);
                }
                $txt.text(text[rnd].trim());
                $gMessage.show();
                return false;
            }
            return true;
        });
    },

    /**
     * Action answer text, display fieldset "answerText".
     *
     * @param {Object} $action, jquery Object action.
     */
    actionAnswerText: function($action) {
        $action.questions.publiquiz("textAnswer");
    },

    /**
     * Action right answer, display right answer of quiz.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionRightAnswer: function($action) {
        $action.questions.publiquiz("quizAnswer", "_correct");
    },

    /**
     * Action user answer, display user answer of quiz.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionUserAnswer: function($action) {
        $action.questions.publiquiz("quizAnswer", "_user");
    },

    /**
     * Action timer answer color, display user answer, and replace
     * them one by one with the correct answer, and color.
     *
     * @param [Object} $action, jQuery Object action.
     */
    actionTimerAnswerColor: function($action) {
        $action.questions.publiquiz("quizTimerAnswerColor");
    },

    /**
     * Action score
     *
     * @param {Object} $action, jquery Object action.
     */
    actionScore: function($action) {
        $.publiquiz.question.displayGlobalScore($action);
    },

    /**
     * Action user color, verify user answer set color for right and false answer.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionUserColor: function($action) {
        $action.questions.publiquiz("verifyUserAnswer");
    },

    /**
     * Action full color, color only right answer.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionRightColor: function($action) {
        $action.questions.publiquiz("verifyRightAnswer");
    },

    /**
     * Action full color, color right and false answer for quiz.
     *
     * @param {Object} $action, jquery Object action.
     */
    actionFullColor: function($action) {
        $action.questions.publiquiz("verifyFullAnswer");
    },

    /**
     * Go to specific position of scenario.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} func, name of function to call.
     * @param {Array} args.
     * @return bool
     */
    actionGoTo: function($action, funcName, args) {
        if (args.length != 3)
            return false;

        var $this = this;
        var condition = args[0];
        var res = $.publiquiz.question.computeGlobalScore($action.questions);
        var percent = (res.score*100)/res.total;

        if (condition === "maxRetry") {
            if (!$this.conditionMaxRetry($action, funcName, args))
                return true;
            if (funcName === "validate") {
                $this.validate($action);
                return false;
            }
        } else if (condition.match("^scoreEq")) {
            if (!$this.conditionScoreEq($action, funcName, args, percent))
                return true;
            if (funcName === "validate") {
                $this.validate($action);
                return false;
            }
        }

        return true;
    },

    /**
     * Action set, set variable to specific index.
     *
     * @param {Object} $action, jquery Object action.
     * @param {Array} args.
     */
    actionSet: function($action, args) {
        if (args.length != 2)
            return;
        var funcName = args[0];
        var idx = args[1];
        if (funcName === "" || idx === "")
            return;

        var $this = this;
        if (funcName === "validate")
            $action.idxValidate = parseInt(idx, 10);
    },

    /**
     * Action Set if, set variable to specific index with condition.
     *
     * @param {Object} $action, jquery Object action.
     * @param {Array} args.
     */
    actionSetIf: function($action, args) {
        if (args.length != 4)
            return;

        var $this = this;
        var condition = args[0];
        var funcName = args[1];
        var nok = args[2];
        var ok = args[3];

        if (condition === "maxRetry")
            $this.conditionMaxRetry($action, funcName, [condition, nok, ok]);
    },

    /**
     * Test condition max retry.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} func, name of function to call.
     * @param {Array} args.
     * @return bool
     */
    conditionMaxRetry: function($action, funcName, args) {
        var nok = args[1];
        var ok = args[2];
        if (ok === "" || nok === "")
            return false;

        var res = $.publiquiz.question.computeGlobalScore($action.questions);
        var score = res.score;
        var total = res.total;

        var nbRetryQuiz = $action.nbRetryQuiz;
        var idx = -1;
        if (nbRetryQuiz <= 0 || score == total) {
            if (ok == "none")
                return false;

            idx = parseInt(ok, 10);
            if (funcName === "validate" && idx >= 0) {
                $action.idxValidate = idx;
                return true;
            }
            return false;
        } else {
            if (nok == "none")
                return false;
            idx = parseInt(nok, 10);
            if (funcName === "validate" && idx >= 0) {
                $action.idxValidate = idx;
                return true;
            }
            return false;
        }
    },

    /**
     * text condition score equiv to specific percent.
     *
     * @param {Object} $action, jquery Object action.
     * @param {String} func, name of function to call.
     * @param {Array} args.
     * @param {Float} quiz score in percent.
     * @return bool
     */
    conditionScoreEq: function($action, funcName, args, percent) {
        var nok = args[1];
        var ok = args[2];
        if (ok === "" || nok === "")
            return false;

        var idx = -1;
        var p = parseInt(args[0].replace("scoreEq", ""), 10);
        if (p == percent) {
            if (ok == "none")
                return false;
            idx = parseInt(ok, 10);
            if (funcName === "validate" && idx >= 0) {
                $action.idxValidate = idx;
                return true;
            }
            return false;
        } else {
            if (nok == "none")
                return false;
            idx = parseInt(nok, 10);
            if (funcName === "validate" && idx >= 0) {
                $action.idxValidate = idx;
                return true;
            }
            return false;
        }
    }

};


/*****************************************************************************
 *                  Define namespace publiquiz.question
 ****************************************************************************/

$.publiquiz.question = {

    /**
     * Define variables for register function.
     */
    enable: {},
    disable: {},
    configure: {},
    help: {},
    retry: {},
    textAnswer: {},
    insertUserAnswers: {},
    quizAnswer: {},
    quizTimerAnswerColor: {},
    verifyUserAnswer: {},
    verifyRightAnswer: {},
    verifyFullAnswer: {},
    computeScore: {},
    quizScore: {},
    scoreFunc: {},

    // Référence au tableau contenant les timer pour la fonction "verify"
    timers: [],

    /**
     * Register function score by quiz id.
     *
     * @param {String} quzId, id of quiz.
     * @param {Object} $quiz, object jquery quiz.
     * @param {OBject} func, functions for compute score.
     */
    registerScoreFunc: function(quzId, $quiz, func) {
        this.scoreFunc[quzId] = {quiz: $quiz, func: func};
    },

    /**
     * Register function.
     *
     * @param {String} engine: type of engine apply function.
     * @param {Dictionnary} functions: function we want register.
     */
    register: function(engine, functions) {
        var $this = this;
        $.each(functions, function(key, func) {
            switch (key) {
                case ("enable"):
                    $this.enable[engine] = func;
                    break;
                case ("disable"):
                    $this.disable[engine] = func;
                    break;
                case ("configure"):
                    $this.configure[engine] = func;
                    break;
                case ("help"):
                    $this.help[engine] = func;
                    break;
                case ("retry"):
                    $this.retry[engine] = func;
                    break;
                case ("textAnswer"):
                    $this.textAnswer[engine] = func;
                    break;
                case ("insertUserAnswers"):
                    $this.insertUserAnswers[engine] = func;
                    break;
                case ("quizAnswer"):
                    $this.quizAnswer[engine] = func;
                    break;
                case ("quizTimerAnswerColor"):
                    $this.quizTimerAnswerColor[engine] = func;
                    break;
                case ("verifyUserAnswer"):
                    $this.verifyUserAnswer[engine] = func;
                    break;
                case ("verifyRightAnswer"):
                    $this.verifyRightAnswer[engine] = func;
                    break;
                case ("verifyFullAnswer"):
                    $this.verifyFullAnswer[engine] = func;
                    break;
                case ("computeScore"):
                    $this.computeScore[engine] = func;
                    break;
                case ("quizScore"):
                    $this.quizScore[engine] = func;
                    break;
                default:
                    console.log("Namespace publiquiz unknown function: '"+key+"' for engine: '"+engine+"'");
            }
        });
    },


    /**********************************************************************
     *                          Quiz Ui function
     *********************************************************************/

    /**
     * Add drag on item.
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $item : jQuery object item.
     * @params {String} suffix : String suffix class name.
     */
    setDraggableItem: function($quiz, $item, suffix) {
        if ($item.length === 0)
            return;
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var evtStart = "mousedown touchstart";
        var evtMove = "mousemove touchmove";
        var evtEnd = "mouseup touchend";

        if ($item.find("img").length > 0)
            $item.find("img").on("dragstart", function(ev) { ev.preventDefault(); });

        $item.each( function() {
            var $itm = $(this);
            if ($itm.find("."+prefix+"AudioPlayer").length > 0)
                $itm.find("."+prefix+"AudioPlayer").css("margin", "2em");
        });

        $item.bind(evtStart, function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var $target = $(ev.target);
            if ($target[0].tagName.toLowerCase() == "img" &&
                    $target.parent().data("player") == "button-play") {
                return;
            }
            while (!$target.hasClass(prefix+suffix+"Item"))
                $target = $target.parent();
            $this.clearVerify();
            $target.addClass("dragging");
            var $ghost = $this.makeGhost($target, ev);
            var $dropbox = null;
            $(document).bind(evtMove, function(e) {
                if (!$target.hasClass("dragging"))
                    return;
                e.preventDefault();
                $dropbox = $this.dragItem($quiz, $ghost, suffix, e);
            });
            $(document).bind(evtEnd, function(e) {
                if (!$target.hasClass("dragging"))
                    return;
                $ghost.remove();
                $this.dropItem($quiz, $dropbox, $target, suffix);
                $dropbox = null;
            });
        });
    },

    /**
     * Helper, drag item and return a valide dropbox object.
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $ghost : jQuery object ghost.
     * @params {String} suffix : String suffix class name.
     * @params {Event} ev : Object event.
     * @return Object dropbox.
     */
    dragItem: function($quiz, $ghost, suffix, ev) {
        var $this = this;
        var $dropbox = null;
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        $quiz.find("."+prefix+suffix+"Drop").removeClass("dragOver mipDragOver");

        var pos = $this.eventPosition($ghost, ev);
        $ghost.css("left", (pos[0] - $ghost.width())+"px");
        $ghost.css("top", (pos[1] - $ghost.height())+"px");

        var bodyHeight = $(document).height();
        var scrollHeight = $(window).scrollTop();
        var pageHeight = $(window).height();
        var elemPosY = pos[1]+$ghost.height();
        if (elemPosY > (pageHeight+scrollHeight)) {
            var offset = elemPosY - (pageHeight+scrollHeight);
            window.scrollTo(0, scrollHeight+offset);
        }

        var pointX = pos[0];
        var pointY = pos[1] - scrollHeight;
        var $elementOver = $(document.elementFromPoint(pointX, pointY));
        if ($elementOver.length === 0)
            return $dropbox;
        if ($elementOver[0] == $ghost[0] ||
                ($elementOver.parent().hasClass(prefix+suffix+"Item") &&
                    $elementOver.parent()[0] == $ghost[0]) ||
                ($elementOver.parent().data("player") == "button-play" &&
                    $elementOver.parent().parent().parent()[0] == $ghost[0])) {
            $ghost.css("display", "none");
            $elementOver = $(document.elementFromPoint(pointX, pointY));
            $ghost.css("display", "block");
        }

        if ($elementOver.parent().hasClass(prefix+suffix+"Item"))
            $elementOver = $elementOver.parent();

        var dropId = $elementOver.attr("id");
        if ($elementOver.attr("class") && $elementOver.attr("class").search(prefix+suffix+"Drop") > -1) {
            dropId = dropId.substring(0, dropId.length - 4);
            if (dropId == quzId) {
                $dropbox = $elementOver;
                if (engine == "mip")
                    $dropbox.addClass("mipDragOver");
                else
                    $dropbox.addClass("dragOver");
            }
        } else if ($elementOver.hasClass(prefix+suffix+"Item") && $elementOver.parent().hasClass(prefix+suffix+"Drop")) {
            dropId = dropId.substring(0, dropId.length - 8);
            if (dropId == quzId) {
                $dropbox = $elementOver.parent();
                if (engine == "mip")
                    $dropbox.addClass("mipDragOver");
                else
                    $dropbox.addClass("dragOver");
            }
        } else {
            $dropbox = null;
        }

        return $dropbox;
    },

    /**
     * Helper, drop item.
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $dropbox : jQuery object dropbox.
     * @params {Object} $item : jQuery object item.
     * @params {String} suffix : String suffix class name.
     */
    dropItem: function($quiz, $dropbox, $item, suffix) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var evtStart = "mousedown touchstart";
        var evtMove = "mousemove touchmove";
        var evtEnd = "mouseup touchend";

        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                    $quiz.data("engine-options").search("multiple") > -1 )
                isMultiple = true;

        $quiz.find("."+prefix+suffix+"Drop").removeClass("dragOver mipDragOver");
        $item.removeClass("dragging");

        // On remet l'item dans la boite a items
        if ($dropbox === null) {
            if ($item.parent().hasClass(prefix+suffix+"Drop")) {
                if (engine != "categories" && engine != "mip")
                    $item.parent().text(".................");
                $this.cancelItemDrop($quiz, $item, suffix);
            }
            $(document).unbind(evtMove);
            $(document).unbind(evtEnd);
            return;
        }

        // Si le block a déjà un element, on enlève celui en place
        if (engine != "categories") {
            var $itm = $dropbox.find("."+prefix+suffix+"Item");
            if ($itm.length > 0)
                $this.cancelItemDrop($quiz, $itm, suffix);

            // Si l'ancien emplacement de l'item était un pquizDrop
            if ($item.parent().hasClass(prefix+suffix+"Drop") && engine != "mip")
                $item.parent().text(".................");
        } else {
            // On vérifie que la boite de drop n'as pas encore l'item
            var find = $dropbox.find("."+prefix+suffix+"Item").filter("[data-item-value=\""+$item.data("item-value")+"\"]");
            if (isMultiple && find.length > 0) {
                $dropbox.removeClass("dragOver");
                if ($item.parent().hasClass(prefix+suffix+"Drop")) {
                    $item.remove();
                } else {
                    $item.unbind(evtStart);
                    $(document).unbind(evtMove);
                    $(document).unbind(evtEnd);
                    $this.setDraggableItem($quiz, $item, suffix);
                    $this.setAudioPlayable($quiz, $item);
                }
                return;
            }
        }

        // On déplace l'item dans la dropbox
        $item.unbind(evtStart);
        $(document).unbind(evtMove);
        $(document).unbind(evtEnd);
        var count = 0;
        if (engine == "blanks-color") {
            var color = $item.find("."+prefix+"ItemColor").css("background-color");
            $dropbox.css("fill", color);
            $dropbox.data("choice-value", $item.data("item-value"));
            $this.setDraggableItem($quiz, $item, suffix);
            $this.setAudioPlayable($quiz, $item);
        } else if (engine == "categories") {
            $dropbox.removeClass("dragOver");
            if (isMultiple && $item.parent().hasClass(prefix+"CategoriesItems")) {
                count = $quiz.find("."+prefix+suffix+"Item").length;
                $this.setDraggableItem($quiz, $item, suffix);
                $this.setAudioPlayable($quiz, $item);
                $item = $item.clone();
                $item.attr("id", quzId+"_item"+$this.formatNumber(count += 100, 3));
            }
            $item.appendTo($dropbox)
                .addClass(prefix+"CategoryItemDropped");
            $dropbox.find("."+prefix+suffix+"Item").removeClass("dragOver");
            $this.setDraggableItem($quiz, $item, suffix);
            $this.setAudioPlayable($quiz, $item);
        } else {
            $dropbox.text("");
            $dropbox.removeClass("dragOver");
            if (isMultiple && $item.parent().hasClass(prefix+suffix+"Items")) {
                count = $quiz.find("."+prefix+suffix+"Item").length;
                $this.setDraggableItem($quiz, $item, suffix);
                $this.setAudioPlayable($quiz, $item);
                $item = $item.clone();
                $item.attr("id", quzId+"_item"+$this.formatNumber(count += 100, 3));
            }
            $item.appendTo($dropbox)
                   .addClass(prefix+"ItemDropped");
            $this.setDraggableItem($quiz, $item, suffix);
            $this.setAudioPlayable($quiz, $item);

            // Specific par type d'engine
            if (engine == "sort" && $item.children("img").length > 0)
                $item.addClass(prefix+"InlineItemImageDropped");
            else if (engine == "matching" && $item.children("img").length > 0)
                $item.addClass(prefix+"BlockItemImageDropped");
            else if (engine == "mip") {
                $item.addClass(prefix+"ItemImageDropped");
                $item.each( function() {
                    var $itm = $(this);
                    $itm.find("audio").each( function() {
                        var $audioPlayer = $(this).parent();
                        if ($audioPlayer.attr("class").indexOf("AudioPlayer") >= 0) {
                            $audioPlayer.css("margin-right", "");
                        }
                    });
                });
            }
        }
    },

    /**
     * Helper, get event position (mouse or touch).
     *
     * @params {Object} $target : jQuery object.
     * @params {Event} ev : Object event.
     * @return Array: position X/Y, original position
     */
    eventPosition: function($target, ev) {
        var posX = null;
        var posY = null;

        if (ev.originalEvent.changedTouches) {
            var touch = ev.originalEvent.changedTouches[0];
            posX = touch.pageX;
            posY = touch.pageY;
        } else {
            posX = ev.pageX;
            posY = ev.pageY;
        }

        return [posX, posY];
    },

    /**
     * Helper, make ghost of item touch.
     *
     * @params {Object} $target : jQuery object.
     * @params {Event} ev : Object event.
     * @return Object ghost.
     */
    makeGhost: function($target, ev) {
        var $this = this;
        var $ghost = $target.clone();
        var pos = $this.eventPosition($target, ev);

        // Specific when we are in opener
        if ($target.children("img").length > 0) {
            $ghost.children("img").css("width", $target.children("img").css("width"));
            $ghost.children("img").css("height", $target.children("img").css("height"));
        }

        $ghost.appendTo($("body"));
        $ghost.css("opacity", "0.25");
        $ghost.css("position", "absolute");
        $ghost.css("left", (pos[0] - $ghost.width())+"px");
        $ghost.css("top", (pos[1] - $ghost.height())+"px");
        $ghost.css("height", "initial");
        return $ghost;
    },

    /**
     * Helper, cancel a item dropped.
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $item : jQuery object item.
     * @params {String} suffix : String suffix class name.
     */
    cancelItemDrop: function($quiz, $item, suffix) {
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 ) {
            $item.remove();
            return;
        }

        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var evtStart = "mousedown touchstart";
        var evtMove = "mousemove touchmove";
        var evtEnd = "mouseup touchend";

        $item.removeClass(prefix+"ItemDropped " +
                prefix+"CategoryItemDropped " +
                prefix+"ItemImageDropped " +
                prefix+"InlineItemImageDropped " +
                prefix+"BlockItemImageDropped")
            .appendTo($quiz.find("#"+quzId+"_items"));
        $item.unbind(evtStart);
        $(document).unbind(evtMove);
        $(document).unbind(evtEnd);
        $this.setDraggableItem($quiz, $item, suffix);
        $this.setAudioPlayable($quiz, $item);
    },

    /**
     * Set enable player audio after drop it
     *
     * @params {Object} $quiz : jQuery object quiz.
     * @params {Object} $item : jQuery object item.
     */
    setAudioPlayable: function($quiz, $item) {
        $item.find("audio").each( function() {
            var $audioPlayer = $(this).parent();
            if ($audioPlayer.attr("class").indexOf("AudioPlayer") >= 0) {
                $audioPlayer.unbind();
                $audioPlayer.find("[data-player='duration']").unbind();
                $audioPlayer.find("[data-player='button-play']").unbind();
                $audioPlayer.find("[data-player='timeline']").unbind();
                $audioPlayer.find("[data-player='cursor']").unbind();

                $audioPlayer.player({
                    timeLineWidth: 300
                });
            }
        });
    },

    /**
     * Function call for display/hide help
     *
     * @param {Object} $quiz, object jquery quiz.
     */
    displayHelp: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var $hlp = $quiz.find("#"+quzId+"_help-slot");

        if ($hlp.hasClass(prefix+"HelpPopUp")) {
            if ($hlp.hasClass("hidden"))
                $hlp.removeClass("hidden");
            else
                $hlp.addClass("hidden");

            var width = $("body").width()/2;
            var posX = width - (width/2);
            var posY = ($(window).height()/2) - ($hlp.height()/2) - $hlp.parent().position().top + $(document).scrollTop();
            $hlp.css({
                "top": posY+"px",
                "width": width+"px",
                "margin-left": posX+"px"
            });
        } else {
            if ($hlp.css("display") == "none")
                $hlp.slideDown("slow");
            else
                $hlp.slideUp("slow");
        }
    },

    /**
     * Display quiz text answer.
     *
     * @param {Object} quiz.
     */
    displayTextAnswer: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var $answer = $quiz.find("#"+quzId+"_answer-slot");
        if ($answer.length > 0)
            $answer.slideDown("slow");
    },

    /**
     * Hide quiz text answer.
     *
     * @param {Object} quiz.
     */
    hideTextAnswer: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var $answer = $quiz.find("#"+quzId+"_answer-slot");
        if ($answer.length > 0 && $answer.css("display") != "none")
            $answer.slideUp("slow");
    },


    /**********************************************************************
     *                          Quiz retry function
     *********************************************************************/

    /**
     * Retry quiz choices, keep only right answer.
     *
     * @param {Object} quiz.
     * @params {String} suffix : suffix string for select object.
     */
    retryChoices: function($quiz, suffix) {
        var $this = this;
        $this.clearVerify();
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        var quzId = $quiz.data("quiz-id");
        var res = $this.correction($quiz.find("#"+quzId+"_correct"));

        if (isCheckRadio && engine != "pointing") {
            var $engine = $quiz.find("#"+quzId+"_engine");

            // Get group
            var choices = [];
            $quiz.find("."+prefix+"Choice").each( function() {
                var group = $(this).data("group");
                if ($.inArray(group, choices) < 0 )
                    choices.push(group);
            });

            // Keep only right choice
            $.each(choices, function() {
                var group = this;
                var $item = null;
                if (res[group] && $engine.find("."+prefix+"Choice")
                                    .filter("[data-group=\""+group+"\"]")
                                    .filter("[data-name=\"false\"]")
                                    .hasClass("selected")) {
                    $item = $engine.find("."+prefix+"Choice")
                                    .filter("[data-group=\""+group+"\"]")
                                    .filter("[data-name=\"false\"]");
                    $item.find("input").prop("checked", false);
                    $item.removeClass("selected");
                } else if (!res[group] && $engine.find("."+prefix+"Choice")
                                    .filter("[data-group=\""+group+"\"]")
                                    .filter("[data-name=\"true\"]")
                                    .hasClass("selected")) {
                    $item = $engine.find("."+prefix+"Choice")
                                    .filter("[data-group=\""+group+"\"]")
                                    .filter("[data-name=\"true\"]");
                    $item.find("input").prop("checked", false);
                    $item.removeClass("selected");
                }
            });
        } else {
            $quiz.find("."+prefix+suffix).each( function() {
                var $elem = $(this);
                var _id = $elem.attr("id");
                var key = _id.substring(_id.length - 3, _id.length);

                if ($elem.hasClass("selected") && !(key in res)) {
                    $elem.find("input").prop("checked", false);
                    $elem.removeClass("selected");
                }
            });
        }
    },

    /**
     * Retry quiz blanks, keep only right answer.
     *
     * @param {Object} quiz.
     */
    retryBlanks: function($quiz) {
        var $this = this;
        $this.clearVerify();
        var engine = $quiz.data("engine");
        if (engine == "blanks-fill") {
            var quzId = $quiz.data("quiz-id");
            var prefix = $quiz.data("prefix");
            var isStrict = false;
            var options = [];
            if ($quiz.data("engine-options") &&
                    $quiz.data("engine-options").search("strict") > -1 ) {
                isStrict = true;
                var opts = $quiz.data("engine-options").replace("strict", "").trim();
                if (opts !== "")
                    options = opts.split(" ");
            }

            var res = $this.correction($quiz.find("#"+quzId+"_correct"));
            $.each(res, function(key, value) {
                var $item = $quiz.find("#"+quzId+"_"+key);
                var data = $item.val().trim();

                if (!$this.isValideBlanksFillAnswer(data, value, isStrict, options))
                    $item.val("");

            });
        } else {
            $this.retryQuizCmp($quiz);
        }
    },

    /**
     * Retry quiz pointing category, keep only right answer.
     *
     * @param {Object} quiz.
     */
    retryPointingCategory: function($quiz) {
        var $this = this;
        $this.clearVerify();
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var res = $this.correctionCategories($quiz.find("#"+quzId+"_correct"));

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            var pointId = $point.data("choice-id");
            if (category && res[category].search(pointId) == -1) {
                var classList = $point.attr("class").split(/\s+/);
                if (classList.length > 1)
                    $point.removeClass(classList[classList.length - 1]);
            }

        });
    },

    /**
     * Retry quiz categories, keep only right answer.
     *
     * @param {Object} quiz.
     */
    retryCategories: function($quiz) {
        var $this = this;
        $this.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var res = $this.correctionCategories($quiz.find("#"+quzId+"_correct"));

        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 ) {
            $quiz.find("."+prefix+"Choice").each( function() {
                var $choice = $(this);
                var value = $choice.data("choice-value").toString();
                if (isMultiple) {
                    $choice.find("."+prefix+"ItemColor").each( function() {
                        var $item = $(this);
                        var category = $item.data("category-id");
                        if (category && $.inArray(value, res[category].split("|")) == -1)
                            $item.remove();
                    });
                } else {
                    var category = $choice.data("category-id");
                    if (category && $.inArray(value, res[category].split("|")) == -1) {
                        var classList = $choice.attr("class").split(/\s+/);
                        if (classList.length > 1)
                            $choice.removeClass(classList[classList.length - 1]);
                    }
                }
            });
        } else {
            var $items = $quiz.find("#"+quzId+"_items");
            $.each(res, function(key, value) {
                var $dropbox = $quiz.find("#"+quzId+"_"+key);
                var values = value.split("|");
                $dropbox.find("."+prefix+"CategoryItem").each( function() {
                    var $item = $(this);
                    var data = $item.data("item-value").toString();
                    if ($.inArray(data, values) == -1) {
                        if (isMultiple)
                            $item.remove();
                        else
                            $item.appendTo($items).removeClass(prefix+"CategoryItemDropped");
                    }
                });
            });
        }
    },

    /**
     * Retry quiz engine compared mode check.
     *
     * @params {Object} $quiz : Object jquery quiz.
     */
    retryQuizCmp: function($quiz) {
        var $this = this;
        $this.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var $items = $quiz.find("#"+quzId+"_items");

        var res;
        if (engine == "mip")
            res = $this.correctionCategories($quiz.find("#"+quzId+"_correct"));
        else
            res = $this.correction($quiz.find("#"+quzId+"_correct"));

        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0 && $item.data("item-value") != value ) {
                if (isMultiple) {
                    $item.remove();
                } else {
                    $item.removeClass(prefix+"ItemDropped "+
                        prefix+"ItemImageDropped " +
                        prefix+"InlineItemImageDropped " +
                        prefix+"BlockItemImageDropped")
                        .appendTo($items);
                }

                if (engine != "mip")
                    $dropbox.text(".................");
            }
        });
    },


    /**********************************************************************
     *                  Quiz insert user anwer function
     *********************************************************************/

    /**
     * Insert user answers in html for quiz compare
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} suffix : suffix string for select object.
     */
    insertUserAnswersQuizChoices: function($quiz, suffix) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = "";

        $quiz.find("."+prefix+suffix+".selected").each( function() {
            var $item = $(this);
            var _id = $item.attr("id");
            _id = _id.substring(_id.length - 3, _id.length) + "x";
            if (answer !== "")
                answer += "::";
            answer += _id;
        });

        $this.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Insert user answers in html for quiz drop
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    inserUserAnswersQuizDrop: function ($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = "";

        $quiz.find("."+prefix+"Drop").each( function() {
            var $dropbox = $(this);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                var value = $item.data("item-value");
                if (answer !== "")
                    answer += "::";
                var id = $dropbox.attr("id");
                answer += id.substring(id.length - 3, id.length) + value;
            }
        });

       $this.writeUserAnswers($quiz, quzId, answer);
    },


    /**********************************************************************
     *                          Quiz score function
     *********************************************************************/

    /**
     * Show quiz score.
     */
    displayQuizScore: function($quiz) {
    },

    /**
     * Show global score for specific action and questions.
     *
     * @params {Object} $action : object jquery publiquiz action.
     */
    displayGlobalScore: function($action) {
        var result = this.computeGlobalScore($action.questions);
        var score = result.score;
        var total = result.total;

        if (total === 0)
            return;

        var prefix = $.publiquiz.defaults.prefix;
        var baseScore = -1;
        var baseScoreElem = $action.find("."+prefix+"BaseScore");
        if (baseScoreElem.length > 0)
            baseScore = parseInt(baseScoreElem.text(), 10);

        if (baseScore > -1) {
            score = (score * baseScore) / total.toFixed(1);
            score = Math.round(score);
            total = baseScore;
        }

        var $gScoreElem = $action.find("."+prefix+"GlobalScore");
        $gScoreElem.text(score + " / " + total);
        $gScoreElem.removeClass("hidden");
    },

    /**
     * Compute score for specific questions.
     *
     * @params {Object} $questions : array of object jquery publiquiz.
     * @return {Dictionnary}.
     */
    computeGlobalScore: function($questions) {
        var $this = this;
        var score = 0.0;
        var total = 0;
        $questions.each( function(){
            var $quiz = $(this);
            var quzId = $quiz.data("quiz-id");
            var res = $this.scoreFunc[quzId].func($quiz);
            score += res.score;
            total += res.total;
        });
        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine choices mode radio.
     *
     * @param {Object} jquery Object quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizChoicesRadio: function($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var total = 1;
        var score = 0;
        var correct = true;
        var res = $this.correction($quiz.find("#"+quzId+"_correct"));
        $.each(res, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if (! $item.hasClass("selected")) {
                correct = false;
                return false;
            }
            return false;
        });
        if (correct)
            score = 1;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine choices mode check.
     * Le score se calcule par rapport au poids de la réponse, la réponse
     * fausse vaut toujours '-1' point.
     *
     * @param {Object} jquery Object quiz.
     * @params {String} suffix : suffix string for select object.
     * @return {Dictionnary}.
     */
    scoreForQuizChoicesCheck: function($quiz, suffix) {
        var $this = this;
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var score = 0.0;
        var total = $quiz.find("."+prefix+suffix).length;
        var res = $this.correction($quiz.find("#"+quzId+"_correct"));

        // On determine le poids d'une reponse correcte
        var weight_correct = total / Object.keys(res).length;

        $quiz.find("."+prefix+suffix).each( function() {
            var $elem = $(this);
            var _id = $elem.attr("id");
            var key = _id.substring(_id.length - 3, _id.length);

            if ($elem.hasClass("selected") && key in res)
                score += weight_correct;
            else if ($elem.hasClass("selected") && !(key in res))
                score -= 1;
        });

        score = Math.round(score);
        if (score < 0)
            score = 0;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine compared mode check.
     * the mode explain how compute score.
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizCmpCheck: function($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var res = $this.correction($quiz.find("#"+quzId+"_correct"));

        var total = 0;
        total = $quiz.find("."+prefix+"Drop").length;
        var score = 0;

        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0 && $item.data("item-value") == value)
                score += 1;
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine compared mode radio.
     * the mode explain how compute score.
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizCmpRadio: function($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var total = 1;
        var score = 0;
        var correct = true;
        var res = $this.correction($quiz.find("#"+quzId+"_correct"));

        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length === 0) {
                correct = false;
                return false;
            }
            if ($item.data("item-value") != value) {
                correct = false;
                return false;
            }
            return null;
        });

        if (correct)
            score = 1;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Score for quiz engine "pointin-categories".
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    scoreForQuizPointingCategories: function($quiz) {
        var $this = this;
        var result = {};
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            result.score = 0;
            result.total = 0;
            return result;
        }

        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var score = 0;
        var total = 0;
        var res = $this.correctionCategories($quiz.find("#"+quzId+"_correct"));

        $.each(res, function(key, value) {
            total += value.split("|").length;
        });

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            var pointId = $point.data("choice-id");
            if (category && res[category].search(pointId) > -1)
                score += 1;
            else if (category && res[category].search(pointId) == -1)
                score -= 1;
        });

        if (score < 0)
            score = 0;

        result.score = score;
        result.total = total;
        return result;
    },


    /**********************************************************************
     *                      Quiz verify function
     *********************************************************************/

    /**
     * Suppression des informations de verification du quiz
     */
    clearVerify: function() {
        $.each($.publiquiz.question.timers, function() {
            clearTimeout(this);
        });
        $('.animated').finish();
        $('.publiquizAction').finish();
        $($.find(".answer")).removeClass("answer");
        $($.find(".answerKo")).removeClass("answerKo");
        $($.find(".answerOk")).removeClass("answerOk");
    },

    /**
     * Verify answer for quiz qcm.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    verifyQuizChoicesAnswer: function($quiz, mode) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;
        var timerValidation = $.publiquiz.defaults.timerValidation;
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;

        var rightAnswers = $this.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $this.correction($quiz.find("#"+quzId+"_user"));

        if (isCheckRadio && engine != "pointing") {
            var $engine = $quiz.find("#"+quzId+"_engine");

            // Get group
            var choices = [];
            $quiz.find("."+prefix+"Choice").each( function() {
                var group = $(this).data("group");
                if ($.inArray(group, choices) < 0 )
                    choices.push(group);
            });

            // Verify user answer
            $.each(choices, function() {
                var group = this;
                var $choices = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]");
                if (rightAnswers[group]) {
                    var $true = $choices.filter("[data-name=\"true\"]");
                    var $false = $choices.filter("[data-name=\"false\"]");
                    if ($true.hasClass("selected")) {
                        $.publiquiz.question.addClassColorAnswer($quiz, $true, true);
                    }
                    else if ($false.hasClass("selected")) {
                        $.publiquiz.question.addClassColorAnswer($quiz, $false, false);
                    }
                }
                else {
                    var $true = $choices.filter("[data-name=\"true\"]");
                    var $false = $choices.filter("[data-name=\"false\"]");
                    if ($false.hasClass("selected")) {
                        $.publiquiz.question.addClassColorAnswer($quiz, $false, true);
                    }
                    else if ($true.hasClass("selected")) {
                        $.publiquiz.question.addClassColorAnswer($quiz, $true, false);
                    }
                }
                $('.publiquizAction').delay(timerValidation);
            });

        } else {
            var suffix = "Choice";
            if (engine == "pointing")
                suffix = "Point";
            var inputs = $quiz.find("."+prefix+suffix);
            if (mode == "user" || mode == "right")
                inputs = inputs.filter('.selected');

            inputs.each( function() {
                var $item = $(this);
                var key = $item.attr("id");
                key = key.substring(key.length - 3, key.length);
                if (mode == "user") {
                    var valid = rightAnswers[key];
                    $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                    if (!valid && paramWrongAnswers == "clear") {
                        $('.publiquizAction').queue(function(next) {
                            $item.find("input").prop("checked", false);
                            $item.removeClass("selected answerKo");
                            next();
                        });
                    }
                    $('.publiquizAction').delay(timerValidation);
                } else if (mode == "right") {
                    if (rightAnswers[key])
                        $item.addClass("answerOk");
                } else {
                    if (isCheckRadio || engine == "choices-radio") {
                        if (rightAnswers[key] && userAnswers[key])
                            $item.addClass("answerOk");
                        else if (rightAnswers[key] && !userAnswers[key])
                            $item.addClass("answerKo");
                    } else {
                        if (rightAnswers[key] == userAnswers[key])
                            $item.addClass("answerOk");
                        else
                            $item.addClass("answerKo");
                    }
                }
            });

        }

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($this.clearVerify, duration);
            $this.timers.push(timer);
        }
    },

    /**
     * Verify user answer for quiz cmp.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    verifyQuizCmpAnswer: function($quiz, mode) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var rightAnswers = $this.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $this.correction($quiz.find("#"+quzId+"_user"));
        var $items = $quiz.find("#"+quzId+"_items");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var timerValidation = $.publiquiz.defaults.timerValidation;
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;
        $.each(rightAnswers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                var valid;
                if (mode == "user") {
                    valid = $item.data("item-value") == value;
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, valid);
                    if (!valid && paramWrongAnswers == "clear") {
                        $('.publiquizAction').queue(function(next) {
                            if (isMultiple) {
                                $item.remove();
                            }
                            else {
                                $item.removeClass(prefix+"ItemDropped "+
                                                  prefix+"ItemImageDropped " +
                                                  prefix+"InlineItemImageDropped " +
                                                  prefix+"BlockItemImageDropped")
                                    .animateMoveElement($items);
                            }
                            $dropbox.text(".................");
                            $dropbox.removeClass("answerKo");
                            next();
                        });
                    }
                    $('.publiquizAction').delay(timerValidation);
                } else if (mode == "right") {
                    if ($item.data("item-value") == value)
                        $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, true);
                } else {
                    valid = userAnswers[key] && userAnswers[key] == value;
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, valid);
                }
            }
        });

        if (mode == "user")
            return;

        // Gestion des intrus
        var userValues = [];
        var rightValues = [];

        $.each(userAnswers, function(key, value) { userValues.push(value); });
        $.each(rightAnswers, function(key, value) {
            if( $.inArray(value.toString(), rightValues) == -1)
                rightValues.push(value);
        });

        $quiz.find("#"+quzId+"_items")
                .find("."+prefix+"Item").each( function() {
            var $item = $(this);
            var value = $item.data("item-value").toString();

            // S'il y a plusieurs etiquette de meme valeur dans la correction on les cache
            if ($.inArray(value, rightValues) >= 0)
                $item.addClass("hidden");

            if (mode == "right") {
                if ($.inArray(value, rightValues) < 0)
                    $item.addClass("answerOk");
            } else {
                if ($.inArray(value, userValues) >= 0 && $.inArray(value, rightValues) < 0)
                    $item.addClass("answerKo");
                else
                    $item.addClass("answerOk");
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($this.clearVerify, duration);
            $this.timers.push(timer);
        }
    },


    /**********************************************************************
     *                      Quiz correction function
     *********************************************************************/

    /**
     * Display right/user answer for quiz qcm.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} suffix : suffix string for select object.
     * @params {String} mode : mode "correct" or "user".
     */
    displayQuizChoicesAnswer: function($quiz, suffix, mode) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");

        var isModeRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isModeRadio = true;

        // Reset quiz
        $quiz.find("."+prefix+suffix+" input").prop("checked", false);
        $quiz.find("."+prefix+suffix).removeClass("selected answerOk answerKo");

        // Display pquizChoice selected
        var answers = $this.correction($quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if (mode == "_correct")
            userAnswers = $this.correction($quiz.find("#"+quzId+"_user"));

        $quiz.find("."+prefix+suffix).each( function() {
            var $item = $(this);
            var key = $item.attr("id");
            key = key.substring(key.length - 3, key.length);
            if (answers[key]) {
                $item.addClass("selected");

                // If Input set checked
                $item.find("input").prop("checked", true);
            }
        });
    },

    /**
     * Display correct answer one by one for quiz qcm.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} suffix : suffix string for select object.
     */
    displayQuizChoicesTimerAnswerColor: function($quiz, suffix) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var timerValidation = $.publiquiz.defaults.timerValidation;
        var answers = $this.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $this.correction($quiz.find("#"+quzId+"_user"));

        $quiz.find("."+prefix+suffix).each( function() {
            var $item = $(this);
            var key = $item.attr("id");
            key = key.substring(key.length - 3, key.length);
            $.publiquiz.question.addClassColorAnswer($quiz, $item, (answers[key] == userAnswers[key]));
            $('.publiquizAction').queue(function(next) {
                if (answers[key]) {
                    $item.addClass("selected");
                    $item.find("input").prop("checked", true);
                }
                else {
                    $item.removeClass("selected");
                    $item.find("input").prop("checked", false);
                }
                next();
            });
            $('.publiquizAction').delay(timerValidation);
        });
    },

    /**
     * Display right/user answer for quiz drag and drop.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : mode "correct" or "user".
     */
    displayQuizCmpAnswer: function($quiz, mode) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $this.correction($quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if(mode == "_correct")
            userAnswers = $this.correction($quiz.find("#"+quzId+"_user"));

        // On vide les champs
        $quiz.find("."+prefix+"Drop").each( function() {
            var $dropbox = $(this);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                if (isMultiple) {
                    $item.remove();
                } else {
                    $item.removeClass(prefix+"ItemDropped "+
                        prefix+"InlineItemImageDropped " +
                        prefix+"BlockItemImageDropped")
                        .appendTo($quiz.find("#"+quzId+"_items"));
                }
                $dropbox.text(".................")
                    .removeClass("answerOk answerKo");
            }
        });

        var $items = $quiz.find("#"+quzId+"_items");
        $items.find("."+prefix+"Item").removeClass("answerKo answerOk hidden");

        // On place la correction en deplacant les items
        $.each(answers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $items.find("."+prefix+"Item").filter("[data-item-value=\""+value+"\"]");
            if ($item.length > 1)
                $item = $($item[0]);
            if (isMultiple)
                $item = $item.clone();
            $dropbox.text("");
            $item.appendTo($dropbox)
                .addClass(prefix+"ItemDropped");

            // Specific par type d'engine
            if (engine == "sort" && $item.children("img").length > 0)
                $item.addClass(prefix+"InlineItemImageDropped");
            else if (engine == "matching" && $item.children("img").length > 0)
                $item.addClass(prefix+"BlockItemImageDropped");
        });
    },

    /**
     * Display one by one correct answers with color.
     *
     * @param {Object} $quiz : object jQuery quiz.
     */
    displayQuizCmpTimerAnswerColor: function($quiz) {
        var $this = this;
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $this.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $this.correction($quiz.find("#"+quzId+"_user"));

        var $items = $quiz.find("#"+quzId+"_items");
        $items.find("."+prefix+"Item").removeClass("answerKo answerOk hidden");

        var timerValidation = $.publiquiz.defaults.timerValidation;
        $.each(answers, function(key, value) {
            var valid = false;
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $quiz.find("."+prefix+"Item").filter("[data-item-value=\""+value+"\"]");
            if ($item.length > 1)
                $item = $($item[0]);

            if (userAnswers[key]) {
                if (userAnswers[key] == value) {
                    valid = true;
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, true);
                }
                else {
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, false);
                    delete userAnswers[key];
                    $('.publiquizAction').queue(function(next) {
                        var $oldItem = $dropbox.find("."+prefix+"Item");
                        if (isMultiple) {
                            $oldItem.remove();
                        } else {
                            $oldItem.removeClass(prefix+"ItemDropped "+
                                                 prefix+"InlineItemImageDropped " +
                                                 prefix+"BlockItemImageDropped")
                                .animateMoveElement($items);
                        }
                        $dropbox.text(".................");
                        next();
                    });
                }
            }
            else {
                $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, false);
            }

            if (!valid) {
                var $oldDropbox;
                if (!isMultiple && $.publiquiz.question.valueInAnswers(value, userAnswers)) {
                    $oldDropbox = $item.parent();
                    var oldKey = $oldDropbox.attr('id').substring((quzId+"_").length);
                    delete userAnswers[oldKey];
                }
                $('.publiquizAction').queue(function(next) {
                    if (isMultiple)
                        $item = $item.clone().insertBefore($item);
                    $dropbox.text("");
                    $item.animateMoveElement($dropbox)
                        .queue(function(next) {
                            $item.addClass(prefix+"ItemDropped");
                            // Specific par type d'engine
                            if (engine == "sort" && $item.children("img").length > 0)
                                $item.addClass(prefix+"InlineItemImageDropped");
                            else if (engine == "matching" && $item.children("img").length > 0)
                                $item.addClass(prefix+"BlockItemImageDropped");
                            next();
                        });
                    if ($oldDropbox) {
                        $oldDropbox.text(".................");
                    }
                    next();
                });
            }
            $('.publiquizAction').delay(timerValidation);
        });
    },

    /**
     * Display right/user answer for quiz engine blanks-fill.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @params {String} mode : display correct/user answer.
     */
    displayQuizAnswerBlanksFill: function($quiz, mode) {
        var $this = this;
        var prefix = $quiz.data("prefix");

        // On vide les champs
        $quiz.find("."+prefix+"Choice").each( function() {
            var $item = $(this);
            $item.val("");
            $item.removeClass("answerOk answerKo");
        });

        var quzId = $quiz.data("quiz-id");
        var isStrict = false;
        var options = [];
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("strict") > -1 ) {
            isStrict = true;
            var opts = $quiz.data("engine-options").replace("strict", "").trim();
            if (opts !== "")
                options = opts.split(" ");
        }
        var answers = $this.correction($quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if(mode == "_correct")
            userAnswers = $this.correction($quiz.find("#"+quzId+"_user"));
        $.each(answers, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if ($item.length > 0) {
                // Set text
                var data = value.split("|").join(" / ");
                data = data.replace(new RegExp(/_/g), " ");
                $item.val(data);
            }
        });
    },


    /**********************************************************************
     *                          Quiz library function
     *********************************************************************/

    /**
     * Shuffle items.
     *
     * @params {Object} $items : object jquery items.
     */
    shuffleItems: function($items) {
        $items.each( function() {
            var $container = $(this);
            var shuffle = $container.hasClass("shuffle");
            if (!shuffle)
                $container.shuffle();
        });
    },

    /**
     * Shuffle items and control not give the right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {Array} dropzones : array of drop zone.
     * @params {Dict} res : dict of correction of quiz.
     * @return bool
     */
    shuffleAndControlItems: function($quiz, $dropzones, res) {
        var prefix = $quiz.data("prefix");
        var answer = true;
        var count = 0;
        
        if ($.isEmptyObject(res))
            return false;

        $.publiquiz.question.shuffleItems($quiz.find("."+prefix+"Items"));
        var items = $quiz.find("."+prefix+"Item");
        $dropzones.each(function() {
            var $dropzone = $(this);
            var $item = $(items[count]);
            var dropId = $dropzone.attr("id");
            dropId = dropId.substring(dropId.length - 3, dropId.length);
            if (res[dropId] != $item.data("item-value")) {
                answer = false;
                return false;
            }
            count ++;   
        });

        return answer;
    },

    /**
     * Get the correction of quiz in dico.
     *
     * @param {Object} $elem, object contain correction.
     * @return {Dictionnary} the result is in a dico.
     */
    correction: function ($elem) {
        var res = {};
        var data = $elem.text().trim();
        if (!data)
            return res;
        data = data.replace(/(\r\n|\n|\r)/gm,"");
        $.each(data.split("::"), function() {
            var value = this;
            if (value && value.length > 0) {
                var k = value.substring(0, 3);
                var v = value.substring(3, value.length);
                res[k] = v;
            }
        });
        return res;
    },

    /**
     * Get the correction of quiz categories in dico.
     *
     * @param {Object} $elem, object contain correction.
     * @return {Dictionnary} the result is in a dico.
     */
    correctionCategories: function($elem){
        var res = {};
        var data = $elem.text();
        if (!data)
            return res;
        data = data.replace(/(\r\n|\n|\r)/gm,"");
        $.each(data.split("::"), function(idx, value) {
            if (value && value.length > 0) {
                value = value.trim();
                var key = value.substring(0, 3);
                var data = value.substring(3, value.length);
                if ($.inArray(key, Object.keys(res)) >= 0 )
                    data = res[key] + "|" + data;
                res[key] = data;
            }
        });

        return res;
    },

    /**
     * Write user answer in DOM.
     *
     * @param {Object} quiz.
     * @param {String} quiz id.
     * @param {String} user answer.
     */
    writeUserAnswers: function($quiz, quzId, answer) {
        var $userAnswer = $quiz.find("#"+quzId+"_user");
        if ($userAnswer.length === 0) {
            var prefix = $quiz.data("prefix");
            var engine = $quiz.data("engine");
            var $quizAnswer = null;
            if (engine != "production")
                $quizAnswer = $quiz.find("#"+quzId+"_correct");
            else
                $quizAnswer = $quiz.find("."+prefix+"Production");

            $userAnswer = $("<div>")
                    .attr("id", quzId+"_user")
                    .addClass("hidden");
            $userAnswer.insertAfter($quizAnswer);
        }
        $userAnswer.text(answer);
    },

    /**
     * Helper, function contruct string for compare.
     *
     * @param {String} text origin.
     * @params {Boolean} isStrict : mode strict or not.
     * @params {Array} options : strict options.
     * @return {String} text for compare.
     */
    constructCmpString: function(text, isStrict, options) {
        var r = text.trim(); // TODO: rewrite.
        r = r.replace("-", " - ");
        r = r.replace("+", " + ");
        r = r.replace("/", " / ");
        r = r.replace("*", " * ");
        r = r.replace("=", " = ");
        r = r.replace(new RegExp(/æ/g),"ae");
        r = r.replace(new RegExp(/œ/g),"oe");
        r = r.replace(new RegExp(/\s{2,}/g),"");

        if (!isStrict) {
            r = r.toLowerCase();
            r = r.replace(new RegExp(/\s/g),"");
            r = this.removePunctuation(r);
            r = this.removeAccent(r);
            return r;
        }

        if ($.inArray("total", options) > -1 || options.length < 1)
            return r;

        if ($.inArray("accent", options) == -1)
            r = this.removeAccent(r);

        if ($.inArray("punctuation", options) == -1)
            r = this.removePunctuation(r);

        if ($.inArray("upper", options) == -1)
            r = r.toLowerCase();

        return r;
    },

    removePunctuation: function(text) {
        return text.replace(new RegExp(/[\.,#!?$%\^&;:{}\_`~()]/g)," ");
    },

    removeAccent: function(text) {
        var r = text.replace(new RegExp(/[àáâ]/g),"a");
        r = r.replace(new RegExp(/ç/g),"c");
        r = r.replace(new RegExp(/[èéê]/g),"e");
        r = r.replace(new RegExp(/[îï]/g),"i");
        r = r.replace(new RegExp(/[ùúû]/g),"u");
        return r;
    },

    /**
     * Helper, use for validate user answer for engine blanks-fill.
     *
     * @params {String} userAnswer : answer of player.
     * @params {String} rightAnswer : the right answer.
     * @params {Boolean} isStrict : mode strict or not.
     * @params {Array} options : strict options.
     * @return {Boolean}.
     */
    isValideBlanksFillAnswer: function (userAnswer, rightAnswer, isStrict, options) {
        var $this = this;
        if (!userAnswer)
            userAnswer = "";

        userAnswer = $this.constructCmpString(userAnswer, isStrict, options);
        userAnswer = userAnswer.split("/")[0];

        var answer = [];
        $.each(rightAnswer.split("|"), function() {
            var txt = this;
            txt = $this.constructCmpString(txt, isStrict, options);
            answer.push(txt);
        });

        if ($.inArray(userAnswer, answer) > -1)
            return true;

        return false;
    },

    /**
     * Helper, function format number "3" -> "003".
     *
     * @param {String} str, number to format.
     * @return {Int} max, length max of format.
     */
    formatNumber: function (str, max) {
        str = str.toString();
        return str.length < max ? this.formatNumber("0" + str, max) : str;
    },

    /**
     * Add color class to answers.
     * If timerValidation is set, classes are toggle multiple times
     * before stopping on the Ok or Ko class.
     *
     * @param {Object} $quiz, jQuery object publiquiz.
     * @param {Object} $item, jQuery item to add class on.
     * @param {Boolean} right, True if answer is valid.
     */
    addClassColorAnswer: function($quiz, $item, right) {
        $('.publiquizAction').queue(function(next) {
            if (right)
                $item.addClass("answerOk");
            else
                $item.addClass("answerKo");
            next();
        });

        var timer = $.publiquiz.defaults.timerValidation;
        if (timer > 0) {
            var toggle = function() {
                if (!$item.hasClass("answerOk") && !$item.hasClass("answerKo"))
                    $item.addClass("answerOk");
                else if ($item.hasClass("answerOk"))
                    $item.removeClass("answerOk").addClass("answerKo");
                else
                    $item.removeClass("answerKo");
            };

            for (var i=0; i<6; i++) {
                $('.publiquizAction').delay(100).queue(function(next) { toggle(); next(); });
            }

            var $sound = $('#validation_' + (right?'right':'wrong'));
            if ($sound.length > 0) {
                $('.publiquizAction').queue(function(next) {
                    $sound[0].pause();
                    $sound[0].currentTime = 0;
                    $sound[0].play();
                    next();
                }).delay($sound[0].duration*1000);
            }
        }
    },

    /**
     * Helper, to know device.
     */
    isIosDevice: function() {
        if (navigator.userAgent.match(/iPhone|iPad|iPod/i))
            return true;
        return false;
    },

    isAndroidDevice: function() {
        if (navigator.userAgent.match(/Android/i))
            return true;
        return false;
    },

    isBlackBerryDevice: function() {
        return navigator.userAgent.match(/BlackBerry/i);
    },

    isWindowsDevice: function() {
        if (navigator.userAgent.match(/IEMobile/i))
            return true;
        return false;
    },

    isOperaDevice: function() {
        if (navigator.userAgent.match(/Opera Mini/i))
            return true;
        return false;
    },

    valueInAnswers: function(value, answers) {
        for (var prop in answers) {
            if (answers.hasOwnProperty(prop) && answers[prop] == value)
                return true;
        }
        return false;
    }
};

}(jQuery));


/******************************************************************************
 *
 *                                  Plugin shuffle
 *
******************************************************************************/

(function ($) {

"use strict";

/**
 * To shuffle all <li> elements within each '.member' <div>:
 * $(".member").shuffle("li");
 *
 * To shuffle all children of each <ul>:
 * $("ul").shuffle();
*/
$.fn.shuffle = function(selector) {
    var $elems = selector ? $(this).find(selector) : $(this).children(),
        $parents = $elems.parent();

    $parents.each(function(){
        $(this).children(selector).sort(function() {
            return Math.round(Math.random()) - 0.5;
        }).detach().appendTo(this);
    });

    return this;
};

/**
 * To shuffle an array
*/
$.shuffle = function(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
    return array;
};

})(jQuery);


/******************************************************************************
 *
 *                           Plugin animate moving element
 *
******************************************************************************/

(function ($) {

"use strict";

/**
 * Animate moving element to new parent in page.
 *
 * @param {Object} $newParent : Destination.
 * @return {Object} The element, to enable chaining.
 */
$.fn.animateMoveElement = function($newParent) {
    var $item = this;
    var $clone = $item.clone().insertAfter($item);
    $item.appendTo('body');
    var cloneOffset = $clone.offset();
    $item
        .css('position', 'absolute')
        .css('left', cloneOffset.left)
        .css('top', cloneOffset.top)
        .css('zIndex', 1000);
    $clone.appendTo($newParent);
    cloneOffset = $clone.offset();
    // $clone.css('visibility', 'hidden');
    $clone.hide();
    $item.addClass("animated");
    $item.animate({
        'top': cloneOffset.top,
        'left': cloneOffset.left
    }, 'slow', function(){
        $clone.remove();
        $item.removeClass("animated");
        $item.appendTo($newParent);
        $item
            .css('position', '')
            .css('left', '')
            .css('top', '')
            .css('zIndex', '');
    });

    return $item;
};

}(jQuery));
