# AGENTS.md

Guidance for AI coding agents (e.g. Claude Code) working in this repository. `CLAUDE.md` in this repo is a symlink to this file.

## What this is

The Jekyll source for https://ocpc.camp/ — the website for the Osijek Competitive Programming Camp (OCPC). It is a static, data-driven Bootstrap 5 site. Archive build tooling lives in `scripts/build_site.py`, with integration tests in `tests/`.

## Serving locally

```sh
bundle install
python3 -m venv .venv
.venv/bin/pip install -r requirements-build.txt
.venv/bin/python scripts/build_site.py --output _site/preview
python3 -m http.server 4000 --directory _site/preview
```

The Jekyll source root is `docs/`. `Gemfile.lock` pins the Ruby build dependencies; `requirements-build.txt` pins the Python archive tooling. `.github/workflows/pages.yml` builds the live site plus archives and deploys the combined output after Pages is switched to GitHub Actions (see README for activation and rollback). `docs/CNAME` records ocpc.camp; preserve the custom domain in Pages settings. Use a new output directory for each build. `docs/_config.yml` is intentionally minimal; its `include: [_includes]` is vestigial — there is no `_includes` directory, and pages compose layout via `include_relative` instead (see below).

## Architecture

### One self-contained folder per camp edition

Each edition is served at its own `<year><season>/` path, where season is `w` (winter) or `s` (summer). The working tree retains the active season under `docs/2026s/`; the seven older editions are reconstructed from pinned Git tags. Their HTML and season-data folders were removed from `main` after migration checks. A source directory holds the full set of pages for that edition (`index.html`, `details.html`, `schedule.html`, `contest-info.html`, `sponsors.html`, `contact.html`, `legal.html`) plus two layout fragments, `before.html` and `after.html`.

New editions are created by **copying the current edition's folder** and editing it — there is no shared template, so HTML/structure drift between editions is expected and fine. For an archived edition's sources, use a separate worktree at its pinned tag; do not recreate redundant folders on `main`. Only change the current edition unless explicitly asked otherwise.

A season with **multiple simultaneous venues** nests one folder per venue under the season code: e.g. `docs/2026s/hk/` and `docs/2026s/iasi/`, each a full self-contained edition (its own page set plus `before.html`/`after.html`). Their data lives under `docs/_data/2026s/<venue>/` and is read with nested bracket access — `site.data['2026s'].hk.*` / `site.data['2026s'].iasi.*`.

### Root redirect → current-season portal

`docs/index.html` is a **thin redirect** to the current season: `docs/_data/current.yml` holds a single pointer, `current_season: 2026s`, and the root page meta-refreshes to `/{{ current_season }}/`. (The other top-level `docs/*.html` files — `schedule.html`, `sponsors.html`, … — are likewise redirect stubs to `/`.)

The **portal itself lives in the season folder** (`docs/2026s/index.html`) — a per-season artifact like any edition. Its content data is season-scoped, while CSS/JS/images are shared in the working tree. Use the tagged archive build below to freeze both content and shared assets. The portal renders the season's venue cards from `docs/_data/2026s/sites.yml`, and also carries the **shared/general content** — "What is this?", participant reviews (`docs/_data/2026s/reviews.yml`) and "Who can participate?" — so the lean venue sub-sites don't each duplicate it (they link back with a "New to OCPC →" link).

> History: originally a single `current_season` pointer with `index.html` redirecting to `{{ current_season }}/...`. Summer 2026 added two simultaneous venues, so the "current edition" became a two-card portal at `docs/2026s/` — but the root-redirect + per-season-folder model is otherwise unchanged.

### Layout via `include_relative`, not `_layouts`/`_includes`

There are no Jekyll layouts. Each content page starts with YAML front matter (just a `title:`) and wraps its body with:

```liquid
{% include_relative before.html %}
... page content ...
{% include_relative after.html %}
```

- `before.html` = `<head>`, CSS/JS links, the navbar, Discord-init script.
- `after.html` = footer (for venue sub-sites this renders the Sponsors and Partners logo grids).

These are per-edition copies, so edits to the header/footer must be made in the relevant edition's `before.html`/`after.html`.

**Uniform navbar.** Every page in the Summer 2026 cluster (the `2026s` portal, the `hk`/`iasi` sub-sites, and the root `archive.html`) shares the same navbar skeleton: `[OCPC logo →/] [ Hong Kong | Iași toggle ] …middle… [Discord blurple-SVG icon] [Archive]`. The toggle (left, by the logo) and the right-anchored (`ms-auto`) Discord+Archive group sit in the **same place on every page**; only the *middle* changes — the venue sub-sites slot in Details / Schedule / Contest info / Sponsors / Contact. On a sub-site the toggle highlights the current camp (`btn-primary active`) and the *other* button preserves the relative path (`{{ page.url | replace: '/2026s/hk/', '/2026s/iasi/' }}`), so e.g. HK→Sponsors toggles straight to Iași→Sponsors; on the portal/archive both toggle buttons just link to the two landing pages.

