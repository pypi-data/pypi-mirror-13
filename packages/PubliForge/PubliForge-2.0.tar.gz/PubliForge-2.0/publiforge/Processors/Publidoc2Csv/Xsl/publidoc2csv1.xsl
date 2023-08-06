<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2csv1.xsl adcff0d830fe 2015/04/01 16:05:56 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- PubliForge parameters -->
  <xsl:param name="processor"/>   <!-- Full path to processor directory -->
  <xsl:param name="output"/>      <!-- Full path to output directory -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->

  <xsl:output method="text" encoding="utf-8"/>

  <!--
      =========================================================================
      selection
      =========================================================================
  -->
  <xsl:template match="selection"/>

  <!--
      =========================================================================
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <xsl:apply-templates select="document|topic"/>
    <xsl:message>
      <xsl:value-of select="document/head/title|topic/head/title"/>
      <xsl:value-of select="concat('… ', count(.//media), ' &lt;media&gt;')"/>
    </xsl:message>
  </xsl:template>

  <!--
      =========================================================================
      document
      =========================================================================
  -->
  <xsl:template match="document">
    <xsl:apply-templates select="division|topic//media"/>
  </xsl:template>

  <!--
      =========================================================================
      topic
      =========================================================================
  -->
  <xsl:template match="topic">
    <xsl:apply-templates select=".//media"/>
  </xsl:template>

  <!--
      =========================================================================
      division
      =========================================================================
  -->
  <xsl:template match="division">
    <xsl:text>
</xsl:text>
    <xsl:choose>
      <xsl:when test="count(ancestor::division)=1"> ; </xsl:when>
    </xsl:choose>
    <xsl:apply-templates select="head/title"/><xsl:text>
</xsl:text>
    <xsl:apply-templates select="division|topic//media"/>
  </xsl:template>

  <!--
      =========================================================================
      media
      =========================================================================
  -->
  <xsl:template match="media">
    <xsl:choose>
      <xsl:when test="count(ancestor::division)=1"> ; </xsl:when>
      <xsl:when test="count(ancestor::division)=2"> ; ; </xsl:when>
    </xsl:choose>
    <xsl:value-of select="image[1]/@id"/>
    <xsl:text> ; </xsl:text>
    <xsl:value-of select="translate(normalize-space(caption), ';', '')"/><xsl:text>
</xsl:text>
  </xsl:template>
</xsl:stylesheet>
