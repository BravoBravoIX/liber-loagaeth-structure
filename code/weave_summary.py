"""Weave study: Holm over the primary family H1-H4 and a short printout; writes
results/weave_summary.json from results/weave_h1.json ... weave_h4.json."""

import json
from pathlib import Path

R = Path(__file__).resolve().parent.parent / "results"


def load(name):
    return json.load(open(R / f"weave_{name}.json"))


def holm(ps):
    order = sorted(ps, key=ps.get)
    out, run = {}, 0.0
    for i, k in enumerate(order):
        run = max(run, min(1.0, (len(ps) - i) * ps[k]))
        out[k] = run
    return out


def main():
    prim = {k: load(k.lower())[k] for k in ("H1", "H2", "H3", "H4")}
    ps = {k: v["p_one_sided"] for k, v in prim.items()}
    hp = holm(ps)
    rows = {k: {"observed": v["observed"], "controls_mean": v["controls"]["mean"],
                "controls_95": [v["controls"]["q025"], v["controls"]["q975"]],
                "p": ps[k], "holm": hp[k]} for k, v in prim.items()}
    out = {"primary": rows}
    json.dump(out, open(R / "weave_summary.json", "w"), indent=1)
    for k, v in rows.items():
        print(k, json.dumps(v))


if __name__ == "__main__":
    main()
