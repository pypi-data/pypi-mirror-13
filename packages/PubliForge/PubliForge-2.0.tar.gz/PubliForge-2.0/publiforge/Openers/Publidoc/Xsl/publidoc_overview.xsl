<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc_overview.xsl 98c11874ce69 2015/05/15 09:08:15 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:import href="publidoc2xhtml_template.inc.xsl"/>
  <xsl:import href="publidoc2xhtml_base.inc.xsl"/>

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="route"/>       <!-- Route to the opener public directory -->
  <xsl:param name="main_route"/>  <!-- Route to the main public directory -->

  <!-- Variables -->
  <xsl:variable name="img_dir"
                select="concat($main_route, 'Images/notfound.jpg#')"/>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              omit-xml-declaration="yes"/>

  <!--
      =========================================================================
      publidoc
      =========================================================================
  -->
  <xsl:template match="publidoc">
    <xsl:apply-templates select="document|topic"/>
  </xsl:template>

  <!--
      =========================================================================
      document, topic
      =========================================================================
  -->
  <xsl:template match="document|topic">
    <xsl:call-template name="overview"/>
  </xsl:template>

</xsl:stylesheet>
