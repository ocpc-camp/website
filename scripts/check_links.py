#!/usr/bin/env python3
"""Check local HTML and CSS URL targets in the assembled deployment directory."""

import argparse
from pathlib import Path
import re
from urllib.parse import unquote, urljoin, urlsplit

from bs4 import BeautifulSoup
import tinycss2

ORIGIN = "https://ocpc.camp"


def css_links(text):
    def walk(tokens):
        for i, token in enumerate(tokens):
            if token.type == "url":
                yield token.value
            elif token.type == "function" and token.lower_name == "url":
                args = [t for t in token.arguments if t.type not in ("whitespace", "comment")]
                if len(args) == 1 and args[0].type == "string":
                    yield args[0].value
            elif hasattr(token, "content"):
                yield from walk(token.content)
            elif hasattr(token, "arguments"):
                yield from walk(token.arguments)
            if token.type == "at-keyword" and token.lower_value == "import":
                following = next((t for t in tokens[i + 1:] if t.type not in ("whitespace", "comment")), None)
                if following is not None and following.type == "string":
                    yield following.value
    yield from walk(tinycss2.parse_component_value_list(text))


def check_site(root):
    root = root.resolve()
    if not (root / "index.html").is_file():
        raise ValueError(f"Not a built site: {root} (missing index.html)")
    files = sorted(p for p in root.rglob("*") if p.is_file())
    print(f"Inventory: {len(files)} files")
    sources = [p for p in files if p.suffix in (".html", ".css")]
    errors, skipped = [], []
    checked = references = external = 0
    fragments = 0
    anchors = {}

    def check(value, base, source, html_fragment=True):
        nonlocal references, external, fragments
        value = value.strip()
        if not value or (not html_fragment and value.startswith("#")):
            return
        url = urlsplit(urljoin(base, value))
        if url.scheme not in ("http", "https") or url.netloc != "ocpc.camp":
            external += 1
            return
        references += 1
        path = unquote(url.path)
        target = (root / path.lstrip("/")).resolve()
        if not target.is_relative_to(root):
            errors.append(f"{source}: {value!r} escapes site root")
        elif not target.is_file() and not (target / "index.html").is_file():
            errors.append(f"{source}: {value!r} -> {path} (missing)")
        elif html_fragment and url.fragment:
            if target.is_dir():
                target = target / "index.html"
            # Non-HTML fragments (PDF pages, SVG views, media times) have
            # different semantics. Text-fragment directives are browser searches.
            fragment = unquote(url.fragment.split(":~:", 1)[0])
            if target.suffix != ".html" or not fragment or fragment.lower() == "top":
                return
            fragments += 1
            if target not in anchors:
                document = BeautifulSoup(target.read_text(), "html.parser")
                anchors[target] = {el["id"] for el in document.find_all(id=True)}
                anchors[target].update(el["name"] for el in document.find_all("a", attrs={"name": True}))
            if fragment not in anchors[target]:
                errors.append(f"{source}: {value!r} -> {path} (missing fragment #{fragment})")

    for path in sources:
        name = path.relative_to(root).as_posix()
        # These are copied Jekyll include sources, not rendered documents.
        if path.suffix == ".html" and path.name in ("before.html", "after.html"):
            skipped.append(name)
            continue
        checked += 1
        base = ORIGIN + "/" + name
        text = path.read_text()
        if path.suffix == ".css":
            for url in css_links(text):
                check(url, base, name, html_fragment=False)
            continue
        soup = BeautifulSoup(text, "html.parser")
        base_element = soup.find("base", href=True)
        if base_element:
            base = urljoin(base, base_element["href"])
        for element in soup.find_all(True):
            for attr in ("href", "src", "poster", "data", "xlink:href"):
                if element.has_attr(attr):
                    check(element[attr], base, name)
            if element.has_attr("srcset"):
                errors.append(f"{name}: srcset needs explicit checker support")
            if element.has_attr("style"):
                for url in css_links(element["style"]):
                    check(url, base, name, html_fragment=False)
            if element.name == "style":
                for url in css_links(element.get_text()):
                    check(url, base, name, html_fragment=False)
            if element.name == "meta" and element.get("http-equiv", "").lower() == "refresh":
                match = re.search(r";\s*url\s*=\s*(.*)", element.get("content", ""), re.I)
                if match:
                    check(match[1].strip().strip("\"'"), base, name)
    print(f"Checked {checked}/{len(sources)} HTML/CSS files; {references} local references; {external} external/non-HTTP references not fetched")
    print(f"Checked {fragments} local HTML section fragments")
    print(f"Not checked: {len(skipped)} Jekyll include fragments: {', '.join(skipped) or 'none'}")
    for error in errors:
        print(error)
    print(f"Broken targets or unsupported constructs: {len(errors)}")
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path)
    args = parser.parse_args()
    raise SystemExit(bool(check_site(args.site)))
