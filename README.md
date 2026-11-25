# Joomla 6.2 — Korean (ko-KR) language pack

한국어 언어 팩 for **Joomla 6.2** (built and checked against the 6.2.1 sources).

It is a complete translation of the three Joomla® language clients:

| client | files | strings | translated |
|--------|------:|--------:|-----------:|
| site (front end) | 67 | 2,504 | 100 % |
| administrator | 466 | 10,083 | 100 % |
| api (web services) | 2 | 900 | 100 % |

The installer's own Korean strings (`installation/language/ko-KR`) already ship inside Joomla, so they are
not part of this pack.

## Install

1. Download `pkg_ko-KR-<version>.zip` from the [releases](https://github.com/camsonne/joomla-korean/releases).
2. In Joomla go to **System → Install → Extensions → Upload Package File** and upload the zip.
3. **System → Manage → Languages**: set *Korean (ko-KR)* as the default for the site and/or the administrator.
   (For a multilingual site also create a content language with the tag `ko-KR`.)

The package installs three language extensions (`site`, `administrator`, `api`) in one go and registers an update
server, so a later 6.2.x pack is offered through **System → Update → Extensions**.

The version is `<Joomla version>.<pack revision>`, for example `6.2.1.1`.

## What was decided

* Tone: polite (`~합니다 / ~하세요`), as in Joomla's own Korean installer strings; "Joomla" is written without `!`.
* Glossary (main terms): Article = 글, Category = 카테고리, Module = 모듈, Plugin = 플러그인, Template = 템플릿,
  Extension = 확장 프로그램, Menu item = 메뉴 항목, Access level = 접근 레벨, Publish / Unpublish = 게시 / 게시 중지,
  Trash = 휴지통, Featured = 추천, Check-in / Check-out = 체크인 / 체크아웃, Global Configuration = 전체 환경 설정,
  Workflow = 워크플로, Multi-factor Authentication = 다단계 인증, Passkey = 패스키.
* Dates use `Y년 n월 j일 l`; the week starts on Sunday (`firstDay` 0, weekend 0,6).
* Placeholder text (Lorem ipsum, brand and protocol names) is left as in the English source.
* Keys are never renamed; an untranslated key would simply fall back to `en-GB`.

> **Disclaimer — unofficial, interim pack.** This is *not* the official Joomla Korean translation. It was produced
> automatically by an AI assistant (Claude) from the English Joomla 6.2.1 language files, using the Korean wording of
> the existing Joomla installer pack (`installation/language/ko-KR`) as a style reference, and it has **not yet been
> reviewed by native speakers**. It is a stop-gap until an official Korean 6.2 language pack is released; once that
> exists, please switch to it. Use at your own risk, and corrections are very welcome — see *Contributing*.
> "Joomla!" is a registered trademark of Open Source Matters, Inc.; this project is not affiliated with or endorsed by it.

## Layout

```
site/  admin/  api/       the language files (one .ini per Joomla extension) + langmetadata.xml, install.xml, localise.php
pkg_ko-KR.xml             package manifest
updates/pkg_ko-KR.xml     update-server manifest (the package points at it)
tools/work.py             translation workflow + validator
tools/build.py            builds dist/pkg_ko-KR-<version>.zip and the update manifest
tools/phpcheck.php        parses every .ini the way Joomla does
```

## Contributing / fixing a string

Edit the `.ini` value directly (keep the key, the placeholders `%s`, `%1$s`, `{NAME}`, HTML tags and `\n`), then:

```bash
JOOMLA_SRC=/path/to/joomla-cms-6.2.x python3 tools/work.py check   # placeholders, quotes, unknown keys
php tools/phpcheck.php                                             # same parser as Joomla
python3 tools/build.py --version 6.2.1.2                           # builds dist/ and updates/
```

`work.py check` compares every file with the English source in `$JOOMLA_SRC`, a checkout of the matching Joomla tag
(`git clone --depth 1 --branch 6.2.1 https://github.com/joomla/joomla-cms`). The variable is required.

## Updating to a new Joomla release (6.2.x / 6.3)

```bash
git -C $JOOMLA_SRC checkout 6.3.0
python3 tools/work.py status          # how many strings are new
python3 tools/work.py todo admin com_content.ini 1 80    # new strings of a file, numbered
python3 tools/work.py apply admin com_content.ini batch.txt   # batch.txt: "N|translation" lines
python3 tools/work.py reuse           # fill strings that are identical to already translated ones
python3 tools/work.py check && python3 tools/build.py --version 6.3.0.1
```

A tag `vX.Y.Z.N` runs `.github/workflows/release.yml`, which validates, builds and attaches the zip to a GitHub release.

## License

**GPL-2.0-or-later** — GNU General Public License, version 2 or (at your option) any later version, the same
license as Joomla. The full text of version 2 is in [LICENSE.txt](LICENSE.txt).

* The translations are derivative works of the Joomla language files (© Open Source Matters, Inc.), so they must be
  distributed under the GPL as well.
* The scripts in `tools/` carry an `SPDX-License-Identifier: GPL-2.0-or-later` header.
* © 2026 Joomla Korean contributors.
