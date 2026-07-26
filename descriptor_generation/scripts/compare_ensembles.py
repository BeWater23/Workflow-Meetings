#!/usr/bin/env python3
"""Compare relative-energy coverage of the RDKit and CREST ensembles."""

from __future__ import annotations

import argparse
import csv
import statistics
from pathlib import Path


WORKSHOP_DIR = Path(__file__).resolve().parents[1]
HARTREE_TO_KCAL_MOL = 627.509474


def read_rdkit(path: Path) -> list[float]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [float(row["relative_energy_kcal_mol"]) for row in csv.DictReader(handle)]


def read_crest_xyz(path: Path) -> list[float]:
    """Read the total energy in each CREST XYZ comment line (Hartree)."""
    lines = path.read_text(encoding="utf-8").splitlines()
    energies: list[float] = []
    index = 0
    while index < len(lines):
        if not lines[index].strip():
            index += 1
            continue
        try:
            atom_count = int(lines[index].strip())
        except ValueError as exc:
            raise ValueError(f"Expected an atom count on line {index + 1} of {path}") from exc
        if index + 1 >= len(lines):
            raise ValueError(f"Missing XYZ comment line after line {index + 1} of {path}")
        try:
            energies.append(float(lines[index + 1].split()[0]))
        except (IndexError, ValueError) as exc:
            raise ValueError(
                f"Could not read a CREST energy on line {index + 2} of {path}"
            ) from exc
        index += atom_count + 2
    if not energies:
        raise ValueError(f"No structures found in {path}")
    minimum = min(energies)
    return [(energy - minimum) * HARTREE_TO_KCAL_MOL for energy in energies]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rdkit",
        type=Path,
        default=WORKSHOP_DIR / "outputs" / "03_rdkit_search" / "rdkit_summary.csv",
    )
    parser.add_argument(
        "--crest",
        type=Path,
        default=WORKSHOP_DIR / "outputs" / "04_crest_quick" / "crest_conformers.xyz",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=WORKSHOP_DIR / "outputs" / "05_comparison" / "relative_energies.csv",
    )
    args = parser.parse_args()

    ensembles = {
        "RDKit_ETKDGv3_MMFF": read_rdkit(args.rdkit),
        "CREST_GFN2-xTB": read_crest_xyz(args.crest),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["method", "conformer", "relative_energy_kcal_mol"],
        )
        writer.writeheader()
        for method, energies in ensembles.items():
            for conformer, energy in enumerate(sorted(energies), start=1):
                writer.writerow(
                    {
                        "method": method,
                        "conformer": conformer,
                        "relative_energy_kcal_mol": f"{energy:.6f}",
                    }
                )

    print("method                     n_confs   median ΔE   max ΔE (kcal/mol)")
    print("-------------------------  -------   ---------   -----------------")
    for method, energies in ensembles.items():
        print(
            f"{method:25}  {len(energies):7d}   "
            f"{statistics.median(energies):9.3f}   {max(energies):17.3f}"
        )
    print(f"\nWrote {args.output}")
    print(
        "Compare relative-energy coverage only: RDKit/MMFF and CREST/GFN2-xTB "
        "absolute energies are not on the same scale."
    )


if __name__ == "__main__":
    main()

