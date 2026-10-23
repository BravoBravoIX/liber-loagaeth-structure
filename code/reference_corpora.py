"""Build the two period reference texts used by Q1 and Q4: Latin (la15) and English (en15).

Vendored from the author's solvability-first-framework (targets/corpora_period/latin/build.py,
build_norm part, and targets/corpora_period/english/build.py, commit 3a7e8c1) and from the
train/held-out split of the author's private working repository (function split_lines). The cleaning
rules are unchanged; only the input folders and the output step differ. The study used the
"train" part of each split, as here.

  la15: Latin Wikisource (CC BY-SA 4.0), Alberti, De pictura (1435) and five works of Nicolaus
        Cusanus (1440-1450), at the page revisions fetched by scripts/fetch_sources.sh.
  en15: Project Gutenberg (public domain) editions in original spelling, c. 1380-1509: Chaucer's
        Boece and Astrolabe (Skeat), the Paston Letters (Gairdner, vols. 2-6), Caxton's Chesse
        (Axon), the Book of Quinte Essence (Furnivall) and the Forme of Cury (Pegge).

Neither text is redistributed here. Writes OUT_DIR/la15/train.txt and OUT_DIR/en15/train.txt
(git-ignored) and data/reference_corpora.json (hashes and counts only).

Usage: reference_corpora.py SOURCE_DIR OUT_DIR    (SOURCE_DIR/latin/*.html, SOURCE_DIR/english/pg*.txt)
"""

from __future__ import annotations

import collections
import hashlib
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_LA = RAW_EN = None  # set in main()

# Wikisource pages in output order
NORM_ORDER = [
    "De_pictura__Prologus", "De_pictura__Liber_I", "De_pictura__Liber_II",
    "De_pictura__Liber_III",
    "De_docta_ignorantia__Dedicatio", "De_docta_ignorantia__1", "De_docta_ignorantia__2",
    "De_docta_ignorantia__3", "De_coniecturis", "Apologia_doctae_ignorantiae",
    "Idiota_de_mente",
]

# ---------------------------------------------------------------- split (split_lines)

BLOCK_CHARS = 4000  # split block size (whole lines, about this many characters)
HELDOUT_EVERY = 10  # every 10th block is held out


def split_lines(lines: list[str]) -> tuple[list[str], list[str]]:
    """Deterministic split into blocks of whole lines of about ``BLOCK_CHARS`` characters;
    every ``HELDOUT_EVERY``-th block is held out. Long lines are cut at a space so corpora made of
    a few very long lines still split. Blocks keep local context together."""
    pieces: list[str] = []
    for ln in lines:
        while len(ln) > BLOCK_CHARS:
            cut = ln.rfind(" ", 0, BLOCK_CHARS)
            cut = cut if cut > 0 else BLOCK_CHARS
            pieces.append(ln[:cut])
            ln = ln[cut:].lstrip()
        pieces.append(ln)
    train, held, block, size = [], [], 0, 0
    for ln in pieces:
        (held if block % HELDOUT_EVERY == HELDOUT_EVERY - 1 else train).append(ln)
        size += len(ln) + 1
        if size >= BLOCK_CHARS:
            block, size = block + 1, 0
    return train, held


# ---------------------------------------------------------------- Latin Wikisource (latin/build.py)

_DROP_CLASSES = {"ws-noexport", "mw-editsection", "titulusHeaderBox", "pagenum",
                 "reference", "references", "mw-references-wrap", "mw-heading", "ws-pagenum",
                 "noprint", "mw-cite-backlink", "sectionnotes"}
_DROP_TAGS = {"table", "style", "script", "h1", "h2", "h3", "h4", "h5", "h6", "sup",
              "center", "ol"}
