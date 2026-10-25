"""Validate the paired output tables and selected observation counts."""
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
d = pd.read_csv(ROOT/'results/MMA3001_appletree_depthmetric.csv')
c = pd.read_csv(ROOT/'results/MMA3001_appletree_commonsupportmetric.csv')
keys = ['image','design','method']
assert len(d) == len(c) == 48
assert d.image.nunique() == c.image.nunique() == 12
assert not d.duplicated(keys).any() and not c.duplicated(keys).any()
assert set(map(tuple,d[keys].values)) == set(map(tuple,c[keys].values))
assert d[['rmse','mae','coverage']].notna().all().all()
assert c[['shared_rmse','shared_mae','common_fraction','individual_coverage']].notna().all().all()
assert ((d.coverage >= 0) & (d.coverage <= 1)).all()
assert ((c.common_fraction >= 0) & (c.common_fraction <= 1)).all()
print('PASS: two paired tables, 48 rows each, 12 distinct images, valid metrics.')
