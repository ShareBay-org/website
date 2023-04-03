<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:output method="html" indent="yes"/>
	<xsl:template match="freelist">
	<xsl:variable name="APP" select="header/appName"/>
		<html lang="en">
			<head>
				<title>Freelist.xml from <xsl:value-of select="header/appID"/></title>
				<style type="text/css">
				body {  
					font-family: Arial;
				  }
				img {
					width: 80%;
					height: auto;
				  }
				  .white-space-pre-line {
				  white-space: pre-line;
				  }
				  div{
				  padding: 0.1px 1em 1em 1em;
				  max-width: 800px;
				  }
				  div:nth-child(even){
				  background: #eee;
				  }
				  .smaller{
				  font-size: 80%;
				  }
				</style>
			</head>
			<body>
				<h1>This is the current freelist.xml of <xsl:value-of select="header/appName"/>
				</h1>
				<hr/>
				<xsl:for-each select="list/item">
					<div>
						<h2>
							<xsl:value-of select="title"/>
						</h2>
						<p>
						<xsl:value-of select="description"/>
						</p>
						<p>
						<xsl:choose>
							<xsl:when test="string(imageURL)">
								<xsl:element name="img">
									<xsl:attribute name="src"><xsl:value-of select="imageURL"/></xsl:attribute>
									<xsl:attribute name="alt"><xsl:value-of select="title"/></xsl:attribute>
								</xsl:element>
							</xsl:when>
						</xsl:choose>
						</p>
						<p>
							<xsl:text>Location: </xsl:text>
							<xsl:value-of select="state"/>
							<xsl:text>, </xsl:text>
							<xsl:value-of select="countryName"/>
							<xsl:text> </xsl:text>
						<xsl:element name="a">
							<xsl:attribute name="href"><xsl:text>https://www.openstreetmap.org/?mlat=</xsl:text><xsl:value-of select="lat"/><xsl:text>&amp;mlon=</xsl:text><xsl:value-of select="long"/><xsl:text>#map=16/</xsl:text><xsl:value-of select="lat"/><xsl:text>/</xsl:text><xsl:value-of select="long"/></xsl:attribute>
							<xsl:attribute name="target">_blank</xsl:attribute>
							<xsl:text>See map</xsl:text>
						</xsl:element>
						</p>
						<p>
						<xsl:value-of select="quantity"/>
						<xsl:text> available</xsl:text>
						<xsl:text> (</xsl:text>
						<xsl:value-of select="terms"/>
						<xsl:text>) </xsl:text>
						<xsl:element name="a">
							<xsl:attribute name="href"><xsl:value-of select="url"/></xsl:attribute>
							<xsl:attribute name="target">_blank</xsl:attribute>
							<xsl:text>Apply on </xsl:text>
							<xsl:value-of select="$APP"/>
						</xsl:element>
						</p>
						<p class="smaller">
						<xsl:choose>
							<xsl:when test="string(category)">
						<xsl:text>Posted in: </xsl:text>
						<xsl:value-of select="category"/>
							<xsl:text>, </xsl:text>
							</xsl:when>
						</xsl:choose>
						<xsl:choose>
							<xsl:when test="string(updated)">
						<xsl:value-of select="updated"/>
							<xsl:text>, </xsl:text>
							</xsl:when>
						</xsl:choose>
						<xsl:choose>
							<xsl:when test="string(tags)">
						<xsl:text>Tags: </xsl:text>
						<xsl:value-of select="tags"/>
							<xsl:text>, </xsl:text>
							</xsl:when>
						</xsl:choose>
						<xsl:choose>
							<xsl:when test="string(language)">
						<xsl:text>Language: </xsl:text>
						<xsl:value-of select="language"/>
							</xsl:when>
						</xsl:choose>
						</p>
					</div>
				</xsl:for-each>
				<hr width="10%" size="10" align="center" color="blue"/>
				<div class="white-space-pre-line">
					<h3>Comments</h3>
					<xsl:value-of select="comments"/>
				</div>
			</body>
		</html>
	<!-- /xsl:variable -->
	</xsl:template>
</xsl:stylesheet>
