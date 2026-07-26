# Molecular-property modeling with ROBERT

This exercise starts with descriptor tables that already contain a molecular
identifier, the response variable `ddG`, and numerical molecular descriptors.
ROBERT curates the data, generates models, evaluates them, and assembles a
report.

## 1. Run the smallest example

From the repository root:

```bash
conda activate robert
cd modeling_robert/dft_descriptors/ka2
python -m robert --names name --y ddG --csv_name ka2.csv
```

The arguments specify:

- `--names name`: the column containing molecule identifiers;
- `--y ddG`: the response variable to predict; and
- `--csv_name ka2.csv`: the input descriptor table.

## 2. Inspect the workflow

ROBERT organizes its results by modeling stage:

| Stage | Purpose |
| --- | --- |
| `CURATE` | Clean the dataset and analyze correlated variables |
| `GENERATE` | Select and train candidate models |
| `VERIFY` | Apply model-validation tests |
| `PREDICT` | Report predictions, errors, and interpretation plots |
| `ROBERT_report.pdf` | Summarize settings, results, warnings, and figures |

Open the report and identify:

- the number of observations and descriptors;
- the selected model and variables;
- cross-validation and prediction statistics;
- compounds with large errors or unusual descriptor values; and
- warnings caused by the small dataset.

## 3. Compare dataset sizes

The related examples contain 15, 17, and 19 molecules:

```text
dft_descriptors/ka2/ka2.csv
dft_descriptors/ka4/ka4.csv
dft_descriptors/ka6/ka6.csv
```

Run the same command from each directory by changing `--csv_name`. Compare the
selected variables, validation results, and uncertainty across the three
reports. These datasets are suitable for learning the workflow but are too small
for strong scientific conclusions.

## 4. Connect descriptors to the model

Before modeling, distinguish the three column roles:

- **identifier:** `name`;
- **target:** `ddG`; and
- **features:** the calculated molecular descriptors.

Conformer generation and descriptor averaging occur upstream of ROBERT. Choices
made during structure preparation can therefore affect the features available
to the model.

For further details, see the
[ROBERT full-workflow example](https://robert.readthedocs.io/en/latest/Examples/full_workflow/full_workflow.html).
