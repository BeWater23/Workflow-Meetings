# Start here: your first command-line chemistry workflow

This guide assumes you have never used a terminal or written Python. Run one
command at a time and discuss its output before continuing.

## 1. Meet the tools

- **Terminal:** a window where you give the computer text instructions.
- **Command:** one instruction entered in the terminal.
- **Folder or directory:** a location containing files.
- **Path:** the address of a file or folder.
- **Python:** the language used by the workshop scripts, RDKit, and AQME.
- **Conda environment:** an isolated collection of programs and packages.
- **Script:** a saved sequence of instructions.
- **Notebook:** explanations, Python code, and results in one document.

Type only the text inside each gray box and press Return.

## 2. Find the workshop in the terminal

Open Terminal and ask which folder you are in:

```bash
pwd
```

Move into the repository, replacing the example path if you saved it elsewhere:

```bash
cd "/Users/luccapfitzer/Workflow-Meetings/descriptor_generation"
```

List the files:

```bash
ls
```

You should see `README.md`, `START_HERE.md`, `inputs`, and `scripts`.

Useful keys:

- Tab completes a file or folder name.
- Up arrow recalls the previous command.
- Control-C stops a running command.
- Capital letters matter in file names.

## 3. Activate the chemistry environment

```bash
conda activate aqme
```

Check which Python will run, then ask it to print a message:

```bash
which python
python --version
python -c "print('Hello from Python')"
```

## 4. Inspect the molecular input

```bash
ls inputs
head -n 2 inputs/A1.csv
```

The first line gives the column names. The second contains a SMILES string and
the short name `A1`. A SMILES describes atoms, bonds, charge, and stereochemistry
without storing 3D coordinates.

## 5. Convert SMILES to one 3D structure

```bash
python scripts/smiles_to_xyz.py
```

Inspect the new XYZ file:

```bash
head -n 8 outputs/01_smiles_to_xyz/A1.xyz
```

An XYZ stores an element and three coordinates on each atom line. It does not
store bonds, bond orders, charge, or the atom labels from the original SMILES.

## 6. Search conformers with RDKit

```bash
python scripts/rdkit_conformer_search.py
```

Inspect the energy ranking:

```bash
column -s, -t < outputs/02_rdkit_search/rdkit_summary.csv
```

The lowest relative energy is zero. Other rows are alternative 3D conformations.

## 7. Search conformers with CREST

Run this slower step only when the facilitator asks:

```bash
bash scripts/run_crest.sh quick 4
```

A long text log is normal. A successful run ends with `CREST terminated normally`
and creates `outputs/03_crest_quick/crest_conformers.xyz`.

## 8. Compare the searches

```bash
python scripts/compare_ensembles.py
```

RDKit and CREST search and rank structures differently. Their absolute energy
values should not be compared directly.

## 9. Let AQME automate the workflow

```bash
bash scripts/run_aqme_descriptors.sh
```

The earlier steps exposed some of the choices behind descriptor generation. AQME
now combines conformer generation, xTB calculations, descriptor collection, and
Boltzmann averaging in a reproducible workflow.

List the generated descriptor files:

```bash
ls outputs/05_aqme_descriptors
```

## 10. Try the Jupyter version

```bash
jupyter lab AQME_descriptor_and_conformer_workshop.ipynb
```

Select the `aqme` kernel. Run one cell with Shift-Return and work from top to
bottom. The notebook uses the same concepts while showing the Python code beside
its output.

## If something goes wrong

Read the final line of the error, then check:

```bash
pwd
conda activate aqme
ls
```

- `No such file or directory`: check the current folder and spelling.
- `command not found`: activate the environment or install the missing program.
- `ModuleNotFoundError`: the selected Python environment is missing a package.
- A Python `Traceback`: the last line usually contains the useful message.

The generated files are under `outputs/` and can be reproduced from the input.
