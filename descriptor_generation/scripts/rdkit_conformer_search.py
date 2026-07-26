#!/usr/bin/env python3
"""Generate, optimize, energy-rank, and RMSD-prune an RDKit conformer ensemble."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from rdkit import Chem
from rdkit.Chem import AllChem, rdMolAlign


WORKSHOP_DIR = Path(__file__).resolve().parents[1]


def read_named_smiles(csv_path: Path, name: str) -> str:
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row["code_name"] == name:
                return row["SMILES"]
    raise ValueError(f"No molecule named {name!r} in {csv_path}")


def optimize_conformers(mol: Chem.Mol, conf_ids: list[int]) -> tuple[str, dict[int, tuple[int, float]]]:
    if AllChem.MMFFHasAllMoleculeParams(mol):
        method = "MMFF94"
        results = AllChem.MMFFOptimizeMoleculeConfs(
            mol, numThreads=0, maxIters=1000, mmffVariant=method
        )
    else:
        method = "UFF"
        results = AllChem.UFFOptimizeMoleculeConfs(mol, numThreads=0, maxIters=1000)
    return method, dict(zip(conf_ids, results, strict=True))


def prune_by_heavy_atom_rmsd(
    mol: Chem.Mol,
    ranked_conf_ids: list[int],
    threshold: float,
    max_keep: int,
) -> list[int]:
    """Greedily retain low-energy conformers separated by at least threshold Å."""
    heavy_mol = Chem.RemoveHs(mol)
    kept: list[int] = []
    for conf_id in ranked_conf_ids:
        if all(
            rdMolAlign.GetBestRMS(heavy_mol, heavy_mol, prbId=conf_id, refId=other_id)
            >= threshold
            for other_id in kept
        ):
            kept.append(conf_id)
            if len(kept) == max_keep:
                break
    return kept


def one_conformer_record(mol: Chem.Mol, conf_id: int) -> Chem.Mol:
    record = Chem.Mol(mol)
    record.RemoveAllConformers()
    record.AddConformer(mol.GetConformer(conf_id), assignId=True)
    return record


def xyz_block(mol: Chem.Mol, comment: str) -> str:
    lines = Chem.MolToXYZBlock(mol).splitlines()
    lines[1] = comment
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=WORKSHOP_DIR / "inputs" / "A1.csv"
    )
    parser.add_argument("--name", default="A1")
    parser.add_argument("--num-confs", type=int, default=100)
    parser.add_argument("--rmsd-threshold", type=float, default=0.50)
    parser.add_argument("--max-keep", type=int, default=20)
    parser.add_argument("--seed", type=int, default=20260726)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=WORKSHOP_DIR / "outputs" / "02_rdkit_search",
    )
    args = parser.parse_args()

    smiles = read_named_smiles(args.input, args.name)
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit could not parse this SMILES: {smiles}")
    formal_charge = Chem.GetFormalCharge(mol)
    canonical_smiles = Chem.MolToSmiles(mol)
    mol = Chem.AddHs(mol)

    params = AllChem.ETKDGv3()
    params.randomSeed = args.seed
    params.enforceChirality = True
    params.pruneRmsThresh = -1.0  # Perform a transparent, energy-ordered pruning below.
    params.numThreads = 0
    conf_ids = list(AllChem.EmbedMultipleConfs(mol, numConfs=args.num_confs, params=params))
    if not conf_ids:
        raise RuntimeError("RDKit did not generate any conformers")

    force_field, results = optimize_conformers(mol, conf_ids)
    ranked = sorted(conf_ids, key=lambda conf_id: results[conf_id][1])
    kept = prune_by_heavy_atom_rmsd(mol, ranked, args.rmsd_threshold, args.max_keep)
    minimum_energy = results[kept[0]][1]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    sdf_path = args.output_dir / f"{args.name}_rdkit.sdf"
    ensemble_path = args.output_dir / f"{args.name}_rdkit_ensemble.xyz"
    summary_path = args.output_dir / "rdkit_summary.csv"

    writer = Chem.SDWriter(str(sdf_path))
    ensemble_blocks: list[str] = []
    summary_rows: list[dict[str, object]] = []
    for rank, conf_id in enumerate(kept, start=1):
        not_converged, energy = results[conf_id]
        relative_energy = energy - minimum_energy
        record = one_conformer_record(mol, conf_id)
        record.SetProp("_Name", f"{args.name}_rdkit_conf_{rank}")
        record.SetProp("force_field", force_field)
        record.SetDoubleProp("energy_kcal_mol", energy)
        record.SetDoubleProp("relative_energy_kcal_mol", relative_energy)
        record.SetIntProp("formal_charge", formal_charge)
        record.SetIntProp("optimization_not_converged", not_converged)
        # QDESCP reads these fields when a pre-generated SDF ensemble is supplied.
        # Their presence lets AQME validate mapped atoms and skip CSEARCH entirely.
        record.SetProp("SMILES_INPUT", smiles)
        record.SetProp("SMILES", canonical_smiles)
        record.SetIntProp("Real charge", formal_charge)
        record.SetIntProp("Mult", 1)
        writer.write(record)

        comment = (
            f"{args.name}_rdkit_conf_{rank}; {force_field}; "
            f"energy_kcal_mol={energy:.6f}; relative_energy_kcal_mol={relative_energy:.6f}; "
            f"charge={formal_charge}"
        )
        block = xyz_block(record, comment)
        ensemble_blocks.append(block)
        (args.output_dir / f"{args.name}_rdkit_conf_{rank}.xyz").write_text(
            block, encoding="utf-8"
        )
        summary_rows.append(
            {
                "rank": rank,
                "original_conformer_id": conf_id,
                "force_field": force_field,
                "energy_kcal_mol": f"{energy:.8f}",
                "relative_energy_kcal_mol": f"{relative_energy:.8f}",
                "optimization_converged": not_converged == 0,
            }
        )
    writer.close()
    ensemble_path.write_text("".join(ensemble_blocks), encoding="utf-8")

    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = list(summary_rows[0])
        csv_writer = csv.DictWriter(handle, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(summary_rows)

    print(f"Parsed {args.name} with formal charge {formal_charge}")
    print(f"Embedded {len(conf_ids)} conformers with ETKDGv3")
    print(f"Optimized with {force_field}")
    print(
        f"Kept {len(kept)} conformers after {args.rmsd_threshold:.2f} Å "
        "heavy-atom RMSD pruning"
    )
    print(f"Wrote {sdf_path}")
    print(f"Wrote {ensemble_path}")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
