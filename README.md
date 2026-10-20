# Liber Loagaeth: a pre-registered structural study of the tables

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23487865.svg)](https://doi.org/10.5281/zenodo.23487865)

*Liber Loagaeth* (British Library, Sloane MS 3189) is the book of letter tables that John Dee
and Edward Kelley received in their sessions with spirits in 1583; the surviving copy is in
Kelley's hand. After two leaves of running text it has 94 table sides: 54 full tables of
49 × 49 cells (leaves 2–28) and 40 partly filled ones (leaves 29–48). No reading of the
tables is known.

This study does not try to read it. It asks how the tables were made: whether the letters
behave like random filling, like a mechanical rule, or like text; whether the sides were made
in pairs; and whether the tables share anything with the 48 Calls that Dee and Kelley received
the next year. It first builds a checked, cell-by-cell corpus, reproduces and corrects the one
earlier computational study (Zubair 2026), and then runs ten tests written down and committed
before any of them was scored, each against 10,000 controls, with Holm's correction.
Version 1.1 adds a second, separately pre-registered study of how the two letter series of
pages 25b–28b are laid into the grid (section 4, "Pages 25b–28b").

This is a structural study, not a decipherment. Nothing here is a reading or a translation, and
no grid paths are searched for words. Where the evidence is short of proof, this README says
"the evidence weighs toward".

October 2026. CPU only; Python with numpy. The whole analysis reruns in about an hour and a half,
almost all of it one test.

**Archived on Zenodo** with its paper, code, data and results: [doi:10.5281/zenodo.23487865](https://doi.org/10.5281/zenodo.23487865) (this DOI always opens the latest version; see How to cite at the end).

**The paper:** [`paper/liber-loagaeth.pdf`](paper/liber-loagaeth.pdf) (working paper: abstract,
method, results, discussion and references; built from `paper/liber-loagaeth.typ` by
`paper/build.sh`). The README below covers the same ground in more detail.

## In short

| Question | Answer | How firm |
|---|---|---|
| Is the corpus sound? | 96 sides, 196,721 cells, 196,353 letters, every cell addressed by side, row and column | 78 of 80 randomly chosen cells agree with the page images, 2 doubtful, none wrong. The only other machine-readable grids (lorselq) turn out to be a copy of the same edition, not an independent check |
| Are Zubair's (2026) counts right? | They count the whole web page, headings and notes included; his lowest index of coincidence (0.044) is an appendix of four *Book of Soyga* tables, not Loagaeth | Our emulation of his count lands within 25 letters of his on every side; for 48b it gives his IC exactly. Loagaeth's own range is 0.060–0.102 |
| Do the tables follow the *Soyga* rule (Zubair)? | No, and they are not "anti-correlated" with it either | With the right baseline (each table's own letters) no table departs from chance after Holm's correction (smallest raw p 0.013, Holm 0.19) |
| Do long strings recur? | Yes, far beyond chance, and mostly across different sides | 6,679 distinct 8-letter strings recur, against 1,244 (95 % range 1,149–1,339) in controls that keep each side's letter pairs; Holm p 0.001 |
| Are a- and b-sides made in pairs (Cocciolilo 2026)? | No sign of it | Same-leaf pairs are no more alike than cross-leaf pairs (−0.021, against a control range of −0.056 to 0.057; p 0.73) |
| Does the cell above predict a cell? | No | p 0.86. Only the two-series tables 25b–28b show a diagonal neighbour effect (secondary test) |
| Do neighbouring tables share material? | Yes: the material drifts slowly through the book | A table's held-out rows are predicted better by its neighbours than by distant tables on 53 of 54 sides (mean rank 0.04 against 0.5; secondary) |
| Are Peterson's word marks on 2a–3b meaningful? | They depend on the letters around them, and the "words" are long | Mutual information 0.207 bits against 0.031 for random placement (Holm p 0.001); 8.8 letters a word against 5.3 in the Calls |
| Are the 48 Calls drawn from the tables? | The evidence weighs against it | Calls words occur in the rows no more often than pseudo-words (50 against 58.4); the Calls' letter order is no closer to the tables' than Latin or English is (Holm p 0.74) |
| How were the two-series tables 25b–28b written? | As two interleaved series that read as text-like sequences along diagonals and differ in their letters | Holm p 0.001 for both primary tests; diagonal reading secondary (p 0.0005) |
| By what rule are the two series laid into the grid? (v1.1) | Like a chessboard: one series on the "black" squares, one on the "white", each written one diagonal per line, so its lines are 1, 3 … 49 … 3, 1 or 2, 4 … 48, 48 … 2 letters long, the row lengths of the tables on 29a–48b. The slant of the letters gives the writing direction | Pre-registered, separate Holm family: slant gives direction on 7 of 9 marked series (Holm p 0.0004), and the fitted rule holds on 2 of 3 held-out series (Holm p 0.0004). The two failures are both `~` series (26b, 27a), which read best down-left (exploratory) |
| Does one series continue or mirror the other? (v1.1) | No sign of it; both draw on the book's common stock of strings | A side's two series share 45 8-letter strings (controls 2.4), but series of different sides share as many (8.0 a pair); none reversed; none copies a 29a–48b table |

## 1. The problem

**The book.** Sloane MS 3189 is the fair copy of *Liber Loagaeth* (also called *Liber
Mysteriorum Sextus et Sanctus*). Leaves 1a and 1b hold words written as running text; every
side from 2a to 48b holds a table. Peterson's edition prints each table cell by cell, with
marks for uncertain letters, word ends, accents and, on 25b–28b, the orientation of letters,
which divide those tables into two interleaved series.

**Earlier answers.** The tables have been described, edited and interpreted (Peterson; Laycock;
Leitch; Burns and Moore), and the Calls have been studied as a language (Laycock). The only
computational study of the whole book is Zubair (2026), who reports 212,082 letters, an index of
coincidence (IC) from 0.044 to 0.101 that he reads as "natural-language-like", and a test of the
*Book of Soyga* generation rule (Reeds) that he reads as Loagaeth being independent of, and on
one side "anti-correlated" with, that rule. Cocciolilo (2026) proposes a staged "table-engine"
reading in which a- and b-sides are paired. Neither was tested against controls that keep the
tables' own letter statistics.

**The questions**, made checkable and written into a pre-registration before scoring:
1. Do Peterson's word marks on 2a–3b behave like word boundaries?
2. Do long strings recur, within and between tables, and are a- and b-sides made in pairs?
3. Can a table be predicted from its own neighbouring cells, or from neighbouring tables?
4. Are the 48 Calls drawn from the tables?
5. How were the two-series tables 25b–28b written?

## 2. Sources

None of the third-party texts is included here (see Licensing). `scripts/fetch_sources.sh`
downloads them from where their owners publish them and checks their SHA-256 sums against the
copies used for the published results (`sources/SHA256SUMS`); the code reads them locally.

| Source | Used for |
|---|---|
| Joseph H. Peterson, *Liber Loagaeth*, Esoteric Archives edition of Sloane MS 3189 (© 1998, updated 2 February 2023) | the corpus: every cell of every side, with Peterson's marks |
| Meric Casaubon (ed.), *A True & Faithful Relation* (London, 1659), keyed text EEBO-TCP A37412 (CC0) | the 48 Calls, as printed word by word in the dictation tables |
| Zubair (2026), Zenodo 10.5281/zenodo.19708274 (CC BY 4.0): his per-table counts and his Soyga-rule table | the counts reproduced in L1 |
| Latin Wikisource (CC BY-SA 4.0): Alberti, *De pictura* (1435), and five works of Nicolaus Cusanus (1440–1450), at fixed page revisions | the period Latin reference text |
| Project Gutenberg (public domain): Chaucer's *Boece* and *Astrolabe* (Skeat), the Paston Letters (Gairdner), Caxton's *Chesse* (Axon), the *Book of Quinte Essence* (Furnivall), the *Forme of Cury* (Pegge), c. 1380–1509, in original spelling | the period English reference text |
| lorselq/enochian_language_modeling, leaf grids for 1c and 2a–16b, commit 0e296b4 (no licence) | optional: the cell-by-cell witness check (`code/compare.py`) |
| anasofiadias/Loagaeth, page images of Sloane MS 3189 (rights unclear) | the image spot checks, recorded as counts; not needed to rerun anything |

**The images.** The British Library lists Sloane MS 3189 as digitised but its images were not
available in October 2026. The image checks used eight folios from the anasofiadias repository,
privately, as a check on the edition; they are not included and nothing in the pipeline needs
them.

**Peterson's site.** On 19 October 2026 the site's TLS certificate had expired, so a verified
download fails. The fetch script never turns verification off; if it still fails, save the page
by hand (see How to reproduce). The copy used is identified by its SHA-256, which the script
checks.

## 3. Method

All random processes use the seed 20261019. The tests were run on CPU only, under `nice -n 19`,
with at most six processes.

| Step | Script | What it does |
|---|---|---|
| L0 | `code/corpus.py` | Parses Peterson's page into one record per cell: side, row, column, the letters, and flags for Peterson's marks (uncertain, word end, accent, capital, orientation, small type, struck through, `[sic]`). Writes the corpus to a git-ignored folder and only counts and hashes to `data/corpus_manifest.json` |
| L0 | `code/compare.py` (optional) | Our parse against the lorselq grids, aligned row by row, so that one missing cell does not count as a run of substitutions |
| L0 | (by eye) | A seeded random sample of 80 cells on the 8 sides with images, and every disputed cell, read on enlarged crops of the page images (`data/image_checks.json`) |
| L0 | `code/calls.py` | The 48 Calls from Casaubon's dictation tables: 838 word rows, 4,402 letters, forward forms (`data/calls_manifest.json`) |
| — | `code/reference_corpora.py` | Rebuilds the period Latin and English reference texts (`data/reference_corpora.json`) |
| L1 | `code/reproduce_zubair.py` | Zubair's letter counts and IC range, by our corpus and by an emulation of a count of every letter on the page; his Soyga-rule test with 10,000 shuffles of each table and a per-table baseline, Holm over 15 tables |
| L2 | `results/preregistration.md` | The five questions, ten primary tests (P) and their secondary tests (S), controls, multiple-testing rule and stop rule, committed before scoring |
| L3 | `code/l3_tests.py`, `code/l3_summary.py` | The pre-registered tests, 10,000 controls each, and Holm's correction over the primary family |
| W (v1.1) | `results/weave_preregistration.md`, `code/weave.py`, `code/weave_summary.py`, `code/weave_explore.py`, `code/weave_rows.py` | The layout of the two series of 25b–28b: four pre-registered tests (H1–H4) with their own Holm family, controls and checks (C1, S1–S3), exploratory follow-ups (E1–E3) and a descriptive count of row lengths |

**Symbols.** For the statistics each cell is one symbol: its first letter, lower case, accents
removed, with u, v and w read as one letter and j as i. Digit cells break every string; no
n-gram or context crosses them.

**Controls.** Every control keeps the letter frequencies of the text it replaces and keeps rows
as rows unless a test says otherwise:
- repeats (P2a, P2c): each row regenerated from its own side's letter-pair (first-order Markov)
  statistics, same length and first letter; a weaker control shuffles letters within rows;
- word marks (P1b): the same number of marks put back at random within each row;
- the cell above (P3a): rows of each side put in random order, each row intact;
- a/b pairing (P2b): which of the 53 adjacent pairs of sides are "same leaf" chosen at random;
- the Calls (P4a): each Calls word replaced by a pseudo-word of the same length from the Calls'
  own letter-pair statistics; (P4b) letter-shuffled copies, and 1,000 samples each of period
  Latin and English of the same number of letters;
- the two series (P5a, P5c): series labels permuted within each row.

**Pre-registration and Holm's correction.** The pre-registration (`results/preregistration.md`)
was committed on 19 October 2026 at 11:35 UTC as commit `7127723` (full hash
`71277239d82f7587deabff23314fd0928d5d6541`) of the author's private working repository, before
any of the statistics was computed; it lists what had been looked at before it was written. The
file here is that file, unchanged (SHA-256 `de117491…92c2de`); the paths in it refer to that
repository: its corpus `cells.jsonl` is the file `code/corpus.py` rebuilds (same SHA-256, recorded
in `data/corpus_manifest.json`), and its L and E are the files `code/reference_corpora.py`
rebuilds (byte for byte the files used in the original runs; SHA-256 in
`data/reference_corpora.json`). The test code was committed four minutes later (`73849f8`), run once with 20
controls as a smoke test to catch crashes, and then run in full with no parameter changed. Every
L3 result file records the pre-registration commit. p-values are one-sided, (1 + controls at
least as extreme) / (1 + controls), so the smallest possible with 10,000 controls is 0.0001.
They are corrected with Holm's method over the ten primary tests at α = 0.05; secondary tests
are reported with raw p and labelled secondary.

**One slip in the pre-registration.** It says the folded alphabet has 22 letters; it has 23
(a–z without j, u and w). The code uses the 23 letters present, and nothing else changes.

## 4. Results

### L0: the corpus (`data/corpus_manifest.json`, `results/witness_compare.json`, `data/image_checks.json`)

- **Corpus.** 96 sides, 196,721 cells, 196,353 letters and 377 digits. Three layouts: the word
  leaves 1a and 1b (18,686 letters); 54 full 49 × 49 tables on 2a–28b (130,047 cells); 40
  partly filled tables printed centred on 29a–48b (47,988 cells; their columns are estimated).
- **Rows.** Of the 2,646 rows of the full tables, 48 have 48 cells, 37 of them on 8b, where the
  manuscript's last column is empty (`results/l3_q5.json`, descriptive).
- **Marks kept as flags:** 65 uncertain, 1,760 accents, 1,269 capitals, 14,234 orientation marks
  on 25b–28b, 35 struck through, 3 rows marked `[sic]`. The 5,638 word-end flags include the word
  ends of the running text on 1a–1b; in the tables, Peterson's word marks fall on 2a–5a.
- **Folios.** Folio = leaf + 8 (2a is f. 10r), confirmed on the images of 8 sides.
- **The lorselq grids are a copy of Peterson's edition.** On 1c and 2a–16b (72,431 letters) the
  raw disagreement is 4.2 %, but 3,033 of the 3,035 disagreements come from one file: lorselq's
  5b is a copy of its 4b (the image of f. 13v shows Peterson's 5b). Without 5b, 2 letters
  disagree in 70,030, both extra letters in lorselq (7a row 4 column 49; 7b row 20), and there
  are no substitutions. So this agreement checks our parse, not Peterson's reading.
- **The images.** A seeded random sample of 80 cells on 8 sides: 78 agree with Peterson, 2 are
  doubtful, none is clearly wrong. In each disputed case the image sides with Peterson (5b; 7a
  row 4 has one d; 7b row 20 has 48 letters, with an empty cell after the 8th, so Peterson's
  column numbers after it are one too low); on 12b rows 30–33 the last cell is lost to damage.
- **Two advisory model readers** (`results/advisory_readers.json`) read 15 crops. A local
  qwen2.5vl:32b matched the edition on 101 of 198 target-row cells (51 %), too weak to judge
  Kelley's secretary hand. Claude (Anthropic API) answered 10 of 15 crops (5 empty answers,
  stop reason "refusal") and matched on 96 of 130 (74 %); on the disputed cases it agrees with
  the reading above except on 8b, where it reads no empty last cell. Neither changes the corpus.

### L1: Zubair (2026) reproduced and corrected (`results/zubair_repro.json`)

- **Letters.** Our corpus has 196,353 letters; Zubair reports 212,082. Counting every letter in
  each leaf's section of the web page, headings and notes included, gives 212,500, within 25
  letters of his figure on every side (mean difference 5.6). His 48b has 11,616 letters because
  that section runs on into Peterson's appendix of four *Book of Soyga* tables; with that text
  our emulated IC for 48b is 0.043744, exactly his value.
- **IC.** Zubair: 0.0437–0.1013 (mean 0.0821). Ours: 0.0597 (47b) to 0.1017 (26a), mean 0.0829.
  His minimum belongs to the Soyga tables. A high IC here comes from one dominant letter
  (a, 37,315 of 196,353 letters); it does not show language.
- **The Soyga rule** (cell = above + f(left) mod 23, Reeds's f), on the top-left 36 × 36 block of
  2a–9a: our match rates are 2.78–5.31 % (his 3.71–5.76 %, on slightly different cells). The
  right baseline is not 1/23 = 4.35 % but the rate expected from each table's own letters,
  3.2–4.0 % (mean 3.52 %). Against 10,000 shuffles of each table, no table differs after Holm's
  correction (smallest raw p 0.013 on 7b; Holm 0.19). His "anti-correlated" side 2a (59 matches,
  2.99 % against 4.35 %) gives 2.94 % here, against a shuffle mean of 3.54 %: p 0.28.

### L3: the pre-registered tests (`results/l3_*.json`, `results/l3_summary.json`)

Six of the ten primary tests are positive after Holm's correction and four are negative.

| Test | Question | Observed | Controls: mean (95 % range) | p | Holm |
|---|---|---|---|---|---|
| P1a | word lengths differ from the Calls' | JSD 0.265 bits | 0.005 (0.002 to 0.010) | 0.0001 | **0.001** |
| P1b | word marks depend on the letters | MI 0.207 bits | 0.031 (0.027 to 0.035) | 0.0001 | **0.001** |
| P2a | repeated 8-letter strings in the full tables | 6,679 | 1,244 (1,149 to 1,339) | 0.0001 | **0.001** |
| P2b | a- and b-sides made in pairs | −0.021 | 0.000 (−0.056 to 0.057) | 0.73 | 1 |
| P2c | 8-letter strings shared between sides | 6,436 | 1,193 (1,100 to 1,285) | 0.0001 | **0.001** |
| P3a | the cell above helps predict a cell | −14,382 bits | −14,187 (−14,535 to −13,828) | 0.86 | 1 |
| P4a | Calls words found in the rows | 50 of 578 types | 58.4 (46 to 71) | 0.92 | 1 |
| P4b | the Calls' letter order is close to Loagaeth's | Δ 0.499 bits | Latin 0.471, English 0.463 | 0.18 | 0.74 |
| P5a | Kelley's two series read as running text | 1.33 | 0.37 (0.16 to 0.59) | 0.0001 | **0.001** |
| P5c | the two series differ in their letters | χ² 502 | 87 (66 to 110) | 0.0001 | **0.001** |

**Q1, words** (`results/l3_q1.json`). The 1,088 word marks on 2a–3b give 1,084 words. They
average 8.8 letters, against 5.3 for the Calls, 5.9 for period Latin and 4.1 for period English.
The length distribution is nearest Latin (JSD 0.139, bootstrap 95 % 0.125–0.159) and far from
the Calls (0.265) and English (0.370). The marks are not scattered: they depend on the letters on
either side of them about six times more than random placement within the same rows allows.

**Q2, repetition** (`results/l3_q2rep.json`, `results/l3_q2pair.json`). Long strings recur far
beyond what each table's own letter-pair statistics produce: 6,679 distinct 8-letter strings
recur, and 6,436 of them occur on two or more sides. Secondary: 391 distinct 12-letter strings
recur (Markov controls 1.8 on average, at most 12), and the longest repeated string is 17 letters
(Markov controls at most 15 in 200). There is no sign that a- and b-sides are made in pairs: not
on 2a–28b (P2b), not on 29a–48b and not with shared 6-letter strings (S2b, all p ≥ 0.19).

**Q3, generation** (`results/l3_q3a.json`, `l3_q3b.json`, `l3_q3c.json`). Knowing the cell
directly above does not help to predict a cell on held-out rows (P3a, 53 sides with at least 40
full rows; no side survives Holm). Secondary tests: the cell above-left helps overall (p 0.0001),
but per side only on 25b, 26a, 27b, 28a and 28b (Holm over 53 sides); the cell above-right helps
only on 26b and 27a. So all seven two-series tables, and no others, carry a diagonal dependence,
which is what series written along diagonals would produce. Rows do not copy the three rows
above them more than random rows of the same side do (S3b, p 0.047, not significant after Holm
within Q3). Neighbouring tables predict a table's held-out rows much better than distant ones
(S3c: mean rank 0.04 among 200 random distant pairs, against 0.5 by chance, and below 0.5 on
53 of 54 sides; p 0.0001).

**Q4, the Calls** (`results/l3_q4.json`). Calls words of four letters or more turn up in the
rows of 2a–28b no more often than pseudo-words built from the Calls' own letter pairs (50 of 578
types, against 58.4; P4a), and on 29a–48b the same (34 against 33.0). Under a letter model of the
tables, the Calls gain 0.499 bits a letter from their letter order, against 0.471 for period
Latin and 0.463 for period English samples of the same size (P4b, p 0.18): their letter order is
no closer to the tables' than ordinary text is.

**Q5, the two series** (`results/l3_q5.json`). On 25b–28b, reading each of Kelley's two series on
its own gives more text-like letter pairs than reading the rows straight through (P5a), and
reading each series along diagonals more so again (S5b: 9.67 against 4.72; p 0.0005 on 2,000
controls, secondary), which supports Peterson's description of series written along diagonals.
The two series also differ in their letters (P5c). Descriptive: each series on these sides holds
about 1,200 cells; every partly filled table
on 29a–48b holds 1,195–1,201 letters except 36b (1,176), the size of one series: those tables look
like one series written and the other never filled in. The 65 uncertain marks fall on 21 sides
between 4a and 17b.

### Pages 25b–28b: the two series and how they are laid (v1.1; `results/weave_*.json`)

A second study, pre-registered on its own (`results/weave_preregistration.md`), asks by what rule
Kelley's two letter series are laid into the 49 × 49 grid of 25b–28b, and what follows from it.
It is a study of layout, not a reading: no translation, no word search.

**The rule, in plain words.** Peterson's orientation marks follow a chessboard exactly on all
seven sides: one series sits on every "black" square (row + column even, 1,201 cells) and the
other on every "white" square (odd, 1,200 cells), with one exception (one `/` on a white square
of 28a). Each series is written along diagonals, one diagonal per line, with the page turned so
that the letters slant. On a 49 × 49 chessboard the diagonals of one colour are 1, 3, 5 … 49 … 5,
3, 1 cells long and those of the other 2, 4 … 48, 48 … 4, 2. These are the row lengths of the
partly filled tables of 29a–48b: 19 of the 40 have rows of exactly 1, 3 … 49 … 3, 1
cells and 17 exactly 2, 4 … 48, 48 … 2; of the other four, 41a, 46a and 47a differ from the
pattern in one or two rows and 36b (1,176 cells) in 24 (`results/weave_rows.json`, a
descriptive count). So each series is laid out like one of the later
tables, written on the diagonal; the later tables look like one series written with the other
never added.

**The slant gives the direction.** Peterson's legend says `/` marks a letter turned 45° clockwise
and `~` one turned 135° counter-clockwise. Turning the writer's line the same way, `/` letters
are written down to the right and `~` letters up to the left. `` ` `` has no legend; letters
without a mark are upright.

**What was tested** (seed 20261019; 20 candidate paths for each set of cells: along rows, columns,
the four diagonals, eight steeper slopes and four back-and-forth versions). Each path is scored
by bits per letter pair within lines, under a letter-pair model trained on the rows of 2a–25a;
lower is more text-like. The controls permute each series' letters within each row
(10,000 times) or regenerate each series from its own letter pairs (1,000 times).

| Test | Question | Observed | Controls: mean (95 % range) | p | Holm |
|---|---|---|---|---|---|
| H1 | the slant mark gives the direction (9 marked series, nothing fitted) | margin 1.69 bits; predicted path first of 20 on 7 of 9 | 0.06 (0.01 to 0.10) | 0.0001 | **0.0004** |
| H2 | unlegended marks: path fitted on one side, tested on held-out sides (3 series) | margin 1.55 bits; first on 2 of 3 | 0.04 (−0.06 to 0.13) | 0.0001 | **0.0004** |
| H3 | the series share 8-letter strings with the rows of 29a–48b | 663 | 61 (42 to 82) | 0.001 | **0.002** |
| H4 | the two series of a side share 8-letter strings | 45 | 2.4 (0 to 7) | 0.001 | **0.002** |

Margin: the mean score of the other 19 paths minus the score of the predicted path, in bits per
letter pair, averaged over the series. Holm's correction is over these four tests only; with
1,000 controls the smallest possible p is 0.001.

- **H1, series by series** (`results/weave_h1.json`). The predicted path is first of 20 on 25b A
  (`/`), 25b B (`~`), 26a B (`~`), 26b A (`/`), 27b B (`/`), 28a A (`/`) and 28b A (`/`), at
  2.81–3.13 bits per letter pair, against 5.22–5.43 for the same cells read along the rows; it
  is first by shared 6-letter strings with 2a–25a as well. It fails on the `~` series of 26b and
  27a (ranks 14 and 6).
- **The `~` exception (exploratory, after the results were seen;** `results/weave_explore.json`,
  E2). On 26b B and 27a B the best path runs down to the left, at 3.05 and 3.03 bits, first of 20
  with margins of 2.13 bits. So in Peterson's marks `~` seems to cover two different turns of the
  letter: up-left on 25b and 26a, down-left on 26b and 27a. Only the page images could settle
  this, and none of 25b–48b was checked.
- **H2** (`results/weave_h2.json`). The `` ` `` letters, fitted on 27b A, run up to the left; held
  out, that path is first on 28a B and 28b B. Upright letters, fitted on 26a A, run down to the
  right; held out on 27a A that path is second (4.32 bits), behind reading every other cell along
  the row (3.92). 27a A is the least text-like series under any path.
- **Specificity (C1, and E1)** (`results/weave_c1.json`). On the two colours of the 38 full
  single-series tables 2a–25a (76 sets of cells) no path is text-like: the best scores 4.90–5.28
  bits. A diagonal path edges out the row on 71 of the 76, but by at most 0.31 bits, against
  margins of about 2 bits on 25b–28b. The rule belongs to the two-series sides.
- **Rows 1–5 of 25b (S3).** The 122 unmarked cells of the second series in rows 1–5 read best left
  to right along the row, as Peterson's note says.
- **Line order (S1, secondary;** `results/weave_s1.json`**).** The letter pairs that join the end of
  one line to the start of the next, with the lines in the writer's order, are more text-like
  than random line orders on 25b A, 25b B, 26a B and 27b B (p 0.006, 0.007, 0.03 and 0.001; none
  in the reverse order). On those series the text runs on from line to line.
- **Line ends (S2, secondary and exploratory;** `results/weave_s2.json`**).** Lines end in h, x or
  s 19 % of the time (14 % inside lines; shuffles 14 %, 95 % up to 16 %; p 0.001) and start in o,
  v or g 22 % of the time (15 % inside; p 0.001). The pre-registration names h, x and s as the
  word-final letters of the marked words of 2a–3b; the start letters o, v and g were added in the
  code and are not in it. There are no word marks on 25b–28b.
- **H3, the later tables** (`results/weave_h3.json`). The series share 663 distinct 8-letter
  strings with 29a–48b (controls 61), but also 1,644 with 2a–25a (controls 190). Allowing for the
  size of each (47,988 cells against 113,240), the rate is about the same, about 14 per 1,000
  cells. No series copies a later table: the best single table shares 7–26 strings with a
  series (none for the two `~` series that fail H1), usually one of the first few (29a–33a). With the down-left reading for 26b B and 27a B
  (exploratory, E3): 730 (controls 71).
- **H4, the two series of a side** (`results/weave_h4.json`). They share 45 strings (controls
  2.4), but a series of one side and the other series of a different side share as many: 8.0 a
  pair on average, about 56 for seven pairs; 28a A and 27b B share 47. The second series reversed
  shares none with the first. With E3's paths: 56 on the same side, against 9.9 a pair across
  sides.

**What this implies, and what it does not.** The evidence weighs toward each series being a
table of the 29a–48b kind written along the diagonals, with the slant of the letters showing the
writing direction. It does not show that one series continues the other, or mirrors it: the two
series of a side are no more alike than series of different sides, and both draw on the same
stock of recurring strings as the rest of the book. Nor do the series copy a later table. "Text-
like" is a statistic against controls; it does not show a language, and nothing here is a
reading or a translation.

**Pre-registration and timing.** `results/weave_preregistration.md` is the file committed on
20 October 2026 at 03:01 UTC as commit `26f8bbb` (full hash
`26f8bbb7c08a8618ea7446a070d49ad7b63174ff`) of the author's private working repository, before
any of the weave statistics was scored; it is unchanged here (SHA-256 `d6564f82…ce2b1d2f`), and
its paths (`../README.md`, `PROGRESS.md`) refer to that repository. It lists what had been looked
at first: the prior art, which cells carry which marks (the chessboard), and the row lengths of
29a–48b. The test code was committed two minutes later (`50421bf`), smoke-run with 20 controls
and then run once in full; the results were committed at 03:08 UTC (`43ca779`). Readers cannot
check this timing: the working repository is private, and the commits were published here only
with version 1.1. The exploratory runs (E1–E3) were written after the primary results were seen
and are labelled so in their file. `results/weave_rows.json` is a descriptive count added for
this release.

## 5. Verdict

- **The evidence weighs toward tables built from a recurring stock of word-like strings**, laid
  out row by row and varied gradually through the book: long strings recur across many sides far
  beyond what letter-pair statistics give, neighbouring tables share the most, and the word marks
  on 2a–3b fall at letter-dependent places and cut long words.
- **No simple mechanical rule of the Soyga kind**, and no "cell above" rule, is visible; Zubair's
  Soyga result and his low IC both go once the baseline and the corpus are right.
- **The two-series tables 25b–28b were written differently**: as two interleaved series that
  read as text-like sequences along diagonals and differ in their letters. The partly filled
  tables 29a–48b are each the size of one such series.
- **(v1.1) Each series of 25b–28b is laid like a chessboard colour, one diagonal per line**, so
  its lines have the row lengths of the tables of 29a–48b, and the slant of the letters gives the
  writing direction (7 of 9 marked series and 2 of 3 held-out series). The two series of a side
  do not continue or mirror each other; both draw on the common stock of strings.
- **No a/b pairing of sides** (against Cocciolilo 2026).
- **The evidence weighs against the 48 Calls being drawn from the tables' running text.** This
  does not rule out a relation by some other path (directions, skips, grid paths), which was not
  searched, by design.

None of this is a reading of the tables or a translation. "Text-like" and "word-like" describe
statistics measured against controls; they do not show that the tables encode a language.

## 6. What is new, and what earlier work did

This study stands on the work of others:

- **Joseph H. Peterson** edited Sloane MS 3189 cell by cell, with marks for doubtful letters,
  word ends and letter orientation, and described the two series of 25b–28b as written along
  diagonals. Every letter here is read from his edition. His note on 25b says, in words, that one
  series runs along alternate diagonals from upper left to lower right with its letters slanted
  45° clockwise, that the gaps of rows 1–5 are filled left to right, and that another series runs
  along diagonals from lower right to upper left; his legend explains `/` and `~` (not `` ` ``).
- **Donald Laycock** (*The Complete Enochian Dictionary*, 1978; revised 1994) compiled the
  vocabulary of the Calls and judged them language-like in syntax, unlike the untranslated
  Loagaeth.
- **Aaron Leitch** (*The Angelical Language*, 2 vols, 2010) gave the history of Loagaeth and the
  Calls and a lexicon.
- **Teresa Burns and J. Moore** (*Journal of the Western Mystery Tradition*, 2010) interpreted
  the tables and their use; **Deborah Harkness** (1999) and **Egil Asprem** (2012) set the
  sessions and their reception in context; **Christopher Whitby** (PhD thesis, Birmingham,
  1982) edited the record of the sessions of 1581–1583.
- **Muhammad Zubair** (2026; Zenodo 10.5281/zenodo.19708274, 10.5281/zenodo.19709277 and
  10.5281/zenodo.19709477) made the first computational analysis of the whole book: letter
  counts, IC, a test of the Soyga rule, and an argument that the Calls are structurally
  independent of the tables.
- **Gary Cocciolilo** (2026; Zenodo 10.5281/zenodo.19914827, 10.5281/zenodo.19917987 and
  10.5281/zenodo.19976902) proposed a staged "table-engine" reading, qualitative and without
  translation, including a pairing of a- and b-sides. He noticed (2026a, §5) that 25b–28b should
  not be read row by row and that one diagonal stream extracted from 25b grows 1 → 49 → 1 in the
  shape of the later leaves, and (2026c, §9) that the tables of 29a–42b alternate fields of
  2 … 48 … 2 and 1 … 49 … 1 cells. He states this qualitatively, without a path rule or a test,
  and does not claim that 25b generates 29a.
- **lorselq** (GitHub, enochian_language_modeling) published machine-readable grids of 2a–16b
  with marks for uncertain cells and lacunae, and n-gram experiments; **anasofiadias** (GitHub,
  Loagaeth) published page images of the manuscript and a transcription; **Marco Ponzi** fitted
  Zipf's law to Peterson's text.
- **Jim Reeds** (1998; 2006) found the rule and the step function of the *Book of Soyga* tables
  that Zubair applied to Loagaeth.

What this study adds, as far as our search found (GitHub, Zenodo and the web, 18–19 October
2026):
1. **A checked, coordinate-addressed corpus** of the whole book from Peterson's edition, every
   cell addressed and every mark kept, with the finding that the lorselq grids are a copy of the
   same edition (with one misfiled side), not an independent witness, and an image check of a
   random sample.
2. **Corrections to Zubair (2026)**: his letter total counts page text, not cells; his lowest IC
   (0.044, the basis of "random-text zone" comparisons) is Peterson's appendix of four Soyga
   tables; his Soyga-rule test used a 1/23 baseline where each table's own letters give 3.2–4.0 %,
   and with that baseline and shuffle controls no table departs from chance, so the
   "anti-correlation" on 2a disappears.
3. **Ten pre-registered tests with controls that keep the tables' own statistics**, and Holm's
   correction: the recurring long strings shared between sides, the slow drift from table to
   table, the letter-dependence of the word marks, the diagonal series of 25b–28b and the
   difference in their letters; and the negative results: no a/b pairing (Cocciolilo), no
   "cell above" rule, and no sign that the Calls were drawn from the tables' rows. Zubair also
   argued that the Calls are independent of the tables; the tests here reach a compatible result
   with matched controls, and say only that the evidence weighs against the Calls being drawn
   from the rows.
4. **The partly filled tables 29a–48b are each one series' worth of letters** (about 1,200),
   matching one of the two series on 25b–28b.
5. **(v1.1) The layout rule of 25b–28b**, stated exactly and tested (search of GitHub, Zenodo
   and the web, 20 October 2026): each series is one chessboard colour, written one diagonal per
   line, so that its lines have exactly the row lengths of the 29a–48b tables; the slant mark
   gives the writing direction, tested before scoring with held-out sides and controls; the `~`
   mark seems to cover two directions (exploratory); the text runs on from line to line on four
   series; and the tests of what follows (no copy of a later table, no continuation or mirror
   between the two series). Peterson's note gives the direction of the 25b series in words, and
   Cocciolilo saw the 1 → 49 → 1 growth of one stream and the alternating fields of the later
   tables; what is new is the full mapping for all seven sides and the controlled tests.

## 7. Caveats and open checks

1. **The edition.** Everything is read from Peterson's edition. Our image check covers 80 random
   cells and the disputed cases on 8 sides; a full collation with the manuscript was not
   possible (the British Library's images were unavailable). The lorselq grids do not help:
   they copy the same edition.
2. **The series labels** on 25b–28b are Peterson's orientation marks. Q5 tests his reading of
   them, not an independent one.
3. **What "word-like" means.** Recurring long strings and letter-dependent word marks are what
   text would give, but also what copying from a stock of invented strings, or any generator
   with a memory longer than one letter, would give. The controls rule out first-order letter
   statistics, not every mechanism.
4. **The pre-registration was not blind.** It was written after the corpus counts, the witness
   and image checks, Zubair's counts and a few simple tallies had been seen (it lists them), and
   the test code was written after it. The slip of 22 for 23 letters is reported above.
5. **The Calls word list** was extracted from Casaubon's dictation tables by a rule (838 word
   rows; 176 of the forward forms are inferred rather than printed). A hand-checked list could
   shift P4a by a few words.
6. **The reference texts** are one Latin set (normalised modern editions of 1435–1450 works) and
   one English set (mostly the Paston Letters). They stand for "ordinary text", not for the
   language of the Calls.
7. **Not searched, by design:** directions other than the written rows, skips, knight's moves or
   any other grid path, and any translation. The one exception is the weave study (v1.1), which
   scores 20 fixed paths on 25b–28b (and, as a control, on 2a–25a) for letter-pair statistics
   only; no path is searched for words.
8. **(v1.1) The weave study rests on Peterson's marks.** The chessboard, the slant directions and
   the two kinds of `~` are all read from his edition; no image of 25b–48b was checked, so how
   the marks look on the page, what `` ` `` means, and how the tables of 29a–48b sit on the page
   are open. "Direction" means the sense that reads like the left-to-right rows of 2a–25a, since
   the letter model is trained on them. The weave pre-registration was written after the
   chessboard and the row lengths had been seen (it says so), and its timing cannot be checked
   by readers (see "Pages 25b–28b").
9. **Open checks:** a full collation with the manuscript images when they are available again;
   a second, independent transcription; generation models beyond first-order Markov and copying
   from recent rows.

## 8. How to reproduce

Needs Linux or macOS with `bash`, `curl`, `python3`, `sha256sum` and
[`uv`](https://docs.astral.sh/uv/) (which supplies Python 3.13 and numpy 2.5.4, the versions the
results were made with; set `PYTHON` to use another interpreter with numpy).

```
scripts/fetch_sources.sh sources/downloads    # about 12 MB; checks SHA-256 sums
code/run_all.sh sources/downloads             # about 1.5 hours (one test takes most of it)
git status --short results/ data/             # should be empty
```

Peterson's page: if the verified download fails (the site's certificate had expired on
19 October 2026), save https://www.esotericarchives.com/dee/sl3189.htm by hand as
`sources/downloads/peterson/sl3189.htm` and run `fetch_sources.sh` again; it checks the SHA-256.

`fetch_sources.sh` pins the Calls text and the Latin pages to the revisions used and checks each
download against `sources/SHA256SUMS`. If a source has changed since, the script warns and the
results may differ. From these copies the pipeline rebuilds the corpus and the reference texts
into `work/` (git-ignored, so a rebuild never republishes them) and rewrites every results file
in `data/` and `results/` byte for byte (checked from a clean fetch and a clean `work/` folder on
19 October 2026), except the files that record checks outside the pipeline:
`data/image_checks.json`, `data/image_grid_boxes.json`, `results/advisory_readers.json`,
`results/run_records.json`, `results/preregistration.md` and `results/weave_preregistration.md`.
The weave files (v1.1) were checked the same way on 20 October 2026, from the fetched edition and
a freshly rebuilt corpus: the ten `results/weave_*.json` files of the original runs come out
byte for byte (the code and run-time fields moved to `results/run_records.json`) with
Python 3.12 and numpy 2.2.6, the versions of the original weave runs, which `run_all.sh` uses for
those steps (`WPYTHON` overrides it). With numpy 2.5.4 the last digit of the H1 control mean and
standard deviation (`weave_h1.json`, `weave_summary.json`) changes; nothing else does. The
optional witness check reruns
with:

```
WITH_LORSELQ=1 scripts/fetch_sources.sh sources/downloads
python3 code/compare.py work/corpus sources/downloads/lorselq    # rewrites results/witness_compare.json
```

The results files hold no machine- or time-dependent fields; the code commits and run times of
the original runs are in `results/run_records.json`.

## Licensing

- **Code** (`code/`, `scripts/`, `paper/build.sh`): MIT, see `LICENSE`.
  `code/reference_corpora.py` vendors the author's own corpus-building code (see its header).
- **Our data, results and paper** (`data/`, `results/`, `paper/`): CC BY 4.0
  (https://creativecommons.org/licenses/by/4.0/). They are counts, hashes, test statistics and
  short cell references; the pre-registration and the paper are our own text.

**Left out, and why:**
- **Peterson's edition**: copyright, research use only. It is not redistributed, and no corpus
  file, row or long string from it is published. The pipeline rebuilds the corpus locally into
  `work/`. The results keep counts, hashes and a handful of cell references (side, row,
  column, and at most a letter or two).
- **The readings of whole row segments** made on the page images, and the per-cell readings of
  the two model readers: they reproduce the edition's text, so only the counts of agreeing cells
  and short references are kept (`data/image_checks.json`, `results/advisory_readers.json`).
- **The two series of 25b–28b as read by the layout rule** (v1.1): they are the edition's letters
  in another order, so they are written only to `work/corpus/weave_series.json`; the results keep
  counts and scores, and the 8-letter strings counted in H3 and H4 are not listed.
- **The list of Calls words found in the rows** (P4a): each is also a string of the edition; the
  count is published and the list is written only to `work/`.
- **The lorselq grids**: no licence; fetched only for the optional check; only counts and two
  cell references are published.
- **The anasofiadias page images**: rights unclear; not included and not needed. The crop boxes
  and the SHA-256 of each crop are kept.
- **Zubair's tables** (CC BY 4.0) and **the Calls** (CC0): they could be shared, but the
  pipeline fetches them; the derived Calls word list stays in `work/`.
- **The reference texts**: Latin Wikisource (CC BY-SA 4.0) and Project Gutenberg (public
  domain); fetched and rebuilt, not included.
- No manuscript images are included.

## References

- British Library, Sloane MS 3189 (*Liber Loagaeth*).
- Joseph H. Peterson (ed.), *Liber Loagaeth*, Esoteric Archives, © 1998, updated 2 February 2023.
  https://www.esotericarchives.com/dee/sl3189.htm
- Meric Casaubon (ed.), *A True & Faithful Relation of What passed for many Yeers Between
  Dr. John Dee … and Some Spirits*, London, 1659. EEBO-TCP A37412,
  https://github.com/textcreationpartnership/A37412
- Muhammad Zubair (2026), "First Computational Analysis of Liber Loagaeth: Statistical and
  Algorithmic Findings", Zenodo, doi:10.5281/zenodo.19708274; "Structural Independence of the 49
  Loagaeth Calls and 48 Claves Angelicae: A Computational Comparison", doi:10.5281/zenodo.19709277;
  "Loagaeth in Context: Diary Evidence, the Mystery of Mysteries, and the Monas Hieroglyphica
  Connection", doi:10.5281/zenodo.19709477.
- Gary Cocciolilo (2026), "Liber Loagaeth as an Angelic Operating Manuscript",
  doi:10.5281/zenodo.19914827; "Compressed, Expanded, Operational: A Dee-First Layered
  Reconstruction Model of Liber Loagaeth, Soyga, and the Great Table",
  doi:10.5281/zenodo.19917987; "Liber Loagaeth as a Staged Table-Engine",
  doi:10.5281/zenodo.19976902.
- Donald C. Laycock, *The Complete Enochian Dictionary* (London, 1978; revised edition 1994).
- Aaron Leitch, *The Angelical Language*, 2 vols (Woodbury, MN: Llewellyn, 2010).
- Teresa Burns and J. Moore, "John Dee and Edward Kelley's Great Table (or, What's This Grid
  For, Anyway?)", *Journal of the Western Mystery Tradition* 2 (2010).
- Deborah E. Harkness, *John Dee's Conversations with Angels: Cabala, Alchemy, and the End of
  Nature* (Cambridge University Press, 1999).
- Egil Asprem, *Arguing with Angels: Enochian Magic and Modern Occulture* (SUNY Press, 2012).
- Christopher L. Whitby, *John Dee's Actions with Spirits, 22 December 1581 to 23 May 1583*,
  PhD thesis, University of Birmingham, 1982. https://etheses.bham.ac.uk/id/eprint/3149/
- Jim Reeds, "John Dee and the Magic Tables in the Book of Soyga", in S. Clucas (ed.), *John Dee:
  Interdisciplinary Studies in English Renaissance Thought* (Springer, 2006), pp. 177–204,
  doi:10.1007/1-4020-4246-9_10.
- lorselq, *enochian_language_modeling*, https://github.com/lorselq/enochian_language_modeling
  (commit 0e296b4).
- anasofiadias, *Loagaeth*, https://github.com/anasofiadias/Loagaeth
- Marco Ponzi, "Zipf's Law and Angelic Languages", Medium,
  https://medium.com/viridisgreen/zipfs-law-and-angelic-languages-96f05109e8f3
- Reference texts: Latin Wikisource (https://la.wikisource.org), pages of *De pictura*,
  *De docta ignorantia*, *De coniecturis*, *Apologia doctae ignorantiae* and *Idiota de mente*;
  Project Gutenberg ebooks 44833, 45027, 40989, 41024, 41081, 42239, 42240, 10672, 17179 and 8102.

## Versions

- **1.1** (20 October 2026): adds the study of how the two series of 25b–28b are laid into the
  grid (section 4, "Pages 25b–28b"): its pre-registration, code (`code/weave*.py`, added to
  `code/run_all.sh`), results (`results/weave_*.json`, run records in
  `results/run_records.json`), and a section and a schematic figure in the paper. No result of
  version 1.0 is changed; the summary, verdict, credits, caveats and reproduction notes now
  mention the new study.
- **1.0** (19 October 2026): the corpus, the reproduction of Zubair (2026) and the ten
  pre-registered tests.

## How to cite

Burford, B. (2026). Liber Loagaeth: a pre-registered structural study of the tables (version
1.1). Zenodo. https://doi.org/10.5281/zenodo.23487865.
Source: https://github.com/BravoBravoIX/liber-loagaeth-structure
