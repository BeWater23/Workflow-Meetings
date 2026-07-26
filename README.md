# Computational chemistry workflow workshop

This repository contains a guided workshop that connects molecular structure
preparation, conformer searching, descriptor calculation, and machine-learning
modeling.

## Learning path

1. **Descriptor generation:** start from a mapped SMILES, create 3D structures,
   compare RDKit and CREST conformer searches, and calculate AQME descriptors
   for an existing ensemble.
2. **Modeling with ROBERT:** identify the target and descriptor columns, run the
   modeling workflow, and interpret its report.
3. **Scaling up:** prepare a larger solubility dataset and run the combined
   AQME–ROBERT workflow.

## Workshop sections

| Section | Material | Environment |
| --- | --- | --- |
| Descriptor generation | [`descriptor_generation/`](descriptor_generation/) | `aqme` |
| ROBERT modeling | [`modeling_robert/`](modeling_robert/) | `robert` |
| Solubility example | [`solubility_prediction/`](solubility_prediction/) | `robert` with AQME dependencies |

Begin with the
[`descriptor-generation student guide`](descriptor_generation/START_HERE.md).
The first part uses a Jupyter notebook; the second part repeats the same workflow
from the command line.

## Software setup

Create the environments by following the official installation instructions:

- [AQME installation](https://aqme.readthedocs.io/en/latest/Quickstart/setup.html)
- [ROBERT installation](https://robert.readthedocs.io/en/latest/Install/installation.html)

The `aqme` environment used in the first section must provide AQME, RDKit, Open
Babel, xTB, CREST, JupyterLab, and an `aqme` Jupyter kernel. Verify it with:

```bash
conda activate aqme
python -m aqme --help
python -c "import rdkit"
xtb --version
crest --version
jupyter lab --version
```

If JupyterLab or the kernel is missing:

```bash
conda install -n aqme -c conda-forge jupyterlab ipykernel
conda activate aqme
python -m ipykernel install --user --name aqme --display-name "Python (aqme)"
```

Verify the modeling environment separately:

```bash
conda activate robert
python -m robert --help
```

## Molecular visualization with Avogadro

On macOS, install Avogadro 2 in `/Applications`. To make it available as a
terminal command, open the Z shell configuration file:

```bash
nano ~/.zshrc
```

Add these lines:

```bash
export PATH="$PATH:/Applications/Avogadro2.app/Contents/MacOS"
alias avogadro="Avogadro2"
```

In Nano, press Control-O and Return to save, then Control-X to close the editor.
Reload the configuration:

```bash
source ~/.zshrc
```

Confirm that the command is available:

```bash
command -v avogadro
```

After generating structures in the descriptor workshop, open an XYZ or SDF from
the repository root with:

```bash
avogadro descriptor_generation/outputs/01_smiles_to_xyz/A1.xyz
avogadro descriptor_generation/outputs/02_rdkit_search/A1_rdkit.sdf
```

XYZ files contain elements and coordinates. Use the SDF when atom connectivity
and bond orders are important.

## Run the ROBERT example

The smallest modeling example contains molecular identifiers, the response
variable `ddG`, and a prepared descriptor table. From the repository root:

```bash
conda activate robert
cd modeling_robert/dft_descriptors/ka2
python -m robert --names name --y ddG --csv_name ka2.csv
```

ROBERT writes the `CURATE`, `GENERATE`, `VERIFY`, and `PREDICT` stages and
assembles `ROBERT_report.pdf`. Return to the repository root before continuing:

```bash
cd ../../..
```

The complete exercise and the related `ka4` and `ka6` datasets are described in
the [`ROBERT modeling guide`](modeling_robert/README.md).

## Generated files

Each exercise writes results into its own output directory. Generated
conformers, logs, descriptor tables, plots, models, and reports are excluded from
version control and can be reproduced from the provided inputs and commands.
