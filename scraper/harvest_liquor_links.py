"""CLI to collect liquor.com recipe URLs and write them to a file."""
import argparse
import logging
import os
import sys
from typing import Iterable, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Support running as script or module
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from rate_limiter import polite_delay  # type: ignore
    from utils import DEFAULT_HEADERS, configure_logging  # type: ignore
else:
    from .rate_limiter import polite_delay
    from .utils import DEFAULT_HEADERS, configure_logging

logger = logging.getLogger(__name__)


def looks_like_recipe(url: str) -> bool:
    """Heuristic to detect liquor.com recipe links."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    # Only keep liquor.com domain and paths containing recipe
    if "liquor.com" not in parsed.netloc:
        return False
    path = parsed.path.lower()
    return "recipe" in path


def harvest_links(
    session: requests.Session, start_urls: Iterable[str]
) -> Set[str]:
    """Fetch start URLs and collect recipe links."""
    found: Set[str] = set()
    for url in start_urls:
        try:
            logger.info("Fetching index page %s", url)
            resp = session.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                full_url = urljoin(url, href)
                if looks_like_recipe(full_url):
                    found.add(full_url)
        except Exception as exc:
            logger.exception("Failed to harvest from %s: %s", url, exc)
        finally:
            polite_delay()
    return found


def read_list(path: str) -> list:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def write_list(path: str, urls: Iterable[str]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for u in sorted(urls):
            f.write(u + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Harvest liquor.com recipe links from index/sitemap pages."
    )
    parser.add_argument("start_urls_file", help="Text file with one start URL per line")
    parser.add_argument(
        "output_file", help="Output file path for harvested recipe URLs"
    )
    args = parser.parse_args()

    configure_logging()

    start_urls = read_list(args.start_urls_file)
    if not start_urls:
        logger.error("No start URLs found in %s", args.start_urls_file)
        sys.exit(1)

    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)

    found = harvest_links(session, start_urls)
    if not found:
        logger.warning("No recipe links found.")
    else:
        logger.info("Found %d recipe links", len(found))

    write_list(args.output_file, found)
    print(f"Wrote {len(found)} recipe URLs to {args.output_file}")


if __name__ == "__main__":
    main()
