# Pickle Duels — marketing site

Static marketing site for **Pickle Duels** (player app) and **VenueOS** (pickleball
tournament management software for clubs and organizers). Powered by RallyXP.

Three audience sections: **Play**, **Organize**, **Company**.

---

## Quick start

```bash
./dev.sh
```

That builds the site and serves it at <http://localhost:4321>. Pass a port to
override: `./dev.sh 8080`.

**Requirements: Python 3.8+ only.** No Node, no npm, no dependencies to install.
(3.8 is the floor because the build uses `shutil.copytree(dirs_exist_ok=True)`.)

To build without serving:

```bash
python3 build.py
```

Output lands in `dist/`, which is disposable and git-ignored.

To verify the build (broken links, accessibility basics, placeholder inventory):

```bash
python3 tools/check.py
```

---

## Project layout

```
build.py              Static site generator (~190 lines, stdlib only)
dev.sh                Build + serve locally
netlify.toml          Netlify build and header config
tools/check.py        Link checker, a11y audit, placeholder inventory

src/
  layouts/base.html   Page shell — every page uses this
  partials/           head, header, footer (shared across all pages)
  components/         Reusable blocks (see below)
  pages/              One file per route

public/               Copied verbatim into dist/
  css/site.css        All styles, design tokens at the top
  js/site.js          Progressive enhancement only
  fonts/              Self-hosted Archivo + Inter (variable woff2)
  images/             Photography

dist/                 Build output — never edit, never commit
```

### Routes

| Source | URL |
|---|---|
| `src/pages/index.html` | `/` |
| `src/pages/play.html` | `/play/` |
| `src/pages/organize.html` | `/organize/` |
| `src/pages/company.html` | `/company/` |
| `src/pages/organize/thanks.html` | `/organize/thanks/` |
| `src/pages/404.html` | `/404.html` |

Every page except `index.html` and `404.html` becomes a pretty-URL directory.

---

## Templating

`build.py` implements a deliberately small template language. There are three tags.

**Variables** — `{{ name }}`. An undefined name renders empty and is reported as a
warning at the end of the build, so typos surface instead of silently vanishing.

**Includes** — pull in a partial or component, optionally with parameters. The tag
may span multiple lines so long values stay readable:

```html
{% include components/feature-card.html
   title="QR code score tracking"
   body="Scan another player's QR code and instantly team up."
%}
```

Parameters may be double- or single-quoted. Use single quotes when the value itself
contains double quotes (SVG markup, for example).

**Conditionals** — `{% if name %}...{% else %}...{% endif %}`. Truthy means
"defined and not empty", which is how optional component parameters work.

### Front matter

Each page starts with a `---` block of simple `key: value` lines:

```yaml
---
layout: base.html
title: Play — Pickle Duels
description: Download Pickle Duels to track your results...
ctaLabel: Get the App
ctaHref: #get-the-app
ctaClass: btn--volt
playCurrent: aria-current="page"
organizeCurrent:
companyCurrent:
---
```

The rendered page body replaces `{{ content }}` in the named layout.

`ctaLabel` / `ctaHref` / `ctaClass` drive the **persistent header CTA**, which adapts
by section — "Get the App" on Home and Play, "Book a Demo" on Organize and Company.

`playCurrent` / `organizeCurrent` / `companyCurrent` set `aria-current="page"` on the
active nav item. **Declare all three on every page**, leaving the inactive ones empty —
that is what keeps them out of the undefined-variable warnings.

### Components

| Component | Used for |
|---|---|
| `page-hero.html` | Interior page heroes (Play, Organize, Company) |
| `path-card.html` | Home "choose your path" cards |
| `feature-card.html` | Play feature grid |
| `capability.html` | Organize capability rows (numbered, alternating) |
| `cta-band.html` | Full-width call-to-action bands |
| `founder-card.html` | Company founder cards |
| `value.html` | Company values grid |
| `store-badges.html` | App Store / Google Play buttons |
| `placeholder.html` | Labeled placeholder image blocks |

---

## Design system

All tokens live at the top of `public/css/site.css` under `:root`. Change them there,
not in individual rules.

| Token | Value | Use |
|---|---|---|
| `--ink` | `#0B1512` | Text, dark sections |
| `--court` | `#0E7C4A` | VenueOS / Organize primary |
| `--volt` | `#C8FF3D` | Play CTAs, accents — **Ink text only** |
| `--mint` | `#D7F5E3` | Soft backgrounds |
| `--chalk` | `#F7F9F7` | Alternate page background |
| `--clay` | `#FF5A3C` | **Decorative only** — fails AA for text |
| `--slate` | `#5C6B64` | Muted text |

Type: **Archivo** (display, uppercase, tight tracking) + **Inter** (body). Both are
self-hosted variable fonts — two files, 84 KB total, no external requests.

Every text/background pairing in use meets WCAG AA (4.5:1). `--volt` and `--clay` are
light enough that they must never carry white text.

---

## Content conventions

Anything awaiting real content is marked `[PLACEHOLDER: description]`. Find them all:

```bash
grep -rn "\[PLACEHOLDER:" src/
```

or run `python3 tools/check.py`, which prints a grouped inventory with page locations.

Rules this site follows, and edits should keep:

- No invented statistics, customer names, testimonials, pricing, or prize values.
- Copy is reused from the source sites where it exists, tightened but not changed in meaning.

---

## The demo request form

`/organize/#demo` uses **Netlify Forms** — no backend.

- Detected at deploy time via `data-netlify="true"` plus the hidden `form-name` field.
- `netlify-honeypot="bot-field"` provides spam filtering with no third-party service.
- **With JavaScript:** submits via `fetch` and shows an inline success state.
- **Without JavaScript:** posts normally and Netlify serves `/organize/thanks/`.

Both paths are live, so the form works even if the script fails to load.

Submissions appear under **Forms** in the Netlify dashboard. No notification email is
configured — to add one, go to *Site configuration → Forms → Form notifications*.

---

## Deploying to Netlify

### From Git (recommended)

1. Push this directory to a Git repository.
2. In Netlify: **Add new site → Import an existing project**, pick the repo.
3. Netlify reads `netlify.toml`, so the settings below are filled in already:
   - **Build command:** `python3 build.py`
   - **Publish directory:** `dist`
4. Deploy. Confirm the form appears under **Forms** after the first deploy.

### Manual drag-and-drop

```bash
python3 build.py
```

Then drag the `dist/` folder into the Netlify dashboard.

Note: Netlify Forms needs the form markup present in the deployed HTML — it is, since
the form is static. Nothing extra to configure.

### If the Netlify build fails on Python

Netlify's build image ships Python 3 and `python3` is on PATH, so `python3 build.py`
works out of the box. If a future image changes that, you have two fallbacks:

1. Pin the version — add a `PYTHON_VERSION` environment variable (e.g. `3.11`) under
   *Site configuration → Environment variables*, or commit a `.python-version` file.
2. Skip the build entirely — the output is plain static files with no runtime
   dependency. Remove `dist/` from `.gitignore`, commit it, and set the build command
   to empty with the publish directory still `dist`. You then rebuild locally and
   commit `dist/` with each change.

### Replacing the current site

The existing site is at `pickleduels.netlify.app`. To replace it, point that Netlify
site at this repository and update the build settings as above.
