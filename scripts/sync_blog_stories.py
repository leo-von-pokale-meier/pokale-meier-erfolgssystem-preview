"""Create a static, public-safe snapshot of the newest Pokale-Meier blog stories.

This runs in GitHub Actions. The public preview never calls pokale-meier.de from
the visitor's browser; it only loads the generated same-origin static JS file.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

BLOG_URL = "https://pokale-meier.de/blog"
OUTPUT = Path(__file__).resolve().parents[1] / "blog-stories.js"
SKIP_PATHS = {
    "/blog",
    "/blog/ratgeber",
    "/blog/material-technik",
    "/blog/anlaesse-inspiration",
    "/blog/mitarbeiter-wertschaetzung",
    "/blog/sportverein-ratgeber",
    "/blog/ehrenamt-gesellschaft",
}


class BlogLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.href: str | None = None
        self.parts: list[str] = []
        self.links: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.href, self.parts = href, []

    def handle_data(self, data: str) -> None:
        if self.href:
            self.parts.append(data.strip())

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self.href:
            self.links.append((self.href, " ".join(part for part in self.parts if part)))
            self.href, self.parts = None, []


def latest_stories(source: str) -> list[dict[str, str]]:
    parser = BlogLinks()
    parser.feed(source)
    stories: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw_href, raw_title in parser.links:
        href = urljoin(BLOG_URL, raw_href)
        parsed = urlparse(href)
        title = re.sub(r"\s+", " ", raw_title).strip()
        if (
            parsed.scheme != "https"
            or parsed.netloc != "pokale-meier.de"
            or parsed.path in SKIP_PATHS
            or not parsed.path.startswith("/blog/")
            or parsed.query
            or parsed.fragment
            or not title
            or title.lower() == "weiter"
            or title.lower().startswith("0 kommentare")
            or parsed.path in seen
        ):
            continue
        seen.add(parsed.path)
        stories.append({"title": title, "href": href, "topic": "Pokale Meier Blog"})
        if len(stories) == 4:
            return stories
    raise RuntimeError("Es konnten nicht vier aktuelle Blogartikel erkannt werden.")


def main() -> None:
    request = Request(BLOG_URL, headers={"User-Agent": "Pokale-Meier-Preview-Blog-Sync/1.0"})
    with urlopen(request, timeout=30) as response:
        source = response.read().decode("utf-8", errors="replace")
    stories = latest_stories(source)
    output = "/* Automatisch aus https://pokale-meier.de/blog erzeugt. Nicht manuell bearbeiten. */\n"
    output += "window.PM_BLOG_STORIES = " + json.dumps(stories, ensure_ascii=False, separators=(",", ":")) + ";\n"
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"Aktualisiert: {OUTPUT.name} ({len(stories)} Story-Kacheln)")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Blog-Synchronisation fehlgeschlagen: {error}", file=sys.stderr)
        raise
