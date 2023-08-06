/**
 * @projectDescription publiquiz_basics.js
 * Plugin jQuery for quiz choices.
 *
 * @author prismallia.fr
 * @version 0.1
 * $Id: publiquiz_basics.js 998083592483 2016/01/26 16:19:04 Tien $
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


/*****************************************************************************
 *
 *                              Plugin publiquiz
 *
 ****************************************************************************/

(function ($) {

"use strict";

$.fn.publiquiz = function(options, args) {

    var $this = this;

    // Options
    var opts = handleOptions(options, args);
    if (opts === false)
        return $this;
    $.publiquiz.defaults.prefix = opts.prefix;
    if (opts.baseScore > -1)
        $.publiquiz.defaults.baseScore = opts.baseScore;

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                              Library
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    /**
     * Process the args that were passed to the plugin fn
     *
     * @param {Object} options, object can be String or {}.
     */
    function handleOptions(options, args) {
        if (options && options.constructor == String) {

            $.publiquiz.question.clearVerify( );

            $this.each( function() {
                var $quiz = $(this);
                if (!$quiz.attr("data-engine"))
                    return;
                var engine = $quiz.data("engine");
                var prefix = $quiz.data("prefix");

                switch (options) {
                    case ("validate"):
                        $.publiquiz.question.disable[engine]($quiz);
                        $.publiquiz.question.textAnswer[engine]($quiz);
                        $.publiquiz.question.insertUserAnswers[engine]($quiz);
                        break;
                    case ("enable"):
                        $.publiquiz.question.enable[engine]($quiz);
                        $.publiquiz.question.hideTextAnswer($quiz);
                        break;
                    case ("disable"):
                        $.publiquiz.question.disable[engine]($quiz);
                        break;
                    case ("retry"):
                        $.publiquiz.question.retry[engine]($quiz);
                        break;
                    case ("textAnswer"):
                        $.publiquiz.question.textAnswer[engine]($quiz);
                        break;
                    case ("insertUserAnswers"):
                        $.publiquiz.question.insertUserAnswers[engine]($quiz);
                        break;
                    case ("quizAnswer"):
                        $.publiquiz.question.quizAnswer[engine]($quiz, args);
                        break;
                    case ("quizTimerAnswerColor"):
                        $.publiquiz.question.quizTimerAnswerColor[engine]($quiz);
                        break;
                    case ("verifyUserAnswer"):
                        $.publiquiz.question.verifyUserAnswer[engine]($quiz);
                        break;
                    case ("verifyRightAnswer"):
                        $.publiquiz.question.verifyRightAnswer[engine]($quiz);
                        break;
                    case ("verifyFullAnswer"):
                        $.publiquiz.question.verifyFullAnswer[engine]($quiz);
                        break;
                    default:
                        $.fn.publiquiz[options]($quiz, args);
                }
            });
            return false;
        }

        return $.extend({}, $.publiquiz.defaults, options || {});
    }

    /**
     * Quiz process, set quiz enable.
     *
     * @param {Object} jquery Object quiz.
     */
    function quizProcess($quiz) {
        var engine = $quiz.data("engine");

        // Verify quiz is valide
        if (!$.publiquiz.question.enable[engine])
            return;

        activateQuiz($quiz);
    }

    /**
     * Action process, set action on quiz.
     *
     * @param {Object} $action, jquery Object action.
     */
    function actionProcess($action) {
        var prefix = opts.prefix;
        var $questions = opts.questions;
        var $scenario = opts.scenario;

        if (!opts.questions || !opts.scenario)
            return;

        // Retrieve nb retry for quiz
        var nbRetryQuiz = -1;
        var $nbRetryQuizElem = $action.find("."+prefix+"NbRetry");
        if ($nbRetryQuizElem.length > 0)
            nbRetryQuiz = parseInt($nbRetryQuizElem.text(), 10);

        $action.questions = opts.questions;
        $action.scenario = opts.scenario;
        $action.nbRetryQuiz = nbRetryQuiz;
        $action.idxValidate = 0;
        $action.idxVerify = 0;
        $action.idxRetry = 0;
        $action.idxUserAnswer = 0;
        $action.idxRightAnswer = 0;

        // Set button events
        $action.find("."+prefix+"Button").click( function(ev) {
            ev.preventDefault();
            var $btn = $(this);
            if ($btn.hasClass(prefix+"Submit")) {
                if ($scenario.validate)
                    $.publiquiz.action.validate($action);
            } else if ($btn.hasClass(prefix+"UserAnswer")) {
                if ($scenario.userAnswer)
                    $.publiquiz.action.userAnswer($action);
            } else if ($btn.hasClass(prefix+"RightAnswer")) {
                if ($scenario.rightAnswer)
                    $.publiquiz.action.rightAnswer($action);
            } else if ($btn.hasClass(prefix+"VerifyUserAnswer")) {
                if ($scenario.verify)
                    $.publiquiz.action.verify($action);
            } else if ($btn.hasClass(prefix+"Retry")) {
                if ($scenario.retry)
                    $.publiquiz.action.retry($action);
            } else if ($btn.hasClass(prefix+"Redo")) {
                if ($scenario.redo)
                    $.publiquiz.action.redo($action);
            }
        });
    }

    /**
     * Activate quiz.
     *
     * @param {Object} jquery Object quiz.
     */
    function activateQuiz($quiz) {
        var engine = $quiz.data("engine");
        var quzId = $quiz.data("quiz-id");
        var prefix = opts.prefix;
        $quiz.data("prefix", opts.prefix);
        $quiz.data("verify-duration", opts.verifyDuration);

        // Configure quiz
        $.publiquiz.question.configure[engine]($quiz);

        // Set enable quiz
        $.publiquiz.question.enable[engine]($quiz);

        // Register score function
        $.publiquiz.question.registerScoreFunc(
                quzId,
                $quiz,
                $.publiquiz.question.computeScore[engine]
            );
        
        // Set event on help popup
        $quiz.find("."+prefix+"HelpPopUp").click( function(ev) {
            $(this).addClass("hidden");
        });

        // Set button events
        $quiz.find("."+prefix+"Button").click( function(ev) {
            ev.preventDefault();
            var $btn = $(this);
            var id = $btn.attr("id");
            if (id.search("_help-link") != -1 ) {
                $.publiquiz.question.help[engine]($quiz);
            } else if (id.search("_explanation-link") > -1 || 
                    id.search("_script-link") > -1 ||
                    id.search("_strategy-link") > -1) {
                $("#" + id.replace("link", "slot")).slideToggle();
            } 
        });
    }

    /* ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
     *                          Plug-in main function
     * ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ */

    return $this.each( function() {
        var $elem = $(this);
        var engine = $elem.data("engine");

        if (engine)
            quizProcess($elem);
        else
            actionProcess($elem);
    });
};

}(jQuery));


/*****************************************************************************
 *
 *                                  Choices
 *
 ****************************************************************************/

