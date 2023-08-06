// $Id: publiquiz_schema.js 0f26fe80e742 2015/12/04 11:11:06 Coraline $

/*jshint globalstrict: true*/
/*global jQuery: true */

"use strict";

(function($) {


// ****************************************************************************
//                               PUBLIQUIZ SCHEMA
// ****************************************************************************

if (!$.publiquiz) $.publiquiz = {};

$.publiquiz.schemaEngine = [
    "choices-radio", "choices-check", "blanks-fill", "blanks-select",
    "blanks-char", "pointing", "pointing-categories", "matching", "sort",
    "categories", "production"];

$.publiquiz.schemaBlockBlanks = [
    "blanks.p", "blanks.list", "blanks.blockquote", "blanks.speech",
    "table", "media"];
$.publiquiz.schemaBlockPointing = [
    "pointing.p", "pointing.list", "pointing.blockquote", "pointing.speech",
    "table", "media"];

$.publiquiz.schemaInlineBlanks = $.publidoc.schemaInline.concat(["blank"]);
$.publiquiz.schemaInlinePointing = $.publidoc.schemaInline.concat(["point"]);

$.publiquiz.schema = $.extend(
    $.publidoc.schema,
    {
        // ------ DIVISION ----------------------------------------------------
        ".division": {
            content: [["division", "topic", "quiz"]]
        },
        division: {
            attributes: { type: null, "xml:lang": $.publidoc.schemaAttLang },
            content: [["division.head", "division", "topic", "quiz"]]
        },

        // ------ COMPONENT ---------------------------------------------------
        quiz: {
            attributes: {
                id: null,
                type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["component.head", "instructions", "composite", "help",
                       "answer"].concat($.publiquiz.schemaEngine)]
        },

        // ------ SECTION -----------------------------------------------------
        ".instructions": {
            content: [["section.head", "section"],
                      ["section.head"].concat($.publidoc.schemaBlock)]
        },
        instructions: {
            content: [["section.head", "section"],
                      ["section.head"].concat($.publidoc.schemaBlock)]
        },

        "blanks.section": {
            element: "section",
            attributes: {
                "xml:id": null, type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["section.head", "blanks.section"],
                      ["section.head"].concat($.publiquiz.schemaBlockBlanks)],
            seed: "<section><p e4x='here'/></section>"
        },
        "pointing.section": {
            element: "section",
            attributes: {
                "xml:id": null, type: null,
                "xml:lang": $.publidoc.schemaAttLang },
            content: [["section.head", "pointing.section"],
                      ["section.head"].concat($.publiquiz.schemaBlockPointing)],
            seed: "<section><p e4x='here'/></section>"
        },

        ".help": {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },
        help: {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },
        ".answer": {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },
        answer: {
            content: [["section", "link"], $.publidoc.schemaBlock]
        },

        // ------ SECTION - Choices -------------------------------------------
        "choices-radio": {
            type: "radio",
            rightElement: "right",
            wrongElement: "wrong",
            attributes: { shuffle: ["true", "false"] },
            content: [["right", "wrong"]]
        },
        "choices-check": {
            type: "checkbox",
            rightElement: "right",
            wrongElement: "wrong",
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                shuffle: ["true", "false"] },
            content: [["right", "wrong"]]
        },
        right: {
            content: [["p", "image", "audio", "video", "help", "answer"],
                      $.publidoc.schemaInline]
        },
        wrong: {
            content: [["p", "image", "audio", "video", "help", "answer"],
                      $.publidoc.schemaInline]
        },

        // ------ SECTION - Blanks --------------------------------------------
        "blanks-fill": {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                strict: ["true", "false"], long: null },
            content: [["blanks.section"], $.publiquiz.schemaBlockBlanks]
        },

        "blanks-select": {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                multiple: ["true", "false"], "no-shuffle": ["true", "false"] },
            content: [["blanks.intruders", "blanks.section"],
                      ["blanks.intruders"].concat(
                          $.publiquiz.schemaBlockBlanks)]
        },

        "blanks-char": {
            attributes: {
                "remove-space": ["true", "false"] },
            content: [["blanks.intruders", "blanks.section"],
                      ["blanks.intruders"].concat(
                          $.publiquiz.schemaBlockBlanks)]
        },
        "blanks.intruders": {
            element: "intruders",
            content: [["blank"]]
        },

        // ------ SECTION - Pointing ------------------------------------------
        pointing: {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                type: ["radio", "check"] },
            content: [["pointing.section"],
                      $.publiquiz.schemaBlockPointing]
        },
        "pointing-categories": {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"] },
            content: [["pointing-c.categories", "pointing.section"]]
        },
        "pointing-c.categories": {
            element: "categories",
            content: [["pointing-c.category"]]
        },
        "pointing-c.category": {
            element: "category",
            attributes: { id: ["1", "2", "3", "4", "5"] },
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Matching ------------------------------------------
        matching: {
            intrudersElement: "intruders",
            matchElement: "match",
            itemElement: "item",
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                multiple: ["true", "false"] },
            content: [["matching.intruders", "match"]]
        },
        "matching.intruders": {
            element: "intruders",
            content: [["match.item"]]
        },
        match: {
            content: [["match.item"]]
        },
        "match.item": {
            element: "item",
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Sort ----------------------------------------------
        sort: {
            comparisonElement: "comparison",
            itemElement: "item",
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                shuffle: ["true", "false"] },
            content: [["comparison", "sort.item"]]
        },
        comparison: {
            content: [[".text"]]
        },
        "sort.item": {
            element: "item",
            attributes: {
                shuffle: ["1", "2", "3", "4", "5", "6", "7", "8", "9",
                          "10", "11", "12", "13", "14", "15"] },
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Categories ----------------------------------------
        categories: {
            intrudersElement: "intruders",
            categoryElement: "category",
            headElement: "head",
            itemElement: "item",
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                multiple: ["true", "false"], "no-shuffle": ["true", "false"] },
            content: [["category.intruders", "category"]]
        },
        "category.intruders": {
            element: "intruders",
            content: [["category.item"]]
        },
        category: {
            content: [["category.head", "category.item"]]
        },
        "category.head": {
            element: "head",
            content: [["title", "shorttitle", "subtitle"]]
        },
        "category.item": {
            element: "item",
            content: [$.publidoc.schemaInline]
        },

        // ------ SECTION - Production ----------------------------------------
        production: {
            content: [[]]
        },

        // ------ SECTION - Composite -----------------------------------------
        composite: {
            attributes: {
                success: ["1",".9",".8",".7",".6",".5",".4",".3",".2",".1"],
                multipage: ["true", "false"] },
            content: [["subquiz"]]
        },
        subquiz: {
            content: [["instructions", "help", "answer"]
                      .concat($.publiquiz.schemaEngine)]
        },

        // ------ BLOCK -------------------------------------------------------
        "blanks.p": {
            element: "p",
            content: [$.publiquiz.schemaInlineBlanks]
        },
        "pointing.p": {
            element: "p",
            content: [$.publiquiz.schemaInlinePointing]
        },

        "blanks.list": {
            element: "list",
            attributes: { type: ["ordered", "glossary"] },
            content: [["block.head", "blanks.item"]],
            seed: "<list><item e4x='here'/><item e4x='hold'/></list>"
        },
        "pointing.list": {
            element: "list",
            attributes: { type: ["ordered", "glossary"] },
            content: [["block.head", "pointing.item"]],
            seed: "<list><item e4x='here'/><item e4x='hold'/></list>"
        },
        "blanks.item": {
            element: "item",
            content: [["label"].concat($.publiquiz.schemaBlockBlanks),
                      $.publiquiz.schemaInlineBlanks]
        },
        "pointing.item": {
            element: "item",
            content: [["label"].concat($.publiquiz.schemaBlockPointing),
                      $.publiquiz.schemaInlinePointing]
        },

        "blanks.blockquote": {
            element: "blockquote",
            attributes: { type: null },
            content: [["block.head", "blanks.p", "blanks.list",
                       "blanks.speech", "attribution"]],
            seed: "<blockquote><p e4x='here'/><attribution e4x='hold'/>"
                + "</blockquote>"
        },
        "pointing.blockquote": {
            element: "blockquote",
            attributes: { type: null },
            content: [["block.head", "pointing.p", "pointing.list",
                       "pointing.speech", "attribution"]],
            seed: "<blockquote><p e4x='here'/><attribution e4x='hold'/>"
                + "</blockquote>"
        },

        "blanks.speech": {
            element: "speech",
            content: [["speaker", "stage", "blanks.p",
                       "blanks.blockquote"]],
            seed: "<speech><speaker e4x='hold'/><stage e4x='hold'/>"
                + "<p e4x='here'/></speech>"
        },
        "pointing.speech": {
            element: "speech",
            content: [["speaker", "stage", "pointing.p",
                       "pointing.blockquote"]],
            seed: "<speech><speaker e4x='hold'/><stage e4x='hold'/>"
                + "<p e4x='here'/></speech>"
        },

        // ------ INLINE ------------------------------------------------------
        blank: {
            content: [[".text"], ["s"]],
            attributes: {
                area: ["true", "false"],
                long: null,
                function: ["uppercase", "accent"] }
        },
        s: {
            content: [[".text"]]
        },
        point: {
            attributes: {
                ref: ["right", "cat1", "cat2", "cat3", "cat4", "cat5"] },
            content: [$.publidoc.schemaInline]
        }
    }
);


})(jQuery);
