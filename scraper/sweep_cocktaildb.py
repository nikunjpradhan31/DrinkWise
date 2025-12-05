"""Sweep TheCocktailDB for all cocktails by iterating letters/digits."""
import argparse
import logging
import os
import sys
from string import ascii_lowercase, digits
from typing import Iterable

import requests

# Support running as script or module
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from cocktaildb_client import fetch_by_letter  # type: ignore
    from db import get_session  # type: ignore
    from scraper_core import save_to_db  # type: ignore
    from utils import DEFAULT_HEADERS, configure_logging  # type: ignore
else:
    from .cocktaildb_client import fetch_by_letter
    from .db import get_session
    from .scraper_core import save_to_db
    from .utils import DEFAULT_HEADERS, configure_logging

logger = logging.getLogger(__name__)


def sweep_letters(letters: Iterable[str]) -> None:
    http_session = requests.Session()
    http_session.headers.update(DEFAULT_HEADERS)

    for letter in letters:
        letter = letter.strip()
        if not letter:
            continue
        try:
            results = fetch_by_letter(http_session, letter)
            if not results:
                logger.info("No drinks for letter '%s'", letter)
                continue
            logger.info("Found %d drinks for letter '%s'", len(results), letter)
            for drink, ingredients in results:
                with get_session() as db_session:
                    save_to_db(db_session, drink, ingredients)
                    print(f"Saved drink: {drink.name}")
        except Exception as exc:
            logger.exception("Failed letter '%s': %s", letter, exc)


def main():
    parser = argparse.ArgumentParser(
        description="Sweep TheCocktailDB by iterating first letters (a-z, optional digits)."
    )
    parser.add_argument(
        "--include-digits",
        action="store_true",
        help="Also sweep digits 0-9 for numeric-leading names.",
    )
    args = parser.parse_args()

    configure_logging()

    letters = list(ascii_lowercase)
    if args.include_digits:
        letters += list(digits)

    sweep_letters(letters)


if __name__ == "__main__":
    main()