(function ($) {

"use strict";

$.publiquiz.question.choices = {

    /**
     * Configure quiz.
     */
    choicesConfigure: function($quiz) {
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    choicesEnable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Choice input").removeAttr("disabled");
        $quiz.find("."+prefix+"Choice").click( function(ev) {
            var $target = $(this);
            if(ev.target.nodeName.toLowerCase() == "audio")
                return;
            while (!$target.hasClass(prefix+"Choice"))
                $target = $target.parentNode;
            $.publiquiz.question.choices._onChoice($quiz, $target);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Choice").unbind("click");
        $quiz.find("."+prefix+"Choice input").attr("disabled", "disabled");
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    choicesRetry: function($quiz) {
        $.publiquiz.question.retryChoices($quiz, "Choice");
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    choicesComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        var engine = $quiz.data("engine");
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        if (engine == "choices-radio") {
            return $.publiquiz.question.scoreForQuizChoicesRadio($quiz);
        } else {
            if (isCheckRadio)
                return $.publiquiz.question.choices._scoreForQuizChoicesCheckRadio($quiz);
            else
                return $.publiquiz.question.scoreForQuizChoicesCheck($quiz, "Choice");
        }
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    choicesInsertUserAnswers: function($quiz) {
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        if (isCheckRadio)
            $.publiquiz.question.choices._insertUserAnswersQuizChoicesCheckRadio($quiz);
        else
            $.publiquiz.question.insertUserAnswersQuizChoices($quiz, "Choice");
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    choicesQuizAnswer: function($quiz, mode) {
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        if (isCheckRadio)
            $.publiquiz.question.choices._displayQuizChoicesAnswerCheckRadio($quiz, mode);
        else
            $.publiquiz.question.displayQuizChoicesAnswer($quiz, "Choice", mode);
    },

    /**
     * Display user answer, replace one by one with correct answer
     * and color them
     *
     * @param {Object} $quiz : object jQuery publiquiz.
     */
    choicesQuizTimerAnswerColor: function($quiz) {
        var isCheckRadio = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 )
            isCheckRadio = true;

        if (isCheckRadio)
            $.publiquiz.question.choices._displayQuizChoicesAnswerCheckRadio($quiz, "full");
        else
            $.publiquiz.question.displayQuizChoicesTimerAnswerColor($quiz, "Choice");
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    choicesVerifyUserAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "user");
    },

    /**
     * Verify only right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    choicesVerifyRightAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    choicesVerifyFullAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "full");
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * This function call when click on choice.
     *
     * @params {Object} $quiz: object jquery publiquiz.
     * @param {Object} $elem: object jquery receive click.
     */
    _onChoice: function($quiz, $elem) {
        $.publiquiz.question.clearVerify( );

        var prefix = $quiz.data("prefix");
        var engine = $quiz.data("engine");
        var quzId = $quiz.data("quiz-id");
        var $input = $elem.find("input");
        var $engine = $quiz.find("#"+quzId+"_engine");
        if (engine == "choices-radio") {
            if ($elem.hasClass("selected"))
                return;

            $engine.find("."+prefix+"Choice.selected").removeClass("selected");
            $elem.addClass("selected");
            if ($input)
                $input.prop("checked", true);
        } else {
            if ($quiz.data("engine-options") &&
                    $quiz.data("engine-options").search("radio") > -1 ) {
                if ($elem.hasClass("selected"))
                    return;

                var group = $elem.data("group");
                $engine.find("."+prefix+"Choice")
                    .filter("[data-group=\""+group+"\"]").removeClass("selected");
                $elem.addClass("selected");
                if ($input)
                    $input.prop("checked", true);
            } else {
                if ($elem.hasClass("selected")) {
                    $elem.removeClass("selected");
                    if ($input)
                        $input.prop("checked", false);
                } else {
                    $elem.addClass("selected");
                    if ($input)
                        $input.prop("checked", true);
                }
            }
        }
    },

    /**
     * Score for quiz engine choice-check with option "radio".
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    _scoreForQuizChoicesCheckRadio: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $engine = $quiz.find("#"+quzId+"_engine");
        var res = $.publiquiz.question.correction(
                $quiz.find("#"+quzId+"_correct"));

        // Get group
        var choices = [];
        $quiz.find("."+prefix+"Choice").each( function() {
            var group = $(this).data("group");
            if ($.inArray(group, choices) < 0 )
                choices.push(group);
        });

        // Compute score
        var total = choices.length;
        var score = 0;
        $.each(choices, function() {
            var group = this;
            if (res[group] && $engine.find("."+prefix+"Choice")
                                .filter("[data-group=\""+group+"\"]")
                                .filter("[data-name=\"true\"]")
                                .hasClass("selected"))
                score += 1;
            else if (!res[group] && $engine.find("."+prefix+"Choice")
                                .filter("[data-group=\""+group+"\"]")
                                .filter("[data-name=\"false\"]")
                                .hasClass("selected"))
                score += 1;
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Insert user answers in html for quiz choices-check with option "radio"
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _insertUserAnswersQuizChoicesCheckRadio: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = "";

        $quiz.find("."+prefix+"Choice.selected").each( function() {
            var $item = $(this);
            var name = $item.data("name");
            var group = $item.data("group");
            if (answer !== "")
                answer += "::";
            answer += group+name;
        });

        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz choices-check with option "radio".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : mode "correct" or "user".
     */
    _displayQuizChoicesAnswerCheckRadio: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        // Reset quiz
        $quiz.find("."+prefix+"Choice input").prop("checked", false);
        $quiz.find("."+prefix+"Choice").removeClass(
                "selected answerOk answerKo");

        // Get group
        var choices = [];
        $quiz.find("."+prefix+"Choice").each( function() {
            var group = $(this).data("group");
            if ($.inArray(group, choices) < 0 )
                choices.push(group);
        });

        // Display pquizChoice selected
        var $engine = $quiz.find("#"+quzId+"_engine");
        var answers = $.publiquiz.question.correction(
                $quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if(mode == "_correct")
            userAnswers = $.publiquiz.question.correction(
                    $quiz.find("#"+quzId+"_user"));

        $.each(choices, function() {
            var group = this;
            var $choice = null;
            if(mode == "_correct") {
                if (answers[group])
                    $choice = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]")
                        .filter("[data-name=\"true\"]");
                else
                    $choice = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]")
                        .filter("[data-name=\"false\"]");
            } else {
                if (answers[group])
                    $choice = $engine.find("."+prefix+"Choice")
                        .filter("[data-group=\""+group+"\"]")
                        .filter("[data-name=\""+answers[group]+"\"]");
            }

            if ($choice) {
                $choice.addClass("selected");
                var $input = $choice.find("input");
                if ($input.length > 0)
                    $input.prop("checked", true);
            }
        });
    }
};

// Register function
$.publiquiz.question.register("choices-radio", {
        configure: $.publiquiz.question.choices.choicesConfigure,
        enable: $.publiquiz.question.choices.choicesEnable,
        disable: $.publiquiz.question.choices.choicesDisable,
        help: $.publiquiz.question.choices.choicesHelp,
        retry: $.publiquiz.question.choices.choicesRetry,
        textAnswer: $.publiquiz.question.choices.choicesTextAnswer,
        insertUserAnswers: $.publiquiz.question.choices.choicesInsertUserAnswers,
        quizAnswer: $.publiquiz.question.choices.choicesQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.choices.choicesQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.choices.choicesVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.choices.choicesVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.choices.choicesVerifyFullAnswer,
        computeScore: $.publiquiz.question.choices.choicesComputeScore,
        quizScore: $.publiquiz.question.choices.choicesScore
    });

$.publiquiz.question.register("choices-check", {
        configure: $.publiquiz.question.choices.choicesConfigure,
        enable: $.publiquiz.question.choices.choicesEnable,
        disable: $.publiquiz.question.choices.choicesDisable,
        help: $.publiquiz.question.choices.choicesHelp,
        retry: $.publiquiz.question.choices.choicesRetry,
        textAnswer: $.publiquiz.question.choices.choicesTextAnswer,
        insertUserAnswers: $.publiquiz.question.choices.choicesInsertUserAnswers,
        quizAnswer: $.publiquiz.question.choices.choicesQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.choices.choicesQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.choices.choicesVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.choices.choicesVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.choices.choicesVerifyFullAnswer,
        computeScore: $.publiquiz.question.choices.choicesComputeScore,
        quizScore: $.publiquiz.question.choices.choicesScore
    });

}(jQuery));


/******************************************************************************
 *
 *                                  Blanks
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.question.blanks = {

    /**
     * Configure quiz.
     */
    blanksConfigure: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var noShuffle = false;
        var comboBox = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("no-shuffle") > -1 )
            noShuffle = true;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("combobox") > -1 )
            comboBox = true;

        if (engine == "blanks-fill" && !comboBox) {
            $.publiquiz.question.blanks._configureBlanksFill($quiz);
        } else if (engine == "blanks-select" && !noShuffle && !comboBox) {
            var $dropzones = $($quiz.find("."+prefix+"Drop"));
            var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
            var answer = true;
            while(answer) {
                answer = $.publiquiz.question.shuffleAndControlItems($quiz, $dropzones, res);
            }
        } else if (comboBox) {
            var $box = $($quiz.find("."+prefix+"SelectItem"));
            $box.shuffle();
            $box.each( function() {
                var $combo = $(this);
                $combo.children('option[value=""]').detach().prependTo($combo);
                $combo.val("").prop("selected", true);
            }); 
        }
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    blanksEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event change on choice
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            $choice.prop("disabled", false);
            $choice.removeClass("disabled");
        }).on({
            input: function(ev) {
                $.publiquiz.question.clearVerify();
            }
        });

        // Event "draggable" on item
        $.publiquiz.question.setDraggableItem($quiz, $quiz.find("."+prefix+"Item"), "");

        // Event "select" on combo box
        $quiz.find("."+prefix+"SelectItem").prop("disabled", false).change( function() {
            var $combo = $(this);
            $.publiquiz.question.blanks._onChangeSelectedItem($quiz, $combo);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    blanksDisable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event change on choice
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            $choice.prop("disabled", true);
            $choice.addClass("disabled");
        }).unbind("input");

        // Event "draggable" on item
        var evtStart = "mousedown touchstart";
        var $items = $quiz.find("."+prefix+"Item");
        $items.unbind(evtStart);

        // Event "select" on combo box
        $quiz.find("."+prefix+"SelectItem").unbind("change").prop("disabled", true);
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
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksRetry: function($quiz) {
        var comboBox = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("combobox") > -1 )
            comboBox = true;

        if (comboBox)
            $.publiquiz.question.blanks._retryBlanksComboBox($quiz);
        else
            $.publiquiz.question.retryBlanks($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    blanksComputeScore: function($quiz) {
        var noMark = false;
        var comboBox = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("combobox") > -1 )
            comboBox = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        var engine = $quiz.data("engine");
        if (engine == "blanks-fill") {
            return $.publiquiz.question.blanks._computeScoreBlanksFill($quiz);
        } else {
            if (comboBox)
                return $.publiquiz.question.blanks._computeScoreBlanksComboBox($quiz);
            else
                return $.publiquiz.question.scoreForQuizCmpCheck($quiz);
        }
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
        var engine = $quiz.data("engine");
        var comboBox = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("combobox") > -1 )
            comboBox = true;

        var answer = "";
        if (engine == "blanks-fill") {
            $quiz.find("."+prefix+"Choice").each( function() {
                var $item = $(this);
                var id = $item.attr("id");
                var value = $item.val().trim();
                if (value !== "") {
                    if (answer !== "")
                        answer += "::";
                    answer += id.substring(id.length - 3, id.length) + value;
                }
            });
            $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
        } else {
            if (comboBox) {
                $quiz.find("."+prefix+"SelectItem").each( function() {
                    var $item = $(this);
                    var id = $item.attr("id");
                    var value = $item.data("item-value");
                    if (value) {
                        if (answer !== "")
                            answer += "::";
                        answer += id.substring(id.length - 3, id.length) + value;
                    }
                });
                $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
            } else {
                $.publiquiz.question.inserUserAnswersQuizDrop($quiz);
            }
        }
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    blanksQuizAnswer: function($quiz, mode) {
        var engine = $quiz.data("engine");
        var comboBox = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("combobox") > -1 )
            comboBox = true;

        if (engine == "blanks-fill") {
            $.publiquiz.question.displayQuizAnswerBlanksFill($quiz, mode);
        } else {
            if (comboBox)
                $.publiquiz.question.blanks._displayQuizAnswerBlanksComboBox($quiz, mode);
            else
                $.publiquiz.question.displayQuizCmpAnswer($quiz, mode);
        }
    },

    /**
     * Display user answer, replace one by one with correct answer
     * and color them
     *
     * @param {Object} $quiz : object jQuery publiquiz.
     */
    blanksQuizTimerAnswerColor: function($quiz) {
        var engine = $quiz.data("engine");
        var comboBox = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("combobox") > -1 )
            comboBox = true;

        if (engine == "blanks-fill") {
            $.publiquiz.question.blanks._displayQuizBlanksFillTimerAnswerColor($quiz);
        } else {
            if (comboBox)
                $.publiquiz.question.blanks._displayQuizBlanksComboBoxTimerAnswerColor($quiz);
            else
                $.publiquiz.question.displayQuizCmpTimerAnswerColor($quiz);
        }
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksVerifyUserAnswer: function($quiz) {
        var engine = $quiz.data("engine");
        var comboBox = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("combobox") > -1 )
            comboBox = true;

        if (engine == "blanks-fill") {
            $.publiquiz.question.blanks._verifyBlanksFill($quiz, "user");
        } else {
            if (comboBox)
                $.publiquiz.question.blanks._verifyBlanksComboBox($quiz, "user");
            else
                $.publiquiz.question.verifyQuizCmpAnswer($quiz, "user");
        }
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksVerifyRightAnswer: function($quiz) {
        var engine = $quiz.data("engine");
        var comboBox = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("combobox") > -1 )
            comboBox = true;

        if (engine == "blanks-fill") {
            $.publiquiz.question.blanks._verifyBlanksFill($quiz, "right");
        } else {
            if (comboBox)
                $.publiquiz.question.blanks._verifyBlanksComboBox($quiz, "right");
            else
                $.publiquiz.question.verifyQuizCmpAnswer($quiz, "right");
        }
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    blanksVerifyFullAnswer: function($quiz) {
        var engine = $quiz.data("engine");
        var comboBox = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("combobox") > -1 )
            comboBox = true;

        if (engine == "blanks-fill") {
            $.publiquiz.question.blanks._verifyBlanksFill($quiz, "full");
        } else {
            if (comboBox)
                $.publiquiz.question.blanks._verifyBlanksComboBox($quiz, "full");
            else
                $.publiquiz.question.verifyQuizCmpAnswer($quiz, "full");
        }
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * On change selected item in combobox.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _onChangeSelectedItem: function($quiz, $combo) {
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var $item = $($combo.find(":selected"));
        var value = $item.val();

        if (!isMultiple) {
            var oldValue = $combo.data("item-value");
            $quiz.find("."+prefix+"SelectItem").each( function() {
                var $combobox = $(this);
                if ($combobox !== $combo && value !== "")
                    $combobox.children('option[value="'+value+'"]').attr("disabled", "disabled");
                if (oldValue)
                    $combobox.children('option[value="'+oldValue+'"]').removeAttr("disabled");
            });
        }

        $combo.data("item-value", value);
    },

    /**
     * Retry quiz blanks option combobox.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _retryBlanksComboBox: function($quiz) {
        $.publiquiz.question.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var valuesToShow = [];
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        // On retrouve les valeurs mal placé
        $.each(res, function(key, value) {
            var $combo = $quiz.find("#"+quzId+"_"+key);
            var data = $combo.data("item-value");
            if (data && data != value) {
                valuesToShow.push(data);
                $combo.data("item-value", "");
                $combo.val("").prop("selected", true);
            }
        });

        if (isMultiple)
            return;

        // On re-affiche les valeurs qui on été mal placer dans les selects
        $quiz.find("."+prefix+"SelectItem").each( function() {
            var $combo = $(this);
            $.each(valuesToShow, function(idx, value) {
                $combo.children('option[value="'+value+'"]').removeAttr("disabled");
            });
        });
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    _displayQuizAnswerBlanksComboBox: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $.publiquiz.question.correction($quiz.find("#"+quzId+mode));
        var userAnswers = null;
        if (mode == "_correct")
            userAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_user"));

        // On vide les champs
        $quiz.find("."+prefix+"SelectItem").each( function() {
            var $combo = $(this);
            $combo.removeClass("answerOk answerKo");
            $combo.find("option").removeAttr("disabled");
            $combo.val("").prop("selected", true);
        });

        // On place la correction en selection la bonne option
        $.each(answers, function(key, value) {
            var $combo = $quiz.find("#"+quzId+"_"+key);
            $combo.val(value).prop("selected", true);
        });
    },

    /**
     * Display right/user answer for quiz engine blanks-fill.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    _displayQuizBlanksFillTimerAnswerColor: function($quiz) {
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
        var answers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        var timerValidation = $.publiquiz.defaults.timerValidation;
        $.each(answers, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if ($item.length > 0) {
                var data = $item.val().trim();
                var valid = $.publiquiz.question.isValideBlanksFillAnswer(data, value, isStrict, options);
                data = value.split("|").join(" / ");
                data = data.replace(new RegExp(/_/g), " ");
                $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                $('.publiquizAction').queue(function(next) {
                    $item.val(data);
                    next();
                });
                $('.publiquizAction').delay(timerValidation);
            }
        });
    },

    /**
     * Display correct answers one by one for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    _displayQuizBlanksComboBoxTimerAnswerColor: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var engine = $quiz.data("engine");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_user"));
        var timerValidation = $.publiquiz.defaults.timerValidation;

        // On place la correction en selection la bonne option
        $.each(answers, function(key, value) {
            var $combo = $quiz.find("#"+quzId+"_"+key);
            var valid = $combo.data("item-value") == value;
            $.publiquiz.question.addClassColorAnswer($quiz, $combo, valid);
            if (!valid) {
                $('.publiquizAction').queue(function(next) {
                    $combo.val(value).prop("selected", true);
                    next();
                });
            }
            $('.publiquizAction').delay(timerValidation);
        });
    },

    /**
     * Verify answer for quiz blanks-fill.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    _verifyBlanksFill: function($quiz, mode) {
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

        var rightAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_user"));

        var timerValidation = $.publiquiz.defaults.timerValidation;
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;
        $.each(rightAnswers, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if ($item.length > 0) {
                var data = $item.val().trim();
                if (data !== "") {
                    var valid = $.publiquiz.question.isValideBlanksFillAnswer(data, value, isStrict, options);
                    if (mode == "user") {
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                        if (!valid && paramWrongAnswers == "clear") {
                            $('.publiquizAction').queue(function(next) {
                                $item.val("");
                                $item.removeClass("answerKo");
                                next();
                            });
                        }
                        $('.publiquizAction').delay(timerValidation);
                    } else if (mode == "right") {
                        if (valid)
                            $.publiquiz.question.addClassColorAnswer($quiz, $item, true);
                    } else {
                        var userAnswer = userAnswers[key];
                        valid = userAnswer && $.publiquiz.question.isValideBlanksFillAnswer(userAnswer, value, isStrict, options);
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                    }
                }
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    },

    /**
     * Verify answer for quiz blanks-select option combobox.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _verifyBlanksComboBox: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var rightAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correction($quiz.find("#"+quzId+"_user"));
        var timerValidation = $.publiquiz.defaults.timerValidation;
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;

        $.each(rightAnswers, function(key, value) {
            var $combo = $quiz.find("#"+quzId+"_"+key);
            var data = $combo.data("item-value");
            var valid;
            if (mode == "user") {
                if (data) {
                    valid = data == value;
                    $.publiquiz.question.addClassColorAnswer($quiz, $combo, valid);
                    if (!valid && paramWrongAnswers == "clear") {
                        $('.publiquizAction').queue(function(next) {
                            $combo.removeClass("answerKo");
                            $combo.data("item-value", "");
                            $combo.val("").prop("selected", true);
                            $quiz.find("."+prefix+"SelectItem").children('option[value="'+data+'"]').removeAttr("disabled");
                            next();
                        });
                    }
                }
            } else if (mode == "right") {
                if (data && data == value)
                    $.publiquiz.question.addClassColorAnswer($quiz, $combo, true);
            } else {
                valid = data && data == value;
                $.publiquiz.question.addClassColorAnswer($quiz, $combo, valid);
            }
            $('.publiquizAction').delay(timerValidation);
        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    },

    /**
     * Configure quiz blanks fill.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    _configureBlanksFill: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Choice").each( function() {
            if (this.parentNode.nodeName.toLowerCase() == "td" ||
                this.parentNode.parentNode.nodeName.toLowerCase == "td")
                return;
            if (this.nodeName.toLowerCase() == "textarea")
                return;

            var $choice = $(this);
            var id = $choice.attr("id");
            var key = id.substring(id.length - 3, id.length);
            var answers = $.publiquiz.question.correction($("#"+quzId+"_correct"));
            var value = answers[key];

            var answer = "";
            $(value.split("|")).each( function(ids, data) {
                if (data.length > answer)
                    answer = data;
            });

            var w = answer.length * 2;
            if(w < 20)
                w = 20;
            if (!$choice.attr("style"))
                $choice.css("width", w+"ex");
        });
    },

    /**
     * This function use for compute score for engine blanks-fill.
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    _computeScoreBlanksFill: function ($quiz) {
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

        var total = $quiz.find("."+prefix+"Choice").length;
        var score = 0.0;

        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        $.each(res, function(key, value) {
            var $item = $quiz.find("#"+quzId+"_"+key);
            if ($item.length > 0) {
                var data = $item.val().trim();
                if ($.publiquiz.question.isValideBlanksFillAnswer(data, value, isStrict, options))
                    score += 1;
            }
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * This function use for compute score for engine blanks-select option combobox.
     *
     * @params {Object} $quiz : Object jquery quiz.
     * @return {Dictionnary}.
     */
    _computeScoreBlanksComboBox: function ($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        var total = $quiz.find("."+prefix+"SelectItem").length;
        var score = 0;

        $.each(res, function(key, value) {
            var $combo = $quiz.find("#"+quzId+"_"+key);
            if ($combo.data("item-value") && $combo.data("item-value") == value)
                score += 1;
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    }
};

// Register function
$.publiquiz.question.register("blanks-fill", {
        configure: $.publiquiz.question.blanks.blanksConfigure,
        enable: $.publiquiz.question.blanks.blanksEnable,
        disable: $.publiquiz.question.blanks.blanksDisable,
        help: $.publiquiz.question.blanks.blanksHelp,
        retry: $.publiquiz.question.blanks.blanksRetry,
        textAnswer: $.publiquiz.question.blanks.blanksTextAnswer,
        insertUserAnswers: $.publiquiz.question.blanks.blanksInsertUserAnswers,
        quizAnswer: $.publiquiz.question.blanks.blanksQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.blanks.blanksQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.blanks.blanksVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.blanks.blanksVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.blanks.blanksVerifyFullAnswer,
        computeScore: $.publiquiz.question.blanks.blanksComputeScore,
        quizScore: $.publiquiz.question.blanks.blanksScore
    });

$.publiquiz.question.register("blanks-select", {
        configure: $.publiquiz.question.blanks.blanksConfigure,
        enable: $.publiquiz.question.blanks.blanksEnable,
        disable: $.publiquiz.question.blanks.blanksDisable,
        help: $.publiquiz.question.blanks.blanksHelp,
        retry: $.publiquiz.question.blanks.blanksRetry,
        textAnswer: $.publiquiz.question.blanks.blanksTextAnswer,
        insertUserAnswers: $.publiquiz.question.blanks.blanksInsertUserAnswers,
        quizAnswer: $.publiquiz.question.blanks.blanksQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.blanks.blanksQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.blanks.blanksVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.blanks.blanksVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.blanks.blanksVerifyFullAnswer,
        computeScore: $.publiquiz.question.blanks.blanksComputeScore,
        quizScore: $.publiquiz.question.blanks.blanksScore
    });

}(jQuery));



