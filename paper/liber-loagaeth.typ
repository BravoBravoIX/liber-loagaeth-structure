// Working paper for the liber-loagaeth-structure repository. Build: paper/build.sh
#set document(title: "Liber Loagaeth: a pre-registered structural study of the tables", author: "Brett Burford")
#set page(paper: "a4", margin: (x: 2.3cm, y: 2.4cm), numbering: "1")
#set text(font: ("Libertinus Serif", "New Computer Modern"), size: 10.5pt, lang: "en", region: "au")
#set par(justify: true, leading: 0.62em)
#set heading(numbering: "1.")
#show heading: set block(above: 1.3em, below: 0.7em)
#show link: set text(fill: rgb("#1a4f8b"))
#set table(stroke: 0.4pt + luma(150), inset: 5pt)
#show table: set text(size: 9.2pt)
#show table: set par(justify: false)

#align(center)[
  #text(size: 16pt, weight: "bold")[Liber Loagaeth: a pre-registered structural study of the tables]
  #v(0.5em)
  #text(size: 11pt)[Brett Burford]
  #v(0.2em)
  #text(size: 9pt)[ORCID #link("https://orcid.org/0009-0003-6599-8297")[0009-0003-6599-8297] · Independent researcher, Australia]
  #v(0.2em)
  #text(size: 9pt)[Working paper, version 1.0, 19 October 2026 · not peer reviewed]
  #v(0.2em)
  #text(size: 9pt)[Code, data and results: #link("https://github.com/BravoBravoIX/liber-loagaeth-structure")[github.com/BravoBravoIX/liber-loagaeth-structure] · doi:10.5281/zenodo.23487865]
]

#v(0.8em)
#block(inset: (x: 1.2cm))[
  #text(weight: "bold")[Abstract.] _Liber Loagaeth_ (British Library, Sloane MS 3189), the book of letter tables that John Dee and Edward Kelley received in 1583, has never been read, and this paper does not try to read it. It asks how the tables were made. From Joseph Peterson's cell-by-cell edition we build a coordinate-addressed corpus of 196,353 letters on 96 sides; the only other machine-readable grids turn out to copy the same edition, and 78 of 80 randomly chosen cells agree with the page images (2 doubtful, none wrong). We reproduce the one earlier computational study (Zubair 2026) and correct it: its letter total counts the whole web page, its lowest index of coincidence (0.044) belongs to an appendix of _Book of Soyga_ tables, and its test of the Soyga generation rule used the wrong baseline; with each table's own letters as the baseline, no table departs from chance. We then ran ten tests that were written down and committed before scoring, each against 10,000 controls that keep the tables' own letter statistics, with Holm's correction. Six are positive: long strings recur across the book far beyond chance (6,679 distinct 8-letter strings against about 1,240 in controls), mostly on different sides; the word marks on leaves 2a–3b fall at letter-dependent places and cut long words (8.8 letters); and on 25b–28b Kelley's two interleaved letter series read as text-like sequences and differ in their letters. Four are negative: there is no pairing of a- and b-sides, the cell above does not predict a cell, and the 48 Calls are neither found in the rows more often than pseudo-words nor closer to the tables in letter order than Latin or English text. The evidence weighs toward tables built from a recurring stock of word-like strings, laid out row by row and varied gradually through the book, with the two-series tables written along diagonals, and against the Calls being drawn from the tables' rows. Nothing here is a decipherment or a translation.
]

= Introduction

_Liber Loagaeth_, also called _Liber Mysteriorum Sextus et Sanctus_, survives in a fair copy in Edward Kelley's hand, British Library Sloane MS 3189. It was received in 1583, in the sessions that John Dee recorded with Kelley as his scryer. Leaves 1a and 1b hold words written as running text. Every side from 2a to 48b holds a table: 54 full tables of $49 times 49$ cells on 2a–28b and 40 partly filled tables on 29a–48b. No key or reading was recorded. The next year, in Kraków, Dee and Kelley received the 48 Calls (_Claves Angelicae_), word by word, with English glosses.

