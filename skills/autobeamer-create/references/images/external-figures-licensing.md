# External figures — licensing & sourcing for publishable decks

A deck meant to be **published or used for teaching** can only ship figures that are
**legally clear and actually correct**. Two failures sink a deck: a wrong hand-drawn diagram,
and a copyrighted figure copied "with attribution" (attribution is not a license). This file
is the discipline that avoids both.

## Search first; draw only as a last resort (standing user rule)

**Searching for a real figure is the priority.** TikZ renders mathematical figures poorly, so
reach for it only when a search genuinely fails.

1. **Search the vetted sources below for an openly-licensed figure first** (PD / CC0 / CC BY).
   A real, correct figure almost always beats a hand-drawn one for math, 3-D surfaces,
   curvature, anatomy, and scientific diagrams.
2. **Only if search truly fails**, draw TikZ — and only for what it does well: simple 2-D
   schematics, flowcharts, labelled triangles/meshes, computed function plots. A wrong or
   crude TikZ figure is worse than none.
3. **Every TikZ figure is mandatory-rendered and double visual-checked** (self + Codex) — see
   the section at the bottom. No exceptions.
4. **Never** paste a figure from a copyrighted paper/journal (IEEE, ACM, Springer, Elsevier…).
   Attribution is not a license. Cite and link it, or redraw the concept yourself.

## Where to search — vetted openly-licensed sources

All verified reachable (June 2026). Prefer PD/CC0/CC BY; record license + author for every
adopted figure. **Per-item licenses vary on aggregators — always check the individual file.**

| Source | Best for | Typical license | Notes / access |
|---|---|---|---|
| [Wikimedia Commons](https://commons.wikimedia.org) | math, geometry, 3-D surfaces, science, anatomy | PD / CC0 / CC BY / CC BY-SA (per file) | richest for math; has an API (workflow below) |
| [Openverse](https://openverse.org) | CC meta-search across 800M+ works | CC / PD (per file) | aggregator; API at `api.openverse.org`; site 403s bare curl (use API/browser) |
| [Servier Medical Art (SMART)](https://smart.servier.com) | **medical / anatomy / colon / physiology** | CC BY 4.0 | 3000+ pro illustrations; credit "Servier Medical Art, CC BY 4.0" |
| [NIH BioArt Source](https://bioart.niaid.nih.gov) | biomedical / science art (NIH) | free for use, attribution requested | US-gov biomedical art library |
| [NIH Open-i](https://openi.nlm.nih.gov) | biomedical figures from open literature | **license varies per item — check each** | many source articles are © — verify before use |
| [Smithsonian Open Access](https://www.si.edu/openaccess) | science/history imagery, 3-D scans | CC0 | 5M+ items; site 403s bare curl (use API/browser) |
| [NASA images](https://images.nasa.gov) | space/physics imagery | public domain (US) | not subject to US copyright |
| [BioIcons](https://bioicons.com) · [SciDraw](https://scidraw.io) | biology vector icons / drawings (SVG) | CC0 / CC BY | clean vector clip-art for life-science schematics |
| [Openclipart](https://openclipart.org) | general clip-art / simple diagrams | public domain (CC0) | simple icons and schematics |

Search tactic: try Commons first (best math coverage + API), then Openverse (broad CC
meta-search), then the domain-specific sources (SMART/BioArt for medical, NASA/Smithsonian for
science imagery). For this repo's colon/anatomy decks, **SMART is the go-to** for anatomical art.

## Acceptable licenses (publishable product)

| License | Use | On-slide credit |
|---|---|---|
| Public Domain / CC0 | free, no strings | credit anyway (good practice) |
| CC BY | free **with attribution** | required: author + source + "CC BY x.0" |
| CC BY-SA | free with attribution **+ share-alike notice** | required; prefer CC0/CC BY when a choice exists |
| anything non-free / "fair use" / © paper | **do not embed** | link/cite only |

## Acceptable licenses (publishable product)

| License | Use | On-slide credit |
|---|---|---|
| Public Domain / CC0 | free, no strings | credit anyway (good practice) |
| CC BY | free **with attribution** | required: author + source + "CC BY x.0" |
| CC BY-SA | free with attribution **+ share-alike notice** | required; prefer CC0/CC BY when a choice exists |
| anything non-free / "fair use" / © paper | **do not embed** | link/cite only |

## Wikimedia Commons workflow (proxy required — bare curl has no egress)

```bash
P="curl -q --proxy http://127.0.0.1:8888 -sL --max-time 30"
# 1. search the File namespace (ns=6)
$P "https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srsearch=<topic>&srnamespace=6&srlimit=6"
# 2. license + author + a PNG rendering URL (iiurlwidth rasterizes SVG → PNG server-side)
$P "https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url|extmetadata|user&iiurlwidth=1000&titles=File:<Name>.svg"
#    read extmetadata: LicenseShortName, UsageTerms, Artist, AttributionRequired, LicenseUrl ; thumburl = the PNG
# 3. download the PNG rendering (not the SVG — avoids a local SVG toolchain)
$P -o assets/<deck>/<name>.png "<thumburl>"
magick identify assets/<deck>/<name>.png      # verify it's a real raster
```

Keep the **original** download for provenance and a **credits ledger** `assets/<deck>/CREDITS.md`
(file · source · author · license · file-page URL). Add a **Figure-credits** slide near the
References, and an on-slide one-line credit under each sourced figure:

```latex
{\scriptsize Figure: <Author>, \href{<file-page-url>}{Wikimedia Commons}, <license>.}
```

## Technical inclusion (avoid the overflow trap)

- `graphicx` is already loaded by `template-lib`; `\includegraphics` works. `\href` works (beamer
  loads hyperref).
- **Bound the figure by height** in a column, `\includegraphics[height=3cm]{...}`, not by width —
  a near-square image at `width=\linewidth` in a side column is taller than the frame and
  overflows. `-trim` only reclaims real whitespace; a surface that fills its canvas stays square.
- **Visually check** every embedded figure (render the page) — confirm it shows what you claim
  and is not clipped. A figure that overflows still "compiles."

## If you must use TikZ: render + double visual-check (self + Codex)

TikZ is the *fallback* (search failed). A hand-drawn math figure is the single most common way
a deck ships something subtly wrong (a "perpendicular" arrow that isn't, a marker off the curve).
So every TikZ figure clears this gate before it stays in the deck — **no exceptions**:

1. **Render it.** Compile and rasterize the page: `pdftoppm -png -r 150 -f N -l N build/deck.pdf out`.
   A figure that is geometrically wrong still *compiles* — you must look at the pixels.
2. **Self visual-check.** Open the PNG and verify the geometry actually matches the math: arrows
   land where claimed, perpendiculars are perpendicular, points lie on their curves, labels are
   on the right objects, nothing is clipped. Coordinates that *should* lie on a plotted curve must
   be **computed** (`\pgfmathsetmacro`), never hardcoded (see autobeamer-tikz).
3. **Codex cross-check.** Get an independent read via `codex:codex-rescue`: pass the TikZ source
   (and the PNG if its runtime has vision) and ask it to find geometric/mathematical errors —
   non-perpendicular "perpendiculars", wrong angle, off-curve markers, mislabeled vertices. A
   second model catches what the author's eye rationalizes away.
4. **Fix and re-render until both checks pass.** Only then does the TikZ figure stay.

If it cannot pass, that is a signal to **search harder for a real figure** (sources above), not to
ship the flawed drawing.

## Provenance is non-negotiable

Every sourced asset has a verifiable file-page URL, a recorded license, and a credit line. If you
cannot establish the license, **do not use the figure** — redraw it or cite the paper instead.
