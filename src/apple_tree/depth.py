"""Numerical functions used in the depth and common-support notebooks.

Algorithms and defaults correspond to the final Colab notebooks:
random 5% validation/5% test; 12x12 spatial blocks; radius 6 pixels;
nearest-neighbour or inverse-distance weighting with up to 8 neighbours.

The value zero is assumed to indicate invalid depth. This assumption and
the physical depth scale were not verified against camera documentation.
"""

import numpy as np
from scipy.ndimage import distance_transform_edt
from scipy.spatial import cKDTree


def make_split(depth, seed=42, block_size=None):
    """Create non-overlapping training, validation and test masks.

    Args:
        depth (ndarray): Two-dimensional depth image with zero as invalid.
        seed (int): Seed controlling repeatable random selection.
        block_size (int or None): If None, hold out random valid pixels.
            Otherwise, hold out square blocks with at least 50% valid pixels.

    Returns:
        tuple[ndarray, ndarray, ndarray]: Boolean (train, val, test)
        masks, each the same shape as ``depth``. Validation/test use
        approximately 5% each of valid pixels or eligible blocks.

    Notes:
        This is deterministic for a fixed image and random seed. It is
        not a split into independent trees; each mask is drawn within
        one individual depth image.
    """
    valid = np.asarray(depth) > 0

    if block_size is None:
        positions = np.argwhere(valid)
    else:
        if block_size < 1:
            raise ValueError('block_size must be positive')
        h, w = valid.shape
        positions = [
            (y, x)
            for y in range(0, h - block_size + 1, block_size)
            for x in range(0, w - block_size + 1, block_size)
            if valid[y:y + block_size, x:x + block_size].mean() >= 0.5
        ]
        positions = np.asarray(positions)

    order = np.random.default_rng(seed).permutation(len(positions))
    n = max(1, int(len(positions) * 0.05))
    val = np.zeros(valid.shape, dtype=bool)
    test = np.zeros(valid.shape, dtype=bool)

    for mask, chosen in ((val, order[:n]), (test, order[n:2 * n])):
        for i in chosen:
            y, x = positions[i]
            if block_size is None:
                mask[y, x] = True
            else:
                mask[y:y + block_size, x:x + block_size] = True

    val &= valid
    test &= valid
    return valid & ~val & ~test, val, test


def make_block_split(depth, block_size=12, seed=42):
    """Make a spatially blocked split using square regions.

    Args:
        depth (ndarray): Two-dimensional depth-code image.
        block_size (int): Side length of withheld blocks, in pixels.
        seed (int): Random seed used to select blocks.

    Returns:
        tuple[ndarray, ndarray, ndarray]: Train, validation, test masks.
    """
    return make_split(depth, seed=seed, block_size=block_size)


def interpolate_depth(depth, train, query, method='nearest', radius=6):
    """Predict withheld depth codes using nearby observed depth pixels.

    Args:
        depth (ndarray): Two-dimensional image containing numeric depth codes.
        train (ndarray): Boolean mask of known pixels used as input.
        query (ndarray): Boolean mask of pixels to predict.
        method (str): ``'nearest'`` or ``'idw'`` (inverse distance squared).
        radius (float): Maximum Euclidean search distance, in pixels.

    Returns:
        tuple[ndarray, ndarray]: Float-valued predictions, with NaN at
        unsupported locations, and a boolean prediction-support mask.

    Raises:
        ValueError: For unsupported interpolation methods or invalid radius.

    Notes:
        IDW uses up to 8 nearest known pixels and weights proportional
        to 1 / distance**2. Nearest uses an Euclidean distance transform.
        Neither operation converts raw depth codes into metric distances.
    """
    if radius <= 0:
        raise ValueError('radius must be positive')
    if method not in ('nearest', 'idw'):
        raise ValueError('method must be nearest or idw')

    depth = np.asarray(depth)
    train = np.asarray(train, dtype=bool)
    query = np.asarray(query, dtype=bool)
    if depth.ndim != 2 or train.shape != depth.shape or query.shape != depth.shape:
        raise ValueError('depth, train and query must have matching 2D shapes')

    prediction = np.full(depth.shape, np.nan)
    supported = np.zeros(depth.shape, dtype=bool)
    if not train.any() or not query.any():
        return prediction, supported

    if method == 'nearest':
        distances, indices = distance_transform_edt(~train, return_indices=True)
        supported = query & (distances <= radius)
        prediction[supported] = depth[
            tuple(index[supported] for index in indices)
        ]

    else:
        known = np.argwhere(train)
        targets = np.argwhere(query)
        k = min(8, len(known))
        distances, indices = cKDTree(known).query(
            targets, k=k, distance_upper_bound=radius
        )
        if k == 1:
            distances = distances[:, None]
            indices = indices[:, None]

        ok = np.isfinite(distances) & (indices < len(known))
        weights = np.zeros_like(distances)
        weights[ok] = 1 / np.maximum(distances[ok], 1e-10) ** 2
        nearby = np.zeros_like(weights)
        nearby[ok] = depth[train][indices[ok]]

        total = weights.sum(axis=1)
        found = total > 0
        y, x = targets[found].T
        prediction[y, x] = (
            (nearby[found] * weights[found]).sum(axis=1) / total[found]
        )
        supported[y, x] = True

    return prediction, supported
