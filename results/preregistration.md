# Liber Loagaeth: pre-registration of the five questions (L2)

Written 19 October 2026, before any of the tests below was scored. The commit that adds this
file is the pre-registration; every result file of L3 records it. Plan: `docs/dee-plan.md` §2
(D101). Scope: structure only. No translation is attempted, and no grid paths are searched for
known Enochian words; the only reading order used for words is the order in which the rows are
written (left to right within a row).

What had been looked at before writing this: the corpus counts (`data/corpus_manifest.json`),
the witness check, the image spot checks, Zubair's counts and the Soyga-rule test (L1), the
number of word marks per side, the number of cells per orientation mark on 25b–28b, and the size
of the Calls word list. None of the statistics below had been computed.

## Data (frozen)

- **Corpus:** `cells.jsonl`, SHA-256 `4b748035da85702ba8431221181d9a64ee1e04023d40311f0e59851de7f50e18`
  (`code/corpus.py`, Peterson's edition, SHA-256 `8d1c0ebf…`).
- **Symbols:** one per cell: the cell's first letter, lower case, accents removed, u and w read
  as v, j as i (22 letters). Digit cells (9a, 11a and a few others) are a break: no n-gram or
  context crosses them.
- **G**, the full tables: sides 2a–28b (54 sides). Tests that use columns (above, diagonal)
  use only rows of exactly 49 cells (48 rows of 48 cells are left out there; their column
  numbers are uncertain after a gap). Tests that read rows use all rows.
- **C**, the partly filled tables 29a–48b (40 sides), rows as printed.
- **K**, the Calls: the 838 word rows of Casaubon's dictation tables (`code/calls.py`, EEBO-TCP
  A37412, CC0; manifest `data/calls_manifest.json`), forward forms, folded as above.
- **L** and **E**, period Latin and English: `~/cipher-hunter-data/corpora/la15/train.txt` and
  `en15/train.txt`; words are maximal runs of letters, folded as above.
