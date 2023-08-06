/**
 * @projectDescription publiquiz_loader.js
 * Javascript quiz loader.
 *
 * @author prismallia.fr
 * @version 0.2
 * $Id: publiquiz_loader.js 199887c8ebb8 2016/01/25 18:51:32 Sylvain $
 *
 * 0.2 :
 *  Add publiquizAction, now we have 2 parts for quiz
 *      - questions : includes instruction, engine and button of quiz (help,...)
 *      - actions : manage all actions on quiz validate, retry, show answer...
 *          and scenario for action description.
 * 0.1 :
 *   Initial release.
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


"use strict";

jQuery(document).ready( function($) {
    // Publiquiz question plug-in
    var $questions = $(".publiquiz");
    var validationMode = $questions.data("engine-validation");
    var $action;
    if (!validationMode) {
        $questions.publiquiz();

        // Publiquiz action plug-in
        var $action = $(".publiquizAction");
        $action.publiquiz({
            "questions": $questions,
            "scenario": {
                "validate": [
                    ["hide(Submit)", "validate", "showMessage", "goto(maxRetry, 1, 2)"],
                    ["userColor", "show(Retry)"],
                    ["score", "answerText", "rightAnswer", "fullColor", "show(UserAnswer)"]
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
    }
    else if (validationMode == "double") {
        $.publiquiz.defaults.timerValidation = 800;
        $.publiquiz.defaults.wrongAnswers = "clear";

        $questions.publiquiz();

        $action = $(".publiquizAction");
        $action.publiquiz({
            "questions": $questions,
            "scenario": {
                "validate": [
                    ["hide(Submit)", "validate", "goto(maxRetry, 1, 2)"],
                    ["userColor", "show(Retry)"],
                    ["showMessage", "score", "answerText", "timerAnswerColor"]
                ],
                "retry": [
                    ["hide(Retry)", "retry", "show(Submit)", "set(validate, 0)"]
                ]
            }
        });
    }
});
