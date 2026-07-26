#!/usr/bin/env bash
set -euo pipefail

workshop_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mode="${1:-quick}"
threads="${2:-4}"
output_dir="${3:-${workshop_dir}/outputs/03_crest_${mode}}"
input_xyz="${workshop_dir}/outputs/01_smiles_to_xyz/A1.xyz"

if [[ "${mode}" != "quick" && "${mode}" != "full" ]]; then
  echo "Usage: bash scripts/run_crest.sh [quick|full] [threads] [output_dir]" >&2
  exit 2
fi

if ! command -v crest >/dev/null 2>&1; then
  echo "crest is not on PATH. Activate the aqme Conda environment first." >&2
  exit 1
fi

if [[ ! -f "${input_xyz}" ]]; then
  echo "Missing ${input_xyz}" >&2
  echo "Run: python scripts/smiles_to_xyz.py" >&2
  exit 1
fi

if [[ -e "${output_dir}/crest_conformers.xyz" ]]; then
  echo "A completed ensemble already exists in ${output_dir}" >&2
  echo "Pass a different output directory as the third argument to keep runs separate." >&2
  exit 1
fi

mkdir -p "${output_dir}"
cp "${input_xyz}" "${output_dir}/A1.xyz"
cd "${output_dir}"

crest_args=(A1.xyz --chrg -1 --uhf 0 --gfn2 --T "${threads}")
if [[ "${mode}" == "quick" ]]; then
  crest_args+=(--quick)
fi

echo "Running CREST in ${output_dir}"
echo "Command: crest ${crest_args[*]}"
crest "${crest_args[@]}" 2>&1 | tee crest.log

if [[ ! -s crest_conformers.xyz ]]; then
  echo "CREST finished without producing crest_conformers.xyz; inspect crest.log" >&2
  exit 1
fi

echo "CREST ensemble: ${output_dir}/crest_conformers.xyz"
