<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiset_edit.xsl e45603baa0b4 2015/05/27 20:43:44 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <!-- PubliForge parameters -->
  <xsl:param name="fid"/>         <!-- XML File name without extension -->
  <xsl:param name="route"/>       <!-- Route to the opener public directory -->
  <xsl:param name="main_route"/>  <!-- Route to the main public directory -->
  <xsl:param name="variables"/>   <!-- Full path to variable file -->
  <xsl:param name="mode"/>        <!-- variables or html -->
  <xsl:param name="autocheck"/>   <!-- delay and cycles to check and save -->

  <!-- Variables -->
  <xsl:variable name="lang">
    <xsl:choose>
      <xsl:when test="/*/*/@xml:lang">
        <xsl:value-of select="/*/*/@xml:lang"/>
      </xsl:when>
      <xsl:otherwise>en</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>
  <xsl:variable name="variables_doc" select="document($variables)"/>


  <xsl:output method="xml" encoding="utf-8" indent="yes"
              omit-xml-declaration="yes"/>


  <!--
      =========================================================================
      publiset
      =========================================================================
  -->
  <xsl:template match="publiset">
    <xsl:choose>
      <xsl:when test="$mode='variables'">
        <publiforge version="1.0">
          <variables>
            <xsl:apply-templates select="composition|selection" mode="variables"/>
          </variables>
        </publiforge>
      </xsl:when>
      <xsl:when test="$mode='html'">
        <xsl:apply-templates select="composition|selection" mode="html"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>


  <!--
      *************************************************************************
                                      TOP LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      composition mode variables
      =========================================================================
  -->
  <xsl:template match="composition" mode="variables">
    <xsl:apply-templates
        select="$variables_doc/*/*/group[@name='composition_head']"
        mode="variables">
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
    <xsl:apply-templates
        select="$variables_doc/*/*/group[@name='composition_corpus']"
        mode="variables">
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
  </xsl:template>

  <!--
      =========================================================================
      composition mode html
      =========================================================================
  -->
  <xsl:template match="composition" mode="html">
    <div class="pdocComposition">
      <xsl:if test="$autocheck">
        <xsl:attribute name="data-autocheck">
          <xsl:value-of select="$autocheck"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='composition_head']"
          mode="html_table"/>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='composition_corpus']"
          mode="html_div"/>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      selection mode variables
      =========================================================================
  -->
  <xsl:template match="selection" mode="variables">
    <xsl:apply-templates
        select="$variables_doc/*/*/group[@name='selection_head']"
        mode="variables">
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
    <xsl:apply-templates
        select="$variables_doc/*/*/group[@name='selection_corpus']"
        mode="variables">
      <xsl:with-param name="node" select="."/>
    </xsl:apply-templates>
  </xsl:template>

  <!--
      =========================================================================
      selection mode html
      =========================================================================
  -->
  <xsl:template match="selection" mode="html">
    <div class="pdocSelection">
      <xsl:if test="$autocheck">
        <xsl:attribute name="data-autocheck">
          <xsl:value-of select="$autocheck"/>
        </xsl:attribute>
      </xsl:if>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='selection_head']"
          mode="html_table"/>
      <xsl:apply-templates
          select="$variables_doc/*/*/group[@name='selection_corpus']"
          mode="html_div"/>
    </div>
  </xsl:template>


  <!--
      *************************************************************************
                                       GROUP
      *************************************************************************
  -->
  <!--
      =========================================================================
      group mode variables
      =========================================================================
  -->
  <xsl:template match="group" mode="variables">
    <xsl:param name="node"/>

    <group name="{@name}">
      <xsl:copy-of select="label"/>
      <xsl:apply-templates select="var" mode="variables">
        <xsl:with-param name="group" select="@name"/>
        <xsl:with-param name="node" select="$node"/>
      </xsl:apply-templates>
    </group>
  </xsl:template>

  <!--
      =========================================================================
      group mode html_table
      =========================================================================
  -->
  <xsl:template match="group" mode="html_table">
    <xsl:param name="node"/>

    <table class="pdocMeta tableToolTip">
      <xsl:apply-templates select="var" mode="html_table">
        <xsl:with-param name="group" select="@name"/>
        <xsl:with-param name="node" select="$node"/>
      </xsl:apply-templates>
    </table>
  </xsl:template>

  <!--
      =========================================================================
      group mode html_div
      =========================================================================
  -->
  <xsl:template match="group" mode="html_div">
    <xsl:apply-templates select="var" mode="html_div">
      <xsl:with-param name="group" select="@name"/>
    </xsl:apply-templates>
  </xsl:template>

  
  <!--
      *************************************************************************
                                          VAR
      *************************************************************************
  -->
  <!--
      =========================================================================
      var mode variables
      =========================================================================
  -->
  <xsl:template match="var" mode="variables">
    <xsl:param name="group"/>
    <xsl:param name="node"/>

    <xsl:variable name="default">
      <xsl:call-template name="var_default">
        <xsl:with-param name="node" select="$node"/>
      </xsl:call-template>
    </xsl:variable>

    <var name="{$group}_{@name}">
      <xsl:copy-of select="@type|@class|@cast|@rows"/>
      <xsl:if test="string-length($default)">
        <default>
          <xsl:copy-of select="$default"/>
        </default>
      </xsl:if>
      <xsl:copy-of select="pattern|option|label"/>
    </var>
  </xsl:template>

  <!--
      =========================================================================
      var mode html_table
      =========================================================================
  -->
  <xsl:template match="var" mode="html_table">
    <xsl:param name="group"/>

    <tr>
      <th>
        <xsl:call-template name="localized_label"/>
      </th>
      <td>
        <xsl:if test="not(description)">
          <xsl:attribute name="colspan">2</xsl:attribute>
        </xsl:if>
        <xsl:value-of select="concat('__', $group, '_', @name, '__')"/>
      </td>
      <xsl:if test="description">
        <td class="pdocMetaToolTip">
          <input type="image" name="des!{../@name}:{@name}" class="toolTip"
                 src="{$main_route}Images/action_help_one.png" alt="tooltip"/>
        </td>
      </xsl:if>
    </tr>
  </xsl:template>

  <!--
      =========================================================================
      var mode html_div
      =========================================================================
  -->
  <xsl:template match="var" mode="html_div">
    <xsl:param name="group"/>

    <div>
      <xsl:value-of select="concat('__', $group, '_', @name, '__')"/>
    </div>
  </xsl:template>

  
  <!--
      *************************************************************************
                                   CALLABLE TEMPLATES
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template var_default
      =========================================================================
  -->
  <xsl:template name="var_default">
    <xsl:param name="node"/>

    <xsl:choose>
      <!-- Head attributes -->
      <xsl:when test="@name='xml:lang'">
        <xsl:value-of select="$node/@xml:lang"/>
      </xsl:when>
      <xsl:when test="@name='path'">
        <xsl:value-of select="$node/@path"/>
      </xsl:when>
      <xsl:when test="@name='pi_source'">
        <xsl:value-of select="$node/@pi-source"/>
      </xsl:when>
      <xsl:when test="@name='xpath'">
        <xsl:value-of select="$node/@xpath"/>
      </xsl:when>
      <xsl:when test="@name='xslt'">
        <xsl:value-of select="$node/@xslt"/>
      </xsl:when>
      <xsl:when test="@name='as'">
        <xsl:value-of select="$node/@as"/>
      </xsl:when>
      <xsl:when test="@name='attributes'">
        <xsl:value-of select="$node/@attributes"/>
      </xsl:when>

      <!-- Head element -->
      <xsl:when test="@name='title'">
        <xsl:copy-of select="$node/head/title/node()"/>
      </xsl:when>
      <xsl:when test="@name='shorttitle'">
        <xsl:copy-of select="$node/head/shorttitle/node()"/>
      </xsl:when>
      <xsl:when test="@name='subtitle'">
        <xsl:copy-of select="$node/head/subtitle[1]/node()"/>
      </xsl:when>
      <xsl:when test="@name='identifier_ean'">
        <xsl:copy-of
            select="$node/head/identifier[@type='ean' and not(@for)]/node()"/>
      </xsl:when>
      <xsl:when test="@name='identifier_uri'">
        <xsl:copy-of select="$node/head/identifier[@type='uri']/node()"/>
      </xsl:when>
      <xsl:when test="@name='copyright'">
        <xsl:copy-of select="$node/head/copyright/node()"/>
      </xsl:when>
      <xsl:when test="@name='collection'">
        <xsl:copy-of select="$node/head/collection/node()"/>
      </xsl:when>
      <xsl:when test="@name='contributors'">
        <xsl:copy-of select="$node/head/contributors/node()"/>
      </xsl:when>
      <xsl:when test="@name='date'">
        <xsl:value-of select="$node/head/date/@value"/>
      </xsl:when>
      <xsl:when test="@name='source_book'">
        <xsl:copy-of select="$node/head/source[@type='book']/node()"/>
      </xsl:when>
      <xsl:when test="@name='source_file'">
        <xsl:copy-of select="$node/head/source[@type='file']/node()"/>
      </xsl:when>
      <xsl:when test="@name='keywordset'">
        <xsl:copy-of select="$node/head/keywordset/node()"/>
      </xsl:when>
      <xsl:when test="@name='subjectset'">
        <xsl:copy-of select="$node/head/subjectset/node()"/>
      </xsl:when>
      <xsl:when test="@name='abstract'">
        <xsl:copy-of select="$node/head/abstract/node()"/>
      </xsl:when>
      <xsl:when test="@name='cover'">
        <xsl:value-of select="$node/head/cover/image/@id"/>
      </xsl:when>

      <!-- Corpus -->
      <xsl:when test="@name='composition' or @name='selection'">
        <xsl:copy-of
            select="$node/division|$node/file|$node/link
                    |$node/comment()|$node/processing-instruction()"/>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      Template localized_label
      =========================================================================
  -->
  <xsl:template name="localized_label">
    <xsl:param name="node" select="label"/>

    <xsl:choose>
      <xsl:when test="$node[@xml:lang=$lang]">
        <xsl:apply-templates select="$node[@xml:lang=$lang]"/>
      </xsl:when>
      <xsl:when test="$node[starts-with($lang, @xml:lang)]">
        <xsl:apply-templates select="$node[starts-with($lang, @xml:lang)][1]"/>
      </xsl:when>
      <xsl:when test="$node[@xml:lang='en']">
        <xsl:apply-templates select="$node[@xml:lang='en']"/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates select="$node[1]"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
