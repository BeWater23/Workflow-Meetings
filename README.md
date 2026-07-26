# Computational chemistry / modeling workflow

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

## Command-line basics

This section introduces the terms and commands used throughout the workshop. No
previous command-line or programming experience is required.

### Vocabulary

- **Terminal:** an application in which you give the computer text instructions.
- **Command:** one instruction entered in the terminal.
- **Option or flag:** a setting added to a command, such as `--version`.
- **Folder or directory:** a location containing files. The terms mean the same
  thing.
- **Path:** the address of a file or directory.
- **Working directory:** the directory in which the terminal is currently
  operating.
- **Python:** the programming language used by RDKit, AQME, and the workshop
  scripts.
- **Conda environment:** an isolated collection of compatible programs and
  packages.
- **Script:** a saved sequence of Python or shell instructions.
- **Notebook:** a document containing explanations, executable cells, and their
  results.

Type only the text inside each code block, not the terminal prompt. Run one
command at a time and inspect its output before continuing.

### Navigate the filesystem

Open the macOS Terminal application. Ask the terminal for your current location:

```bash
pwd
```

`pwd` means **print working directory**. Move into the repository by replacing
the example path with its location on your computer:

```bash
cd "/path/to/Workflow-Meetings"
```

`cd` means **change directory**. Quotation marks protect paths containing spaces.
Confirm the location and list its contents:

```bash
pwd
ls
```

Move into the descriptor workshop and return to its parent directory:

```bash
cd descriptor_generation
cd ..
```

`..` means the parent directory. A path without a leading `/` is interpreted
relative to the current working directory.

### Inspect files without editing them

List the descriptor inputs and display the first two lines of the example CSV:

```bash
ls descriptor_generation/inputs
head -n 2 descriptor_generation/inputs/A1.csv
```

In the second command, `head` displays the beginning of a file, `-n 2` requests
two lines, and the final argument is the file path.

### Activate a Conda environment

Activate the chemistry environment:

```bash
conda activate aqme
```

The terminal prompt normally shows `(aqme)` after activation. Confirm which
Python will run and check its version:

```bash
which python
python --version
```

Run a short Python instruction directly from the terminal:

```bash
python -c "print('Hello from Python')"
```

Here, `python` starts Python, `-c` indicates that code follows on the command
line, and `print(...)` produces the displayed output.

### Useful terminal habits

- Press Tab to complete a file or directory name.
- Press Up arrow to recall the previous command.
- Press Control-C to stop a running command.
- Commands and file names are case-sensitive: `A1.csv` and `a1.csv` are
  different names.
- Use `pwd` whenever you are unsure which directory is active.
- Read the final line of an error message first; it often contains the most
  useful explanation.

### Basic troubleshooting

Check the working directory, environment, Python executable, and available files:

```bash
pwd
conda activate aqme
which python
ls
```

Common messages:

- `No such file or directory`: check the current directory, path, and spelling.
- `command not found`: activate the required environment or check that the
  program is installed.
- `ModuleNotFoundError`: the active Python environment does not contain the
  requested package.
- A Python `Traceback`: begin with its final line, then work upward for context.

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
