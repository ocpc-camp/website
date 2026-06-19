# AGENTS.md

Guidance for AI coding agents (e.g. Claude Code) working in this repository. `CLAUDE.md` in this repo is a symlink to this file.

## What this is

The Jekyll source for https://ocpc.camp/ — the website for the Osijek Competitive Programming Camp (OCPC). It is a static, data-driven Bootstrap 5 site. There is no application code, no test suite, and no lint step.

## Serving locally

```sh
cd docs
jekyll serve   # http://127.0.0.1:4000
```

The Jekyll site root is `docs/` (GitHub Pages serves from this subdirectory; `docs/CNAME` maps it to ocpc.camp). There is no Gemfile — Jekyll/Bootstrap are expected to be available globally / via GitHub Pages' build. `docs/_config.yml` is intentionally minimal; its `include: [_includes]` is vestigial — there is no `_includes` directory, and pages compose layout via `include_relative` instead (see below).

## Architecture

### One self-contained folder per camp edition

Each edition lives in its own directory under `docs/`, named `<year><season>` where season is `w` (winter) or `s` (summer): e.g. `docs/2026w/`, `docs/2025s/`. A directory holds the full set of pages for that edition (`index.html`, `details.html`, `schedule.html`, `contest-info.html`, `sponsors.html`, `contact.html`, `legal.html`) plus two layout fragments, `before.html` and `after.html`.

New editions are created by **copying a previous edition's folder** and editing it — there is no shared template, so HTML/structure drift between editions is expected and fine. Only change the current edition unless explicitly asked otherwise.

### "Current edition" pointer + redirect stubs

`docs/_data/current.yml` contains a single key, `current_season` (e.g. `2026w`). The top-level `docs/*.html` files (`index.html`, `schedule.html`, `contest-info.html`, …) are **thin redirect stubs** that meta-refresh to `{{ site.data.current.current_season }}/...`. To make a new edition the live one, update `current.yml` — do not edit the redirect stubs.

### Layout via `include_relative`, not `_layouts`/`_includes`

There are no Jekyll layouts. Each content page starts with YAML front matter (just a `title:`) and wraps its body with:

```liquid
{% include_relative before.html %}
... page content ...
{% include_relative after.html %}
```

- `before.html` = `<head>`, CSS/JS links, navbar, Discord-init script.
- `after.html` = footer, which renders the Sponsors and Partners logo grids.

These are per-edition copies, so edits to the header/footer must be made in the relevant edition's `before.html`/`after.html`.

### Data-driven content (`docs/_data/<season>/`)

Per-edition content lives in YAML under `docs/_data/<season>/`: `schedule.yml`, `sponsors.yml`, `team.yml`, `authors.yml`, `reviews.yml`. Pages iterate over these. Because the data keys begin with a digit, they must be accessed with bracket syntax: `site.data['2026w'].schedule`, **not** `site.data.2026w` (note that `after.html` currently uses the dotted form `site.data.2026w.sponsors` — when forking a new edition, update that hardcoded season reference in the new `after.html`).

So: editing schedule/sponsors/team/etc. means editing the YAML, not the HTML.

### Archive

- `docs/archive.html` (top-level) iterates `docs/_data/archives.yml` to list all past editions with links to their archived site, Codeforces announcement/wrap blog posts, rating standings, and per-day contest gym links. Add a block here when an edition concludes.
- An archived edition's site is preserved in place; the convention is to add an "archived website" banner to that edition's `before.html` pointing back to `/`.

### Other pieces

- **Discord widget**: `docs/js/discord.js` exposes `initDiscordInvite('<invite-code>')` (called in `before.html`) and renders into `<div data-discord-invite></div>`.
- **CSS**: vendored Bootstrap 5 in `docs/css/`; site overrides in `docs/css/site.css`, linked with a cache-busting query (`site.css?v=N`) — bump `N` in `before.html` when you change `site.css`.
- `docs/_site/` and `.jekyll-cache/` are Jekyll build output (gitignored / not edited by hand).

## Publishing a new edition (summary)

1. Copy the most recent `docs/<season>/` folder to the new season code; update its pages, `before.html`/`after.html` (including the hardcoded `site.data.<season>.sponsors` references).
2. Create `docs/_data/<new-season>/` with `schedule.yml`, `sponsors.yml`, `team.yml`, `authors.yml`, `reviews.yml`.
3. Point `docs/_data/current.yml` `current_season` at the new code.
4. Add the previous edition to `docs/_data/archives.yml` and add the "archived" banner to its `before.html`.
