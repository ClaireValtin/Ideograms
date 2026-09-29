# Idiograms

Interactive R- and G-banded idiograms of all 24 human chromosomes at the 400, 550 and ~700-band levels, with landmark genes; a simulator that shows how the same chromosomes look in a real RHG metaphase; and a builder for structural and numerical abnormalities that writes ISCN 2024 nomenclature. Three self-contained HTML pages, no dependencies.

## Use

Open `index.html` in any browser. It works offline; without internet it falls back to system fonts.

### Idiogram reference (`index.html`)

- **Karyogram:** all chromosomes in A–G groups, aligned on the centromere and drawn to one shared scale. Switch between 400, 550 and ~700 bands. Click a chromosome to open it.
- **Detail view:** the selected chromosome at all three band levels side by side. Hover or tap a band to outline the same genomic interval at the other levels. The side panel shows the band's R- and G-banding appearance, its GRCh38 interval, its size and any landmark genes inside it.
- **R/G switch:** flips every view between R-banding (RHG) and G-banding (GTG).
- **Landmark genes:** 2 to 6 per chromosome, 74 in total. Hover a gene name for its band and a short note.
- **Deep links:** add `#chr9`, `#chrX` and so on to the address to open a chromosome directly.
- **Simulator link:** "See it under the microscope" opens the chromosome you are viewing in the simulator.

### Microscope simulator (`simulator.html`)

A synthetic brightfield image of R-banded (RHG) chromosomes, built from the same GRCh38 (~700-band) data. It is a model of what you would see, not a photograph.

- **One chromosome:** a homologue pair of any chromosome, with an optional idiogram beside it. Small chromosomes are enlarged to fill the field, and the caption gives the magnification relative to chromosome 1.
- **Karyogram:** all chromosomes in rows, aligned on the centromere at one shared scale, as 46,XX or 46,XY.
- **Controls:** condensation (about 300 to 700 bands; sub-bands merge as it drops), focus, staining, chromatid separation, bending, Giemsa colour or camera grayscale, and the tone of heterochromatin.
- **New spread:** draws different homologues. Heterochromatin blocks and acrocentric stalks vary in size between homologues, as they do in people.
- **Deep links:** `simulator.html#chr1` through `#chrY`, or `simulator.html#karyogram`.

### Abnormality builder (`abnormalities.html`)

- **Type a karyotype** in the ISCN short system, e.g. `46,XY,t(9;22)(q34;q11.2)`, or pick one of 23 examples of recurrent rearrangements, grouped as myeloid, lymphoid, solid tumours and constitutional (WHO/ICC notation where one exists). The result appears directly below.
- **Or build it by hand.** Choose the abnormality (translocation, unbalanced der, deletion, duplication, inversion, isochromosome, ring, unknown material, extra or missing copy) and the chromosome(s), then click the bands where the breaks are. Drag an orange breakpoint marker up or down: the band name, the resulting chromosome and the ISCN string update as it moves, so you can find the right cut by eye.
- **Output:** the karyotype in the short system, each derivative in the detailed system (e.g. `der(9) 9pter→9q34::22q11.2→22qter`), and the landmark genes lying in the breakpoint bands.
- **Views:** normal and abnormal homologues side by side as idiograms (a coloured strip shows which chromosome each segment comes from) or as a simulated microscope image.
- **Scope:** t, der(…)t, del, dup, inv, i, r, add, and gains/losses. Not supported: insertions, dicentrics, markers, three-way translocations, inverted duplications, mosaics and clone counts.

### Publish with GitHub Pages

The site is published with GitHub Pages (Settings → Pages → Deploy from a branch → `main`, `/ (root)`) at `https://clairevaltin.github.io/Idiograms/`. Links between the pages carry a version tag (`?v=…`) that changes with every build, so a browser never shows an older cached copy of a page after an update.

## How this repo is organised

| Path | What it is |
|---|---|
| `index.html`, `simulator.html`, `abnormalities.html` | The website pages. **Generated — do not edit by hand.** |
| `src/*.template.html` | The page sources: layout, styles and code, with placeholders where the data goes. Edit these. |
| `data/bands.json`, `data/landmark-genes.json`, `data/breakpoint-genes.json` | The band and gene data. Edit these to change what the pages show. |
| `build.py` | Puts templates and data together into the pages. |
| `tools/make_data.py` | Regenerates the data files from the original NCBI/Ensembl sources, for audits or refreshes. |

After changing a template or a data file, rebuild the pages and commit them:

```
python build.py
```

Each page stays a single self-contained file, so it works offline and on GitHub Pages without a server.

## Data

