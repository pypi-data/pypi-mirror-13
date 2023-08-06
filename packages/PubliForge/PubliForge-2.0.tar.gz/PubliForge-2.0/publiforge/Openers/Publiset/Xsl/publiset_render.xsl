<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiset_render.xsl 7627ff288a79 2015/05/24 20:23:48 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <xsl:import href="publiset_render_i18n.inc.xsl"/>
  <xsl:import href="publiset_render_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="route"/>       <!-- Route to the opener public directory -->
  <xsl:param name="main_route"/>  <!-- Route to the main public directory -->

  <!-- Processor image variables -->
  <xsl:variable name="img" select="1"/>
  <xsl:variable name="img_ext"></xsl:variable>
  <xsl:variable name="img_ext_cover"></xsl:variable>
  <!-- Processor string variables -->
  <xsl:variable name="str_sep"> – </xsl:variable>

  <!-- Variables -->
  <xsl:variable name="img_dir"
                select="concat($main_route, 'Images/notfound.jpg#')"/>
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              omit-xml-declaration="yes"/>

  <!--
      =========================================================================
      publiset
      =========================================================================
  -->
  <xsl:template match="publiset">
    <xsl:apply-templates select="composition|selection"/>
  </xsl:template>

  <!--
      =========================================================================
      composition
      =========================================================================
  -->
  <xsl:template match="composition">
    <div class="pdocComposition">
      <xsl:apply-templates select="." mode="meta"/>
      <xsl:if test="head/title">
        <div class="h1">
          <xsl:apply-templates select="head/title"/>
          <xsl:if test="head/subtitle">
            <div><xsl:call-template name="subtitle"/></div>
          </xsl:if>
        </div>
      </xsl:if>
      <xsl:apply-templates select="head" mode="cover"/>
      <ul>
        <xsl:apply-templates select="division|file"/>
      </ul>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      selection
      =========================================================================
  -->
  <xsl:template match="selection">
    <div class="pdocSelection">
      <xsl:apply-templates select="." mode="meta"/>
      <xsl:if test="head/title">
        <div class="h1">
          <xsl:apply-templates select="head/title"/>
          <xsl:if test="head/subtitle">
            <div><xsl:call-template name="subtitle"/></div>
          </xsl:if>
        </div>
      </xsl:if>
      <xsl:apply-templates select="head" mode="cover"/>
      <ul>
        <xsl:apply-templates select="division|file|link"/>
      </ul>
    </div>
  </xsl:template>

</xsl:stylesheet>
