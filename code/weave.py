"""Weave study: the layout rule of Kelley's two series on Liber Loagaeth 25b-28b.

Pre-registration: results/weave_preregistration.md (commit 26f8bbb of the author's working
repository, see README). Usage:
    weave.py CORPUS_DIR N_CONTROLS N_MARKOV [tests...]     # tests: h1 h2 h3 h4 c1 s1 s2 s3
  CORPUS_DIR  cells.jsonl (code/corpus.py)
Writes results/weave_<test>.json: the pre-registration commit, the corpus hash, the seed, the
number of controls and counts and scores only. Nothing time- or machine-dependent is written, so
a rerun reproduces the files byte for byte. The series as read by the rule are letters of the
edition: they are written only to CORPUS_DIR/weave_series.json (git-ignored, never published).
Seed 20261019. CPU only; run under nice -n 19.
"""

import json
import sys
import time
from collections import Counter
from pathlib import Path

import l3_tests as L
import numpy as np
from loag import CENTRE_SIDES, GRID_SIDES, ROOT, SEED, sha256

RESULTS = ROOT / "results"

PREREG = "26f8bbb"
N = 49
SERIES_SIDES = ["25b", "26a", "26b", "27a", "27b", "28a", "28b"]
REF_SIDES = [s for s in GRID_SIDES if s not in SERIES_SIDES]  # 2a-25a
CH = L.ALPHA + "#"

# ---------------------------------------------------------------- paths

STEPS = [(0, 2), (0, -2), (2, 0), (-2, 0), (1, 1), (-1, -1), (1, -1), (-1, 1),
         (1, 3), (-1, -3), (1, -3), (-1, 3), (3, 1), (-3, -1), (3, -1), (-3, 1)]
PATHS = [f"step{dr:+d}{dc:+d}" for dr, dc in STEPS] + \
    ["bous_rows", "bous_cols", "bous_diag", "bous_anti"]
DIAG = ["step+1+1", "step-1-1", "step+1-1", "step-1+1"]
BOUS = {"bous_rows": (0, 2), "bous_cols": (2, 0), "bous_diag": (1, 1), "bous_anti": (1, -1)}


def perp_key(step, r, c):
    dr, dc = step
    if dr == 0:
        return r
    if dc == 0:
        return c
    return dc * r - dr * c  # constant along the line


def lines_for(mask, path):
    """Lines (lists of flat indices) reading the True cells of mask along a path."""
    if path in BOUS:
        step, bous = BOUS[path], True
    else:
        dr, dc = (int(path[4:6]), int(path[6:8]))
        step, bous = (dr, dc), False
    dr, dc = step
    out = []
    for r in range(N):
        for c in range(N):
            if not mask[r, c]:
                continue
            pr, pc = r - dr, c - dc
            if 0 <= pr < N and 0 <= pc < N and mask[pr, pc]:
                continue
            line, rr, cc = [], r, c
            while 0 <= rr < N and 0 <= cc < N and mask[rr, cc]:
                line.append(rr * N + cc)
                rr, cc = rr + dr, cc + dc
            out.append((perp_key(step, r, c), r, c, line))
    out.sort()
    lines = [x[3] for x in out]
    if bous:
        lines = [ln if i % 2 == 0 else ln[::-1] for i, ln in enumerate(lines)]
    return lines


def pair_index(lines):
    a = np.array([ln[i] for ln in lines for i in range(len(ln) - 1)], dtype=np.int64)
    b = np.array([ln[i + 1] for ln in lines for i in range(len(ln) - 1)], dtype=np.int64)
    return a, b


# ---------------------------------------------------------------- data

def side_grid(data, s):
    rows = data[s]
    assert len(rows) == N and all(len(r) == N for r in rows), s
    G = np.array([[x for x, _, _ in r] for r in rows], dtype=np.int64)
    M = np.array([[L.series_label(f) for _, f, _ in r] for r in rows])
    return G.ravel(), M


def bigram_lp(data):
    T = np.zeros((L.A, L.A))
    for s in REF_SIDES:
        for r in L.sym_rows(data, s):
            for a, b in zip(r[:-1], r[1:], strict=True):
                if a >= 0 and b >= 0:
                    T[a, b] += 1
    return -np.log2((T + 0.5) / (T.sum(1, keepdims=True) + 0.5 * L.A))