`archive.html` borrows the current season's chrome (`{% include_relative {{ site.data.current.current_season }}/before.html %}`), so there is no root `before.html`/`after.html`. The portal footer's contact email is **assembled in JavaScript** (so `oleksandr@ocpc.camp` / `mailto:` never appear literally in the HTML) — with one deliberate exception, the season legal page (see below). The portal's own `docs/2026s/after.html` footer additionally shows the header-image credits.

### Photo credits — carry them across every season fork

**Every page that shows a photo carries a credit on that page**: the author, the work's title linked to its source page, a licence link where a licence applies, and a note if the image was changed. We credit public-domain photos too, as a courtesy. Forking a season copies the layout but can drop credit lines, so after creating a new season, grep the new folder for every photo and confirm each page that shows one has its credit.

**Choosing a photo.** Prefer public-domain or CC0 photos. Avoid works under version 3.0 or older Creative Commons licences: unlike 4.0 they have no grace period for fixing a missing credit. Check a photo's upload history as well as its licence tag; a public-domain tag on a crop of someone else's licensed photo is worthless. Prefer the photographer's own upload from a long-standing account, or a Flickr import that passed Commons' licence review.

Current photos:

- `images/hong-kong-harbour.jpg` — *Hong Kong Island from Kowloon – DSC00674* by Daderot, [Commons](https://commons.wikimedia.org/wiki/File:Hong_Kong_Island_from_Kowloon_-_DSC00674.JPG), own work dedicated to the public domain (CC0). Our file is a 5472×1990 crop of the original (SHA-1 `61db9e28c3ac9f3a0233671eeb9a7cdf126b7634`) scaled to 1920×698. Its header frame uses `aspect-ratio:2.75/1` because a flatter strip cuts off the tallest tower. Used by Winter 2027 and by the Summer 2026 archive.
- `images/iasi.jpg` — *Palatul Culturii, Iași* by Andrei Lucian Vaida, CC BY-SA 4.0.
- `images/uaic-informatics.jpg` — by Argenna, CC BY-SA 3.0 or GFDL.
- `images/cityu-building.jpg` — City University of Hong Kong, CC BY-SA 4.0.
- `images/Bucharest_Business_District.jpg` (archived Summer 2025) — *Bucharest Business District* by Madalin Pentelie, [Commons](https://commons.wikimedia.org/wiki/File:Bucharest_Business_District.jpg), CC0 confirmed by Flickr review. Our file is a crop.
- `images/bridge.jpg` — *Bridge in Osijek* by Zdenko Brkanić, [Commons](https://commons.wikimedia.org/wiki/File:OS-Most-na-dravi.jpg), public domain. Our file is a crop. Credited on the Winter 2027 pages and on the six archived seasons that show it.

**Archives carry only the photos they show.** The builder publishes every file in an archive tag's `docs/images/` under `/<season>/_assets/`, whether or not a page uses it, so a photo left in the tree is reachable by direct URL without any credit. When cutting or correcting an archive tag, remove photos that the season's own pages and data do not name.

### Legal pages

**The site does not print the operator's legal name or registered address** (owner's decision, November 2026). They are given in the registration form and on every invoice. Do not add them back without the owner's say-so. **Trade-off to remember:** a card-payment application with any acquirer will check the site for the legal name and address, so offering card payment again means restoring them first.

Keep these when forking a season:

- **`docs/<season>/legal.html`** (portal chrome) is the season **Terms & Refund Policy**: services and pricing, payment terms, and the refund policy (**full refund before camp start, none after**). It calls the company "the Operator" and says its name and address are in the registration form and on invoices. The contact email is **plain text on this page only**; JS-assembly stays everywhere else.
- **Every footer** in the season cluster links to the Terms & Refund Policy.
- **Venue `legal.html`** pages keep the host-university submission/IP terms (the host is "Camp Host") and link to the season terms.
- **Root `docs/index.html` and `docs/legal.html`** still meta-refresh to the current season but contain real fallback content, so crawlers that don't follow meta-refresh never see a blank page.
- Invoices are payable by bank transfer; the site must not promise card payment while it is unavailable.
- The registration form names the operator in its "Payment details" section, past the first page. Keep that in each new season's form.

**This repository is public.** Keep business correspondence, disputes and anything else not meant for publication out of its files and commit messages; the private superproject is the place for that.

**History starts on 14 November 2026.** `main` and each archive tag were recreated then as single commits; earlier history is kept privately. A clone made before that date still holds the old branches and tags: never push from it. Re-clone, and push only `main` and tags created after that date.

### Data-driven content (`docs/_data/<season>/`)

Per-edition content lives in YAML under `docs/_data/<season>/`: `schedule.yml`, `sponsors.yml`, `team.yml`, `authors.yml`, `reviews.yml`. Pages iterate over these. Because the data keys begin with a digit, they must be accessed with bracket syntax: `site.data['2026w'].schedule`, **not** `site.data.2026w` (note that `after.html` currently uses the dotted form `site.data.2026w.sponsors` — when forking a new edition, update that hardcoded season reference in the new `after.html`).

So: editing schedule/sponsors/team/etc. means editing the YAML, not the HTML.

For the multi-venue `2026s` season the data lives under `docs/_data/2026s/`:

- `sites.yml` (a bare list) → `site.data['2026s'].sites` — the portal's venue cards.
- `reviews.yml` → `site.data['2026s'].reviews.reviews` — the portal's participant reviews.
- `hk/` and `iasi/` subdirs → `site.data['2026s'].hk.*` / `.iasi.*` — each venue's `sponsors.yml` + `team.yml` (Iași also `schedule.yml`). The sub-sites were stripped to site-specific content (no reviews/authors of their own); their `after.html` use the nested bracket form and guard the Partners block with `{% if partner_list.size > 0 %}`.

### Archive

- `docs/archive.html` is a standalone page (reachable via the **Archive** button in the navbar) that iterates `docs/_data/archives.yml` to list all past editions with links to their archived site (**Website**), Codeforces announcement/wrap blog posts, rating standings, optional **Mirrors**, and per-day contest gym links. Add a block here when an edition concludes. It uses the current season's `before.html`/`after.html` chrome.
- For a multi-venue season, the archive row points **Website → the season portal** and **Mirrors → each sub-site** (e.g. Summer 2026 → Website = the summer portal snapshot, Mirrors = `2026s/hk`, `2026s/iasi`).
- `archive-builds.yml` opts seasons into builds from `archive/<season>` tags with pinned commit SHAs. The builder freezes shared assets under `/<season>/_assets/` and adds the banner automatically. It rejects missing/moved tags and the active season. Existing public season/venue URLs are retained. Seasons without manifest entries still build from their folders. See README for the complete procedure, limitations and correction tags.

### Other pieces

- **Discord widget**: `docs/js/discord.js` exposes `initDiscordInvite('<invite-code>')` (called in `before.html`) and renders into `<div data-discord-invite></div>`.
- **CSS**: vendored Bootstrap 5 in `docs/css/`; site overrides in `docs/css/site.css`, linked with a cache-busting query (`site.css?v=N`) — bump `N` in `before.html` when you change `site.css`.
- `docs/_site/` and `.jekyll-cache/` are Jekyll build output (gitignored / not edited by hand).

## Publishing a new edition (summary)

1. **Copy the previous season's folder** to the new code (e.g. `docs/2026s/` → `docs/2027w/`): its portal `index.html` + chrome, and for a multi-venue season the per-venue subfolders. Update the navbar toggle and the hardcoded `site.data[...].sponsors` references in `after.html`. Keep venue sub-sites **site-specific** (header, dates/location, team, sponsors, fees, registration) — the general "what is this / reviews / who can participate" stays on the portal.
2. Copy/adjust the data dir `docs/_data/<new-season>/`: `sites.yml` (portal cards), `reviews.yml` (portal reviews), and per-venue `sponsors.yml` / `team.yml` / etc.
3. **Repoint `docs/_data/current.yml`** (`current_season: <new-season>`) so the root `/` redirects to the new portal.
4. Tag the reviewed final revision of the just-finished season and publish the tag. Add the season to `docs/_data/archives.yml` (**Website → its portal**, **Mirrors → its sub-sites**) and pin the tag/commit in `archive-builds.yml`. Build and check the combined site before publication. The archive banner and asset isolation are automatic; old source folders may remain during migration. Do not move published tags. See README for the full workflow.

## Winter 2027 launch

The current season is `2027w`, with Hong Kong and Osijek venue pages. Summer 2026 is frozen by `archive/2026s-4` in `archive-builds.yml`; its source remains in place. Winter schedules share `_includes/schedule-table-2027w.html`, rendering a compact desktop table and stacked mobile cards from each venue’s schedule groups. This is an exception to the older include_relative-only structure described above.
