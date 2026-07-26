# Solubility prediction with AQME and ROBERT

This exercise applies the combined AQME–ROBERT workflow to a larger collection
of molecules. AQME generates descriptors from SMILES, and ROBERT uses those
descriptors to model measured aqueous solubility.

## Input data

`dataset.csv` contains compound names, SMILES, measured solubilities, and
published ESOL predictions. The preparation script keeps the compound name,
SMILES, and measured value. The published prediction is not used as a model
feature.

## 1. Prepare a workshop-sized dataset

From the repository root:

```bash
cd solubility_prediction
python prepare_input.py --limit 100
```

The prepared file contains 100 compounds and three columns:

```text
outputs/solubility_robert.csv
```

Inspect it with:

```bash
head -n 5 outputs/solubility_robert.csv
```

The columns are:

- `code_name`: molecular identifier;
- `smiles`: structure input for AQME; and
- `solubility`: measured response variable for ROBERT.

## 2. Run the combined workflow

Activate a ROBERT environment that also contains the AQME, Open Babel, and xTB
dependencies required for descriptor generation:

```bash
conda activate robert
python -m robert \
  --aqme \
  --y solubility \
  --csv_name outputs/solubility_robert.csv
```

`--aqme` tells ROBERT to generate molecular descriptors from the SMILES before
starting the modeling stages. `--y solubility` identifies the response variable.

## 3. Inspect the results

Follow the data through the two main phases:

1. AQME converts each SMILES into molecular descriptors.
2. ROBERT curates the descriptor table, generates models, verifies them, and
   reports predictions.

In the ROBERT report, locate the dataset size, selected descriptors, validation
statistics, prediction plots, and outlier analysis. Compare this example with
the small datasets in [`../modeling_robert/`](../modeling_robert/).

## 4. Prepare the full dataset

Omit `--limit` to include every valid row:

```bash
python prepare_input.py
```

Descriptor generation for the full dataset requires substantially more time
than the 100-compound exercise. Generated inputs, descriptors, models, and
reports are written below `outputs/`.

For installation details and additional options, see the official
[ROBERT workflow from SMILES](https://robert.readthedocs.io/en/latest/Examples/full_workflow/smiles_workflow.html).