def score(G, pi, LP):
    a, b = G[pi[0]], G[pi[1]]
    ok = (a >= 0) & (b >= 0)
    return float(LP[a[ok], b[ok]].mean())


def parity_mask(par):
    rr, cc = np.indices((N, N))
    return (rr + cc) % 2 == par


def cases(data):
    """The pre-registered (side, series) cell sets. Returns {name: (side, mask)}."""
    out = {}
    marks = {}
    for s in SERIES_SIDES:
        G, M = side_grid(data, s)
        marks[s] = M
    A, B = parity_mask(0), parity_mask(1)

    def m(side, par, lab=None):
        base = A if par == 0 else B
        return base & (marks[side] == lab) if lab is not None else base
    out["25b A /"] = ("25b", m("25b", 0, "/"))
    out["25b B ~"] = ("25b", m("25b", 1, "~"))
    out["26a B ~"] = ("26a", m("26a", 1, "~"))
    out["26b A /"] = ("26b", m("26b", 0, "/"))
    out["26b B ~"] = ("26b", m("26b", 1, "~"))
    out["27a B ~"] = ("27a", m("27a", 1, "~"))
    out["27b B /"] = ("27b", m("27b", 1, "/"))
    out["28a A /"] = ("28a", m("28a", 0, "/"))
    out["28b A /"] = ("28b", m("28b", 0, "/"))
    out["26a A 0"] = ("26a", m("26a", 0))
    out["27a A 0"] = ("27a", m("27a", 0))
    out["27b A `"] = ("27b", m("27b", 0))
    out["28a B `"] = ("28a", m("28a", 1, "`"))
    out["28b B `"] = ("28b", m("28b", 1))
    out["25b B rows1-5 0"] = ("25b", m("25b", 1, "0"))
    return out


H1_CASES = ["25b A /", "25b B ~", "26a B ~", "26b A /", "26b B ~", "27a B ~", "27b B /",
            "28a A /", "28b A /"]
PRED = {"/": "step+1+1", "~": "step-1-1"}
H2_FIT = {"0": ("26a A 0", ["27a A 0"]), "`": ("27b A `", ["28a B `", "28b B `"])}


