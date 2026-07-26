#!/usr/bin/env bash
set -euo pipefail

workshop_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
input_csv="${workshop_dir}/inputs/A1.csv"
output_dir="${workshop_dir}/outputs/05_aqme_descriptors"

if ! python -c "import aqme" >/dev/null 2>&1; then
  echo "AQME is not available in this Python." >&2
  echo "Run 'conda activate aqme' and try again." >&2
  exit 1
fi

mkdir -p "${output_dir}"
cd "${output_dir}"

echo "Input:  ${input_csv}"
echo "Output: ${output_dir}"
echo "Mapped atoms requested: 1, 2, 3"

python -m aqme \
  --qdescp \
  --input "${input_csv}" \
  --qdescp_atoms "['1','2','3']" \
  --destination "${output_dir}" \
  --nprocs 4

echo "Descriptor workflow complete."
