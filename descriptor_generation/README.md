# Descriptor generation with RDKit, CREST, and AQME

This workshop follows one molecule from a mapped SMILES to a conformer-averaged
descriptor table. It first presents the workflow interactively in Jupyter and
then repeats it from the command line.

## Learning goals

By the end of the workshop, you will be able to:

- explain what information is stored in SMILES, XYZ, and SDF files;
- generate one 3D structure from a SMILES with RDKit;
- create and filter an RDKit conformer ensemble;
- run a CREST conformer search with explicit charge and spin settings;
- compare relative-energy coverage from RDKit and CREST; and
- calculate AQME QDESCP descriptors for a conformer ensemble that already
  exists.

## Example molecule

The input file [`inputs/A1.csv`](inputs/A1.csv) contains molecule `A1`:

```text
O=C([CH-:1]/[N:2]=[CH:3]/C1=CC=CC=C1)OC
```

The molecule has charge `−1`, multiplicity `1`, and mapped atoms `1`, `2`, and
`3`. The atom maps identify the atoms for which AQME calculates local
descriptors.

## Workshop sequence

### Part A — Interactive notebook

Run the notebook one cell at a time and inspect each result:

```bash
cd descriptor_generation
conda activate aqme
jupyter lab AQME_descriptor_and_conformer_workshop.ipynb
```

Select the `Python (aqme)` kernel. Notebook results are written to
`outputs/notebook/`.

### Part B — Command line

Repeat the same stages with Python scripts and direct CREST and AQME commands.
Use the [`student guide`](START_HERE.md) during the exercise. The
[`command-line reference`](DIRECT_COMMAND_LINE_WORKFLOW.md) collects the full
commands and keyword explanations on one page.

## Workshop files

| Path | Purpose |
| --- | --- |
| `AQME_descriptor_and_conformer_workshop.ipynb` | Interactive Part A |
| `START_HERE.md` | Step-by-step student guide |
| `DIRECT_COMMAND_LINE_WORKFLOW.md` | Part B command reference |
| `inputs/A1.csv` | Mapped SMILES and molecule name |
| `scripts/smiles_to_xyz.py` | Build one optimized XYZ structure |
| `scripts/rdkit_conformer_search.py` | Generate and filter the RDKit ensemble |
| `scripts/compare_ensembles.py` | Compare relative-energy coverage |
| `scripts/crest_xyz_to_sdf.py` | Attach mapped topology to a CREST ensemble |
| `scripts/run_crest.sh` | Reusable CREST shell workflow |
| `scripts/run_aqme_descriptors.sh` | Reusable QDESCP shell workflow |

## Output directories

The command-line exercise uses:

```text
outputs/
├── 01_smiles_to_xyz/
├── 02_rdkit_search/
├── 03_crest_quick/
├── 04_comparison/
└── 05_aqme_descriptors/
```

The notebook uses parallel locations under `outputs/notebook/`, allowing both
versions of the workflow to be inspected side by side.

## Important distinction

RDKit and CREST generate the conformer ensembles. AQME QDESCP receives one of
those completed ensembles through `--files`, performs xTB calculations, and
Boltzmann-averages the resulting descriptors. QDESCP optimizes the supplied
geometries with xTB by default, but it does not run a new conformer search.

## Documentation

- [AQME](https://aqme.readthedocs.io/)
- [CREST](https://crest-lab.github.io/crest-docs/)
- [RDKit conformer generation](https://www.rdkit.org/docs/RDKit_Book.html#conformer-generation)
