"""L0: parse Peterson's Esoteric Archives edition of Sloane MS 3189 into a coordinate-addressed
corpus, one record per cell.

Input: a local copy of sl3189.htm (scripts/fetch_sources.sh; (c) Joseph H. Peterson, research
use only, not redistributed).
Output (under CORPUS_DIR, which git ignores; never published):
  cells.jsonl  one JSON object per cell:
     side      "2a" ... "48b" (Peterson's leaf numbering; "1a", "1b" are the word leaves)
     leaf, face
     layout    "words" (1a, 1b running text), "grid" (2a-28b, 49 x 49 tables, and the
               single-letter rows at the end of 1b), "centre" (29a-48b, partly filled
               tables printed centred; the column is estimated, not given)
     row, col  1-based; for "words" col is the letter index within the row
     col_exact true when the column is the printed column (grid), false when estimated
     cell      the cell's characters as printed, marks removed (may be 2+ characters,
               a digit, or a capital)
     letters   the cell's letters, lower case, accents removed (digits kept)
     flags     list of: uncertain (?), word_end (.), comma, colon, semicolon,
               apostrophe, caret, accent:<name>, capital, digit, orient:/ orient:~
               orient:` (Peterson's letter-orientation marks, leaves 25b-28b), small
               (printed in small type), struck (struck through), multi (2+ letters)
     row_flags list of: sic (Peterson's [sic] on the row)
  rows.json   per side and row: number of cells and letters
Writes data/corpus_manifest.json (counts and SHA-256 of input and outputs; no text).

Usage: corpus.py SL3189_HTM CORPUS_DIR
"""

import hashlib
import html
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMBINING = {"́": "acute", "̀": "grave", "̂": "circumflex", "̄": "macron",
             "̃": "tilde", "̇": "dot", "̈": "diaeresis", "̋": "dacute",
             "̍": "vline"}
PUNCT = {".": "word_end", ",": "comma", ":": "colon", ";": "semicolon", "'": "apostrophe",
         "^": "caret"}
ORIENT = {"/", "~", "`"}
SMALL_OPEN, SMALL_CLOSE, STRUCK_OPEN, STRUCK_CLOSE = "\x01", "\x02", "\x03", "\x04"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()



def sections(text):
    """Split the leaf part of the page into sides, in page order."""
    start = text.index("id=l1a>")
    end = text.index('<A NAME="s1">')
    body = text[start - 4:end]
    pat = re.compile(r'<H\d id=l(\d+[ab])>|<A NAME="l(\d+[ab])">')
    marks = list(pat.finditer(body))
    out = []
    for i, m in enumerate(marks):
        side = m.group(1) or m.group(2)
        stop = marks[i + 1].start() if i + 1 < len(marks) else len(body)
        out.append((side, body[m.end():stop]))
    return out


def clean_markup(s):
    """Keep only text, with small-type and strike-through spans marked by control chars."""
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r'<FONT COLOR=#FF0000>.*?</FONT>', "", s, flags=re.S | re.I)
    s = re.sub(r'<FONT=COLOR=#FF0000>.*?</FONT>', "", s, flags=re.S | re.I)
    s = re.sub(r"<FONT SIZE=1>(.*?)</FONT>", SMALL_OPEN + r"\1" + SMALL_CLOSE, s, flags=re.S)
    s = re.sub(r"<(s|STRIKE)>(.*?)</\1>", STRUCK_OPEN + r"\2" + STRUCK_CLOSE, s, flags=re.S)
    s = re.sub(r"<SUP>.*?</SUP>", "", s, flags=re.S)
    s = re.sub(r"<[^>]*>", "", s)
    s = s.replace("&3769;", "&#769;")  # a typo in the edition (leaf 1a)
    s = html.unescape(s)
    return unicodedata.normalize("NFD", s)


