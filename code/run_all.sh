#!/usr/bin/env bash
# Rerun the whole study from the fetched sources.
# Usage: code/run_all.sh SOURCE_DIR [WORK_DIR]    (SOURCE_DIR filled by scripts/fetch_sources.sh;
#        WORK_DIR, default work/, holds the rebuilt corpus and reference texts; git ignores it)
# CPU only. Python 3.13 with numpy 2.5.4, run through uv (set PYTHON to use another interpreter
# that has numpy). The L3 tests run under nice -n 19, at most MAXJ (default 6) at a time; the
# longest (q2rep) takes about 1.5 hours, the rest a few minutes each. The weave study of 25b-28b
# (v1.1) takes about 3 minutes in one process; it was first run with Python 3.12 and numpy 2.2.6,
# which it uses here (set WPYTHON to change; numpy 2.5.4 changes the last digit of two control
# summaries in results/weave_h1.json and one in weave_summary.json, nothing else).
set -euo pipefail
SRC="$(cd "$1" && pwd)"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${2:-$HERE/../work}"
mkdir -p "$WORK"
WORK="$(cd "$WORK" && pwd)"
CORPUS="$WORK/corpus"
REF="$WORK/reference"
MAXJ="${MAXJ:-6}"
read -r -a PY <<< "${PYTHON:-uv run --no-project --python 3.13 --with numpy==2.5.4 python}"
read -r -a WPY <<< "${WPYTHON:-uv run --no-project --python 3.12 --with numpy==2.2.6 python}"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$HERE"
mkdir -p "$WORK/logs"

# L0: the corpus from Peterson's edition, and the 48 Calls from Casaubon 1659
"${PY[@]}" corpus.py "$SRC/peterson/sl3189.htm" "$CORPUS" > "$WORK/logs/corpus.log"
"${PY[@]}" calls.py "$SRC/calls/tcp_A37412.xml" "$CORPUS" > "$WORK/logs/calls.log"
# period Latin and English reference texts
"${PY[@]}" reference_corpora.py "$SRC" "$REF" > "$WORK/logs/reference.log"
# L1: Zubair (2026) reproduced
nice -n 19 "${PY[@]}" reproduce_zubair.py "$CORPUS" "$SRC/peterson/sl3189.htm" "$SRC/zubair" \
  > "$WORK/logs/zubair.log"
# L3: the pre-registered tests, 10,000 controls each
for t in q2rep q3a q5 q4 q3b q1 q3c q2pair; do
  while [ "$(jobs -rp | wc -l)" -ge "$MAXJ" ]; do wait -n; done
  nice -n 19 "${PY[@]}" l3_tests.py "$t" "$CORPUS" "$REF" 10000 > "$WORK/logs/$t.log" 2>&1 &
done
wait
"${PY[@]}" l3_summary.py > "$WORK/logs/summary.log"
# v1.1, the weave study of 25b-28b (results/weave_preregistration.md): 10,000 controls for H1, H2,
# C1 and S3, 1,000 Markov controls for H3, H4, S1 and S2; then Holm, then the exploratory E1-E3
nice -n 19 "${WPY[@]}" weave.py "$CORPUS" 10000 1000 h1 h2 c1 s3 h3 h4 s1 s2 \
  > "$WORK/logs/weave.log" 2>&1
"${WPY[@]}" weave_summary.py > "$WORK/logs/weave_summary.log"
nice -n 19 "${WPY[@]}" weave_explore.py "$CORPUS" 1000 > "$WORK/logs/weave_explore.log" 2>&1
"${WPY[@]}" weave_rows.py "$CORPUS"
"${WPY[@]}" weave_figure.py
echo "done; logs in $WORK/logs"
