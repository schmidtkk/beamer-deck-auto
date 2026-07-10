# Tools

## Figure Sourcing (search-first; draft is text-only)

| Tool | Purpose | Example |
|------|---------|---------|
| `figure_search.py search` | Search openly-licensed sources (Commons/Openverse), license-filtered | `python tools/figure_search.py search --query "large intestine anatomy" --limit 6` |
| `figure_search.py fetch` | Download a chosen image via the egress proxy | `python tools/figure_search.py fetch --url <thumb_url> --out assets/<deck>/x.png` |
| `figure_search.py db-add / db / db-credits` | Per-deck figure database with provenance + credit lines | `python tools/figure_search.py db-credits --db assets/<deck>/figures_db.json --latex` |
| `figure_search.py sources --ping` | List sources; auto-disable unreachable with `--disable-unreachable` | `python tools/figure_search.py sources --ping` |

Sources are configured in `tools/figure_sources.json` (enable/disable). Only PD/CC0/CC-BY/CC-BY-SA
are returned; copyrighted paper figures are never embedded — cite/link them. See the create skill's
`references/images/external-figures-licensing.md`.

## Layout Analysis & Optimization

| Tool | Purpose | Example |
|------|---------|---------|
| `check_layout.py` | Parse .tex source, output U/B/G/AR/DGV metrics per frame | `python tools/check_layout.py deck.tex build/deck.log --advise` |
| `layout_optimizer.py` | Four-layer decision tree for best layout template, generate LaTeX skeleton | `python tools/layout_optimizer.py suggest --img 1716:1124 --cards 2` |
| `auto_crop.py` | Auto-crop image white margins for better embedding scale | `python tools/auto_crop.py fig.png --padding 8` |

## Theme Validation

| Tool | Purpose | Example |
|------|---------|---------|
| `test_themes.py` | Compile-test all themes (+ optional layout stress test) | `python tools/test_themes.py` |
| `test_themes.py --layouts` | Full 5×8 layout stress test (40 compilations) | `python tools/test_themes.py --layouts` |
| `test_themes.py --theme dark` | Test single theme only | `python tools/test_themes.py --theme dark` |

## Quick Build

```powershell
# Compile single deck
.\build_clean.ps1                    # default cvgdiff-beamer
.\build_clean.ps1 template-lib-demo  # compile specific deck
.\build_clean.ps1 all                # compile all .tex files
```
