"""Build the passage corpus from the EEBO-TCP XML files.

Output
------
data/passages_all.csv.gz every passage from every unit (about 10k)
data/passages_court.csv  the analysis corpus: passages that are about a ruler or
                         court AND can be attributed to one court
data/sources.csv         one row per source unit with bibliographic metadata

Steps (each is documented in data/README.md):
1. read <body> prose blocks with their heading chain and page number
2. keep the blocks that belong to each unit (heading include/exclude rules)
3. segment into passages of roughly 90-170 words, never crossing a chapter
4. attribute each passage to a court (gazetteer over a 3-passage window, with
   a unit-level default that the gazetteer can override)
5. score court vocabulary and keep passages above threshold
"""
from __future__ import annotations

import csv
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from normalise import change_rate, normalise  # noqa: E402
from sources import COURT_CORE, COURT_SECONDARY, GAZETTEER, UNITS  # noqa: E402
from tei import read_tcp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XML = os.path.join(ROOT, "data", "tcp_xml")
OUT = os.path.join(ROOT, "data")

MIN_W, TARGET_W, MAX_W = 90, 140, 170
GAZ = {k: re.compile(v, re.I) for k, v in GAZETTEER.items()}
CORE = re.compile(COURT_CORE)
SEC = re.compile(COURT_SECONDARY)

SENT = re.compile(r"(?<=[.;:?!])\s+(?=[A-Z])")


def split_long(text: str) -> list[str]:
    """Split a long block at sentence boundaries into chunks near TARGET_W words."""
    sents = SENT.split(text)
    chunks, cur = [], []
    for s in sents:
        w = s.split()
        # a single overlong 'sentence' (common in period prose): hard-split on words
        while len(w) > MAX_W:
            if cur:
                chunks.append(" ".join(cur)); cur = []
            chunks.append(" ".join(w[:TARGET_W])); w = w[TARGET_W:]
        if cur and len(cur) + len(w) > MAX_W:
            chunks.append(" ".join(cur)); cur = []
        cur.extend(w)
        if len(cur) >= TARGET_W:
            chunks.append(" ".join(cur)); cur = []
    if cur:
        if chunks and len(cur) < MIN_W // 2:
            chunks[-1] = chunks[-1] + " " + " ".join(cur)
        else:
            chunks.append(" ".join(cur))
    return chunks


def unit_blocks(unit, blocks):
    inc = re.compile(unit["include"]) if unit["include"] else None
    exc = re.compile(unit["exclude"]) if unit["exclude"] else None
    lo, hi = unit.get("block_from", 0), unit.get("block_to", 10 ** 9)
    for b in blocks:
        if not (lo <= b.block_no <= hi):
            continue
        path = " || ".join(b.div_path)
        if inc and not inc.search(path):
            continue
        if exc and exc.search(path):
            continue
        yield b


def segment(unit, blocks):
    """Merge short blocks / split long ones, never crossing a chapter (top 3 heads)."""
    passages = []
    buf, buf_page, buf_key, buf_path = [], None, None, None

    def flush():
        nonlocal buf, buf_page, buf_key, buf_path
        if buf:
            text = " ".join(buf)
            for chunk in split_long(text) if len(text.split()) > MAX_W else [text]:
                passages.append(dict(page=buf_page, section=buf_path, text=chunk))
        buf, buf_page, buf_key, buf_path = [], None, None, None

    for b in blocks:
        key = tuple(b.div_ids[:3])
        if buf and key != buf_key:
            flush()
        if not buf:
            buf_page, buf_key = b.page, key
            buf_path = " > ".join(h for h in b.div_path[1:3]) or (b.div_path[0] if b.div_path else "")
        buf.append(b.text)
        if sum(len(x.split()) for x in buf) >= TARGET_W:
            flush()
    flush()
    # drop fragments (tables, captions, list items of a few words)
    return [p for p in passages if len(p["text"].split()) >= 40]


def gaz_counts(text):
    return {k: len(r.findall(text)) for k, r in GAZ.items()}


def attribute(unit, passages):
    counts = [gaz_counts(p["text"]) for p in passages]
    for i, p in enumerate(passages):
        window = Counter()
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(passages):
                w = 2 if j == i else 1  # the passage itself counts double
                for k, v in counts[j].items():
                    window[k] += w * v
        total = sum(window.values())
        top, top_n = (window.most_common(1)[0] if total else (None, 0))
        share = top_n / total if total else 0.0
        default = unit["default_court"]
        if default:
            # single-court account: the court is the one at which the observer was present,
            # even when a passage mentions other rulers (e.g. a Mughal envoy at the Qing court)
            court, how = default, "unit (single-court account)"
        elif total >= 2 and share >= 0.6 and top_n >= 2:
            court, how = top, "gazetteer"
        else:
            court, how = "", "unassigned"
        p["court"], p["court_basis"] = court, how
        p["gaz_hits"] = ";".join(f"{k}:{v}" for k, v in counts[i].items() if v)


def court_score(norm_text):
    t = norm_text.lower()
    n = max(len(t.split()), 1)
    core = CORE.findall(t)
    sec = SEC.findall(t)
    return len(core), len(sec), round(100 * (len(core) * 2 + len(sec)) / n, 2)


def main():
    cache = {}
    all_rows = []
    for u in UNITS:
        if u["tcp"] not in cache:
            cache[u["tcp"]] = read_tcp(os.path.join(XML, u["tcp"] + ".xml"), u["tcp"])
        blocks = list(unit_blocks(u, cache[u["tcp"]]))
        passages = segment(u, blocks)
        attribute(u, passages)
        for k, p in enumerate(passages, 1):
            norm = normalise(p["text"])
            c, s, dens = court_score(norm)
            all_rows.append(dict(
                pid=f"{u['unit']}-{k:04d}", unit=u["unit"], author=u["author"], tcp=u["tcp"],
                page=p["page"], section=p["section"][:200], court=p["court"], court_basis=p["court_basis"],
                gaz_hits=p["gaz_hits"], n_words=len(p["text"].split()), court_core=c, court_secondary=s,
                court_density=dens, ortho_change=round(change_rate(p["text"]), 3),
                text=p["text"], text_norm=norm))
        print(f"{u['unit']:20s} blocks={len(blocks):5d} passages={len(passages):5d}")

    # analysis corpus: attributed to a court, and about rulers/courts
    keep = [r for r in all_rows if r["court"] and r["court_core"] >= 2 and r["court_density"] >= 5.0]
    fields = list(all_rows[0].keys())
    import gzip
    for name, rows in (("passages_all.csv.gz", all_rows), ("passages_court.csv", keep)):
        opener = gzip.open if name.endswith(".gz") else open
        with opener(os.path.join(OUT, name), "wt", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
    with open(os.path.join(OUT, "sources.csv"), "w", newline="", encoding="utf-8") as f:
        cols = ["unit", "author", "observer", "orig_lang", "translator", "vehicle", "pub", "visit", "role",
                "tcp", "default_court", "include", "exclude"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for u in UNITS:
            w.writerow({c: u.get(c) if u.get(c) is not None else "" for c in cols})
    print("all passages:", len(all_rows), " court passages:", len(keep))
    print(Counter((r["court"]) for r in keep).most_common())
    print(Counter((r["unit"]) for r in keep).most_common())


if __name__ == "__main__":
    main()
