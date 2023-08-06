<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publiquiz2scorm12_i18n.inc.xsl ba03399bcca2 2015/07/27 10:15:27 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_topic">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Sujet</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Asunto</xsl:when>
      <xsl:otherwise>Topic</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_quiz">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Exercice</xsl:when>
      <xsl:when test="starts-with($lang, 'es')">Ejercicio</xsl:when>
      <xsl:otherwise>Exercise</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

</xsl:stylesheet>
