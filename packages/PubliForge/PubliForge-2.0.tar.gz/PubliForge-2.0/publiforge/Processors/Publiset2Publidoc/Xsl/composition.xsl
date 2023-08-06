<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: composition.xsl 1e65bc9fc1a1 2015/07/14 10:17:20 Patrick $ -->
<!-- Publiset2publidoc -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:output method="xml" encoding="utf-8" indent="yes"/>

  <!--
      =========================================================================
      Copy
      =========================================================================
  -->
  <xsl:template match="*|@*|text()|comment()|processing-instruction()">
    <xsl:copy>
      <xsl:apply-templates
          select="*|@*|text()|comment()|processing-instruction()"/>
    </xsl:copy>
  </xsl:template>

  <!--
      =========================================================================
      publidoc, publiquiz
      =========================================================================
  -->
  <xsl:template match="publidoc|publiquiz">
    <xsl:apply-templates/>
  </xsl:template>

  <!--
      =========================================================================
      head
      =========================================================================
  -->
  <xsl:template match="head">
    <head>
      <xsl:choose>
        <xsl:when test="ancestor::publidoc|ancestor::publiquiz">
          <xsl:apply-templates
              select="title|subtitle|contributors|date|place
                      |keywordset|subjectset|index|abstract|annotation"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:apply-templates/>
        </xsl:otherwise>
      </xsl:choose>
    </head>
  </xsl:template>

  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <division>
      <xsl:if test="head/title or head/indexset
                    or head/abstract or head/annotation">
        <head>
          <xsl:apply-templates
              select="head/title|head/shorttitle|head/subtitle
                      |head/indexset|head/abstract|head/annotation"/>
        </head>
      </xsl:if>
      <xsl:apply-templates
          select="*[name()!='head']|comment()|processing-instruction()"/>
    </division>
  </xsl:template>

  <!--
      =========================================================================
      element
      =========================================================================
  -->
  <xsl:template match="element"/>

</xsl:stylesheet>
