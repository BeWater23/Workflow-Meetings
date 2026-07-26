#!/usr/bin/env python3
"""Attach SMILES topology to a CREST multi-XYZ ensemble and write an AQME-ready SDF."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from rdkit import Chem
from rdkit.Geometry import Point3D


WORKSHOP_DIR = Path(__file__).resolve().parents[1]
HARTREE_TO_KCAL_MOL = 627.509474


def read_named_smiles(csv_path: Path, name: str) -> str:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row["code_name"] == name:
                return row["SMILES"]
    raise ValueError(f"No molecule named {name!r} in {csv_path}")


def read_xyz_ensemble(path: Path) -> list[tuple[str, list[str], list[Point3D]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    frames: list[tuple[str, list[str], list[Point3D]]] = []
    index = 0
    while index < len(lines):
        if not lines[index].strip():
            index += 1
            continue
        try:
            atom_count = int(lines[index].strip())
        except ValueError as exc:
            raise ValueError(f"Expected atom count on line {index + 1} of {path}") from exc
        if index + atom_count + 1 >= len(lines):
            raise ValueError(f"Incomplete XYZ frame beginning on line {index + 1}")
        comment = lines[index + 1].strip()
        symbols: list[str] = []
        coordinates: list[Point3D] = []
        for atom_line in lines[index + 2 : index + 2 + atom_count]:
            fields = atom_line.split()
            if len(fields) < 4:
                raise ValueError(f"Invalid XYZ atom line: {atom_line}")
            symbols.append(fields[0])
            coordinates.append(Point3D(float(fields[1]), float(fields[2]), float(fields[3])))
        frames.append((comment, symbols, coordinates))
        index += atom_count + 2
    if not frames:
        raise ValueError(f"No XYZ frames found in {path}")
    return frames


def crest_energy(comment: str) -> float | None:
    try:
        return float(comment.split()[0])
    except (IndexError, ValueError):
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--xyz",
        type=Path,
        default=WORKSHOP_DIR / "outputs" / "03_crest_quick" / "crest_conformers.xyz",
    )
    parser.add_argument(
        "--input", type=Path, default=WORKSHOP_DIR / "inputs" / "A1.csv"
    )
    parser.add_argument("--name", default="A1")
    parser.add_argument("--mult", type=int, default=1)
    parser.add_argument(
        "--output",
        type=Path,
        default=WORKSHOP_DIR / "outputs" / "03_crest_quick" / "A1_crest.sdf",
    )
    args = parser.parse_args()

    smiles = read_named_smiles(args.input, args.name)
    template = Chem.MolFromSmiles(smiles)
    if template is None:
        raise ValueError(f"RDKit could not parse this SMILES: {smiles}")
    formal_charge = Chem.GetFormalCharge(template)
    canonical_smiles = Chem.MolToSmiles(template)
    template = Chem.AddHs(template)
    expected_symbols = [atom.GetSymbol() for atom in template.GetAtoms()]

    frames = read_xyz_ensemble(args.xyz)
    energies = [crest_energy(comment) for comment, _, _ in frames]
    numeric_energies = [energy for energy in energies if energy is not None]
    minimum_energy = min(numeric_energies) if numeric_energies else None

    args.output.parent.mkdir(parents=True, exist_ok=True)
    writer = Chem.SDWriter(str(args.output))
    try:
        for rank, ((comment, symbols, coordinates), energy) in enumerate(
            zip(frames, energies, strict=True), start=1
        ):
            if symbols != expected_symbols:
                raise ValueError(
                    f"Atom order in CREST frame {rank} does not match the mapped SMILES. "
                    "Use the XYZ generated from this workshop as the CREST starting structure."
                )
            record = Chem.Mol(template)
            record.RemoveAllConformers()
            conformer = Chem.Conformer(record.GetNumAtoms())
            for atom_index, point in enumerate(coordinates):
                conformer.SetAtomPosition(atom_index, point)
            record.AddConformer(conformer, assignId=True)
            record.SetProp("_Name", f"{args.name}_crest_conf_{rank}")
            record.SetProp("SMILES_INPUT", smiles)
            record.SetProp("SMILES", canonical_smiles)
            record.SetIntProp("Real charge", formal_charge)
            record.SetIntProp("Mult", args.mult)
            record.SetProp("crest_xyz_comment", comment)
            if energy is not None:
                record.SetDoubleProp("crest_energy_hartree", energy)
                if minimum_energy is not None:
                    record.SetDoubleProp(
                        "relative_crest_energy_kcal_mol",
                        (energy - minimum_energy) * HARTREE_TO_KCAL_MOL,
                    )
            writer.write(record)
    finally:
        writer.close()

    print(f"Read {len(frames)} CREST conformers from {args.xyz}")
    print(f"Attached mapped topology and charge {formal_charge} from {args.input}")
    print(f"Wrote AQME-ready ensemble: {args.output}")


if __name__ == "__main__":
    main()
