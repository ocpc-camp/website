#!/usr/bin/env python3
"""Build the live site and pinned season archives into a new output directory."""

import argparse
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import tempfile
from urllib.parse import unquote, urljoin, urlsplit, urlunsplit

from bs4 import BeautifulSoup
import tinycss2
from tinycss2.serializer import serialize_string_value
import yaml

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ("css", "js", "images", "favicon.ico")
ORIGIN = "https://ocpc.camp"


def run(*args, cwd=ROOT):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()


def read_yaml(path):
    return yaml.safe_load(path.read_text())


def archive_revisions(repo):
    entries = read_yaml(repo / "archive-builds.yml")
    if not isinstance(entries, dict):
        raise ValueError("archive-builds.yml must be a mapping")
    current = read_yaml(repo / "docs/_data/current.yml")["current_season"]
    listed = {row.get("archive_link", "").strip("/")
              for row in read_yaml(repo / "docs/_data/archives.yml")}
    revisions = {}
    for season, entry in entries.items():
        if not isinstance(season, str) or not re.fullmatch(r"\d{4}[sw]", season):
            raise ValueError(f"Invalid season: {season!r}")
        if season == current:
            raise ValueError(f"Cannot archive the current season: {season}")
        if season not in listed:
            raise ValueError(f"Add {season} to docs/_data/archives.yml first")
        if not isinstance(entry, dict) or set(entry) != {"tag", "commit"}:
            raise ValueError(f"{season}: expected tag and commit")
        tag, commit = entry["tag"], entry["commit"]
        if not isinstance(tag, str) or not re.fullmatch(
                rf"archive/{season}(?:-\d+)?", tag):
            raise ValueError(f"Invalid archive tag: {tag!r}")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise ValueError(f"{season}: expected a full commit SHA")
        actual = run("git", "rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}", cwd=repo)
        if actual != commit:
            raise ValueError(f"{tag} moved: expected {commit}, found {actual}")
        revisions[season] = entry
    return revisions


def jekyll(source, destination):
    env = dict(os.environ, JEKYLL_ENV="production", BUNDLE_GEMFILE=str(ROOT / "Gemfile"))
    subprocess.run(["bundle", "exec", "jekyll", "build", "--safe",
                    "--disable-disk-cache", "--source", str(source),
                    "--destination", str(destination)], cwd=ROOT, env=env, check=True)


def asset_url(value, page_url, season):
    """Keep page navigation stable; relocate only our shared static assets."""
    if not value or value.startswith("#"):
        return value
    parsed = urlsplit(urljoin(ORIGIN + page_url, value))
    if parsed.scheme not in ("http", "https") or parsed.netloc != "ocpc.camp":
        return value
    if unquote(parsed.path).lstrip("/").split("/")[0] not in ASSETS:
        return value
    return urlunsplit(("", "", f"/{season}/_assets{parsed.path}", parsed.query, parsed.fragment))


def css_urls(text, page_url, season):
    tokens = tinycss2.parse_component_value_list(text)

    def walk(items):
        for token in items:
            if token.type == "url":
                token.value = asset_url(token.value, page_url, season)
                token.representation = 'url("' + serialize_string_value(token.value) + '")'
            elif token.type == "function" and token.lower_name == "url":
                args = [x for x in token.arguments if x.type not in ("whitespace", "comment")]
                if len(args) == 1 and args[0].type == "string":
                    args[0].value = asset_url(args[0].value, page_url, season)
                    args[0].representation = '"' + serialize_string_value(args[0].value) + '"'
            elif hasattr(token, "content"):
                walk(token.content)
            elif hasattr(token, "arguments"):
                walk(token.arguments)
        # @import permits a bare string instead of url(...).
        for i, token in enumerate(items):
            if token.type == "at-keyword" and token.lower_value == "import":
                following = next((x for x in items[i + 1:] if x.type not in ("whitespace", "comment")), None)
                if following is not None and following.type == "string":
                    following.value = asset_url(following.value, page_url, season)
                    following.representation = '"' + serialize_string_value(following.value) + '"'

    walk(tokens)
    return tinycss2.serialize(tokens)


