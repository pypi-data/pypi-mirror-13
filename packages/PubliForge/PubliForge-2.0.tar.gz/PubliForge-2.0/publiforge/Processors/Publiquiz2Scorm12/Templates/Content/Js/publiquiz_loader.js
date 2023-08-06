// $Id: publiquiz_loader.js 92e17f1c3176 2015/08/05 08:03:09 Coraline $

/*jshint globalstrict: true*/
/*global jQuery: true */
/*global LMSInitialize: true */
/*global LMSFinish: true */
/*global LMSGetValue: true */
/*global LMSSetValue: true */
/*global LMSCommit: true */

"use strict";


jQuery(document).ready(function($) {
    // ========================================================================
    //                               SCORM ACTION
    // ========================================================================

    $.publiquiz.action.actionCustom = function($action, name, args) {
        if (name == "scormScore") {
            var score = $.publiquiz.question.computeGlobalScore(
                $action.questions);
            var threshold = parseFloat(
                $action.children(".pquizSuccessThreshold").text());
            if (score.total) {
                LMSSetValue("cmi.core.score.min", 0);
                LMSSetValue("cmi.core.score.max", score.total);
                LMSSetValue("cmi.core.score.raw", score.score);
                if (score.score / score.total >= threshold)
                    LMSSetValue("cmi.core.lesson_status", "passed");
                else
                    LMSSetValue("cmi.core.lesson_status", "failed");
                LMSCommit();
            }
        }
    };

    // ========================================================================
    //                                  LOADER
    // ========================================================================

    // Publiquiz default options
    var prefix = "pquiz";
    $.publiquiz.defaults.prefix = prefix;

    // Publiquiz question plug-in
    var $questions = $(".publiquiz");
    $questions.publiquiz();

    // Publiquiz action plug-in
    var $action = $(".publiquizAction");
    $action.publiquiz({
        "questions": $questions,
        "scenario": {
            "validate": [
                ["hide(Submit)", "validate", "showMessage", "goto(maxRetry, 1, 2)"],
                ["userColor", "show(Retry)"],
                ["score", "scormScore", "answerText", "rightAnswer", "fullColor", "show(UserAnswer)"]
            ],
            "verify": [
                ["userColor"]
            ],
            "retry": [
                ["hide(Retry)", "retry", "show(Submit)", "set(validate, 0)"]
            ],
            "userAnswer": [
                ["hide(UserAnswer)", "show(RightAnswer)", "userAnswer", "userColor"]
            ],
            "rightAnswer": [
                ["hide(RightAnswer)", "show(UserAnswer)", "rightAnswer", "fullColor"]
            ]
        }
    });

    // SCORM initialization
    LMSInitialize();
    // LMSSetValue("cmi.core.lesson_status", "incomplete");

    // SCORM finalization
    // //$(window).bind('beforeunload', function() {
    $(window).unload(function() {
        // LMSSetValue("cmi.core.lesson_status", "completed");
        // LMSSetValue("cmi.core.exit", "logout");
        LMSFinish();
    });
});
