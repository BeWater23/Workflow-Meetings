# Command-line reference: RDKit, CREST, and AQME

Run these commands from `descriptor_generation`. They reproduce the notebook
workflow and keep the output from each stage in a separate directory.

## 1. Activate the environment

```bash
conda activate aqme
workshop_dir="$PWD"
```

Check the programs:

```bash
python -c "from importlib.metadata import version; print('AQME', version('aqme'))"
python -c "from rdkit import rdBase; print('RDKit', rdBase.rdkitVersion)"
crest --version
xtb --version
```

## 2. Generate structures with RDKit

Create one optimized XYZ:

```bash
python scripts/smiles_to_xyz.py
```

Create the optimized and RMSD-filtered conformer ensemble:

```bash
python scripts/rdkit_conformer_search.py
```

Inspect the results:

```bash
head -n 8 outputs/01_smiles_to_xyz/A1.xyz
column -s, -t < outputs/02_rdkit_search/rdkit_summary.csv
```

## 3. Run CREST

Prepare a dedicated CREST directory:

```bash
crest_dir="$workshop_dir/outputs/03_crest_quick"
mkdir -p "$crest_dir"
cp "$workshop_dir/outputs/01_smiles_to_xyz/A1.xyz" "$crest_dir/A1.xyz"
```

Run a quick conformer search:

```bash
(
  cd "$crest_dir"
  crest A1.xyz \
    --chrg -1 \
    --uhf 0 \
    --gfn2 \
    --T 4 \
    --quick 2>&1 | tee crest.log
)
```

For a standard search, use a new directory and omit `--quick`:

```bash
crest_full_dir="$workshop_dir/outputs/03_crest_full"
mkdir -p "$crest_full_dir"
cp "$workshop_dir/outputs/01_smiles_to_xyz/A1.xyz" "$crest_full_dir/A1.xyz"
(
  cd "$crest_full_dir"
  crest A1.xyz --chrg -1 --uhf 0 --gfn2 --T 4 2>&1 | tee crest.log
)
```

### CREST keyword reference

| Argument | Meaning |
| --- | --- |
| `A1.xyz` | Starting coordinates |
| `--chrg -1` | Total molecular charge |
| `--uhf 0` | Number of unpaired electrons |
| `--gfn2` | GFN2-xTB energy and force model |
| `--T 4` | Four processing threads |
| `--quick` | Reduced conformer-sampling effort |

Inspect the principal CREST outputs:

```bash
head outputs/03_crest_quick/crest.energies
ls -lh outputs/03_crest_quick/crest_best.xyz \
  outputs/03_crest_quick/crest_conformers.xyz
```

## 4. Compare the ensembles

```bash
python scripts/compare_ensembles.py
```

The script compares ensemble size and relative-energy coverage. MMFF and
GFN2-xTB absolute energies are not directly comparable.

## 5. Run AQME QDESCP on the RDKit ensemble

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

### AQME keyword reference

| Argument | Meaning |
| --- | --- |
| `--qdescp` | Run the descriptor module |
| `--files ...sdf` | Use the supplied conformer ensemble |
| `--csv_name ...csv` | Add the molecule name and original SMILES to the tables |
| `--charge -1` | Total molecular charge |
| `--mult 1` | Singlet multiplicity |
| `--qdescp_atoms "['1','2','3']"` | Calculate local descriptors for mapped atoms 1–3 |
| `--destination "."` | Write results in the current output directory |
| `--nprocs 4` | Use four processes |

The SDF supplied with `--files` is the completed RDKit ensemble, so QDESCP does
not run CSEARCH. QDESCP xTB-optimizes the supplied geometries by default before
calculating and averaging their properties. Add `--xtb_opt False` when the
descriptors must use the exact input coordinates.

Inspect the descriptor table:

```bash
head -n 2 outputs/05_aqme_descriptors/AQME-ROBERT_interpret_A1.csv
```

## 6. Run AQME QDESCP on the CREST ensemble

Convert the coordinate-only CREST multi-XYZ into a mapped, bond-aware SDF:

```bash
python scripts/crest_xyz_to_sdf.py
```

Create a separate output directory and run QDESCP:

```bash
crest_aqme_dir="$workshop_dir/outputs/05_aqme_descriptors_crest"
mkdir -p "$crest_aqme_dir"
(
  cd "$crest_aqme_dir"
  python -m aqme \
    --qdescp \
    --files "../03_crest_quick/A1_crest.sdf" \
    --csv_name "../../inputs/A1.csv" \
    --charge -1 \
    --mult 1 \
    --qdescp_atoms "['1','2','3']" \
    --destination "." \
    --nprocs 4
)
```

Separate output directories preserve both descriptor tables for comparison.

## 7. Shell-script commands

Run CREST through the reusable shell workflow in its own directory:

```bash
bash scripts/run_crest.sh quick 4 "$workshop_dir/outputs/03_crest_script"
```

Run QDESCP on `outputs/02_rdkit_search/A1_rdkit.sdf`:

```bash
bash scripts/run_aqme_descriptors.sh
```

The shell scripts use the same charge, spin, method, mapped atoms, and output
conventions shown in the expanded commands above.
