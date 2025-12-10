import argparse
import asyncio
import mimetypes
import random
import re
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Set
from urllib.parse import urlparse

import aiohttp
from aiohttp import ClientSession
from playwright.async_api import Page, async_playwright


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


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s-]+", "_", text)


def guess_extension(url: str, content_type: Optional[str]) -> str:
    if content_type:
        ext = mimetypes.guess_extension(content_type.split(";")[0].strip())
        if ext:
            return ext
    suffix = Path(urlparse(url).path).suffix
    if suffix:
        return suffix
    return ".jpg"


async def maybe_accept_consent(page: Page) -> None:
    selectors = [
        'button:has-text("Accept all")',
        'button:has-text("I agree")',
        'button:has-text("Accept")',
        'button:has-text("Reject all")',
        'div[role="button"]:has-text("Accept")',
        'div[role="button"]:has-text("I agree")',
        'div[role="button"]:has-text("Reject all")',
        'button[aria-label="Accept all"]',
    ]
    for selector in selectors:
        try:
            button = page.locator(selector)
            if await button.count():
                await button.first.click(timeout=1500)
                await page.wait_for_timeout(400)
                break
        except Exception:
            continue


async def collect_image_urls(page: Page, query: str, target: int) -> List[str]:
    await page.goto("https://www.google.com/imghp?hl=en", wait_until="load")
    await maybe_accept_consent(page)
    await page.wait_for_selector('input[name="q"], textarea[name="q"]', timeout=45000)
    search_box = page.locator('input[name="q"], textarea[name="q"]')
    await search_box.first.click()
    await search_box.first.fill(query)
    await page.keyboard.press("Enter")
    await page.wait_for_load_state("networkidle")
    images_tab = page.locator(
        'a[href*="tbm=isch"], a[aria-label="Images"], a[role="tab"]:has-text("Images")'
    )
    if await images_tab.count():
        await images_tab.first.click()
        await page.wait_for_load_state("networkidle")
    else:
        # Fallback: go directly to images vertical
        from urllib.parse import quote_plus

        images_url = f"https://www.google.com/search?tbm=isch&q={quote_plus(query)}&hl=en&safe=off"
        await page.goto(images_url, wait_until="load")
        await maybe_accept_consent(page)
    image_urls: Set[str] = set()

    async def harvest_from_dom() -> None:
        nonlocal image_urls
        try:
            srcs = await page.evaluate(
                """() => {
                    const imgs = Array.from(document.querySelectorAll('img'));
                    const vals = [];
                    for (const img of imgs) {
                        const candidates = [
                            img.src,
                            img.getAttribute('data-src'),
                            img.getAttribute('data-iurl'),
                        ];
                        for (const c of candidates) {
                            if (c && c.startsWith('http')) {
                                vals.push(c);
                                break;
                            }
                        }
                    }
                    return vals;
                }"""
            )
            for s in srcs:
                image_urls.add(s)
        except Exception:
            return

    # Try to harvest immediately
    await harvest_from_dom()

    # Scroll-and-harvest loop to load more thumbnails without strict selectors
    attempts = 0
    while len(image_urls) < target and attempts < 30:
        await page.mouse.wheel(0, random.randint(1200, 2200))
        await page.wait_for_timeout(random.randint(600, 1200))
        await maybe_accept_consent(page)
        await harvest_from_dom()
        attempts += 1

    if not image_urls:
        raise RuntimeError("No thumbnails detected; page may be blocked or layout changed.")

    return list(image_urls)[:target]


async def download_image(
    session: ClientSession, url: str, dest_dir: Path, prefix: str, idx: int
) -> bool:
    try:
        async with session.get(url, timeout=15) as resp:
            if resp.status != 200:
                return False
            content_type = resp.headers.get("Content-Type", "")
            if "image" not in content_type:
                return False
            data = await resp.read()
    except Exception:
        return False

    ext = guess_extension(url, content_type)
    filename = f"{prefix}_{idx:04d}{ext}"
    dest_path = dest_dir / filename
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path.write_bytes(data)
        return True
    except Exception:
        return False


async def download_images(urls: Iterable[str], dest_dir: Path, prefix: str) -> int:
    semaphore = asyncio.Semaphore(8)
    success_counter = 0

    async def worker(enumerated):
        nonlocal success_counter
        idx, url = enumerated
        async with semaphore:
            ok = await download_image(session, url, dest_dir, prefix, idx)
            if ok:
                success_counter += 1

    timeout = aiohttp.ClientTimeout(total=20)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        await asyncio.gather(*(worker(item) for item in enumerate(urls)))

    return success_counter


async def scrape_categories(
    categories: List[str],
    target_per_category: int,
    output_root: Path,
    headless: bool = True,
) -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless)
        page = await browser.new_page(
            viewport={"width": 1280, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        output_root.mkdir(parents=True, exist_ok=True)
        url_file = output_root / "image_urls.txt"
        url_file.write_text("")
        for category in categories:
            print(f"Scraping '{category}'...")
            urls = await collect_image_urls(page, category, target_per_category)
            print(f"  collected {len(urls)} urls")
            with url_file.open("a") as f:
                for u in urls:
                    f.write(f"{category}\t{u}\n")
            print(f"  appended {len(urls)} urls to {url_file}")
            await page.wait_for_timeout(random.randint(800, 1400))
        await browser.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape Google Images results for drink categories."
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
        "--headful",
        action="store_true",
        help="Run browser in headed mode for debugging.",
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
    output_root: Path = args.out
    output_root.mkdir(parents=True, exist_ok=True)
    asyncio.run(
        scrape_categories(
            categories=args.categories,
            target_per_category=args.target_per_category,
            output_root=output_root,
            headless=not args.headful,
        )
    )


if __name__ == "__main__":
    main()
