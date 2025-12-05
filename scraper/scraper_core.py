"""Core scraping and persistence logic."""
import logging
import os
import sys
from typing import List, Tuple

import requests
from bs4 import BeautifulSoup

# Allow imports when run as a standalone script
if __package__ is None or __package__ == "":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from models import Drink, DrinkIngredient  # type: ignore
else:
    from .models import Drink, DrinkIngredient

logger = logging.getLogger(__name__)


def _extract_text(node, default: str = "") -> str:
    return node.get_text(strip=True) if node else default


def scrape_recipe(session: requests.Session, url: str) -> Tuple[Drink, List[DrinkIngredient]]:
    """Fetch and parse a liquor.com recipe page into ORM objects."""
    logger.info("Fetching %s", url)
    response = session.get(url, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title_node = soup.select_one("h1.heading__title")
    name = _extract_text(title_node, default="Unknown Drink")

    desc_nodes = soup.select(".article-header .loc p")
    description = " ".join([_extract_text(p) for p in desc_nodes if _extract_text(p)])
    if not description:
        description = "No description available."

    image_node = soup.select_one("figure.mntl-primary-image img")
    image_url = image_node.get("src") if image_node and image_node.has_attr("src") else None

    ingredient_nodes = soup.select("ul.mntl-structured-ingredients__list > li")
    ingredients: List[DrinkIngredient] = []
    for li in ingredient_nodes:
        quantity_text = _extract_text(li.select_one(".mntl-structured-ingredients__quantity"))
        ingredient_text = _extract_text(
            li.select_one(".mntl-structured-ingredients__ingredient"), default="Unknown ingredient"
        )
        ingredients.append(
            DrinkIngredient(
                ingredient_name=ingredient_text,
                quantity=quantity_text or None,
                is_allergen=False,
            )
        )

    drink = Drink(
        name=name,
        description=description,
        category="alcohol",
        price_tier="$$",
        sweetness_level=5,
        caffeine_content=0,
        sugar_content=0.0,
        calorie_content=0,
        image_url=image_url,
        is_alcoholic=True,
        alcohol_content=0.0,
        safety_flags=["contains alcohol"],
    )

    logger.info("Parsed recipe %s with %d ingredients", name, len(ingredients))
    return drink, ingredients


def save_to_db(session, drink: Drink, ingredients: List[DrinkIngredient]) -> None:
    """Persist a drink and its ingredients within a transaction."""
    session.add(drink)
    session.flush()  # ensure drink_id is populated
    for ingredient in ingredients:
        ingredient.drink = drink
    session.add_all(ingredients)
    session.commit()
    logger.info("Saved drink %s (id=%s)", drink.name, drink.drink_id)