_VOID = {"br", "img", "meta", "hr", "input", "link", "wbr"}
_BLOCK = {"p", "div", "li", "dd", "dt", "poem", "blockquote"}


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []  # (tag, dropped incl. by an ancestor)
        self.paras: list[str] = []
        self.cur: list[str] = []

    def _dropped(self) -> bool:
        return bool(self.stack) and self.stack[-1][1]

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        drop = (self._dropped() or tag in _DROP_TAGS or bool(cls & _DROP_CLASSES)
                or a.get("id") in ("ws-data", "infoedit", "textquality"))
        if tag in _BLOCK or tag == "br":
            self._flush()
        if tag not in _VOID:
            self.stack.append((tag, drop))

    def handle_endtag(self, tag):
        if tag in _VOID:
            return
        for k in range(len(self.stack) - 1, -1, -1):  # tolerate unclosed tags
            if self.stack[k][0] == tag:
                del self.stack[k:]
                break
        if tag in _BLOCK:
            self._flush()

    def handle_data(self, data):
        if not self._dropped():
            self.cur.append(data)

    def _flush(self):
        t = re.sub(r"\s+", " ", "".join(self.cur)).strip()
        if t:
            self.paras.append(t)
        self.cur = []


def clean_para(t: str) -> str:
    t = re.sub(r"\[[^\]]*\]", " ", t)          # editorial brackets, folio refs, note marks
    t = re.sub(r"<[^>]*>", " ", t)              # editorial angle-bracket insertions
    t = re.sub(r"_{3,}", " ", t)
    t = re.sub(r"^\d+\.\s+", "", t)           # editor's paragraph numbers (De pictura)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def html_paras(path: Path) -> list[str]:
    p = _Text()
    p.feed(path.read_text(encoding="utf-8"))
    p._flush()
    out = []
    for t in p.paras:
        t = clean_para(t)
        if len(t.split()) < 3 or re.fullmatch(r"Doctae Ignorantiae Liber \w+", t):
            continue                            # stray titles, separators
        out.append(t)
    return out


def build_norm() -> list[str]:
    paras = []
    for slug in NORM_ORDER:
        paras += html_paras(RAW_LA / f"{slug}.html")
    return paras



# ---------------------------------------------------------------- English Gutenberg (english/build.py)

PASTON_VOLS = [40989, 41024, 41081, 42239, 42240]

# ---------------------------------------------------------------- shared helpers


def gutenberg_body(n: int) -> str:
    t = (RAW_EN / f"pg{n}.txt").read_text(encoding="utf-8").replace("\r\n", "\n")
    start = t.index("\n", t.index("*** START OF THE PROJECT GUTENBERG"))
    return t[start:t.index("*** END OF THE PROJECT GUTENBERG")]


def between(text: str, start: str, end: str) -> str:
    i = text.index(start)
    return text[i:text.index(end, i)]


def paragraphs(text: str) -> list[str]:
    return [p for p in re.split(r"\n[ \t]*\n", text) if p.strip()]


def drop_brackets(t: str) -> str:
    """Remove editorial brackets; keep letters restored inside a word (``Richa[rd]``)."""
    t = re.sub(r"\[\[[^\[\]]*\]\]", " ", t)                    # transcriber's notes
    t = re.sub(r"\[(\d+[.\-]?\d*|\*|[a-z])\]", " ", t)         # footnote references
    t = re.sub(r"\[_[^\[\]]*_\]|\[£[^\[\]]*\]", " ", t)        # glosses, modern sums
    for _ in range(3):                                          # nested brackets
        t = re.sub(r"(?<=\w)\[([^\[\]\s]+)\]|\[([^\[\]\s]+)\](?=\w)",
                   lambda m: m.group(1) or m.group(2), t)
        t = re.sub(r"\[[^\[\]]*\]", " ", t)
    return t.replace("[", " ").replace("]", " ")


def tidy(t: str) -> str:
    t = re.sub(r"\(_?sic_?\)|\(\?\)", " ", t)
    t = t.replace("^", "").replace("{", "").replace("}", "").replace("_", "")
    return re.sub(r"\s+", " ", t).strip()


def is_caps(t: str) -> bool:
    letters = [c for c in t if c.isalpha()]
    return bool(letters) and sum(c.isupper() for c in letters) >= 0.8 * len(letters)


# ---------------------------------------------------------------- Skeat's Chaucer


