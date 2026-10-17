# Legal audit notes — internal

Not published. These are findings from auditing the site, the Pickle Duels app
listings, and VenueOS while drafting `/privacy/` and `/terms/`.

## 1. The App Store "Terms of Use" link points at an unrelated company

The Pickle Duels App Store listing links Terms of Use to:

```
https://clmsstudio.com/apps/paddle-wars/terms
```

That document is titled "Paddle Wars Terms of Use", is a binding agreement with
**CLMS Studio LLC**, covers a different app, directs users to `support@clmsstudio.com`,
and describes a paid subscription ("Paddle Wars Pro", $7.99/month or $59.99/year with a
7-day trial) that Pickle Duels does not offer — the listing shows Pickle Duels as Free
with no in-app purchases.

CLMS Studio is an unrelated company. Anyone tapping Terms of Use on the Pickle Duels
listing is therefore shown a contract with a third party.

**Action:** once `/terms/` is approved by counsel, repoint the Terms of Use URL in
App Store Connect to it. Check the Google Play listing for the same problem.

**Note on drafting:** the first draft of `/terms/` reused phrasing from that document —
measured at 19 shared 8-word sequences, concentrated in the prohibited-use list and the
termination clause. Those passages were rewritten. Current overlap is 1 shared 8-word
sequence ("non-exclusive, non-transferable, revocable licence to use"), which is
standard licensing terminology, and zero at 10 words or longer.

## 2. Three company names are attached to Pickle Duels

| Name | Where it appears |
|---|---|
| RallyXP | This website — "Pickle Duels is powered by RallyXP" |
| Capsule Kaiba, LLC | App Store seller and copyright line (© 2024) |
| CLMS Studio LLC | Via the mislinked Terms of Use above — unrelated |

Both legal pages need the single operating entity named. Unresolved.

## 3. The existing privacy policy covers the app only

Apple links to `pickleball-web-server.onrender.com/privacy-policy` (effective
Aug 8, 2025). It is served inside an `<embed>`, so it looks blank to most tools.
It covers the app and says nothing about this website or VenueOS.

`/terms/` has no predecessor — the same server's `/terms` route is an empty SPA shell.
That server returns HTTP 200 for any path, so a 200 there proves nothing.

## 4. Apple's privacy labels may not match the policy

Apple's App Privacy section declares only **Contact Info (name, email)** under
"Data Not Linked to You". But the policy says that data creates and manages your
account, which is linked to identity by definition. Reconcile the declaration.

Apple also rates the app **4+**, while the privacy policy sets a 13+ floor. Confirm how
under-13 users are handled; COPPA may apply.

## 5. What the website itself collects

Verified at runtime on the live site:

- No cookies, no `localStorage`, no `sessionStorage`
- No analytics, trackers, or third-party scripts; fonts are self-hosted
- Every request is same-origin, apart from Netlify's own injected HUD script
- The demo form is the only collection point: name, email, organization, role,
  events per year, message — processed by Netlify Forms

## 6. VenueOS

Authentication is handled by **Clerk** (identified from `__client_uat` cookies and the
`__clerk_environment` storage key). Sign-in options are email/password, **Google**, and
**Facebook**. All three are sub-processors and are disclosed in `/privacy/`.

## 7. Google Play data safety not yet checked

The Play listing is JavaScript-rendered and could not be retrieved as text. Its
Data safety declarations are a separate submission from Apple's and often differ.
Worth checking at `play.google.com/store/apps/datasafety?id=com.capsulekaiba.pickleduels`.