def tokenise(line, allow_digits=True):
    """Cells of one printed row. A cell starts after a separator (space, a word mark or other
    punctuation, '?') or at an orientation mark; letters written together form one cell."""
    cells = []
    cur = None
    pending = []
    small = struck = False
    sic = False
    if "[sic]" in line:
        sic = True
        line = line.replace("[sic]", " ")
    for ch in line:
        if ch == SMALL_OPEN:
            small = True
            continue
        if ch == SMALL_CLOSE:
            small = False
            continue
        if ch == STRUCK_OPEN:
            struck = True
            cur = None
            continue
        if ch == STRUCK_CLOSE:
            struck = False
            cur = None
            continue
        if ch in COMBINING:
            if cur is not None:
                cur["flags"].append("accent:" + COMBINING[ch])
            continue
        if unicodedata.combining(ch):
            if cur is not None:
                cur["flags"].append("accent:other")
            continue
        if ch.isalpha() or (allow_digits and ch.isdigit()):
            if cur is None:
                cur = {"cell": "", "flags": pending}
                pending = []
                if small:
                    cur["flags"].append("small")
                if struck:
                    cur["flags"].append("struck")
                cells.append(cur)
            cur["cell"] += ch
            continue
        if ch in ORIENT:
            pending = ["orient:" + ch]
            cur = None
            continue
        if ch == "?":
            if cur is not None:
                cur["flags"].append("uncertain")
            cur = None
            continue
        if ch in PUNCT:
            if cur is not None:
                cur["flags"].append(PUNCT[ch])
            cur = None
            continue
        # space, hyphen, brackets, daggers and anything else separate cells
        cur = None
    for c in cells:
        letters = c["cell"].lower()
        c["letters"] = letters
        if any(x.isupper() for x in c["cell"]):
            c["flags"].append("capital")
        if any(x.isdigit() for x in c["cell"]):
            c["flags"].append("digit")
        if len(c["cell"]) > 1:
            c["flags"].append("multi")
    return cells, sic


def grid_rows(block, side):
    lines = [ln for ln in block.split("\n") if ln.strip()]
    numbered = sum(bool(re.match(r"\s*\d+\.", ln)) for ln in lines) > len(lines) / 2
    rows = []
    for ln in lines:
        if numbered:
            ln = re.sub(r"^\s*\d+\.", "", ln)
        cells, sic = tokenise(ln)
        if cells:
            rows.append((cells, sic))
    return rows


KEEP = ("small", "struck", "capital", "multi")


def word_rows(part):
    """Leaves 1a and 1b: numbered paragraphs of words, each a row."""
    part = re.sub(r'<TD CLASS=NOTE>.*?</TD>', "", part, flags=re.S | re.I)
    part = re.sub(r"<PRE.*?</PRE>", "", part, flags=re.S | re.I)
    part = re.sub(r"<IMG[^>]*>", "", part, flags=re.I)
    part = re.sub(r"<em class=pg[^>]*>.*?</em>", "", part, flags=re.S | re.I)
    text = clean_markup(part)
    # a row starts at a line beginning "N." or "N [*M.]" (Peterson's row number, with the
    # renumbered row in brackets); rows are numbered here in page order
    starts = list(re.finditer(r"(?m)^\s*(\d+)(?:\.\s*(?:\[\*\d+\.\])?|\s*\[\*\d+\.\])\s*", text))
    rows = []
    for k, m in enumerate(starts):
        body = text[m.end():starts[k + 1].start() if k + 1 < len(starts) else len(text)]
        body = re.sub(r"\[[^\]]*\]", " ", body).replace("\n", " ")  # editorial brackets
        cells, sic = tokenise(body, allow_digits=False)
        letters = []
        for c in cells:  # in running text, each letter is a position; the word ends at a space
            for j, ch in enumerate(c["cell"]):
                fl = [f for f in c["flags"] if f in ("small", "struck", "capital")]
                if j == len(c["cell"]) - 1:
                    fl += [f for f in c["flags"] if f not in KEEP]
                    fl.append("word_end") if "word_end" not in fl else None
                letters.append({"cell": ch, "letters": ch.lower(), "flags": fl})
        rows.append((k + 1, letters, sic))
    return rows


