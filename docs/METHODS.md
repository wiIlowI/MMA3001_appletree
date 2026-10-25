# Numerical methods and validation

The four Colab notebooks implement numerical interpolation on **raw 8-bit depth
image codes**, not metric depth measurements. The extracted source package under
`src/apple_tree/` contains matching reusable implementations with docstrings.

## Splits

For random pixels, valid locations (assumed to have code >0) are permuted using
seed=42. About 5% are validation, 5% test and the remainder training.

For spatial blocks, candidate non-overlapping 12x12 pixel tiles require >=50%
positive-coded pixels. About 5% of eligible tiles are chosen for validation,
5% for testing; only valid pixel positions within each tile are withheld.

All methods use the same split for a given image and design. These are
within-image holdouts, not independent depth ground-truth measurements.

## Interpolation

* Nearest neighbour: Euclidean distance transform to the nearest training pixel.
* IDW: up to 8 nearest training pixels within Euclidean radius 6 pixels,
  weighted by 1/max(distance, 1e-10)^2.
* A query is unsupported when no training sample lies within the radius.
* Validation RMSE divided by max(coverage, 0.01) ranks methods; reported final
  metrics use untouched test pixels.

## Fair comparison

Original metrics score each method on its *own* supported withheld pixels.
Common-support metrics use the intersection of supported test pixels for both
methods, while retaining individual prediction coverage. This reduces selective
coverage bias.

## Limitations

8-bit code value zero is provisionally invalid; this assumption is not certified.
RGB/Depth optical registration and GT annotation meaning are not verified.
Results do not establish 3D reconstruction, skeleton accuracy, or metric depth.
The 12 observations cover six tree IDs and both seasons; they do not represent
12 independent trees or the entire inventory statistically.
