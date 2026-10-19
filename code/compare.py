"""L0 cross-check: Peterson's edition (our corpus) against the lorselq grids, cell by cell.

Optional: not part of code/run_all.sh. The lorselq files carry no licence and are not
redistributed; fetch them with WITH_LORSELQ=1 scripts/fetch_sources.sh.

Witnesses: our parse of Peterson (cells.jsonl) and lorselq/enochian_language_modeling leaf JSONs
(commit 0e296b4): sides 2a-16b, and "1c" (= the single-letter rows at the end of Peterson's 1b).

Each row is aligned on its sequence of letters (lower case, accents removed; digits kept) with
difflib, so that one extra or missing cell does not count as a run of 48 substitutions.
Differences:
  substitution   both witnesses have a symbol at the position and they differ
                 (sub-types: u/v, i/j/y, other)
  peterson_only  a symbol in Peterson that lorselq lacks (or lorselq has [NULL]/[LACUNA])
  lorselq_only   a symbol in lorselq that Peterson lacks
Marks compared at aligned equal positions: accent present, '?' (uncertain), '.' (word end).
Case is compared separately (capital in one witness only).

Writes results/witness_compare.json (counts, rates, and every letter disagreement as a short
cell reference with the two readings).
Usage: compare.py CORPUS_DIR LORSELQ_DIR
"""

import difflib
import hashlib
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def norm(cell):
    base = "".join(ch for ch in unicodedata.normalize("NFD", cell) if ch.isalnum())
    return base.lower()


def lorselq_cells(line):
    out = []
    for raw in line.split("|"):
        flags = set()
        s = raw
        if "[sic]" in s:
            flags.add("sic")
            s = s.replace("[sic]", "")
        if "[NULL]" in s or "[LACUNA]" in s:
            flags.add("lacuna" if "[LACUNA]" in s else "null")
            s = s.replace("[NULL]", "").replace("[LACUNA]", "")
        nfd = unicodedata.normalize("NFD", s)
        if any(unicodedata.combining(ch) for ch in nfd):
            flags.add("accent")
        if "?" in s:
            flags.add("uncertain")
        if "." in s:
            flags.add("word_end")
        letters = norm(s)
        capital = any(ch.isupper() for ch in s)
        if not letters:
            out.append({"sym": None, "flags": flags, "capital": False})
            continue
        for k, ch in enumerate(letters):  # a multi-letter cell counts as several symbols
            out.append({"sym": ch, "flags": flags if k == len(letters) - 1 else set(),
                        "capital": capital and k == 0})
    return out


def kind(a, b):
    pair = {a, b}
    if pair == {"u", "v"}:
        return "u/v"
    if pair <= {"i", "j", "y"}:
        return "i/j/y"
    return "other"


