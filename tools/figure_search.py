#!/usr/bin/env python3
"""
figure_search.py — search & adopt openly-licensed external figures for AutoBeamer
=================================================================================

Decks are drafted as TEXT first; figures are sourced separately and inserted
afterward. This tool hardens that "search a real figure first" procedure
(autobeamer-tikz Rule 0 / external-figures-licensing.md):

    1. SEARCH openly-licensed sources (Wikimedia Commons, Openverse) by topic,
       filtered to publishable licenses (PD / CC0 / CC BY / CC BY-SA).
    2. FETCH a chosen image locally (via the egress proxy).
    3. Record it in a per-deck FIGURE DATABASE (figures_db.json) with full
       provenance, so credits + the figure-proposal workflow are reproducible.

Dependency-free (stdlib only) and proxy-aware, matching the other tools/.
Programmatic sources are configured in ``figure_sources.json`` and can be
enabled/disabled (or auto-disabled when unreachable).

Subcommands
-----------
    sources [--ping] [--disable-unreachable]
    search  --query Q [--sources commons,openverse] [--licenses pd,cc0,by,by-sa]
            [--limit N] [--json]
    fetch   --url URL --out PATH
    commons-info --file "File:Name.svg" [--width N]
    db-add  --db PATH --local PATH --source S --title T --author A --license L
            [--license-url U] [--file-page P] [--query Q] [--slide S] [--status adopted]
    db      --db PATH               (list)
    db-credits --db PATH [--latex]  (emit credit lines / CREDITS.md rows)

Examples
--------
    python3 tools/figure_search.py search --query "large intestine anatomy" --limit 6
    python3 tools/figure_search.py fetch --url <thumb_url> --out assets/colon-en/colon.png
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(HERE, "figure_sources.json")

# license short-name / code -> normalized token
_ALLOWED = ("pd", "cc0", "by", "by-sa")


def _now() -> str:
    return _dt.date.today().isoformat()


def load_config(path: str = DEFAULT_CONFIG) -> dict:
    if not os.path.exists(path):
        return _DEFAULT_SOURCES
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


_DEFAULT_SOURCES = {
    "proxy": "http://127.0.0.1:8888",
    "user_agent": "autobeamer-figuresearch/1.0 (educational deck building)",
    "allowed_licenses": list(_ALLOWED),
    "sources": [
        {"name": "wikimedia_commons", "kind": "commons", "enabled": True,
         "api": "https://commons.wikimedia.org/w/api.php",
         "note": "best for math/science/anatomy; PD/CC0/CC-BY/CC-BY-SA per file"},
        {"name": "openverse", "kind": "openverse", "enabled": True,
         "api": "https://api.openverse.org/v1/images/",
         "note": "CC meta-search aggregator (800M+)"},
    ],
}


def _opener(cfg: dict):
    proxy = cfg.get("proxy") or os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    handlers = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    op = urllib.request.build_opener(*handlers)
    ua = cfg.get("user_agent", "autobeamer-figuresearch/1.0")
    op.addheaders = [("User-Agent", ua)]
    return op


def _get_json(cfg: dict, url: str, timeout: int = 30) -> dict:
    op = _opener(cfg)
    with op.open(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _strip_html(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def _norm_license(short: str) -> str | None:
    """Map a license short-name/code to a normalized token in _ALLOWED, else None."""
    s = (short or "").strip().lower()
    if not s:
        return None
    if "cc0" in s or "zero" in s:
        return "cc0"
    if "public domain" in s or s in ("pd", "pdm", "public-domain"):
        return "pd"
    # CC BY-SA before CC BY
    if "by-sa" in s or ("by" in s and "sa" in s and "nc" not in s and "nd" not in s):
        return "by-sa"
    if "nc" in s or "nd" in s:  # non-commercial / no-derivatives are NOT publishable here
        return None
    if "by" in s:
        return "by"
    return None


# --------------------------------------------------------------------------- #
# Wikimedia Commons
# --------------------------------------------------------------------------- #
def commons_search(cfg: dict, api: str, query: str, limit: int) -> list[dict]:
    q = urllib.parse.urlencode({
        "action": "query", "format": "json", "list": "search",
        "srsearch": query, "srnamespace": 6, "srlimit": max(1, limit) * 2,
    })
    data = _get_json(cfg, f"{api}?{q}")
    titles = [s["title"] for s in data.get("query", {}).get("search", [])]
    return commons_info(cfg, api, titles, width=1000, allowed=cfg.get("allowed_licenses", _ALLOWED))[:limit]


def commons_info(cfg: dict, api: str, titles: list[str], width: int, allowed) -> list[dict]:
    if not titles:
        return []
    out = []
    # batch in groups of 25 (API limit for titles)
    for i in range(0, len(titles), 25):
        batch = titles[i:i + 25]
        q = urllib.parse.urlencode({
            "action": "query", "format": "json", "prop": "imageinfo",
            "iiprop": "url|extmetadata|size", "iiurlwidth": width,
            "titles": "|".join(batch),
        })
        data = _get_json(cfg, f"{api}?{q}")
        for _, page in data.get("query", {}).get("pages", {}).items():
            ii = (page.get("imageinfo") or [{}])[0]
            em = ii.get("extmetadata", {})
            lic = _norm_license(em.get("LicenseShortName", {}).get("value", ""))
            if lic is None or lic not in allowed:
                continue
            out.append({
                "source": "wikimedia_commons",
                "title": page.get("title", ""),
                "license": lic,
                "license_short": em.get("LicenseShortName", {}).get("value", ""),
                "license_url": em.get("LicenseUrl", {}).get("value", ""),
                "author": _strip_html(em.get("Artist", {}).get("value", "")) or "(unknown)",
                "file_page": ii.get("descriptionurl", ""),
                "thumb_url": ii.get("thumburl", ""),
                "width": ii.get("thumbwidth") or ii.get("width"),
                "height": ii.get("thumbheight") or ii.get("height"),
            })
    return out


# --------------------------------------------------------------------------- #
# Openverse
# --------------------------------------------------------------------------- #
def openverse_search(cfg: dict, api: str, query: str, limit: int) -> list[dict]:
    q = urllib.parse.urlencode({
        "q": query, "license": "cc0,pdm,by,by-sa",
        "page_size": max(1, min(limit, 20)),
    })
    data = _get_json(cfg, f"{api}?{q}")
    out = []
    for r in data.get("results", []):
        lic = _norm_license(r.get("license", ""))
        if lic is None or lic not in cfg.get("allowed_licenses", _ALLOWED):
            continue
        out.append({
            "source": "openverse",
            "title": (r.get("title") or "")[:120],
            "license": lic,
            "license_short": f'{r.get("license","").upper()} {r.get("license_version","")}'.strip(),
            "license_url": r.get("license_url", ""),
            "author": r.get("creator") or "(unknown)",
            "file_page": r.get("foreign_landing_url", ""),
            "thumb_url": r.get("url", ""),  # full image; .thumbnail also available
            "width": r.get("width"),
            "height": r.get("height"),
        })
    return out[:limit]


# --------------------------------------------------------------------------- #
# commands
# --------------------------------------------------------------------------- #
def cmd_sources(args, cfg):
    changed = False
    for s in cfg.get("sources", []):
        line = f'  [{"x" if s.get("enabled") else " "}] {s["name"]:22s} kind={s["kind"]:9s} {s.get("note","")}'
        if args.ping and s.get("kind") in ("commons", "openverse") and s.get("enabled"):
            ok = _ping(cfg, s)
            line += "   -> " + ("REACHABLE" if ok else "UNREACHABLE")
            if not ok and args.disable_unreachable:
                s["enabled"] = False
                changed = True
                line += " (disabled)"
        print(line)
    if changed and args.disable_unreachable:
        with open(args.config, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        print(f"updated {args.config}")


def _ping(cfg, s) -> bool:
    try:
        if s["kind"] == "commons":
            commons_search(cfg, s["api"], "test", 1)
        elif s["kind"] == "openverse":
            openverse_search(cfg, s["api"], "test", 1)
        return True
    except Exception:
        return False


def cmd_search(args, cfg):
    want = set((args.sources or "commons,openverse").split(","))
    licenses = (args.licenses or ",".join(cfg.get("allowed_licenses", _ALLOWED))).split(",")
    cfg["allowed_licenses"] = licenses
    results, errors = [], []
    for s in cfg.get("sources", []):
        if not s.get("enabled"):
            continue
        kind = s["kind"]
        key = "commons" if kind == "commons" else ("openverse" if kind == "openverse" else None)
        if key is None or key not in want:
            continue
        try:
            if kind == "commons":
                results += commons_search(cfg, s["api"], args.query, args.limit)
            elif kind == "openverse":
                results += openverse_search(cfg, s["api"], args.query, args.limit)
        except Exception as e:
            errors.append(f'{s["name"]}: {type(e).__name__}: {str(e)[:80]} (consider disabling)')
    if args.json:
        print(json.dumps({"query": args.query, "results": results, "errors": errors},
                         ensure_ascii=False, indent=2))
        return
    print(f'== {len(results)} openly-licensed candidates for: "{args.query}" ==')
    for i, r in enumerate(results, 1):
        print(f'[{i}] {r["source"]} · {r["license"].upper()} · {r["author"]}')
        print(f'    {r["title"]}')
        print(f'    file: {r["file_page"]}')
        print(f'    img : {r["thumb_url"]}  ({r.get("width")}x{r.get("height")})')
    for e in errors:
        print("  ! " + e)


def _open_image(op, url):
    """Open an image URL; auto-retry Commons thumbnails at a valid size on HTTP 400."""
    try:
        return op.open(url, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code == 400 and "upload.wikimedia.org" in url and re.search(r"/\d+px-", url):
            fixed = re.sub(r"/\d+px-", "/1280px-", url)
            if fixed != url:
                print(f"  (Commons rejected that thumb size; retrying at 1280px)", file=sys.stderr)
                return op.open(fixed, timeout=60)
        raise


def cmd_fetch(args, cfg):
    op = _opener(cfg)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with _open_image(op, args.url) as r:
        ctype = r.headers.get("Content-Type", "")
        data = r.read()
    if not (ctype.startswith("image/") or args.out.lower().endswith((".png", ".jpg", ".jpeg", ".svg"))):
        print(f"WARNING: content-type is {ctype!r} — not obviously an image", file=sys.stderr)
    with open(args.out, "wb") as f:
        f.write(data)
    print(f"saved {args.out} ({len(data)} bytes, {ctype})")


def cmd_commons_info(args, cfg):
    api = next((s["api"] for s in cfg["sources"] if s["kind"] == "commons"),
               "https://commons.wikimedia.org/w/api.php")
    rows = commons_info(cfg, api, [args.file], width=args.width, allowed=_ALLOWED)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


def _load_db(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"figures": []}


def cmd_db_add(args, cfg):
    db = _load_db(args.db)
    fid = f"fig-{len(db['figures'])+1:03d}"
    db["figures"].append({
        "id": fid, "query": args.query or "", "source": args.source,
        "title": args.title, "author": args.author, "license": args.license,
        "license_url": args.license_url or "", "file_page": args.file_page or "",
        "local_path": args.local, "slide": args.slide or "", "status": args.status,
        "retrieved": _now(),
    })
    os.makedirs(os.path.dirname(os.path.abspath(args.db)) or ".", exist_ok=True)
    with open(args.db, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"{args.db}: added {fid} ({args.source}, {args.license})")


def cmd_db(args, cfg):
    db = _load_db(args.db)
    for fz in db["figures"]:
        print(f'{fz["id"]}  [{fz["status"]}] {fz["license"].upper():6s} {fz["source"]:18s} '
              f'{fz["local_path"]}  <- {fz.get("slide","")}')


def cmd_db_credits(args, cfg):
    db = _load_db(args.db)
    for fz in db["figures"]:
        if fz["status"] != "adopted":
            continue
        if args.latex:
            print(r"{\scriptsize Figure: %s, \href{%s}{%s}, %s.}" % (
                fz["author"], fz["file_page"] or fz["license_url"],
                fz["source"].replace("_", " ").title(), fz["license"].upper()))
        else:
            print(f'| {os.path.basename(fz["local_path"])} | {fz["source"]} | {fz["author"]} '
                  f'| {fz["license"].upper()} | {fz["file_page"]} |')


def main(argv=None):
    p = argparse.ArgumentParser(description="Search & adopt openly-licensed figures for AutoBeamer decks.")
    p.add_argument("--config", default=DEFAULT_CONFIG)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("sources"); s.add_argument("--ping", action="store_true")
    s.add_argument("--disable-unreachable", action="store_true"); s.set_defaults(fn=cmd_sources)

    s = sub.add_parser("search")
    s.add_argument("--query", required=True); s.add_argument("--sources")
    s.add_argument("--licenses"); s.add_argument("--limit", type=int, default=6)
    s.add_argument("--json", action="store_true"); s.set_defaults(fn=cmd_search)

    s = sub.add_parser("fetch")
    s.add_argument("--url", required=True); s.add_argument("--out", required=True)
    s.set_defaults(fn=cmd_fetch)

    s = sub.add_parser("commons-info")
    s.add_argument("--file", required=True); s.add_argument("--width", type=int, default=1000)
    s.set_defaults(fn=cmd_commons_info)

    s = sub.add_parser("db-add")
    for a in ("--db", "--local", "--source", "--title", "--author", "--license"):
        s.add_argument(a, required=True)
    s.add_argument("--license-url"); s.add_argument("--file-page")
    s.add_argument("--query"); s.add_argument("--slide")
    s.add_argument("--status", default="adopted"); s.set_defaults(fn=cmd_db_add)

    s = sub.add_parser("db"); s.add_argument("--db", required=True); s.set_defaults(fn=cmd_db)

    s = sub.add_parser("db-credits"); s.add_argument("--db", required=True)
    s.add_argument("--latex", action="store_true"); s.set_defaults(fn=cmd_db_credits)

    args = p.parse_args(argv)
    cfg = load_config(args.config)
    args.fn(args, cfg)


if __name__ == "__main__":
    main()