The tables have been edited and interpreted, but rarely measured. The one computational study of the whole book (Zubair 2026a) reports an index of coincidence that it reads as "natural-language-like", and finds the tables independent of, and on one side "anti-correlated" with, the generation rule of the _Book of Soyga_. A recent qualitative reading (Cocciolilo 2026c) proposes that a- and b-sides were made in pairs. None of these claims had been tested against controls that keep the tables' own letter statistics.

This paper asks five questions about how the tables were made, all made checkable and written into a pre-registration before scoring: (1) do Peterson's word marks on 2a–3b behave like word boundaries; (2) do long strings recur, and are a- and b-sides made in pairs; (3) can a table be predicted from neighbouring cells or neighbouring tables; (4) are the 48 Calls drawn from the tables; and (5) how were the two-series tables 25b–28b written? It is a structural study: no translation is attempted and no grid paths are searched for words.

= Earlier work

- *Peterson* edited Sloane MS 3189 cell by cell, with marks for doubtful letters, word ends and letter orientation, and described the two series of 25b–28b as written along diagonals. Every letter here is read from his edition.
- *Laycock* (1978; revised 1994) compiled the vocabulary of the Calls and judged them language-like in syntax, unlike the untranslated Loagaeth. *Leitch* (2010) gave the history of Loagaeth and the Calls and a lexicon. *Burns and Moore* (2010) interpreted the tables and their use. *Harkness* (1999) and *Asprem* (2012) set the sessions and their reception in context, and *Whitby* (1982) edited the record of the sessions of 1581–1583.
- *Zubair* (2026a, b, c) made the first computational analysis of the whole book: letter counts (212,082 letters), an IC range of 0.044–0.101, a test of the Soyga rule against a 1/23 baseline, and an argument that the Calls are structurally independent of the tables.
- *Cocciolilo* (2026a, b, c) proposed a staged "table-engine" reading, qualitative and without translation, including a pairing of a- and b-sides.
- *lorselq* published machine-readable grids of 2a–16b with marks for uncertain cells and lacunae; *anasofiadias* published page images of the manuscript and a transcription; *Ponzi* fitted Zipf's law to Peterson's text.
- *Reeds* (2006) found the rule and step function of the _Book of Soyga_ tables that Zubair applied to Loagaeth.

= Sources and data

The corpus is parsed from Peterson's edition (Esoteric Archives, © 1998, updated 2 February 2023), which is under copyright and is not redistributed; a script fetches it and checks its SHA-256, and the pipeline rebuilds the corpus locally. The 48 Calls come from Casaubon's 1659 _True & Faithful Relation_, in the CC0 keyed text EEBO-TCP A37412: 838 word rows of the dictation tables, 4,402 letters, in forward form. Period reference texts are Latin (Latin Wikisource, CC BY-SA 4.0: Alberti, _De pictura_, 1435, and five works of Nicolaus Cusanus, 1440–1450) and English (Project Gutenberg, public domain: Chaucer's _Boece_ and _Astrolabe_, the Paston Letters, Caxton's _Chesse_, the _Book of Quinte Essence_ and the _Forme of Cury_, c. 1380–1509, in original spelling). Zubair's per-table counts and Soyga-rule table come from his Zenodo record (CC BY 4.0). The lorselq grids (no licence) were used only for a cell-by-cell witness check, and eight folio images from the anasofiadias repository (rights unclear) only for spot checks by eye; neither is redistributed, and neither is needed to rerun the main results. The British Library's own images of the manuscript were unavailable.

= Method

Every random process uses the seed 20261019. The tests ran on CPU only, with numpy.

*Corpus.* Each cell becomes one record: side, row, column, its letters, and flags for Peterson's marks (uncertain, word end, accent, capital, orientation, struck through, `[sic]`). For the statistics a cell is one symbol, its first letter in lower case without accents, with _u_, _v_ and _w_ read as one letter and _j_ as _i_; digit cells break every string. The parse is checked against the lorselq grids, row by row with an alignment, and against the page images on a seeded random sample of 80 cells on eight sides and on every disputed cell. Two vision models read the same crops, as advisers only.

*Zubair reproduced.* We count letters in our corpus and, to emulate his parse, every letter in each leaf's section of the web page. For the Soyga rule (a cell is the cell above moved on by $f$ of the cell to its left, mod 23, with Reeds's $f$) we score the top-left $36 times 36$ block of 2a–9a, compare the match rate with the rate expected from each table's own letters, and test it against 10,000 shuffles of each table, with Holm's correction over the fifteen tables.