- **Seed** 20261019 for every random process (numpy `default_rng`, one child stream per test).
- **Controls:** 10,000 per test unless stated. Every control keeps the letter frequencies of the
  text it replaces, and keeps rows as rows (a row's letters stay in that row) unless a test says
  otherwise.

## Multiple testing and decision rule

The primary family is the ten tests marked **P** below. p-values are one-sided as stated,
computed as (1 + number of controls at least as extreme) / (1 + number of controls), and
corrected with Holm's method over the ten, α = 0.05. Tests marked **S** are secondary: reported
with raw p and Holm within their question, and labelled secondary. A Holm-adjusted p < 0.05 is
reported as "the evidence weighs toward …"; nothing here is called a solution or a reading.

## Stop rule

Each test is run once, on the frozen corpus, with the parameters written here. Parameters are
not changed after seeing results. If a coding error is found after scoring, it is fixed, the
test is rerun, and both runs and the fix are reported. No test is added to the primary family
after scoring; anything new is labelled exploratory. Negative results are reported in full.
Compute: CPU only, `nice -n 19`, at most 6 processes; if a test would take more than 3 hours
with 10,000 controls it runs with 2,000 and says so.

## Q1. Cell and word structure

Word marks (Peterson's ".") occur on 2a–5a only; the sides with at least 200 marks are 2a, 2b,
3a, 3b (1,088 marks). A word is the run of letters between two consecutive marks in row-major
reading order (rows run on into the next row); letters before a side's first mark and after its
last are dropped.

- **P1a word length against the Calls.** Statistic: Jensen–Shannon divergence (bits) between
  the word-length distributions of Loagaeth and K (lengths 1–14, 15 and over pooled). Null:
  both come from one distribution; 10,000 random reassignments of the pooled words to the two
  groups (sizes kept). One-sided (large divergence). Reported alongside: mean length and the JSD
  to L and to E with 10,000-bootstrap 95 % intervals, and which reference is nearest.
- **P1b do the marks depend on the letters?** Statistic: mutual information (bits) between
  "a mark follows this cell" and the pair (this letter, next letter in the row). Control: the
  same number of marks put back at random cells within each row (marks per row kept, letters
  untouched), 10,000 times. One-sided (larger than controls).

## Q2. Repetition

- **P2a long repeats within G.** Statistic: the number of distinct 8-letter strings (read
  within rows, not across row ends or digits) that occur at two or more places in G.
  Control: each row regenerated from its own side's first-order letter-transition table,
  starting with the row's first letter, same length (keeps each side's letter and pair
  statistics and the row lengths), 10,000 times. One-sided (more repeats than controls).
  Secondary **S2a**: the same for 12-letter strings, the longest repeated string, and against
  a weaker control (letters shuffled within each row).
- **P2b are a- and b-sides made in pairs?** (Cocciolilo 2026.) For the 53 adjacent pairs of
  sides in G (2a|2b, 2b|3a, …, 28a|28b), similarity = cosine of their letter-trigram count
  vectors (trigrams within rows). Statistic: mean similarity of the 27 same-leaf pairs minus
  mean of the 26 cross-leaf pairs (nb|(n+1)a). Null: which 27 of the 53 adjacent pairs are
  "same leaf" is random; 10,000 random choices. One-sided (same-leaf more similar).
  Secondary **S2b**: the same on C (20 leaves, 39 adjacent pairs) and with shared 6-gram counts
  in place of cosine.
- **P2c shared strings between tables.** Statistic: the number of distinct 8-letter strings
  that occur on two or more different sides of G. Control: as P2a (the same 10,000
  surrogates). One-sided.

## Q3. Generation: is a table predictable from its own neighbours?

Rows whose number is a multiple of 5 (5, 10, …, 45) are held out on every side of G; models
are fitted on the other rows of the same side; losses are in bits per held-out letter, with
add-0.5 smoothing over the 22 letters.

- **P3a the cell above.** Per side, gain Δ = loss of P(x | left) − loss of P(x | left, above).
  Statistic: the sum of Δ over held-out cells of all sides. Control: the rows of each side put in
  random order (each row kept intact; the "above" letter now comes from a random row of the
  same side), 10,000 times, recomputed in full. One-sided (larger gain than controls).
  Secondary **S3a**: the same with the cell above-left and above-right in place of above,
  and per side (Holm over 54 sides).
- **S3b copying from recent rows.** Statistic: mean over held-out rows of the longest string
  shared with any of the three rows above it. Control: row order permuted within side, 10,000.
- **S3c neighbouring tables.** For each side of G, a letter-trigram model (add-0.5,
  interpolated with bigram and unigram at fixed weights 0.6/0.3/0.1) is trained on the two
  adjacent sides (the one before and the one after; one side at the ends) and its loss on the
  side's held-out rows is compared with the losses from 200 random pairs of sides at distance
  3 or more. Statistic: mean over sides of the rank (0–1) of the neighbour loss among the 200.
  Null: 0.5 (rank of a random pair); p from 10,000 random relabellings of which pair is the
  neighbour pair.

## Q4. Relation to the 48 Calls

- **P4a shared vocabulary.** Statistic: the number of Calls word types of four or more letters
  (folded) that occur as a contiguous string within a row of G as written (left to right; no
  other direction, no wrap, no skips). Control: each type replaced by a pseudo-word of the
  same length from a first-order letter-transition model of the Calls (keeps the Calls'
  letters and pairs), 10,000 sets. One-sided. Reported with it, not tested: the same count on C.
- **P4b n-gram closeness.** An interpolated trigram model (weights as S3c) is trained on all
  rows of G. For a text X, Δ_X = cross-entropy of a letter-shuffled copy of X minus the
  cross-entropy of X (bits per letter, words scored separately with a start symbol); Δ is the
  gain from letter order beyond letter frequencies. X = K (all 838 words; 10,000 shuffles for
  its Δ) and 1,000 samples each of L and E of the same number of letters (consecutive words,
  random start; one shuffle each). Statistic: Δ_K. One-sided p = share of the 2,000 L and E
  samples with Δ ≥ Δ_K. Reported with it: Δ_K against its own shuffles.

## Q5. How the tables were produced: Kelley's series and corrections

On 25b–28b every cell is in one of two interleaved series (Peterson's orientation marks / ~ `
or none), about 1,200 cells each, laid out like a chessboard. Peterson thinks the series were
written at different times. A letter-bigram model (add-0.5) is trained on G without 25b–28b.

- **P5a are the series written as running text?** Per side, loss (bits per letter) of reading
  the whole row in order minus the mean loss of reading each series on its own in row order
  (skipping the other series). Statistic: the sum over the seven sides 25b–28b. Control: the
  series labels permuted within each row (counts per row kept), 10,000 times. One-sided
  (series-by-series reading better than controls).
  Secondary **S5b**: the same along diagonals (upper left to lower right) for each series.
- **P5c do the series differ in their letters?** Statistic: the chi-squared statistic of the
  letter × series table pooled over 25b–28b (letters with fewer than 5 expected counts pooled).
  Control: series labels permuted within rows, 10,000. One-sided.
- **Descriptive only (no test):** where the uncertain marks, [sic] rows and 48-cell rows fall;
  the sizes of the tables of 29a–48b (about 1,200 cells, one series' worth) set against the
  two-series tables; the renumbered rows of 1b.

## What is not done

No translation or gloss. No search of directions, diagonals or knight's moves for Enochian
words. No claim beyond the stated statistics and controls.