class Setup:
    def __init__(self, corpus):
        self.corpus = Path(corpus)
        self.data = L.load(self.corpus)
        self.LP = bigram_lp(self.data)
        self.grids = {s: side_grid(self.data, s)[0] for s in SERIES_SIDES}
        self.cases = cases(self.data)
        self.lines = {k: {p: lines_for(mask, p) for p in PATHS}
                      for k, (_, mask) in self.cases.items()}
        self.pairs = {k: {p: pair_index(v) for p, v in d.items()} for k, d in self.lines.items()}
        self.rowgroups = {}
        for k, (_, mask) in self.cases.items():
            self.rowgroups[k] = [np.flatnonzero(mask.ravel() & (np.arange(N * N) // N == r))
                                 for r in range(N)]

    def scores(self, k, G):
        return {p: score(G, self.pairs[k][p], self.LP) for p in PATHS}

    def permuted(self, k, G, rng):
        H = G.copy()
        for g in self.rowgroups[k]:
            if len(g) > 1:
                H[g] = G[rng.permutation(g)]
        return H


def margin(sc, path):
    others = [v for p, v in sc.items() if p != path]
    return float(np.mean(others) - sc[path])


def rank(sc, path):
    return 1 + sum(v < sc[path] for p, v in sc.items() if p != path)


# ---------------------------------------------------------------- 6-/8-grams

def seqs_str(G, lines):
    return ["".join(CH[x] for x in G[ln]) for ln in lines]


def grams(strs, k):
    out = set()
    for s in strs:
        for i in range(len(s) - k + 1):
            g = s[i:i + k]
            if "#" not in g:
                out.add(g)
    return out


def rows_str(data, sides):
    return {s: ["".join(CH[x] for x in r) for r in L.sym_rows(data, s)] for s in sides}


# ---------------------------------------------------------------- tests

def t_h1(S, n, rng):
    obs = {k: S.scores(k, S.grids[S.cases[k][0]]) for k in H1_CASES}
    ref6 = grams([x for v in rows_str(S.data, REF_SIDES).values() for x in v], 6)
    per = {}
    for k in H1_CASES:
        p = PRED[k.split()[-1]]
        G = S.grids[S.cases[k][0]]
        g6 = {q: len(grams(seqs_str(G, S.lines[k][q]), 6) & ref6) for q in PATHS}
        per[k] = {"predicted": p, "score_predicted": obs[k][p], "rank": rank(obs[k], p),
                  "best_path": min(obs[k], key=obs[k].get), "margin": margin(obs[k], p),
                  "scores": obs[k], "shared_6grams_with_2a-25a": g6,
                  "rank_by_6grams": 1 + sum(v > g6[p] for q, v in g6.items() if q != p),
                  "cells": int(S.cases[k][1].sum())}
    T = float(np.mean([per[k]["margin"] for k in H1_CASES]))
    sims = np.empty(n)
    for i in range(n):
        ms = []
        for k in H1_CASES:
            H = S.permuted(k, S.grids[S.cases[k][0]], rng)
            ms.append(margin(S.scores(k, H), PRED[k.split()[-1]]))
        sims[i] = np.mean(ms)
    return {"H1": {"statistic": "mean over 9 slant-marked cases of (mean score of the other 19 "
                                "paths - score of the predicted path), bits per pair",
                   "observed": T, "p_one_sided": L.pval_high(T, sims), "controls": L.summ(sims),
                   "cases_ranked_first": sum(per[k]["rank"] == 1 for k in H1_CASES),
                   "cases": per}}


def h2_stat(S, grids_by_case):
    out, detail = [], {}
    for mark, (fit, tests) in H2_FIT.items():
        sf = S.scores(fit, grids_by_case[fit])
        best = min(sf, key=sf.get)
        detail[mark] = {"fit_case": fit, "fitted_path": best, "tests": {}}
        for t in tests:
            st = S.scores(t, grids_by_case[t])
            out.append(margin(st, best))
            detail[mark]["tests"][t] = {"rank": rank(st, best), "margin": margin(st, best),
                                        "best_path": min(st, key=st.get), "scores": st}
    return float(np.mean(out)), detail


def t_h2(S, n, rng):
    ks = [H2_FIT[m][0] for m in H2_FIT] + [t for m in H2_FIT for t in H2_FIT[m][1]]
    base = {k: S.grids[S.cases[k][0]] for k in ks}
    T, detail = h2_stat(S, base)
    sims = np.empty(n)
    for i in range(n):
        sims[i] = h2_stat(S, {k: S.permuted(k, base[k], rng) for k in ks})[0]
    return {"H2": {"statistic": "mean over 3 held-out cases of (mean of other 19 - score of the "
                                "path fitted on the fit case)",
                   "observed": T, "p_one_sided": L.pval_high(T, sims), "controls": L.summ(sims),
                   "detail": detail}}


def rule_paths(S):
    """Path of each whole series under the rule (H1 prediction; H2 fit for the others)."""
    fit = {}
    for mark, (fk, _) in H2_FIT.items():
        sf = S.scores(fk, S.grids[S.cases[fk][0]])
        fit[mark] = min(sf, key=sf.get)
    marks = {"25b": ("/", "~"), "26a": ("0", "~"), "26b": ("/", "~"), "27a": ("0", "~"),
             "27b": ("`", "/"), "28a": ("/", "`"), "28b": ("/", "`")}
    out = {}
    for s in SERIES_SIDES:
        for par, ser in ((0, "A"), (1, "B")):
            mk = marks[s][par]
            p = PRED.get(mk) or fit[mk]
            out[(s, ser)] = (p, mk, lines_for(parity_mask(par), p))
    return out


def series_strings(S, rp):
    return {k: seqs_str(S.grids[k[0]], v[2]) for k, v in rp.items()}


def markov_series(strs, rng):
    rows = [np.array([CH.index(ch) if ch != "#" else -1 for ch in s]) for s in strs]
    rows = [np.where(r == L.A, -1, r) for r in rows]
    cum = L.transitions(rows)
    gen = L.markov_surrogate([rows], [cum], rng)
    return ["".join(CH[x] if x >= 0 else "#" for x in g) for g in gen]


def t_h3(S, n, rng):
    rp = rule_paths(S)
    ss = series_strings(S, rp)
    diam = rows_str(S.data, CENTRE_SIDES)
    d8 = {s: grams(v, 8) for s, v in diam.items()}
    all_d8 = set().union(*d8.values())
    ref8 = grams([x for v in rows_str(S.data, REF_SIDES).values() for x in v], 8)

    def stat(strs_by):
        g = set().union(*(grams(v, 8) for v in strs_by.values()))
        return len(g & all_d8)
    obs = stat(ss)
    per = {}
    for k, v in ss.items():
        g = grams(v, 8)
        bt = {s: len(g & d8[s]) for s in CENTRE_SIDES}
        top = sorted(bt.items(), key=lambda x: -x[1])[:3]
        per[f"{k[0]} {k[1]}"] = {"path": rp[k][0], "mark": rp[k][1],
                                 "shared_8grams_29a-48b": len(g & all_d8),
                                 "shared_8grams_2a-25a": len(g & ref8),
                                 "best_tables": top, "letters": sum(len(x) for x in v)}
    sims = np.empty(n)
    sims_ref = np.empty(n)
    for i in range(n):
        surr = {k: markov_series(v, rng) for k, v in ss.items()}
        sims[i] = stat(surr)
        sims_ref[i] = len(set().union(*(grams(v, 8) for v in surr.values())) & ref8)
    ref_obs = len(set().union(*(grams(v, 8) for v in ss.values())) & ref8)
    return {"H3": {"statistic": "distinct 8-grams shared between the 14 series (read by the "
                                "rule) and the rows of 29a-48b",
                   "observed": obs, "p_one_sided": L.pval_high(obs, sims),
                   "controls": L.summ(sims),
                   "against_2a-25a": {"observed": ref_obs, "controls": L.summ(sims_ref),
                                      "p_one_sided": L.pval_high(ref_obs, sims_ref)},
                   "rule_paths": {f"{k[0]} {k[1]}": [v[0], v[1]] for k, v in rp.items()},
                   "per_series": per}}


def t_h4(S, n, rng):
    rp = rule_paths(S)
    ss = series_strings(S, rp)

    def shared(x, y):
        return len(grams(x, 8) & grams(y, 8))

    def stat(d):
        return sum(shared(d[(s, "A")], d[(s, "B")]) for s in SERIES_SIDES)
    obs = stat(ss)
    mirror = sum(shared(ss[(s, "A")], [x[::-1] for x in ss[(s, "B")]]) for s in SERIES_SIDES)
    cross = {f"A {s} / B {t}": shared(ss[(s, "A")], ss[(t, "B")])
             for s in SERIES_SIDES for t in SERIES_SIDES}
    same_side = [cross[f"A {s} / B {s}"] for s in SERIES_SIDES]
    other = [v for k, v in cross.items() if k.split()[1] != k.split()[-1]]
    sims, sims_m = np.empty(n), np.empty(n)
    for i in range(n):
        surr = {k: markov_series(v, rng) for k, v in ss.items()}
        sims[i] = stat(surr)
        sims_m[i] = sum(shared(surr[(s, "A")], [x[::-1] for x in surr[(s, "B")]])
                        for s in SERIES_SIDES)
    return {"H4": {"statistic": "distinct 8-grams shared between series A and B of the same "
                                "side, summed over 7 sides",
                   "observed": obs, "p_one_sided": L.pval_high(obs, sims),
                   "controls": L.summ(sims),
                   "mirror_B_reversed": {"observed": mirror, "controls": L.summ(sims_m),
                                         "p_one_sided": L.pval_high(mirror, sims_m)},
                   "same_side_per_side": dict(zip(SERIES_SIDES, same_side, strict=True)),
                   "other_side_pairs_mean": float(np.mean(other)),
                   "cross_matrix": cross}}


def t_c1(S, n, rng):
    out = {}
    for s in REF_SIDES:
        rows = S.data[s]
        if len(rows) != N or any(len(r) != N for r in rows):
            continue
        G = np.array([[x for x, _, _ in r] for r in rows], dtype=np.int64).ravel()
        for par in (0, 1):
            ls = {p: pair_index(lines_for(parity_mask(par), p)) for p in PATHS}
            sc = {p: score(G, ls[p], S.LP) for p in PATHS}
            bd = min(DIAG, key=sc.get)
            out[f"{s} {'AB'[par]}"] = {"best_path": min(sc, key=sc.get),
                                       "rank_best_diagonal": rank(sc, bd),
                                       "rank_row_step+0+2": rank(sc, "step+0+2"),
                                       "diag_minus_row": sc[bd] - sc["step+0+2"]}
    best = Counter(v["best_path"] for v in out.values())
    return {"C1": {"sets": len(out), "best_path_counts": dict(best),
                   "diagonal_beats_row": sum(v["diag_minus_row"] < 0 for v in out.values()),
                   "per_set": out}}


def join_loss(G, lines, LP):
    a = np.array([ln[-1] for ln in lines[:-1]])
    b = np.array([ln[0] for ln in lines[1:]])
    x, y = G[a], G[b]
    ok = (x >= 0) & (y >= 0)
    return float(LP[x[ok], y[ok]].mean())


def t_s1(S, n, rng):
    out = {}
    for k in H1_CASES:
        p = PRED[k.split()[-1]]
        G = S.grids[S.cases[k][0]]
        lines = [ln for ln in S.lines[k][p] if len(ln) > 0]
        fwd, back = join_loss(G, lines, S.LP), join_loss(G, lines[::-1], S.LP)
        sims = np.array([join_loss(G, [lines[j] for j in rng.permutation(len(lines))], S.LP)
                         for _ in range(n)])
        within = S.scores(k, G)[p]
        out[k] = {"join_bits_order_ascending": fwd, "join_bits_order_descending": back,
                  "within_line_bits": within, "random_orders": L.summ(sims),
                  "p_low_ascending": L.pval_low(fwd, sims),
                  "p_low_descending": L.pval_low(back, sims)}
    return {"S1": out}


def t_s2(S, n, rng):
    rp = rule_paths(S)
    ss = series_strings(S, rp)
    end, start = set("hxs"), set("ovg")

    def shares(strs):
        ends = [x[-1] for x in strs if len(x) >= 2]
        starts = [x[0] for x in strs if len(x) >= 2]
        inner = [ch for x in strs for ch in x[1:-1]]
        return (np.mean([c in end for c in ends]), np.mean([c in start for c in starts]),
                np.mean([c in end for c in inner]), np.mean([c in start for c in inner]))
    allstr = [x for v in ss.values() for x in v]
    obs = shares(allstr)
    sims = []
    for _ in range(n):
        surr = []
        for v in ss.values():
            letters = list("".join(v))
            rng.shuffle(letters)
            pos = 0
            for x in v:
                surr.append("".join(letters[pos:pos + len(x)]))
                pos += len(x)
        sims.append(shares(surr))
    sims = np.array(sims)
    return {"S2": {"share_hxs_at_line_ends": obs[0], "share_ovg_at_line_starts": obs[1],
                   "share_hxs_inside": obs[2], "share_ovg_inside": obs[3],
                   "p_high_ends": L.pval_high(obs[0], sims[:, 0]),
                   "p_high_starts": L.pval_high(obs[1], sims[:, 1]),
                   "controls_ends": L.summ(sims[:, 0]), "controls_starts": L.summ(sims[:, 1])}}


def t_s3(S, n, rng):
    k = "25b B rows1-5 0"
    sc = S.scores(k, S.grids["25b"])
    return {"S3": {"cells": int(S.cases[k][1].sum()), "rank_row_step+0+2": rank(sc, "step+0+2"),
                   "best_path": min(sc, key=sc.get), "scores": sc}}


TESTS = {"h1": t_h1, "h2": t_h2, "h3": t_h3, "h4": t_h4, "c1": t_c1, "s1": t_s1, "s2": t_s2,
         "s3": t_s3}
MARKOV = {"h3", "h4", "s1", "s2"}


def main():
    corpus, n, nm = Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    S = Setup(corpus)
    # the series read by the rule (letters of the edition): local corpus folder only
    series = {f"{k[0]} {k[1]}": v for k, v in series_strings(S, rule_paths(S)).items()}
    json.dump(series, open(corpus / "weave_series.json", "w"), indent=0)
    for name in sys.argv[4:]:
        t0 = time.time()
        rng = np.random.default_rng([SEED, list(TESTS).index(name)])
        k = nm if name in MARKOV else n
        body = TESTS[name](S, k, rng)
        out = {"test": name, "prereg_commit": PREREG,
               "seed": [SEED, list(TESTS).index(name)], "controls": k,
               "inputs": {"cells.jsonl": sha256(corpus / "cells.jsonl")}}
        out.update(body)
        json.dump(out, open(RESULTS / f"weave_{name}.json", "w"), indent=1, default=float)
        print(f"weave {name}: {time.time() - t0:.1f} s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
