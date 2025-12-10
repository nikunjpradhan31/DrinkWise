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

## Name-based scraping (all drinks)

A consolidated list of all 500 drink names from `data/generated` is at `data_drink_names/drink_names.txt`. To scrape image URLs per drink name into a separate folder:

```bash
python scrape_images.py \
  --names-file data_drink_names/drink_names.txt \
  --target-per-category 5 \
  --out data_drink_names \
  --url-file data_drink_names/image_urls.txt \
  --headful
```

Adjust `--target-per-category` as needed. URLs append to `data_drink_names/image_urls.txt` (tab-separated `name<TAB>url`). The script does not download images.
