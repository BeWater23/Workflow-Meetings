#!/usr/bin/env bash
set -euo pipefail

workshop_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ensemble_sdf="${workshop_dir}/outputs/02_rdkit_search/A1_rdkit.sdf"
output_dir="${workshop_dir}/outputs/05_aqme_descriptors"

if ! python -c "import aqme" >/dev/null 2>&1; then
  echo "AQME is not available in this Python." >&2
  echo "Run 'conda activate aqme' and try again." >&2
  exit 1
fi

if [[ ! -f "${ensemble_sdf}" ]]; then
  echo "Missing manual conformer ensemble: ${ensemble_sdf}" >&2
  echo "Run 'python scripts/rdkit_conformer_search.py' first." >&2
  exit 1
fi

mkdir -p "${output_dir}"
cd "${output_dir}"

echo "Ensemble: ${ensemble_sdf}"
echo "Output: ${output_dir}"
echo "Mapped atoms requested: 1, 2, 3"

python -m aqme \
  --qdescp \
  --files "../02_rdkit_search/A1_rdkit.sdf" \
  --csv_name "../../inputs/A1.csv" \
  --charge -1 \
  --mult 1 \
  --qdescp_atoms "['1','2','3']" \
  --destination "." \
  --nprocs 4

echo "Descriptor workflow complete; the supplied ensemble was reused without CSEARCH."
