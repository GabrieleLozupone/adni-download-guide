#!/usr/bin/env bash
# Download the ZIP links of an IDA collection (Advanced Download -> list of URLs), one at a time, with resume.
#
#   bash scripts/download_urls.sh urls.txt /path/to/ADNI_zips
#
# urls.txt: one link per line (blank lines and lines starting with # are ignored).
# Files are saved as 001_<name>.zip, 002_<name>.zip, ... in the order of the list (IDA often gives every ZIP of a
# collection the same name). A finished file gets a .done marker and is skipped next time, so you can simply run
# the command again after an interruption. The log (download_log.tsv) never contains the links: they work
# without a login, so keep urls.txt private and delete it when you are done.
set -uo pipefail

if [ $# -ne 2 ]; then
  echo "usage: $0 urls.txt output_folder" >&2
  exit 2
fi
urls="$1"; out="$2"
mkdir -p "$out"
log="$out/download_log.tsv"
[ -f "$log" ] || printf "file\thttp_code\tbytes\tseconds\tbytes_per_s\tfinished_at\n" > "$log"

n=0; failed=0
while IFS= read -r url || [ -n "$url" ]; do
  url="${url%%[[:space:]]}"
  case "$url" in ""|\#*) continue ;; esac
  n=$((n + 1))
  name=$(basename "${url%%\?*}")
  file="$out/$(printf "%03d" "$n")_$name"
  if [ -f "$file.done" ]; then
    echo "skip  $(basename "$file") (already done)"
    continue
  fi
  echo "->    $(basename "$file")"
  stats=$(curl -fL -C - --retry 5 --retry-delay 20 --connect-timeout 60 \
          -o "$file" -w "%{http_code}\t%{size_download}\t%{time_total}\t%{speed_download}" "$url")
  rc=$?
  printf "%s\t%s\t%s\n" "$(basename "$file")" "$stats" "$(date '+%Y-%m-%d %H:%M:%S')" >> "$log"
  if [ $rc -eq 0 ]; then
    touch "$file.done"
    echo "ok    $(basename "$file")  ($stats)"
  else
    failed=$((failed + 1))
    echo "FAIL  $(basename "$file")  curl exit $rc; run again to resume (an expired link gives 403/404)" >&2
  fi
done < "$urls"

echo "done: $n links, $failed failed. Log: $log"
[ $failed -eq 0 ]
