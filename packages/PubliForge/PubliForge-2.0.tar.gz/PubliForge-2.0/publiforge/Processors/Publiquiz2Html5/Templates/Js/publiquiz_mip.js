/**
 * @projectDescription publiquiz_basics.js
 * Plugin jQuery for quiz choices.
 *
 * @author prismallia.fr
 * @version 0.1
 * $Id: publiquiz_mip.js 529bc5b6ce5e 2016/01/26 15:18:20 Sylvain $
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


/******************************************************************************
 *
 *                                  Mip
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.question.mip = {

    /**
     * Configure quiz.
     */
    mipConfigure: function($quiz) {
    },

    /**
     * Set event click.
     *
     * @param {Object} jquery Object quiz.
     */
    mipEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "draggable" on item
        $.publiquiz.question.setDraggableItem($quiz, $quiz.find("."+prefix+"Item"), "");
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    mipDisable: function($quiz) {
        var prefix = $quiz.data("prefix");

        var evtStart = "mousedown touchstart";
        var $items = $quiz.find("."+prefix+"Item");
        $items.unbind(evtStart);
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    mipHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    mipRetry: function($quiz) {
        $.publiquiz.question.retryQuizCmp($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    mipComputeScore: function($quiz) {
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

        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var total = 0;
        var score = 0;
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        $.each(res, function(key, value) {
            total++;
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                var data = $item.data("item-value");
                if (data == value)
                    score += 1;
            } else if ($item.length === 0 && value === "") {
                score += 1;
            }
        });

        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    mipScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    mipTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    mipInsertUserAnswers: function($quiz) {
        var answer = "";
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Drop").each( function() {
            var $dropbox = $(this);
            var key = $dropbox.attr("id");
            key = key.substring(key.length - 3, key.length);
            $dropbox.find("."+prefix+"Item").each( function() {
                var $item = $(this);
                var value = $item.data("item-value");
                if (answer !== "")
                    answer += "::";
                answer += key + value;
            });
        });

        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    mipQuizAnswer: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        /*var correctionOnly = $quiz.data("display-correction-only");*/
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $.publiquiz.question.correction($quiz.find("#"+quzId+mode));
        var $items = $quiz.find("#"+quzId+"_items");
        var userAnswers = null;
        if(mode == "_correct")
            userAnswers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_user"));

        // On enleve la correction
        if (isMultiple) {
            $quiz.find("."+prefix+"ItemDropped").remove();
        } else {
            $quiz.find("."+prefix+"ItemDropped").each( function() {
                var $item = $(this);
                $item.appendTo($items)
                    .removeClass(prefix+"ItemDropped " +
                        prefix+"ItemImageDropped");
            });
        }

        // On place la correction en deplacant les items
        // ou bien en les clonant si "isMultiple" est a true
        $.each(answers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            $dropbox.text("");
            $dropbox.removeClass("answerOk answerKo");
            var $item = $items.find("."+prefix+"Item").filter("[data-item-value=\""+value+"\"]");
            if (isMultiple)
                $item = $item.clone();
            //if (mode == "_correct") {
            //    if (correctionOnly) {
            //        $dropbox.addClass("answerOk");
            //    } else {
            //        if ((!userAnswers[key] && value !== "") ||
            //            (userAnswers[key] && value === "") ||
            //            (userAnswers[key] && userAnswers[key] != value))
            //            $dropbox.addClass("answerKo");
            //        else
            //            $dropbox.addClass("answerOk");
            //    }
            //}
            $item.appendTo($dropbox)
                .addClass(prefix+"ItemDropped " +
                    prefix+"ItemImageDropped");
        });
    },

    /**
     * Display one by one correct answers for quiz, and color them.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    mipQuizTimerAnswerColor: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        var $items = $quiz.find("#"+quzId+"_items");
        var timerValidation = $.publiquiz.defaults.timerValidation;

        $.each(answers, function(key, value) {
            var valid = false;

            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $quiz.find("."+prefix+"Item").filter("[data-item-value=\""+value+"\"]");
            var $oldItem;
            if ($item.length == 0) {
                $oldItem = $dropbox.find("."+prefix+"Item");
                if ($oldItem.length > 0) {
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, false);
                    $('.publiquizAction').queue(function(next) {
                        if (isMultiple) {
                            $dropbox.find("."+prefix+"ItemDropped").remove();
                        } else {
                            $dropbox.find("."+prefix+"ItemDropped").each( function() {
                                var $item = $(this);
                                $item.removeClass(prefix+"ItemDropped " +
                                                  prefix+"ItemImageDropped")
                                    .animateMoveElement($items);
                            });
                        }
                        next();
                    });
                }
                else {
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, true);
                }
            }
            else {
                if ($item.length > 1)
                    $item = $($item[0]);
                $oldItem = $dropbox.find("."+prefix+"Item");
                if ($oldItem.length > 0) {
                    var data = $oldItem.data("item-value");
                    if (data == value) {
                        valid = true;
                        $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, true);
                    }
                    else {
                        $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, false);
                        $('.publiquizAction').queue(function(next) {
                            if (isMultiple) {
                                $dropbox.find("."+prefix+"ItemDropped").remove();
                            } else {
                                $dropbox.find("."+prefix+"ItemDropped").each( function() {
                                    var $item = $(this);
                                    $item.removeClass(prefix+"ItemDropped " +
                                                      prefix+"ItemImageDropped")
                                        .animateMoveElement($items);
                                });
                            }
                            next();
                        });
                    }
                }
                else {
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, false);
                }
                if (!valid) {
                    $('.publiquizAction').queue(function(next) {
                        if (isMultiple)
                            $item = $item.clone().insertBefore($item);
                        $dropbox.text("");
                        $item.animateMoveElement($dropbox)
                            .queue(function(next) {
                                $item.addClass(prefix+"ItemDropped " +
                                               prefix+"ItemImageDropped");
                                next();
                            });
                        next();
                    });
                }
            }
            $('.publiquizAction').delay(timerValidation);

        });
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    mipVerifyUserAnswer: function($quiz) {
        $.publiquiz.question.mip._verifyAnswer($quiz, "user");
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    mipVerifyRightAnswer: function($quiz) {
        $.publiquiz.question.mip._verifyAnswer($quiz, "right");
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    mipVerifyFullAnswer: function($quiz) {
        $.publiquiz.question.mip._verifyAnswer($quiz, "full");
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * Verify answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode.
     */
    _verifyAnswer: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var rightAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_user"));
        var $items = $quiz.find("#"+quzId+"_items");

        var timerValidation = $.publiquiz.defaults.timerValidation;
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;
        $.each(rightAnswers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            var $item = $dropbox.find("."+prefix+"Item");
            if ($item.length > 0) {
                var data = $item.data("item-value");
                var valid;
                if (mode == "user") {
                    valid = data == value;
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, valid);
                    if (!valid && paramWrongAnswers == "clear") {
                        $('.publiquizAction').queue(function(next) {
                            if (isMultiple) {
                                $item.remove();
                            }
                            else {
                                $item.removeClass(prefix+"ItemDropped " +
                                                  prefix+"ItemImageDropped " +
                                                  prefix+"InlineItemImageDropped " +
                                                  prefix+"BlockItemImageDropped")
                                    .animateMoveElement($items);
                            }
                            $dropbox.removeClass("answerKo");
                            next();
                        });
                    }
                    $('.publiquizAction').delay(timerValidation);
                } else if (mode == "right") {
                    if (data == value)
                        $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, true);
                } else {
                    valid = !((!userAnswers[key] && value !== "") ||
                              (userAnswers[key] && value === "") ||
                              (userAnswers[key] && userAnswers[key] != value));
                    $.publiquiz.question.addClassColorAnswer($quiz, $dropbox, valid);
                }
            }

        });

        var duration = $.publiquiz.defaults.verifyDuration;
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    }
};

// Register function
$.publiquiz.question.register("mip", {
        configure: $.publiquiz.question.mip.mipConfigure,
        enable: $.publiquiz.question.mip.mipEnable,
        disable: $.publiquiz.question.mip.mipDisable,
        help: $.publiquiz.question.mip.mipHelp,
        retry: $.publiquiz.question.mip.mipRetry,
        textAnswer: $.publiquiz.question.mip.mipTextAnswer,
        insertUserAnswers: $.publiquiz.question.mip.mipInsertUserAnswers,
        quizAnswer: $.publiquiz.question.mip.mipQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.mip.mipQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.mip.mipVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.mip.mipVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.mip.mipVerifyFullAnswer,
        computeScore: $.publiquiz.question.mip.mipComputeScore,
        quizScore: $.publiquiz.question.mip.mipScore
    });

}(jQuery));
