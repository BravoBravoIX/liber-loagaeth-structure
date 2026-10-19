"""L3: collect the ten primary tests and apply Holm's correction (alpha 0.05).
Writes results/l3_summary.json. Usage: l3_summary.py"""

import json

from loag import ROOT

PRIMARY = [("q1", "P1a"), ("q1", "P1b"), ("q2rep", "P2a"), ("q2pair", "P2b"),
           ("q2rep", "P2c"), ("q3a", "P3a"), ("q4", "P4a"), ("q4", "P4b"), ("q5", "P5a"),
           ("q5", "P5c")]


def main():
    rows = []
    for group, test in PRIMARY:
        d = json.load(open(ROOT / "results" / f"l3_{group}.json"))
        t = d[test]
        obs = t.get("observed", t.get("observed_bits", t.get("delta_calls")))
        rows.append({"test": test, "file": f"results/l3_{group}.json", "controls": d["controls"],
                     "observed": obs, "p": t["p_one_sided"]})
    m = len(rows)
    order = sorted(range(m), key=lambda i: rows[i]["p"])
    run = 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (m - k) * rows[i]["p"]))
        rows[i]["p_holm"] = run
        rows[i]["significant_holm_0.05"] = run < 0.05
    out = {"what": "L3 primary family, Holm-corrected", "prereg_commit": "7127723", "tests": rows}
    json.dump(out, open(ROOT / "results" / "l3_summary.json", "w"), indent=1)
    for r in rows:
        print(r["test"], r["observed"], r["p"], round(r["p_holm"], 5), r["significant_holm_0.05"])


if __name__ == "__main__":
    main()