/******************************************************************************
 *
 *                                  Sort
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.question.sort = {

    /**
     * Configure quiz.
     */
    sortConfigure: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $dropzones = $($quiz.find("."+prefix+"Drop"));
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));
        
        // Control not give the right answer
        var answer = true;
        while(answer) {
            answer = $.publiquiz.question.shuffleAndControlItems($quiz, $dropzones, res);
        }
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    sortEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "draggable" on item
        $.publiquiz.question.setDraggableItem($quiz, $quiz.find("."+prefix+"Item"), "");
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortDisable: function($quiz) {
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
    sortHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    sortRetry: function($quiz) {
        $.publiquiz.question.retryQuizCmp($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    sortComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        return $.publiquiz.question.scoreForQuizCmpRadio($quiz);
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    sortInsertUserAnswers: function($quiz) {
        $.publiquiz.question.inserUserAnswersQuizDrop($quiz);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    sortQuizAnswer: function($quiz, mode) {
        $.publiquiz.question.displayQuizCmpAnswer($quiz, mode);
    },

    /**
     * Display user answer, replace one by one with correct answer
     * and color them
     *
     * @param {Object} $quiz : object jQuery publiquiz.
     */
    sortQuizTimerAnswerColor: function($quiz) {
        $.publiquiz.question.displayQuizCmpTimerAnswerColor($quiz);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    sortVerifyUserAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "user");
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    sortVerifyRightAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    sortVerifyFullAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "full");
    }


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

};

// Register function
$.publiquiz.question.register("sort", {
        configure: $.publiquiz.question.sort.sortConfigure,
        enable: $.publiquiz.question.sort.sortEnable,
        disable: $.publiquiz.question.sort.sortDisable,
        help: $.publiquiz.question.sort.sortHelp,
        retry: $.publiquiz.question.sort.sortRetry,
        textAnswer: $.publiquiz.question.sort.sortTextAnswer,
        insertUserAnswers: $.publiquiz.question.sort.sortInsertUserAnswers,
        quizAnswer: $.publiquiz.question.sort.sortQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.sort.sortQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.sort.sortVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.sort.sortVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.sort.sortVerifyFullAnswer,
        computeScore: $.publiquiz.question.sort.sortComputeScore,
        quizScore: $.publiquiz.question.sort.sortScore
    });

}(jQuery));


