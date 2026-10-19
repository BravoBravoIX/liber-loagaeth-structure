#!/usr/bin/env bash
# Download the public sources this study is built from, into SOURCE_DIR, and check them against
# the SHA-256 sums of the copies used for the published results (sources/SHA256SUMS).
# None of these files is redistributed here; each stays under its own terms (README, Licensing).
# Every download uses HTTPS with the certificate verified (curl's default); nothing is fetched
# with verification turned off.
# Needs bash, curl, python3 (standard library) and sha256sum.
# Usage: scripts/fetch_sources.sh SOURCE_DIR
#        WITH_LORSELQ=1 scripts/fetch_sources.sh SOURCE_DIR   (also the optional witness check)
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
SUMS="$HERE/sources/SHA256SUMS"
OUT="$1"
mkdir -p "$OUT"/peterson "$OUT"/calls "$OUT"/zubair "$OUT"/latin "$OUT"/english
UA="liber-loagaeth-structure source fetch (one request at a time)"
get() { [ -s "$2" ] || { curl -fsSL --proto '=https' --retry 3 -A "$UA" -o "$2.part" "$1" && mv "$2.part" "$2"; sleep 1; }; }

# 1. Joseph H. Peterson, Liber Loagaeth (Sloane MS 3189), Esoteric Archives edition.
#    (c) Peterson; research use only, never redistributed. The study's copy is identified by its
#    SHA-256 (sources/SHA256SUMS), not by its date. On 19 October 2026 the site's TLS certificate
#    had expired, so a verified download failed; if that is still so, save the page from
#    https://www.esotericarchives.com/dee/sl3189.htm by other means as
#    SOURCE_DIR/peterson/sl3189.htm and run this script again: the SHA-256 check below confirms
#    that it is the same copy.
if ! get https://www.esotericarchives.com/dee/sl3189.htm "$OUT/peterson/sl3189.htm"; then
  rm -f "$OUT/peterson/sl3189.htm.part"
  echo "WARNING: Peterson's page could not be fetched with a verified certificate." >&2
  echo "  Save it by hand as $OUT/peterson/sl3189.htm (see the comment in this script)." >&2
fi

# 2. The 48 Calls: Casaubon (1659), A True & Faithful Relation, EEBO-TCP A37412 (CC0),
#    pinned to the Text Creation Partnership repository commit used.
TCP_COMMIT=1a7088384b5e4c702f702f0c8ff1e2c110947cc1
get "https://raw.githubusercontent.com/textcreationpartnership/A37412/$TCP_COMMIT/A37412.xml" \
    "$OUT/calls/tcp_A37412.xml"

# 3. Zubair (2026), First Computational Analysis of Liber Loagaeth, Zenodo 10.5281/zenodo.19708274
#    (CC BY 4.0): the two tables of counts that L1 reproduces.
for f in per_table_frequency.csv soyga_vs_loagaeth_tables_1_15.csv; do
  get "https://zenodo.org/api/records/19708274/files/$f/content" "$OUT/zubair/zubair_$f"
done

# 4. Period Latin (Latin Wikisource, CC BY-SA 4.0), at fixed page revisions, as rendered HTML
#    from the MediaWiki parse API.
while read -r slug revid; do
  dest="$OUT/latin/$slug.html"
  [ -s "$dest" ] && continue
  curl -fsSL --proto '=https' --retry 3 -A "$UA" -o "$dest.json" \
    "https://la.wikisource.org/w/api.php?action=parse&oldid=$revid&prop=text%7Crevid&format=json"
  python3 -I -c 'import json,sys,pathlib; d=json.load(open(sys.argv[1],encoding="utf-8"))["parse"]; pathlib.Path(sys.argv[2]).write_text(d["text"]["*"],encoding="utf-8")' \
    "$dest.json" "$dest"
  rm -f "$dest.json"
  sleep 1
done <<'EOF'
De_pictura__Prologus 127033
De_pictura__Liber_I 127034
De_pictura__Liber_II 127035
De_pictura__Liber_III 127036
De_docta_ignorantia__Dedicatio 120920
De_docta_ignorantia__1 120941
De_docta_ignorantia__2 120967
De_docta_ignorantia__3 120981
De_coniecturis 183024
Apologia_doctae_ignorantiae 183028
Idiota_de_mente 264810
EOF

# 5. Period English: Project Gutenberg plain-text editions (public domain).
for n in 44833 45027 40989 41024 41081 42239 42240 10672 17179 8102; do
  get "https://www.gutenberg.org/cache/epub/$n/pg$n.txt" "$OUT/english/pg$n.txt"
done

# 6. Optional: lorselq/enochian_language_modeling grids (no licence), for code/compare.py only.
if [ "${WITH_LORSELQ:-0}" = 1 ]; then
  mkdir -p "$OUT/lorselq"
  LQ=https://raw.githubusercontent.com/lorselq/enochian_language_modeling/0e296b4/src/loagaeth/liber_loagaeth_construction/leaves
  for s in 01c 02a 02b 03a 03b 04a 04b 05a 05b 06a 06b 07a 07b 08a 08b 09a 09b 10a 10b \
           11a 11b 12a 12b 13a 13b 14a 14b 15a 15b 16a 16b; do
    get "$LQ/leaf$s.json" "$OUT/lorselq/leaf$s.json"
  done
fi

cd "$OUT"
missing=0
while read -r _ f; do
  case "$f" in lorselq/*) continue ;; esac
  [ -s "$f" ] || { echo "MISSING: $f" >&2; missing=1; }
done < "$SUMS"
if sha256sum --quiet --ignore-missing -c "$SUMS" && [ "$missing" = 0 ]; then
  echo "all sources match the copies used for the published results"
else
  echo "WARNING: a source is missing or differs from the copy used for the published results." >&2
  echo "The rebuild may still run, but results can differ (see README, How to reproduce)." >&2
fi
