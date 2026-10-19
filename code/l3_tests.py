"""L3: the pre-registered tests (results/preregistration.md; pre-registration commit 7127723 of
the author's working repository, see README).

One subcommand per test group; each writes results/l3_<name>.json with the pre-registration
commit, the corpus hash, the seed and the number of controls. Nothing time- or machine-dependent
is written, so a rerun reproduces the files byte for byte.

  q1      P1a, P1b         word marks
  q2rep   P2a, P2c, S2a    repeats against Markov surrogates and row shuffles
  q2pair  P2b, S2b         a/b pairing
  q3a     P3a, S3a         the cell above (and diagonals)
  q3b     S3b              copying from recent rows
  q3c     S3c              neighbouring tables
  q4      P4a, P4b         the Calls
  q5      P5a, S5b, P5c    Kelley's series on 25b-28b, plus the descriptive counts

Usage: l3_tests.py NAME CORPUS_DIR REF_DIR [N_CONTROLS]     (CPU only; run under nice -n 19)
  CORPUS_DIR  cells.jsonl (code/corpus.py) and calls_words.jsonl (code/calls.py)
  REF_DIR     la15/train.txt and en15/train.txt, the period Latin and English reference texts
              (code/reference_corpora.py)
"""

import json
import math
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from loag import CENTRE_SIDES, GRID_SIDES, ROOT, SEED, fold, load_cells, sha256

PREREG = "7127723"
ALPHA = "abcdefghiklmnopqrstvxyz"  # the folded alphabet actually present (23 letters)
A = len(ALPHA)
IDX = {c: i for i, c in enumerate(ALPHA)}
BREAK = -1
CORPORA = None  # REF_DIR, set in main()
TEST_IDS = {"q1": 1, "q2rep": 2, "q2pair": 3, "q3a": 4, "q3b": 5, "q3c": 6, "q4": 7, "q5": 8}


# ---------------------------------------------------------------- data

def load(corpus):
    """{side: [row arrays of symbol ids (BREAK for digits)]}, plus flags per cell."""
    cells = load_cells(corpus)
    rows = defaultdict(lambda: defaultdict(list))
    for c in cells:
        s = c["letters"]
        f = fold(s[0]) if s and s[0].isalpha() else None
        sym = IDX.get(f, BREAK) if f else BREAK
        rows[c["side"]][c["row"]].append((sym, c["flags"], c["col"]))
    out = {}
    for side, rr in rows.items():
        out[side] = [rr[k] for k in sorted(rr)]
    return out


def sym_rows(data, side):
    return [np.array([s for s, _, _ in row], dtype=np.int64) for row in data[side]]


def text_words(path):
    words = []
    for w in re.findall(r"[A-Za-z]+", Path(path).read_text(encoding="utf-8", errors="ignore")):
        f = "".join(fold(ch) for ch in w)
        if all(ch in IDX for ch in f):
            words.append(f)
    return words


def calls_words(corpus):
    out = []
    for line in open(Path(corpus) / "calls_words.jsonl"):
        w = "".join(fold(ch) or "" for ch in json.loads(line)["forward"])
        w = "".join(ch for ch in w if ch in IDX)
        if w:
            out.append(w)
    return out


def pval_high(obs, sims):
    sims = np.asarray(sims)
    return float((1 + (sims >= obs).sum()) / (1 + len(sims)))


def pval_low(obs, sims):
    sims = np.asarray(sims)
    return float((1 + (sims <= obs).sum()) / (1 + len(sims)))


def summ(sims):
    sims = np.asarray(sims, dtype=float)
    return {"mean": float(sims.mean()), "sd": float(sims.std()),
            "q025": float(np.quantile(sims, 0.025)), "q975": float(np.quantile(sims, 0.975)),
            "max": float(sims.max()), "min": float(sims.min())}


