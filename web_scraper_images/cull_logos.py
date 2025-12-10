"""
Remove likely logo/doodle URLs from a tab-separated name<tab>url file.

Heuristics:
- Drop URLs containing common logo/doodle substrings.
- Drop URLs where the host is clearly a Google cache/asset host.
Usage:
  python cull_logos.py --in data_drink_names/hi_res_urls.txt --out data_drink_names/hi_res_urls_filtered.txt
"""
import argparse
from pathlib import Path
from urllib.parse import urlparse


LOGO_KEYWORDS = [
    "logo",
    "doodle",
    "favicon",
    "sprite",
    "transparent",
]

BAD_HOSTS = [
    # "gstatic.com",             # Often hosts valid high-res cached images
    # "google.com",              # Core Google domains
    # "googleusercontent.com",   # User content can be valid
]


def is_logo(url: str) -> bool:
    lower = url.lower()
    if any(k in lower for k in LOGO_KEYWORDS):
        return True
    host = urlparse(url).netloc.lower()
    return any(bad in host for bad in BAD_HOSTS)


def main() -> None:
    parser = argparse.ArgumentParser(description="Cull likely logo/doodle URLs from URL list.")
    parser.add_argument("--in", dest="input_file", type=Path, required=True, help="Input TSV file name<TAB>url")
    parser.add_argument("--out", dest="output_file", type=Path, required=True, help="Output TSV file")
    args = parser.parse_args()

    lines = args.input_file.read_text(encoding="utf-8").splitlines()
    kept = []
    dropped = 0
    for line in lines:
        if "\t" not in line:
            continue
        name, url = line.split("\t", 1)
        if is_logo(url):
            dropped += 1
            continue
        kept.append(f"{name}\t{url}")

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text("\n".join(kept), encoding="utf-8")
    print(f"Kept {len(kept)} entries, dropped {dropped} logo/doodle candidates -> {args.output_file}")


if __name__ == "__main__":
    main()
