# OCPC website

This repo contains sources for https://ocpc.camp/.

Install the pinned Ruby and Python build dependencies:

```sh
bundle install
python3 -m venv .venv
.venv/bin/pip install -r requirements-build.txt
```

Build the complete site (including tagged archives) into a **new** directory:

```sh
.venv/bin/python scripts/build_site.py --output _site/preview
python3 -m http.server 4000 --directory _site/preview
```

Open http://127.0.0.1:4000. Use another output directory for each build; the builder refuses to overwrite existing files. For live-page editing only, `bundle exec jekyll serve --source docs` is also available, but does not assemble tagged archives.

## Archiving

1. Commit the finished season's pages and data. Create a tag at that reviewed commit, for example `git tag archive/2026s <commit>`, then publish it with `git push origin refs/tags/archive/2026s`. Do not move published archive tags.
2. Prepare the next season's pages/data and update `docs/_data/current.yml`. Add the completed season's contest links and website path to `docs/_data/archives.yml` as usual.
3. Add the completed season to `archive-builds.yml` with its tag and the full commit from `git rev-parse 'archive/2026s^{commit}'`. The builder requires the tag to match that commit and rejects the current season.
4. Build and preview the combined site. Commit and push the new season and manifest together. There is no manual archive banner or asset-copy step.

Existing season URLs stay unchanged, including venue paths such as `/2026s/hk/`. Each tagged season is built from its own Git revision using the locked build dependencies. Its CSS, JavaScript, images and favicon are copied under `/<season>/_assets/`; HTML and CSS asset references are adjusted automatically. Links to `/`, `/archive.html` and other seasons continue to use the live site. Canonical URLs retain their existing public paths. The generated `/archive-builds.json` records the deployed archive revisions.

All seven past editions, Winter 2023 through Winter 2026, are registered in `archive-builds.yml`; their redundant HTML and season-data folders have been removed from `main`. Their tags capture the preserved archives in November 2026, rather than claiming original closing-day snapshots. For future seasons, remove source folders only after checking dependencies and comparing the complete built URL inventory before and after removal. Keep the active season, shared assets and `docs/_data/archives.yml` in place. The builder also supports legacy seasons without manifest entries, which continue to build from their folders.

For a later archive correction, create a separate worktree from that season's existing tag, edit and commit the correction there, and publish a **new** tag such as `archive/2023w-2`. Update the manifest's tag and commit together on `main`. Keep the old tag; rolling back the manifest change selects the previous snapshot. This does not require restoring archive source folders to `main`.

The archive freezes repository content, not third-party websites, registration forms or live Discord responses. Shared asset roots are defined in `scripts/build_site.py`; add new roots there if the website gains another asset directory. Dynamically constructed JavaScript URLs are not rewritten. The builder rejects `<base>` and `srcset` in tagged pages until explicit handling is added, rather than silently publishing incorrect links.

## Deployment

Production uses GitHub Actions (activated 4 November 2026), with the custom domain `ocpc.camp`.

`.github/workflows/pages.yml` tests and builds pull requests without deploying them. Pushes to `main` and manual runs on `main` deploy the combined artifact. Tag pushes alone do not publish a site: the manifest change controls publication. Checkout must fetch full history and tags.

**One-time activation:** after reviewing and merging the workflow, change Settings → Pages → Build and deployment → Source to **GitHub Actions**, then run the workflow on `main`. The previous setting is **Deploy from a branch**, `main`, `/docs`. Until that switch, the branch-based build does not assemble tagged archives. Keep the legacy season folders during activation so the previous publishing method remains available for rollback. Preserve the custom domain `ocpc.camp`.

After archive source folders are removed, keep Pages on GitHub Actions. Changing back to branch publishing alone would omit those editions. To undo a source-removal migration, restore the removed folders from the pre-removal commit and commit that restoration; use the reviewed pre-migration manifest too if reverting the tag migration itself. Restore all required source folders before considering branch publishing again.

## Checks

```sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/build_site.py --output _site/check
```

The integration test builds a real temporary Git repository before and after changing the live assets and removing an archived season's source. It checks portal and venue paths, frozen assets, live navigation, automatic banners, and missing/moved-tag failures.

