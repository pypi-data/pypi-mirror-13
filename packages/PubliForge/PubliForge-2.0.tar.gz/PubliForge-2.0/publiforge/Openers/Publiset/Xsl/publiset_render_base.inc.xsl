<?xml version="1.0" encoding="utf-8"?>
<!-- $Id: publiset_render_base.inc.xsl 8ce798c99ca0 2016/01/26 15:13:23 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">


  <!--
      *************************************************************************
                                      HEAD LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      head mode cover
      =========================================================================
  -->
  <xsl:template match="head" mode="cover">
    <xsl:if test="cover/image">
      <div class="pdocCover">
        <img src="{$img_dir}{cover/image/@id}{$img_ext_cover}"
             alt="{$i18n_cover}"/>
      </div>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      contributor
      =========================================================================
  -->
  <xsl:template match="contributor">
    <div>
      <xsl:apply-templates select="firstname"/><xsl:text> </xsl:text>
      <xsl:apply-templates select="lastname|label"/>
      <xsl:if test="link">
        <xsl:text> (</xsl:text>
        <xsl:apply-templates select="link" mode="contributor"/>
        <xsl:text>)</xsl:text>
      </xsl:if>
      <xsl:text>, </xsl:text>
      <xsl:for-each select="role">
        <xsl:if test="position()&gt;1"> / </xsl:if>
        <xsl:apply-templates/>
      </xsl:for-each>
    </div>
  </xsl:template>

  <!--
      =========================================================================
      source
      =========================================================================
  -->
  <xsl:template match="source">
    <xsl:value-of select="concat('[', @type, '] ')"/>
    <xsl:apply-templates select="title"/>
    <xsl:if test="title and identifier">, </xsl:if>
    <xsl:apply-templates select="identifier"/>
    <xsl:if test="pages">
      <xsl:text>, </xsl:text>
      <xsl:apply-templates select="pages"/>
      <xsl:text> pages</xsl:text>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      keyword, subject
      =========================================================================
  -->
  <xsl:template match="keyword|subject">
    <xsl:if test="count(preceding-sibling::keyword|preceding-sibling::subject)&gt;0">
      <xsl:text> / </xsl:text>
    </xsl:if>
    <xsl:apply-templates/>
  </xsl:template>

  <!--
      =========================================================================
      cover
      =========================================================================
  -->
  <xsl:template match="cover">
    <xsl:value-of select="image/@id"/>
  </xsl:template>


  <!--
      *************************************************************************
                                       TOP LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      composition, selection mode meta
      =========================================================================
  -->
  <xsl:template match="composition|selection" mode="meta">
    <xsl:if test="@xml:lang or @path or @pi-source
                  or @xpath or @xslt or @as or @attributes or @transform
                  or head">
      <table class="pdocMeta">
        <xsl:apply-templates
            select="@xml:lang|@path|@pi-source|@xpath|@xslt|@as|@attributes
                    |@transform"
            mode="meta_item"/>
        <xsl:apply-templates
            select="head/@as|head/@attributes|head/@transform"
            mode="meta_item"/>
        <xsl:apply-templates
            select="head/title|head/shorttitle|head/subtitle|head/identifier
                    |head/copyright|head/collection|head/contributors|head/date
                    |head/source|head/keywordset|head/subjectset|head/abstract
                    |head/cover"
            mode="meta_item"/>
      </table>
    </xsl:if>
  </xsl:template>

  <xsl:template match="*|@*" mode="meta_item">
    <tr>
      <th>
        <xsl:choose>
          <xsl:when test="name()='xml:lang'"><xsl:value-of select="$i18n_language"/></xsl:when>
          <xsl:when test="name()='path'"><xsl:value-of select="$i18n_path"/></xsl:when>
          <xsl:when test="name()='pi-source'"><xsl:value-of select="$i18n_pi_source"/></xsl:when>
          <xsl:when test="name()='xpath'"><xsl:value-of select="$i18n_xpath"/></xsl:when>
          <xsl:when test="name()='xslt'"><xsl:value-of select="$i18n_xslt"/></xsl:when>
          <xsl:when test="name()='as'">
            <xsl:if test="ancestor::head"><xsl:value-of select="concat($i18n_head, ', ')"/></xsl:if>
            <xsl:value-of select="$i18n_as"/>
          </xsl:when>
          <xsl:when test="name()='attributes'">
            <xsl:if test="ancestor::head"><xsl:value-of select="concat($i18n_head, ', ')"/></xsl:if>
            <xsl:value-of select="$i18n_attributes"/>
          </xsl:when>
          <xsl:when test="name()='transform'">
            <xsl:if test="ancestor::head"><xsl:value-of select="concat($i18n_head, ', ')"/></xsl:if>
            <xsl:value-of select="$i18n_transform"/>
          </xsl:when>
          <xsl:when test="name()='title'"><xsl:value-of select="$i18n_title"/></xsl:when>
          <xsl:when test="name()='shorttitle'"><xsl:value-of select="$i18n_shorttitle"/></xsl:when>
          <xsl:when test="name()='subtitle'"><xsl:value-of select="$i18n_subtitle"/></xsl:when>
          <xsl:when test="name()='identifier'">
            <xsl:value-of select="concat($i18n_identifier, ' ', @type)"/>
            <xsl:if test="@for"><xsl:value-of select="concat(' ', @for)"/></xsl:if>
          </xsl:when>
          <xsl:when test="name()='copyright'"><xsl:value-of select="$i18n_copyright"/></xsl:when>
          <xsl:when test="name()='collection'"><xsl:value-of select="$i18n_collection"/></xsl:when>
          <xsl:when test="name()='contributors'"><xsl:value-of select="$i18n_contributors"/></xsl:when>
          <xsl:when test="name()='date'"><xsl:value-of select="$i18n_date"/></xsl:when>
          <xsl:when test="name()='source'"><xsl:value-of select="$i18n_source"/></xsl:when>
          <xsl:when test="name()='keywordset'"><xsl:value-of select="$i18n_keywords"/></xsl:when>
          <xsl:when test="name()='subjectset'"><xsl:value-of select="$i18n_subjects"/></xsl:when>
          <xsl:when test="name()='abstract'"><xsl:value-of select="$i18n_abstract"/></xsl:when>
          <xsl:when test="name()='cover'"><xsl:value-of select="$i18n_cover"/></xsl:when>
          <xsl:otherwise><xsl:value-of select="name()"/></xsl:otherwise>
      </xsl:choose>
      </th>
      <xsl:if test="ancestor::division"><td> = </td></xsl:if>
      <td>
        <xsl:if test="name()='subtitle'">
          <xsl:attribute name="class">pdocSubtitle</xsl:attribute>
        </xsl:if>
        <xsl:apply-templates select="."/>
      </td>
    </tr>
  </xsl:template>


  <!--
      *************************************************************************
                                     DIVISION LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      division mode meta
      =========================================================================
  -->
  <xsl:template match="division" mode="meta">
    <xsl:if test="head/@as or head/@attributes or head/transform 
                  or head/subtitle or head/shorttitle or head/identifier
                  or head/copyright or head/collection or head/contributors
                  or head/date or head/source or head/keywordset
                  or head/subjectset or head/abstract or head/cover">
      <table class="pdocMeta">
        <xsl:apply-templates
            select="head/@as|head/@attributes|head/@transform"
            mode="meta_item"/>
        <xsl:apply-templates
            select="head/subtitle|head/shorttitle|head/identifier
                    |head/copyright|head/collection|head/contributors|head/date
                    |head/source|head/keywordset|head/subjectset |head/abstract
                    |head/cover"
            mode="meta_item"/>
      </table>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      division mode attributes
      =========================================================================
  -->
  <xsl:template match="division" mode="attributes">
    <xsl:if test="@path or @xpath or @xslt or @as or @attributes or @transform">
      <xsl:text> </xsl:text>
      <em class="pdocAttributes">
        <xsl:if test="@path">
          <xsl:text>path="</xsl:text>
          <xsl:value-of select="@path"/>
          <xsl:text>"</xsl:text>
        </xsl:if>
        <xsl:if test="@xpath">
          <xsl:if test="@path">, </xsl:if>
          <xsl:text>xpath="</xsl:text>
          <xsl:value-of select="@xpath"/>
          <xsl:text>"</xsl:text>
        </xsl:if>
        <xsl:if test="@xslt">
          <xsl:if test="@path or @xpath">, </xsl:if>
          <xsl:text>xslt="</xsl:text>
          <xsl:value-of select="@xslt"/>
          <xsl:text>"</xsl:text>
        </xsl:if>
        <xsl:if test="@as">
          <xsl:if test="@path or @xpath or @xslt">, </xsl:if>
          <xsl:text>as="</xsl:text>
          <xsl:value-of select="@as"/>
          <xsl:text>"</xsl:text>
        </xsl:if>
         <xsl:if test="@attributes">
          <xsl:if test="@path or @xpath or @xslt or @as">, </xsl:if>
          <xsl:text>argument="</xsl:text>
          <xsl:value-of select="@attributes"/>
          <xsl:text>"</xsl:text>
        </xsl:if>
        <xsl:if test="@transform">
          <xsl:if test="@path or @xpath or @xslt or @as or @attributes">, </xsl:if>
          <xsl:text>transform="</xsl:text>
          <xsl:value-of select="@transform"/>
          <xsl:text>"</xsl:text>
        </xsl:if>
      </em>
    </xsl:if>
  </xsl:template>

  <!--
      =========================================================================
      division
      =========================================================================
  -->
  <xsl:template match="division">
    <li class="pdocDivision">
      <xsl:apply-templates select="head" mode="cover"/>

      <xsl:if test="head/title or @*">
        <xsl:choose>
          <xsl:when test="count(ancestor::division)=0">
            <h2 class="pdocTitle">
              <xsl:apply-templates select="head/title"/>
              <xsl:apply-templates select="." mode="attributes"/>
            </h2>
          </xsl:when>
          <xsl:otherwise>
            <h3 class="pdocTitle">
              <xsl:apply-templates select="head/title"/>
              <xsl:apply-templates select="." mode="attributes"/>
            </h3>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:if>

      <xsl:apply-templates select="." mode="meta"/>

      <xsl:if test="division|file|link">
        <ul>
          <xsl:apply-templates select="division|file|link"/>
        </ul>
      </xsl:if>
    </li>
  </xsl:template>


  <!--
      *************************************************************************
                                     COMPONENT LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      file
      =========================================================================
  -->
  <xsl:template match="file">
    <li class="pdocFile">
      <xsl:text>▪ </xsl:text>
      <a>
        <xsl:attribute name="href">
          <xsl:if test="ancestor-or-self::*[@path]">
            <xsl:value-of
                select="concat(ancestor-or-self::*[@path][1]/@path, '/')"/>
          </xsl:if>
          <xsl:value-of select="concat(normalize-space(), '?keep')"/>
        </xsl:attribute>
        <xsl:apply-templates/>
      </a>
      <xsl:if test="@path or @xpath or @xslt or @argument or @mode">
        <strong> | </strong>
        <em class="pdocAttributes">
          <xsl:if test="@path">
            <xsl:text>path="</xsl:text>
            <xsl:value-of select="@path"/>
            <xsl:text>"</xsl:text>
          </xsl:if>
          <xsl:if test="@xpath">
            <xsl:if test="@path">, </xsl:if>
            <xsl:text>xpath="</xsl:text>
            <xsl:value-of select="@xpath"/>
            <xsl:text>"</xsl:text>
          </xsl:if>
          <xsl:if test="@xslt">
            <xsl:if test="@path or @xpath">, </xsl:if>
            <xsl:text>xslt="</xsl:text>
            <xsl:value-of select="@xslt"/>
            <xsl:text>"</xsl:text>
          </xsl:if>
          <xsl:if test="@argument">
            <xsl:if test="@path or @xpath or @xslt">, </xsl:if>
            <xsl:text>argument="</xsl:text>
            <xsl:value-of select="@argument"/>
            <xsl:text>"</xsl:text>
          </xsl:if>
          <xsl:if test="@mode">
            <xsl:if test="@path or @xpath or @xslt or @argument">, </xsl:if>
            <xsl:text>mode="</xsl:text>
            <xsl:value-of select="@mode"/>
            <xsl:text>"</xsl:text>
          </xsl:if>
         </em>
      </xsl:if>
    </li>
  </xsl:template>

  <!--
      =========================================================================
      link
      =========================================================================
  -->
  <xsl:template match="link">
    <li class="pdocFileLink">
      <xsl:choose>
        <xsl:when test="starts-with(@uri, 'http')">
          <xsl:text>→ </xsl:text>
          <a href="{@uri}" class="pdocLink">
            <xsl:choose>
              <xsl:when test="normalize-space() or node()"><xsl:apply-templates/></xsl:when>
              <xsl:otherwise><xsl:value-of select="@uri"/></xsl:otherwise>
            </xsl:choose>
          </a>
        </xsl:when>
        <xsl:otherwise>
          <xsl:attribute name="title">
            <xsl:value-of select="@uri"/>
          </xsl:attribute>
          <xsl:text>→ </xsl:text>
          <span class="pdocLink">
            <xsl:choose>
              <xsl:when test="normalize-space() or node()"><xsl:apply-templates/></xsl:when>
              <xsl:otherwise><xsl:value-of select="@uri"/></xsl:otherwise>
            </xsl:choose>
          </span>
        </xsl:otherwise>
      </xsl:choose>
    </li>
  </xsl:template>


  <!--
      *************************************************************************
                                      BLOCK LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      p
      =========================================================================
  -->
  <xsl:template match="p">
    <p>
      <xsl:attribute name="class">
        <xsl:text>pdocP</xsl:text>
        <xsl:if test="position()=1"> first</xsl:if>
      </xsl:attribute>
      <xsl:apply-templates/>
    </p>
  </xsl:template>


  <!--
      *************************************************************************
                                     INLINE LEVEL
      *************************************************************************
  -->
  <!--
      =========================================================================
      sup, sub
      =========================================================================
  -->
  <xsl:template match="sup"><sup><xsl:apply-templates/></sup></xsl:template>
  <xsl:template match="sub"><sub><xsl:apply-templates/></sub></xsl:template>

  <!--
      =========================================================================
      date
      =========================================================================
  -->
  <xsl:template match="date">
    <xsl:choose>
      <xsl:when test="not(text())">
        <xsl:choose>
          <xsl:when test="string-length(@value)=4">
            <xsl:value-of select="@value"/>
          </xsl:when>
          <xsl:when test="string-length(@value)=7">
            <xsl:value-of select="substring(@value, 6, 2)"/>
            <xsl:text>/</xsl:text>
            <xsl:value-of select="substring(@value, 1, 4)"/>
          </xsl:when>
          <xsl:when test="string-length(@value)=10">
            <xsl:value-of select="substring(@value, 9, 2)"/>
            <xsl:text>/</xsl:text>
            <xsl:value-of select="substring(@value, 6, 2)"/>
            <xsl:text>/</xsl:text>
            <xsl:value-of select="substring(@value, 1, 4)"/>
          </xsl:when>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise><xsl:apply-templates/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!--
      =========================================================================
      name
      =========================================================================
  -->
  <xsl:template match="name">
    <em class="pdocName">
      <xsl:attribute name="class">
        <xsl:text>pdocName</xsl:text>
        <xsl:if test="@of">
          <xsl:value-of select="concat(' pdocName-', @of)"/>
        </xsl:if>
      </xsl:attribute>
      <xsl:apply-templates/>
    </em>
  </xsl:template>

  <!--
      =========================================================================
      link mode contributor
      =========================================================================
  -->
  <xsl:template match="link" mode="contributor">
    <a href="{@uri}" class="pdocLink">
      <xsl:choose>
        <xsl:when test="normalize-space() or node()"><xsl:apply-templates/></xsl:when>
        <xsl:otherwise><xsl:value-of select="@uri"/></xsl:otherwise>
      </xsl:choose>
    </a>
  </xsl:template>

  <!--
      =========================================================================
      Miscellaneous
      =========================================================================
  -->
  <xsl:template match="highlight">
    <strong class="pdocHighlight"><xsl:apply-templates/></strong>
  </xsl:template>

  <xsl:template match="emphasis">
    <em class="pdocEmphasis"><xsl:apply-templates/></em>
  </xsl:template>

  <xsl:template match="label">
    <strong class="pdocLabel"><xsl:apply-templates/></strong>
  </xsl:template>


  <!--
      *************************************************************************
                                   CALLABLE TEMPLATE
      *************************************************************************
  -->
  <!--
      =========================================================================
      Template subtitle
      =========================================================================
  -->
  <xsl:template name="subtitle">
    <xsl:param name="nodes" select="head/subtitle"/>
    <xsl:choose>
      <xsl:when test="count($nodes)&gt;1">
        <xsl:for-each select="$nodes">
          <span class="pdocSubtitle{position()}"><xsl:apply-templates/></span><br/>
        </xsl:for-each>
      </xsl:when>
      <xsl:otherwise>
        <span class="pdocSubtitle"><xsl:apply-templates select="$nodes"/></span>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
