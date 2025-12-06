"""CLI entry point for scraping liquor.com recipes or ingesting from TheCocktailDB API."""
import argparse
import logging
import os
import sys
from typing import Iterable, List, Tuple

import requests

# Support running as a script (python scrape_liquor.py) and as a module.
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from cocktaildb_client import (  # type: ignore
        fetch_by_filter,
        fetch_by_ids,
        fetch_by_letter,
        fetch_by_name,
        fetch_random,
    )
    from db import get_session  # type: ignore
    from rate_limiter import polite_delay  # type: ignore
    from scraper_core import save_to_db, scrape_recipe  # type: ignore
    from utils import DEFAULT_HEADERS, configure_logging  # type: ignore
else:
    from .cocktaildb_client import (
        fetch_by_filter,
        fetch_by_ids,
        fetch_by_letter,
        fetch_by_name,
        fetch_random,
    )
    from .db import get_session
    from .rate_limiter import polite_delay
    from .scraper_core import save_to_db, scrape_recipe
    from .utils import DEFAULT_HEADERS, configure_logging

logger = logging.getLogger(__name__)


def read_urls(file_path: str) -> List[str]:
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def save_many(pairs: Iterable[Tuple]):
    """Persist many (drink, ingredients) pairs."""
    for drink, ingredients in pairs:
        with get_session() as db_session:
            save_to_db(db_session, drink, ingredients)
            print(f"Saved drink: {drink.name}")


def handle_liquor(url_file: str, http_session: requests.Session):
    urls = read_urls(url_file)
    if not urls:
        logger.error("No URLs found in %s", url_file)
        sys.exit(1)

    for url in urls:
        try:
            with get_session() as db_session:
                drink, ingredients = scrape_recipe(http_session, url)
                save_to_db(db_session, drink, ingredients)
                print(f"Saved drink: {drink.name} ({url})")
        except Exception as exc:
            logger.exception("Failed to process %s: %s", url, exc)
        finally:
            polite_delay()


def handle_cocktaildb(args, http_session: requests.Session):
    mode = args.mode
    value = args.value
    results: List[Tuple] = []

    if mode == "name":
        results = fetch_by_name(http_session, value)
    elif mode == "letter":
        results = fetch_by_letter(http_session, value)
    elif mode == "ids":
        ids = [v.strip() for v in value.split(",") if v.strip()]
        results = fetch_by_ids(http_session, ids)
    elif mode == "ingredient":
        results = fetch_by_filter(http_session, "i", value)
    elif mode == "alcoholic":
        results = fetch_by_filter(http_session, "a", value)
    elif mode == "category":
        results = fetch_by_filter(http_session, "c", value)
    elif mode == "random":
        count = int(value) if value else 1
        results = fetch_random(http_session, count=count)
    else:
        logger.error("Unsupported mode %s", mode)
        sys.exit(1)

    if not results:
        logger.warning("No cocktails returned for mode=%s value=%s", mode, value)
        return

    save_many(results)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scrape liquor.com recipes or ingest from TheCocktailDB API."
    )
    subparsers = parser.add_subparsers(dest="source", required=True)

    liquor_parser = subparsers.add_parser("liquor", help="Scrape liquor.com pages from a URL list")
    liquor_parser.add_argument("urls_file", help="Text file with liquor.com recipe URLs (one per line)")

    cocktaildb_parser = subparsers.add_parser("cocktaildb", help="Ingest from TheCocktailDB API")
    cocktaildb_parser.add_argument(
        "--mode",
        required=True,
        choices=["name", "letter", "ids", "ingredient", "alcoholic", "category", "random"],
        help="API fetch mode",
    )
    cocktaildb_parser.add_argument(
        "--value",
        required=False,
        default="",
        help="Value for the selected mode (name substring, letter, comma-separated IDs, filter value, or count for random)",
    )

    return parser


def main():
    configure_logging()
    parser = build_parser()
    args = parser.parse_args()

    http_session = requests.Session()
    http_session.headers.update(DEFAULT_HEADERS)

    if args.source == "liquor":
        handle_liquor(args.urls_file, http_session)
    elif args.source == "cocktaildb":
        handle_cocktaildb(args, http_session)
    else:
        parser.error("Unknown source selected.")


if __name__ == "__main__":
    main()
