"""Exploratory follow-ups (not pre-registered; run after the primary results were seen).

E1 scale: best path score on the single-series tables (C1) against the two-series sides.
E2 the two `~` series where H1 failed (26b B, 27a B): score of the down-left path (+1, -1).
E3 H3 and H4 redone with the down-left path for those two series (1,000 Markov controls).
Usage: weave_explore.py CORPUS_DIR N_MARKOV   -> results/weave_explore.json
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
import weave as W
from loag import SEED, sha256

FIX = {("26b", "B"): "step+1-1", ("27a", "B"): "step+1-1"}


def main():
    corpus, n = Path(sys.argv[1]), int(sys.argv[2])
    t0 = time.time()
    S = W.Setup(corpus)
    rng = np.random.default_rng([SEED, 99])
    best = []
    for s in W.REF_SIDES:
        rows = S.data[s]
        if len(rows) != W.N or any(len(r) != W.N for r in rows):
            continue
        G = np.array([[x for x, _, _ in r] for r in rows], dtype=np.int64).ravel()
        for par in (0, 1):
            sc = {p: W.score(G, W.pair_index(W.lines_for(W.parity_mask(par), p)), S.LP)
                  for p in W.PATHS}
            best.append(min(sc.values()))
    e1 = {"single_series_best_bits": {"min": min(best), "mean": float(np.mean(best)),
                                      "max": max(best), "sets": len(best)}}
    e2 = {}
    for k in ["26b B ~", "27a B ~"]:
        sc = S.scores(k, S.grids[S.cases[k][0]])
        e2[k] = {"path": "step+1-1", "bits": sc["step+1-1"], "rank": W.rank(sc, "step+1-1"),
                 "margin": W.margin(sc, "step+1-1")}
    # E3: patch rule_paths
    orig = W.rule_paths

    def patched(S_):
        rp = orig(S_)
        for (s, ser), p in FIX.items():
            par = 0 if ser == "A" else 1
            rp[(s, ser)] = (p, rp[(s, ser)][1] + " (down-left)", W.lines_for(W.parity_mask(par), p))
        return rp
    W.rule_paths = patched
    h3 = W.t_h3(S, n, rng)["H3"]
    h4 = W.t_h4(S, n, rng)["H4"]
    W.rule_paths = orig
    out = {"exploratory": True, "seed": [SEED, 99], "controls": n,
           "inputs": {"cells.jsonl": sha256(corpus / "cells.jsonl")},
           "E1": e1, "E2": e2, "E3_H3": h3, "E3_H4": h4}
    json.dump(out, open(W.RESULTS / "weave_explore.json", "w"), indent=1, default=float)
    print(f"weave explore: {time.time() - t0:.1f} s", file=sys.stderr)


if __name__ == "__main__":
    main()
