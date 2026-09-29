#!/usr/bin/env python3
"""Regenerate data/bands.json and data/landmark-genes.json from their original sources.

You only need this if you want to refresh the data or audit how it was made.
The sources are the NCBI band tables and the Ensembl gene cache shipped in the
ideogram.js npm package:

    npm pack ideogram@1.53.0 && tar -xzf ideogram-1.53.0.tgz
    python tools/make_data.py package/dist/data

What it does:
  * bands: NCBI human ideogram tables (GRCh38) at 400, 550 and 850 bands
    (homo-sapiens-400.json, homo-sapiens-550.json, homo-sapiens-GCF_000001405.26.json).
    The 550 file leaves gaps inside a few 400-level bands (7q11.2, 8q11.2, 11p11.1,
    12q24.3, 18p11.3, Xp11.2, Yq11.2); the sub-bands there are rescaled to fill
    their parent band.
  * genes: for every gene already listed in data/landmark-genes.json, the GRCh38
    start/end is refreshed from the Ensembl gene cache and the cytoband span is
    recomputed from the 850-band table. The short clinical notes are kept.
"""
import gzip
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORDER = [str(i) for i in range(1, 23)] + ["X", "Y"]
SOURCES = {
    "400": "bands/native/homo-sapiens-400.json",
    "550": "bands/native/homo-sapiens-550.json",
    "850": "bands/native/homo-sapiens-GCF_000001405.26.json",
}


def read_bands(data_dir: Path):
    out = {}
    for level, rel in SOURCES.items():
        for row in json.loads((data_dir / rel).read_text())["chrBands"]:
            p = row.split(" ")
            stain = p[7] + (p[8] if len(p) > 8 else "")
            out.setdefault(p[0], {}).setdefault(level, []).append(
                [p[1] + p[2], int(p[3]), int(p[4]), int(p[5]), int(p[6]), stain])
    return out


def is_child(child: str, parent: str) -> bool:
    if child == parent or child.startswith(parent + "."):
        return True
    return "." in parent and child.startswith(parent) and child[len(parent):].isdigit()


def fill_550_gaps(bands):
    fixed = []
    for chrom, levels in bands.items():
        for parent in levels["400"]:
            kids = [k for k in levels["550"] if is_child(k[0], parent[0])]
            if not kids:
                continue
            lo, hi = min(k[1] for k in kids), max(k[2] for k in kids)
            if (lo, hi) == (parent[1], parent[2]):
                continue
            for k in kids:
                k[1] = round(parent[1] + (k[1] - lo) * (parent[2] - parent[1]) / (hi - lo))
                k[2] = round(parent[1] + (k[2] - lo) * (parent[2] - parent[1]) / (hi - lo))
            fixed.append(chrom + parent[0])
    return fixed


def format_bands(about, chromosomes):
    """One band per line, so diffs of the data stay readable."""
    lines = ["{", '"_about": ' + json.dumps(about) + ",", '"chromosomes": {']
    items = list(chromosomes.items())
    for i, (chrom, levels) in enumerate(items):
        lines.append(f' "{chrom}": {{')
        lv = list(levels.items())
        for j, (level, rows) in enumerate(lv):
            lines.append(f'  "{level}": [')
            lines.append(",\n".join("   " + json.dumps(r) for r in rows))
            lines.append("  ]" + ("," if j < len(lv) - 1 else ""))
        lines.append(" }" + ("," if i < len(items) - 1 else ""))
    lines += ["}", "}"]
    return "\n".join(lines) + "\n"


def band_at(rows, bp):
    for r in rows:
        if r[3] <= bp <= r[4]:
            return r[0]
    return None


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    data_dir = Path(sys.argv[1])
    bands = read_bands(data_dir)
    fixed = fill_550_gaps(bands)
    print("rescaled 550-level sub-bands in:", ", ".join(fixed))

    about = json.loads((ROOT / "data/bands.json").read_text())["_about"]
    (ROOT / "data/bands.json").write_text(format_bands(about, {c: bands[c] for c in ORDER}))

    cache = {}
    with gzip.open(data_dir / "cache/genes/homo-sapiens-genes.tsv.gz", "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            p = line.rstrip("\n").split("\t")
            cache.setdefault((p[0], p[4]), (int(p[1]), int(p[1]) + int(p[2])))

    genes_path = ROOT / "data/landmark-genes.json"
    genes = json.loads(genes_path.read_text(encoding="utf-8"))
    for chrom, items in genes["chromosomes"].items():
        for g in items:
            symbol = "IGHM" if g["n"] == "IGH" else g["n"]
            start, end = cache[(chrom, symbol)]
            b1, b2 = band_at(bands[chrom]["850"], start), band_at(bands[chrom]["850"], end)
            g["bp"], g["end"] = start, end
            g["band"] = chrom + b1 + ("" if b1 == b2 else "–" + b2)
    genes_path.write_text(json.dumps(genes, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("refreshed", sum(len(v) for v in genes["chromosomes"].values()), "genes")


if __name__ == "__main__":
    main()
