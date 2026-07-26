#!/usr/bin/env python3
"""Prepare the published solubility data for ROBERT's AQME workflow."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


HERE = Path(__file__).resolve().parent
DEFAULT_INPUT = HERE / "dataset.csv"
DEFAULT_OUTPUT = HERE / "outputs" / "solubility_robert.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--limit",
        type=int,
        help="write only the first N compounds for a shorter live demonstration",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.limit is not None and args.limit < 1:
        raise SystemExit("--limit must be a positive integer")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with args.input.open(newline="", encoding="utf-8-sig") as source, args.output.open(
        "w", newline="", encoding="utf-8"
    ) as destination:
        reader = csv.DictReader(source)
        required = {"Compound ID", "measured log(solubility:mol/L)", "SMILES"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"Missing required column(s): {', '.join(sorted(missing))}")

        writer = csv.DictWriter(
            destination, fieldnames=["code_name", "smiles", "solubility"]
        )
        writer.writeheader()

        for row in reader:
            if args.limit is not None and count >= args.limit:
                break
            writer.writerow(
                {
                    "code_name": row["Compound ID"],
                    "smiles": row["SMILES"],
                    "solubility": row["measured log(solubility:mol/L)"],
                }
            )
            count += 1

    print(f"Wrote {count} compounds to {args.output}")


if __name__ == "__main__":
    main()