def skeat(text: str, numbered_paras: bool) -> list[str]:
    """Indented text lines of Skeat's edition, margin line numbers dropped."""
    out: list[str] = []
    for para in paragraphs(text):
        words: list[str] = []
        for line in para.split("\n"):
            ind = len(line) - len(line.lstrip(" "))
            if ind < 2:                       # headings, Latin incipits, apparatus
                continue
            m = re.search(r"\s+(\d+)\s*$", line)
            if m and int(m.group(1)) % 5 == 0:
                line = line[:m.start()]
            words.append(line.strip())
        t = " ".join(w for w in words if w)
        if re.match(r"(EXPLICIT|INCIPIT|Explicit|Incipit)\b", t):   # Latin colophons
            continue
        if numbered_paras:
            t = re.sub(r"^(\d+|[IVX]+)\.\s+", "", t)
        t = tidy(drop_brackets(t))
        if t:
            out.append(t)
    return out


def boece() -> list[str]:
    text = between(gutenberg_body(44833), "\nBOETHIUS DE CONSOLATIONE PHILOSOPHIE.\n",
                   "\nTROILUS AND CRISEYDE.\n")
    return skeat(text, numbered_paras=False)


def astrolabe() -> list[str]:
    text = between(gutenberg_body(45027), "\nA TREATISE ON THE ASTROLABE.\n",
                   "\nSUPPLEMENTARY PROPOSITIONS.\n")
    return skeat(text, numbered_paras=True)


# ---------------------------------------------------------------- Paston Letters

_QUOTE = re.compile(r"‘[^’]*’(?![a-z])|“[^”]*”")
_WORD = re.compile(r"[^\W\d_]+")
_EN = set("the and of to that ye yow you hym him hys his it was be ben for with wyth not my "
          "this thys as by so but they thei hem shall shal xal schal wole wolde wold shuld "
          "schuld ther there whiche which have hath had hadde is i we your youre yowr sir "
          "syr god lord here her".split())
_FR = set("le la les de des du et vous nous que qui pur pour est sont en au aux ma mon son "
          "sa ses vostre nostre dit ceste avez estre par sur tres jeo je soit".split())
_LA = set("et est ad cum pro per non sunt qui quae ut sed dictus dicta dicti dictum "
          "dicto dictæ dictis apud ejus eius nos vos ac atque vel anno domini die sibi suis "
          "suo sua esse fuit quam hoc ab ex super inter".split())
_CUE = re.compile(r"\b(Fenn|MSS?\.|vol\.|letter|written|endorsed|Endorsed|following|"
                  r"above|below|appears|probably|evidently|apparently|editor|Editor|document|"
                  r"copy|printed|dated|abstract|Abstract|No\. \d)")
# Rare in the letters, common in the editor's prose.
_STRONG_CUE = re.compile(r"\b(Fenn|MSS?\.|vol\.|editor|Editor|abstract|probably|apparently|"
                         r"evidently|appears|page \d|account of|resided|manuscripts?)\b")
# Gairdner's abstracts open with a verb and no subject ("Begs him ...", "Thanks him ...").
_ABSTRACT_VERB = re.compile(r"(Begs|Thanks|Complains|Desires|Informs|Reminds|Sends|Has|Is|Was|"
                            r"Hears|Understands|Asks|Requests|Prays|Encloses|Acknowledges|"
                            r"Reports|Giving|Writes|Wishes|Promises|Advises|Urges) [a-z]")


