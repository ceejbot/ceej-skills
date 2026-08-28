#!/usr/bin/env python3
"""Corpus health report for a trivia export.

Usage: stats.py <export-dir> <slug> [<old-slug> ...] [--dupes-threshold 0.34]

Reads the markdown files `trivia export` writes (YAML frontmatter + body) and
prints the numbers memory-gardening triages on: recall concentration, never-
recalled share, net-negative ratings, kind/theme tag coverage, hubs present
versus themes in use, mnemonic prefix and shape drift, alias coverage, and
lexical near-duplicate candidates. Reading files bumps no recall counters,
unlike MCP recall, so this is the safe way to look at a whole corpus.

Extra positional arguments are old project slugs; their tokens are dropped
from the near-duplicate comparison along with the current slug's.

Stdlib only. Exit code 0 always; the report is the output.
"""
import glob
import itertools
import os
import re
import sys
from collections import Counter

KINDS = ("seed", "habits", "worked", "avoid", "learned", "archive")
SPOKE_KINDS = ("worked", "avoid", "learned")
STOP = {
    "the", "a", "of", "in", "on", "to", "is", "not", "for", "and", "vs", "as",
    "at", "by", "than", "over", "with", "when", "into", "from",
}


def unquote(v):
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        inner = v[1:-1]
        return inner.replace("''", "'") if v[0] == "'" else inner.replace('\\"', '"')
    return v