def archive_html(text, page_url, season):
    soup = BeautifulSoup(text, "html.parser")
    if soup.find("base"):
        raise ValueError(f"{page_url}: base elements need explicit archive support")
    for element in soup.find_all(True):
        for attr in ("href", "src", "poster", "data", "xlink:href"):
            if element.has_attr(attr):
                element[attr] = asset_url(element[attr], page_url, season)
        if element.has_attr("srcset"):
            # Do not silently corrupt data URLs or more complex candidate syntax.
            raise ValueError(f"{page_url}: srcset needs explicit archive support")
        if element.has_attr("style"):
            element["style"] = css_urls(element["style"], page_url, season)
        if element.name == "style" and element.string is not None:
            element.string.replace_with(css_urls(str(element.string), page_url, season))
    if soup.body is not None:
        # Legacy editions may already carry the old banner.
        if not soup.find(string=lambda s: s and "You are viewing an archived website" in s):
            banner = soup.new_tag("aside", attrs={"class": "alert alert-warning text-center", "role": "note"})
            banner.append(f"Archived website for {season}. ")
            link = soup.new_tag("a", href="/")
            link.string = "Visit the current camp website."
            banner.append(link)
            soup.body.insert(0, banner)
    return str(soup)


def assemble_archive(built, destination, season):
    source = built / season
    if not (source / "index.html").is_file():
        raise ValueError(f"Tagged build has no {season}/index.html")
    if (source / "_assets").exists():
        raise ValueError(f"{season}/_assets is reserved for the archive builder")
    shutil.copytree(source, destination)
    for asset in ASSETS:
        path = built / asset
        if path.is_dir():
            shutil.copytree(path, destination / "_assets" / asset)
        elif path.is_file():
            (destination / "_assets").mkdir(exist_ok=True)
            shutil.copy2(path, destination / "_assets" / asset)
    for path in destination.rglob("*.html"):
        page_url = f"/{season}/{path.relative_to(destination).as_posix()}"
        path.write_text(archive_html(path.read_text(), page_url, season))
    for path in destination.rglob("*.css"):
        relative = path.relative_to(destination).as_posix()
        original_url = "/" + relative.removeprefix("_assets/") if relative.startswith("_assets/") else f"/{season}/{relative}"
        path.write_text(css_urls(path.read_text(), original_url, season))


def build(repo, output):
    repo, output = repo.resolve(), output.resolve()
    if output.exists():
        raise ValueError(f"Output already exists; choose a new directory: {output}")
    revisions = archive_revisions(repo)
    # Temporary staging prevents a failed archive build from publishing a partial site.
    with tempfile.TemporaryDirectory(prefix="ocpc-build-") as tmp:
        stage = Path(tmp)
        live = stage / "live"
        jekyll(repo / "docs", live)
        for season, entry in revisions.items():
            checkout = stage / f"source-{season}"
            checkout.mkdir()
            archive = subprocess.check_output(["git", "archive", entry["commit"], "docs"], cwd=repo)
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                if any(item.issym() or item.islnk() for item in tar.getmembers()):
                    raise ValueError("Tagged docs must not contain symlinks or hardlinks")
                tar.extractall(checkout, filter="data")
            built = stage / f"built-{season}"
            jekyll(checkout / "docs", built)
            replacement = stage / f"archive-{season}"
            assemble_archive(built, replacement, season)
            if (live / season).exists():
                shutil.rmtree(live / season)  # Generated staging output only.
            shutil.move(replacement, live / season)
        (live / ".nojekyll").touch()
        (live / "archive-builds.json").write_text(json.dumps(revisions, indent=2) + "\n")
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(live, output)
    print(f"Built {output}; {len(revisions)} pinned archives")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new output directory (never overwritten)")
    args = parser.parse_args()
    build(ROOT, args.output)
