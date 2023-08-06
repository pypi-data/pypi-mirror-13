// $Id: publiset_schema.js 8ce798c99ca0 2016/01/26 15:13:23 Patrick $

/*jshint globalstrict: true*/
/*global jQuery: true */

"use strict";

(function($) {


// ****************************************************************************
//                                PUBLISET SCHEMA
// ****************************************************************************

if (!$.publiset) $.publiset = {};

$.publiset.schemaSimpleInline = [".text", "sup", "sub"];

$.publiset.schemaInline = $.publiset.schemaSimpleInline.concat([
    "highlight", "emphasis", "name", "date", "link"]);

$.publiset.schemaAttLang = ["en", "fr", "es", "it"];

$.publiset.schema = {
    // ------ HEAD ------------------------------------------------------------
    "composition.head": {
        element: "head",
        attributes: { as: null, attributes: null, transform: null },
        content: [["title", "shorttitle", "subtitle", "identifier.ean",
                   "copyright", "collection", "contributors", "date", "source",
                   "keywordset", "subjectset", "abstract", "cover"]]
    },
    "selection.head": {
        element: "head",
        content: [["title", "shorttitle", "subtitle", "identifier.ean",
                   "copyright", "collection", "contributors", "date", "source",
                   "keywordset", "subjectset", "abstract", "cover"]]
    },

    title: {
        isFirst: true,
        content: [$.publiset.schemaInline]
    },
    shorttitle: {
        content: [$.publiset.schemaInline]
    },
    subtitle: {
        content: [$.publiset.schemaInline]
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
        content: [$.publiset.schemaSimpleInline]
    },

    collection: {
        content: [$.publiset.schemaSimpleInline]
    },

    ".contributors": {
        content: [["contributor"]]
    },
    contributors: {
        content: [["contributor"]],
        seed: "<contributors><contributor><firstname e4x='hold'/>"
            + "<lastname e4x='here'/><role>author</role></contributor>"
            + "</contributors>"
    },
    contributor: {
        content: [["identifier.uri", "firstname", "lastname", "label",
                   "address", "link", "role"]],
        seed: "<contributor><firstname e4x='hold'/><lastname e4x='here'/>"
            + "<role>author</role></contributor>"
    },
    firstname: {
        content: [$.publiset.schemaSimpleInline]
    },
    lastname: {
        content: [$.publiset.schemaSimpleInline]
    },
    label: {
        content: [$.publiset.schemaSimpleInline]
    },
    address: {
        content: [$.publiset.schemaSimpleInline]
    },
    role: {
        content: [[".text"]]
    },

    source: {
        attributes: { type: ["book", "file"] },
        content: [["identifier.uri"],
                  ["identifier.ean", "title", "subtitle", "copyright",
                   "collection", "folio", "pages"]]
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
        content: [["keyword"]],
        seed: "<keywordset><keyword e4x='here'/></keywordset>"
    },
    keyword: {
        content: [$.publiset.schemaSimpleInline]
    },
    ".subjectset": {
        content: [["subject"]]
    },
    subjectset: {
        content: [["subject"]],
        seed: "<subjectset><subject e4x='here'/></subjectset>"
    },
    subject: {
        content: [$.publiset.schemaSimpleInline]
    },

    ".abstract": {
        content: [["p"]]
    },
    abstract: {
        content: [["p"]],
        seed: "<abstract><p e4x='here'/></abstract>"
    },

    cover: {
        content: [["image"]],
        seed: "<cover><image id=''/></cover>"
    },
    image: {
        attributes: { id: null }
    },

    element: {
        attributes: { name: null },
        content: [["element"], $.publiset.schemaInline]
    },

    // ------ TOP -------------------------------------------------------------
    ".composition": {
        content:[
            ["composition.head", "composition.division", "composition.file"]]
    },
    "composition": {
        attributes: {
            "xml:lang": $.publiset.schemaAttLang, "path": null,
            "pi-source": ["true", "false"], xpath: null, xslt: null },
        content:[
            ["composition.head", "composition.division", "composition.file"]]
    },

    ".selection": {
        content:[
            ["selection.head", "selection.division", "selection.file", "link"]]
    },
    "selection": {
        attributes: { "xml:lang": $.publiset.schemaAttLang, "path": null },
        content:[
            ["selection.head", "selection.division", "selection.file", "link"]]
    },

    // ------ DIVISION --------------------------------------------------------
    "composition.division": {
        element: "division",
        attributes: {
            path: null, xpath: null, xslt: null,
            as: null, attributes: null, transform: null, argument: null },
        content: [
            ["composition.head", "composition.division", "composition.file"]],
        seed: "<division><head><title e4x='here'/></head></division>"
    },

    "selection.division": {
        element: "division",
        attributes: { path: null, argument: null },
        content: [
            ["selection.head", "selection.division", "selection.file", "link"]],
        seed: "<division><head><title e4x='here'/></head></division>"
    },

    // ------ FILE ------------------------------------------------------------
    "composition.file": {
        element: "file",
        attributes: {
            path: null, xpath: null, xslt: null, argument: null, mode: null },
        content: [[".text"]]
    },

    "selection.file": {
        element: "file",
        attributes: { path: null },
        content: [[".text"]]
    },

    // ------ BLOCK -----------------------------------------------------------
    p: {
        content: [$.publiset.schemaInline]
    },

    // ------ INLINE ----------------------------------------------------------
    ".simple.inline": {
        content: [$.publiset.schemaSimpleInline]
    },
    ".inline": {
        content: [$.publiset.schemaInline]
    },

    sup: {
        content: [[".text"]]
    },
    sub: {
        content: [[".text"]]
    },

    highlight: {
        content: [[".text", "sup", "sub", "emphasis"]]
    },
    emphasis: {
        content: [[".text", "sup", "sub", "highlight"]]
    },
    name: {
        attributes: {
            of: ["person", "company", "book", "newspaper", "party", "movie",
                 "painting"]
        },
        content: [[".text", "sup"]]
    },
    date: {
        attributes: { value: null },
        content: [[".text", "sup"]]
    },

    link: {
        attributes: { uri: null },
        content: [$.publiset.schemaSimpleInline]
    }
};


})(jQuery);
