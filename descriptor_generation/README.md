# AQME descriptor and conformer-search workshop

This is a self-contained, command-line workshop built around molecule `A1` from
`../descriptor_generation_aqme/atom_props/input_imines.csv`. It starts with the
high-level AQME descriptor workflow, opens the black box by building 3D structures
with RDKit, and compares RDKit conformer sampling with CREST.

**No coding experience? Start with [`START_HERE.md`](START_HERE.md).** It introduces
the terminal, paths, Conda, Python, CSV/SMILES/XYZ files, and error messages one
command at a time. This README is the instructor and reference version.

For complete beginners, use two 60-minute sessions or one 90-minute session with
CREST precomputed. The original 35–45 minute flow is appropriate only after the
command-line introduction.

## Learning goals

By the end, participants should be able to:

1. Generate xTB and RDKit descriptors from a `SMILES,code_name` CSV with AQME.
2. Explain how a 2D SMILES becomes an explicit-hydrogen 3D XYZ structure.
3. Run and inspect an RDKit ETKDG/MMFF conformer search.
4. Run a CREST/GFN2-xTB conformer search with the correct charge and spin.
5. Explain why conformer counts and relative energies can differ between methods.

## The example

`inputs/A1.csv` contains:

```csv
SMILES,code_name
O=C([CH-:1]/[N:2]=[CH:3]/C1=CC=CC=C1)OC,A1
```

Three details matter:

- `[CH-:1]` makes the total formal charge **−1**.
- `:1`, `:2`, and `:3` are atom-map labels used to request atomic descriptors.
- This closed-shell anion is a singlet: multiplicity `1`, or `--uhf 0` in CREST.

XYZ stores elements and coordinates, but not bonds, formal charges, or atom-map
labels. Keep the original CSV beside every XYZ-derived workflow.

## 0. Start in the AQME environment

From the repository root:

```bash
cd descriptor_generation
conda activate aqme
workshop_dir="$PWD"
python -m aqme
crest --version
xtb --version
```

The workshop was validated with AQME 2.0.1, CREST 2.12, xTB 6.7.1, and the RDKit
installed in the `aqme` Conda environment.

All generated files go under the ignored `outputs/` directory.

## Notebook version

The same workflow is available in
[`AQME_descriptor_and_conformer_workshop.ipynb`](AQME_descriptor_and_conformer_workshop.ipynb).
It uses native RDKit cells, the AQME Python API, and an explicit subprocess for
CREST. Notebook results go under `outputs/notebook/`, so they do not overwrite the
command-line results.

The repository's `environment-aqme.yml` includes Jupyter. If you are using an
older/pre-existing `aqme` environment where `jupyter` is not found, install it once:

```bash
conda install -n aqme -c conda-forge jupyterlab ipykernel
conda activate aqme
jupyter lab AQME_descriptor_and_conformer_workshop.ipynb
```

Use the notebook for teaching and exploration; use the command-line steps below
for repeatable batch runs. The notebook ends with a side-by-side comparison of the
two interfaces.

## 1. Generate descriptors with AQME

AQME's QDESCP workflow accepts the CSV directly. It performs RDKit conformer
generation, xTB calculations, descriptor collection, and Boltzmann averaging:

```bash
aqme_desc_dir="$workshop_dir/outputs/01_aqme_descriptors"
mkdir -p "$aqme_desc_dir"
(
  cd "$aqme_desc_dir"
  python -m aqme \
    --qdescp \
    --input "$workshop_dir/inputs/A1.csv" \
    --qdescp_atoms "['1','2','3']" \
    --destination "$aqme_desc_dir" \
    --nprocs 4
)
```

Inspect the output:

```bash
find outputs/01_aqme_descriptors -maxdepth 2 -type f | sort
```

The JSON files contain per-conformer values. The generated
`AQME-ROBERT_*_A1.csv` tables contain Boltzmann-averaged molecular and mapped-atom
descriptors at different levels of interpretability. Use `interpret` for an
accessible first look; use `full` when downstream feature selection is planned.

Talking point: this one command is the production workflow. The next steps expose
the conformer-generation choices hidden underneath it.

## 2. Convert SMILES to one XYZ manually with RDKit

Run the readable teaching script:

```bash
python scripts/smiles_to_xyz.py
head -n 8 outputs/02_smiles_to_xyz/A1.xyz
```

The script performs these operations explicitly:

1. Parse the SMILES and detect formal charge.
2. Add explicit hydrogens.
3. Embed one 3D geometry with reproducible ETKDGv3 coordinates.
4. Optimize it with MMFF94, falling back to UFF if parameters are unavailable.
5. Write XYZ and record charge and atom-map information in the comment line.

