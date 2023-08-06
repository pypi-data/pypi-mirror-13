/**
 * @projectDescription publiquiz_blanks_char.js
 * Plugin jQuery for quiz blanks-char.
 *
 * @author prismallia.fr
 * @version 0.1
 * $Id: publiquiz_blanks_char.js 199887c8ebb8 2016/01/25 18:51:32 Sylvain $
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
 *                                  Blanks-char
 *
******************************************************************************/


(function ($) {

"use strict";

$.publiquiz.question.blanksChar = {

    /**
     * Configure quiz.
     */
    blanksConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");

        // On récupère la correction
        var answers = $.publiquiz.question.correction(
                $quiz.find("#"+quzId+"_correct"));

        // On va créer une nouvelle correction
        $.publiquiz.question.blanksChar._makeResult($quiz);

        // On va determiner si on doit enlever les espaces
        var space = false;
        if ($quiz.find("."+prefix+"ItemLetter").filter("[data-item-value=\"space\"]").length > 0)
            space = true;

        // On va placer le texte a remanier par le joueur
        $quiz.find("."+prefix+"Sentence").each( function() {
            var total = 0;
            var position = 0;
            var $sentence = $(this);
            var $childrens = $sentence.contents();
            $childrens.each( function() {
                var $child = $(this);
                if ($child.hasClass(prefix+"Letter")) {
                    total += 1;
                    var text = "";
                    if ($child.data("function") == "lowercase") {
                        text = $child.text().toUpperCase();
                        $child.text(text);
                    } else if ($child.data("function") == "uppercase") {
                        text = $child.text().toLowerCase();
                        $child.text(text);
                    } else if ($child.data("function") == "accent") {
                        text = $.publiquiz.question.removeAccent($child.text());
                        $child.text(text);
                    } else {
                        $child.remove();
                    }
                    $child.data("position", $.publiquiz.question.formatNumber(position ,3));
                    $child.data("value", $child.text());
                    position += 1;
                } else {
                    var value = $child.text();
                    for (var i = 0; i < value.length; i ++) {
                        var letter = value[i];
                        if (space && letter == " ") {
                            total += 1;
                            position += 1;
                            continue;
                        }
                        var $letter = $("<span>").addClass("pquizLetter");
                        $letter.data("position", $.publiquiz.question.formatNumber(position ,3));
                        if (letter == " ") {
                            $letter.data("value", "space");
                            $letter.html("&nbsp;");
                        } else {
                            $letter.data("value", letter);
                            $letter.text(letter);
                        }
                        $letter.insertBefore($child);
                        position += 1;
                    }
                    $child.remove();
                }
            });
            $sentence.data("score-total", total);
        });
    },

    /**
     * Set event click.
     *
     * @param {Object} jquery Object quiz.
     */
    blanksEnable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"ItemLetter").click( function(ev) {
            var $target = $(this);
            $.publiquiz.question.blanksChar._onItemLetter($quiz, $target);
        });
        $quiz.find("."+prefix+"Letter").click( function(ev) {
            var $target = $(this);
            $.publiquiz.question.blanksChar._onLetter($quiz, $target);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"ItemLetter").unbind("click").removeClass("selected");
        $quiz.find("."+prefix+"Letter").unbind("click");
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz, keep only right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksRetry: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");

        $quiz.find("."+prefix+"Sentence").each( function() {
            var $sentence = $(this);
            var id = $sentence.attr("id");
            var key = id.substring(id.length - 3, id.length);

            // On récupère les nouvelles corrections
            var $res = $quiz.find("#"+quzId+"_correct_"+key);
            var answer = $.publiquiz.question.correction($res);
            
            $sentence.find("."+prefix+"Letter").filter(".modified").each( function() {
                var $letter = $(this);
                var value = $letter.data("value");
                var position = null;
                if ($letter.hasClass("letterAdd")) {
                    position = $.publiquiz.question.blanksChar._findLetterPosition($letter);
                    if (!answer[position] || answer[position].length == 1) {
                        // On retire la lettre rajouter mal placer
                        $letter.remove();
                    } else {
                        // On retire la lettre fausse et les lettres suivantes ajoutés
                        if (answer[position] != value) {
                            while ($letter.next().hasClass("letterAdd"))
                                $letter.next().remove();
                            $letter.remove();
                        }
                    }
                } else {
                    position = $letter.data("position");
                    if (answer[position] != value) {
                        // On annule la function poser
                        var txt = $letter.text();
                        var func = $letter.data("function");
                        var itemFunc = $letter.data("item-function");
                        if (func) {
                            if (func == "uppercase")
                                txt = txt.toLowerCase();
                            else  if (func == "lowercase")
                              txt = txt.toUpperCase();
                            else if (func == "accent")
                              txt = $.publiquiz.question.removeAccent(txt);
                        } else {
                            if (itemFunc == "uppercase")
                                txt = txt.toLowerCase();
                            else  if (itemFunc == "lowercase")
                              txt = txt.toUpperCase();
                            else if (itemFunc == "accent")
                              txt = $.publiquiz.question.removeAccent(txt);
                        }

                        $letter.text(txt);
                        $letter.data("value", txt);
                        $letter.data("item-function", "");
                        $letter.removeClass("modified");
                    }
                }
            });
        });
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    blanksComputeScore: function($quiz) {
        var result = {};
        var total = 0;
        var score = 0;

        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");

        $quiz.find("."+prefix+"Sentence").each( function() {
            var $sentence = $(this);
            var id = $sentence.attr("id");
            var key = id.substring(id.length - 3, id.length);
            total += $sentence.data("score-total");

            // On récupère les nouvelles corrections
            var answer = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct_"+key));

            $sentence.find("."+prefix+"Letter").each( function() {
                var $letter = $(this);
                var value = $letter.data("value");
                var position = null;
                if ($letter.hasClass("letterAdd")) {
                    position = $.publiquiz.question.blanksChar._findLetterPosition($letter);
                    if (!answer[position]) {
                        // lettre mal placer
                        score -= 1;
                    } else {
                        var $previousLetter = $letter.prev();
                        if ($previousLetter.hasClass("letterAdd")) {
                            var count = 1;
                            while ($previousLetter.hasClass("letterAdd")) {
                                $previousLetter = $previousLetter.prev();
                                count += 1;
                            }
                            var ok = true;
                            position = $.publiquiz.question.formatNumber(parseInt(position, 10) - count, 3);
                            for (var i = 1; i <= count; i++) {
                                var pos = $.publiquiz.question.formatNumber(parseInt(position, 10) + i, 3); 
                                var _$letter = $letter;
                                value = _$letter.data("value");
                                for (var j = count - i; j > 0; j--) {
                                    _$letter = _$letter.prev();
                                    value = _$letter.data("value");
                                }
                                if (answer[pos] != value) {
                                    ok = false;
                                    break;
                                }
                            }
                            if (ok)
                                score += 1;

                        } else {
                            if (answer[position] == value)
                                score += 1;
                        }
                    }
                } else {
                    position = $letter.data("position");
                    var func = $letter.data("function");
                    if (func) {
                        if (answer[position] == value)
                            score += 1;
                        else if ($letter.hasClass("modified") && answer[position] != value)
                            score -= 1;
                    } else {
                        if (answer[position] != value)
                            score -= 1;
                    }
                }
            });
        });

        if (score < 0)
            score = 0;

        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksInsertUserAnswers: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        $quiz.find("."+prefix+"Sentence").each( function() {
            var $sentence = $(this);
            var id = $sentence.attr("id");
            var key = id.substring(id.length - 3, id.length);
            var position = 0;
            var answer = "";

            $sentence.find("."+prefix+"Letter").each( function() {
                var $letter = $(this);
                if (answer !== "")
                    answer += "::";
                var txt = $letter.text();
                if ($letter.html() == "&nbsp;")
                    txt = "space";
                answer += $.publiquiz.question.formatNumber(position, 3) + txt;
                position += 1;
            });

            var $userAnswer = $quiz.find("#"+quzId+"_user_"+key);
            if ($userAnswer.length === 0) {
                var $quizAnswer = $quiz.find("#"+quzId+"_correct");
                $userAnswer = $("<div>")
                        .attr("id", quzId+"_user_"+key)
                        .addClass("hidden");
                $userAnswer.insertAfter($quizAnswer);
            }
            $userAnswer.text(answer);

        });
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    blanksQuizAnswer: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = "";

        $quiz.find("."+prefix+"Sentence").each( function() {
            var $sentence = $(this);
            var id = $sentence.attr("id");
            var key = id.substring(id.length - 3, id.length);

            // En premier on vide
            $sentence.find("."+prefix+"Letter").remove();

            // Ensuite on replace les lettres suivant le mode
            var answers = $.publiquiz.question.correction($quiz.find("#"+quzId+mode+"_"+key));
            $.each(answers, function(k, value){
                var $letter = $("<span>").addClass("pquizLetter");
                if (value == "space")
                    $letter.html("&nbsp;");
                else
                    $letter.text(value);
                $letter.appendTo($sentence);
            });
        });
    },

    blanksQuizTimerAnswerColor: function($quiz) {
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksVerifyUserAnswer: function($quiz) {
        $.publiquiz.question.blanksChar._verifyAnswer($quiz, "user");
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksVerifyRightAnswer: function($quiz) {
        $.publiquiz.question.blanksChar._verifyAnswer($quiz, "right");
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksVerifyFullAnswer: function($quiz) {
        $.publiquiz.question.blanksChar._verifyAnswer($quiz, "full");
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * Make a  new result, set all position of char.
     *
     * @param {Object} jquery Object quiz.
     */
    _makeResult: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");

        $quiz.find("."+prefix+"Sentence").each( function() {
            var $sentence = $(this);
            var id = $sentence.attr("id");
            var key = id.substring(id.length-3, id.length);
            var $res = $("<div>")
                .attr("id", quzId+"_correct"+"_"+key)
                .addClass("hidden");
            var txt = "";
            var position = 0;
            $sentence.contents().each( function() {
                var $child = $(this);
                if ($child.hasClass(prefix+"Letter")) {
                    if (txt !== "")
                        txt += "::";
                    txt += $.publiquiz.question.formatNumber(position, 3) + $child.text();
                    position += 1;
                } else {
                    var value = $child.text();
                    for (var i = 0; i < value.length; i ++) {
                        var letter = value[i];
                        if (txt !== "")
                            txt += "::";
                        if (letter == " ")
                            letter = "space";
                        txt += $.publiquiz.question.formatNumber(position ,3) + letter;
                        position += 1;
                    }
                }
            });
            $res.text(txt);
            $res.insertAfter($quiz.find("#"+quzId+"_correct"));
        });
    },

    /**
     * This function call when click on item letter.
     *
     * @params {Object} $quiz: object jquery publiquiz.
     * @param {Object} $elem: object jquery receive click.
     */
    _onItemLetter: function($quiz ,$elem) {
        $.publiquiz.question.clearVerify();
        var prefix = $quiz.data("prefix");
        $elem.parent().find("."+prefix+"ItemLetter").removeClass("selected");
        $elem.addClass("selected");
    },

    /**
     * This function call when click on letter.
     *
     * @params {Object} $quiz: object jquery publiquiz.
     * @param {Object} $elem: object jquery receive click.
     */
    _onLetter: function($quiz, $elem) {
        $.publiquiz.question.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $elem.fadeTo("fast",0).fadeTo("fast",1);

        var $selected = $quiz.find("."+prefix+"Items").find(".selected");
        if ($selected.length === 0)
            return;
        var value = $selected.data("item-value");
        var func = $selected.data("item-function");
        var txt = "";
        switch (func) {
            case "uppercase":
                txt = $elem.text();
                txt = txt.toUpperCase();
                $elem.text(txt);
                $elem.data("value", txt);
                $elem.data("item-function", func);
                $elem.addClass("modified");
                break;
            case "lowercase":
                txt = $elem.text();
                txt = txt.toLowerCase();
                $elem.text(txt);
                $elem.data("value", txt);
                $elem.data("item-function", func);
                $elem.addClass("modified");
                break;
            case "accent":
                if ($.publiquiz.question.removeAccent($elem.text()) == $.publiquiz.question.removeAccent(value)){
                    $elem.text(value);
                    $elem.data("value", value);
                    $elem.data("item-function", func);
                    $elem.addClass("modified");
                }
                break;
            case "delete":
                if ($elem.hasClass("letterAdd")) {
                    $elem.remove();
                } else if ($elem.hasClass("modified")) {
                    var f = $elem.data("item-function");
                    if (f == "accent") {
                        txt = $.publiquiz.question.removeAccent($elem.text());
                        $elem.text(txt);
                        $elem.data("value", txt);
                        $elem.data("item-function", "");
                        $elem.removeClass("modified");
                    }
                }
                break;
            default:
                $.publiquiz.question.blanksChar._onAddLetter($quiz, $elem, $selected);
        }
    },

    /**
     * This function call for add a letter.
     *
     * @params {Object} $quiz: object jquery publiquiz.
     * @param {Object} $elem: object jquery letter clicked.
     * @param {Object} $selected: object jquery item letter selected.
     */
    _onAddLetter: function($quiz ,$elem, $selected) {
        var value = $selected.data("item-value");

        var $letter = $("<span>").addClass("pquizLetter letterAdd modified");
        $letter.data("value", value);
        if (value=="space") {
            $letter.html("&nbsp;");
        } else {
            var txt = $selected.text();
            $letter.text(txt);
        }

        $letter.insertAfter($elem);
        $letter.fadeTo("fast",0).fadeTo("fast",1);
        $letter.click( function(ev) {
            var $target = $(this);
            $.publiquiz.question.blanksChar._onLetter($quiz, $target);
        });
    },

    /**
     * Verify answer.
     *
     * @param {Object} $quiz: object jquery publiquiz.
     * @param {String} mode: user, right or full.
     */
    _verifyAnswer: function($quiz, mode) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");

        $quiz.find("."+prefix+"Sentence").each( function() {
            var $sentence = $(this);
            var id = $sentence.attr("id");
            var key = id.substring(id.length - 3, id.length);

            // On récupère les nouvelles corrections
            var $res = $quiz.find("#"+quzId+"_correct_"+key);
            var answer = $.publiquiz.question.correction($res);

            // On vérifie
            $sentence.find("."+prefix+"Letter").each( function() {
                var $letter = $(this);
                var value = $letter.data("value");
                var position = null;
                if ($letter.hasClass("letterAdd")) {
                    position = $.publiquiz.question.blanksChar._findLetterPosition($letter);
                } else {
                    position = $letter.data("position");
                }

                var $previousLetter = $letter.prev();
                if (mode == "user" && $letter.hasClass("modified")) {
                    var valid;
                    if ($letter.hasClass("letterAdd") &&
                        $previousLetter.hasClass("letterAdd")) {
                        valid = $previousLetter.hasClass("answerOk") &&
                            answer[position] == value;
                        $.publiquiz.question.addClassColorAnswer($quiz, $letter, valid);
                    } else {
                        valid = answer[position] == value;
                        $.publiquiz.question.addClassColorAnswer($quiz, $letter, valid);
                    }
                } else if (mode == "right" && $letter.hasClass("modified")) {
                    if ($letter.hasClass("letterAdd") &&
                            $previousLetter.hasClass("letterAdd")) {
                        if ($previousLetter.hasClass("answerOk") &&
                                answer[position] == value)
                            $letter.addClass("answerOk");
                    } else {
                        if (answer[position] == value)
                            $letter.addClass("answerOk");
                    }
                } else if (mode == "full") {
                    if ($letter.hasClass("letterAdd") &&
                            $previousLetter.hasClass("letterAdd")) {
                        if ($previousLetter.hasClass("answerOk") &&
                                answer[position] == value) {
                            $letter.addClass("answerOk");
                        } else {
                            $letter.addClass("answerKo");
                        }
                    } else {
                        if (answer[position] == value)
                            $letter.addClass("answerOk");
                        else 
                            $letter.addClass("answerKo");
                    }
                }
            });
        });

        var duration = $quiz.data("verify-duration");
        if (duration > 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    },

    /**
     * Find suppose position of letter.
     *
     * @params {Object} $quiz: object jquery publiquiz.
     */
    _findLetterPosition: function($letter) {
        var $previousLetter = $letter.prev();
        var count = 1;
        while ($previousLetter.hasClass("letterAdd")) {
            $previousLetter = $previousLetter.prev();
            count += 1;
        }
        var previousPosition = $previousLetter.data("position");
        return $.publiquiz.question.formatNumber(parseInt(previousPosition, 10) + count, 3);
    }

};


// Register function
$.publiquiz.question.register("blanks-char", {
        configure: $.publiquiz.question.blanksChar.blanksConfigure,
        enable: $.publiquiz.question.blanksChar.blanksEnable,
        disable: $.publiquiz.question.blanksChar.blanksDisable,
        help: $.publiquiz.question.blanksChar.blanksHelp,
        retry: $.publiquiz.question.blanksChar.blanksRetry,
        textAnswer: $.publiquiz.question.blanksChar.blanksTextAnswer,
        insertUserAnswers: $.publiquiz.question.blanksChar.blanksInsertUserAnswers,
        quizAnswer: $.publiquiz.question.blanksChar.blanksQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.blanksChar.blanksQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.blanksChar.blanksVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.blanksChar.blanksVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.blanksChar.blanksVerifyFullAnswer,
        computeScore: $.publiquiz.question.blanksChar.blanksComputeScore,
        quizScore: $.publiquiz.question.blanksChar.blanksScore
    });

}(jQuery));