def _paston_entries() -> list[tuple[int, str]]:
    entries = []
    for n in PASTON_VOLS:
        t = gutenberg_body(n)
        m = re.search(r"\nTHE PASTON LETTERS\n\n_(Henry|Edward|Richard)[^\n]*_\n", t)
        t = t[m.start():]
        if "\nAPPENDIX\n" in t:                  # wills, mostly Latin (vol. 6)
            t = t[:t.index("\nAPPENDIX\n")]
        parts = re.split(r"\n\n(\d{1,4})\n\n", "\n\n" + t)
        entries += [(int(parts[i]), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    return entries


def _editorial_vocab(entries: list[tuple[int, str]]) -> set[str]:
    """Words of the editor's own prose: notes, sidenotes, abstracts (quotations removed)."""
    c: collections.Counter[str] = collections.Counter()
    for _, text in entries:
        ps = paragraphs(text)
        abstract = bool(ps) and ps[0].strip().startswith("ABSTRACT")
        for p in ps:
            s = p.strip()
            if (s.startswith("[") and not s.startswith("[[")) or abstract:
                c.update(w.lower() for w in _WORD.findall(_QUOTE.sub(" ", s)))
    return {w for w, k in c.items() if k >= 2}


def _editorial(p: str, vocab: set[str]) -> bool:
    """The editor's modern-English remarks and unlabelled abstracts.

    A paragraph is the editor's when it is an inline abstract (``448.--``), or when nearly all
    its words (quotations aside) occur in the editor's own notes: share >= 0.9 with at least 8
    words, a cue word or a closing ``:--``; share >= 0.85 with a cue word; share >= 0.75 with a
    cue that is rare in the letters or an abstract's opening verb; share >= 0.6 with an arabic
    numeral (the writers use roman numerals). Endorsement notes, quoted later abstracts
    (``‘4. John Paston ...``) and the printer's colophon are dropped. Addresses
    (``To my ...``) and account items (``Item, ...``) are the writers' and are kept.
    """
    s = p.strip()
    if re.match(r"\d+\.--|_?Endorsed|Printed by ", s) or re.search(r"\bpage \d", s):
        return True
    if re.match(r"‘\d", s):                       # later abstracts quoted by the editor
        return True
    if re.match(r"_?(To|Item)\b", s):
        return False
    ws = [w.lower() for w in _WORD.findall(_QUOTE.sub(" ", s))]
    if not ws:
        return False
    share = sum(w in vocab for w in ws) / len(ws)
    if re.search(r"\d", drop_brackets(s)) and share >= 0.6:  # writers use roman numerals
        return True
    cue = bool(_CUE.search(s)) or bool(re.search(r":_?--_?\s*$", s))
    return ((share >= 0.9 and (len(ws) >= 8 or cue))
            or (share >= 0.85 and cue and len(ws) >= 5)
            or (share >= 0.75 and (bool(_STRONG_CUE.search(s)) or bool(_ABSTRACT_VERB.match(s)))))


def _language(p: str) -> str:
    ws = [w.lower() for w in _WORD.findall(p)]
    en, fr, la = (sum(w in s for w in ws) for s in (_EN, _FR, _LA))
    if en >= max(fr, la) and (en >= 2 or fr + la == 0 or len(ws) < 5):
        return "en"
    return "fr" if fr > la else "la"


def paston() -> tuple[list[str], collections.Counter[str]]:
    entries = _paston_entries()
    vocab = _editorial_vocab(entries)
    out: list[str] = []
    dropped: collections.Counter[str] = collections.Counter()
    for _, text in entries:
        ps = paragraphs(text)
        if not ps or ps[0].strip().startswith("ABSTRACT"):
            dropped["abstract entries"] += 1
            continue
        depth = 0
        for i, p in enumerate(ps):
            s = p.strip()
            opened = depth > 0 or s.startswith("[")
            depth = max(0, depth + s.count("[") - s.count("]"))
            if opened or s.count("]") > s.count("["):   # bracketed notes, sidenotes
                dropped["bracketed"] += 1
                continue
            if i == 0 and is_caps(drop_brackets(s)):     # editor's heading
                continue
            if _editorial(s, vocab):
                dropped["editorial"] += 1
                continue
            lang = _language(drop_brackets(s))
            if lang != "en":
                dropped[lang] += 1
                continue
            lines = [ln for ln in s.split("\n") if not is_caps(drop_brackets(ln))]
            t = re.sub(r"^\d+\.\s+", "", tidy(drop_brackets(" ".join(lines))))
            if re.search(r"[^\W\d_]", t):            # editor's item numbers dropped above
                out.append(t)
    return out, dropped


# ---------------------------------------------------------------- Caxton, Chesse


def chesse() -> list[str]:
    text = between(gutenberg_body(10672), "[DEDICATION.]", "\nGLOSSARY\n")
    text = text[:text.index("[Footnote 42:")]
    out = []
    for p in paragraphs(text):
        s = p.strip()
        if re.fullmatch(r"\[[A-Z .]+\]|\[Illustration\.?\]", s) or is_caps(s):
            continue
        s = re.sub(r"\[\d+\]", " ", s)                           # footnote references
        s = re.sub(r"\[Blackletter:\s*([^\]]*)\]", r"\1", s)
        s = re.sub(r"\[=(\w)\]", lambda m: m.group(1) + "\u0304", s)
        s = re.sub(r"(?<=[^\W\d_])['*]?9", "\ua770", s)         # -us abbreviation
        s = re.sub(r"(?<=[^\W\d_])'(?=[^\W\d_])", "", s)        # y'e, y't
        s = re.sub(r"(?<=[^\W\d_])3(?=t)", "c", s)   # ct ligature (corre3tion)
        t = tidy(drop_brackets(s))
        if t:
            out.append(t)
    return out


# ---------------------------------------------------------------- Book of Quinte Essence


def quinte() -> list[str]:
    text = between(gutenberg_body(17179), "      [[Fol. 10.]]", "ON THE CHEMISTRY OF THE TEXT")
    text = text[:text.rindex("NOTES")]
    out = []
    for para in paragraphs(text):
        words, depth = [], 0
        for line in para.split("\n"):
            s = line.strip()
            ind = len(line) - len(line.lstrip(" "))
            if depth > 0 or s.startswith("["):              # notes, sidenotes, folios
                depth = max(0, depth + s.count("[") - s.count("]"))
                continue
            if not s or is_caps(s) or ind not in (0, 8):     # headings, Latin explicits
                continue
            words.append(re.sub(r"\s{2,}\d+$", "", line).strip())
        t = tidy(drop_brackets(" ".join(words)))
        if t:
            out.append(t)
    return out


# ---------------------------------------------------------------- Forme of Cury


def cury() -> list[str]:
    body = gutenberg_body(8102)
    parts = [between(body, "FOR TO MAKE GRONDEN BENES", "[1]XPLICIT."),
             between(body, "ANCIENT COOKERY. A.D. 1381.",
                     "EXPLICIT DE COQUINA QUE EST OPTIMA MEDICINA.")]
    out = []
    for text in parts:
        for p in paragraphs(text):
            s = p.strip()
            if re.match(r"\[\d+\]", s) or s.startswith("_"):    # notes, Latin rubrics
                continue
            lines = [ln for ln in s.split("\n") if not is_caps(ln)]
            t = tidy(drop_brackets(" ".join(lines)))
            if t and not re.fullmatch(r"[IVXLC. ]+", t):
                out.append(t)
    return out



# ---------------------------------------------------------------- output


def build_english() -> list[str]:
    pas, _dropped = paston()
    works = {"boece": boece(), "astrolabe": astrolabe(), "paston": pas, "chesse": chesse(),
             "quinte_essence": quinte(), "forme_of_cury": cury()}
    lines = []
    for paras in works.values():
        lines += [unicodedata.normalize("NFC", p) for p in paras if _language(p) == "en"]
    return lines


def main() -> int:
    global RAW_LA, RAW_EN
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    RAW_LA, RAW_EN = src / "latin", src / "english"
    manifest = {"what": "Period reference texts (train part), rebuilt locally; not redistributed"}
    for name, lines in (("la15", [unicodedata.normalize("NFC", s) for s in build_norm()]),
                        ("en15", build_english())):
        source_text = "\n".join(lines) + "\n"   # the built file of the source project
        train, held = split_lines(source_text.splitlines())
        d = out / name
        d.mkdir(parents=True, exist_ok=True)
        data = ("\n".join(train) + "\n").encode("utf-8")
        (d / "train.txt").write_bytes(data)
        manifest[name] = {"source_lines": len(lines), "train_lines": len(train),
                          "heldout_lines": len(held), "train_words": len(data.split()),
                          "train_sha256": hashlib.sha256(data).hexdigest()}
        print(name, manifest[name])
    json.dump(manifest, open(ROOT / "data" / "reference_corpora.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
