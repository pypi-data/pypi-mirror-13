<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publidoc2html5_media.inc.xsl 3f13391148b5 2015/12/03 11:54:51 Coraline $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns="http://www.w3.org/1999/xhtml">

  <!--
      *************************************************************************
                                        AUDIO
      *************************************************************************
  -->
  <!--
      =========================================================================
      audio
      =========================================================================
  -->
  <xsl:template match="audio">
    <xsl:if test="$aud">
      <xsl:choose>
        <xsl:when test="$js and $aud_custom">
          <span class="pdocAudioPlayer">
            <xsl:call-template name="audio">
              <xsl:with-param name="controls" select="0"/>
            </xsl:call-template>
            <span data-player="button-play">
              <xsl:call-template name="audio_symbol">
                <xsl:with-param name="id" select="@id"/>
              </xsl:call-template>
            </span>
          </span>
        </xsl:when>
        <xsl:otherwise>
         <xsl:call-template name="audio"/> 
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

  <xsl:template match="audio" mode="media">
    <xsl:if test="$aud">
      <xsl:choose>
        <xsl:when test="@type='background'">
          <xsl:call-template name="audio">
            <xsl:with-param name="controls" select="0"/>
            <xsl:with-param name="autoplay" select="1"/>
          </xsl:call-template>
        </xsl:when>
        <xsl:when test="$js and $aud_custom">
          <div class="pdocAudioPlayer">
            <xsl:call-template name="audio">
              <xsl:with-param name="controls" select="0"/>
              <xsl:with-param name="preload" select="1"/>
            </xsl:call-template>
            <div data-player="button-play">
              <xsl:call-template name="audio_symbol">
                <xsl:with-param name="id" select="@id"/>
              </xsl:call-template>
            </div>
            <div data-player="duration">0:00 / 0:00</div>
            <div data-player="timeline">
              <div data-player="cursor"><xsl:text> </xsl:text></div>
            </div>
          </div>
        </xsl:when>
        <xsl:otherwise>
          <xsl:call-template name="audio"/>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
