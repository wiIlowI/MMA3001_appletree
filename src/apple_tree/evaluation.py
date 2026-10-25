"""Evaluation helpers corresponding to the MMA3001 depth-metric notebook."""

import time
import numpy as np
from .depth import make_split, make_block_split, interpolate_depth


def compare_methods(depth, train, val, test, radius=6):
    """Compare nearest and IDW methods on validation and withheld test pixels.

    Args:
        depth (ndarray): 2D raw depth-code image.
        train (ndarray): Known-pixel boolean mask.
        val (ndarray): Validation-pixel boolean mask.
        test (ndarray): Final test-pixel boolean mask.
        radius (float): Spatial prediction radius in pixels.

    Returns:
        dict: Selected method (based on validation only), along with
        RMSE, MAE, coverage, predicted count, requested count and runtime
        for each method and split. Test predictions are not used to select
        a method.
    """
    results = {}
    for method in ('nearest', 'idw'):
        results[method] = {}
        for stage, mask in (('validation', val), ('test', test)):
            start = time.perf_counter()
            pred, supported = interpolate_depth(depth, train, mask, method, radius)
            runtime = time.perf_counter() - start
            used = mask & supported
            error = pred[used] - depth[used]
            results[method][stage] = {
                'requested': int(mask.sum()),
                'predicted': int(used.sum()),
                'coverage': float(used.sum() / mask.sum()) if mask.any() else 0,
                'rmse': float(np.sqrt(np.mean(error ** 2))) if error.size else None,
                'mae': float(np.mean(np.abs(error))) if error.size else None,
                'runtime_seconds': runtime,
            }

    def score(method):
        m = results[method]['validation']
        return float('inf') if m['rmse'] is None else m['rmse'] / max(m['coverage'], 0.01)

    return {'selected_method': min(results, key=score), 'results': results}


def compare_interpolators(depth, seed=42, radius=6):
    """Evaluate nearest and IDW interpolation on random withheld pixels.

    Args:
        depth (ndarray): 2D depth-code image.
        seed (int): Reproducible random seed.
        radius (float): Prediction radius in pixels.

    Returns:
        dict: Validation-selected algorithm and per-method metrics.
    """
    train, val, test = make_split(depth, seed=seed)
    return compare_methods(depth, train, val, test, radius)


def compare_block_interpolators(depth, seed=42, radius=6):
    """Evaluate algorithms on randomly withheld 12x12 spatial blocks.

    Args:
        depth (ndarray): 2D depth-code image.
        seed (int): Reproducible random seed.
        radius (float): Prediction radius in pixels.

    Returns:
        dict: Validation-selected algorithm and per-method metrics.
    """
    train, val, test = make_block_split(depth, block_size=12, seed=seed)
    return compare_methods(depth, train, val, test, radius)
