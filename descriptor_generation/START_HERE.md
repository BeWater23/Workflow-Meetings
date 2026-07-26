# Student guide: descriptor generation

Follow this guide in order. Part A uses a Jupyter notebook so that every stage
and result is visible. Part B repeats the workflow from the terminal so that the
same calculation can be automated and scaled.

## Before you begin

Open a terminal in the repository root, enter the workshop folder, and activate
the chemistry environment:

```bash
cd descriptor_generation
conda activate aqme
```

Confirm that the main programs are available:

```bash
python --version
python -m aqme --help
crest --version
xtb --version
jupyter lab --version
```

Useful terminal keys:

- Tab completes a file or folder name.
- Up arrow recalls the previous command.
- Control-C stops a running command.
- File names and paths are case-sensitive.

## Part A — Explore the workflow in Jupyter

Launch the notebook:

```bash
jupyter lab AQME_descriptor_and_conformer_workshop.ipynb
```

Select the `Python (aqme)` kernel. Run one cell at a time with Shift-Return and
read the output before continuing.

### 1. Check the notebook environment

The first cells introduce basic Python objects and load pandas, RDKit, AQME, and
the standard-library tools used in the exercise.

Check that:

- the working directory is `descriptor_generation`;
- the output root is `outputs/notebook/`; and
- the displayed software versions come from the `aqme` environment.

### 2. Read the molecular input

The notebook reads `inputs/A1.csv`, parses the mapped SMILES, and reports the
formal charge and mapped atoms.

Notice that SMILES stores atoms, bonds, stereochemistry, formal charge, and atom
maps, but no 3D coordinates.

### 3. Generate one XYZ structure

RDKit adds explicit hydrogens, embeds a three-dimensional structure with
ETKDGv3, and optimizes it with MMFF94. The resulting file is:

```text
outputs/notebook/01_smiles_to_xyz/A1.xyz
```

XYZ stores element symbols and Cartesian coordinates. It does not preserve bond
orders, charge, multiplicity, or atom maps as structured fields.

### 4. Generate the RDKit ensemble

The notebook embeds multiple structures, optimizes them, ranks them by force-
field energy, and removes geometrically similar conformers using a heavy-atom
RMSD threshold.

Inspect the energy table and these files:

```text
outputs/notebook/02_rdkit_search/A1_rdkit.sdf
outputs/notebook/02_rdkit_search/A1_rdkit_ensemble.xyz
outputs/notebook/02_rdkit_search/rdkit_summary.csv
```

The multi-conformer SDF preserves molecular topology and the metadata required
by AQME.

### 5. Run the CREST search

The notebook displays the CREST command and runs it as an external process. A
new calculation streams its output into the notebook and into `crest.log`. If a
completed ensemble is present, the notebook reuses it and displays the final log
lines.

The main result is:

```text
outputs/notebook/03_crest_quick/crest_conformers.xyz
```

The quick search is suitable for the workshop. A standard CREST search uses
more extensive sampling and takes longer.

### 6. Compare RDKit and CREST

The comparison reports the number of conformers and the distribution of
relative energies for each method.

Compare relative-energy coverage only. RDKit/MMFF and CREST/GFN2-xTB energies
come from different models, so their absolute values are not on the same scale.

### 7. Calculate AQME descriptors

The notebook passes the completed RDKit SDF directly to AQME QDESCP. AQME runs
xTB calculations for the supplied conformers and Boltzmann-averages the
descriptors. It does not create another conformer ensemble.

Inspect the resulting table:

```text
outputs/notebook/05_aqme_descriptors/AQME-ROBERT_interpret_A1.csv
```

Identify the molecule name, SMILES, molecular descriptors, and mapped-atom
descriptors in the output.

## Part B — Repeat the workflow from the command line

Keep the notebook open for comparison and open a second terminal in the
repository root:

```bash
cd descriptor_generation
conda activate aqme
workshop_dir="$PWD"
```

### 1. Inspect the input

```bash
head -n 2 inputs/A1.csv
```

The second line contains the mapped SMILES and the name `A1`.

### 2. Generate one XYZ

```bash
python scripts/smiles_to_xyz.py
head -n 8 outputs/01_smiles_to_xyz/A1.xyz
```

The script reports the detected charge, mapped atoms, optimization method, and
output path.

### 3. Generate the RDKit ensemble

