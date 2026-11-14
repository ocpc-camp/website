"""Exercise the real builder with a tagged repository and later live changes."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from bs4 import BeautifulSoup
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_site import archive_html, archive_revisions, asset_url, build, css_urls


class ArchiveTests(unittest.TestCase):
    def test_asset_urls_and_navigation(self):
        for value in ("/css/site.css?v=4#x", "../../css/site.css?v=4#x",
                      "https://ocpc.camp/css/site.css?v=4#x", "//ocpc.camp/css/site.css?v=4#x"):
            self.assertEqual(asset_url(value, "/2026s/hk/index.html", "2026s"),
                             "/2026s/_assets/css/site.css?v=4#x")
        for value in ("/", "/archive.html", "/2026s/iasi/", "legal.html", "#fees",
                      "mailto:team@example.org", "https://example.org/images/a.png",
                      "data:image/png;base64,abc", "https://ocpc.camp"):
            self.assertEqual(asset_url(value, "/2026s/hk/index.html", "2026s"), value)

    def test_css_and_html_keep_external_content_and_scripts(self):
        css = '@import "/css/extra.css"; a{background:url(../images/é.png)} b{background:url(data:image/png;base64,abc)}'
        rewritten = css_urls(css, "/css/site.css", "2026s")
        self.assertIn('/2026s/_assets/css/extra.css', rewritten)
        self.assertIn('/2026s/_assets/images/é.png', rewritten)
        self.assertIn('data:image/png;base64,abc', rewritten)
        script = 'if (x < 2) { el.innerHTML = "<a href=\"/\">Home</a>"; }'
        html = '<html><body><script>' + script + '</script><img src="/images/a.png"><a href="/">Home</a></body></html>'
        rendered = BeautifulSoup(archive_html(html, "/2026s/index.html", "2026s"), "html.parser")
        self.assertEqual(rendered.script.string, script)
        self.assertEqual(rendered.img["src"], "/2026s/_assets/images/a.png")
        self.assertEqual(rendered.aside.a["href"], "/")
        legacy = '<html><body><b>You are viewing an archived website for a previous edition.</b></body></html>'
        self.assertIsNone(BeautifulSoup(archive_html(legacy, "/2026w/index.html", "2026w"), "html.parser").aside)
        for html in ('<base href="/">', '<img srcset="/images/a.png 2x">'):
            with self.assertRaises(ValueError):
                archive_html(html, "/2026s/index.html", "2026s")

    def test_tagged_build_survives_live_changes_and_missing_source_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()

            def git(*args):
                return subprocess.check_output(["git", *args], cwd=repo, text=True, stderr=subprocess.DEVNULL).strip()

            def write(path, text):
                target = repo / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)

            git("init", "-b", "main")
            git("config", "user.name", "Archive test")
            git("config", "user.email", "test@example.invalid")
            write("docs/_config.yml", "url: https://ocpc.camp\n")
            write("docs/_data/current.yml", "current_season: 2026s\n")
            write("docs/_data/archives.yml", "[]\n")
            write("docs/_data/2026s/content.yml", "name: Original camp\n")
            page = ('---\n---\n<html><body><h1>{{ site.data["2026s"].content.name }}</h1>'
                    '<img src="/images/logo.svg"><link rel="stylesheet" href="/css/site.css?v=1">'
                    '<script src="/js/app.js"></script><a href="/2026s/iasi/">Iași</a>'
                    '<a href="/archive.html">Archive</a></body></html>')
            write("docs/2026s/index.html", page)
            write("docs/2026s/hk/index.html", page)
            write("docs/2026s/iasi/index.html", page)
            write("docs/css/site.css", 'body { background: url("/images/logo.svg"); }')
            write("docs/images/logo.svg", '<svg xmlns="http://www.w3.org/2000/svg"/>')
            write("docs/js/app.js", 'console.log("original");')
            git("add", ".")
            git("commit", "-m", "Final season")
            commit = git("rev-parse", "HEAD")
            git("tag", "-a", "archive/2026s", "-m", "Archive summer")
            write("archive-builds.yml", yaml.safe_dump({"2026s": {"tag": "archive/2026s", "commit": commit}}))
            write("docs/_data/current.yml", "current_season: 2027w\n")
            write("docs/_data/archives.yml", "- season: Summer 2026\n  archive_link: 2026s\n")
            write("docs/2027w/index.html", "Current camp")
            write("docs/index.html", "Current root")
            write("docs/archive.html", "Current archive index")
            write("docs/css/site.css", "body { color: red; }")
            write("docs/images/logo.svg", "new logo")
            write("docs/js/app.js", "new javascript")
            git("rm", "-r", "docs/2026s", "docs/_data/2026s")
            output = Path(tmp) / "output"
            build(repo, output)
            for venue in ("", "hk/", "iasi/"):
                html = BeautifulSoup((output / f"2026s/{venue}index.html").read_text(), "html.parser")
                self.assertEqual(html.h1.string, "Original camp")
                self.assertEqual(html.img["src"], "/2026s/_assets/images/logo.svg")
                self.assertEqual(html.script["src"], "/2026s/_assets/js/app.js")
                self.assertEqual(html.find("a", string="Iași")["href"], "/2026s/iasi/")
                self.assertEqual(html.find("a", string="Archive")["href"], "/archive.html")
                self.assertIsNotNone(html.aside)
            self.assertEqual((output / "2026s/_assets/js/app.js").read_text(), 'console.log("original");')
            self.assertIn('/2026s/_assets/images/logo.svg', (output / "2026s/_assets/css/site.css").read_text())
            self.assertEqual((output / "css/site.css").read_text(), "body { color: red; }")
            self.assertEqual((output / "index.html").read_text(), "Current root")
            self.assertTrue((output / ".nojekyll").is_file())
            with self.assertRaisesRegex(ValueError, "already exists"):
                build(repo, output)
            write("docs/_data/current.yml", "current_season: 2026s\n")
            with self.assertRaisesRegex(ValueError, "current season"):
                archive_revisions(repo)
            write("docs/_data/current.yml", "current_season: 2027w\n")
            git("add", ".")
            git("commit", "-m", "Next camp")
            git("tag", "-f", "archive/2026s")
            with self.assertRaisesRegex(ValueError, "moved"):
                archive_revisions(repo)
            git("tag", "-d", "archive/2026s")
            with self.assertRaises(subprocess.CalledProcessError):
                archive_revisions(repo)


if __name__ == "__main__":
    unittest.main()
