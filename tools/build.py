#!/usr/bin/env python3
"""Build the Joomla ko-KR language package.

  build.py [--version 6.2.1.1]   writes metadata into site/ admin/ api/ and dist/pkg_ko-KR.zip

The package contains three language extensions (site, administrator, api), exactly like
the official Joomla packs. Strings that are not translated yet fall back to en-GB.
"""
import argparse, os, sys, zipfile, datetime, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENTS = {"site": "site", "admin": "administrator", "api": "api"}
COPYRIGHT = {"site": "2005", "admin": "2005", "api": "2020"}

META = """<?xml version="1.0" encoding="UTF-8"?>
<metafile client="{client}">
	<name>Korean (ko-KR)</name>
	<version>{version}</version>
	<creationDate>{date}</creationDate>
	<author>Joomla Korean contributors</author>
	<authorUrl>https://github.com/camsonne/joomla-korean</authorUrl>
	<copyright>(C) 2005 Open Source Matters, Inc.</copyright>
	<license>GNU General Public License version 2 or later; see LICENSE.txt</license>
	<description><![CDATA[ko-KR {client} language]]></description>
	<metadata>
		<name>Korean (South Korea)</name>
		<nativeName>한국어 (대한민국)</nativeName>
		<tag>ko-KR</tag>
		<rtl>0</rtl>
		<locale>ko_KR.utf8, ko_KR.UTF-8, ko_KR, kor_KR, ko, korean, korea, kr</locale>
		<firstDay>0</firstDay>
		<weekEnd>0,6</weekEnd>
		<calendar>gregorian</calendar>
	</metadata>
	<params />
</metafile>
"""

INSTALL = """<?xml version="1.0" encoding="UTF-8"?>
<extension client="{client}" type="language" method="upgrade">
	<name>Korean (ko-KR)</name>
	<tag>ko-KR</tag>
	<version>{version}</version>
	<creationDate>{date}</creationDate>
	<author>Joomla Korean contributors</author>
	<authorUrl>https://github.com/camsonne/joomla-korean</authorUrl>
	<copyright>(C) {copyright} Open Source Matters, Inc.</copyright>
	<license>GNU General Public License version 2 or later; see LICENSE.txt</license>
	<description>ko-KR {client} language</description>
	<files>
		<folder>/</folder>
		<filename file="meta">install.xml</filename>
	</files>
	<params />
</extension>
"""

LOCALISE = """<?php

/**
 * @package    Joomla.Language
 *
 * @copyright  (C) 2010 Open Source Matters, Inc. <https://www.joomla.org>
 * @license    GNU General Public License version 2 or later; see LICENSE.txt
 *
 * @phpcs:disable Squiz.Classes.ValidClassName.NotCamelCaps
 *
 * @phpcs:disable PSR1.Classes.ClassDeclaration.MissingNamespace
 */

// phpcs:disable PSR1.Files.SideEffects
\\defined('_JEXEC') or die;
// phpcs:enable PSR1.Files.SideEffects

/**
 * ko-KR localise class.
 *
 * Korean has no grammatical plural; the suffixes are the same as en-GB so that the
 * language keys with a _0, _1 or _ONE variant keep working.
 *
 * @since  1.6
 */
abstract class Ko_KRLocalise
{
    /**
     * Returns the potential suffixes for a specific number of items
     *
     * @param   integer  $count  The number of items.
     *
     * @return  array  An array of potential suffixes.
     *
     * @since   1.6
     */
    public static function getPluralSuffixes($count)
    {
        switch ($count) {
            case 0:
                return ['0'];

            case 1:
                return ['ONE', '1'];
        }

        return ['OTHER', 'MORE'];
    }
}
"""

