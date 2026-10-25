# MMA3001 — Corrected initial-to-final code comparison

**Correction of the previous comparison:** The first code in the ChatGPT project discussion was **not** the `01_colab_drive_dataset_and_first_analysis.ipynb` ZIP bootstrap and not the first GitHub commit. The project began with a very small Google Colab dataset-inspection snippet. The first downloadable project ZIP and notebook were delivered **after** that initial investigation.

## Chronological source record

1. **15 October 2026 — first code provided in the conversation:** Mount Google Drive and inspect `AppleTreeDataset` with `pathlib.Path.rglob`. A subsequent execution reported a mounted Drive but `Total files: 0`.
2. **15 October 2026 — first corrected dataset access:** Authenticate to the shared `TreeID` folder with the Drive API, using `FOLDER_ID = '13eo790JWqCG11PpBQtxzf1ditf9pU63S'`. This made the authorised shared folder accessible even though the original `MyDrive/AppleTreeDataset` path was absent.
3. **15 October 2026 — first substantial packaged Python implementation:** `mma3001_apple_tree_project.zip`. This package contained `src/apple_tree/io.py`, `depth.py`, `evaluation.py`, `geometry.py`, `cli.py`, scripts, tests, documentation and `notebooks/01_colab_drive_dataset_and_first_analysis.ipynb`. The original ZIP is preserved in the conversation files.
4. **Later Colab revisions:** image decoding was changed after an RGB-stored depth PNG was discovered; package and cloned-repo dependencies were removed from the four final Colab notebooks; the 12-image experiment and common-support analysis were developed.
5. **Final delivered notebook versions:** `1_Dataset.ipynb`, `2_Depth_Metric.ipynb`, `3_Common_Support_Metric.ipynb`, and `4_Results_and_Visualisations.ipynb`; the GitHub repository also contains reusable testable source and documentation.

## 1. The very first code in the chat: Drive mount and inventory

The earliest recovered code statements were:

```python
from google.colab import drive
drive.mount('/content/drive')

from pathlib import Path
root = Path('/content/drive/MyDrive/AppleTreeDataset')
files = [p for p in root.rglob('*') if p.is_file()]
```

*These are the recovered original statements, presented together. The complete original assistant-message formatting is not preserved in a source file.* The user subsequently reported that Drive mounted but the search found **zero files**. The issue was not necessarily an empty dataset; the dataset was shared and could not be found under that assumed `MyDrive` path.

**Final Notebook 1, setup and API inventory:**

```python
from google.colab import auth
from google.auth import default
from googleapiclient.discovery import build

auth.authenticate_user()
creds, _ = default()
service = build('drive', 'v3', credentials=creds)
FOLDER_ID = '13eo790JWqCG11PpBQtxzf1ditf9pU63S'

def list_folder(folder_id):
    results = []
    token = None
    while True:
        response = service.files().list(
            q=f"'{folder_id}' in parents and trashed = false",
            fields='nextPageToken, files(id,name,mimeType,size)',
            pageSize=1000,
            pageToken=token,
            supportsAllDrives=True,
            includeItemsFromAllDrives=True
        ).execute()
        results.extend(response.get('files', []))
        token = response.get('nextPageToken')
        if not token:
            break
    return results
```

*The final excerpt is from the uploaded `1_Dataset.ipynb`; minor trailing lines of the cell are omitted.*

**Actual improvement:** A failed local-path approach was replaced by authenticated, paginated Drive API inventory. This enabled the project to enumerate 4,986 entries and select exact matching RGB/D/GT records, instead of finding zero files.

## 2. First packaged image reader vs final image handling

From the **original, first** `mma3001_apple_tree_project.zip`, `src/apple_tree/io.py`:

```python
def read_depth(path: str | Path) -> np.ndarray:
    with Image.open(path) as im:
        if im.mode in {"RGB", "RGBA", "P", "CMYK", "LA"}:
            raise ValueError(
                f"Depth PNG mode {im.mode!r} is not guaranteed to encode numeric depth"
            )
        arr = np.asarray(im)
    if arr.ndim != 2 or arr.dtype.kind not in 'ui':
        raise ValueError(f"Expected 2D unsigned integer depth; got {arr.shape} {arr.dtype}")
    return arr
```

**Final Notebook 1**:

```python
with Image.open(paths['D']) as img:
    raw = np.asarray(img)

if raw.ndim == 3:
    if not (np.array_equal(raw[:, :, 0], raw[:, :, 1]) and
            np.array_equal(raw[:, :, 1], raw[:, :, 2])):
        raise ValueError('Depth image channels are different.')
    depth = raw[:, :, 0]
else:
    depth = raw
```

**Actual improvement:** The first package rejected any RGB PNG, a conservative but over-restrictive assumption for this dataset. A real sample established that its three stored channels were identical, so the final notebook checks equality and then extracts one channel. This still does **not** establish a physical metres-per-code scale.

## 3. First packaged numerical comparison vs final multi-image study

The first `src/apple_tree/evaluation.py` already measured RMSE, MAE, coverage and runtime and selected between algorithms using validation RMSE adjusted for coverage:

