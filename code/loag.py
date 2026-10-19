"""Shared helpers for the Loagaeth study: load the corpus, build grids, basic statistics."""

import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SEED = 20261019
GRID_SIDES = [f"{n}{f}" for n in range(2, 29) for f in "ab"]  # 54 full 49 x 49 tables
CENTRE_SIDES = [f"{n}{f}" for n in range(29, 49) for f in "ab"]  # 40 partly filled tables
ALL_SIDES = ["1a", "1b"] + GRID_SIDES + CENTRE_SIDES


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_cells(corpus_dir):
    out = []
    with open(Path(corpus_dir) / "cells.jsonl") as f:
        for line in f:
            out.append(json.loads(line))
    return out


def fold(ch):
    """Letter folding used for statistics: lower case; u and v are one letter (v), j is i.
    Digits and anything else return None."""
    if not ch.isalpha():
        return None
    ch = ch.lower()
    return {"u": "v", "j": "i", "w": "v"}.get(ch, ch)


def side_rows(cells, side, fold_letters=True):
    """Rows of a side as lists of single symbols (one per cell; a multi-letter cell keeps its
    first letter, digits are kept as '#'). Returns {row: [symbols in column order]}."""
    rows = {}
    for c in cells:
        if c["side"] != side:
            continue
        s = c["letters"]
        sym = "#" if (s and s[0].isdigit()) else (fold(s[0]) if fold_letters else s[0])
        rows.setdefault(c["row"], []).append(sym)
    return rows


def grid(cells, side):
    """49 x 49 list of lists for a full grid side, or None if any row is not 49 cells."""
    rows = side_rows(cells, side)
    if len(rows) != 49 or any(len(r) != 49 for r in rows.values()):
        return None
    return [rows[r] for r in sorted(rows)]


def ic(counter):
    n = sum(counter.values())
    return sum(v * (v - 1) for v in counter.values()) / (n * (n - 1)) if n > 1 else float("nan")


def entropy(counter):
    n = sum(counter.values())
    return -sum(v / n * math.log2(v / n) for v in counter.values() if v)


def letters_of(cells, side=None, fold_letters=False):
    c = Counter()
    for r in cells:
        if side is not None and r["side"] != side:
            continue
        for ch in r["letters"]:
            if ch.isalpha():
                c[fold(ch) if fold_letters else ch] += 1
    return c
