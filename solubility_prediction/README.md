# Solubility prediction

This example shows the combined AQME–ROBERT workflow on a larger dataset. The
source `dataset.csv` contains compound names, SMILES, measured solubilities, and
published ESOL predictions.

Prepare a workshop-sized ROBERT input:

```bash
cd solubility_prediction
python prepare_input.py --limit 100
```

Then activate the ROBERT environment containing the additional AQME dependencies
listed in the official workflow and run:

```bash
conda activate robert
python -m robert --aqme --y solubility --csv_name outputs/solubility_robert.csv
```

Omit `--limit 100` when preparing the full dataset. All generated inputs,
descriptors, models, and reports under `outputs/` are ignored by Git.

See the official [ROBERT workflow from SMILES](https://robert.readthedocs.io/en/latest/Examples/full_workflow/smiles_workflow.html)
for installation requirements and output details.