```python
def compare_interpolators(depth: np.ndarray, invalid_value: int = 0,
                          radius: float = 6.0, seed: int = 42) -> dict:
    train, val, test = make_split(depth, invalid_value=invalid_value, seed=seed)
    records = {}
    predictions = {}
    for method in ("nearest", "idw"):
        records[method] = {}
        predictions[method] = {}
        for stage, mask in (("validation", val), ("test", test)):
            start = time.perf_counter()
            pred, support = interpolate_depth(depth, train, mask, method=method,
                                              radius=radius)
            duration = time.perf_counter() - start
            metric = prediction_metrics(depth, pred, mask, support)
            metric["runtime_seconds"] = duration
            records[method][stage] = metric
            predictions[method][stage] = (pred, support)
```

**Final Notebook 2** extended the actual repeated evaluation across multiple real images:

```python
for folder, season, entry in selection:
    data = service.files().get_media(
        fileId=entry['id'], supportsAllDrives=True
    ).execute()

    with Image.open(io.BytesIO(data)) as img:
        arr = np.array(img)

    if arr.ndim == 3:
        if not (np.array_equal(arr[:, :, 0], arr[:, :, 1]) and
                np.array_equal(arr[:, :, 1], arr[:, :, 2])):
            print('Skipped:', entry['name'])
            continue
        depth = arr[:, :, 0]
    else:
        depth = arr
```

*These are genuine portions; neither is the entire function/cell.*

**Actual improvement:** The original package already implemented **nearest and IDW**; those algorithms were **not invented in the final notebooks**. The change was from a single-example-oriented evaluator and external package dependencies to repeatable evaluation over 12 selected real images, two holdout designs and 48 saved observations in `MMA3001_appletree_depthmetric.csv`.

## 4. First error evaluation vs final common-support validation

The initial package's `prediction_metrics()` measured error only on the locations supported by each method:

```python
ok = requested & supported & np.isfinite(prediction)
used = int(ok.sum())
delta = prediction[ok] - np.asarray(true_depth, dtype=float)[ok]
```

This is a valid per-method statistic but does not ensure both methods are scored on **identical** pixel locations.

**Final Notebook 3**:

```python
predictions = {}
support = {}
for method in ('nearest', 'idw'):
    pred, ok = interpolate_depth(depth, train, test, method=method, radius=6)
    predictions[method] = pred
    support[method] = ok & np.isfinite(pred)

shared = test & support['nearest'] & support['idw']
```

**Actual improvement:** Common-support RMSE/MAE provide a fair paired comparison, while individual coverage remains a separate engineering outcome. This additional experiment was developed *after* the initial package; it was already present in intermediate common-support notebooks before the final Notebook 3.

## 5. First plotting script vs final Notebook 4

The initial ZIP's `scripts/plot_metrics.py` used a command-line JSON report and plotted **three** grouped statistics:

```python
data = json.loads(args.metrics.read_text())
models = list(data['results'])
fig, axes = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)
for metric, ax in zip(('rmse', 'mae', 'coverage'), axes):
    # plot validation and test values for the two models
    ...
```

*The comment and ellipsis mark the omitted original plotting loop.*

**Final Notebook 4** takes two actual experimental CSV files rather than the original package's JSON output:

```python
depth = pd.read_csv('MMA3001_appletree_depthmetric.csv')
common = pd.read_csv('MMA3001_appletree_commonsupportmetric.csv')
assert len(depth) == 48 and len(common) == 48

runtime = depth.pivot_table(
    index='design', columns='method', values='runtime_seconds',
    aggfunc='median'
) * 1000
```

It produces five PNG plots (`common_rmse`, `common_mae`, `coverage`, `runtime`, `seasonal_rmse`) and two summary CSVs. The final millisecond conversion makes the runtime plot label match the data.

## 6. Early proposed 3D output vs actual final scope

The **first ZIP already had** `src/apple_tree/geometry.py`, implementing `Camera`, `backproject()` and `write_ply()`, but it explicitly required verified camera intrinsics and depth scaling. The early notebook set `CALIBRATION = None` and skipped backprojection if unavailable.

The **final submitted study** remains a 2D image-code interpolation experiment. No calibrated 3D skeleton was produced. This is **scope reduction**, not evidence that the final code completed the initially suggested reconstruction goal.

## What this proves for the AI disclosure

- **Actual first coding step:** a simple Drive mount and `Path.rglob()` that returned no data at the assumed path.
- **AI-generated initial package:** reusable code for image loading, interpolation, evaluation, optional geometry, scripts and tests. It was considerably more ambitious than the final notebook workflow.
- **Verification and correction:** Drive access needed a different method; the image loader was over-restrictive for the actual RGB-stored depth PNG; independent package setup was too fragile for the notebook workflow; unequal prediction support needed paired validation; graph runtime units needed correction.
- **Continuity:** nearest/IDW methods and the basic validation idea were present from the first project ZIP. The final work made those methods more reproducible and reported a broader real-data experiment.
- **Limits:** neither the first package nor the final notebooks establish calibrated depth in metres or a complete 3D apple-tree reconstruction.

**Evidence limitation:** The individual earliest chat messages are recoverable as snippets, but their complete first message formatting/code block is not preserved as a notebook or text file. The first ZIP *is* a preserved, exact source snapshot. The complete Python diff from its `depth.py` and `evaluation.py` to the final repository versions is in the accompanying `.txt` file. This comparison does not falsely equate initial GitHub commit history with the earliest conversation.
