# Web Image Scraper (Google Images)

This directory contains a Playwright-based scraper that collects full-size image URLs from Google Images and downloads them by category.

## Setup

```bash
cd web_scraper_images
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
playwright install chromium
```

## Run

```bash
python scrape_images.py \
  --target-per-category 40 \
  --out data \
  --categories coffee tea smoothie alcohol juice soft_drink energy_drink mocktail milkshake sparkling_water functional_drink hot_chocolate protein_shake cocktail
```

- Images save to `web_scraper_images/data/<category>/`.
- Add `--headful` to watch the browser.
- Adjust `--target-per-category` to reach the ~500 total you need (14 categories × 35–40 each).

## Notes

- Google Images can change markup or throttle aggressively; re-run if some categories return fewer images.
- The script filters for `http*` image sources and only writes responses with an image content-type.
