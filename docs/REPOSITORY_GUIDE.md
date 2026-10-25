# Repository guide and workflow

This folder is an **addition to the existing GitHub repository** `wiIlowI/MMA3001_appletree`. Do not replace or reset its actual Git history.

- `notebooks/`: the four original Google Colab workflows, already committed to the user's GitHub repository.
- `results/`: the two saved derived metrics CSVs already in GitHub, plus regenerated summary CSVs and plots under `results/figures/`.
- `src/apple_tree/`: standalone reusable interpolation and evaluation functions corresponding to notebook methods. Notebooks can still be run independently.
- `tests/`: unit tests and results-integrity tests. Run with `python -m pytest -q`.
- `scripts/`: commands for results validation and plotting without restricted raw images.
- `docs/api/`: HTML reference generated from Python docstrings.
- `reports/`: supplied individual report in Word/PDF, and an actual pytest result report.
- `data/`: restricted dataset access instructions, not source PNG files.

## Recommended workflow

1. Clone your GitHub repository or work from your existing local clone.
2. Copy the files from this update into the matching paths, preserving your existing notebooks, README and `.git`.
3. Run `python -m pip install -e ".[dev]"` and `python -m pytest -q`.
4. Run `python scripts/check_results.py` and `python scripts/plot_results.py`.
5. Inspect changes with `git status`, then create genuine commit(s) and push to `main`.
6. Clone the updated **actual GitHub repository** afresh to create your Moodle clone ZIP.

Access to the original restricted Monash Drive `TreeID` dataset is needed for re-running the data-collection and 12-image experiments. Derived-CSV visualisation and synthetic tests do not require that access. The results are in uncalibrated image codes, not metres or 3D tree skeleton geometry.