def main():
    corpus, lq = Path(sys.argv[1]), Path(sys.argv[2])
    pet = defaultdict(lambda: defaultdict(list))
    for line in open(corpus / "cells.jsonl"):
        r = json.loads(line)
        if r["layout"] != "grid":
            continue
        side = r["side"]
        row = r["row"]
        if side == "1b":
            side, row = "1c", row - 31  # 1b's single-letter rows follow its 31 word rows
        for k, ch in enumerate(r["letters"]):
            fl = set()
            last = k == len(r["letters"]) - 1
            if any(f.startswith("accent") for f in r["flags"]) and last:
                fl.add("accent")
            if "uncertain" in r["flags"] and last:
                fl.add("uncertain")
            if "word_end" in r["flags"] and last:
                fl.add("word_end")
            pet[side][row].append({"sym": ch, "flags": fl, "col": r["col"],
                                   "capital": "capital" in r["flags"] and k == 0})
    tot = Counter()
    by_side = {}
    diffs = []
    mark = Counter()
    sides = ["1c"] + [f"{n}{f}" for n in range(2, 17) for f in "ab"]
    for side in sides:
        fn = lq / f"leaf{int(side[:-1]):02d}{side[-1]}.json"
        grid = json.load(open(fn))["grid_lines"]
        st = Counter()
        for rno, line in enumerate(grid, 1):
            L = lorselq_cells(line)
            P = pet[side].get(rno, [])
            st["lq_null_cells"] += sum(1 for c in L if c["sym"] is None)
            Ls = [c for c in L if c["sym"] is not None]
            a = [c["sym"] for c in P]
            b = [c["sym"] for c in Ls]
            st["peterson_symbols"] += len(a)
            st["lorselq_symbols"] += len(b)
            sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
            for op, i1, i2, j1, j2 in sm.get_opcodes():
                if op == "equal":
                    for i, j in zip(range(i1, i2), range(j1, j2), strict=True):
                        st["equal"] += 1
                        for m in ("accent", "uncertain", "word_end"):
                            x, y = m in P[i]["flags"], m in Ls[j]["flags"]
                            if x != y:
                                mark[(m, "peterson" if x else "lorselq")] += 1
                                st["mark_" + m] += 1
                        if P[i]["capital"] != Ls[j]["capital"]:
                            mark[("capital", "peterson" if P[i]["capital"] else "lorselq")] += 1
                            st["mark_capital"] += 1
                    continue
                n = min(i2 - i1, j2 - j1) if op == "replace" else 0
                for t in range(n):
                    p, q = P[i1 + t], Ls[j1 + t]
                    k = kind(p["sym"], q["sym"])
                    st["substitution"] += 1
                    st["sub_" + k] += 1
                    diffs.append({"side": side, "row": rno, "col": p["col"], "type": "substitution",
                                  "kind": k, "peterson": p["sym"], "lorselq": q["sym"],
                                  "lq_flags": sorted(q["flags"])})
                for i in range(i1 + n, i2):
                    st["peterson_only"] += 1
                    diffs.append({"side": side, "row": rno, "col": P[i]["col"],
                                  "type": "peterson_only", "peterson": P[i]["sym"]})
                for j in range(j1 + n, j2):
                    st["lorselq_only"] += 1
                    diffs.append({"side": side, "row": rno, "col": None, "lq_index": j + 1,
                                  "type": "lorselq_only", "lorselq": Ls[j]["sym"]})
        by_side[side] = dict(st)
        tot.update(st)
    letter_diffs = tot["substitution"] + tot["peterson_only"] + tot["lorselq_only"]
    # lorselq's leaf05b.json is a copy of leaf04b.json (checked on the image: Peterson is right)
    rest = Counter()
    for side, st in by_side.items():
        if side != "5b":
            rest.update(st)
    rest_d = rest["substitution"] + rest["peterson_only"] + rest["lorselq_only"]
    excl = {"peterson_symbols": rest["peterson_symbols"], "letter_disagreements": rest_d,
            "rate": rest_d / rest["peterson_symbols"], "substitutions": rest["substitution"],
            "peterson_only": rest["peterson_only"], "lorselq_only": rest["lorselq_only"],
            "lorselq_null_or_lacuna_cells": rest["lq_null_cells"],
            "mark_disagreements": {k: v for k, v in rest.items() if k.startswith("mark_")}}
    out = {
        "what": "Peterson (our parse) against lorselq grids, sides 1c and 2a-16b, letters aligned",
        "inputs": {"cells.jsonl": hashlib.sha256((corpus / "cells.jsonl").read_bytes()).hexdigest(),
                   "lorselq": {s: hashlib.sha256((lq / f"leaf{int(s[:-1]):02d}{s[-1]}.json")
                                                 .read_bytes()).hexdigest() for s in sides}},
        "totals": dict(tot),
        "letter_disagreements": letter_diffs,
        "letter_disagreement_rate": letter_diffs / tot["peterson_symbols"],
        "substitution_rate": tot["substitution"] / tot["peterson_symbols"],
        "mark_disagreements": {f"{m}:{who}_only": v for (m, who), v in sorted(mark.items())},
        "excluding_5b": excl,
        "by_side": by_side,
        # 5b is left out of the list: it would reprint a whole side of the edition
        "differences": [d for d in diffs if d["side"] != "5b"],
        "differences_5b": "3,033 (lorselq 5b is a copy of 4b); not listed",
    }
    json.dump(out, open(ROOT / "results" / "witness_compare.json", "w"), indent=1)
    print(json.dumps({k: out[k] for k in ("totals", "letter_disagreements",
                                          "letter_disagreement_rate", "mark_disagreements",
                                          "excluding_5b")},
                     indent=1))


if __name__ == "__main__":
    main()