/******************************************************************************
 *
 *                                  Matching
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.question.matching = {

    /**
     * Configure quiz.
     */
    matchingConfigure: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var $dropzones = $($quiz.find("."+prefix+"Drop"));
        var res = $.publiquiz.question.correction($quiz.find("#"+quzId+"_correct"));

        // Control not give the right answer
        var answer = true;
        while(answer) {
            answer = $.publiquiz.question.shuffleAndControlItems($quiz, $dropzones, res);
        }
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    matchingEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "draggable" on item
        $.publiquiz.question.setDraggableItem($quiz, $quiz.find("."+prefix+"Item"), "");
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingDisable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Draggable item
        var evtStart = "mousedown touchstart";
        var $items = $quiz.find("."+prefix+"Item");
        $items.unbind(evtStart);
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingRetry: function($quiz) {
        $.publiquiz.question.retryQuizCmp($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    matchingComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        return $.publiquiz.question.scoreForQuizCmpCheck($quiz);
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    matchingInsertUserAnswers: function($quiz) {
        $.publiquiz.question.inserUserAnswersQuizDrop($quiz);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    matchingQuizAnswer: function($quiz, mode) {
        $.publiquiz.question.displayQuizCmpAnswer($quiz, mode);
    },

    /**
     * Display user answer, replace one by one with correct answer
     * and color them
     *
     * @param {Object} $quiz : object jQuery publiquiz.
     */
    matchingQuizTimerAnswerColor: function($quiz) {
        $.publiquiz.question.displayQuizCmpTimerAnswerColor($quiz);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyUserAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "user");
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyRightAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    matchingVerifyFullAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizCmpAnswer($quiz, "full");
    }


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

};

// Register function
$.publiquiz.question.register("matching", {
        configure: $.publiquiz.question.matching.matchingConfigure,
        enable: $.publiquiz.question.matching.matchingEnable,
        disable: $.publiquiz.question.matching.matchingDisable,
        help: $.publiquiz.question.matching.matchingHelp,
        retry: $.publiquiz.question.matching.matchingRetry,
        textAnswer: $.publiquiz.question.matching.matchingTextAnswer,
        insertUserAnswers: $.publiquiz.question.matching.matchingInsertUserAnswers,
        quizAnswer: $.publiquiz.question.matching.matchingQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.matching.matchingQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.matching.matchingVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.matching.matchingVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.matching.matchingVerifyFullAnswer,
        computeScore: $.publiquiz.question.matching.matchingComputeScore,
        quizScore: $.publiquiz.question.matching.matchingScore
    });

}(jQuery));


/******************************************************************************
 *
 *                                 Pointing
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.question.pointing = {

    /**
     * Configure quiz.
     */
    pointingConfigure: function($quiz) {
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    pointingEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "click" for point
        $quiz.find("."+prefix+"Point").click( function(ev) {
            var $target = $(this);
            $.publiquiz.question.clearVerify();
            while (!$target.hasClass(prefix+"Point"))
                $target = $target.parentNode;
            $.publiquiz.question.pointing._onPoint($quiz, $target);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Point").unbind("click");
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingRetry: function($quiz) {
        $.publiquiz.question.retryChoices($quiz, "Point");
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    pointingComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        var quzId = $quiz.data("quiz-id");
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 ) {
            return $.publiquiz.question.scoreForQuizChoicesRadio($quiz);
        } else {
            return $.publiquiz.question.scoreForQuizChoicesCheck($quiz, "Point");
        }
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingInsertUserAnswers: function($quiz) {
        $.publiquiz.question.insertUserAnswersQuizChoices($quiz, "Point");
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    pointingQuizAnswer: function($quiz, mode) {
        $.publiquiz.question.displayQuizChoicesAnswer($quiz, "Point", mode);
    },

    /**
     * Display user answer, replace one by one with correct answer
     * and color them
     *
     * @param {Object} $quiz : object jQuery publiquiz.
     */
    pointingQuizTimerAnswerColor: function($quiz) {
        $.publiquiz.question.displayQuizChoicesTimerAnswerColor($quiz, "Point");
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyUserAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "user");
    },

    /**
     * Verify only right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyRightAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyFullAnswer: function($quiz) {
        $.publiquiz.question.verifyQuizChoicesAnswer($quiz, "full");
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * This function call when click on object with class pquizPoint.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizPoint.
     */
    _onPoint: function($quiz, $elem) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("radio") > -1 ) {
            $quiz.find("."+prefix+"Point").removeClass("selected");
            $elem.addClass("selected");
        } else {
            if ($elem.hasClass("selected"))
                $elem.removeClass("selected");
            else
                $elem.addClass("selected");
        }
    }

};

// Register function
$.publiquiz.question.register("pointing", {
        configure: $.publiquiz.question.pointing.pointingConfigure,
        enable: $.publiquiz.question.pointing.pointingEnable,
        disable: $.publiquiz.question.pointing.pointingDisable,
        help: $.publiquiz.question.pointing.pointingHelp,
        retry: $.publiquiz.question.pointing.pointingRetry,
        textAnswer: $.publiquiz.question.pointing.pointingTextAnswer,
        insertUserAnswers: $.publiquiz.question.pointing.pointingInsertUserAnswers,
        quizAnswer: $.publiquiz.question.pointing.pointingQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.pointing.pointingQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.pointing.pointingVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.pointing.pointingVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.pointing.pointingVerifyFullAnswer,
        computeScore: $.publiquiz.question.pointing.pointingComputeScore,
        quizScore: $.publiquiz.question.pointing.pointingScore
    });

}(jQuery));


