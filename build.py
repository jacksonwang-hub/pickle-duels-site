#!/usr/bin/env python3
"""
Minimal zero-dependency static site builder for the Pickle Duels marketing site.

Why hand-rolled: this machine (and Netlify's Python image) has no guaranteed
third-party packages. Everything here uses only the standard library, so
`python3 build.py` works anywhere Python 3.7+ exists.

Template syntax
---------------
  {{ name }}                       variable substitution (HTML-escaped: no)
  {% include path.html %}          inline another file, inheriting context
  {% include path.html a="1" %}    ...with extra context (may span lines)
  {% if name %}..{% else %}..{% endif %}   truthy conditional

Pages live in src/pages/ and may start with a `---` front-matter block.
A page's `layout:` key names a file in src/layouts/ whose {{ content }} is
replaced by the rendered page body.
"""

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
PAGES = SRC / "pages"
PUBLIC = ROOT / "public"
DIST = ROOT / "dist"

MAX_INCLUDE_DEPTH = 25

RE_FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
# Include tags may span multiple lines so long param values stay readable.
RE_INCLUDE = re.compile(r"\{%\s*include\s+([^\s%]+)\s*(.*?)%\}", re.S)
RE_PARAM = re.compile(r"""(\w+)\s*=\s*("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')""", re.S)
# Innermost-first: the body must not itself contain another {% if %}.
RE_IF = re.compile(
    r"\{%\s*if\s+(\w+)\s*%\}((?:(?!\{%\s*if\s).)*?)\{%\s*endif\s*%\}", re.S
)
RE_ELSE = re.compile(r"\{%\s*else\s*%\}", re.S)
RE_VAR = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def fail(msg):
    print("build error: " + msg, file=sys.stderr)
    sys.exit(1)


def parse_front_matter(text):
    """Return (meta_dict, body). Front matter is simple `key: value` lines."""
    m = RE_FRONT.match(text)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            fail("bad front-matter line (expected `key: value`): " + line)
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, text[m.end():]


def unquote(raw):
    """Strip surrounding quotes and unescape \\" / \\' inside a param value."""
    quote, inner = raw[0], raw[1:-1]
    return inner.replace("\\" + quote, quote)


def resolve_include(name):
    """Includes resolve against src/ — e.g. components/hero.html."""
    path = SRC / name
    if not path.is_file():
        fail("include not found: src/" + name)
    return path


def expand_includes(text, context, depth=0):
    """Recursively inline {% include %} tags, newest params winning."""
    if depth > MAX_INCLUDE_DEPTH:
        fail("include depth exceeded %d — circular include?" % MAX_INCLUDE_DEPTH)
    if "{% include" not in text:
        return text

    def swap(match):
        name, raw_params = match.group(1).strip(), match.group(2)
        local = dict(context)
        for pm in RE_PARAM.finditer(raw_params):
            # Resolve the value against the CALLER's context first. Without this
            # a param written as key="{{ other }}" would reach the child as the
            # literal text "{{ other }}" -- which {% if key %} reads as truthy
            # no matter what `other` actually holds.
            local[pm.group(1)] = substitute(unquote(pm.group(2)), context)
        body = resolve_include(name).read_text(encoding="utf-8")
        # Render the include fully in its own context before splicing it in,
        # so its {% if %} / {{ }} see the params it was called with.
        body = expand_includes(body, local, depth + 1)
        body = apply_conditionals(body, local)
        return substitute(body, local)

    return RE_INCLUDE.sub(swap, text)


def apply_conditionals(text, context):
    """Resolve {% if %}/{% else %}/{% endif %}, innermost blocks first."""
    guard = 0
    while True:
        match = RE_IF.search(text)
        if not match:
            return text
        guard += 1
        if guard > 500:
            fail("runaway {% if %} expansion — check for an unclosed tag")
        name, body = match.group(1), match.group(2)
        parts = RE_ELSE.split(body, maxsplit=1)
        truthy, falsy = parts[0], (parts[1] if len(parts) > 1 else "")
        value = context.get(name, "")
        text = text[: match.start()] + (truthy if str(value).strip() else falsy) + text[match.end():]


UNKNOWN_VARS = set()


def substitute(text, context):
    """Unknown names render empty (so optional params work) but are reported,
    which turns a silent typo into a visible warning at the end of the build."""

    def swap(match):
        name = match.group(1)
        if name not in context:
            UNKNOWN_VARS.add(name)
            return ""
        return str(context[name])

    return RE_VAR.sub(swap, text)


def render(text, context):
    text = expand_includes(text, context)
    text = apply_conditionals(text, context)
    return substitute(text, context)


def check_leftovers(path, text):
    """Catch typo'd tags rather than silently shipping them to the browser."""
    for pattern, label in ((r"\{%", "unresolved {% %} tag"), (r"\{\{", "unresolved {{ }} variable")):
        if re.search(pattern, text):
            snippet = re.search(r".{0,60}" + pattern + r".{0,60}", text, re.S)
            fail("%s in %s near: %s" % (label, path, snippet.group(0).strip()))


def output_path(rel):
    """index.html stays put; every other page becomes a pretty-URL directory."""
    if rel.name == "index.html" or rel.name == "404.html":
        return DIST / rel
    return DIST / rel.parent / rel.stem / "index.html"


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    if PUBLIC.is_dir():
        shutil.copytree(PUBLIC, DIST, dirs_exist_ok=True)

    pages = sorted(PAGES.rglob("*.html"))
    if not pages:
        fail("no pages found in src/pages/")

    for page in pages:
        rel = page.relative_to(PAGES)
        raw = page.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)

        context = dict(meta)
        context["content"] = render(body, context)

        layout_name = meta.get("layout", "base.html")
        layout_path = SRC / "layouts" / layout_name
        if not layout_path.is_file():
            fail("layout not found: src/layouts/" + layout_name)
        out = render(layout_path.read_text(encoding="utf-8"), context)

        check_leftovers(str(rel), out)

        dest = output_path(rel)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out, encoding="utf-8")
        print("  %-28s -> %s" % (str(rel), dest.relative_to(DIST)))

    if UNKNOWN_VARS:
        print("\nwarning: these variables were never defined and rendered empty:")
        for name in sorted(UNKNOWN_VARS):
            print("  {{ %s }}" % name)

    print("\nbuilt %d page(s) into %s/" % (len(pages), DIST.name))


if __name__ == "__main__":
    print("building Pickle Duels site...")
    build()
