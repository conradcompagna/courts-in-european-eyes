"""Minimal reader for EEBO-TCP P5 TEI files.

Produces one record per prose block (<p>, or <item> with no <p> inside) from the
<body> of the text, with the chain of <head> elements above it and the printed
page number (<pb n=...>) on which the block begins. Front matter (<front>),
back matter (<back>) and marginal notes are excluded.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from lxml import etree

NS = {"t": "http://www.tei-c.org/ns/1.0"}
T = "{http://www.tei-c.org/ns/1.0}"


@dataclass
class Block:
    tcp_id: str
    block_no: int
    div_path: list[str]
    div_ids: list[int]
    page: str
    text: str
    kind: str = "p"
    extra: dict = field(default_factory=dict)


def _clean_head(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s[:160]


def text_of(el) -> str:
    """Flatten an element to text, honouring TCP conventions."""
    out: list[str] = []

    def walk(e):
        tag = e.tag if isinstance(e.tag, str) else ""
        if tag == T + "note":
            # marginal / editorial notes are skipped, but the tail belongs to the parent
            if e.tail:
                out.append(e.tail)
            return
        if tag == T + "gap":
            out.append(" ")
            if e.tail:
                out.append(e.tail)
            return
        if tag == T + "g":
            ref = e.get("ref", "")
            if ref in ("char:EOLhyphen", "char:EOLunhyphen"):
                out.append("\u0000")  # join marker: remove following line break
            else:
                out.append(e.text or "")
            if e.tail:
                out.append(e.tail)
            return
        if tag == T + "pb":
            if e.tail:
                out.append(e.tail)
            return
        if e.text:
            out.append(e.text)
        for c in e:
            walk(c)
        if e is not el and e.tail:
            out.append(e.tail)

    walk(el)
    s = "".join(out)
    s = re.sub(r"\u0000\s*", "", s)
    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")  # drop combining abbreviation strokes
    s = unicodedata.normalize("NFC", s)
    s = s.replace("ſ", "s").replace("•", " ").replace("〈◊〉", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def read_tcp(path: str, tcp_id: str) -> list[Block]:
    tree = etree.parse(path)
    bodies = tree.findall(".//" + T + "body")
    blocks: list[Block] = []
    page = ""
    div_counter = 0
    n = 0

    def visit(el, heads: list[str], ids: list[int]):
        nonlocal page, div_counter, n
        for c in el:
            if not isinstance(c.tag, str):
                continue
            tag = c.tag[len(T):] if c.tag.startswith(T) else c.tag
            if tag == "pb":
                page = c.get("n") or page
                continue
            if tag == "note":
                continue
            if tag == "div":
                div_counter += 1
                h = c.find(T + "head")
                head = _clean_head(text_of(h)) if h is not None else f"[{c.get('type', 'div')}]"
                visit(c, heads + [head], ids + [div_counter])
                continue
            if tag == "p" or (tag == "item" and c.find(".//" + T + "p") is None):
                # page breaks inside a block: record the page where it starts, then advance
                start_page = page
                for pb in c.iter(T + "pb"):
                    page = pb.get("n") or page
                txt = text_of(c)
                if txt:
                    n += 1
                    blocks.append(Block(tcp_id, n, heads, ids, start_page, txt, tag))
                continue
            visit(c, heads, ids)

    for b in bodies:
        # skip bodies nested inside <front>/<back> (rare) by checking ancestry
        anc = [a.tag for a in b.iterancestors()]
        if T + "front" in anc or T + "back" in anc:
            continue
        visit(b, [], [])
    return blocks
