"""Small known-answer tests for numerical depth interpolation.

Run with: python -m pytest -q
"""

import numpy as np
import pytest

from apple_tree.depth import make_split, make_block_split, interpolate_depth
from apple_tree.evaluation import compare_interpolators


def test_nearest_known_value():
    depth = np.zeros((5, 5), dtype=float)
    depth[2, 2] = 17
    train = depth > 0
    query = np.zeros(depth.shape, dtype=bool)
    query[2, 3] = True
    pred, supported = interpolate_depth(depth, train, query, 'nearest', radius=2)
    assert supported[2, 3]
    assert pred[2, 3] == 17
    assert np.isnan(pred[0, 0])


def test_idw_midpoint_average():
    depth = np.zeros((5, 5), dtype=float)
    depth[2, 1], depth[2, 3] = 10, 30
    train = depth > 0
    query = np.zeros(depth.shape, dtype=bool)
    query[2, 2] = True
    pred, supported = interpolate_depth(depth, train, query, 'idw', radius=1.5)
    assert supported[2, 2]
    assert pred[2, 2] == pytest.approx(20)


@pytest.mark.parametrize('method', ['nearest', 'idw'])
def test_radius_limits_prediction(method):
    depth = np.zeros((7, 7), dtype=float)
    depth[0, 0] = 10
    train = depth > 0
    query = np.zeros(depth.shape, dtype=bool)
    query[6, 6] = True
    pred, supported = interpolate_depth(depth, train, query, method, radius=2)
    assert not supported[6, 6]
    assert np.isnan(pred[6, 6])


def test_random_split_disjoint_reproducible():
    depth = np.full((30, 30), 50, dtype=np.uint8)
    depth[0, :] = 0
    one = make_split(depth, seed=42)
    two = make_split(depth, seed=42)
    for a, b in zip(one, two):
        assert np.array_equal(a, b)
    train, val, test = one
    assert not (train & val).any()
    assert not (train & test).any()
    assert not (val & test).any()
    assert not (train | val | test)[0].any()
    assert np.array_equal(train | val | test, depth > 0)


def test_block_split_disjoint_and_deterministic():
    depth = np.full((60, 60), 12, dtype=np.uint8)
    depth[0, :] = 0
    a = make_block_split(depth, block_size=10, seed=42)
    b = make_block_split(depth, block_size=10, seed=42)
    for first, second in zip(a, b):
        assert np.array_equal(first, second)
    train, val, test = a
    assert val.any() and test.any()
    assert not (train & val).any()
    assert not (train & test).any()
    assert not (val & test).any()
    assert np.array_equal(train | val | test, depth > 0)


@pytest.mark.parametrize('method', ['nearest', 'idw'])
def test_no_training_pixels_unsupported(method):
    depth = np.ones((5, 5))
    train = np.zeros((5, 5), dtype=bool)
    query = np.ones((5, 5), dtype=bool)
    pred, supported = interpolate_depth(depth, train, query, method)
    assert not supported.any()
    assert np.isnan(pred).all()


def test_reject_unknown_method():
    depth = np.ones((3, 3))
    mask = np.ones((3, 3), dtype=bool)
    with pytest.raises(ValueError):
        interpolate_depth(depth, mask, mask, method='linear')


def test_reject_invalid_radius():
    depth = np.ones((3, 3))
    mask = np.ones((3, 3), dtype=bool)
    with pytest.raises(ValueError):
        interpolate_depth(depth, mask, mask, radius=0)


def test_comparison_contains_metrics_and_selection():
    depth = np.arange(1, 1 + 40 * 40, dtype=float).reshape(40, 40)
    report = compare_interpolators(depth, seed=42, radius=6)
    assert report['selected_method'] in ('nearest', 'idw')
    for method in ('nearest', 'idw'):
        for stage in ('validation', 'test'):
            metrics = report['results'][method][stage]
            assert metrics['requested'] > 0
            assert 0 <= metrics['coverage'] <= 1
            assert metrics['rmse'] is not None
            assert metrics['mae'] is not None
