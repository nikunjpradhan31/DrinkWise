# Liquor.com Scraper

Polite web scraper that pulls cocktail recipes from liquor.com and saves them to the DrinkWise PostgreSQL database using SQLAlchemy.

## Setup
1. Create/activate a virtualenv.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set `DATABASE_URL` (defaults to `postgresql://user:password@localhost:5432/drinkwise`).

## Usage
### Liquor.com (HTML scrape)
```
python scrape_liquor.py liquor urls.txt
```
`urls.txt` should contain one liquor.com recipe URL per line.

For each URL the scraper:
- fetches the page with realistic browser headers
- parses title, description, ingredients, and hero image
- maps them into `Drink` and `DrinkIngredient` ORM objects
- saves them to Postgres
- prints `Saved drink: <name> (<url>)`

### TheCocktailDB API (no HTML scraping)
Use the API ingestion path when you want to avoid HTML scraping. Examples:
- By name: `python scrape_liquor.py cocktaildb --mode name --value margarita`
- By first letter: `python scrape_liquor.py cocktaildb --mode letter --value a`
- By IDs: `python scrape_liquor.py cocktaildb --mode ids --value 11007,11008`
- Filter by ingredient/category/alcoholic: `python scrape_liquor.py cocktaildb --mode ingredient --value Gin`
- Random: `python scrape_liquor.py cocktaildb --mode random --value 3`  # fetch 3 random drinks

## Rate limiting
Every request sleeps for at least 5 seconds with a small random jitter (see `rate_limiter.py`). This keeps the scraper polite and within 1 request per 5 seconds.

## Files
- `scrape_liquor.py` – CLI entry point
- `scraper_core.py` – scraping/parsing and DB persistence
- `rate_limiter.py` – enforced polite delay
- `db.py` – engine and session factory
- `models.py` – SQLAlchemy models for drinks/ingredients
- `utils.py` – headers and logging helpers
- `cocktaildb_client.py` – API ingestion for TheCocktailDB
- `harvest_liquor_links.py` – optional helper to collect recipe URLs

## Optional: harvest recipe URLs first
You can collect recipe links from index/sitemap pages before scraping:
```
python harvest_liquor_links.py start_urls.txt urls.txt
```
`start_urls.txt` should contain pages to scan (e.g., liquor.com sitemap or category pages). The script filters for liquor.com links with "recipe" in the path, deduplicates them, and writes them to `urls.txt`. Then run the main scraper with that `urls.txt`.
