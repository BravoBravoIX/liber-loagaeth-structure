"""The 48 Calls (Claves Angelicae) as printed in Casaubon's 1659 True & Faithful Relation,
from the EEBO-TCP keyed text A37412 (CC0, public domain).

In 1584 the Calls were dictated word by word (the first ones backwards); Casaubon prints them in
small tables: [number,] the word in capitals as dictated, [the English,] the word written
forwards in ordinary type[, a note]. A word row is a table row of 2-5 cells with one cell in
capitals (letters only) and at least one other cell with lower-case letters. The forward form
is the ordinary-type cell that equals the capitals or their reverse; failing that, the capitals
reversed when the row is numbered (backward dictation), else the capitals as they stand.
Each row is stamped with the nearest preceding section heading (the date of the action).

Writes CORPUS_DIR/calls_words.jsonl and data/calls_manifest.json (counts and hashes only).
Usage: calls.py TCP_A37412_XML CORPUS_DIR
"""

import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from loag import ROOT, sha256


def plain(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]*>", "", s)).strip()


def letters(s):
    s = unicodedata.normalize("NFD", plain(s))
    return "".join(ch for ch in s if ch.isalpha()).lower()


def main():
    src, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    xml = src.read_text(encoding="utf-8")
    heads = [(m.start(), plain(m.group(1))) for m in re.finditer(r"<head>(.*?)</head>", xml, re.S)]
    rows = []
    for t in re.finditer(r"<table>(.*?)</table>", xml, flags=re.S):
        head = ""
        for pos, h in heads:
            if pos < t.start():
                head = h
        for r in re.findall(r"<row>(.*?)</row>", t.group(1), flags=re.S):
            cells = [plain(c) for c in re.findall(r"<cell>(.*?)</cell>", r, flags=re.S)]
            if not 2 <= len(cells) <= 5:
                continue
            caps_i = [i for i, c in enumerate(cells)
                      if re.fullmatch(r"[A-Z][A-Z ]*\.?", c) and not c.isdigit()]
            if not caps_i:
                continue
            ci = caps_i[0]
            caps = letters(cells[ci])
            others = [letters(c) for i, c in enumerate(cells) if i != ci]
            if not any(re.search(r"[a-z]", c) for i, c in enumerate(cells) if i != ci):
                continue
            numbered = cells[0].rstrip(".").isdigit()
            if caps in others:
                fwd, how = caps, "printed"
            elif caps[::-1] in others:
                fwd, how = caps[::-1], "printed_reversed"
            elif numbered:
                fwd, how = caps[::-1], "inferred_reversed"
            else:
                fwd, how = caps, "inferred"
            rows.append({"head": head, "n": int(cells[0].rstrip(".")) if numbered else None,
                         "caps": caps, "forward": fwd, "how": how,
                         "line": xml.count("\n", 0, t.start()) + 1})
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "calls_words.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    lets = Counter(ch for r in rows for ch in r["forward"])
    man = {
        "what": "48 Calls from Casaubon 1659 (EEBO-TCP A37412, CC0): dictation-table word rows",
        "input_sha256": sha256(src),
        "output_sha256": sha256(outdir / "calls_words.jsonl"),
        "word_rows": len(rows),
        "how": dict(Counter(r["how"] for r in rows)),
        "letters": sum(lets.values()),
        "word_types": len({r["forward"] for r in rows}),
        "rows_by_heading": dict(Counter(r["head"][:60] for r in rows)),
    }
    json.dump(man, open(ROOT / "data" / "calls_manifest.json", "w"), indent=1, ensure_ascii=False)
    print(json.dumps(man, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
