"""Regenerate MMA3001 figures from the published derived metric CSVs.

From the repository root, run: python scripts/plot_results.py
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'results'
FIGURES = RESULTS / 'figures'
FIGURES.mkdir(exist_ok=True)

depth = pd.read_csv(RESULTS / 'MMA3001_appletree_depthmetric.csv')
common = pd.read_csv(RESULTS / 'MMA3001_appletree_commonsupportmetric.csv')
assert len(depth) == len(common) == 48
assert set(zip(depth.image, depth.design, depth.method)) == set(zip(common.image, common.design, common.method))

cols = ['design', 'method']
depth_summary = depth.groupby(cols)[['rmse', 'mae', 'coverage', 'runtime_seconds']].median().round(4)
common_summary = common.groupby(cols)[['shared_rmse', 'shared_mae', 'common_fraction', 'individual_coverage']].median().round(4)
depth_summary.to_csv(FIGURES / 'depth_summary.csv')
common_summary.to_csv(FIGURES / 'commonsupport_summary.csv')

for metric, title, filename in [('shared_rmse','Common-support RMSE','common_rmse.png'),
                                 ('shared_mae','Common-support MAE','common_mae.png')]:
    table = common.pivot_table(index='design', columns='method', values=metric, aggfunc='median')
    ax = table.plot(kind='bar', figsize=(7.2,4.3))
    ax.set(title=title, xlabel='Test design', ylabel='Error (raw depth codes)')
    ax.tick_params(axis='x', rotation=0)
    plt.tight_layout(); plt.savefig(FIGURES / filename, dpi=200); plt.close()

coverage = depth.pivot_table(index='design', columns='method', values='coverage', aggfunc='median') * 100
ax = coverage.plot(kind='bar', figsize=(7.2,4.3))
ax.set(title='Prediction coverage', xlabel='Test design', ylabel='Withheld pixels predicted (%)', ylim=(0,105))
ax.tick_params(axis='x', rotation=0)
plt.tight_layout(); plt.savefig(FIGURES / 'coverage.png', dpi=200); plt.close()

runtime = depth.pivot_table(index='design', columns='method', values='runtime_seconds', aggfunc='median') * 1000
ax = runtime.plot(kind='bar', figsize=(7.2,4.3))
ax.set(title='Median computation time', xlabel='Test design', ylabel='Time (milliseconds)')
ax.tick_params(axis='x', rotation=0)
plt.tight_layout(); plt.savefig(FIGURES / 'runtime.png', dpi=200); plt.close()

blocked = common[common.design == 'spatial_blocks_12']
seasonal = blocked.pivot_table(index='season', columns='method', values='shared_rmse', aggfunc='median')
ax = seasonal.plot(kind='bar', figsize=(7.2,4.3))
ax.set(title='Spatial-block RMSE by season', xlabel='Season', ylabel='Common-support RMSE (raw depth codes)')
ax.tick_params(axis='x', rotation=0)
plt.tight_layout(); plt.savefig(FIGURES / 'seasonal_rmse.png', dpi=200); plt.close()

print('Created 5 figures and 2 summary CSVs in', FIGURES)
print('Depth metrics:\n', depth_summary)
print('Common-support:\n', common_summary)
