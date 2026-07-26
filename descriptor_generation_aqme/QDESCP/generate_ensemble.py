#!/usr/bin/env python3
"""Combine QDESCP conformer XYZ files into multi-XYZ ensemble files."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
CONF_PATTERN = re.compile(r"^(?P<base>.+_rdkit)_conf_(?P<number>\d+)\.xyz$")


def normalize_name(value: str) -> str:
    """Return an AQME molecule base name such as A1_rdkit."""
    name = Path(value).name
    for suffix in ("_ensemble.xyz", ".xyz"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    if "_conf_" in name:
        name = name.split("_conf_", 1)[0]
    if not name.endswith("_rdkit"):
        name += "_rdkit"
    return name


def find_conformers(base_name: str) -> list[tuple[int, Path]]:
    """Find conformers in either the QDESCP root or conformer subdirectories."""
    found: dict[int, Path] = {}
    for path in HERE.rglob(f"{base_name}_conf_*.xyz"):
        match = CONF_PATTERN.fullmatch(path.name)
        if not match or match.group("base") != base_name:
            continue
        number = int(match.group("number"))
        if number in found:
            raise ValueError(
                f"Duplicate conformer {number}: {found[number]} and {path}"
            )
        found[number] = path
    return sorted(found.items())


def read_xyz_block(path: Path) -> str:
    """Validate and return one XYZ block without changing its metadata."""
    text = path.read_text().rstrip()
    lines = text.splitlines()
    try:
        atom_count = int(lines[0].strip())
    except (IndexError, ValueError) as error:
        raise ValueError(f"{path}: invalid XYZ atom count") from error

    expected_lines = atom_count + 2
    if len(lines) != expected_lines:
        raise ValueError(
            f"{path}: expected {expected_lines} lines, found {len(lines)}"
        )
    return text + "\n"


def create_ensemble(base_name: str, output: Path | None = None) -> tuple[Path, int]:
    conformers = find_conformers(base_name)
    if not conformers:
        raise FileNotFoundError(f"No {base_name}_conf_*.xyz files found in {HERE}")

    output_path = output or HERE / f"{base_name}_ensemble.xyz"
    output_path.write_text("".join(read_xyz_block(path) for _, path in conformers))
    return output_path, len(conformers)


def natural_key(name: str) -> list[int | str]:
    """Sort A2 before A11."""
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]


def available_molecules() -> list[str]:
    names = {
        match.group("base")
        for path in HERE.rglob("*_rdkit_conf_*.xyz")
        if (match := CONF_PATTERN.fullmatch(path.name))
    }
    return sorted(names, key=natural_key)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine QDESCP conformers into one multi-XYZ ensemble."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("molecule", nargs="?", help="Molecule name, e.g. A1 or A1_rdkit")
    group.add_argument("--all", action="store_true", help="Build every molecule's ensemble")
    parser.add_argument("-o", "--output", type=Path, help="Output path (one molecule only)")
    args = parser.parse_args()
    if args.all and args.output:
        parser.error("--output can only be used with one molecule")
    return args


def main() -> None:
    args = parse_args()
    names = available_molecules() if args.all else [normalize_name(args.molecule)]
    if not names:
        raise SystemExit(f"No conformer XYZ files found in {HERE}")

    try:
        for name in names:
            output, count = create_ensemble(name, args.output)
            print(f"Created {output} with {count} conformers")
    except (OSError, ValueError) as error:
        raise SystemExit(f"Error: {error}") from error


if __name__ == "__main__":
    main()
