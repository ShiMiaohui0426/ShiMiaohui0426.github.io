"""Check the generated bilingual pages without third-party dependencies."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.html_lang = None
        self.h1_count = 0
        self.ids = []
        self.links = []
        self.assets = []
        self.images = []
        self.alternates = {}
        self.current_links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.html_lang = attrs.get("lang")
        if tag == "h1":
            self.h1_count += 1
        if "id" in attrs:
            self.ids.append(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))
            if attrs.get("aria-current") == "page":
                self.current_links.append(attrs.get("href"))
        if tag in ("img", "script"):
            self.assets.append(attrs.get("src", ""))
        if tag == "img":
            self.images.append(attrs)
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.assets.append(attrs.get("href", ""))
        if tag == "link" and attrs.get("rel") == "alternate":
            self.alternates[attrs.get("hreflang")] = attrs.get("href")


def validate(root):
    assert (root / "images/avatar-anime.png").is_file(), "Missing illustrated avatar"
    assert not (root / "images/photo.jpg").exists(), "Original portrait must not be published"
    for html in root.rglob("*.html"):
        assert "/images/photo.jpg" not in html.read_text(encoding="utf-8"), f"Old portrait reference: {html}"
    routes = ["/", "/experience/", "/publications/", "/patents/", "/cv/"]
    all_routes = routes + ["/zh" + route for route in routes]
    parsed = {}
    for route in all_routes:
        file = root / route.lstrip("/") / "index.html"
        assert file.is_file(), f"Missing page: {route}"
        text = file.read_text(encoding="utf-8")
        assert "{%" not in text and "{{" not in text, f"Unrendered Liquid: {route}"
        assert "SMH_RESUME.pdf" not in text, f"Old CV link: {route}"
        assert "fuji.waseda.jp" not in text, f"Old institutional email: {route}"
        assert "年终述职" not in text and ".pptx" not in text, f"Internal report link: {route}"
        page = Page(text)
        assert page.h1_count == 1, f"Expected one H1: {route}"
        assert len(page.ids) == len(set(page.ids)), f"Duplicate IDs: {route}"
        assert page.html_lang == ("zh-CN" if route.startswith("/zh/") else "en"), route
        assert page.current_links == [route], f"Wrong current navigation: {route}"
        other = route[3:] if route.startswith("/zh/") else "/zh" + route
        other_lang = "en" if route.startswith("/zh/") else "zh-CN"
        assert urlsplit(page.alternates[other_lang]).path == other, route
        assert other in page.links, f"Missing language switch: {route}"
        parsed[route] = page

    for route, page in parsed.items():
        for link in page.links + page.assets:
            assert link, f"Empty URL: {route}"
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            path = unquote(url.path) or route
            assert path.startswith("/"), f"Unexpected relative URL: {link}"
            target = root / path.lstrip("/")
            # Legacy Jekyll permalinks omit the .html suffix; GitHub Pages
            # serves the corresponding HTML file for these extensionless URLs.
            candidates = (target, target / "index.html", Path(str(target) + ".html"))
            assert any(file.is_file() for file in candidates), f"Broken URL {link} in {route}"
            if url.fragment and path in parsed:
                assert unquote(url.fragment) in parsed[path].ids, f"Broken anchor: {link}"

    for prefix in ("", "/zh"):
        portraits = [image for image in parsed[prefix + "/"].images if image.get("class") == "portrait"]
        assert len(portraits) == 1, "Expected one homepage portrait"
        assert portraits[0]["src"] == "/images/avatar-anime.png", "Wrong homepage avatar"
        assert portraits[0].get("alt"), "Avatar needs descriptive alternative text"
        assert int(portraits[0]["width"]) * 4 == int(portraits[0]["height"]) * 3
        publications = parsed[prefix + "/publications/"]
        assert len([item for item in publications.ids if item.endswith(("-2021", "-2023", "-2024"))]) == 5
        assert len(parsed[prefix + "/patents/"].ids) == 9  # main + 8 application records
        assert {"gds", "multi-robot", "tactile"}.issubset(parsed[prefix + "/experience/"].ids)
        figures = parsed[prefix + "/experience/"].images
        assert len(figures) == 5, "Expected five sourced project figures"
        for figure in figures:
            assert figure.get("alt"), "Figure needs descriptive alternative text"
            assert int(figure.get("width", 0)) > 0 and int(figure.get("height", 0)) > 0
        cv_text = (root / (prefix + "/cv/").lstrip("/") / "index.html").read_text(encoding="utf-8")
        project_text = (root / (prefix + "/experience/").lstrip("/") / "index.html").read_text(encoding="utf-8")
        assert "Sharpa" in cv_text, "Missing Sharpa-related experience"
        assert "33.3" in project_text and "2.09" in project_text, "Missing full-system and same-platform results"
        assert ("数万小时" if prefix else "tens of thousands of hours") in project_text
    print(f"PASS: {len(parsed)} bilingual pages; routes, language pairs, assets, anchors, publication and patent counts.")


if __name__ == "__main__":
    validate(Path(sys.argv[1] if len(sys.argv) > 1 else "_site"))
