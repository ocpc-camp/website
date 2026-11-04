from contextlib import redirect_stdout
import io
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_links import check_site


class LinkTests(unittest.TestCase):
    def test_archive_regressions_and_supported_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def write(name, text):
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(text)
            write("index.html", '<meta http-equiv="refresh" content="0; url=/2025s/">')
            write("2025s/index.html", '<a href="/2023w/">Winter</a>')
            write("2023w/index.html", "Winter")
            write("2023w/rating.html", '<link rel="icon" href="images/favicon.ico">')
            write("2023w/sponsors.html", '<img src="images/think-cell.svg">')
            write("2025s/archive.html", '<a href="2023w">Website</a><a href="2023w/rating.html">Rating</a>')
            write("2023w/_assets/favicon.ico", "icon")
            write("2023w/_assets/images/think-cell.svg", "svg")
            with redirect_stdout(io.StringIO()):
                errors = check_site(root)
            self.assertEqual(len(errors), 4)
            write("2023w/rating.html", '<link rel="icon" href="/2023w/_assets/favicon.ico">')
            write("2023w/sponsors.html", '<img src="_assets/images/think-cell.svg">')
            write("2025s/archive.html", '<a href="/2023w/">Website</a><a href="https://ocpc.camp/2023w/rating.html?q=1#top">Rating</a><a href="https://example.invalid/missing">External</a>')
            write("css/site.css", '@import "extra.css";a{background:url("../images/a%20b.svg")}')
            write("css/extra.css", 'a{background:url(data:image/png;base64,abc)}')
            write("images/a b.svg", "svg")
            write("2025s/before.html", '<img src="{{ unrendered }}">')
            with redirect_stdout(io.StringIO()):
                self.assertEqual(check_site(root), [])
            write("css/extra.css", 'a{background:url(/missing.png)}')
            with redirect_stdout(io.StringIO()):
                self.assertEqual(len(check_site(root)), 1)

    def test_missing_build_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                check_site(Path(tmp))
