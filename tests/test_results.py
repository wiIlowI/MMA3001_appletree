"""Check saved derived metrics match the common-support experiment contract."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def load_tables():
    d = pd.read_csv(ROOT/'results/MMA3001_appletree_depthmetric.csv')
    c = pd.read_csv(ROOT/'results/MMA3001_appletree_commonsupportmetric.csv')
    return d, c


def test_saved_tables_match_observation_keys():
    depth, common = load_tables()
    assert len(depth) == len(common) == 48
    assert depth.image.nunique() == common.image.nunique() == 12
    keys = ['image', 'design', 'method']
    assert not depth.duplicated(keys).any()
    assert not common.duplicated(keys).any()
    assert set(map(tuple, depth[keys].values)) == set(map(tuple, common[keys].values))


def test_recorded_coverage_is_in_range():
    depth, common = load_tables()
    assert depth.coverage.between(0, 1).all()
    assert common.common_fraction.between(0, 1).all()
    assert common.individual_coverage.between(0, 1).all()
    assert (common.common_fraction <= common.individual_coverage + 1e-10).all()


def test_shared_support_is_identical_for_paired_methods():
    _, common = load_tables()
    for (_, design), g in common.groupby(['image','design']):
        assert set(g.method) == {'nearest','idw'}
        assert g.common_pixels.nunique() == 1
        assert g.requested_pixels.nunique() == 1
        assert g.common_fraction.nunique() == 1
