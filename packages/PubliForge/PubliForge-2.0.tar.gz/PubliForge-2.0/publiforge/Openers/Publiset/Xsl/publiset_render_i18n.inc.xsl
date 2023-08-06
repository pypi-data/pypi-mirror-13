<?xml version='1.0' encoding="utf-8"?>
<!-- $Id: publiset_render_i18n.inc.xsl 7627ff288a79 2015/05/24 20:23:48 Patrick $ -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:variable name="i18n_head">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">En-tête</xsl:when>
      <xsl:otherwise>Head</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_language">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Langue</xsl:when>
      <xsl:otherwise>Language</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_path">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Chemin vers les fichiers</xsl:when>
      <xsl:otherwise>Path to files</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_pi_source">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Source en PI</xsl:when>
      <xsl:otherwise>Source as PI</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_xpath">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">XPath pour le contenu</xsl:when>
      <xsl:otherwise>XPath for content</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_xslt">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">XSLT pour le contenu</xsl:when>
      <xsl:otherwise>XSLT for content</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_as">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Converti en</xsl:when>
      <xsl:otherwise>Converted into</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_attributes">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Attributs</xsl:when>
      <xsl:otherwise>Attributes</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_transform">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">XSLT pour la balise</xsl:when>
      <xsl:otherwise>XSLT for tag</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_title">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Titre</xsl:when>
      <xsl:otherwise>title</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_shorttitle">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Titre court</xsl:when>
      <xsl:otherwise>Short title</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_subtitle">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Sous-titre</xsl:when>
      <xsl:otherwise>Subtitle</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_identifier">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Identifiant</xsl:when>
      <xsl:otherwise>Identifier</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_copyright">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Copyright</xsl:when>
      <xsl:otherwise>Copyright</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_collection">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Collection</xsl:when>
      <xsl:otherwise>Collection</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_contributors">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Contributeurs</xsl:when>
      <xsl:otherwise>Contributors</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_date">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Date</xsl:when>
      <xsl:otherwise>Date</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_source">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Source</xsl:when>
      <xsl:otherwise>Source</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_subjects">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Thèmes</xsl:when>
      <xsl:otherwise>Subjects</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_keywords">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Mots clés</xsl:when>
      <xsl:otherwise>Keywords</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_abstract">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Résumé</xsl:when>
      <xsl:otherwise>Abstract</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

  <xsl:variable name="i18n_cover">
    <xsl:choose>
      <xsl:when test="starts-with($lang, 'fr')">Couverture</xsl:when>
      <xsl:otherwise>Cover</xsl:otherwise>
    </xsl:choose>
  </xsl:variable>

</xsl:stylesheet>