Open it in Avogadro if available:

```bash
avogadro outputs/02_smiles_to_xyz/A1.xyz
```

## 3. Perform the conformer search manually with RDKit

```bash
python scripts/rdkit_conformer_search.py \
  --num-confs 100 \
  --rmsd-threshold 0.50 \
  --max-keep 20
```

The script embeds 100 ETKDGv3 candidates, optimizes each with MMFF94, sorts by
force-field energy, and greedily removes structures less than 0.50 Å apart by
symmetry-aware heavy-atom RMSD.

Inspect the ranking and ensemble:

```bash
column -s, -t < outputs/03_rdkit_search/rdkit_summary.csv
avogadro outputs/03_rdkit_search/A1_rdkit_ensemble.xyz
```

Important distinction: ETKDG generates the coordinates; MMFF optimizes and ranks
them. RDKit is fast enough for interactive work, but the result depends on the
number of embeddings, force field, RMSD cutoff, and random seed.

## 4. Perform the conformer search with CREST

For a meeting, start with CREST's reduced-cost `--quick` protocol:

```bash
bash scripts/run_crest.sh quick 4
```

The script runs the equivalent direct command from a clean output directory:

```bash
crest A1.xyz --chrg -1 --uhf 0 --gfn2 --T 4 --quick
```

Use a standard search when time permits:

```bash
bash scripts/run_crest.sh full 4 outputs/04_crest_full
```

Key outputs are:

- `crest_best.xyz`: lowest-energy conformer.
- `crest_conformers.xyz`: multi-XYZ conformer ensemble.
- `crest.energies`: relative energy list.
- `crest.log`: complete run log.

CREST explores conformational space with metadynamics and ranks structures using
the chosen xTB method. It usually costs much more than RDKit but samples a
semiempirical potential-energy surface rather than a classical force field.

## 5. Compare the two ensembles

After the quick CREST run:

```bash
python scripts/compare_ensembles.py
```

For a result in another directory:

```bash
python scripts/compare_ensembles.py \
  --crest outputs/04_crest_full/crest_conformers.xyz
```

This creates `outputs/05_comparison/relative_energies.csv` and prints the number
of conformers and energy spread. Only compare **relative-energy coverage**.
MMFF energies are in kcal/mol and GFN2-xTB total energies are in Hartree; their
absolute values are not comparable even after unit conversion.

The comparison is illustrative rather than a benchmark: the search effort and
deduplication settings differ. For a controlled benchmark, use the same final QM
or xTB refinement and the same RMSD/energy filters on the union of both ensembles.

## 6. Run the same conformer choices through AQME

AQME exposes both backends through the same CSEARCH interface.

RDKit:

```bash
aqme_rdkit_dir="$workshop_dir/outputs/06_aqme_rdkit"
mkdir -p "$aqme_rdkit_dir"
(
  cd "$aqme_rdkit_dir"
  python -m aqme \
    --csearch \
    --program rdkit \
    --input "$workshop_dir/inputs/A1.csv" \
    --sample 10 \
    --destination "$aqme_rdkit_dir"
)
```

CREST:

```bash
aqme_crest_dir="$workshop_dir/outputs/06_aqme_crest"
mkdir -p "$aqme_crest_dir"
(
  cd "$aqme_crest_dir"
  python -m aqme \
    --csearch \
    --program crest \
    --input "$workshop_dir/inputs/A1.csv" \
    --sample 10 \
    --destination "$aqme_crest_dir" \
    --nprocs 4
)
```

AQME detects the `−1` charge from the SMILES. Keeping the charge explicit in the
direct CREST command is still good practice because XYZ itself does not encode it.
Absolute paths are intentional here: AQME 2.0.1 may resolve a relative destination
against the input CSV's directory rather than the current shell directory.

## Suggested wrap-up questions

1. Which assumptions enter before xTB descriptor calculation even starts?
2. What information is lost when converting SMILES or SDF to XYZ?
3. When is RDKit sampling sufficient, and when is CREST worth the extra cost?
4. Should descriptors represent one minimum or a Boltzmann-weighted ensemble?

## References

- [AQME QDESCP documentation](https://aqme.readthedocs.io/en/latest/API/aqme.qdescp.html)
- [AQME CSEARCH documentation](https://aqme.readthedocs.io/en/latest/API/aqme.csearch.html)
- [RDKit conformer generation](https://www.rdkit.org/docs/RDKit_Book.html#conformer-generation)
- [CREST command-line keywords](https://crest-lab.github.io/crest-docs/page/documentation/keywords.html)