```bash
python scripts/rdkit_conformer_search.py
column -s, -t < outputs/02_rdkit_search/rdkit_summary.csv
```

The lowest relative energy is zero. Each additional row represents a retained
conformer.

### 4. Run CREST directly

Create a dedicated working directory because CREST writes several files into
its current directory:

```bash
crest_dir="$workshop_dir/outputs/03_crest_quick"
mkdir -p "$crest_dir"
cp "$workshop_dir/outputs/01_smiles_to_xyz/A1.xyz" "$crest_dir/A1.xyz"
```

Run the search:

```bash
(
  cd "$crest_dir"
  crest A1.xyz --chrg -1 --uhf 0 --gfn2 --T 4 --quick 2>&1 | tee crest.log
)
```

The parentheses keep the directory change inside a subshell. When CREST
finishes, the terminal remains in `descriptor_generation`.

The keywords specify:

- `--chrg -1`: total molecular charge;
- `--uhf 0`: zero unpaired electrons;
- `--gfn2`: GFN2-xTB energy and force model;
- `--T 4`: four processing threads; and
- `--quick`: reduced sampling for the workshop.

A successful calculation creates
`outputs/03_crest_quick/crest_conformers.xyz` and ends with
`CREST terminated normally`.

### 5. Compare the ensembles

```bash
python scripts/compare_ensembles.py
```

The combined relative-energy table is written to:

```text
outputs/04_comparison/relative_energies.csv
```

### 6. Calculate descriptors for the existing RDKit ensemble

Create a descriptor directory and run AQME from inside it:

```bash
aqme_dir="$workshop_dir/outputs/05_aqme_descriptors"
mkdir -p "$aqme_dir"
(
  cd "$aqme_dir"
  python -m aqme \
    --qdescp \
    --files "../02_rdkit_search/A1_rdkit.sdf" \
    --csv_name "../../inputs/A1.csv" \
    --charge -1 \
    --mult 1 \
    --qdescp_atoms "['1','2','3']" \
    --destination "." \
    --nprocs 4
)
```

`--files` supplies the completed SDF ensemble. `--csv_name` carries the molecule
name and original SMILES into the descriptor tables. AQME QDESCP performs xTB
calculations and descriptor averaging without running CSEARCH.

Inspect the student-facing result:

```bash
head -n 2 outputs/05_aqme_descriptors/AQME-ROBERT_interpret_A1.csv
```

### 7. Use the CREST ensemble with AQME

CREST produces a coordinate-only multi-XYZ. Attach the mapped SMILES topology
before supplying it to AQME:

```bash
python scripts/crest_xyz_to_sdf.py
```

The converted ensemble is
`outputs/03_crest_quick/A1_crest.sdf`. Use it in a separate QDESCP output
directory when comparing RDKit-based and CREST-based descriptor tables.

### 8. Run the reusable shell workflows

The shell scripts collect the same commands for routine use:

```bash
bash scripts/run_crest.sh quick 4 "$workshop_dir/outputs/03_crest_script"
bash scripts/run_aqme_descriptors.sh
```

`run_crest.sh` accepts `quick` or `full`, a thread count, and an optional output
directory. The separate `03_crest_script` directory preserves the direct CREST
result from step 4.

## Output summary

| Stage | Main output |
| --- | --- |
| One 3D structure | `outputs/01_smiles_to_xyz/A1.xyz` |
| RDKit ensemble | `outputs/02_rdkit_search/A1_rdkit.sdf` |
| RDKit energies | `outputs/02_rdkit_search/rdkit_summary.csv` |
| CREST ensemble | `outputs/03_crest_quick/crest_conformers.xyz` |
| Ensemble comparison | `outputs/04_comparison/relative_energies.csv` |
| AQME descriptors | `outputs/05_aqme_descriptors/AQME-ROBERT_interpret_A1.csv` |

## Troubleshooting

- `command not found`: activate the `aqme` environment and check the program
  name.
- `ModuleNotFoundError`: confirm that the notebook kernel and terminal both use
  the `aqme` environment.
- `No such file or directory`: run `pwd`, check the path, and confirm that the
  preceding stage completed.
- CREST output already exists: use a different output directory for a new run.
- Strange bonds in an XYZ viewer: XYZ does not store bond orders; use the SDF
  when topology is required.
- AQME cannot find the ensemble: run the QDESCP command from the descriptor
  output directory with the relative path shown above.
