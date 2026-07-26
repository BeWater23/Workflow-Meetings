# Workflow Meetings

Hands-on materials for introducing command-line chemistry workflows, AQME
descriptor generation, RDKit and CREST conformer searches, Jupyter notebooks, and
ROBERT modeling.

## Start here

The main workshop is in [`descriptor_generation`](descriptor_generation/).

- Complete beginners: begin with
  [`START_HERE.md`](descriptor_generation/START_HERE.md).
- Command-line reference: use the
  [workshop README](descriptor_generation/README.md).
- Interactive version: open
  [`AQME_descriptor_and_conformer_workshop.ipynb`](descriptor_generation/AQME_descriptor_and_conformer_workshop.ipynb).

## Repository contents

| Path | Contents |
| --- | --- |
| `descriptor_generation/` | Beginner-oriented AQME, RDKit, and CREST workshop |
| `descriptor_generation_aqme/` | Imines SMILES inputs and ensemble helper scripts |
| `modeling_robert/` | Raw modeling inputs and DFT descriptor datasets |
| `solubility_prediction/` | Solubility source data for AQME/ROBERT practice |
| `environment-aqme.yml` | AQME, xTB, CREST, RDKit, and Jupyter environment |
| `environment-robert.yml` | Separate ROBERT modeling environment |

Generated conformers, descriptor tables, calculation logs, plots, reports, and
model folders are intentionally excluded through `.gitignore`. Participants create
these outputs themselves by running the workshop.

## Install the AQME workshop environment

AQME, xTB, and CREST are supported on macOS and Linux. Create the environment:

```bash
conda env create -f environment-aqme.yml
conda activate aqme
```

Verify it:

```bash
python -m aqme
xtb --version
crest --version
```

Then enter the workshop:

```bash
cd descriptor_generation
python scripts/smiles_to_xyz.py
bash scripts/run_aqme_descriptors.sh
```

The environment follows the versions used to validate the workshop: AQME 2.0.1,
xTB 6.7.1, CREST 2.12, and Python 3.12. The `libgfortran` pin follows the
[AQME installation guidance](https://aqme.readthedocs.io/en/latest/Quickstart/setup.html).

## Install the optional ROBERT environment

```bash
conda env create -f environment-robert.yml
conda activate robert
python -m robert --help
```

ROBERT calculations write `CURATE`, `GENERATE`, `VERIFY`, and `PREDICT` result
folders. These are deliberately ignored by Git.

## Optional molecular visualization

If Avogadro 2 is installed in `/Applications` on macOS, these lines may be added to
`.zshrc`:

```bash
export PATH="$PATH:/Applications/Avogadro2.app/Contents/MacOS"
alias avogadro="Avogadro2"
```

After reopening Terminal, an XYZ or SDF file can be opened with:

```bash
avogadro FILENAME.xyz
```

## Output policy

Only source inputs, instructions, notebooks, and scripts are version-controlled.
Calculation results remain on the participant's computer. To see why a generated
file is ignored, run:

```bash
git check-ignore -v PATH_TO_FILE
```
