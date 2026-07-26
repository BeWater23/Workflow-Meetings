# Workflow Meetings

Workshop materials for moving from manual molecular structure preparation to
automated descriptor generation and machine-learning models.

## Workshop order

1. **Manual foundations:** convert a SMILES to 3D, search conformers with RDKit
   and CREST, and compare the ensembles in [`descriptor_generation`](descriptor_generation/).
2. **AQME automation:** run the same preparation and descriptor workflow with
   AQME.
3. **ROBERT modeling:** introduce curation, model generation, verification, and
   prediction with the examples in [`modeling_robert`](modeling_robert/).
4. **Larger datasets:** use the solubility dataset in
   [`solubility_prediction`](solubility_prediction/) to connect AQME and ROBERT.

Complete beginners should start with
[`descriptor_generation/START_HERE.md`](descriptor_generation/START_HERE.md).
The same descriptor-generation lesson is also available as a
[`Jupyter notebook`](descriptor_generation/AQME_descriptor_and_conformer_workshop.ipynb).

## Software setup

Create the environments by following the current official instructions:

- [AQME installation](https://aqme.readthedocs.io/en/latest/Quickstart/setup.html)
- [ROBERT installation](https://robert.readthedocs.io/en/latest/Install/installation.html)

For the manual descriptor workshop, make sure the AQME environment also provides
RDKit, Open Babel, xTB, CREST, and JupyterLab. The AQME installation page lists
the required external chemistry programs; JupyterLab can be added with:

```bash
conda activate aqme
conda install -c conda-forge jupyterlab ipykernel
```

Check the installations before the workshop:

```bash
python -m aqme --help
python -c "import rdkit"
xtb --version
crest --version
jupyter lab --version
```

Activate the ROBERT environment separately when the modeling section begins:

```bash
conda activate robert
python -m robert --help
```

## Repository policy

Inputs, scripts, notebooks, and participant instructions are version-controlled.
Generated conformers, descriptors, logs, plots, and models are ignored so every
participant creates their own results.