| File | Contents | Source |
|---|---|---|
| `data/bands.json` | Every band at 400, 550 and GRCh38 (~700, stored under the key `850`) levels: `[band, iscn_start, iscn_stop, bp_start, bp_stop, ncbi_stain]` | NCBI human ideogram data, GRCh38, as packaged in [ideogram.js](https://github.com/eweitz/ideogram) 1.53.0 |
| `data/landmark-genes.json` | Symbol, GRCh38 start/end, cytoband span, short note | Ensembl release 110 GRCh38 gene coordinates (via the ideogram.js gene cache); bands assigned from the GRCh38 table |
| `data/breakpoint-genes.json` | Fusion partners of the example rearrangements (e.g. TCF3, PBX1, EWSR1, FLI1), used only on the abnormalities page | Same source and method as the landmark genes |

`index.html` embeds the same data, so it does not load these files. They are here so the data can be checked and reused on its own.

### Processing

- **R pattern.** Drawn as the reciprocal of NCBI's G-stain grades, which is how ISCN treats R-banded idiograms. Band numbering is identical in both methods.
- **550-level gaps.** The source file leaves gaps in seven places: 7q11.2, 8q11.2, 11p11.1, 12q24.3, 18p11.3, Xp11.2 and Yq11.2. The sub-bands in each were rescaled to fill their parent 400-level band.

## Limitations

### Simulator

- **It is a model, not an image.** Band intensities start from the inverted NCBI grades, and each R-positive band gets a random ±12% change. Real differences between R-positive bands are not in the data, so the simulated band-to-band contrast will not match real slides exactly.
- **Heterochromatin tone is unverified.** I found no source describing how 1q12, 9q12, 16q11.2, Yq12 or the acrocentric satellites stain in RHG. The default "Pale" is an inference from heat denaturation affecting AT-rich regions more; the page lets you change it.
- **Acrocentric short arms are drawn at about half their ISCN idiogram length.** Idiograms draw them larger than they usually appear. This scaling is a judgement, not a measured value.
- **Condensation is an approximation.** It is simulated by smoothing the band profile, not by modelling chromatin.
- **Some features are missing.** The simulator does not draw twisted or crossing chromatids, splayed chromatid ends, overlapping chromosomes or nuclei.
- **Ends are darker by design.** Terminal R-positive bands are drawn slightly darker, consistent with R-banded chromosome ends being "almost always positive" ([IntechOpen](https://www.intechopen.com/chapters/75292)).

### Idiograms

- **Band intensities are schematic.** The intermediate R-band tones come from inverting NCBI's G-stain grades, not from measured RHG intensities. The source gives every G-negative band the same value, so real differences between R-positive bands, such as the strongly staining T-bands, are not shown.
- **Heterochromatin is not inverted.** Variable heterochromatin (1q12, 9q12, 16q11.2, Yq12, acrocentric p11.2 and p13) and stalks are drawn with a hatch instead of a guessed tone, because their appearance varies between individuals and preparations.
- **550-level proportions are approximate** in the seven rescaled regions listed above.
- **Detail views are not to scale with each other.** Each chromosome is drawn tall enough to fit its labels; only the karyogram uses a shared scale.
- **The finest level is GRCh38, not ISCN 850.** ISCN 2024 (section 2.4) says the GRCh38 idiograms best fit the ISCN 700-band level. GRCh38 is more detailed than ISCN at 6p24 and 9q34.1; ISCN 850 is more detailed at 1q32, 2p21, 5q13.2, 6p22.3 and 6q21. NCBI's file calls this set 850, which is why earlier versions of the site did too. The data key is still `850` for compatibility.
- **GRCh38 sub-band names are not karyotype names.** Names such as 9q34.12 exist only in GRCh38; an ISCN karyotype uses the level actually resolved, e.g. `t(9;22)(q34;q11.2)`.
- **Two ISCN levels are missing.** ISCN also defines 300- and 850-band idiograms, but they are not in the source data.
- **Gene positions are for orientation.** They are placed by interpolation within their band. Gene extents follow Ensembl's annotation, which is sometimes longer than the canonical transcript (for example CFTR shows as 7q31.2–q31.31). IGH is marked at IGHM, inside the IGH locus.

## Landmark genes

| Chr | Genes (band) |
|---|---|
| 1 | MUTYH (1p34.1), NRAS (1p13.2), CKS1B (1q21.3) |
| 2 | MYCN (2p24.3), ALK (2p23.2–p23.1), MSH2 (2p21–p16.3) |
| 3 | VHL (3p25.3), MLH1 (3p22.2), MECOM (3q26.2) |
| 4 | FGFR3 (4p16.3), KIT (4q12), TET2 (4q24) |
| 5 | APC (5q22.2), NPM1 (5q35.1), NSD1 (5q35.3) |
| 6 | DEK (6p22.3), HLA-A (6p22.1), MYB (6q23.3) |
| 7 | EGFR (7p11.2), ELN (7q11.23), CFTR (7q31.2–q31.31) |
| 8 | FGFR1 (8p11.23), RUNX1T1 (8q21.3), MYC (8q24.21) |
| 9 | JAK2 (9p24.1), CDKN2A (9p21.3), ABL1 (9q34.12) |
| 10 | RET (10q11.21), PTEN (10q23.31) |
| 11 | WT1 (11p13), CCND1 (11q13.3), ATM (11q22.3), KMT2A (11q23.3) |
| 12 | ETV6 (12p13.2), KRAS (12p12.1), PAH (12q23.2) |
| 13 | FLT3 (13q12.2), BRCA2 (13q13.1), RB1 (13q14.2) |
| 14 | SERPINA1 (14q32.13), IGH (14q32.33) |
| 15 | SNRPN (15q11.2), FBN1 (15q21.1), PML (15q24.1) |
| 16 | TSC2 (16p13.3), MYH11 (16p13.11), CBFB (16q22.1) |
| 17 | TP53 (17p13.1), NF1 (17q11.2), RARA (17q21.2), BRCA1 (17q21.31) |
| 18 | SMAD4 (18q21.2), BCL2 (18q21.33) |
| 19 | STK11 (19p13.3), LDLR (19p13.2), CEBPA (19q13.11) |
| 20 | JAG1 (20p12.2), ASXL1 (20q11.21), GNAS (20q13.32) |
| 21 | APP (21q21.3), RUNX1 (21q22.12), ERG (21q22.2) |
| 22 | TBX1 (22q11.21), BCR (22q11.23), NF2 (22q12.2) |
| X | SHOX (Xp22.33), DMD (Xp21.2–p21.1), AR (Xq12), XIST (Xq13.2), FMR1 (Xq27.3), MECP2 (Xq28) |
| Y | SRY (Yp11.2), USP9Y (Yq11.221), DAZ1 (Yq11.223) |