*Pre-registration.* The questions, the ten primary tests (P), their secondary tests (S), the controls, the multiple-testing rule and a stop rule were written down and committed on 19 October 2026 (commit `7127723` of the author's working repository, reproduced unchanged in the repository) before any statistic was computed; the file lists what had been looked at before. The test code was committed four minutes later, run once with 20 controls as a smoke test to catch crashes, and then run in full with no parameter changed. p-values are one-sided, $(1 + k) slash (1 + n)$ for $k$ of $n$ = 10,000 controls at least as extreme, so the smallest possible is 0.0001; they are corrected with Holm's method over the ten primary tests at $alpha = 0.05$. One slip in the text: it gives the folded alphabet as 22 letters; it has 23 (a–z without _j_, _u_ and _w_), and the code uses the 23 present.

*Controls.* Every control keeps the letter frequencies of the text it replaces and keeps rows as rows unless stated. For repeats (P2a, P2c), each row is regenerated from its own side's letter-pair (first-order Markov) statistics with the same first letter and length. For the word marks (P1b), the marks are put back at random within each row. For the cell above (P3a), the rows of each side are put in random order and the gain in bits on held-out rows (every fifth row) is recomputed. For pairing (P2b), which of the 53 adjacent pairs of sides count as "same leaf" is chosen at random. For the Calls, each word is replaced by a pseudo-word of the same length from the Calls' own letter pairs (P4a), and the Calls' gain from letter order under a letter-trigram model of the tables is compared with 1,000 samples each of Latin and English of the same size (P4b). For the two series of 25b–28b (P5a, P5c), the series labels are permuted within each row.

= Results

== The corpus

The corpus has 96 sides, 196,721 cells, 196,353 letters and 377 digits: the word leaves 1a and 1b (18,686 letters), 54 full tables on 2a–28b (130,047 cells) and 40 partly filled tables on 29a–48b (47,988 cells). Of the 2,646 rows of the full tables, 48 have 48 cells, 37 of them on 8b, where the manuscript's last column is empty. Folio is leaf + 8 (2a is f. 10r), confirmed on eight sides.

The lorselq grids disagree with our parse on 3,035 of 72,431 letters, but 3,033 of these come from one file: lorselq's 5b is a copy of its 4b, and the image of f. 13v shows Peterson's 5b. Without 5b, 2 of 70,030 letters disagree, both extra letters in lorselq, and there are no substitutions. The grids therefore copy the same edition and check our parse, not Peterson's reading. On the page images, 78 of 80 random cells agree with Peterson, 2 are doubtful and none is clearly wrong; in each disputed case the image sides with Peterson. The local vision model matched the edition on 51 % of cells, too few to judge Kelley's secretary hand; Claude (Anthropic) answered 10 of 15 crops and matched on 74 %. Neither changes the corpus.

== Zubair (2026a) reproduced and corrected

Counting every letter in each leaf's section of the web page, headings and notes included, gives 212,500 letters, within 25 letters of Zubair's figure on every side, against 196,353 in the tables themselves. His 48b section runs on into Peterson's appendix of four _Book of Soyga_ tables, and with that text our emulated IC for 48b is 0.043744, exactly his value: the low end of his IC range is not Loagaeth. On the tables alone the IC runs from 0.0597 (47b) to 0.1017 (26a), mean 0.0829. A high IC here comes from one dominant letter, _a_ (37,315 letters); it does not show language. For the Soyga rule (Table 1), the right baseline is not 1/23 but the rate expected from each table's own letters, 3.2–4.0 %; no table departs from chance after Holm's correction, and Zubair's "anti-correlated" side 2a (2.99 % against 4.35 %) gives 2.94 % against a shuffle mean of 3.54 % (p 0.28).

#figure(
  table(
    columns: (auto, 1fr, 1fr),
    align: (left, center, center),
    table.header([*Quantity*], [*Zubair (2026a)*], [*This study*]),
    [letters], [212,082], [196,353 in the tables; 212,500 counting the whole page],
    [IC range (mean)], [0.0437–0.1013 (0.0821)], [0.0597–0.1017 (0.0829)],
    [lowest IC], [0.044, read as random-like], [0.043744 only with the Soyga appendix in 48b],
    [Soyga-rule match rate, 2a–9a], [3.71–5.76 %], [2.78–5.31 %],
    [baseline], [4.35 % (1/23)], [3.2–4.0 % (each table's letters; mean 3.52 %)],
    [tables departing from chance], [—], [none after Holm (smallest raw p 0.013, Holm 0.19)],
  ),
  caption: [Zubair's counts reproduced and corrected (`results/zubair_repro.json`).],
)

== The pre-registered tests

Six of the ten primary tests are positive after Holm's correction and four are negative (Table 2).

#figure(
  table(
    columns: (auto, 2fr, 1.2fr, 1.6fr, auto, auto),
    align: (left, left, center, center, center, center),
    table.header([*Test*], [*Question*], [*Observed*], [*Controls: mean (95 % range)*], [*p*], [*Holm*]),
    [P1a], [word lengths differ from the Calls'], [JSD 0.265 bits], [0.005 (0.002–0.010)], [0.0001], [*0.001*],
    [P1b], [word marks depend on the letters], [MI 0.207 bits], [0.031 (0.027–0.035)], [0.0001], [*0.001*],
    [P2a], [repeated 8-letter strings in the full tables], [6,679], [1,244 (1,149–1,339)], [0.0001], [*0.001*],
    [P2b], [a- and b-sides made in pairs], [−0.021], [0.000 (−0.056 to 0.057)], [0.73], [1],
    [P2c], [8-letter strings shared between sides], [6,436], [1,193 (1,100–1,285)], [0.0001], [*0.001*],
    [P3a], [the cell above helps predict a cell], [−14,382 bits], [−14,187 (−14,535 to −13,828)], [0.86], [1],
    [P4a], [Calls words found in the rows], [50 of 578], [58.4 (46–71)], [0.92], [1],
    [P4b], [the Calls' letter order close to Loagaeth's], [Δ 0.499 bits], [Latin 0.471, English 0.463], [0.18], [0.74],
    [P5a], [the two series read as running text], [1.33], [0.37 (0.16–0.59)], [0.0001], [*0.001*],
    [P5c], [the two series differ in their letters], [χ² 502], [87 (66–110)], [0.0001], [*0.001*],
  ),
  caption: [The ten primary tests, 10,000 controls each (`results/l3_summary.json` and `results/l3_*.json`). Bold: Holm-adjusted p < 0.05. For P3a the gain is negative for real and shuffled rows alike: adding the cell above as context costs bits on held-out rows, and the real rows do no better than shuffled ones.],
)

*Words.* The 1,088 word marks on 2a–3b give 1,084 words, averaging 8.8 letters, against 5.3 for the Calls, 5.9 for the Latin and 4.1 for the English reference. The length distribution is nearest Latin (JSD 0.139, bootstrap 95 % 0.125–0.159) and far from the Calls (0.265) and English (0.370). The marks depend on the letters on either side of them about six times more than random placement within the same rows allows.

*Repetition.* Long strings recur far beyond what each side's letter-pair statistics produce, and almost all of the recurring 8-letter strings occur on two or more sides. In secondary tests, 391 distinct 12-letter strings recur (Markov controls 1.8 on average, at most 12) and the longest repeated string is 17 letters (controls at most 15 in 200). There is no sign of a/b pairing on 2a–28b, nor on 29a–48b or with shared 6-letter strings (all secondary p ≥ 0.19).

*Generation.* The cell above does not help to predict a cell on held-out rows, on the 53 sides with enough full rows, and no single side survives Holm. In secondary tests the cell above-left helps overall ($p = 0.0001$), but per side only on 25b, 26a, 27b, 28a and 28b, and the cell above-right only on 26b and 27a: all seven two-series tables, and no others, carry a diagonal dependence. Rows do not copy the three rows above them more than random rows of the same side do ($p = 0.047$, not significant after Holm within the question). A letter model trained on a table's two neighbours predicts its held-out rows better than models trained on distant pairs of tables on 53 of the 54 sides (mean rank 0.04 among 200 distant pairs, against 0.5 by chance; $p = 0.0001$): the material drifts slowly through the book.

*The Calls.* Calls words of four letters or more turn up in the rows of 2a–28b no more often than pseudo-words built from the Calls' own letter pairs (50 of 578 types, against 58.4), and likewise on 29a–48b (34 against 33.0). The Calls gain 0.499 bits a letter from their letter order under a model of the tables, against 0.471 for Latin and 0.463 for English samples of the same size: no closer than ordinary text.

*The two series.* On 25b–28b, reading each of Kelley's series on its own gives more text-like letter pairs than reading the rows straight through, and reading each series along diagonals more so again (9.67 against 4.72, in bits per letter pair summed over the seven sides; $p = 0.0005$ on 2,000 controls, secondary). The two series differ in their letters. Each series holds about 1,200 cells, and every partly filled table on 29a–48b holds 1,195–1,201 letters except 36b (1,176): those tables look like one series written and the other never filled in. The 65 uncertain marks fall on 21 sides between 4a and 17b.

= Discussion

*What the evidence weighs toward.* The tables look built from a recurring stock of word-like strings, laid out row by row and varied gradually through the book: long strings recur across many sides far beyond what letter-pair statistics give, neighbouring tables share the most, and the word marks on 2a–3b fall at letter-dependent places and cut long words. No simple mechanical rule of the Soyga kind and no "cell above" rule is visible. The two-series tables 25b–28b were written differently, as two interleaved series that read as text-like sequences along diagonals and differ in their letters, and the partly filled tables of 29a–48b are each one series' worth. There is no pairing of a- and b-sides. The evidence weighs against the 48 Calls being drawn from the tables' rows; a relation by some other path (directions, skips, grid paths) was not searched, by design. "Text-like" and "word-like" describe statistics measured against controls; they do not show that the tables encode a language.

*What is new*, as far as a search of GitHub, Zenodo and the web on 18–19 October 2026 found:
+ a checked, coordinate-addressed corpus of the whole book, with the finding that the lorselq grids copy Peterson's edition (with one misfiled side) and so are not an independent witness, and an image check of a random sample;
+ corrections to Zubair (2026a): the letter total counts page text; the lowest IC is Peterson's appendix of Soyga tables; and with each table's own letters as baseline the Soyga rule is at chance, so the "anti-correlation" disappears;
+ ten pre-registered, controlled tests with Holm's correction, giving the recurring strings shared between sides, the slow drift between tables, the letter-dependence of the word marks and the diagonal series of 25b–28b, and the negative results: no a/b pairing (against Cocciolilo), no cell-above rule, and no sign that the Calls were drawn from the rows (compatible with Zubair 2026b, now with matched controls);
+ the observation that the partly filled tables are each the size of one series.

*Limits.*
+ Everything is read from Peterson's edition. The image check covers 80 random cells and the disputed cases on eight sides; a full collation was not possible, and the lorselq grids copy the same edition. The series labels of 25b–28b are Peterson's orientation marks.
+ Recurring strings and letter-dependent marks are what text would give, but also what copying from a stock of invented strings, or any generator with a memory longer than one letter, would give. The controls rule out first-order letter statistics, not every mechanism.
+ The pre-registration was not blind: it was written after the corpus counts, the witness and image checks and Zubair's counts had been seen, and the test code was written after it.
+ The Calls word list was extracted by a rule (176 of 838 forward forms are inferred), and the reference texts are one Latin and one English set.

= Data and code availability

Code (MIT), our data and all results (CC BY 4.0) are at #link("https://github.com/BravoBravoIX/liber-loagaeth-structure")[github.com/BravoBravoIX/liber-loagaeth-structure], with the pre-registration; a Zenodo DOI will be added. Third-party texts are not redistributed: a script fetches them from where their owners publish them and checks their SHA-256 sums, and the pipeline then rebuilds every results file byte for byte (about an hour and a half on CPU). No text of Peterson's edition beyond short cell references, and no manuscript image, is included.

= Acknowledgements

This study stands on the work of Joseph H. Peterson, whose edition is its text, and of Donald Laycock, Aaron Leitch, Muhammad Zubair, Gary Cocciolilo, lorselq, anasofiadias and Jim Reeds. The analysis code was written with the help of an AI coding assistant (Claude, Anthropic); the author checked the results and is responsible for any errors.

= References

#set par(hanging-indent: 1.2em, justify: false)
#set text(size: 9.5pt)

anasofiadias. _Loagaeth_. #link("https://github.com/anasofiadias/Loagaeth")[github.com/anasofiadias/Loagaeth].

Asprem, E. (2012). _Arguing with Angels: Enochian Magic and Modern Occulture_. Albany: SUNY Press.

British Library, Sloane MS 3189.

Burns, T. and Moore, J. (2010). John Dee and Edward Kelley's Great Table (or, What's This Grid For, Anyway?). _Journal of the Western Mystery Tradition_ 2.

Casaubon, M. (ed.) (1659). _A True & Faithful Relation of What passed for many Yeers Between Dr. John Dee … and Some Spirits_. London. EEBO-TCP A37412, #link("https://github.com/textcreationpartnership/A37412")[github.com/textcreationpartnership/A37412].

Cocciolilo, G. (2026a). Liber Loagaeth as an Angelic Operating Manuscript. Zenodo. #link("https://doi.org/10.5281/zenodo.19914827")[doi:10.5281/zenodo.19914827].

Cocciolilo, G. (2026b). Compressed, Expanded, Operational: A Dee-First Layered Reconstruction Model of Liber Loagaeth, Soyga, and the Great Table. Zenodo. #link("https://doi.org/10.5281/zenodo.19917987")[doi:10.5281/zenodo.19917987].

Cocciolilo, G. (2026c). Liber Loagaeth as a Staged Table-Engine: A Structural Reconstruction of John Dee's Angelic Book. Zenodo. #link("https://doi.org/10.5281/zenodo.19976902")[doi:10.5281/zenodo.19976902].

Harkness, D. E. (1999). _John Dee's Conversations with Angels: Cabala, Alchemy, and the End of Nature_. Cambridge: Cambridge University Press.

Laycock, D. C. (1978; revised 1994). _The Complete Enochian Dictionary_. London.

Leitch, A. (2010). _The Angelical Language_, 2 vols. Woodbury, MN: Llewellyn.

lorselq. _enochian\_language\_modeling_ (commit 0e296b4). #link("https://github.com/lorselq/enochian_language_modeling")[github.com/lorselq/enochian\_language\_modeling].

Peterson, J. H. (ed.). _Liber Loagaeth_. Esoteric Archives, © 1998, updated 2 February 2023. #link("https://www.esotericarchives.com/dee/sl3189.htm")[esotericarchives.com/dee/sl3189.htm].

Ponzi, M. Zipf's Law and Angelic Languages. Medium. #link("https://medium.com/viridisgreen/zipfs-law-and-angelic-languages-96f05109e8f3")[medium.com/viridisgreen].

Reeds, J. (2006). John Dee and the magic tables in the Book of Soyga. In S. Clucas (ed.), _John Dee: Interdisciplinary Studies in English Renaissance Thought_. Dordrecht: Springer, pp. 177–204. #link("https://doi.org/10.1007/1-4020-4246-9_10")[doi:10.1007/1-4020-4246-9_10].

Whitby, C. L. (1982). _John Dee's Actions with Spirits, 22 December 1581 to 23 May 1583_. PhD thesis, University of Birmingham. #link("https://etheses.bham.ac.uk/id/eprint/3149/")[etheses.bham.ac.uk/id/eprint/3149].

Zubair, M. (2026a). First Computational Analysis of Liber Loagaeth: Statistical and Algorithmic Findings. Zenodo. #link("https://doi.org/10.5281/zenodo.19708274")[doi:10.5281/zenodo.19708274].

Zubair, M. (2026b). Structural Independence of the 49 Loagaeth Calls and 48 Claves Angelicae: A Computational Comparison. Zenodo. #link("https://doi.org/10.5281/zenodo.19709277")[doi:10.5281/zenodo.19709277].

Zubair, M. (2026c). Loagaeth in Context: Diary Evidence, the Mystery of Mysteries, and the Monas Hieroglyphica Connection. Zenodo. #link("https://doi.org/10.5281/zenodo.19709477")[doi:10.5281/zenodo.19709477].
