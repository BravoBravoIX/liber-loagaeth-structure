"""L1: reproduce the counts published by Zubair (2026, Zenodo 10.5281/zenodo.19708274) and
explain the differences.

Claims checked:
  (1) 212,082 letters over 96 leaf-sides parsed from Peterson's edition;
  (2) per-side index of coincidence 0.044-0.101 (mean 0.082);
  (3) the Soyga rule cell[r][c] = above + f(left) mod 23 (Reeds's f) on 15 Loagaeth tables
      paired with Soyga tables 1-15 gives 3.71-5.76 % matches against a 4.35 % (1/23) baseline.

For (1)-(2): our corpus counts, and an emulation of a parse that counts every letter in the
text of each leaf's section of the web page (headings, notes and, for 48b, everything to the
end of the page, which is where Peterson prints four Book of Soyga tables).
For (3): the rule on the top-left 36 x 36 block of sides 2a ... 9a (interior cells r, c >= 2,
as for a Soyga table), with u/v folded to u and j to i (the Soyga alphabet has no v, j, w);
cells whose letters fall outside the 23-letter alphabet are skipped. Controls: the expected
rate from each table's own letter frequencies, and 10,000 random shuffles of each table's
cells (seed 20261019); a p-value per table and Holm's correction over 15.

Usage: reproduce_zubair.py CORPUS_DIR SL3189_HTM ZUBAIR_DIR   (writes results/zubair_repro.json)
ZUBAIR_DIR holds zubair_per_table_frequency.csv and zubair_soyga_vs_loagaeth_tables_1_15.csv
(Zenodo 10.5281/zenodo.19708274, CC BY 4.0; fetched by scripts/fetch_sources.sh).
"""

import csv
import html
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
from loag import ALL_SIDES, GRID_SIDES, ROOT, SEED, entropy, ic, load_cells, sha256, side_rows

ALPHA = "abcdefghiklmnopqrstuxyz"
IDX = {c: i for i, c in enumerate(ALPHA)}
F_REEDS = dict(a=2, b=2, c=3, d=5, e=14, f=2, g=6, h=5, i=14, k=15, l=20, m=22, n=14, o=8,
               p=13, q=20, r=11, s=8, t=8, u=15, x=15, y=15, z=2)
N_SHUFFLE = 10000


def page_sections(text):
    start = text.index("id=l1a>")
    pat = re.compile(r'<H\d id=l(\d+[ab])>|<A NAME="l(\d+[ab])">')
    marks = [m for m in pat.finditer(text) if m.start() >= start - 4]
    out = {}
    for i, m in enumerate(marks):
        side = m.group(1) or m.group(2)
        stop = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out[side] = text[m.start():stop]
    return out


def letters_in_html(s, drop_comments):
    if drop_comments:
        s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<[^>]*>", " ", s)
    s = html.unescape(s.replace("&3769;", "&#769;"))
    s = unicodedata.normalize("NFD", s)
    return Counter(ch.lower() for ch in s if "a" <= ch.lower() <= "z")


def soyga_test(g, rng):
    """Matches of the Soyga rule on the interior of the top-left 36 x 36 block."""
    def m(ch):
        ch = {"v": "u", "j": "i", "w": "u"}.get(ch, ch)
        return IDX.get(ch, -1)
    a = np.array([[m(g[r][c]) for c in range(36)] for r in range(36)])
    above, left, cur = a[:-1, 1:], a[1:, :-1], a[1:, 1:]
    ok = (above >= 0) & (left >= 0) & (cur >= 0)
    fl = np.array([F_REEDS[ALPHA[i]] for i in range(23)])
    pred = (above + fl[np.where(left >= 0, left, 0)]) % 23
    hits = int(((pred == cur) & ok).sum())
    n = int(ok.sum())
    # expected from the table's own frequencies: P(pred = x) * P(cur = x), x over letters
    pc = np.bincount(cur[ok], minlength=23) / n
    pp = np.bincount(pred[ok], minlength=23) / n
    expected = float((pc * pp).sum())
    # shuffle control: permute the valid letters of the block, recompute
    flat = a.flatten()
    valid = np.where(flat >= 0)[0]
    sims = np.empty(N_SHUFFLE)
    for k in range(N_SHUFFLE):
        b = flat.copy()
        b[valid] = rng.permutation(flat[valid])
        b = b.reshape(36, 36)
        ab, le, cu = b[:-1, 1:], b[1:, :-1], b[1:, 1:]
        ok2 = (ab >= 0) & (le >= 0) & (cu >= 0)
        pr = (ab + fl[np.where(le >= 0, le, 0)]) % 23
        sims[k] = ((pr == cu) & ok2).sum() / ok2.sum()
    rate = hits / n
    p_high = (1 + (sims >= rate).sum()) / (N_SHUFFLE + 1)
    p_low = (1 + (sims <= rate).sum()) / (N_SHUFFLE + 1)
    return {"cells": n, "matches": hits, "rate": rate, "expected_from_frequencies": expected,
            "shuffle_mean": float(sims.mean()), "shuffle_sd": float(sims.std()),
            "p_two_sided": min(1.0, 2 * min(p_high, p_low))}


def holm(ps):
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj = [0.0] * len(ps)
    run = 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - k) * ps[i]))
        adj[i] = run
    return adj


