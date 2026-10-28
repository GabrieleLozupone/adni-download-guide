#!/usr/bin/env bash
# Convert unpacked IDA images to compressed NIfTI, one file per Image ID: <out>/<Subject ID>/I<Image ID>.nii.gz
# DICOM folders go through dcm2niix (https://github.com/rordenlab/dcm2niix); folders that already contain NIfTI are
# compressed/copied. Existing outputs are skipped, so the command can be run again.
#
#   bash scripts/convert_to_nifti.sh /path/to/ADNI_raw/ADNI /path/to/ADNI_nifti
set -uo pipefail

if [ $# -ne 2 ]; then
  echo "usage: $0 unpacked_ADNI_folder output_folder" >&2
  exit 2
fi
root="$1"; out="$2"
command -v dcm2niix >/dev/null || { echo "dcm2niix not found: install it first" >&2; exit 1; }
mkdir -p "$out"
errlog="$out/conversion_errors.txt"

ok=0; skipped=0; failed=0
while IFS= read -r dir; do
  id=$(basename "$dir")
  subject=$(basename "$(dirname "$(dirname "$(dirname "$dir")")")")
  dest="$out/$subject"
  if ls "$dest/$id".nii.gz "$dest/$id"_*.nii.gz >/dev/null 2>&1; then
    skipped=$((skipped + 1)); continue
  fi
  mkdir -p "$dest"
  nii=$(find "$dir" -maxdepth 1 -type f \( -name "*.nii" -o -name "*.nii.gz" \) | head -1)
  if [ -n "$nii" ]; then
    case "$nii" in
      *.gz) cp "$nii" "$dest/$id.nii.gz" ;;
      *) gzip -c "$nii" > "$dest/$id.nii.gz" ;;
    esac
    rc=$?
  else
    dcm2niix -z y -b y -f "$id" -o "$dest" "$dir" >/dev/null 2>>"$errlog"
    rc=$?
  fi
  if [ $rc -eq 0 ]; then ok=$((ok + 1)); else failed=$((failed + 1)); echo "$dir" >> "$errlog"; fi
done < <(find "$root" -type d -regex '.*/[ID][0-9][0-9]*' | sort)

echo "converted $ok, skipped (already done) $skipped, failed $failed"
[ $failed -eq 0 ] || echo "see $errlog"