def main():
    src, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    outdir.mkdir(parents=True, exist_ok=True)
    text = src.read_text(encoding="latin-1")
    records = []
    rows_info = {}
    for side, part in sections(text):
        leaf, face = int(side[:-1]), side[-1]
        recs = []
        if side in ("1a", "1b"):
            for rno, letters, sic in word_rows(part):
                for col, c in enumerate(letters, 1):
                    recs.append(dict(side=side, leaf=leaf, face=face, layout="words", row=rno,
                                     col=col, col_exact=True, **c,
                                     row_flags=["sic"] if sic else []))
            if side == "1b":  # the last rows of 1b, one letter each, printed as a grid
                for block in re.findall(r"<PRE[^>]*>(.*?)</PRE>", part, flags=re.S | re.I):
                    start = max([r["row"] for r in recs] + [0])
                    for i, (cells, sic) in enumerate(grid_rows(clean_markup(block), side), 1):
                        for col, c in enumerate(cells, 1):
                            recs.append(dict(side=side, leaf=leaf, face=face, layout="grid",
                                             row=start + i, col=col, col_exact=True, **c,
                                             row_flags=["sic"] if sic else []))
        elif leaf <= 28:
            blocks = re.findall(r"<PRE[^>]*>(.*?)</PRE>", part, flags=re.S | re.I)
            assert len(blocks) == 1, (side, len(blocks))
            for r, (cells, sic) in enumerate(grid_rows(clean_markup(blocks[0]), side), 1):
                for col, c in enumerate(cells, 1):
                    recs.append(dict(side=side, leaf=leaf, face=face, layout="grid", row=r,
                                     col=col, col_exact=True, **c,
                                     row_flags=["sic"] if sic else []))
        else:
            cen = re.findall(r"<CENTER>(.*?)</CENTER>", part, flags=re.S | re.I)
            for r, block in enumerate(cen, 1):
                cells, sic = tokenise(clean_markup(block).replace("\n", " "))
                n = len(cells)
                for i, c in enumerate(cells, 1):
                    recs.append(dict(side=side, leaf=leaf, face=face, layout="centre", row=r,
                                     col=(49 - n) // 2 + i, col_exact=False, **c,
                                     row_flags=["sic"] if sic else []))
        records.extend(recs)
        per_row = Counter((r["row"]) for r in recs)
        rows_info[side] = {str(k): v for k, v in sorted(per_row.items())}

    cells_path = outdir / "cells.jsonl"
    with open(cells_path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rows_path = outdir / "rows.json"
    json.dump(rows_info, open(rows_path, "w"), indent=0)

    # counts only (no text) for the manifest in git
    by_layout = Counter(r["layout"] for r in records)
    letters = Counter()
    flags = Counter()
    for r in records:
        for ch in r["letters"]:
            letters[ch] += 1
        for fl in r["flags"]:
            flags[fl.split(":")[0] if fl.startswith("accent") else fl] += 1
    per_side = {}
    for side in rows_info:
        rs = [r for r in records if r["side"] == side]
        leaf = int(side[:-1])
        per_side[side] = {"folio": (f"{leaf + 8}{'r' if side[-1] == 'a' else 'v'}" if leaf >= 2
                                    else None),
                          "layout": rs[0]["layout"] if rs else None, "rows": len(rows_info[side]),
                          "cells": len(rs), "alpha_letters": sum(ch.isalpha() for r in rs
                                                                 for ch in r["letters"]),
                          "rows_not_49": sum(v != 49 for v in rows_info[side].values())}
    manifest = {
        "what": "Coordinate-addressed corpus of Liber Loagaeth from Peterson's edition (L0)",
        "input": {"file": "peterson/sl3189.htm", "sha256": sha256(src)},
        "outputs": {"cells.jsonl": sha256(cells_path), "rows.json": sha256(rows_path)},
        "sides": len(rows_info),
        "cells": len(records),
        "cells_by_layout": dict(by_layout),
        "alpha_letters": sum(v for k, v in letters.items() if k.isalpha()),
        "digits": sum(v for k, v in letters.items() if k.isdigit()),
        "letter_counts": dict(sorted(letters.items())),
        "flag_counts": dict(sorted(flags.items())),
        "rows_with_sic": sum(1 for r in {(x["side"], x["row"]) for x in records
                                         if "sic" in x["row_flags"]}),
        "folio_note": "folio = leaf + 8 (recto a, verso b): Peterson marks f. 10r at leaf 2a; "
                      "confirmed on the images of 8 sides (data/image_checks.json)",
        "per_side": per_side,
    }
    json.dump(manifest, open(ROOT / "data" / "corpus_manifest.json", "w"), indent=1)
    print(json.dumps({k: manifest[k] for k in ("sides", "cells", "cells_by_layout",
                                               "alpha_letters", "digits", "flag_counts")},
                     indent=1))


if __name__ == "__main__":
    main()
