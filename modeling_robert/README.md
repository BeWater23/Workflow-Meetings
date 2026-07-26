# Modeling with ROBERT

This section starts after descriptor generation. The example CSV files already
contain a target column (`ddG`) and molecular descriptors.

Activate ROBERT and run the smallest example:

```bash
conda activate robert
cd modeling_robert/dft_descriptors/ka2
python -m robert --names name --y ddG --csv_name ka2.csv
```

ROBERT creates a report and folders for data curation, model generation,
verification, and prediction. These outputs are ignored by Git.

The `ka2`, `ka4`, and `ka6` folders contain related small datasets. They are useful
for discussing how the amount of data affects a model, but they are too small for
strong scientific conclusions.

See the [ROBERT full-workflow example](https://robert.readthedocs.io/en/latest/Examples/full_workflow/full_workflow.html)
for an explanation of the generated report.
