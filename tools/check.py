#!/usr/bin/env python3
"""
Post-build verifier: broken links, accessibility basics, placeholder inventory.

Usage:  python3 build.py && python3 tools/check.py
Exits non-zero if anything is actually broken, so it can gate a deploy.
"""

import re
import sys
from pathlib import Path

DIST = Path(__file__).resolve().parent.parent / "dist"
PLACEHOLDER = re.compile(r"\[PLACEHOLDER:[^\]]*\]")


def load():
    if not DIST.is_dir():
        sys.exit("dist/ not found — run `python3 build.py` first.")
    return {str(p.relative_to(DIST)): p.read_text(encoding="utf-8")
            for p in sorted(DIST.rglob("*.html"))}


def check_links(pages):
    ids = {name: set(re.findall(r'id="([^"]+)"', html)) for name, html in pages.items()}
    broken = []

    for name, html in pages.items():
        for ref in re.findall(r'(?:href|src)="([^"]+)"', html):
            if ref.startswith(("http://", "https://", "mailto:", "tel:", "data:", "[PLACEHOLDER")):
                continue
            if ref.startswith("#"):
                if ref[1:] not in ids[name]:
                    broken.append("%s -> %s (no such id on page)" % (name, ref))
                continue
            path, _, frag = ref.partition("#")
            target = DIST / path.lstrip("/")
            if target.is_dir() or path.endswith("/"):
                target = target / "index.html"
            if not target.exists():
                broken.append("%s -> %s (missing file)" % (name, ref))
            elif frag:
                key = str(target.relative_to(DIST))
                if frag not in ids.get(key, set()):
                    broken.append("%s -> %s (no such id on target)" % (name, ref))
    return broken


def check_a11y(pages):
    problems = []
    for name, html in pages.items():
        if len(re.findall(r"<h1[^>]*>", html)) != 1:
            problems.append("%s: should have exactly one <h1>" % name)

        prev = 0
        for level in (int(m) for m in re.findall(r"<h([1-6])[^>]*>", html)):
            if prev and level > prev + 1:
                problems.append("%s: heading jumps h%d -> h%d" % (name, prev, level))
            prev = level

        for img in re.findall(r"<img[^>]*>", html):
            if "alt=" not in img:
                problems.append("%s: <img> without alt — %s" % (name, img[:60]))

        for control in re.findall(r'<(?:input|select|textarea)[^>]*id="([^"]+)"', html):
            if 'for="%s"' % control not in html:
                problems.append("%s: form control #%s has no <label for>" % (name, control))

        for needle, label in (
            ('lang="en"', "lang attribute"),
            ('<main id="main">', "main landmark"),
            ('class="skip-link"', "skip link"),
        ):
            if needle not in html:
                problems.append("%s: missing %s" % (name, label))
    return problems


def inventory_placeholders(pages):
    found = {}
    for name, html in pages.items():
        for hit in PLACEHOLDER.findall(html):
            found.setdefault(hit, set()).add(name)
    return found


def main():
    pages = load()
    print("checked %d page(s)\n" % len(pages))

    broken = check_links(pages)
    print("LINKS: %s" % ("%d broken" % len(broken) if broken else "all resolve"))
    for item in broken:
        print("  BROKEN  " + item)

    problems = check_a11y(pages)
    print("\nACCESSIBILITY: %s" % ("%d issue(s)" % len(problems) if problems else "no issues found"))
    for item in problems:
        print("  ISSUE  " + item)

    found = inventory_placeholders(pages)
    print("\nPLACEHOLDERS: %d distinct" % len(found))
    for text in sorted(found):
        print("  %s\n      in: %s" % (text, ", ".join(sorted(found[text]))))

    if broken or problems:
        print("\nFAILED")
        return 1
    print("\nPASSED (placeholders are expected until real content lands)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
