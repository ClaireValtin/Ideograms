#!/usr/bin/env python3
"""Rebuild the website pages from src/ templates and data/ JSON.

Usage:
    python build.py                  # writes index.html and simulator.html (the GitHub Pages site)
    python build.py --out DIR        # writes the same pages into another folder

Each page is a single self-contained HTML file: the template gets the band
and gene data embedded, so the pages work offline and on GitHub Pages
without a server. Edit the templates or the data, then run this script;
never edit index.html or simulator.html by hand.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
DATA = ROOT / "data"

# page file name -> template file name
PAGES = {
    "index.html": "ideograms.template.html",
    "simulator.html": "simulator.template.html",
    "abnormalities.html": "abnormalities.template.html",
}


def load_data():
    bands = json.loads((DATA / "bands.json").read_text(encoding="utf-8"))["chromosomes"]
    genes = json.loads((DATA / "landmark-genes.json").read_text(encoding="utf-8"))["chromosomes"]
    compact = lambda obj: json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
    return compact(bands), compact(genes)


def wrap(body: str) -> str:
    """Templates start with <title>, <link> and <style>; move those into a proper <head>."""
    cut = body.index("</style>") + len("</style>")
    return (
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + body[:cut]
        + "\n<style>body{margin:0}</style>\n</head>\n<body>"
        + body[cut:]
        + "\n</body>\n</html>\n"
    )


def render(template: str, bands: str, genes: str, links: dict) -> str:
    out = template.replace("__DATA__", bands).replace("__GENES__", genes)
    for key, value in links.items():
        out = out.replace(key, value)
    leftover = [tok for tok in ("__DATA__", "__GENES__", "__IDEO_HREF__", "__SIM_HREF__", "__ABN_HREF__") if tok in out]
    if leftover:
        raise SystemExit(f"unfilled placeholders: {leftover}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(ROOT), help="output folder (default: repo root)")
    args = ap.parse_args()
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    bands, genes = load_data()
    links = {
        "__IDEO_HREF__": "index.html",
        "__SIM_HREF__": "simulator.html",
        "__ABN_HREF__": "abnormalities.html",
        # the tab links open in the same window on the website
        "__IDEO_TGT__": "", "__SIM_TGT__": "", "__ABN_TGT__": "",
    }
    for page, template_name in PAGES.items():
        template_path = SRC / template_name
        if not template_path.exists():
            continue
        html = wrap(render(template_path.read_text(encoding="utf-8"), bands, genes, links))
        (out_dir / page).write_text(html, encoding="utf-8")
        print(f"wrote {out_dir / page} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