/******************************************************************************
 *
 *                              Pointing-categories
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.question.pointingCategories = {

    /**
     * Configure quiz.
     */
    pointingConfigure: function($quiz) {
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    pointingEnable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // Event "click" for category
        $quiz.find("."+prefix+"Category").click( function(ev) {
            var $target = $(this);
            while (!$target.hasClass(prefix+"Category"))
                $target = $target.parentNode;
            $.publiquiz.question.pointingCategories._onCategory($quiz, $target);
        });

        // Event "click" for point
        $quiz.find("."+prefix+"Point").click( function(ev) {
            var $target = $(this);
            while (!$target.hasClass(prefix+"Point"))
                $target = $target.parentNode;
            $.publiquiz.question.pointingCategories._onPoint($quiz, $target);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Point").unbind("click");
        $quiz.find("."+prefix+"Category").unbind("click");
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingRetry: function($quiz) {
        $.publiquiz.question.retryPointingCategory($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    pointingComputeScore: function($quiz) {
        return $.publiquiz.question.scoreForQuizPointingCategories($quiz);
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    pointingInsertUserAnswers: function($quiz) {
        var answer = "";
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            var pointId = $point.data("choice-id");
            if (category) {
                if (answer !== "")
                    answer += "::";
                answer += category + pointId;
            }
        });

        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    pointingQuizAnswer: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+mode));

        // On enleve la category selected
        $quiz.find("."+prefix+"Category").removeClass("selected");

        // On enleve les couleurs
        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            $point.removeClass("answerOk answerKo");
            $point.data("category-id", "");
            var classList = $point.attr("class").split(/\s+/);
            if (classList.length > 1)
                $point.removeClass(classList[classList.length - 1]);
        });

        // On place les couleurs de la correction
        $.each(answers, function(key, value) {
            var $category = $quiz.find("."+prefix+"Category").filter("[data-category-id=\""+key+"\"]");
            var $categoryColor = $category.find("."+prefix+"CategoryColor");
            var color = $categoryColor.attr("class").split(/\s+/)[1];

            $.each(value.split("|"), function(idx, data) {
                var $point = $quiz.find("."+prefix+"Point").filter("[data-choice-id=\""+data+"\"]");
                $point.addClass(color);
                $point.data("category-id", key);
            });
        });
    },

    /**
     * Display user answer, replace one by one with correct answer
     * and color them
     *
     * @param {Object} $quiz : object jQuery publiquiz.
     */
    pointingQuizTimerAnswerColor: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_correct"));
        var timerValidation = $.publiquiz.defaults.timerValidation;
        var pointCategories = {};
        $.each(answers, function(cat, value) {
            var values = value.split('|');
            $.each(values, function(key, point) {
                pointCategories[point] = cat;
            });
        });

        // On enleve la category selected
        $quiz.find("."+prefix+"Category").removeClass("selected");

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            var pointId = $point.data("choice-id");
            var valid = category && answers[category].search(pointId) > -1;
            $.publiquiz.question.addClassColorAnswer($quiz, $point, valid);
            if (!valid) {
                var newCategory = pointCategories[pointId];
                $('.publiquizAction').queue(function(next) {
                    var classList = $point.attr("class").split(/\s+/);
                    $point.removeClass(classList[classList.length - 2]);
                    if (newCategory) {
                        var $category = $quiz.find("."+prefix+"Category").filter("[data-category-id=\""+newCategory+"\"]");
                        var $categoryColor = $category.find("."+prefix+"CategoryColor");
                        var color = $categoryColor.attr("class").split(/\s+/)[1];
                        $point.addClass(color);
                        $point.data("category-id", newCategory);
                    }
                    next();
                });
            }
            $('.publiquizAction').delay(timerValidation);
        });
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyUserAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var res = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_correct"));
        var timerValidation = $.publiquiz.defaults.timerValidation;
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            if (category) {
                var pointId = $point.data("choice-id");
                var valid = res[category].search(pointId) > -1;
                $.publiquiz.question.addClassColorAnswer($quiz, $point, valid);
                if (!valid && paramWrongAnswers == "clear") {
                    $('.publiquizAction').queue(function(next) {
                        $point.removeClass("answerKo");
                        var classList = $point.attr("class").split(/\s+/);
                        if (classList.length > 1)
                            $point.removeClass(classList[classList.length - 1]);
                        next();
                    });
                }
                $('.publiquizAction').delay(timerValidation);
           }
        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyRightAnswer: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var res = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_correct"));

        $quiz.find("."+prefix+"Point").each( function() {
            var $point = $(this);
            var category = $point.data("category-id");
            if (category) {
                var pointId = $point.data("choice-id");
                if (res[category].search(pointId) > -1)
                    $point.addClass("answerOk");
            }
        });
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    pointingVerifyFullAnswer: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var rightAnswers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_user"));

        $.each(rightAnswers, function(key, value) {
            var $category = $quiz.find("."+prefix+"Category").filter("[data-category-id=\""+key+"\"]");
            var res = [];
            if (userAnswers[key])
                res = userAnswers[key].split("|");
            $.each(value.split("|"), function(idx, data) {
                var $point = $quiz.find("."+prefix+"Point").filter("[data-choice-id=\""+data+"\"]");
                if ($.inArray(data, res) > -1)
                    $point.addClass("answerOk");
                else
                    $point.addClass("answerKo");
            });
        });
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * This function call when click on object with class pquizCategory.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizCategory.
     */
    _onCategory: function($quiz, $elem) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        $quiz.find("."+prefix+"Category").removeClass("selected");
        $elem.addClass("selected");
    },

    /**
     * This function call when click on object with class pquizPoint.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizPoint.
     */
    _onPoint: function($quiz, $elem) {
        $.publiquiz.question.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var category = null;
        var color = null;
        var $selected = $quiz.find("."+prefix+"Category.selected");
        if ($selected.length > 0) {
            category = $selected.data("category-id");
            var $categoryColor = $selected.find("."+prefix+"CategoryColor");
            color = $categoryColor.attr("class").split(/\s+/)[1];
        }

        if (!category)
            return;

        var classList = $elem.attr("class").split(/\s+/);
        var categoryId = $elem.data("category-id");
        if (classList.length > 1 && categoryId == category) {
            $elem.removeClass(classList[classList.length - 1]);
            $elem.data("category-id", "");
            return;
        } else if (classList.length > 1) {
            $elem.removeClass(classList[classList.length - 1]);
        }
        $elem.data("category-id", category);
        $elem.addClass(color);
    }

};

// Register function
$.publiquiz.question.register("pointing-categories", {
        configure: $.publiquiz.question.pointingCategories.pointingConfigure,
        enable: $.publiquiz.question.pointingCategories.pointingEnable,
        disable: $.publiquiz.question.pointingCategories.pointingDisable,
        help: $.publiquiz.question.pointingCategories.pointingHelp,
        retry: $.publiquiz.question.pointingCategories.pointingRetry,
        textAnswer: $.publiquiz.question.pointingCategories.pointingTextAnswer,
        insertUserAnswers: $.publiquiz.question.pointingCategories.pointingInsertUserAnswers,
        quizAnswer: $.publiquiz.question.pointingCategories.pointingQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.pointingCategories.pointingQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.pointingCategories.pointingVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.pointingCategories.pointingVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.pointingCategories.pointingVerifyFullAnswer,
        computeScore: $.publiquiz.question.pointingCategories.pointingComputeScore,
        quizScore: $.publiquiz.question.pointingCategories.pointingScore
    });

}(jQuery));



/******************************************************************************
 *
 *                                  Categories
 *
******************************************************************************/


