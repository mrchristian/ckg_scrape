<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text" encoding="UTF-8" />
  <xsl:strip-space elements="*"/>
  <xsl:template match="text()"/>

  <xsl:template match="/work/publication">
    <xsl:text>= </xsl:text><xsl:value-of select="title"/><xsl:text> =&#10;</xsl:text>
    <xsl:apply-templates select="series"/>
  </xsl:template>

  <xsl:template match="series">
    <xsl:text>== </xsl:text><xsl:value-of select="title"/><xsl:text> ==&#10;</xsl:text>

    <!-- Metadata Section -->
    <xsl:text>'''DOI:''' [https://doi.org/</xsl:text>
    <xsl:value-of select="doi"/>
    <xsl:text> </xsl:text>
    <xsl:value-of select="doi"/>
    <xsl:text>] | </xsl:text>
    <xsl:text>'''Date:''' </xsl:text>
    <xsl:value-of select="date"/>
    <xsl:text>&#10;&#10;</xsl:text>

    <!-- 1. Process Front Matter -->
    <xsl:text>=== Front Matter ===&#10;</xsl:text>
    <xsl:call-template name="chapter_table">
      <xsl:with-param name="nodes" select="front_matter/chapter"/>
    </xsl:call-template>

    <!-- 2. Process Books/Chapters -->
    <xsl:for-each select="books/book">
      <xsl:text>=== </xsl:text><xsl:value-of select="title"/><xsl:text> ===&#10;</xsl:text>
      <xsl:call-template name="chapter_table">
        <xsl:with-param name="nodes" select="chapters/chapter"/>
      </xsl:call-template>
    </xsl:for-each>
  </xsl:template>

  <!-- Reusable Table Template -->
  <xsl:template name="chapter_table">
    <xsl:param name="nodes"/>
    <xsl:text>{| class="wikitable sortable" style="width:100%"&#10;</xsl:text>
    <xsl:text>! ID !! Title !! DOI !! Wiki !! Resources&#10;</xsl:text>
    <xsl:for-each select="$nodes">
      <xsl:text>|-&#10;</xsl:text>
      <xsl:text>| </xsl:text><xsl:value-of select="@id"/><xsl:text>&#10;</xsl:text>
      <xsl:text>| '''</xsl:text><xsl:value-of select="title"/><xsl:text>'''&#10;</xsl:text>
      <xsl:text>| [https://doi.org/</xsl:text><xsl:value-of select="doi"/><xsl:text></xsl:text><xsl:text> </xsl:text><xsl:value-of select="doi"/><xsl:text>]&#10;</xsl:text>
      <xsl:text>| [</xsl:text><xsl:value-of select="wiki"/><xsl:text> Link]&#10;</xsl:text>
      <xsl:text>| [</xsl:text><xsl:value-of select="source"/><xsl:text> Source]</xsl:text>
      <xsl:text>&lt;br /&gt;</xsl:text>
      <xsl:text>[</xsl:text><xsl:value-of select="pdf"/><xsl:text> PDF]</xsl:text>
      <xsl:text>&lt;br /&gt;</xsl:text>
      <xsl:text>[https://openalex.org/</xsl:text><xsl:value-of select="openalex"/><xsl:text> OpenAlex]&#10;</xsl:text>
    </xsl:for-each>
    <xsl:text>|}&#10;&#10;</xsl:text>
  </xsl:template>
</xsl:stylesheet>
<!-- vim: set shiftwidth=2 tabstop=2 softtabstop=2 expandtab: -->
