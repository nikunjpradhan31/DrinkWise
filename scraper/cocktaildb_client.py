"""Client for TheCocktailDB API, mapping responses into ORM models."""
import logging
import os
import sys
from typing import Iterable, List, Tuple
from urllib.parse import urlencode

import requests

# Allow imports when run as a standalone script
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from models import Drink, DrinkIngredient  # type: ignore
    from rate_limiter import polite_delay  # type: ignore
    from utils import DEFAULT_HEADERS  # type: ignore
else:
    from .models import Drink, DrinkIngredient
    from .rate_limiter import polite_delay
    from .utils import DEFAULT_HEADERS

logger = logging.getLogger(__name__)

API_BASE = "https://www.thecocktaildb.com/api/json/v1/1/"


def _get(session: requests.Session, path: str) -> dict:
    """Make a GET request and return JSON, respecting polite delay always."""
    try:
        resp = session.get(API_BASE + path, timeout=20)
        resp.raise_for_status()
        return resp.json()
    finally:
        polite_delay()


def _parse_drink(drink_json: dict) -> Tuple[Drink, List[DrinkIngredient]]:
    """Map a CocktailDB drink JSON object into ORM objects."""
    name = drink_json.get("strDrink") or "Unknown Drink"
    description = drink_json.get("strInstructions") or "No description available."
    image_url = drink_json.get("strDrinkThumb")
    alcoholic = (drink_json.get("strAlcoholic") or "").lower()
    is_alcoholic = "non" not in alcoholic
    category_val = drink_json.get("strCategory") or "alcohol"

    ingredients: List[DrinkIngredient] = []
    seen_names = set()
    for i in range(1, 16):
        ingredient = drink_json.get(f"strIngredient{i}")
        measure = drink_json.get(f"strMeasure{i}")
        if ingredient:
            name_clean = ingredient.strip()
            if name_clean.lower() in seen_names:
                continue
            seen_names.add(name_clean.lower())
            ingredients.append(
                DrinkIngredient(
                    ingredient_name=name_clean,
                    quantity=(measure or "").strip() or None,
                    is_allergen=False,
                )
            )

    drink = Drink(
        name=name,
        description=description,
        category=category_val,
        price_tier="$$",
        sweetness_level=5,
        caffeine_content=0,
        sugar_content=0.0,
        calorie_content=0,
        image_url=image_url,
        is_alcoholic=is_alcoholic,
        alcohol_content=0.0,
        safety_flags=["contains alcohol"] if is_alcoholic else [],
    )

    return drink, ingredients


def _collect_from_drinks(drinks_json: Iterable[dict]) -> List[Tuple[Drink, List[DrinkIngredient]]]:
    results: List[Tuple[Drink, List[DrinkIngredient]]] = []
    for d in drinks_json:
        results.append(_parse_drink(d))
    return results


def fetch_by_name(session: requests.Session, name: str) -> List[Tuple[Drink, List[DrinkIngredient]]]:
    """Search cocktails by name."""
    data = _get(session, f"search.php?{urlencode({'s': name})}")
    drinks = data.get("drinks") or []
    return _collect_from_drinks(drinks)


def fetch_by_letter(session: requests.Session, letter: str) -> List[Tuple[Drink, List[DrinkIngredient]]]:
    """List cocktails by first letter."""
    data = _get(session, f"search.php?{urlencode({'f': letter})}")
    drinks = data.get("drinks") or []
    return _collect_from_drinks(drinks)


def fetch_by_ids(session: requests.Session, ids: Iterable[str]) -> List[Tuple[Drink, List[DrinkIngredient]]]:
    """Lookup cocktails by explicit IDs."""
    results: List[Tuple[Drink, List[DrinkIngredient]]] = []
    for cid in ids:
        data = _get(session, f"lookup.php?{urlencode({'i': cid})}")
        drinks = data.get("drinks") or []
        results.extend(_collect_from_drinks(drinks))
    return results


def fetch_by_filter(session: requests.Session, filter_param: str, value: str) -> List[Tuple[Drink, List[DrinkIngredient]]]:
    """
    Use filter endpoint (by ingredient/alcoholic/category/glass) then lookup each ID for full details.
    filter_param: one of 'i', 'a', 'c', 'g'
    """
    data = _get(session, f"filter.php?{urlencode({filter_param: value})}")
    drinks = data.get("drinks") or []
    ids = [d.get("idDrink") for d in drinks if d.get("idDrink")]
    if not ids:
        return []
    return fetch_by_ids(session, ids)


def fetch_random(session: requests.Session, count: int = 1) -> List[Tuple[Drink, List[DrinkIngredient]]]:
    """Fetch one or more random cocktails."""
    results: List[Tuple[Drink, List[DrinkIngredient]]] = []
    for _ in range(count):
        data = _get(session, "random.php")
        drinks = data.get("drinks") or []
        results.extend(_collect_from_drinks(drinks))
    return results