(function ($) {

"use strict";

$.publiquiz.question.categories = {

    /**
     * Configure quiz.
     */
    categoriesConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        var noShuffle = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("no-shuffle") > -1 )
            noShuffle = true;

        if (!noShuffle) {
            // Shuffle items for mode "basket"
            $.publiquiz.question.shuffleItems($quiz.find("."+prefix+"CategoriesItems"));

            // Shuffle items for mode "color"
            if ($quiz.data("engine-options") &&
                    $quiz.data("engine-options").search("color") > -1 )
                $.publiquiz.question.shuffleItems($quiz.find("."+prefix+"CategoriesChoices"));

            // Shuffle "<tbody>" content for mode "grid"
            if ($quiz.data("engine-options") &&
                    $quiz.data("engine-options").search("grid") > -1 )
                $.publiquiz.question.shuffleItems($quiz.find("table tbody"));
        }
    },

    /**
     * Set event click on Choice.
     *
     * @param {Object} jquery Object quiz.
     */
    categoriesEnable: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        // ========== Event "draggable" on item for mode "basket"
        $.publiquiz.question.setDraggableItem($quiz, $quiz.find("."+prefix+"CategoryItem"), "Category");

        // ========== Event for mode "color"
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 ) {

            // Event "click" on category for mode "color"
            $quiz.find("."+prefix+"Category").click( function(ev) {
                var $target = $(this);
                while (!$target.hasClass(prefix+"Category"))
                    $target = $target.parentNode;
                $.publiquiz.question.categories._onCategory($quiz, $target);
            });

            // Event "click" for point
            $quiz.find("."+prefix+"Choice").click( function(ev) {
                var $target = $(this);
                while (!$target.hasClass(prefix+"Choice"))
                    $target = $target.parentNode;
                $.publiquiz.question.categories._onChoice($quiz, $target);
            });

        }

        // =========== Event for mode "grid"
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("grid") > -1 ) {

            $quiz.find("."+prefix+"CategoryChoice input").removeAttr("disabled");
            $quiz.find("."+prefix+"CategoryChoice").click( function(ev) {
                var $target = $(this);
                $.publiquiz.question.categories._onCategoryChoice($quiz, $target);
            });

        }
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesDisable: function($quiz) {
        var prefix = $quiz.data("prefix");

        // ========== Disable event "draggable" on item for mode "basket"
        var evtStart = "mousedown touchstart";
        var $items = $quiz.find("."+prefix+"CategoryItem");
        $items.unbind(evtStart);

        // ========== Disable event for mode "color"
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 ) {
            $quiz.find("."+prefix+"Choice").unbind("click");
            $quiz.find("."+prefix+"Category").unbind("click");
        }

        // =========== Disable Event for mode "grid"
        $quiz.find("."+prefix+"CategoryChoice").unbind("click");
        $quiz.find("."+prefix+"CategoryChoice input").attr("disabled", "disabled");
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    categoriesRetry: function($quiz) {
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("grid") > -1 )
            $.publiquiz.question.categories._retryCategoryChoices($quiz);
        else
            $.publiquiz.question.retryCategories($quiz);
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    categoriesComputeScore: function($quiz) {
        var noMark = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("nomark") > -1 )
            noMark = true;

        if (noMark) {
            var result = {};
            result.score = 0;
            result.total = 0;
            return result;
        }

        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 )
            return $.publiquiz.question.categories._computeScoreColor($quiz);
        else if ($quiz.data("engine-options") &&
                    $quiz.data("engine-options").search("grid") > -1 )
            return $.publiquiz.question.categories._computeScoreChoices($quiz);
        else
            return $.publiquiz.question.categories._computeScoreBasket($quiz);
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    categoriesInsertUserAnswers: function($quiz) {
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 )
            $.publiquiz.question.categories._insertUserAnswersColor($quiz);
        else if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("grid") > -1 )
            $.publiquiz.question.categories._insertUserAnswersChoices($quiz);
        else
            $.publiquiz.question.categories._insertUserAnswersBasket($quiz);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    categoriesQuizAnswer: function($quiz, mode) {
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 )
            $.publiquiz.question.categories._quizAnswersColor($quiz, mode);
        else if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("grid") > -1 )
            $.publiquiz.question.categories._quizAnswersChoices($quiz, mode);
        else
            $.publiquiz.question.categories._quizAnswersBasket($quiz, mode);
    },

    /**
     * Display user answer, replace one by one with correct answer
     * and color them
     *
     * @param {Object} $quiz : object jQuery publiquiz.
     */
    categoriesQuizTimerAnswerColor: function($quiz) {
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 )
            $.publiquiz.question.categories._quizTimerAnswersColor($quiz);
        else
            $.publiquiz.question.categories._quizTimerAnswersColorBasket($quiz);
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    categoriesVerifyUserAnswer: function($quiz) {
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 )
            $.publiquiz.question.categories._verifyAnswersColor($quiz, "user");
        else if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("grid") > -1 )
            $.publiquiz.question.categories._verifyAnswersChoices($quiz, "user");
        else
            $.publiquiz.question.categories._verifyAnswersBasket($quiz, "user");
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    categoriesVerifyRightAnswer: function($quiz) {
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 )
            $.publiquiz.question.categories._verifyAnswersColor($quiz, "right");
        else if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("grid") > -1 )
            $.publiquiz.question.categories._verifyAnswersChoices($quiz, "right");
        else
            $.publiquiz.question.categories._verifyAnswersBasket($quiz, "right");
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    categoriesVerifyFullAnswer: function($quiz) {
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("color") > -1 )
            $.publiquiz.question.categories._verifyAnswersColor($quiz, "full");
        else if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("grid") > -1 )
            $.publiquiz.question.categories._verifyAnswersChoices($quiz, "full");
        else
            $.publiquiz.question.categories._verifyAnswersBasket($quiz, "full");
    },


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

    /**
     * This function call when click on object with class pquizCategory.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizCategory.
     */
    _onCategory: function($quiz, $elem) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        $quiz.find("."+prefix+"Category").removeClass("selected");
        $elem.addClass("selected");
    },

    /**
     * This function call when click on object with class pquizChoice.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizPoint.
     */
    _onChoice: function($quiz, $elem) {
        $.publiquiz.question.clearVerify();
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var category = null;
        var color = null;
        var $selected = $quiz.find("."+prefix+"Category.selected");
        if ($selected.length > 0) {
            category = $selected.data("category-id");
            var $categoryColor = $selected.find("."+prefix+"CategoryColor");
            var $classList = $categoryColor.attr("class").split(/\s+/);
            color = $classList[$classList.length - 1];
        }

        if (!category)
            return;

        if (isMultiple) {
            // On verifie que le target n'appartient pas deja cette categorie si
            // c'est le cas on retire la categorie
            var hasCategory = false;
            $elem.find("."+prefix+"ItemColor").each( function() {
                var $item = $(this);
                if ($item.data("category-id") == category) {
                    $item.remove();
                    hasCategory = true;
                    return false;
                }
                return true;
            });

            if (hasCategory)
                return;

            // Ajout d'un item color
            var $item = $(document.createElement("span"));
            $item.addClass(prefix+"ItemColor " + color);
            $item.data("category-id", category);
            $item.appendTo($elem);

        } else {
            var classList = $elem.attr("class").split(/\s+/);
            if (classList.length > 1)
                $elem.removeClass(classList[classList.length - 1]);
            $elem.data("category-id", category);
            $elem.addClass(color);
        }
    },

    /**
     * This function call when click on object class pquizCategoryChoice.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @param {Object} Jquery object, object element pquizCategoryChoice.
     */
    _onCategoryChoice: function($quiz, $elem) {
        $.publiquiz.question.clearVerify();
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var $engine = $quiz.find("#"+quzId+"_engine");
        var $input = $elem.find("input");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        if ($elem.hasClass("selected")) {
            if (!isMultiple)
                return;
            $elem.removeClass("selected");
            if ($input)
                $input.prop("checked", false);
            return;
        }

        var group = $elem.data("group");
        if (!isMultiple) {
            $engine.find("."+prefix+"CategoryChoice")
                .filter("[data-group=\""+group+"\"]")
                .removeClass("selected");
        }
        $elem.addClass("selected");
        if ($input)
            $input.prop("checked", true);
    },

    /**
     * Retry quiz categories option grid, keep only right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _retryCategoryChoices: function($quiz) {
        $.publiquiz.question.clearVerify();
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var res = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));

        $quiz.find("."+prefix+"CategoryChoice").filter(".selected").each( function() {
            var $this = $(this);
            var grp = $this.data("group");
            var $item = $quiz.find("#"+quzId+"_item"+grp);
            if ($.inArray($item.data("item-value"),
                    res[$this.data("category-id")].split("|")) == -1) {
                $this.find("input").prop("checked", false);
                $this.removeClass("selected");
            }
        });
    },

    /**
     * This function compute score for categories mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Dictionnary}.
     */
    _computeScoreBasket: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var total = 0;
        var score = 0;
        var res = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));

        // Listes des intrus
        var values = [];
        var intrus = [];
        $.each(res, function(key, value) { values = $.merge(values, value.split("|")); });
        $quiz.find("."+prefix+"CategoryItem").each( function() {
            var $item = $(this);
            var value = $item.data("item-value").toString();
            if( $.inArray(value, values) == -1)
                intrus.push(value);
        });

        // Score
        $.each(res, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            // Vrai items
            $.each(value.split("|"), function(idx, data) {
                var $item = $dropbox.find("."+prefix+"CategoryItem")
                    .filter("[data-item-value=\""+data+"\"]");
                if ($item.length > 0)
                    score += 1;
                total += 1;
            });

            // Intrus
            $.each(intrus, function(idx, data) {
                var $item = $dropbox.find("."+prefix+"CategoryItem")
                    .filter("[data-item-value=\""+data+"\"]");
                if ($item.length > 0)
                    score -= 1;
            });
        });

        if (score < 0)
            score = 0;

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * This function compute score for categories mode "color".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Dictionnary}.
     */
    _computeScoreColor: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var score = 0;
        var total = 0;
        var res = $.publiquiz.question.correctionCategories(
            $quiz.find("#"+quzId+"_correct"));

        // Total
        $.each(res, function(key, value) {
            total += value.split("|").length;
        });

        // Score
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            var value = $choice.data("choice-value").toString();
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").each( function() {
                    var $item = $(this);
                    var category = $item.data("category-id");
                    if ($.inArray(value, res[category].split("|")) >= 0)
                        score += 1;
                });
            } else {
                var category = $choice.data("category-id");
                if (category && $.inArray(value, res[category].split("|")) >= 0)
                    score += 1;
            }
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * This function compute score for categories mode "grid".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @return {Dictionnary}.
     */
    _computeScoreChoices: function($quiz) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");

        var score = 0;
        var total = 0;
        var res = $.publiquiz.question.correctionCategories(
            $quiz.find("#"+quzId+"_correct"));
        var $engine = $quiz.find("#"+quzId+"_engine");

        // Get group
        var choices = [];
        $quiz.find("."+prefix+"CategoryChoice").each( function() {
            var group = $(this).data("group");
            if ($.inArray(group, choices) < 0 )
                choices.push(group);
        });

        // Compute score
        // Total
        $.each(res, function(key, value) {
            total += value.split("|").length;
        });
        // Score
        $.each(choices, function() {
            var group = this;
            var items = $engine.find("."+prefix+"CategoryChoice")
                            .filter("[data-group=\""+group+"\"]")
                            .filter(".selected");
            $.each(items, function() {
                var $item = $(this);
                var _$item = $engine.find("#"+quzId+"_item"+group);
                if ($.inArray(_$item.data("item-value"), 
                        res[$item.data("category-id")].split("|")) >= 0)
                    score += 1;
            });
        });

        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Insert user answers in html for mode "basket"
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    _insertUserAnswersBasket: function($quiz) {
        var answer = "";
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"CategoryDrop").each( function() {
            var $dropbox = $(this);
            var key = $dropbox.attr("id");
            key = key.substring(key.length - 3, key.length);
            $dropbox.find("."+prefix+"CategoryItem").each( function() {
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
     * Insert user answers in html for mode "color"
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    _insertUserAnswersColor: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;

        var answer = "";
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            var value = $choice.data("choice-value");
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").each( function() {
                    var $item = $(this);
                    var category = $item.data("category-id");
                    if (answer !== "")
                        answer += "::";
                    answer += category + value;
                });
            } else {
                var category = $choice.data("category-id");
                if (category) {
                    if (answer !== "")
                        answer += "::";
                    answer += category + value;
                }
            }
        });

        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Insert user answers in html for mode "grid"
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    _insertUserAnswersChoices: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");

        var answer = "";
        $quiz.find("."+prefix+"CategoryChoice").filter(".selected").each( function() {
            var $this = $(this);
            var grp = $this.data("group");
            var $item = $quiz.find("#"+quzId+"_item"+grp);
            var value = $item.data("item-value");
            if (answer !== "")
                answer += "::";
            answer += $this.data("category-id") + value;
        });

        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    _quizAnswersBasket: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+mode));
        var $items = $quiz.find("#"+quzId+"_items");

        // On enleve la correction
        if (isMultiple) {
            $quiz.find("."+prefix+"CategoryItemDropped").remove();
        } else {
            $quiz.find("."+prefix+"CategoryItemDropped").each( function() {
                var $item = $(this);
                $item.appendTo($items)
                    .removeClass(prefix+"CategoryItemDropped answerKo");
            });
        }

        // On place la correction en deplacant les items
        // ou bien en les clonant si "isMultiple" est a true
        $items.removeClass("answer");
        $.each(answers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            $dropbox.removeClass("answer");
            $.each(value.split("|"), function(idx, data) {
                var $item = $items.find("."+prefix+"CategoryItem").filter("[data-item-value=\""+data+"\"]");
                if (isMultiple)
                    $item = $item.clone();
                $item.appendTo($dropbox)
                    .addClass(prefix+"CategoryItemDropped");
            });

            if (mode == "_correct")
                $dropbox.addClass("answer");
        });
    },

    /**
     * Display correct answer one by one for quiz mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _quizTimerAnswersColorBasket: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_user"));
        $.each(userAnswers, function(idx, val) {
            userAnswers[idx] = val.split('|');
        });
        var $items = $quiz.find("#"+quzId+"_items");
        var timerValidation = $.publiquiz.defaults.timerValidation;

        $items.removeClass("answer");
        $.each(answers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            $dropbox.removeClass("answer");
            var values = value.split("|");

            // For each item in the category, remove the wrong answers.
            if (userAnswers[key]) {
                $.each(userAnswers[key], function(idx, data) {
                    var $item = $dropbox.find("."+prefix+"CategoryItem").filter("[data-item-value=\""+data+"\"]");
                    var valid = $.inArray(data, values) >= 0;
                    if (valid)
                        values.splice(values.indexOf(data), 1);

                    $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                    if (!valid) {
                        $('.publiquizAction').queue(function(next) {
                            if (isMultiple)
                                $item.remove();
                            else
                                $item.removeClass(prefix+"CategoryItemDropped").animateMoveElement($items);
                            next();
                        });
                    }
                    $('.publiquizAction').delay(timerValidation);
                });
            }

            // Then add right answers that were not given.
            $.each(values, function(idx, data) {
                var $item = $quiz.find("."+prefix+"CategoryItem").filter("[data-item-value=\""+data+"\"]");
                if ($quiz, $item.hasClass(prefix+"CategoryItemDropped")) {
                    var key = $item.parent().attr("id").substring((quzId+"_").length);
                    userAnswers[key].splice(userAnswers[key].indexOf(data), 1);
                }
                $.publiquiz.question.addClassColorAnswer($quiz, $item, false);
                $('.publiquizAction').queue(function(next) {
                    if (isMultiple)
                        $item = $item.clone().insertBefore($item);
                    $item.animateMoveElement($dropbox)
                        .queue(function(next) {
                            $item.addClass(prefix+"CategoryItemDropped");
                            next();
                        });
                    next();
                });
                $('.publiquizAction').delay(timerValidation);
            });

            $dropbox.addClass("answer");
        });
    },

    /**
     * Display right/user answer for quiz mode "color".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    _quizAnswersColor: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+mode));

        // On enleve la category selected
        $quiz.find("."+prefix+"Category").removeClass("selected");

        // On enleve les couleurs
        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").remove();
            } else {
                $choice.removeClass("answerOk answerKo");
                $choice.data("category-id", "");
                var classList = $choice.attr("class").split(/\s+/);
                if (classList.length > 1)
                    $choice.removeClass(classList[classList.length - 1]);
            }
        });

        // On place les couleurs de la correction
        $.each(answers, function(key, data) {
            var $category = $quiz.find("."+prefix+"Category")
                .filter("[data-category-id=\""+key+"\"]");
            var $categoryColor = $category.find("."+prefix+"CategoryColor");
            var $classList = $categoryColor.attr("class").split(/\s+/);
            var color = $classList[$classList.length-1];

            $.each(data.split("|"), function(idx, value) {
                var $choice = $quiz.find("."+prefix+"Choice")
                    .filter("[data-choice-value=\""+value+"\"]");
                if ($choice.length > 0) {
                    if (isMultiple) {
                        var $item = $(document.createElement("span"));
                        $item.addClass(prefix+"ItemColor " + color);
                        $item.data("category-id", key);
                        $item.appendTo($choice);
                    } else {
                        $choice.addClass(color);
                        $choice.data("category-id", key);
                    }
                }
            });
        });
    },

    /**
     * Display correct answer one by one for quiz mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    _quizTimerAnswersColor: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
            $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var timerValidation = $.publiquiz.defaults.timerValidation;
        var answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+"_correct"));
        var answersCategories = {};
        $.each(answers, function(cat, value) {
            var items = value.split('|');
            $.each(items, function(key, item) {
                if (answersCategories[item])
                    answersCategories[item].push(cat);
                else
                    answersCategories[item] = [cat];
            });
        });

        // On enleve la category selected
        $quiz.find("."+prefix+"Category").removeClass("selected");

        $quiz.find("."+prefix+"Choice").each(function() {
            var $choice = $(this);
            var value = $choice.data("choice-value");
            if (isMultiple) {
                // Check user answers
                $choice.find("."+prefix+"ItemColor").each( function() {
                    var $item = $(this);
                    var category = $item.data("category-id");
                    var valid = $.inArray(category, answersCategories[value]) >= 0;
                    $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                    if (!valid) {
                        $(".publiquizAction").queue(function(next) {
                            $item.remove();
                            next();
                        });
                    }
                    else {
                        answersCategories[value].splice(answersCategories[value].indexOf(category), 1);
                    }
                    $(".publiquizAction").delay(timerValidation);
                });
                // Complete correct answers
                $.each(answersCategories[value], function(key, cat) {
                    var $category = $quiz.find("."+prefix+"Category")
                            .filter("[data-category-id=\""+cat+"\"]");
                    var $categoryColor = $category.find("."+prefix+"CategoryColor");
                    var $classList = $categoryColor.attr("class").split(/\s+/);
                    var color = $classList[$classList.length-1];
                    var $item = $(document.createElement("span"));
                    $(".publiquizAction").queue(function(next) {
                        $item.addClass(prefix+"ItemColor " + color);
                        $item.data("category-id", cat);
                        $item.appendTo($choice);
                        next();
                    });
                    $.publiquiz.question.addClassColorAnswer($quiz, $item, false);
                    $(".publiquizAction").delay(timerValidation);
                });
            }
            else {
                console.error("TODO");
            }
        });
    },

    /**
     * Display right/user answer for quiz mode "grid".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    _quizAnswersChoices: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answers = $.publiquiz.question.correctionCategories($quiz.find("#"+quzId+mode));

        // Reset quiz
        $quiz.find("."+prefix+"CategoryChoice input").prop("checked", false);
        $quiz.find("."+prefix+"CategoryChoice").removeClass(
                "selected answerOk answerKo");

        $.each(answers, function(key, data) {
            var values = data.split("|");
            var $items = $quiz.find("."+prefix+"CategoryChoice")
                            .filter("[data-category-id=\""+key+"\"]");
            $items.each(function() {
                var $this = $(this);
                var grp = $this.data("group");
                var $item = $quiz.find("#"+quzId+"_item"+grp);
                var value = $item.data("item-value");
                if ($.inArray($item.data("item-value"), values) >= 0) {
                    $this.find("input").prop("checked", true);
                    $this.addClass("selected");
                }
            });
        });
    },

    /**
     * Verify user answer for mode "basket".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    _verifyAnswersBasket: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var rightAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_user"));
        var $items = $quiz.find("#"+quzId+"_items");

        var timerValidation = $.publiquiz.defaults.timerValidation;
        var paramWrongAnswers = $.publiquiz.defaults.wrongAnswers;
        $.each(rightAnswers, function(key, value) {
            var $dropbox = $quiz.find("#"+quzId+"_"+key);
            $dropbox.addClass("answer");
            var values = value.split("|");
            $dropbox.find("."+prefix+"CategoryItem").each( function() {
                var $item = $(this);
                var data = $item.data("item-value").toString();
                var valid;
                if (mode == "user") {
                    valid = $.inArray(data, values) >= 0;
                    $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                    if (!valid && paramWrongAnswers == "clear") {
                        $('.publiquizAction').queue(function(next) {
                            if (isMultiple)
                                $item.remove();
                            else
                                $item.removeClass(prefix+"CategoryItemDropped").animateMoveElement($items);
                            next();
                        });
                    }
                    $('.publiquizAction').delay(timerValidation);
                } else if (mode == "right") {
                    if ($.inArray(data, values) >= 0)
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, true);
                } else {
                    var userAnswer = userAnswers[key];
                    if (userAnswer) {
                        userAnswer = userAnswer.split("|");
                        if ($.inArray(data, values) >= 0 && $.inArray(data, userAnswer) >= 0)
                            $.publiquiz.question.addClassColorAnswer($quiz, $item, true);
                        else
                            $.publiquiz.question.addClassColorAnswer($quiz, $item, false);
                    } else {
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, false);
                    }
                }

            });

        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }

        if (mode == "user" || isMultiple)
            return;

        // Gestion des intrus
        var $items = $quiz.find("#"+quzId+"_items");
        $items.addClass("answer");
        $items.find("."+prefix+"CategoryItem").each( function() {
            var $item = $(this);
            var value = $item.data("item-value").toString();
            var used = false;
            var isIntru = true;
            $.each(userAnswers, function(k, v) {
                if ($.inArray(value, v.split("|")) > -1) {
                    used = true;
                    return false;
                }
                return true;
            });
            $.each(rightAnswers, function(k, v) {
                if ($.inArray(value, v.split("|")) > -1) {
                    isIntru = false;
                    return false;
                }
                return true;
            });

            if (isIntru && !used)
                $item.addClass("answerOk");
            else
                if (mode != "right")
                    $item.addClass("answerKo");
        });
    },

    /**
     * Verify user answer for mode "color".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    _verifyAnswersColor: function($quiz, mode) {
        var prefix = $quiz.data("prefix");
        var quzId = $quiz.data("quiz-id");
        var isMultiple = false;
        if ($quiz.data("engine-options") &&
                $quiz.data("engine-options").search("multiple") > -1 )
            isMultiple = true;
        var timerValidation = $.publiquiz.defaults.timerValidation;
        var rightAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_user"));

        $quiz.find("."+prefix+"Choice").each( function() {
            var $choice = $(this);
            var value = $choice.data("choice-value").toString();
            if (isMultiple) {
                $choice.find("."+prefix+"ItemColor").each( function() {
                    var $item = $(this);
                    var category = $item.data("category-id");
                    if (mode == "user") {
                        var valid = $.inArray(value, rightAnswers[category].split("|")) >= 0;
                        $.publiquiz.question.addClassColorAnswer($quiz, $item, valid);
                        if (!valid) {
                            $(".publiquizAction").queue(function(next) {
                                $item.remove();
                                next();
                            });
                        }
                        $(".publiquizAction").delay(timerValidation);
                    } else if (mode == "right") {
                        if ($.inArray(value, rightAnswers[category].split("|")) >= 0)
                            $item.addClass("answerOk");
                    } else {
                        var userAnswer = userAnswers[category];
                        var rightAnswer = rightAnswers[category].split("|");
                        if (userAnswer) {
                            userAnswer = userAnswer.split("|");
                            if ($.inArray(value, userAnswer) >= 0 && $.inArray(value, rightAnswer) >= 0)
                                $item.addClass("answerOk");
                            else
                                $item.addClass("answerKo");
                        } else {
                            $item.addClass("answerKo");
                        }
                    }
                });
            } else {
                var category = $choice.data("category-id");
                var rightAnswer = null;
                if (mode == "user") {
                    if (category) {
                        rightAnswer = rightAnswers[category].split("|");
                        if ($.inArray(value, rightAnswer) > -1)
                            $choice.addClass("answerOk");
                        else
                            $choice.addClass("answerKo");
                    }
                } else if (mode == "right") {
                    if (category) {
                        rightAnswer = rightAnswers[category].split("|");
                        if ($.inArray(value, rightAnswer) > -1)
                            $choice.addClass("answerOk");
                    }
                } else {
                    var userAnswer = userAnswers[category];
                    rightAnswer = rightAnswers[category].split("|");
                    if (userAnswer) {
                        userAnswer = userAnswer.split("|");
                        if ($.inArray(value, userAnswer) >= 0 && $.inArray(value, rightAnswer) >= 0)
                            $choice.addClass("answerOk");
                        else
                            $choice.addClass("answerKo");
                    } else {
                        $choice.addClass("answerKo");
                    }
                }
            }
        });

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    },

    /**
     * Verify user answer for mode "grid".
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : "full", "right" or "user" color.
     */
    _verifyAnswersChoices: function($quiz, mode) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var rightAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_correct"));
        var userAnswers = $.publiquiz.question.correctionCategories(
                $quiz.find("#"+quzId+"_user"));

        if (mode == "user") {
            $quiz.find("."+prefix+"CategoryChoice").filter(".selected").each( function() {
                var $this = $(this);
                var grp = $this.data("group");
                var $item = $quiz.find("#"+quzId+"_item"+grp);
                if ($.inArray($item.data("item-value"),
                        rightAnswers[$this.data("category-id")].split("|")) >= 0)
                    $this.addClass("answerOk");
                else
                    $this.addClass("answerKo");
            });
        } else if (mode == "right") {
            $quiz.find("."+prefix+"CategoryChoice").filter(".selected").each( function() {
                var $this = $(this);
                var grp = $this.data("group");
                var $item = $quiz.find("#"+quzId+"_item"+grp);
                if ($.inArray($item.data("item-value"),
                        rightAnswers[$this.data("category-id")].split("|")) >= 0)
                    $this.addClass("answerOk");
            });
        } else {
            $quiz.find("."+prefix+"CategoryChoice").filter(".selected").each( function() {
                var $this = $(this);
                var grp = $this.data("group");
                var $item = $quiz.find("#"+quzId+"_item"+grp);

                if (userAnswers[$this.data("category-id")]) {
                    if ($.inArray($item.data("item-value"),
                            userAnswers[$this.data("category-id")].split("|")) >= 0)
                        $this.addClass("answerOk");
                    else
                        $this.addClass("answerKo");
                } else {
                    $this.addClass("answerKo");
                }

            });
        }

        var duration = $quiz.data("verify-duration");
        if (duration < 0) {
            var timer = setTimeout($.publiquiz.question.clearVerify, duration);
            $.publiquiz.question.timers.push(timer);
        }
    }

};