def main():
    corpus, page, zdir = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    cells = load_cells(corpus)
    zub = {r["leaf_id"]: r for r in csv.DictReader(open(zdir / "zubair_per_table_frequency.csv"))}
    zsoy = list(csv.DictReader(open(zdir / "zubair_soyga_vs_loagaeth_tables_1_15.csv")))
    text = page.read_text(encoding="latin-1")
    secs = page_sections(text)

    per_side = {}
    ours_total = 0
    emu_total = {True: 0, False: 0}
    for side in ALL_SIDES:
        cnt = Counter()
        for c in cells:
            if c["side"] == side:
                cnt.update(ch for ch in c["letters"] if ch.isalpha())
        ours_total += sum(cnt.values())
        emu = {d: letters_in_html(secs[side], d) for d in (True, False)}
        for d in emu:
            emu_total[d] += sum(emu[d].values())
        z = zub[side]
        per_side[side] = {
            "ours_letters": sum(cnt.values()), "ours_ic": round(ic(cnt), 6),
            "ours_entropy": round(entropy(cnt), 4),
            "emulated_letters": sum(emu[True].values()),
            "emulated_letters_with_comments": sum(emu[False].values()),
            "emulated_ic": round(ic(emu[True]), 6),
            "zubair_letters": int(z["total_letters"]), "zubair_ic": float(z["ic"]),
        }
    zic = [float(zub[s]["ic"]) for s in ALL_SIDES]
    our_ic = [per_side[s]["ours_ic"] for s in ALL_SIDES]
    exact_emu = sum(per_side[s]["emulated_letters"] == per_side[s]["zubair_letters"]
                    for s in ALL_SIDES)
    exact_emu_c = sum(per_side[s]["emulated_letters_with_comments"]
                      == per_side[s]["zubair_letters"] for s in ALL_SIDES)

    rng = np.random.default_rng(SEED)
    soy = []
    for row in zsoy:
        side = row["loagaeth_leaf"]
        rows = side_rows(cells, side, fold_letters=False)
        g = [rows[r] for r in sorted(rows)]
        res = soyga_test(g, rng)
        res.update({"soyga_table": int(row["soyga_table"]), "side": side,
                    "zubair_cells": int(row["comparison_cells"]),
                    "zubair_rate_pct": float(row["exact_match_percentage"])})
        soy.append(res)
    adj = holm([s["p_two_sided"] for s in soy])
    for s, a in zip(soy, adj, strict=True):
        s["p_holm"] = a

    out = {
        "what": "L1: reproduction of Zubair (2026) counts, IC range and Soyga-rule test",
        "seed": SEED, "shuffles": N_SHUFFLE,
        "inputs": {"cells.jsonl": sha256(corpus / "cells.jsonl"), "sl3189.htm": sha256(page),
                   "zubair_per_table_frequency.csv":
                       sha256(zdir / "zubair_per_table_frequency.csv"),
                   "zubair_soyga_vs_loagaeth_tables_1_15.csv":
                       sha256(zdir / "zubair_soyga_vs_loagaeth_tables_1_15.csv")},
        "letters": {"zubair": sum(int(zub[s]["total_letters"]) for s in ALL_SIDES),
                    "ours_corpus": ours_total,
                    "ours_grid_sides_2a_28b": sum(per_side[s]["ours_letters"] for s in GRID_SIDES),
                    "emulated_page_sections": emu_total[True],
                    "emulated_page_sections_with_comments": emu_total[False],
                    "sides_where_emulation_equals_zubair": exact_emu,
                    "sides_where_emulation_with_comments_equals_zubair": exact_emu_c},
        "ic": {"zubair_min": min(zic), "zubair_max": max(zic),
               "zubair_mean": sum(zic) / len(zic),
               "zubair_min_side": ALL_SIDES[zic.index(min(zic))],
               "ours_min": min(our_ic), "ours_max": max(our_ic),
               "ours_mean": sum(our_ic) / len(our_ic),
               "ours_min_side": ALL_SIDES[our_ic.index(min(our_ic))],
               "ours_max_side": ALL_SIDES[our_ic.index(max(our_ic))],
               "ours_mean_without_1a_1b": sum(our_ic[2:]) / len(our_ic[2:])},
        "soyga_rule": soy,
        "soyga_rule_summary": {"ours_min_pct": 100 * min(s["rate"] for s in soy),
                               "ours_max_pct": 100 * max(s["rate"] for s in soy),
                               "expected_mean_pct": 100 * float(np.mean(
                                   [s["expected_from_frequencies"] for s in soy])),
                               "tables_p_holm_below_0.05": sum(s["p_holm"] < 0.05 for s in soy)},
        "per_side": per_side,
    }
    json.dump(out, open(ROOT / "results" / "zubair_repro.json", "w"), indent=1, default=float)
    print(json.dumps({k: out[k] for k in ("letters", "ic", "soyga_rule_summary")}, indent=1,
                     default=float))
    for s in soy:
        print(s["side"], s["cells"], s["zubair_cells"], round(100 * s["rate"], 2),
              s["zubair_rate_pct"], round(100 * s["expected_from_frequencies"], 2),
              round(100 * s["shuffle_mean"], 2), s["p_two_sided"], round(s["p_holm"], 3))


if __name__ == "__main__":
    main()
