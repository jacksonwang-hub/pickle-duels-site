#!/usr/bin/env python3
"""
Export a built legal page to a .docx for legal review.

Usage:  python3 build.py && python3 tools/export-legal-docx.py [privacy|terms|all]

Reads straight from dist/<page>/index.html, so a document can never drift
from what is actually published.

Why this is hand-rolled: there is no Node, pandoc, or LibreOffice on this
machine, and macOS `textutil` flattens tables into prose and discards
highlighting -- both of which matter in a review document. A .docx is a ZIP
of XML, so the standard library is enough.
"""

import html as H
import re
import zipfile
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAGES = {
    "privacy": ("Pickle Duels Privacy Policy", "Pickle-Duels-Privacy-Policy-DRAFT.docx",
                "Draft privacy policy covering the Pickle Duels website, player app, and VenueOS"),
    "terms": ("Pickle Duels Terms of Service", "Pickle-Duels-Terms-of-Service-DRAFT.docx",
              "Draft terms of service covering the Pickle Duels website, player app, and VenueOS"),
}

# Where each draft came from, so a reviewer knows what it is grounded in.
PREPARED = {
    "privacy":
        "The app section preserves the commitments in the existing Pickle Duels privacy policy "
        "(effective Aug 8, 2025) linked from the App Store listing at "
        "pickleball-web-server.onrender.com/privacy-policy. The website section reflects a runtime "
        "audit of the live site, which sets no cookies, writes nothing to browser storage, and "
        "makes no third-party requests. The VenueOS section reflects its sign-in page, which "
        "authenticates via Clerk and offers Google and Facebook sign-in. Apple's App Privacy "
        "labels for the app declare only Contact Info (name, email). This draft has not been "
        "reviewed by a lawyer and is not legal advice.",
    "terms":
        "No Terms of Service previously existed for Pickle Duels: the onrender /terms route is an "
        "empty page, and the App Store listing links Terms of Use to clmsstudio.com for a "
        "different app, Paddle Wars, published by CLMS Studio LLC. This draft is original text "
        "written against what Pickle Duels and VenueOS actually do; no wording was taken from that "
        "other document. This draft has not been reviewed by a lawyer and is not legal advice.",
}

PLACEHOLDER = re.compile(r"(\[PLACEHOLDER:[^\]]*\])")


# --- Parse the page into a block model ------------------------------------

class Doc(HTMLParser):
    """Collect headings, paragraphs, lists and tables as structured blocks.

    A run is (text, bold). Highlighting is derived later from the text itself,
    so placeholders stay marked wherever they appear.
    """

    BLOCKS = {"h2", "h3", "p", "li", "th", "td"}

    def __init__(self):
        super().__init__()
        self.blocks = []
        self.runs = []
        self.bold = 0
        self.mode = None
        self.in_notice = False
        self.table = None
        self.row = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "div" and "review-notice" in a.get("class", ""):
            self.in_notice = True
        elif tag == "table":
            self.table = []
        elif tag == "tr":
            self.row = []
        elif tag in self.BLOCKS:
            self.mode, self.runs = tag, []
        elif tag in ("strong", "b"):
            self.bold += 1

    def handle_endtag(self, tag):
        if tag == "div" and self.in_notice and self.mode is None:
            self.in_notice = False
        elif tag == "table":
            if self.table:
                self.blocks.append(("table", self.table))
            self.table = None
        elif tag == "tr":
            if self.row is not None:
                self.table.append(self.row)
            self.row = None
        elif tag in ("strong", "b"):
            self.bold = max(0, self.bold - 1)
        elif tag in self.BLOCKS and self.mode == tag:
            runs = [(t, b) for t, b in self.runs if t.strip()]
            if runs:
                if tag in ("th", "td"):
                    self.row.append((tag, runs))
                else:
                    kind = tag if tag != "p" else ("notice-p" if self.in_notice else "p")
                    if tag == "li" and self.in_notice:
                        kind = "notice-li"
                    if tag == "h2" and self.in_notice:
                        kind = "notice-h"
                    self.blocks.append((kind, runs))
            self.mode = None

    def handle_data(self, d):
        if self.mode:
            text = re.sub(r"\s+", " ", d)
            if text:
                self.runs.append((text, self.bold > 0))