// Register function
$.publiquiz.question.register("categories", {
        configure: $.publiquiz.question.categories.categoriesConfigure,
        enable: $.publiquiz.question.categories.categoriesEnable,
        disable: $.publiquiz.question.categories.categoriesDisable,
        help: $.publiquiz.question.categories.categoriesHelp,
        retry: $.publiquiz.question.categories.categoriesRetry,
        textAnswer: $.publiquiz.question.categories.categoriesTextAnswer,
        insertUserAnswers: $.publiquiz.question.categories.categoriesInsertUserAnswers,
        quizAnswer: $.publiquiz.question.categories.categoriesQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.categories.categoriesQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.categories.categoriesVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.categories.categoriesVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.categories.categoriesVerifyFullAnswer,
        computeScore: $.publiquiz.question.categories.categoriesComputeScore,
        quizScore: $.publiquiz.question.categories.categoriesScore
    });

}(jQuery));



/******************************************************************************
 *
 *                              Production
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.question.production = {

    /**
     * Configure quiz.
     */
    productionConfigure: function($quiz) {
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    productionEnable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Production").each( function() {
            var $this= $(this);
            $this.removeAttr("disabled");
            $this.removeClass("disabled");
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Production").each( function() {
            var $this= $(this);
            $this.attr("disabled", "true");
            $this.addClass("disabled");
        });
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    productionRetry: function($quiz) {
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    productionComputeScore: function($quiz) {
        var result = {};
        result.score = 0;
        result.total = 0;
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionTextAnswer: function($quiz) {
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    productionInsertUserAnswers: function($quiz) {
        var quzId = $quiz.data("quiz-id");
        var prefix = $quiz.data("prefix");
        var answer = $("."+prefix+"Production").val();
        answer = answer.replace(/\n/g, "#R#");
        $.publiquiz.question.writeUserAnswers($quiz, quzId, answer);
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    productionQuizAnswer: function($quiz, mode) {
    },

    /**
     * Display user answer, replace one by one with correct answer
     * and color them
     *
     * @param {Object} $quiz : object jQuery publiquiz.
     */
    productionQuizTimerAnswerColor: function($quiz) {
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    productionVerifyAnswer: function($quiz) {
    }


    /**********************************************************************
     *                          Private Library
    **********************************************************************/

};

// Register function
$.publiquiz.question.register("production", {
        configure: $.publiquiz.question.production.productionConfigure,
        enable: $.publiquiz.question.production.productionEnable,
        disable: $.publiquiz.question.production.productionDisable,
        help: $.publiquiz.question.production.productionHelp,
        retry: $.publiquiz.question.production.productionRetry,
        textAnswer: $.publiquiz.question.production.productionTextAnswer,
        insertUserAnswers: $.publiquiz.question.production.productionInsertUserAnswers,
        quizAnswer: $.publiquiz.question.production.productionQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.production.productionQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.production.productionVerifyAnswer,
        verifyRightAnswer: $.publiquiz.question.production.productionVerifyAnswer,
        verifyFullAnswer: $.publiquiz.question.production.productionVerifyAnswer,
        computeScore: $.publiquiz.question.production.productionComputeScore,
        quizScore: $.publiquiz.question.production.productionScore
    });

}(jQuery));


/******************************************************************************
 *
 *                              Composite
 *
******************************************************************************/

(function ($) {

"use strict";

$.publiquiz.question.composite = {

    /**
     * Configure quiz.
     */
    compositeConfigure: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            var elementId = $element.data("quiz-id");
            $element.data("prefix", prefix);
            $element.data("verify-duration", $.publiquiz.defaults.verifyDuration);

            // Register score function
            $.publiquiz.question.registerScoreFunc(
                    elementId,
                    $element,
                    $.publiquiz.question.computeScore[subEngine]
                );

            // Set button events
            $element.find("."+prefix+"Button").click( function(ev) {
                ev.preventDefault();
                var $btn = $(this);
                var id = $btn.attr("id");
                if (id.search("_help-link") != -1 ) {
                    $.publiquiz.question.help[subEngine]($element);
                }
            });

            // Configure sub quiz
            $.publiquiz.question.configure[subEngine]($element);
        });
    },

    /**
     * Set event click on point.
     *
     * @param {Object} jquery Object quiz.
     */
    compositeEnable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.enable[subEngine]($element);
            $.publiquiz.question.hideTextAnswer($element);
        });
    },

    /**
     * Remove events listener on quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeDisable: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.disable[subEngine]($element);
        });
    },

    /**
     * Display help of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeHelp: function($quiz) {
        $.publiquiz.question.displayHelp($quiz);
    },

    /**
     * Retry quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    compositeRetry: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.retry[subEngine]($element);
        });
    },

    /**
     * Compute score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     * @return {Dictionnary}.
     */
    compositeComputeScore: function($quiz) {
        var prefix = $quiz.data("prefix");
        var score = 0;
        var total = 0;
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            var res = $.publiquiz.question.computeScore[subEngine]($element);
            score += res.score;
            total += res.total;
        });
        var result = {};
        result.score = score;
        result.total = total;
        return result;
    },

    /**
     * Display score of quiz.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeScore: function($quiz) {
    },

    /**
     * Display quiz text answer.
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeTextAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.textAnswer[subEngine]($element);
        });
        $.publiquiz.question.displayTextAnswer($quiz);
    },

    /**
     * Insert user answers in html
     *
     * @params {Object} $quiz : object jquery quiz.
     */
    compositeInsertUserAnswers: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.insertUserAnswers[subEngine]($element);
        });
    },

    /**
     * Display right/user answer for quiz.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     * @params {String} mode : display correct/user answer.
     */
    compositeQuizAnswer: function($quiz, mode) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.quizAnswer[subEngine]($element, mode);
        });
    },

    /**
     * Display user answer, replace one by one with correct answer
     * and color them
     *
     * @param {Object} $quiz : object jQuery publiquiz.
     */
    compositeQuizTimerAnswerColor: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.quizTimerAnswerColor[subEngine]($element);
        });
    },

    /**
     * Verify user answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    compositeVerifyUserAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.verifyUserAnswer[subEngine]($element);
        });
    },

    /**
     * Verify right answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    compositeVerifyRightAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.verifyRightAnswer[subEngine]($element);
        });
    },

    /**
     * Verify full answer.
     *
     * @params {Object} $quiz : object jquery publiquiz.
     */
    compositeVerifyFullAnswer: function($quiz) {
        var prefix = $quiz.data("prefix");
        $quiz.find("."+prefix+"Element").each( function() {
            var $element = $(this);
            var subEngine = $element.data("engine");
            $.publiquiz.question.verifyFullAnswer[subEngine]($element);
        });
    }
};

// Register function
$.publiquiz.question.register("composite", {
        configure: $.publiquiz.question.composite.compositeConfigure,
        enable: $.publiquiz.question.composite.compositeEnable,
        disable: $.publiquiz.question.composite.compositeDisable,
        help: $.publiquiz.question.composite.compositeHelp,
        retry: $.publiquiz.question.composite.compositeRetry,
        textAnswer: $.publiquiz.question.composite.compositeTextAnswer,
        insertUserAnswers: $.publiquiz.question.composite.compositeInsertUserAnswers,
        quizAnswer: $.publiquiz.question.composite.compositeQuizAnswer,
        quizTimerAnswerColor: $.publiquiz.question.composite.compositeQuizTimerAnswerColor,
        verifyUserAnswer: $.publiquiz.question.composite.compositeVerifyUserAnswer,
        verifyRightAnswer: $.publiquiz.question.composite.compositeVerifyRightAnswer,
        verifyFullAnswer: $.publiquiz.question.composite.compositeVerifyFullAnswer,
        computeScore: $.publiquiz.question.composite.compositeComputeScore,
        quizScore: $.publiquiz.question.composite.compositeScore
    });

}(jQuery));
