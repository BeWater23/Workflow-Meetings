# Descriptor generation workshop

This workshop uses molecule `A1` from
`../descriptor_generation_aqme/atom_props/input_imines.csv`. It first exposes the
individual structure-preparation steps and then replaces them with AQME.

If you are new to the terminal or Python, follow
[`START_HERE.md`](START_HERE.md) one command at a time.

## 1. Enter the workshop

```bash
cd descriptor_generation
conda activate aqme
```

All commands below create files under the ignored `outputs/` folder.

## 2. Build one 3D structure from SMILES

```bash
python scripts/smiles_to_xyz.py
```

The script reads `inputs/A1.csv`, adds hydrogens, generates coordinates, optimizes
the structure with RDKit, and writes `outputs/01_smiles_to_xyz/A1.xyz`.

## 3. Search conformers with RDKit

```bash
python scripts/rdkit_conformer_search.py
```

The conformer ensemble and its energy summary are written to
`outputs/02_rdkit_search/`.

## 4. Search conformers with CREST

The quick version is suitable for a live demonstration:

```bash
bash scripts/run_crest.sh quick 4
```

The second argument is the number of processor cores. CREST writes its results to
`outputs/03_crest_quick/`.

## 5. Compare the two searches

```bash
python scripts/compare_ensembles.py
```

RDKit and CREST use different energy models, so compare the ensemble sizes and
relative-energy ranges—not their absolute energies.

## 6. Automate descriptor generation with AQME

```bash
bash scripts/run_aqme_descriptors.sh
```

AQME performs conformer generation, xTB calculations, descriptor collection, and
Boltzmann averaging. Its results are written to `outputs/05_aqme_descriptors/`.

## 7. Repeat the workflow in Jupyter

```bash
jupyter lab AQME_descriptor_and_conformer_workshop.ipynb
```

Select the `aqme` kernel and run the cells from top to bottom. Notebook results
are kept separately under `outputs/notebook/`.

## Further reading

- [AQME documentation](https://aqme.readthedocs.io/)
- [RDKit conformer generation](https://www.rdkit.org/docs/RDKit_Book.html#conformer-generation)
- [CREST documentation](https://crest-lab.github.io/crest-docs/)