# --- OOXML emitters --------------------------------------------------------

def esc(t):
    return H.escape(t, quote=False)


def runs_xml(runs, size=None, color=None):
    """Emit runs, highlighting placeholder text.

    Placeholders are matched against the paragraph's full text rather than
    one run at a time: a placeholder containing bold text arrives as several
    runs, and matching per-run would miss it entirely.
    """
    joined = "".join(t for t, _ in runs)
    spans = [m.span() for m in PLACEHOLDER.finditer(joined)]
    inside = lambda i: any(a <= i < b for a, b in spans)

    out, pos = [], 0
    for text, bold in runs:
        start = pos
        pos += len(text)
        if not text:
            continue
        # Split this run wherever its highlight state changes.
        piece, state, i = "", inside(start), 0
        for i, ch in enumerate(text):
            cur = inside(start + i)
            if cur != state and piece:
                out.append(_run(piece, bold, state, size, color))
                piece, state = "", cur
            state = cur
            piece += ch
        if piece:
            out.append(_run(piece, bold, state, size, color))
    return "".join(out)


def _run(text, bold, highlight, size, color):
    props = []
    if bold:
        props.append("<w:b/>")
    if color:
        props.append('<w:color w:val="%s"/>' % color)
    if size:
        props.append('<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (size, size))
    if highlight:
        props.append('<w:highlight w:val="yellow"/>')
    rpr = "<w:rPr>%s</w:rPr>" % "".join(props) if props else ""
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (rpr, esc(text))


def para(runs, style="Body", **kw):
    return '<w:p><w:pPr><w:pStyle w:val="%s"/></w:pPr>%s</w:p>' % (style, runs_xml(runs, **kw))


def bullet(runs, **kw):
    return ('<w:p><w:pPr><w:pStyle w:val="Body"/>'
            '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'
            '<w:spacing w:after="60"/></w:pPr>%s</w:p>' % runs_xml(runs, **kw))


def table_xml(rows):
    total = 9360  # Letter minus 1" margins, in DXA
    ncols = max(len(r) for r in rows)
    width = total // ncols
    grid = "".join('<w:gridCol w:w="%d"/>' % width for _ in range(ncols))

    body = []
    for row in rows:
        cells = []
        for tag, runs in row:
            shade = '<w:shd w:val="clear" w:color="auto" w:fill="EFEFEF"/>' if tag == "th" else ""
            cells.append(
                '<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s</w:tcPr>%s</w:tc>'
                % (width, shade,
                   '<w:p><w:pPr><w:pStyle w:val="Cell"/></w:pPr>%s</w:p>'
                   % runs_xml([(t, b or tag == "th") for t, b in runs], size=18)))
        body.append("<w:tr>%s</w:tr>" % "".join(cells))

    borders = "".join(
        '<w:%s w:val="single" w:sz="4" w:space="0" w:color="999999"/>' % e
        for e in ("top", "left", "bottom", "right", "insideH", "insideV"))
    return ('<w:tbl><w:tblPr><w:tblW w:w="%d" w:type="dxa"/>'
            '<w:tblBorders>%s</w:tblBorders></w:tblPr>'
            '<w:tblGrid>%s</w:tblGrid>%s</w:tbl><w:p/>'
            % (total, borders, grid, "".join(body)))


STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr>
<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/><w:sz w:val="22"/>
</w:rPr></w:rPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>
<w:style w:type="paragraph" w:styleId="Body"><w:name w:val="Body Text"/>
<w:pPr><w:spacing w:after="140" w:line="276" w:lineRule="auto"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Cell"><w:name w:val="Table Cell"/>
<w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/>
<w:pPr><w:spacing w:after="60"/><w:outlineLvl w:val="0"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="44"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/>
<w:pPr><w:spacing w:after="300"/></w:pPr>
<w:rPr><w:color w:val="555555"/><w:sz w:val="20"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/>
<w:pPr><w:keepNext/><w:spacing w:before="360" w:after="120"/><w:outlineLvl w:val="0"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="30"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/>
<w:pPr><w:keepNext/><w:spacing w:before="260" w:after="100"/><w:outlineLvl w:val="1"/></w:pPr>
<w:rPr><w:b/><w:sz w:val="24"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Banner"><w:name w:val="Banner"/>
<w:pPr><w:pBdr>
<w:top w:val="single" w:sz="12" w:space="6" w:color="CC0000"/>
<w:left w:val="single" w:sz="12" w:space="6" w:color="CC0000"/>
<w:bottom w:val="single" w:sz="12" w:space="6" w:color="CC0000"/>
<w:right w:val="single" w:sz="12" w:space="6" w:color="CC0000"/>
</w:pBdr><w:spacing w:after="140"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Note"><w:name w:val="Note"/>
<w:pPr><w:pBdr><w:top w:val="single" w:sz="4" w:space="8" w:color="999999"/></w:pBdr>
<w:spacing w:before="400" w:after="0"/></w:pPr>
<w:rPr><w:color w:val="444444"/><w:sz w:val="18"/></w:rPr></w:style>
</w:styles>"""

NUMBERING = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0">
<w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="&#8226;"/>
<w:lvlJc w:val="left"/>
<w:pPr><w:ind w:left="567" w:hanging="283"/></w:pPr>
<w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:hint="default"/></w:rPr>
</w:lvl></w:abstractNum>
<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>"""

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>"""

DOC_RELS = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>"""


def export(slug):
    title, filename, subject = PAGES[slug]
    src = ROOT / "dist" / slug / "index.html"
    out = ROOT / "legal" / filename
    if not src.exists():
        raise SystemExit("%s not found — run `python3 build.py` first." % src)

    page = src.read_text(encoding="utf-8")
    # Only the page's prose block -- otherwise the footer's column headings
    # (Play / Organize / Company) are parsed as document headings.
    prose = re.search(r'<div class="prose">(.*?)\n      </div>\n', page, re.S)
    if not prose:
        raise SystemExit("could not isolate the .prose block in the built page")

    parser = Doc()
    parser.feed(prose.group(1))
    blocks = parser.blocks

    n_ph = sum(len(PLACEHOLDER.findall(t)) for kind, c in blocks
               if kind != "table" for t, _ in c)
    n_ph += sum(len(PLACEHOLDER.findall(t)) for kind, rows in blocks if kind == "table"
                for row in rows for _, runs in row for t, _ in runs)

    today = date.today().strftime("%d %B %Y")
    body = [
        para([(title, False)], "Title"),
        para([("DRAFT FOR LEGAL REVIEW — NOT PUBLISHED AS FINAL", True),
              (" · Prepared %s · %d items need input, highlighted in yellow · "
               "Live draft: heartfelt-pony-dcc6b9.netlify.app/%s/" % (today, n_ph, slug), False)],
             "Subtitle"),
    ]

    for kind, content in blocks:
        if kind == "table":
            body.append(table_xml(content))
        elif kind == "h2":
            body.append(para(content, "Heading1"))
        elif kind == "h3":
            body.append(para(content, "Heading2"))
        elif kind == "notice-h":
            body.append(para(content, "Banner", color="CC0000"))
        elif kind in ("notice-p",):
            body.append(para(content, "Banner"))
        elif kind in ("li", "notice-li"):
            body.append(bullet(content))
        else:
            body.append(para(content))

    body.append(para([("How this draft was prepared. ", True),
                       (PREPARED[slug], False)], "Note"))

    document = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:body>%s'
        '<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" '
        'w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'
        '</w:body></w:document>' % "".join(body))

    core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/">'
            '<dc:title>%s (Draft for Legal Review)</dc:title>'
            '<dc:subject>%s</dc:subject>'
            '</cp:coreProperties>' % (esc(title), esc(subject)))
    app = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
           '<Application>Pickle Duels site export</Application></Properties>')

    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/document.xml", document)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/styles.xml", STYLES)
        z.writestr("word/numbering.xml", NUMBERING)
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)

    print("wrote %-50s %2d blocks, %2d placeholders"
          % (out.relative_to(ROOT), len(blocks), n_ph))


if __name__ == "__main__":
    import sys
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for slug in (list(PAGES) if which == "all" else [which]):
        if slug not in PAGES:
            raise SystemExit("unknown page %r — choose: %s, all" % (slug, ", ".join(PAGES)))
        export(slug)
