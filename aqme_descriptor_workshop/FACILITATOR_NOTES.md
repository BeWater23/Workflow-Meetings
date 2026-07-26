# Facilitator notes

## Before the meeting

1. Activate `aqme` and run `python scripts/smiles_to_xyz.py` plus
   `python scripts/rdkit_conformer_search.py` from this folder.
2. Run `bash scripts/run_crest.sh quick 4`. Start the full CREST run separately if
   you want to show how the quick and standard ensembles differ.
3. Run the AQME QDESCP command in the README so descriptor tables are available
   even if a live xTB calculation is slow.
4. Confirm Avogadro opens both multi-XYZ ensemble files.
5. If using the notebook, install Jupyter once as shown in the README and confirm
   that the selected kernel is `aqme`.

Generated files are intentionally ignored by Git. Preserve a demonstration run by
copying it to a named, tracked folder only if the group wants fixed reference data.

## Recommended beginner flow: two 60-minute sessions

| Time | Topic | Demonstration |
| ---: | --- | --- |
| Session 1, 0–10 | Vocabulary | Terminal, command, folder, path, Python, environment |
| Session 1, 10–25 | Navigation | Practice `pwd`, `cd`, `ls`, Tab, Up arrow, Control-C |
| Session 1, 25–35 | Conda and Python | Activate `aqme`; run `which python` and `print(...)` |
| Session 1, 35–50 | Chemistry files | Inspect CSV and SMILES; generate and inspect one XYZ |
| Session 1, 50–60 | Recap | Learners repeat navigation and XYZ generation in pairs |
| Session 2, 0–10 | Retrieval practice | Explain CSV → conformers → xTB → descriptors |
| Session 2, 10–25 | AQME | Run the simple wrapper; inspect JSON and CSV outputs |
| Session 2, 25–40 | Notebook | Run cells slowly; connect variables to terminal options |
| Session 2, 40–50 | RDKit vs CREST | Compare precomputed structures, time, and energy models |
| Session 2, 50–60 | Participant task | Repeat one step and explain it to a partner |

For a single 90-minute meeting, shorten the paired practice and show precomputed
CREST results. Do not attempt the original 40-minute agenda with new programmers.

For a notebook-focused audience, use
`AQME_descriptor_and_conformer_workshop.ipynb` for the 5–35 minute portion, then
show the matching terminal commands in the README. The notebook keeps CREST
disabled by default because the validated quick run still took about 2.5 minutes
with two threads.

## Teaching approach for first-time programmers

- Use the sequence **I do → we do → you do** for every new command.
- Put only one new command on screen at a time and explain its output before moving on.
- Say “current folder” before introducing the term “working directory.”
- Describe options such as `--input` as labeled settings before calling them flags.
- Ask learners to predict what a command will do before pressing Return.
- Keep a known-good terminal open for recovery and precompute the CREST ensemble.
- Never debug installation problems in front of the group; verify environments first.
- Treat error messages as a reading exercise: start from the final line.

## Points worth emphasizing

- Conformer generation is part of the descriptor model, not merely file
  preparation. Different ensembles can produce different Boltzmann averages.
- A SMILES carries bonding, stereochemical, charge, and atom-map information.
  Plain XYZ carries only elements and coordinates.
- Multiplicity and CREST's `--uhf` are related but not numerically identical:
  a singlet has multiplicity 1 and zero unpaired electrons, so `--uhf 0`.
- The RDKit and CREST energies answer different questions. Do not compare their
  absolute values or declare a winner based only on the number of conformers.
- Atom maps `1`, `2`, and `3` identify the chemically corresponding atoms across
  the dataset. They are more robust for atomic descriptors than raw atom indices.

## If time is short

Run only the AQME descriptor command and the RDKit scripts live. Show the
precomputed CREST outputs and explain that a full search is intentionally not a
seconds-long interactive calculation.

## Common failures

- `ModuleNotFoundError: rdkit` or `aqme`: the `aqme` Conda environment is inactive.
- `crest: command not found`: activate `aqme` and verify `which crest`.
- AQME writes under `inputs/outputs` or QDESCP finds no conformers: set
  `workshop_dir="$PWD"` and use the absolute paths shown in the README.
- Wrong charge: re-check the bracketed `[CH-:1]`; direct CREST needs `--chrg -1`.
- A rerun refuses to start: the CREST script protects an existing ensemble. Pass a
  new output directory as its third argument.
- Avogadro displays an odd bond: XYZ has no bond orders. Open the SDF for a
  bond-aware view, or treat the XYZ view as coordinates only.
