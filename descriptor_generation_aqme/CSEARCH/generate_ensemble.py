#!/usr/bin/env python3
"""Create multi-XYZ conformer ensembles from AQME CSEARCH output."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent


def normalize_name(value: str) -> str:
    """Return the AQME base name (for example, A1_rdkit)."""
    name = Path(value).name
    for suffix in ("_ensemble.xyz", ".sdf", ".xyz"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    if "_conf_" in name:
        name = name.split("_conf_", 1)[0]
    if not name.endswith("_rdkit"):
        name += "_rdkit"
    return name


def xyz_blocks_from_sdf(path: Path) -> list[str]:
    """Convert the V2000 structures in an SDF file to XYZ blocks."""
    records = [record for record in path.read_text().split("$$$$") if record.strip()]
    blocks: list[str] = []

    for conformer_number, record in enumerate(records, start=1):
        lines = record.lstrip("\r\n").splitlines()
        if len(lines) < 4 or "V2000" not in lines[3]:
            raise ValueError(
                f"{path.name}, conformer {conformer_number}: expected V2000 SDF"
            )

        try:
            atom_count = int(lines[3][:3])
        except ValueError as error:
            raise ValueError(
                f"{path.name}, conformer {conformer_number}: invalid atom count"
            ) from error

        atom_lines = lines[4 : 4 + atom_count]
        if len(atom_lines) != atom_count:
            raise ValueError(
                f"{path.name}, conformer {conformer_number}: incomplete atom block"
            )

        atoms: list[str] = []
        for line in atom_lines:
            try:
                x = float(line[0:10])
                y = float(line[10:20])
                z = float(line[20:30])
                element = line[31:34].strip()
            except ValueError as error:
                raise ValueError(
                    f"{path.name}, conformer {conformer_number}: invalid coordinates"
                ) from error
            if not element:
                raise ValueError(
                    f"{path.name}, conformer {conformer_number}: missing element"
                )
            atoms.append(f"{element:<2} {x:14.8f} {y:14.8f} {z:14.8f}")

        comment = f"{path.stem} conformer {conformer_number}"
        blocks.append(f"{atom_count}\n{comment}\n" + "\n".join(atoms) + "\n")

    if not blocks:
        raise ValueError(f"{path.name}: no structures found")
    return blocks


def xyz_blocks_from_files(base_name: str) -> list[str]:
    """Read individual XYZ files if no matching SDF file exists."""
    pattern = re.compile(rf"^{re.escape(base_name)}_conf_(\d+)\.xyz$")
    matches: list[tuple[int, Path]] = []
    for path in HERE.glob(f"{base_name}_conf_*.xyz"):
        match = pattern.match(path.name)
        if match:
            matches.append((int(match.group(1)), path))

    blocks: list[str] = []
    for _, path in sorted(matches):
        text = path.read_text().strip()
        lines = text.splitlines()
        try:
            atom_count = int(lines[0])
        except (IndexError, ValueError) as error:
            raise ValueError(f"{path.name}: invalid XYZ atom count") from error
        if len(lines) != atom_count + 2:
            raise ValueError(
                f"{path.name}: expected {atom_count + 2} lines, found {len(lines)}"
            )
        blocks.append(text + "\n")
    return blocks


def create_ensemble(base_name: str, output: Path | None = None) -> tuple[Path, int]:
    sdf_path = HERE / f"{base_name}.sdf"
    if sdf_path.exists():
        # The SDF is authoritative: later AQME steps can move individual XYZ files.
        blocks = xyz_blocks_from_sdf(sdf_path)
    else:
        blocks = xyz_blocks_from_files(base_name)

    if not blocks:
        raise FileNotFoundError(
            f"No {base_name}.sdf or {base_name}_conf_*.xyz files found in {HERE}"
        )

    output_path = output or HERE / f"{base_name}_ensemble.xyz"
    output_path.write_text("".join(blocks))
    return output_path, len(blocks)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine all conformers of an AQME molecule into one multi-XYZ file."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("molecule", nargs="?", help="Molecule name, e.g. A1 or A1_rdkit")
    group.add_argument("--all", action="store_true", help="Build ensembles for every SDF")
    parser.add_argument("-o", "--output", type=Path, help="Output path (single molecule only)")
    args = parser.parse_args()
    if args.all and args.output:
        parser.error("--output can only be used with one molecule")
    return args


def main() -> None:
    args = parse_args()
    if args.all:
        names = sorted(path.stem for path in HERE.glob("*_rdkit.sdf"))
        if not names:
            raise SystemExit(f"No *_rdkit.sdf files found in {HERE}")
    else:
        names = [normalize_name(args.molecule)]

    try:
        for name in names:
            output, count = create_ensemble(name, args.output)
            print(f"Created {output} with {count} conformers")
    except (OSError, ValueError) as error:
        raise SystemExit(f"Error: {error}") from error


if __name__ == "__main__":
    main()
