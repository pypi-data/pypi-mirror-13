<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publidoc2epub2_base.inc.xsl 905d65a55aca 2015/08/29 12:23:46 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <!--
      *************************************************************************
                                      HEAD LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      index
      =========================================================================
  -->
  <xsl:template match="index">
    <xsl:if test="not(ancestor::head)">
      <a id="{concat('idx', count(preceding::index))}">
        <xsl:text> </xsl:text>
      </a>
    </xsl:if>
    <xsl:apply-templates select="w"/>
  </xsl:template>


  <!--
      *************************************************************************
                                   COMPONENT LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      topic mode file
      =========================================================================
  -->
  <xsl:template match="topic" mode="file">
    <xsl:choose>
      <!-- ~~~~~~~~~~~~~~~~~~~~~~~ tune-html-replace-by ~~~~~~~~~~~~~~~~~~~ -->
      <xsl:when test="processing-instruction('tune-html-replace-by')"/>

      <!-- ~~~~~~~~~~~~~~~~~~~~~~~ title, copyright ~~~~~~~~~~~~~~~~~~~~~~~ -->
      <xsl:when test="@type='title' or @type='copyright'">
        <xsl:call-template name="html_file">
          <xsl:with-param
              name="name"
              select="concat($fid, '-tpc-',
                      format-number(count(preceding::topic)+1, '0000'))"/>
          <xsl:with-param name="title">
            <xsl:if test="/*/*/head/title">
              <xsl:apply-templates select="/*/*/head/title" mode="text"/>
              <xsl-text> – </xsl-text>
            </xsl:if>
            <xsl:choose>
              <xsl:when test="@type='title'"><xsl:value-of select="$i18n_title_page"/></xsl:when>
              <xsl:when test="@type='copyright'"><xsl:value-of select="$i18n_copyright"/></xsl:when>
            </xsl:choose>
          </xsl:with-param>
          <xsl:with-param name="body">
            <body>
              <xsl:attribute name="class">
                <xsl:value-of select="concat('pdocTopic pdocTopic-', @type)"/>
              </xsl:attribute>
              <div>
                <xsl:call-template name="navigation"/>
                <xsl:apply-templates select="header"/>
                <xsl:call-template name="anchor_levels"/>
                <xsl:if test="head/title">
                  <div class="h1 pdocTitle"><xsl:apply-templates select="head/title"/></div>
                </xsl:if>
                <xsl:if test="head/subtitle">
                  <div class="h2 pdocSubtitle"><xsl:call-template name="subtitle"/></div>
                </xsl:if>
                <xsl:apply-templates select="." mode="corpus"/>
                <xsl:apply-templates select="footer"/>
                <xsl:call-template name="navigation">
                  <xsl:with-param name="bottom" select="1"/>
                </xsl:call-template>
              </div>
            </body>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:when>

       <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ image ~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
      <xsl:when test="@type='image'">
        <xsl:call-template name="html_file">
          <xsl:with-param
              name="name"
              select="concat($fid, '-tpc-',
                      format-number(count(preceding::topic)+1, '0000'))"/>
          <xsl:with-param name="title">
            <xsl:if test="/*/*/head/title">
              <xsl:apply-templates select="/*/*/head/title" mode="text"/>
            </xsl:if>
            <xsl:if test="head/title">
              <xsl:if test="/*/*/head/title"> – </xsl:if>
              <xsl:apply-templates select="head/title" mode="text"/>
            </xsl:if>
          </xsl:with-param>
          <xsl:with-param name="body">
            <body>
              <xsl:attribute name="class">
                <xsl:text>pdocTopic</xsl:text>
                <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
              </xsl:attribute>
              <xsl:call-template name="anchor_levels"/>
              <xsl:choose>
                <xsl:when test="count(.//section)=1 and count(section/media)=1
                                and count(.//p)=0 and count(.//hotspot)=0
                                and count(.//caption)=0
                                and not(processing-instruction())">
                  <div id="sect1">
                    <xsl:apply-templates select="section/media/image" mode="media"/>
                  </div>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:apply-templates select="." mode="corpus"/>
                </xsl:otherwise>
              </xsl:choose>
            </body>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:when>

      <!-- ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ others ~~~~~~~~~~~~~~~~~~~~~~~~~~ -->
      <xsl:otherwise>
        <xsl:call-template name="html_file">
          <xsl:with-param
              name="name"
              select="concat($fid, '-tpc-',
                      format-number(count(preceding::topic)+1, '0000'))"/>
          <xsl:with-param name="title">
            <xsl:if test="/*/*/head/title">
              <xsl:apply-templates select="/*/*/head/title" mode="text"/>
            </xsl:if>
            <xsl:if test="head/title">
              <xsl:if test="/*/*/head/title"> – </xsl:if>
              <xsl:apply-templates select="head/title" mode="text"/>
            </xsl:if>
          </xsl:with-param>

          <xsl:with-param name="body">
            <body>
              <xsl:attribute name="class">
                <xsl:text>pdocTopic</xsl:text>
                <xsl:if test="@type"> pdocTopic-<xsl:value-of select="@type"/></xsl:if>
                <xsl:if test="ancestor::division">
                  <xsl:value-of select="concat(' depth', count(ancestor::division)+1)"/>
                  <xsl:for-each select="ancestor::division">
                    <xsl:if test="@type"> pdocDivision-<xsl:value-of select="@type"/></xsl:if>
                  </xsl:for-each>
                </xsl:if>
              </xsl:attribute>
              <xsl:call-template name="navigation"/>
              <xsl:call-template name="lead"/>
              <xsl:apply-templates select="header"/>
              <xsl:call-template name="anchor_levels"/>
              <xsl:if test="head/title">
                <div class="h1 pdocTitle"><xsl:apply-templates select="head/title"/></div>
              </xsl:if>
              <xsl:if test="head/subtitle">
                <div class="h2 pdocSubtitle"><xsl:call-template name="subtitle"/></div>
              </xsl:if>
              <xsl:apply-templates select="." mode="corpus"/>
              <xsl:apply-templates select="footer"/>
              <xsl:call-template name="navigation">
                <xsl:with-param name="bottom" select="1"/>
              </xsl:call-template>
            </body>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>


  <!--
      *************************************************************************
                                     INLINE LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      anchor
      =========================================================================
  -->
  <xsl:template match="anchor">
    <a id="{@xml:id}"><xsl:text> </xsl:text></a>
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>