PKG = """<?xml version="1.0" encoding="UTF-8"?>
<extension type="package" method="upgrade">
	<name>Korean (ko-KR) Language Pack</name>
	<packagename>ko-KR</packagename>
	<version>{version}</version>
	<creationDate>{date}</creationDate>
	<author>Joomla Korean contributors</author>
	<authorUrl>https://github.com/camsonne/joomla-korean</authorUrl>
	<copyright>(C) 2005 Open Source Matters, Inc.</copyright>
	<license>GNU General Public License version 2 or later; see LICENSE.txt</license>
	<description>한국어(ko-KR) 언어 팩 for Joomla {joomla}</description>
	<url>https://github.com/camsonne/joomla-korean</url>
	<packager>Joomla Korean contributors</packager>
	<packagerurl>https://github.com/camsonne/joomla-korean</packagerurl>
	<files>
		<file type="language" client="site" id="ko-KR">site_ko-KR.zip</file>
		<file type="language" client="administrator" id="ko-KR">admin_ko-KR.zip</file>
		<file type="language" client="api" id="ko-KR">api_ko-KR.zip</file>
	</files>
	<blockChildUninstall>true</blockChildUninstall>
	<updateservers>
		<server type="extension" name="Korean (ko-KR) Language Pack" priority="1">https://raw.githubusercontent.com/camsonne/joomla-korean/master/updates/pkg_ko-KR.xml</server>
	</updateservers>
</extension>
"""

UPDATE = """<?xml version="1.0" encoding="utf-8"?>
<updates>
	<update>
		<name>Korean (ko-KR) Language Pack</name>
		<description>Korean language pack for Joomla {joomla}</description>
		<element>pkg_ko-KR</element>
		<type>package</type>
		<client>site</client>
		<version>{version}</version>
		<infourl title="Release notes">https://github.com/camsonne/joomla-korean/releases/tag/v{version}</infourl>
		<downloads>
			<downloadurl type="full" format="zip">{url}</downloadurl>
			<downloadsource type="full" format="zip">{url}</downloadsource>
		</downloads>
		<tags>
			<tag>stable</tag>
		</tags>
		<maintainer>Joomla Korean contributors</maintainer>
		<maintainerurl>https://github.com/camsonne/joomla-korean</maintainerurl>
		<targetplatform name="joomla" version="{platform}"/>
		<php_minimum>8.3</php_minimum>
	</update>
</updates>
"""

def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", default="6.2.1.1")
    ap.add_argument("--date", default=datetime.date.today().strftime("%Y-%m"))
    a = ap.parse_args()
    joomla = ".".join(a.version.split(".")[:3])
    if subprocess.call([sys.executable, os.path.join(ROOT, "tools", "work.py"), "check"]):
        sys.exit("language files do not validate")
    dist = os.path.join(ROOT, "dist"); os.makedirs(dist, exist_ok=True)
    zips = []
    for d, client in CLIENTS.items():
        base = os.path.join(ROOT, d); os.makedirs(base, exist_ok=True)
        meta = dict(client=client, version=a.version, date=a.date, copyright=COPYRIGHT[d])
        write(os.path.join(base, "langmetadata.xml"), META.format(**meta))
        write(os.path.join(base, "install.xml"), INSTALL.format(**meta))
        if d != "api":
            write(os.path.join(base, "localise.php"), LOCALISE)
        files = sorted(f for f in os.listdir(base) if os.path.isfile(os.path.join(base, f)))
        zp = os.path.join(dist, f"{d}_ko-KR.zip")
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files:
                z.write(os.path.join(base, f), f)
        zips.append(zp)
    write(os.path.join(ROOT, "pkg_ko-KR.xml"), PKG.format(version=a.version, date=a.date, joomla=joomla))
    out = os.path.join(dist, f"pkg_ko-KR-{a.version}.zip")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(ROOT, "pkg_ko-KR.xml"), "pkg_ko-KR.xml")
        for zp in zips:
            z.write(zp, os.path.basename(zp))
    # update-server manifest for this release (polled by sites that installed the pack)
    import hashlib
    sha = hashlib.sha256(open(out, "rb").read()).hexdigest()   # printed only: zips are not byte-reproducible
    url = f"https://github.com/camsonne/joomla-korean/releases/download/v{a.version}/pkg_ko-KR-{a.version}.zip"
    major_minor = ".".join(a.version.split(".")[:2])
    os.makedirs(os.path.join(ROOT, "updates"), exist_ok=True)
    write(os.path.join(ROOT, "updates", "pkg_ko-KR.xml"),
          UPDATE.format(joomla=joomla, version=a.version, url=url,
                        platform=major_minor.replace(".", r"\.")))
    print(out, sha)

if __name__ == "__main__":
    main()
