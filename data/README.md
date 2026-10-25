# Restricted RGB-D apple-tree dataset

The full dataset is stored in an access controlled Google
Drive folder named TreeID, containing Dataset and Dataset (With Summer GT).
This repository does not include source RGB-D or GT PNGs,
inventory.csv, original Drive file identifiers, or the dataset ZIP.

To reproduce the raw-image experiments:
1. Obtain permission to access TreeID.
2. Open notebooks/1_Dataset.ipynb in Google Colab and authenticate
3. Run all its cells to generate and download MMA3001_appletree_dataset.zip locally. This is an evidence packet, not a full copy of the original dataset.
4. Run notebooks 2 and 3 in Colab, uploading that dataset ZIP when asked, and authenticate with the same permitted account to fetch 12 selected D PNGs.
5. Download the generated CSVs and run notebook 4 using those two CSVs.

No camera intrinsics, depth scale or definitive annotation meanings are supplied
with the saved outputs. Zero depth is invalid, not verified.
