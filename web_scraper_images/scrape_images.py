import argparse
import random
import sys
import time
from pathlib import Path
from typing import List, Optional

from duckduckgo_search import DDGS

DEFAULT_CATEGORIES = [
    "coffee",
    "tea",
    "smoothie",
    "alcohol",
    "juice",
    "soft_drink",
    "energy_drink",
    "mocktail",
    "milkshake",
    "sparkling_water",
    "functional_drink",
    "hot_chocolate",
    "protein_shake",
    "cocktail",
]


def is_wanted_image(url: str, alt: str = "") -> bool:
    """Return False if url or alt text suggests a logo, icon, or vector graphic."""
    # Basic extension/type check
    if ".svg" in url.lower():
        return False
    
    # Keyword check
    unwanted = ["logo", "icon", "vector", "clipart", "brand", "symbol", "sign", "illustration", "drawing", "cartoon"]
    combined = (url + " " + alt).lower()
    for w in unwanted:
        if w in combined:
            return False
            
    # We do NOT block gstatic/googleusercontent here to allow high-res cached versions if DDG serves them.
    return True


def collect_image_urls_ddg(query: str, target: int) -> List[str]:
    """
    Search DuckDuckGo for images.
    Returns a list of image URLs.
    """
    # Refine query
    refined_query = f"{query} drink real photo"
    
    image_urls = []
    
    print(f"  Searching DDG for: '{refined_query}'")
    
    # Retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with DDGS() as ddgs:
                # max_results needs to be higher than target to account for filtering
                # DDGS generators yield results
                results = ddgs.images(
                    refined_query,
                    region="wt-wt",
                    safesearch="off",
                    size="Large", # Prefer high res
                    type_image="photo", # Prefer photos
                    max_results=target * 4
                )
                
                for res in results:
                    url = res.get("image")
                    alt = res.get("title", "")
                    
                    if url and is_wanted_image(url, alt):
                        image_urls.append(url)
                        if len(image_urls) >= target:
                            break
            
            if image_urls:
                break
                
        except Exception as e:
            print(f"  Error searching DDG (attempt {attempt+1}/{max_retries}): {e}")
            time.sleep(random.uniform(2.0, 5.0) * (attempt + 1))
        
    return image_urls


def scrape_categories(
    categories: List[str],
    target_per_category: int,
    output_root: Path,
    url_file: Path,
) -> None:
    
    output_root.mkdir(parents=True, exist_ok=True)
    url_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Only wipe if not appending.
    # For now, we will default to append mode in this context or handle it via logic.
    # But to be safe for a generic script, we should probably check if we want a fresh start.
    # However, given the current task is to 'fill gaps', I will comment out the wipe.
    # url_file.write_text("")

    for category in categories:
        print(f"Scraping '{category}'...")
        urls = collect_image_urls_ddg(category, target_per_category)
        
        print(f"  collected {len(urls)} urls")
        if urls:
            with url_file.open("a") as f:
                for u in urls:
                    f.write(f"{category}\t{u}\n")
            print(f"  appended {len(urls)} urls to {url_file}")
        else:
            print("  No URLs found.")
            
        # Polite delay
        time.sleep(random.uniform(1.0, 2.5))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape Image results for drink categories using DuckDuckGo."
    )
    parser.add_argument(
        "--names-file",
        type=Path,
        help="Optional file with one search query per line; overrides default categories.",
    )
    parser.add_argument(
        "--target-per-category",
        type=int,
        default=40,
        help="Number of images to attempt per category (default: 40).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent / "data",
        help="Directory to store downloaded images (default: web_scraper_images/data).",
    )
    parser.add_argument(
        "--url-file",
        type=Path,
        help="Optional path for the URL output file (default: <out>/image_urls.txt).",
    )
    # Kept for compatibility but ignored
    parser.add_argument(
        "--headful",
        action="store_true",
        help="Ignored (DDG scraper is API-based).",
    )
    parser.add_argument(
        "--categories",
        nargs="+",
        default=DEFAULT_CATEGORIES,
        help="Override categories to scrape.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    if args.names_file:
        text = args.names_file.read_text(encoding="utf-8")
        categories = [line.strip() for line in text.splitlines() if line.strip()]
    else:
        categories = args.categories

    output_root: Path = args.out
    output_root.mkdir(parents=True, exist_ok=True)
    url_file = args.url_file or (output_root / "image_urls.txt")
    
    scrape_categories(
        categories=categories,
        target_per_category=args.target_per_category,
        output_root=output_root,
        url_file=url_file,
    )


if __name__ == "__main__":
    main()
