<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiset2publidoc.xsl 64ce0a62af09 2015/12/02 14:47:48 Coraline $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publiset2publidoc_ini.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="processor"/>   <!-- Full path to processor directory -->
  <xsl:param name="output"/>      <!-- Full path to output directory -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->

  <!-- Processor image parameters -->
  <xsl:param name="img" select="0"/>
  <xsl:param name="img_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="img_quality" select="92"/>
  <xsl:param name="img_optimize" select="4"/>
  <xsl:param name="img_ext">.png</xsl:param>
  <xsl:param name="img_ext_cover">.png</xsl:param>
  <xsl:param name="img_ext_icon">.png</xsl:param>
  <xsl:param name="img_size">768x1024&gt;</xsl:param>
  <xsl:param name="img_size_cover">768x1024&gt;</xsl:param>
  <xsl:param name="img_size_header">x48&gt;</xsl:param>
  <xsl:param name="img_size_thumbnail">120x120&gt;</xsl:param>
  <xsl:param name="img_size_icon">x32&gt;</xsl:param>
  <!-- Processor audio parameters -->
  <xsl:param name="aud" select="0"/>
  <xsl:param name="aud_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="aud_ext">.ogg</xsl:param>
  <!-- Processor video parameters -->
  <xsl:param name="vid" select="0"/>
  <xsl:param name="vid_search">%(id)s.%(ext)s</xsl:param>
  <xsl:param name="vid_ext">.ogv</xsl:param>
  <xsl:param name="vid_width">300</xsl:param>

  <!-- Variables -->
  <xsl:variable name="path" select="$output"/>
  <xsl:variable name="img_dir">Images/</xsl:variable>
  <xsl:variable name="aud_dir">Audios/</xsl:variable>
  <xsl:variable name="vid_dir">Videos/</xsl:variable>


  <xsl:output method="xml" encoding="utf-8" indent="yes"/>
  <xsl:strip-space elements="*"/>


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
    <xsl:copy>
      <xsl:apply-templates select="*|@*|text()|comment()|processing-instruction()"/>
      <xsl:if test="$img"><xsl:apply-templates select="//image" mode="ini"/></xsl:if>
      <xsl:if test="$aud"><xsl:apply-templates select="//audio" mode="ini"/></xsl:if>
      <xsl:if test="$vid"><xsl:apply-templates select="//video" mode="ini"/></xsl:if>
    </xsl:copy>
  </xsl:template>

  <!--
      =========================================================================
      Template image_extension
      =========================================================================
  -->
  <xsl:template name="image_extension">
    <xsl:choose>
      <xsl:when test="processing-instruction('tune-html-img-format')">
        <xsl:text>.</xsl:text>
        <xsl:value-of
            select="normalize-space(processing-instruction('tune-html-img-format'))"/>
      </xsl:when>
      <xsl:when test="ancestor::cover">
        <xsl:value-of select="$img_ext_cover"/>
      </xsl:when>
      <xsl:when test="@type='animation'">.gif</xsl:when>
      <xsl:when test="ancestor::hotspot">.png</xsl:when>
      <xsl:when test="ancestor::dropzone">.png</xsl:when>
      <xsl:when test="@type='icon' or not(ancestor::media)">
        <xsl:value-of select="$img_ext_icon"/>
      </xsl:when>
      <xsl:when test="contains($img_ext, '+')">
        <xsl:value-of select="substring-before($img_ext, '+')"/>
      </xsl:when>
      <xsl:otherwise><xsl:value-of select="$img_ext"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      Template image_size
      =========================================================================
  -->
  <xsl:template name="image_size">
    <xsl:choose>
      <xsl:when test="processing-instruction('tune-html-img-size')">
        <xsl:value-of
            select="normalize-space(processing-instruction('tune-html-img-size'))"/>
      </xsl:when>
      <xsl:when test="@type='thumbnail' or ancestor::match
                      or ancestor::right or ancestor::wrong
                      or (ancestor::item and not(ancestor::list))">
        <xsl:value-of select="$img_size_thumbnail"/>
      </xsl:when>
      <xsl:when test="@type='cover' or ancestor::cover">
        <xsl:value-of select="$img_size_cover"/>
      </xsl:when>
      <xsl:when test="ancestor::header or ancestor::footer">
        <xsl:value-of select="$img_size_header"/>
      </xsl:when>
      <xsl:when test="ancestor::mip and not(ancestor::dropzone)">
        <xsl:value-of select="$img_size"/>
      </xsl:when>
      <xsl:when test="ancestor::mip">
        <xsl:value-of select="$img_size_thumbnail"/>
      </xsl:when>
      <xsl:when test="@type='icon' or not(ancestor::media)">
        <xsl:value-of select="$img_size_icon"/>
      </xsl:when>
      <xsl:otherwise><xsl:value-of select="$img_size"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