def write(name, corpus, n, body, t0):
    out = {"test_group": name, "prereg_commit": PREREG,
           "seed": SEED, "controls": n, "inputs": {"cells.jsonl": sha256(corpus / "cells.jsonl")}}
    out.update(body)
    json.dump(out, open(ROOT / "results" / f"l3_{name}.json", "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float)[:3000])
    print(f"{name}: {time.time() - t0:.1f} s", file=sys.stderr)


# ---------------------------------------------------------------- Q1

def jsd(p, q):
    p, q = np.asarray(p, float), np.asarray(q, float)
    p, q = p / p.sum(), q / q.sum()
    m = (p + q) / 2

    def kl(a, b):
        mask = a > 0
        return float((a[mask] * np.log2(a[mask] / b[mask])).sum())
    return 0.5 * kl(p, m) + 0.5 * kl(q, m)


def hist(lengths):
    h = np.zeros(15)
    for n in lengths:
        h[min(n, 15) - 1] += 1
    return h


def q1(corpus, data, n, rng):
    sides = ["2a", "2b", "3a", "3b"]
    lw = []
    for side in sides:
        seq = [(s, "word_end" in fl) for row in data[side] for s, fl, _ in row]
        cur, started = 0, False
        for _s, end in seq:
            cur += 1
            if end:
                if started and cur > 0:
                    lw.append(cur)
                started, cur = True, 0
    kw = [len(w) for w in calls_words(corpus)]
    L = [len(w) for w in text_words(CORPORA / "la15" / "train.txt")]
    E = [len(w) for w in text_words(CORPORA / "en15" / "train.txt")]
    hl, hk, hL, hE = hist(lw), hist(kw), hist(L), hist(E)
    obs = jsd(hl, hk)
    pool = np.array(lw + kw)
    sims = np.empty(n)
    for i in range(n):
        p = rng.permutation(pool)
        sims[i] = jsd(hist(p[:len(lw)]), hist(p[len(lw):]))
    boot = {k: np.empty(n) for k in ("calls", "latin", "english")}
    lwa = np.array(lw)
    for i in range(n):
        b = hist(rng.choice(lwa, len(lwa)))
        boot["calls"][i] = jsd(b, hk)
        boot["latin"][i] = jsd(b, hL)
        boot["english"][i] = jsd(b, hE)
    # P1b: mutual information between a mark after the cell and (this, next)
    rows = []
    for side in sides:
        for row in data[side]:
            sy = [s for s, _, _ in row]
            nx = sy[1:] + [A]  # A = row end
            pair = np.array([(s if s >= 0 else A) * (A + 1) + (t if t >= 0 else A)
                             for s, t in zip(sy, nx, strict=True)])
            mk = np.array([1 if "word_end" in fl else 0 for _, fl, _ in row])
            rows.append((pair, mk))
    pairs = np.concatenate([p for p, _ in rows])
    K = (A + 1) ** 2

    def mi(marks):
        tot = len(marks)
        c1 = np.bincount(pairs[marks == 1], minlength=K)
        c0 = np.bincount(pairs[marks == 0], minlength=K)
        cp = c0 + c1
        pm = marks.mean()
        val = 0.0
        for c, pmk in ((c1, pm), (c0, 1 - pm)):
            mask = c > 0
            val += float((c[mask] / tot * np.log2(c[mask] / (cp[mask] * pmk))).sum())
        return val
    marks = np.concatenate([m for _, m in rows])
    obs_mi = mi(marks)
    sims_mi = np.empty(n)
    for i in range(n):
        sims_mi[i] = mi(np.concatenate([rng.permutation(m) for _, m in rows]))
    return {
        "P1a": {"statistic": "JSD(word lengths Loagaeth, Calls), bits", "observed": obs,
                "p_one_sided": pval_high(obs, sims), "controls": summ(sims),
                "loagaeth_words": len(lw), "calls_words": len(kw),
                "mean_length": {"loagaeth": float(np.mean(lw)), "calls": float(np.mean(kw)),
                                "latin": float(np.mean(L)), "english": float(np.mean(E))},
                "jsd": {"calls": obs, "latin": jsd(hl, hL), "english": jsd(hl, hE)},
                "jsd_bootstrap_95": {k: [float(np.quantile(v, .025)), float(np.quantile(v, .975))]
                                     for k, v in boot.items()},
                "length_hist_1_to_15plus": {"loagaeth": hl.tolist(), "calls": hk.tolist(),
                                            "latin_share": (hL / hL.sum()).round(4).tolist(),
                                            "english_share": (hE / hE.sum()).round(4).tolist()}},
        "P1b": {"statistic": "MI(mark after cell; (this, next letter)), bits", "observed": obs_mi,
                "p_one_sided": pval_high(obs_mi, sims_mi), "controls": summ(sims_mi),
                "marks": int(marks.sum()), "cells": int(len(marks))},
    }


# ---------------------------------------------------------------- Q2

def kgram_hashes(rows, k):
    """Hashes of all k-grams within rows (no BREAK inside); returns (hashes, row index)."""
    hs, ri = [], []
    for i, r in enumerate(rows):
        if len(r) < k:
            continue
        w = np.lib.stride_tricks.sliding_window_view(r, k)
        ok = (w >= 0).all(1)
        h = (w[ok] * (A ** np.arange(k - 1, -1, -1))).sum(1)
        hs.append(h)
        ri.append(np.full(len(h), i))
    if not hs:
        return np.array([], dtype=np.int64), np.array([], dtype=np.int64)
    return np.concatenate(hs), np.concatenate(ri)


def repeat_stats(rows, side_of_row, k):
    h, ri = kgram_hashes(rows, k)
    u, cnt = np.unique(h, return_counts=True)
    rep = int((cnt >= 2).sum())
    sides = side_of_row[ri]
    pair = np.unique(np.stack([h, sides], 1), axis=0)
    u2, c2 = np.unique(pair[:, 0], return_counts=True)
    return rep, int((c2 >= 2).sum())


def longest_repeat(rows):
    k = 8
    while True:
        h, _ = kgram_hashes(rows, k)
        if len(h) == 0:
            return k - 1
        _, cnt = np.unique(h, return_counts=True)
        if not (cnt >= 2).any():
            return k - 1
        k += 1
        if k > 13:  # 23**13 stays inside int64; longer repeats are compared as strings
            break
    strs = ["".join(ALPHA[x] if x >= 0 else "#" for x in r) for r in rows]
    best = 13
    seen = {}
    while True:
        k = best + 1
        seen = Counter(s[i:i + k] for s in strs for i in range(len(s) - k + 1)
                       if "#" not in s[i:i + k])
        if any(v >= 2 for v in seen.values()):
            best = k
        else:
            return best


def transitions(rows):
    T = np.zeros((A, A))
    U = np.zeros(A)
    for r in rows:
        for a, b in zip(r[:-1], r[1:], strict=True):
            if a >= 0 and b >= 0:
                T[a, b] += 1
        for a in r:
            if a >= 0:
                U[a] += 1
    P = T.copy()
    for a in range(A):
        P[a] = T[a] / T[a].sum() if T[a].sum() > 0 else U / U.sum()
    return np.cumsum(P, 1)


def markov_surrogate(side_rows, cums, rng):
    out = []
    for rows, cum in zip(side_rows, cums, strict=True):
        L = max(len(r) for r in rows)
        M = np.full((len(rows), L), -2, dtype=np.int64)
        for i, r in enumerate(rows):
            M[i, :len(r)] = r
        G = M.copy()
        for t in range(1, L):
            prev = G[:, t - 1]
            need = (M[:, t] >= 0) & (prev >= 0)
            if need.any():
                u = rng.random(need.sum())
                G[need, t] = (u[:, None] > cum[prev[need]]).sum(1)
                G[need, t] = np.minimum(G[need, t], A - 1)
        out.extend(G[i, :len(r)] for i, r in enumerate(rows))
    return out


def q2rep(corpus, data, n, rng):
    side_rows = [sym_rows(data, s) for s in GRID_SIDES]
    rows = [r for sr in side_rows for r in sr]
    side_of_row = np.array([i for i, sr in enumerate(side_rows) for _ in sr])
    cums = [transitions(sr) for sr in side_rows]
    obs8, obs8s = repeat_stats(rows, side_of_row, 8)
    obs12, obs12s = repeat_stats(rows, side_of_row, 12)
    obs_long = longest_repeat(rows)
    mk = {k: np.empty(n) for k in ("rep8", "shared8", "rep12", "shared12")}
    sh = {k: np.empty(n) for k in ("rep8", "rep12")}
    long_m, long_s = [], []
    for i in range(n):
        g = markov_surrogate(side_rows, cums, rng)
        mk["rep8"][i], mk["shared8"][i] = repeat_stats(g, side_of_row, 8)
        mk["rep12"][i], mk["shared12"][i] = repeat_stats(g, side_of_row, 12)
        s = [rng.permutation(r) for r in rows]
        sh["rep8"][i], _ = repeat_stats(s, side_of_row, 8)
        sh["rep12"][i], _ = repeat_stats(s, side_of_row, 12)
        if i < 200:  # the longest repeat is costly; 200 of each control
            long_m.append(longest_repeat(g))
            long_s.append(longest_repeat(s))
    return {
        "P2a": {"statistic": "distinct 8-grams occurring 2+ times in G", "observed": obs8,
                "p_one_sided": pval_high(obs8, mk["rep8"]), "controls_markov": summ(mk["rep8"])},
        "P2c": {"statistic": "distinct 8-grams on 2+ sides of G", "observed": obs8s,
                "p_one_sided": pval_high(obs8s, mk["shared8"]),
                "controls_markov": summ(mk["shared8"])},
        "S2a": {"rep12": {"observed": obs12, "p_markov": pval_high(obs12, mk["rep12"]),
                          "controls_markov": summ(mk["rep12"]),
                          "p_row_shuffle": pval_high(obs12, sh["rep12"]),
                          "controls_row_shuffle": summ(sh["rep12"])},
                "shared12": {"observed": obs12s, "p_markov": pval_high(obs12s, mk["shared12"]),
                             "controls_markov": summ(mk["shared12"])},
                "rep8_row_shuffle": {"observed": obs8, "p": pval_high(obs8, sh["rep8"]),
                                     "controls": summ(sh["rep8"])},
                "longest_repeat": {"observed": obs_long, "controls_n": 200,
                                   "p_markov": pval_high(obs_long, long_m),
                                   "markov": summ(long_m),
                                   "p_row_shuffle": pval_high(obs_long, long_s),
                                   "row_shuffle": summ(long_s)}},
    }


def trigram_vec(rows):
    h, _ = kgram_hashes(rows, 3)
    return np.bincount(h, minlength=A ** 3).astype(float)


def sixgram_set(rows):
    h, _ = kgram_hashes(rows, 6)
    return set(h.tolist())


def pairing(sides, data, n, rng):
    vec = {s: trigram_vec(sym_rows(data, s)) for s in sides}
    six = {s: sixgram_set(sym_rows(data, s)) for s in sides}
    adj = list(zip(sides[:-1], sides[1:], strict=True))
    same = np.array([a[:-1] == b[:-1] for a, b in adj])
    cos = np.array([vec[a] @ vec[b] / math.sqrt((vec[a] @ vec[a]) * (vec[b] @ vec[b]))
                    for a, b in adj])
    sh6 = np.array([len(six[a] & six[b]) for a, b in adj], dtype=float)

    def stat(v, lab):
        return float(v[lab].mean() - v[~lab].mean())
    out = {}
    for name, v in (("cosine", cos), ("shared6", sh6)):
        obs = stat(v, same)
        sims = np.array([stat(v, rng.permutation(same)) for _ in range(n)])
        out[name] = {"observed": obs, "p_one_sided": pval_high(obs, sims), "controls": summ(sims),
                     "same_leaf_mean": float(v[same].mean()),
                     "cross_leaf_mean": float(v[~same].mean())}
    out["pairs"] = int(len(adj))
    out["same_leaf_pairs"] = int(same.sum())
    return out


def q2pair(corpus, data, n, rng):
    g = pairing(GRID_SIDES, data, n, rng)
    c = pairing(CENTRE_SIDES, data, n, rng)
    return {"P2b": {"statistic": "mean trigram cosine, same-leaf minus cross-leaf adjacent pairs",
                    **g["cosine"], "pairs": g["pairs"], "same_leaf_pairs": g["same_leaf_pairs"]},
            "S2b": {"G_shared6": g["shared6"], "C_cosine": c["cosine"],
                    "C_shared6": c["shared6"], "C_pairs": c["pairs"]}}


# ---------------------------------------------------------------- Q3

def full_rows(data, side):
    rows = [r for r in data[side] if len(r) == 49]
    if len(rows) < 40:
        return None
    return np.array([[s for s, _, _ in r] for r in rows], dtype=np.int64)


def gain_vertical(M, held, shift):
    """Sum over held-out cells of loss(x|left) - loss(x|left, upper neighbour at col+shift)."""
    R, C = M.shape
    x = M[1:, 1:]
    left = M[1:, :-1]
    up = np.full_like(x, -1)
    lo, hi = max(0, 1 + shift), min(C, C + shift)
    # up[r, c] = M[r-1+1 ... ] aligned: cell (r, c) with c from 1; neighbour (r-1, c+shift)
    cols = np.arange(1, C) + shift
    okc = (cols >= 0) & (cols < C)
    up[:, okc] = M[:-1, cols[okc]]
    del lo, hi
    ok = (x >= 0) & (left >= 0) & (up >= 0)
    rows_idx = np.arange(1, R)
    is_held = np.isin(rows_idx, held)[:, None] & ok
    is_train = (~np.isin(rows_idx, held))[:, None] & ok
    xt, lt, ut = x[is_train], left[is_train], up[is_train]
    ch = np.bincount(lt * A + xt, minlength=A * A).reshape(A, A)
    cv = np.bincount((lt * A + ut) * A + xt, minlength=A ** 3).reshape(A * A, A)
    xh, lh, uh = x[is_held], left[is_held], up[is_held]
    ph = (ch[lh, xh] + 0.5) / (ch[lh].sum(1) + 0.5 * A)
    pv = (cv[lh * A + uh, xh] + 0.5) / (cv[lh * A + uh].sum(1) + 0.5 * A)
    return float((np.log2(pv) - np.log2(ph)).sum()), int(len(xh))


def q3a(corpus, data, n, rng):
    mats = {s: full_rows(data, s) for s in GRID_SIDES}
    mats = {s: m for s, m in mats.items() if m is not None}
    held_of = {s: np.arange(4, m.shape[0], 5) for s, m in mats.items()}  # row numbers 5,10,..

    def total(shift, perm=None):
        tot, cells, per = 0.0, 0, {}
        for s, m in mats.items():
            mm = m if perm is None else m[perm[s]]
            g, k = gain_vertical(mm, held_of[s], shift)
            tot += g
            cells += k
            per[s] = g
        return tot, cells, per
    res = {}
    for name, shift in (("above", 0), ("above_left", -1), ("above_right", 1)):
        obs, cells, per = total(shift)
        sims = np.empty(n)
        per_sims = {s: np.empty(n) for s in mats}
        for i in range(n):
            perm = {s: rng.permutation(m.shape[0]) for s, m in mats.items()}
            sims[i], _, ps = total(shift, perm)
            for s in mats:
                per_sims[s][i] = ps[s]
        per_p = {s: pval_high(per[s], per_sims[s]) for s in mats}
        res[name] = {"observed_bits": obs, "held_out_cells": cells,
                     "bits_per_letter": obs / cells, "p_one_sided": pval_high(obs, sims),
                     "controls": summ(sims), "per_side_bits": per, "per_side_p": per_p,
                     "per_side_holm_below_0.05": holm_count(per_p)}
    return {"P3a": {"statistic": "summed held-out gain in bits from the cell above",
                    **{k: v for k, v in res["above"].items()}},
            "S3a": {"above_left": res["above_left"], "above_right": res["above_right"]},
            "sides_used": sorted(mats, key=lambda s: (int(s[:-1]), s[-1]))}


def holm_count(pdict):
    ps = sorted(pdict.values())
    m = len(ps)
    cnt = 0
    for k, p in enumerate(ps):
        if p * (m - k) < 0.05:
            cnt += 1
        else:
            break
    return cnt


def q3b(corpus, data, n, rng):
    sides = {s: sym_rows(data, s) for s in GRID_SIDES}
    K = 20
    pre = {}
    for s, rows in sides.items():
        pre[s] = [[set(kgram_hashes([r], k)[0].tolist()) for k in range(1, K + 1)] for r in rows]

    def lcs(sets_a, sets_list):
        best = 0
        for k in range(K):
            if any(sets_a[k] & sb[k] for sb in sets_list):
                best = k + 1
            else:
                break
        return best

    def stat(order):
        vals = []
        for s, rows in sides.items():
            o = order[s]
            for pos in range(4, len(rows), 5):
                cur = pre[s][o[pos]]
                prev = [pre[s][o[q]] for q in range(max(0, pos - 3), pos)]
                vals.append(lcs(cur, prev))
        return float(np.mean(vals))
    ident = {s: np.arange(len(r)) for s, r in sides.items()}
    obs = stat(ident)
    sims = np.array([stat({s: rng.permutation(len(r)) for s, r in sides.items()})
                     for _ in range(n)])
    return {"S3b": {"statistic": "mean longest string shared with the 3 rows above (held-out rows)",
                    "observed": obs, "p_one_sided": pval_high(obs, sims), "controls": summ(sims)}}


class Trigram:
    """Interpolated letter trigram model (0.6/0.3/0.1, add-0.5) with a start symbol."""

    def __init__(self, c3, c2, c1):
        self.c3, self.c2, self.c1 = c3, c2, c1
        self.n3 = c3.sum(2)
        self.n2 = c2.sum(1)
        self.n1 = c1.sum()

    @staticmethod
    def counts(seqs):
        S = A  # start symbol
        c3 = np.zeros((A + 1, A + 1, A))
        c2 = np.zeros((A + 1, A))
        c1 = np.zeros(A)
        for seq in seqs:
            p2, p1 = S, S
            for x in seq:
                if x < 0:
                    p2, p1 = S, S
                    continue
                c3[p2, p1, x] += 1
                c2[p1, x] += 1
                c1[x] += 1
                p2, p1 = p1, x
        return c3, c2, c1

    def loss(self, seqs):
        tot, n = 0.0, 0
        S = A
        for seq in seqs:
            p2, p1 = S, S
            for x in seq:
                if x < 0:
                    p2, p1 = S, S
                    continue
                q3 = (self.c3[p2, p1, x] + 0.5) / (self.n3[p2, p1] + 0.5 * A)
                q2 = (self.c2[p1, x] + 0.5) / (self.n2[p1] + 0.5 * A)
                q1 = (self.c1[x] + 0.5) / (self.n1 + 0.5 * A)
                tot -= math.log2(0.6 * q3 + 0.3 * q2 + 0.1 * q1)
                n += 1
                p2, p1 = p1, x
        return tot, n


def q3c(corpus, data, n, rng):
    sides = GRID_SIDES
    rows = {s: sym_rows(data, s) for s in sides}
    cnt = {s: Trigram.counts(rows[s]) for s in sides}
    held = {s: [r for i, r in enumerate(rows[s]) if (i + 1) % 5 == 0] for s in sides}
    ranks, losses_all = [], {}
    for i, s in enumerate(sides):
        nb = [sides[j] for j in (i - 1, i + 1) if 0 <= j < len(sides)]
        far = [j for j in range(len(sides)) if abs(j - i) >= 3]
        pairs = []
        for _ in range(200):
            a, b = rng.choice(far, 2, replace=False)
            pairs.append([sides[a], sides[b]])

        def model(group):
            c3 = sum(cnt[g][0] for g in group)
            c2 = sum(cnt[g][1] for g in group)
            c1 = sum(cnt[g][2] for g in group)
            t, k = Trigram(c3, c2, c1).loss(held[s])  # noqa: B023 (called within the same iteration)
            return t / k
        ln = model(nb)
        lr = np.array([model(p) for p in pairs])
        losses_all[s] = np.concatenate([[ln], lr])
        ranks.append(float((lr < ln).mean()))
    obs = float(np.mean(ranks))
    sims = np.empty(n)
    for k in range(n):
        rr = []
        for s in sides:
            v = losses_all[s]
            j = rng.integers(len(v))
            others = np.delete(v, j)
            rr.append(float((others < v[j]).mean()))
        sims[k] = np.mean(rr)
    return {"S3c": {"statistic": "mean rank (0-1) of the neighbour-trained loss among 200 "
                                 "random far pairs (low = neighbours predict better)",
                    "observed": obs, "p_one_sided_low": pval_low(obs, sims),
                    "controls": summ(sims),
                    "per_side_rank": dict(zip(sides, ranks, strict=True))}}


# ---------------------------------------------------------------- Q4

def q4(corpus, data, n, rng):
    kw = calls_words(corpus)
    types = sorted({w for w in kw if len(w) >= 4})

    def grams(sides):
        out = set()
        for s in sides:
            for r in sym_rows(data, s):
                st = "".join(ALPHA[x] if x >= 0 else "#" for x in r)
                for k in range(4, 21):
                    for i in range(len(st) - k + 1):
                        g = st[i:i + k]
                        if "#" not in g:
                            out.add(g)
        return out
    gG, gC = grams(GRID_SIDES), grams(CENTRE_SIDES)
    obs = sum(t in gG for t in types)
    obsC = sum(t in gC for t in types)
    found = [t for t in types if t in gG]
    # the matching strings are written only to the local corpus folder (not published)
    json.dump(found, open(Path(corpus) / "l3_q4_found.json", "w"), indent=0)
    # first-order Markov model of the Calls letters (word-initial and transitions)
    T = np.zeros((A, A))
    S0 = np.zeros(A)
    for w in kw:
        S0[IDX[w[0]]] += 1
        for a, b in zip(w[:-1], w[1:], strict=True):
            T[IDX[a], IDX[b]] += 1
    U = np.bincount([IDX[c] for w in kw for c in w], minlength=A).astype(float)
    P = np.array([T[a] / T[a].sum() if T[a].sum() else U / U.sum() for a in range(A)])
    cumP, cumS = np.cumsum(P, 1), np.cumsum(S0 / S0.sum())
    lens = np.array([len(t) for t in types])
    sims = np.empty(n)
    simsC = np.empty(n)
    for i in range(n):
        m = len(types)
        L = lens.max()
        G = np.zeros((m, L), dtype=np.int64)
        G[:, 0] = np.minimum((rng.random(m)[:, None] > cumS).sum(1), A - 1)
        for t in range(1, L):
            G[:, t] = np.minimum((rng.random(m)[:, None] > cumP[G[:, t - 1]]).sum(1), A - 1)
        ws = ["".join(ALPHA[x] for x in G[j, :lens[j]]) for j in range(m)]
        sims[i] = sum(w in gG for w in ws)
        simsC[i] = sum(w in gC for w in ws)
    # P4b
    grows = [r for s in GRID_SIDES for r in sym_rows(data, s)]
    model = Trigram(*Trigram.counts(grows))

    def H(words):
        t, k = model.loss([[IDX[c] for c in w] for w in words])
        return t / k

    def shuffled(words):
        letters = rng.permutation([c for w in words for c in w])
        out, i = [], 0
        for w in words:
            out.append("".join(letters[i:i + len(w)]))
            i += len(w)
        return out
    hk = H(kw)
    dk_sims = np.array([H(shuffled(kw)) for _ in range(n)])
    dK = float(dk_sims.mean() - hk)
    nlet = sum(len(w) for w in kw)
    refs = {}
    for name, path in (("latin", CORPORA / "la15" / "train.txt"),
                       ("english", CORPORA / "en15" / "train.txt")):
        words = text_words(path)
        ds = []
        for _ in range(1000):
            st = rng.integers(0, len(words) - 2000)
            sample, tot = [], 0
            j = st
            while tot < nlet:
                sample.append(words[j])
                tot += len(words[j])
                j += 1
            ds.append(H(shuffled(sample)) - H(sample))
        refs[name] = np.array(ds)
    allref = np.concatenate([refs["latin"], refs["english"]])
    return {
        "P4a": {"statistic": "Calls word types (4+ letters) found as strings within rows of G",
                "types": len(types), "observed": obs, "p_one_sided": pval_high(obs, sims),
                "controls_pseudowords": summ(sims),
                "in_C_observed": obsC, "in_C_controls": summ(simsC),
                "in_C_p": pval_high(obsC, simsC)},
        "P4b": {"statistic": "Delta = H(letter-shuffled X) - H(X) under a trigram model of G, "
                             "bits per letter; X = Calls",
                "H_calls": hk, "delta_calls": dK,
                "p_vs_calls_shuffles": pval_low(hk, dk_sims),
                "delta_latin": summ(refs["latin"]), "delta_english": summ(refs["english"]),
                "p_one_sided": float((1 + (allref >= dK).sum()) / (1 + len(allref))),
                "calls_letters": nlet},
    }


# ---------------------------------------------------------------- Q5

SERIES_SIDES = ["25b", "26a", "26b", "27a", "27b", "28a", "28b"]


def series_label(flags):
    o = [f for f in flags if f.startswith("orient")]
    return o[0][-1] if o else "0"


def q5(corpus, data, n, rng):
    train = [r for s in GRID_SIDES if s not in SERIES_SIDES for r in sym_rows(data, s)]
    T = np.zeros((A, A))
    for r in train:
        for a, b in zip(r[:-1], r[1:], strict=True):
            if a >= 0 and b >= 0:
                T[a, b] += 1
    LP = -np.log2((T + 0.5) / (T.sum(1, keepdims=True) + 0.5 * A))
    sides = {}
    for s in SERIES_SIDES:
        rows = data[s]
        sym = [np.array([x for x, _, _ in r]) for r in rows]
        lab = [np.array([series_label(f) for _, f, _ in r]) for r in rows]
        sides[s] = (sym, lab)

    def seq_loss(seqs):
        tot, k = 0.0, 0
        for q in seqs:
            if len(q) < 2:
                continue
            a, b = q[:-1], q[1:]
            ok = (a >= 0) & (b >= 0)
            tot += LP[a[ok], b[ok]].sum()
            k += ok.sum()
        return tot, k

    def stat(labels, diagonal=False):
        total = 0.0
        for s, (sym, _) in sides.items():
            lab = labels[s]
            whole = seq_loss(sym)
            if not diagonal:
                parts = [r[lb == v] for r, lb in zip(sym, lab, strict=True)
                         for v in np.unique(lb)]
            else:
                parts = []
                cells = defaultdict(list)
                for i, (r, lb) in enumerate(zip(sym, lab, strict=True)):
                    for j in range(len(r)):
                        cells[(lb[j], j - i)].append(r[j])
                parts = [np.array(v) for v in cells.values()]
            ser = seq_loss(parts)
            total += whole[0] / whole[1] - ser[0] / ser[1]
        return total
    obs_lab = {s: v[1] for s, v in sides.items()}
    obs = stat(obs_lab)
    obs_d = stat(obs_lab, diagonal=True)
    sims, sims_d = np.empty(n), np.empty(n)
    for i in range(n):
        perm = {s: [rng.permutation(lb) for lb in v[1]] for s, v in sides.items()}
        sims[i] = stat(perm)
        sims_d[i] = stat(perm, diagonal=True) if i < 2000 else np.nan
    sims_d = sims_d[~np.isnan(sims_d)]
    # P5c chi-squared, letters x series label, pooled
    labs = ["0", "/", "~", "`"]

    def chi(labels):
        tab = np.zeros((A, 4))
        for s, (sym, _) in sides.items():
            for r, lb in zip(sym, labels[s], strict=True):
                for x, v in zip(r, lb, strict=True):
                    if x >= 0:
                        tab[x, labs.index(v)] += 1
        tab = tab[:, tab.sum(0) > 0]
        exp = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
        small = exp.max(1) < 5
        if small.any():
            tab = np.vstack([tab[~small], tab[small].sum(0, keepdims=True)])
            exp = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
        return float(((tab - exp) ** 2 / exp).sum())
    obs_c = chi(obs_lab)
    sims_c = np.empty(n)
    for i in range(n):
        sims_c[i] = chi({s: [rng.permutation(lb) for lb in v[1]] for s, v in sides.items()})
    # descriptive
    desc = defaultdict(Counter)
    for s, rows in data.items():
        for r in rows:
            if len(r) == 48 and s in GRID_SIDES:
                desc["rows_of_48"][s] += 1
            for _, fl, _ in r:
                if "uncertain" in fl:
                    desc["uncertain"][s] += 1
    sizes = {s: sum(len(r) for r in data[s]) for s in CENTRE_SIDES}
    series_sizes = {s: dict(Counter(v for lb in sides[s][1] for v in lb)) for s in sides}
    return {
        "P5a": {"statistic": "sum over 25b-28b of (bits per pair reading whole rows) - "
                             "(bits per pair reading each series on its own in row order)",
                "observed": obs, "p_one_sided": pval_high(obs, sims), "controls": summ(sims)},
        "S5b": {"statistic": "as P5a, each series read along diagonals",
                "observed": obs_d, "p_one_sided": pval_high(obs_d, sims_d),
                "controls": summ(sims_d), "controls_n": int(len(sims_d))},
        "P5c": {"statistic": "chi-squared, letters x series label, 25b-28b pooled",
                "observed": obs_c, "p_one_sided": pval_high(obs_c, sims_c),
                "controls": summ(sims_c)},
        "descriptive": {"rows_of_48": dict(desc["rows_of_48"]),
                        "uncertain_marks": dict(desc["uncertain"]),
                        "centre_table_cells": sizes, "series_sizes": series_sizes},
    }


TESTS = {"q1": q1, "q2rep": q2rep, "q2pair": q2pair, "q3a": q3a, "q3b": q3b, "q3c": q3c,
         "q4": q4, "q5": q5}


def main():
    global CORPORA
    name, corpus, CORPORA = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 10000
    rng = np.random.default_rng([SEED, TEST_IDS[name]])
    t0 = time.time()
    data = load(corpus)
    body = TESTS[name](corpus, data, n, rng)
    write(name, corpus, n, body, t0)


if __name__ == "__main__":
    main()
