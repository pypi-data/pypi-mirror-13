// $Id: publidoc_schema.js 0736afc93bf0 2015/11/12 17:59:51 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */

"use strict";

(function($) {


// ****************************************************************************
//                                PUBLIDOC SCHEMA
// ****************************************************************************

if (!$.publidoc) $.publidoc = {};

$.publidoc.schemaBlock = [
    "p", "list", "blockquote", "speech", "table", "media"];

$.publidoc.schemaSimpleInline = [
    ".text", "sup", "sub", "var", "number", "acronym"];

$.publidoc.schemaInline = $.publidoc.schemaSimpleInline.concat([
    "highlight", "emphasis", "mentioned", "literal", "term", "stage", "name",
    "foreign", "date", "math", "quote", "initial", "note", "link", "anchor",
    "image", "audio", "smil"]);

$.publidoc.schemaAttLang = ["en", "fr", "es", "it"];
$.publidoc.schemaSectionAttType = ["box", "ex", "insert", "sign"];
$.publidoc.schemaMediaAttType = ["insert", "logo"];

$.publidoc.schema = {
    // ------ HEAD ------------------------------------------------------------
    "top.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle", "identifier",
                   "copyright", "collection", "contributors", "date", "place",
                   "source", "keywordset", "subjectset", "abstract", "cover",
                   "annotation"]]
    },
    "division.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle", "abstract", "annotation"]]
    },
    "component.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle", "contributors", "date",
                   "place", "keywordset", "subjectset", "abstract",
                   "annotation"]]
    },
    "section.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle", "keywordset",
                   "subjectset", "abstract", "audio", "annotation"]]
    },
    "block.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle", "annotation"]]
    },

    title: {
        isFirst: true,
        content: [$.publidoc.schemaInline]
    },
    shorttitle: {
        content: [$.publidoc.schemaInline]
    },
    subtitle: {
        content: [$.publidoc.schemaInline]
    },

    identifier: {
        attributes: { type: ["ean", "uri"], for: null },
        content: [[".text"]]
    },
    "identifier.ean": {
        element: "identifier",
        attributes: { type: ["ean"], for: null },
        content: [[".text"]],
        seed: "<identifier type='ean' e4x='here'/>"
    },
    "identifier.uri": {
        element: "identifier",
        attributes: { type: ["uri"], for: null },
        content: [[".text"]],
        seed: "<identifier type='uri' e4x='here'/>"
    },

    copyright: {
        content: [$.publidoc.schemaSimpleInline]
    },

    collection: {
        content: [$.publidoc.schemaSimpleInline]
    },

    ".contributors": {
        content: [["contributor"]]
    },
    contributors: {
        content: [["contributor"]]
    },
    contributor: {
        content: [["identifier.uri", "firstname", "lastname", "label",
                   "address", "link", "role"]],
        seed: "<contributor><firstname e4x='hold'/><lastname e4x='here'/>"
            + "<role>author</role></contributor>"
    },
    firstname: {
        content: [$.publidoc.schemaSimpleInline]
    },
    lastname: {
        content: [$.publidoc.schemaSimpleInline]
    },
    label: {
        content: [$.publidoc.schemaSimpleInline]
    },
    address: {
        content: [$.publidoc.schemaSimpleInline]
    },
    role: {
        content: [[".text"]]
    },

    place: {
        content: [$.publidoc.schemaSimpleInline]
    },

    source: {
        attributes: { type: ["book", "file"] },
        content: [["identifier.uri", "annotation"],
                  ["identifier.ean", "title", "subtitle", "copyright",
                   "collection", "contributors", "date", "place", "folio",
                   "pages", "annotation"]]
    },
    folio: {
        content: [[".text"]]
    },
    pages: {
        content: [[".text"]]
    },

    ".keywordset": {
        content: [["keyword"]]
    },
    keywordset: {
        content: [["keyword"]]
    },
    keyword: {
        content: [$.publidoc.schemaSimpleInline]
    },
    ".subjectset": {
        content: [["subject"]]
    },
    subjectset: {
        content: [["subject"]]
    },
    subject: {
        content: [$.publidoc.schemaSimpleInline]
    },

    ".abstract": {
        content: [["p"]]
    },
    abstract: {
        content: [["p"]]
    },

    cover: {
        content: [["image"]]
    },

    annotation: {
        content: [["p"], $.publidoc.schemaInline]
    },

    // ------ DIVISION --------------------------------------------------------
    ".division": {
        content: [["division", "topic"]]
    },
    division: {
        attributes: { type: null, "xml:lang": $.publidoc.schemaAttLang },
        content: [["division.head", "front", "division", "topic"]],
        seed: "<division><head><title e4x='here'/></head>"
            + "<topic><head><title e4x='hold'/></head>"
            + "<section><p e4x='hold'/></section></topic></division>"
    },

    front: {
        content: [["section"]]
    },

    // ------ COMPONENT -------------------------------------------------------
    document: {
        attributes: {
            id: null, type: null, "xml:lang": $.publidoc.schemaAttLang },
        content: [["top.head", "division", "topic"]]
    },

    topic: {
        attributes: {
            id: null, type: null, "xml:lang": $.publidoc.schemaAttLang },
        content: [["component.head", "section"]],
        seed: "<topic><head><title e4x='here'/></head>"
            + "<section><p e4x='hold'/></section></topic>"
    },

    // ------ SECTION ---------------------------------------------------------
    ".section": {
        content: [["section"]]
    },
    section: {
        attributes: {
            "xml:id": null,
            type: $.publidoc.schemaSectionAttType,
            "xml:lang": $.publidoc.schemaAttLang
        },
        content: [["section.head", "section"],
                  ["section.head"].concat($.publidoc.schemaBlock)],
        seed: "<section><p e4x='here'/></section>"
    },
    "special.section": {
        element: "section",
        attributes: {
            "xml:id": null,
            type: $.publidoc.schemaSectionAttType,
            "xml:lang": $.publidoc.schemaAttLang
        },
        content: [["section.head", "special.section"],
                  ["section.head", "special.p"]],
        seed: "<section><p e4x='here'/></section>"
    },
    bibliography: {
        content: [["bibliography.entry"]]
    },

    // ------ BLOCK -----------------------------------------------------------
    ".block": {
        content: [$.publidoc.schemaBlock]
    },

    p: {
        content: [$.publidoc.schemaInline]
    },
    "special.p": {
        element: "p",
        content: [$.publidoc.schemaInline]
    },

    list: {
        attributes: { type: ["ordered", "glossary"] },
        content: [["block.head", "item"]],
        seed: "<list><item e4x='here'/><item e4x='hold'/></list>"
    },
    item: {
        content: [["label"].concat($.publidoc.schemaBlock),
                  $.publidoc.schemaInline]
    },

    blockquote: {
        attributes: { type: null },
        content: [["block.head", "p", "list", "speech", "attribution"]],
        seed: "<blockquote><p e4x='here'/><attribution e4x='hold'/>"
            + "</blockquote>"
    },
    attribution: {
        content: [[".text", "sup", "number", "date", "name", "foreign",
                 "acronym", "term", "literal", "highlight", "emphasis",
                 "mentioned", "note"]]
    },

    speech: {
        content: [["speaker", "stage", "p", "blockquote"]],
        seed: "<speech><speaker e4x='hold'/><stage e4x='hold'/>"
            + "<p e4x='here'/></speech>"
    },
    speaker: {
        content: [$.publidoc.schemaInline]
    },

    table: {
        attributes: { type: null },
        content: [["block.head", "thead", "tbody", "caption"],
                  ["block.head", "tr", "caption"]],
        seed: "<table><tr><th e4x='here'/><th e4x='hold'/><th e4x='hold'/></tr>"
            + "<tr><td e4x='hold'/><td e4x='hold'/><td e4x='hold'/></tr></table>"
    },
    thead: {
        content: [["tr"]]
    },
    tbody: {
        content: [["tr"]]
    },
    tr: {
        attributes: {
            align: ["left", "right", "center", "justify"],
            valign: ["top", "middle", "bottom"],
            type: null
        },
        content: [["th", "td"]]
    },
    th: {
        attributes: {
            align: ["left", "right", "center", "justify"],
            valign: ["top", "middle", "bottom"],
            colspan: ["2", "3", "4", "5", "6", "7", "8", "9", "10"],
            rowspan: ["2", "3", "4", "5", "6", "7", "8", "9", "10"],
            type: null
        },
        content: [["p", "speech", "list", "blockquote"],
                  $.publidoc.schemaInline]
    },
    td: {
        attributes: {
            align: ["left", "right", "center", "justify"],
            valign: ["top", "middle", "bottom"],
            colspan: ["2", "3", "4", "5", "6", "7", "8", "9", "10"],
            rowspan: ["2", "3", "4", "5", "6", "7", "8", "9", "10"],
            type: null
        },
        content: [["p", "speech", "list", "blockquote"],
                  $.publidoc.schemaInline]
    },
    caption: {
        content: [["p", "speech", "list", "blockquote"],
                  $.publidoc.schemaInline]
    },

    media: {
        captionElement: "caption",
        attributes: {
            "xml:id": null,
            type: $.publidoc.schemaMediaAttType
         },
        content: [["block.head", "image", "audio", "video", "caption"]]
    },
    image: {
        attributes: {
            id: null,
            type: ["cover", "thumbnail", "icon", "animation"],
            alt: null },
        content: [["copyright"]]
    },
    audio: {
        attributes: {
            id: null,
            type: ["music", "voice", "background", "smil"] }
    },
    video: {
        attributes: { id: null }
    },

    "bibliography.entry": {
        content: [["identifier.ean", "title", "subtitle", "copyright",
                   "collection", "contributors", "date", "place", "folio",
                   "pages"]]
    },

    // ------ INLINE ----------------------------------------------------------
    ".simple.inline": {
        content: [$.publidoc.schemaSimpleInline]
    },
    ".inline": {
        content: [$.publidoc.schemaInline]
    },

    sup: {
        content: [[".text"]]
    },
    sub: {
        content: [[".text"]]
    },
    var: {
        content: [[".text"]]
    },
    number: {
        attributes: { type: ["roman"] },
        content: [[".text", "sup"]]
    },
    acronym: {
        content: [[".text", "sup"]]
    },

    highlight: {
        content: [[".text", "sup", "sub", "emphasis"]]
    },
    emphasis: {
        content: [[".text", "sup", "sub", "highlight"]]
    },
    mentioned: {
        content: [[".text"]]
    },
    literal: {
        content: [$.publidoc.schemaInline]
    },
    term: {
        content: [[".text", "sup"]]
    },
    stage: {
        content: [[".text"]]
    },
    name: {
        attributes: {
            of: ["person", "company", "book", "newspaper", "party", "movie",
                 "painting"]
        },
        content: [[".text", "sup", "number", "acronym"]]
    },
    foreign: {
        attributes: { "xml:lang": null },
        content: [$.publidoc.schemaInline]
    },
    date: {
        attributes: { value: null, of: ["birth", "death"] },
        content: [[".text", "sup", "number"]]
    },
    math: {
        attributes: {
            "xml:id": null,
            display: ["wide", "numbered", "box", "numbered-box"]
        },
        content: [["latex"], [".text", "sup", "sub", "var"]]
    },
    latex: {
        attributes: { plain: ["true"] },
        content: [[".text"]]
    },
    quote: {
        content: [["phrase", "attribution"], $.publidoc.schemaInline]
    },
    phrase: {
        content: [$.publidoc.schemaInline]
    },

    initial: {
        content: [["c", "w"]]
    },
    c: {
        content: [[".text"]]
    },
    w: {
        content: [$.publidoc.schemaInline]
    },
    note: {
        attributes: { label: null },
        content: [$.publidoc.schemaBlock.concat(["w"]),
                  $.publidoc.schemaInline]
    },
    link: {
        attributes: { uri: null, idref: null },
        content: [$.publidoc.schemaSimpleInline]
    },
    anchor: {
        attributes: { "xml:id": null },
        content: [$.publidoc.schemaInline]
    },
    smil: {
        attributes: { begin: null, end: null, audio: null },
        content: [$.publidoc.schemaSimpleInline]
    }
};


})(jQuery);
