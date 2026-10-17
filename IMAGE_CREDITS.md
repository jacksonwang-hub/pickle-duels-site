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
| `players-rally.jpg` | Home path card — For players (`/`) | [Joan Azeka](https://unsplash.com/@jha900) | [bg43g7xTu2M](https://unsplash.com/photos/person-showing-pair-of-blue-and-white-running-shoes-bg43g7xTu2M) |
| `king-of-the-court.jpg` | King of the Court spotlight (`/play/`) | [Lesli Whitecotton](https://unsplash.com/@lnicolern) | [UHZ_w1bOIvY](https://unsplash.com/photos/a-group-of-people-play-tennis-UHZ_w1bOIvY) |
| `paddles-gear.jpg` | Prizes spotlight (`/play/`) | [Alex Saks](https://unsplash.com/@alexsaks) | [KO6QJcddk28](https://unsplash.com/photos/two-paddles-and-three-balls-on-a-tennis-court-KO6QJcddk28) |
| `hero-play-page.jpg` | Play page hero (`/play/`) | [Venti Views](https://unsplash.com/@ventiviews) | [q97_OyjWS1U](https://unsplash.com/photos/pickleball-player-holds-a-ball-with-the-net-in-view-q97_OyjWS1U) |
| `hero-organize.jpg` | Organize page hero (`/organize/`) | [Frankie Lopez](https://unsplash.com/@frankielopez) | [dA68yigQgSQ](https://unsplash.com/photos/black-and-white-tennis-net-dA68yigQgSQ) |
| `hero-company.jpg` | Company page hero (`/company/`) | [Frankie Lopez](https://unsplash.com/@frankielopez) | [lXy07zu3NN4](https://unsplash.com/photos/white-net-on-green-field-lXy07zu3NN4) |

### Photo descriptions

- **`hero-play.jpg`** — Two people are playing pickleball on the court
- **`players-rally.jpg`** — Pickleball paddles come in some wild colors!
- **`king-of-the-court.jpg`** — Pickle ball game
- **`paddles-gear.jpg`** — Pickleball session details — paddle, ball, and court setup. Gear I use → linktr.ee/alexsaks.inspiration

## Brand assets

| File | Used for | Source |
|---|---|---|
| `logo-pickle-duels.png` | Header logo, all pages | Own artwork — © RallyXP |
| `founder-huyen.jpg` | Huyen Hoang's founder card (`/company/`) | Own photograph — © RallyXP |
| `founder-jackson.jpg` | Jackson Wang's founder card (`/company/`) | Own photograph — © RallyXP |
| `badge-app-store.png` | App Store button (home, `/play/`) | Official Apple badge artwork |
| `badge-google-play.png` | Google Play button (home, `/play/`) | Official Google badge artwork |

918×262 PNG with transparency (24 KB), rendered at 36px tall in the header
(30px below 26rem). The header bar stays 68px regardless.

**A reversed version would help.** The wordmark text in this file is black, so it
cannot sit on the dark footer — the footer still uses the type-set wordmark in white.
Supply a white-text variant (`logo-pickle-duels-light.png`) and the footer can use the
real logo too.

`founder-jackson.jpg` was cropped from a 312×673 original to 230×230 around the
face using `sips --cropOffset`, at native resolution with no upscaling. That is the
largest square the source allows while keeping the whole head in frame. It is sharp
at the 160px display size on a standard display, but slightly soft on a 2x retina
screen, which wants 320px. **A higher-resolution original would fix that** — anything
400px square or larger is plenty.

`founder-huyen.jpg` is an 800×800 source shown as a circular avatar
(160px desktop, 120px mobile) cropped by `object-fit: cover`. Converted from a
396 KB PNG to a 64 KB JPEG with `sips`. A square source is ideal for this slot.

An SVG would also be worth having: it would stay crisp at any size and on any
display, and would likely be smaller than 24 KB.

## Still needed

These slots render a clearly labeled placeholder until a real file is added.
See the README section *Replacing a placeholder with a real photo*.

| Slot | Page(s) | Source |
|---|---|---|
| VenueOS screenshot — bracket view and final results | `organize/` | Your own VenueOS capture |
| VenueOS screenshot — event-day check-in screen | `organize/` | Your own VenueOS capture |
| VenueOS screenshot — inviting past participants by email | `organize/` | Your own VenueOS capture |
| VenueOS screenshot — pool play standings | `organize/` | Your own VenueOS capture |
| VenueOS screenshot — registration list | `organize/` | Your own VenueOS capture |
| VenueOS screenshot — tournament creation screen | `organize/` | Your own VenueOS capture |
| drop six team pickleball photos into this gallery | `company/` | Your own photograph |
| photo of a tournament desk or organizer with a tablet | `/` | Stock or your own |
| replace these with the official App Store and Google Play badge artwork | `play/` | Your own brand asset |
| team photo 1 | `company/` | Your own photograph |
| team photo 2 | `company/` | Your own photograph |
| team photo 3 | `company/` | Your own photograph |
| team photo 4 | `company/` | Your own photograph |
| team photo 5 | `company/` | Your own photograph |
| team photo 6 | `company/` | Your own photograph |

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

Both currently link to `[PLACEHOLDER: iOS App Store URL]` and
`[PLACEHOLDER: Google Play Store URL]`.
