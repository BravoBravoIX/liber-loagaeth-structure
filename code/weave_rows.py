"""Weave study, descriptive (counts only, no controls): the line lengths of the two chessboard
colours of a 49 x 49 grid read along a diagonal, against the row lengths of the partly filled
tables 29a-48b. Written for the public v1.1 release, after the study; the pre-registration
states the match in words (its item 3). Usage: weave_rows.py CORPUS_DIR -> results/weave_rows.json
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import weave as W
from loag import CENTRE_SIDES, load_cells, sha256

ODD = [2 * i + 1 for i in range(25)] + [2 * i + 1 for i in range(23, -1, -1)]  # 1, 3 ... 49 ... 1
EVEN = [2 * i for i in range(1, 25)] + [2 * i for i in range(24, 0, -1)]  # 2 ... 48, 48 ... 2


def off_by(lengths, pattern):
    """Rows whose length differs from the pattern, row by row (None if the row counts differ)."""
    if len(lengths) != len(pattern):
        return None
    return sum(a != b for a, b in zip(lengths, pattern, strict=True))


def main():
    corpus = Path(sys.argv[1])
    colours = {}
    for par, name in ((0, "A (row + column even)"), (1, "B (row + column odd)")):
        ls = [len(x) for x in W.lines_for(W.parity_mask(par), "step+1+1")]
        colours[name] = {"lines": len(ls), "cells": sum(ls), "is_1_3_to_49_to_3_1": ls == ODD,
                         "is_2_4_to_48_48_to_4_2": ls == EVEN}
    rows = defaultdict(lambda: defaultdict(int))
    for c in load_cells(corpus):
        if c["side"] in CENTRE_SIDES:
            rows[c["side"]][c["row"]] += 1
    sides = {}
    for s in CENTRE_SIDES:
        ls = [rows[s][r] for r in sorted(rows[s])]
        fit = {"odd": off_by(ls, ODD), "even": off_by(ls, EVEN)}
        sides[s] = {"rows": len(ls), "cells": sum(ls), "exact_odd": ls == ODD,
                    "exact_even": ls == EVEN, "rows_differing_from_odd": fit["odd"],
                    "rows_differing_from_even": fit["even"]}
    out = {"descriptive": True,
           "what": "line lengths of the two chessboard colours read along a diagonal (the same "
                   "for all four diagonal directions), and the row lengths of 29a-48b",
           "inputs": {"cells.jsonl": sha256(corpus / "cells.jsonl")},
           "colours": colours,
           "tables_exact_odd": sum(v["exact_odd"] for v in sides.values()),
           "tables_exact_even": sum(v["exact_even"] for v in sides.values()),
           "tables": len(sides), "per_side": sides}
    json.dump(out, open(W.RESULTS / "weave_rows.json", "w"), indent=1)


if __name__ == "__main__":
    main()