def parse(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return None
    fm, body = m.group(1), m.group(2)

    def scalar(key, default=""):
        mm = re.search(r"^%s: ?(.*)$" % re.escape(key), fm, re.M)
        return unquote(mm.group(1).strip()) if mm else default

    def block(key):
        mm = re.search(r"^%s:\n((?:- .*\n?)*)" % re.escape(key), fm, re.M)
        return [unquote(ln[2:].strip()) for ln in mm.group(1).splitlines()] if mm else []

    def num(key):
        v = scalar(key, "0")
        return int(v) if v.isdigit() else 0

    return {
        "mn": scalar("mnemonic"),
        "created": scalar("created_at")[:10],
        "rc": num("recall_count"),
        "uc": num("useful_count"),
        "nc": num("not_useful_count"),
        "tags": block("tags"),
        "aliases": block("mnemonics"),
        "links": "links:" in fm,
        "size": len(body),
        "file": os.path.basename(path),
    }


def main():
    args = [a for a in sys.argv[1:]]
    thr = 0.34
    if "--dupes-threshold" in args:
        i = args.index("--dupes-threshold")
        if i + 1 < len(args):
            try:
                thr = float(args[i + 1])
            except ValueError:
                pass
            del args[i:i + 2]
        else:
            del args[i]
    if len(args) < 2:
        print(__doc__)
        return
    export_dir, slug, old_slugs = args[0], args[1], args[2:]

    rows = [r for r in (parse(p) for p in sorted(glob.glob(os.path.join(export_dir, "*.md")))) if r]
    n = len(rows)
    if not n:
        print("no memories found in", export_dir)
        return
    project_tag = "project:" + slug
    slug_tokens = set()
    for s in [slug, *old_slugs]:
        slug_tokens |= set(re.split(r"[^a-z0-9]+", s.lower()))
    drop = STOP | slug_tokens | set(KINDS) | {"general"}

    def tokens(mn):
        return {t for t in re.split(r"[^a-z0-9]+", mn.lower()) if len(t) > 2 and t not in drop}

    def kind_of(r):
        ks = [t for t in r["tags"] if t in KINDS]
        return ks[0] if len(ks) == 1 else None

    def section(title):
        print("\n## " + title)

    print("# memory health: %s (%d memories)" % (slug, n))
    print("created by month:", ", ".join("%s=%d" % kv for kv in sorted(Counter(r["created"][:7] for r in rows).items())))

    section("recall concentration")
    never = sum(1 for r in rows if r["rc"] == 0)
    print("never recalled: %d (%d%%)" % (never, 100 * never // n))
    for k in (1, 3, 10, 100):
        print("recalled >= %-3d: %d" % (k, sum(1 for r in rows if r["rc"] >= k)))
    total_rc = sum(r["rc"] for r in rows) or 1
    top = sorted(rows, key=lambda r: -r["rc"])[:15]
    print("top 15 carry %d%% of all recalls:" % (100 * sum(r["rc"] for r in top) // total_rc))
    for r in top:
        print("  rc=%4d  +%-3d -%-3d %s" % (r["rc"], r["uc"], r["nc"], r["mn"]))

    section("net-negative ratings (archive or rewrite candidates)")
    neg = [r for r in rows if r["nc"] > r["uc"]]
    for r in sorted(neg, key=lambda r: r["uc"] - r["nc"]):
        print("  rc=%4d  +%-3d -%-3d %s" % (r["rc"], r["uc"], r["nc"], r["mn"]))
    if not neg:
        print("  none")

    section("mnemonic shape")
    on_prefix = re.compile(r"^(%s|general)/" % re.escape(slug))
    taxonomy = re.compile(
        r"^(?:%s/(?:overview|conventions|current-focus|trivia-bootstrapped)$"
        r"|%s/(?:habits|worked|avoid|learned|history)/.+"
        r"|general/habits/.+)$" % (re.escape(slug), re.escape(slug)))
    off_prefix = [r for r in rows if not on_prefix.match(r["mn"])]
    off_shape = [r for r in rows if on_prefix.match(r["mn"]) and not taxonomy.match(r["mn"])]
    print("off-prefix mnemonics (rename candidates): %d" % len(off_prefix))
    for r in off_prefix[:20]:
        print("  " + r["mn"])
    if len(off_prefix) > 20:
        print("  … %d more" % (len(off_prefix) - 20))
    print("on-prefix but outside the taxonomy shapes (reshape candidates): %d" % len(off_shape))
    for r in off_shape[:20]:
        print("  " + r["mn"])
    shapes = Counter()
    for r in rows:
        mm = re.match(r"^(?:%s|general)/([a-z-]+)/" % re.escape(slug), r["mn"])
        if mm:
            shapes[mm.group(1)] += 1
        elif on_prefix.match(r["mn"]):
            shapes["seed-or-flat"] += 1
        else:
            shapes["off-prefix"] += 1
    print("by shape:", dict(shapes.most_common()))

    section("tag coverage")
    print("missing %s: %d" % (project_tag, sum(1 for r in rows if project_tag not in r["tags"] and not r["mn"].startswith("general/"))))
    kind_counts = Counter(len([t for t in r["tags"] if t in KINDS]) for r in rows)
    print("kind tags per memory (want exactly 1):", dict(sorted(kind_counts.items())))
    themed_kinds = ("habits",) + SPOKE_KINDS
    need_theme = [r for r in rows if kind_of(r) in themed_kinds]
    have_theme = [r for r in need_theme if sum(1 for t in r["tags"] if t.startswith("theme:")) == 1]
    print("hubs+spokes with exactly one theme: tag: %d / %d" % (len(have_theme), len(need_theme)))
    spoke_themes = Counter(t for r in rows if kind_of(r) in SPOKE_KINDS for t in r["tags"] if t.startswith("theme:"))
    print("spokes per theme:", dict(spoke_themes.most_common()) or "(no theme tags yet)")
    general = Counter(t for r in rows for t in r["tags"] if t.startswith("general:"))
    print("general: tags:", dict(general.most_common()) or "none")
    other = Counter(
        t for r in rows for t in r["tags"]
        if t != project_tag and t not in KINDS and not t.startswith(("theme:", "general:"))
    )
    print("other tags (top 20):", other.most_common(20) or "none")

    section("hubs")
    hubs = sorted(r["mn"] for r in rows if re.match(r"^(?:%s|general)/habits/" % re.escape(slug), r["mn"]))
    print("present:", hubs or "none")
    hub_themes = {h.rsplit("/", 1)[1] for h in hubs}
    want = {t.split(":", 1)[1] for t in spoke_themes}
    if spoke_themes:
        print("themes in use with no hub:", sorted(want - hub_themes) or "none")
    else:
        print("themes in use with no hub: (no theme tags yet)")
    big = [(t, c) for t, c in spoke_themes.items() if c > 20]
    print("themes over 20 spokes (split candidates):", big or "none")

    section("findability")
    spokes = [r for r in rows if kind_of(r) in SPOKE_KINDS or re.search(r"/(worked|avoid|learned)/", r["mn"])]
    no_alias = [r for r in spokes if not r["aliases"]]
    print("spokes: %d; without aliases: %d; without links: %d" % (
        len(spokes), len(no_alias), sum(1 for r in spokes if not r["links"])))

    section("lexical near-duplicate candidates (jaccard on mnemonic tokens >= %.2f)" % thr)
    toks = {r["mn"]: tokens(r["mn"]) for r in rows}
    pairs = []
    for a, b in itertools.combinations(rows, 2):
        ta, tb = toks[a["mn"]], toks[b["mn"]]
        if not ta or not tb:
            continue
        inter = len(ta & tb)
        if inter >= 2 and inter / len(ta | tb) >= thr:
            pairs.append((inter / len(ta | tb), a, b))
    for j, a, b in sorted(pairs, key=lambda p: -p[0]):
        print("  %.2f  [rc %3d] %s\n        [rc %3d] %s" % (j, a["rc"], a["mn"], b["rc"], b["mn"]))
    if not pairs:
        print("  none — semantic duplicates (same lesson, different words) need the per-theme read")
    print("\nlexical pairs: %d. This undercounts: the per-theme read in step 5 finds the rest." % len(pairs))


if __name__ == "__main__":
    main()
