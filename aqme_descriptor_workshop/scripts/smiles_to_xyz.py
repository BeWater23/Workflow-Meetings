#!/usr/bin/env python3
"""Build one optimized 3D XYZ structure from a SMILES string with RDKit."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem


WORKSHOP_DIR = Path(__file__).resolve().parents[1]


def read_named_smiles(csv_path: Path, name: str) -> str:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row["code_name"] == name:
                return row["SMILES"]
    raise ValueError(f"No molecule named {name!r} in {csv_path}")


def xyz_block(mol: Chem.Mol, conf_id: int, comment: str) -> str:
    lines = Chem.MolToXYZBlock(mol, confId=conf_id).splitlines()
    lines[1] = comment
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=WORKSHOP_DIR / "inputs" / "A1.csv",
        help="CSV with SMILES and code_name columns",
    )
    parser.add_argument("--name", default="A1", help="code_name to select")
    parser.add_argument(
        "--output",
        type=Path,
        default=WORKSHOP_DIR / "outputs" / "02_smiles_to_xyz" / "A1.xyz",
    )
    parser.add_argument("--seed", type=int, default=20260726)
    args = parser.parse_args()

    smiles = read_named_smiles(args.input, args.name)
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit could not parse this SMILES: {smiles}")

    formal_charge = Chem.GetFormalCharge(mol)
    mapped_atoms = {
        atom.GetAtomMapNum(): atom.GetSymbol()
        for atom in mol.GetAtoms()
        if atom.GetAtomMapNum()
    }

    # XYZ coordinates must include explicit hydrogens.
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = args.seed
    params.enforceChirality = True
    status = AllChem.EmbedMolecule(mol, params)
    if status != 0:
        raise RuntimeError("RDKit ETKDGv3 embedding failed")

    if AllChem.MMFFHasAllMoleculeParams(mol):
        force_field = "MMFF94"
        not_converged = AllChem.MMFFOptimizeMolecule(mol, maxIters=1000)
    else:
        force_field = "UFF"
        not_converged = AllChem.UFFOptimizeMolecule(mol, maxIters=1000)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    comment = (
        f"{args.name}; RDKit ETKDGv3/{force_field}; charge={formal_charge}; "
        "multiplicity=1; atom_maps="
        + ",".join(f"{number}:{symbol}" for number, symbol in sorted(mapped_atoms.items()))
    )
    args.output.write_text(xyz_block(mol, 0, comment), encoding="utf-8")

    convergence = "converged" if not_converged == 0 else "reached the iteration limit"
    print(f"SMILES: {smiles}")
    print(f"Formal charge detected by RDKit: {formal_charge}")
    print(f"Mapped atoms: {mapped_atoms}")
    print(f"Optimization: {force_field}, {convergence}")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

