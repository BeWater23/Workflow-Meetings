# Start here: your first command line and chemistry workflow

This guide assumes you have never used a terminal, written Python, or run a
computational chemistry program. Nothing needs to be memorized. Copy each command,
run it, and discuss what happened before continuing.

## What are we using?

- **Terminal:** a window where we ask the computer to perform an action using text.
- **Command:** one instruction entered in the terminal.
- **Folder or directory:** a location containing files. The terms mean the same thing.
- **Path:** the address of a file or folder.
- **Python:** the language used by RDKit and AQME.
- **Conda environment:** an isolated collection of compatible programs and packages.
- **Script:** a saved sequence of Python or shell instructions.
- **Notebook:** a document in which explanations, Python cells, and results coexist.

In command examples, type only the text inside the gray code block. Press Return
after each command. Do not type several commands at once.

## Part 1: orient yourself in the terminal

Open the macOS Terminal application.

Ask “where am I?”:

```bash
pwd
```

`pwd` means **print working directory**. The output is your current location.

Move into the workshop folder:

```bash
cd "/Users/luccapfitzer/Workflow-Meetings/descriptor_generation"
```

`cd` means **change directory**. Quotation marks protect paths containing spaces.

Confirm your location:

```bash
pwd
```

List the files here:

```bash
ls
```

You should see `README.md`, `START_HERE.md`, `inputs`, and `scripts`, among other
files. If you do not, stop and check the `cd` command rather than continuing.

Useful habits:

- Press Tab while typing a filename to complete it.
- Press the Up arrow to recover the previous command.
- Press Control-C to stop a running command.
- Terminal commands are case-sensitive: `A1.csv` and `a1.csv` are different names.

## Part 2: activate the chemistry environment

Activate the prepared environment:

```bash
conda activate aqme
```

The word `(aqme)` should appear near the terminal prompt. Check which Python will
run:

```bash
which python
```

Check the Python version:

```bash
python --version
```

Ask Python to print a message:

```bash
python -c "print('Hello from Python')"
```

This command has three parts:

- `python` starts Python.
- `-c` says that Python code follows directly on the command line.
- `print('Hello from Python')` is the Python instruction.

## Part 3: inspect the input without changing it

See which input files are available:

```bash
ls inputs
```

Show the first two lines of the example:

```bash
head -n 2 inputs/A1.csv
```

The first line contains column names. The second line contains the SMILES and the
short molecule name `A1`.

For this SMILES:

- `[CH-:1]` gives the molecule a formal charge of −1.
- `:1`, `:2`, and `:3` label atoms for atomic descriptors.
- The `/` symbols specify alkene-like bond stereochemistry.

## Part 4: run your first saved Python script

Generate a three-dimensional XYZ structure:

```bash
python scripts/smiles_to_xyz.py
```

Read the message printed by the script. It should report charge `-1`, mapped atoms
1–3, a converged MMFF94 optimization, and an output path.

List the generated file:

```bash
ls outputs/02_smiles_to_xyz
```

Inspect its first eight lines:

```bash
head -n 8 outputs/02_smiles_to_xyz/A1.xyz
```

An XYZ begins with the atom count, followed by a comment, then one element and
three coordinates per line. XYZ does not store bonds, bond orders, charge, or atom
maps; that is why we retain the original CSV.

## Part 5: generate descriptors with one workshop command

Run the prepared AQME wrapper:

```bash
bash scripts/run_aqme_descriptors.sh
```

`bash` runs a shell script. The wrapper supplies AQME with the input path, mapped
atoms, output path, and processor count. It exists so that your first AQME run is
not obscured by a long command. The full AQME command is unpacked later in the
main `README.md`.

When it finishes, list the results:

```bash
ls outputs/01_aqme_descriptors
```

Look for:

- `A1_rdkit_conf_*.json`: descriptors for individual conformers.
- `AQME-ROBERT_interpret_A1.csv`: an approachable descriptor table.
- `AQME-ROBERT_full_A1.csv`: the complete descriptor table.
- `boltz/A1_boltz.json`: Boltzmann-averaged results.

## Part 6: run a conformer search with RDKit

```bash
python scripts/rdkit_conformer_search.py
```

This may generate many candidates but retain only distinct conformers. “Distinct”
depends on the energy and RMSD rules selected by the script.

Inspect the resulting table:

```bash
column -s, -t < outputs/03_rdkit_search/rdkit_summary.csv
```

At this stage, the important columns are `rank` and
`relative_energy_kcal_mol`. A value of zero identifies a lowest-energy structure.

## Part 7: move from commands to a notebook

A notebook divides Python into cells. Run one cell with Shift-Return. Variables
created by an earlier cell remain available to later cells, so run the notebook
from top to bottom the first time.

After the one-time Jupyter installation described in `README.md`, start it with:

```bash
jupyter lab AQME_descriptor_and_conformer_workshop.ipynb
```

Select the `aqme` kernel. The notebook repeats the same workflow interactively and
writes its files under `outputs/notebook/` so it does not overwrite terminal runs.

## Part 8: CREST is the slow step

Do not run CREST until the facilitator asks. A reduced-cost search still takes a
few minutes for A1. The command is:

```bash
bash scripts/run_crest.sh quick 4
```

While it runs, the terminal displays a log rather than a progress bar. A long log
does not necessarily indicate an error. Successful completion includes the words
`CREST terminated normally` and produces `crest_conformers.xyz`.

## When something goes wrong

Read the final few lines of the error first. Then check, in order:

```bash
pwd
```

```bash
conda activate aqme
```

```bash
ls
```

Common messages:

- `No such file or directory`: you are in the wrong folder or mistyped a path.
- `command not found`: the environment is inactive or the program is not installed.
- `ModuleNotFoundError`: the selected Python is not from the `aqme` environment.
- A Python `Traceback`: read the last line first; it usually contains the useful message.

Errors are diagnostic information, not a sign that you have damaged anything.
Generated workshop files live under `outputs/` and can be reproduced from the CSV.
