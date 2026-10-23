# Image credits

Every photograph on this site is listed here with its source, photographer, and
license. Files live in `public/images/` and are copied to `dist/images/` at build time.

## In use

All four are from [Unsplash](https://unsplash.com) under the
[Unsplash License](https://unsplash.com/license) — free for commercial use, no
attribution required. Credited here anyway, as Unsplash's API guidelines ask.

| File | Used for | Photographer | Source |
|---|---|---|---|
| `hero-play.jpg` | Homepage hero (`/`) | [eedgar ivann](https://unsplash.com/@eedgarivann) | [7lsgTpUfnes](https://unsplash.com/photos/two-people-are-playing-pickleball-on-the-court-7lsgTpUfnes) |
| `players-rally.webp` | Home path card — For players (`/`) | Supplied by RallyXP | [PLACEHOLDER: source and licence for the paddle-tap photo] |
| `king-of-the-court.jpg` | King of the Court spotlight (`/play/`) | [Lesli Whitecotton](https://unsplash.com/@lnicolern) | [UHZ_w1bOIvY](https://unsplash.com/photos/a-group-of-people-play-tennis-UHZ_w1bOIvY) |
| `paddles-gear.jpg` | Prizes spotlight (`/play/`) | [Alex Saks](https://unsplash.com/@alexsaks) | [KO6QJcddk28](https://unsplash.com/photos/two-paddles-and-three-balls-on-a-tennis-court-KO6QJcddk28) |
| `hero-play-page.jpg` | Play page hero (`/play/`) | [Venti Views](https://unsplash.com/@ventiviews) | [q97_OyjWS1U](https://unsplash.com/photos/pickleball-player-holds-a-ball-with-the-net-in-view-q97_OyjWS1U) |
| `hero-organize.jpg` | Organize page hero (`/organize/`) | [Frankie Lopez](https://unsplash.com/@frankielopez) | [dA68yigQgSQ](https://unsplash.com/photos/black-and-white-tennis-net-dA68yigQgSQ) |
| `hero-company.jpg` | Company page hero (`/company/`) | [Frankie Lopez](https://unsplash.com/@frankielopez) | [lXy07zu3NN4](https://unsplash.com/photos/white-net-on-green-field-lXy07zu3NN4) |

### Photo descriptions

- **`hero-play.jpg`** — Two people are playing pickleball on the court
- **`players-rally.webp`** — Two players touching paddles over the net at sunset. 1024x572, kept as WebP (51 KB; re-encoding to JPEG cost 87 KB for no gain).
- **`king-of-the-court.jpg`** — Pickle ball game
- **`paddles-gear.jpg`** — Pickleball session details — paddle, ball, and court setup. Gear I use → linktr.ee/alexsaks.inspiration

## Brand assets

| File | Used for | Source |
|---|---|---|
| `logo-pickle-duels.png` | Header logo, all pages | Own artwork — © RallyXP |
| `founder-huyen.png` | Huyen Hoang's founder card (`/company/`) | Own illustration — © RallyXP |
| `founder-jackson.png` | Jackson Wang's founder card (`/company/`) | Own illustration — © RallyXP |
| `venueos-create-tournament.png` | Capability 1, Create tournaments (`/organize/`) | Own product mockup — © RallyXP |
| `venueos-registrations.png` | Capability 2, Manage registrations (`/organize/`) | Own product mockup — © RallyXP |
| `venueos-check-in.png` | Capability 3, Check-in on event day (`/organize/`) | Own product mockup — © RallyXP |
| `organizers-court.webp` | Home path card — For organizers & clubs (`/`) | [PLACEHOLDER: source and licence for the isometric court illustration] |
| `venueos-pool-play.png` | Capability 4, Track pool play (`/organize/`) | Own product mockup — © RallyXP |
| `venueos-brackets.png` | Capability 5, Track bracket play (`/organize/`) | Own product mockup — © RallyXP |
| `venueos-invite-past-players.png` | Capability 6, Re-engage past participants (`/organize/`) | Own product mockup — © RallyXP |
| `badge-app-store.png` | App Store button (home, `/play/`) | Official Apple badge artwork |
| `badge-google-play.png` | Google Play button (home, `/play/`) | Official Google badge artwork |

918×262 PNG with transparency (24 KB), rendered at 36px tall in the header
(30px below 26rem). The header bar stays 68px regardless.

**A reversed version would help.** The wordmark text in this file is black, so it
cannot sit on the dark footer — the footer still uses the type-set wordmark in white.
Supply a white-text variant (`logo-pickle-duels-light.png`) and the footer can use the
real logo too.

`founder-jackson.png` is an illustrated avatar, resized from a 1254×1254 WebP to
360×360 PNG. PNG rather than JPEG because the artwork is line work on flat colour,
where JPEG puts ringing around the black outlines; `sips` on this machine cannot write
WebP. 360px covers the 320 device pixels a 2x display needs at the 160px render size.

Both founder avatars are now illustrations, but only Huyen's is transparent.
Jackson's has a teal background baked into the file, so the two circles do not match.
**A transparent version of Jackson's avatar would fix it with no code change** — the
CSS background is already in place.

`founder-huyen.png` is a transparent illustrated avatar, resized from a 1254×1254 WebP
to 360×360 PNG with its alpha channel intact. The circle behind it is painted in CSS
with `var(--volt)` on `.founder__media`, not baked into the file, so the colour stays a
design token and any future transparent avatar picks it up automatically.

An SVG would also be worth having: it would stay crisp at any size and on any
display, and would likely be smaller than 24 KB.

## Still needed

These slots render a clearly labeled placeholder until a real file is added.
See the README section *Replacing a placeholder with a real photo*.

| Slot | Page(s) | Source |
|---|---|---|
| replace these with the official App Store and Google Play badge artwork | `play/` | Your own brand asset |

## Licensing rules for this site

This is a commercial site. Acceptable sources:

- **Unsplash License** or **Pexels License** — commercial use, no attribution required
- **CC0 / Public Domain**
- **CC BY**, with attribution recorded in the table above

Do **not** use anything marked **NC** (non-commercial) or **ND** (no derivatives),
and never hotlink — download the file into `public/images/`.

A caution specific to this sport: searching "pickleball" on any stock library returns
a large amount of **tennis** mislabeled as pickleball. Check the paddle (solid, no
strings), the ball (perforated), and the net height before using a photo.

## App store badges

The official Apple and Google badge artwork is now in place (240×80 PNG, rendered
at 48px tall). Both stores forbid altering their badges, so these are scaled only —
never recoloured, cropped, re-typeset, or given effects.

They are the black variants, which read correctly on this site because every
placement sits on a dark background (the home hero, the Play hero, and the Play
CTA band). **If a badge is ever placed on a light background, swap in the white
variant** rather than restyling this one.

- Apple: <https://developer.apple.com/app-store/marketing/guidelines/>
- Google Play: <https://play.google.com/intl/en_us/badges/>

Both link to the live store listings:

- App Store: <https://apps.apple.com/us/app/pickle-duels/id6745139136>
- Google Play: <https://play.google.com/store/apps/details?id=com.capsulekaiba.pickleduels>
