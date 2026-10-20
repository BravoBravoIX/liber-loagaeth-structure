# Weave study: pre-registration (written and committed before any scoring)

Follow-up to the Loagaeth study (`../README.md`, tests P5a, S5b, P5c, S3a). Question: by what
rule are Kelley's two letter series on 25b–28b laid into the 49 × 49 grid, and what follows?
Seed 20261019. CPU only, `nice -n 19`, at most 6 processes. No translation, no word search.

## What was looked at before this was written (no scoring)

1. **Prior art** (log in `PROGRESS.md`, batch 0). Peterson's note on 25b: one series along
   "alternating diagonals" from upper left to lower right, letters slanted 45° clockwise; a part
   filling the gaps of rows 1–5 left to right; a third series along diagonals from lower right to
   upper left; mark legend: `/` = letter slants 45° clockwise, `~` = rotated 135° counter
   clockwise (no legend for `` ` ``). Note on 26b: odd letters of row 1 and first letters of odd
   rows not tilted. Cocciolilo 2026a: on 25b "one extracted diagonal stream" grows 1, 3, 5 … 49
   … 3, 1, the same shape as the later leaves; 29a–42b alternate even (2 … 48 … 2) and odd
   (1 … 49 … 1) row-length fields; he explicitly does not claim generation from 25b to 29a.
2. **The partition** (descriptive, from the marks only). On all seven sides the marks follow
   the chessboard exactly: series A = cells with row + column even (1,201 cells), series B = odd
   (1,200); one exception (28a, a `/` on one B cell). Marks by side (A | B): 25b `/` | `~` (122
   unmarked B cells = rows 1–5); 26a none | `~`; 26b `/` (49 unmarked) | `~`; 27a none | `~`;
   27b `` ` `` | `/`; 28a `/` | `` ` ``; 28b `/` | `` ` ``.
3. **Row lengths of 29a–48b** (descriptive). Every partly filled table has rows of 1, 3, … 49
   … 3, 1 (1,201 cells) or 2, 4, … 48, 48 … 2 (1,200 cells), small slips aside. These are
   exactly the lengths of the diagonals of series A and of series B of a 49 × 49 chessboard.

So the hypothesis is: **each series is a diamond table of the 29a–48b kind, written into the
grid with its rows along diagonals, the page turned so that the letters slant; the slant mark
gives the writing direction.** Rotating the writer's baseline as Peterson's legend says: `/`
(45° clockwise) means writing down-right, step (+1, +1) in (row, column); `~` (135° counter
clockwise) means writing up-left, step (−1, −1).

## Candidate paths (20)

A path reads one series as lines. A line is a maximal chain of the series' cells along a step
vector, read in its direction; letter pairs are counted **within lines only** (so the order of
lines does not matter for the primary scores).
- Steps (row, column): rows (0, ±2); columns (±2, 0); diagonals (±1, ±1), all four; slope-3
  lines (±1, ±3) and (±3, ±1), all eight. (Knight steps change colour and cannot stay in a series.)
- Boustrophedon versions of rows (0, 2), columns (2, 0), diagonals (1, 1) and (1, −1) (sense
  alternates line by line).

## Scores

- **Primary score:** bits per within-line letter pair under an add-0.5 letter-bigram model
  trained on the rows (left to right) of 2a–25a (the same reference as P5a; 25b–28b excluded).
  Lower is more text-like. The folded 23-letter alphabet of the study; digits break pairs.
- Secondary score: number of distinct 6-grams of the path's lines that occur in the rows of
  2a–25a.

## Tests

Primary family (Holm over H1–H4, α = 0.05):

- **H1 slant gives direction (no fitting).** Cases: the nine (side, series) cells sets with a
  `/` or `~` mark: 25b A `/`, 25b B `~` (the 1,078 marked cells; the 122 unmarked cells of rows
  1–5 are scored separately as a descriptive check), 26a B `~`, 26b A `/` (marked cells), 26b B
  `~`, 27a B `~`, 27b B `/`, 28a A `/`, 28b A `/`. Predicted path: (+1, +1) for `/`, (−1, −1)
  for `~`. Statistic T1 = mean over the nine cases of (mean primary score of the 19 other paths
  − score of the predicted path). Reported with it: the predicted path's rank in each case.
  Control: in each case the letters are permuted within each row among that series' cells (row
  letter counts and the series kept), 10,000 times, T1 recomputed. One-sided p.
- **H2 held-out direction for the unlegended marks.** Upright cells (no mark): fit the best of
  the 20 paths on 26a A, test it on 27a A. `` ` `` cells: fit on 27b A, test on 28a B and 28b B.
  Statistic T2 = mean over the three test cases of (mean of the other 19 − score of the fitted
  path). Control as H1 (10,000), fitting redone on each control. One-sided p.
- **H3 the series match the partly filled tables.** Each series read by the rule (H1's
  predicted path where marked; otherwise the H2-fitted path; lines in order from the end where
  the first line starts, which does not affect this score) gives a 1,200- or 1,201-letter
  sequence of lines. Statistic: number of distinct 8-grams shared between the 14 series and the
  rows (left to right) of 29a–48b. Control: each series regenerated as a first-order Markov
  chain from its own letter pairs with the same line lengths and first letters (1,000 times).
  One-sided p. Reported with it: the same count against the rows of 2a–25a, and the best-matching
  29a–48b table per series.
- **H4 do the two series of a side share material?** Statistic: distinct 8-grams shared between
  A and B of the same side, summed over the seven sides. Control: the same Markov regeneration
  (1,000). One-sided p. Reported with it: the same with B reversed (a mirror), and A of each side
  against B of the other six sides.

Controls and checks (not in the Holm family):
- **C1 specificity.** The 20 paths applied to the two chessboard colours of each single-series
  table 2a–25a: for each side, the rank of the best diagonal path and of row (0, +2). The rule
  should not win there.
- **S1 line order.** For the H1 cases, letter pairs joining the end of one line to the start of
  the next, with lines in order from either corner, against 1,000 random line orders: is the text
  continuous across line ends, and from which corner?
- **S2 line ends.** Share of the word-final letters of Q1 (h, x, s) at line ends against
  within lines (exploratory; there are no word marks on 25b–28b).
- **S3** the 122 unmarked B cells of 25b rows 1–5: rank of (0, +2) (Peterson: left to right).

## Stop rule

Each test is run once at the stated size, after a smoke run of 20 controls to catch crashes; no
parameter is changed after seeing a result. If a bug is found, it is fixed, logged in
`PROGRESS.md` and the test rerun in full. If H1 fails after Holm, no rule is claimed; H3 and H4
are still reported but labelled exploratory. Anything not listed here is exploratory and says so.
