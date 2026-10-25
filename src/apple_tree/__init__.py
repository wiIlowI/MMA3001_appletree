"""Numerical depth-code interpolation methods for the MMA3001 apple-tree study.

The depth values are uncalibrated sensor image codes, not metres.
"""
from .depth import make_split, make_block_split, interpolate_depth

__all__ = ['make_split', 'make_block_split', 'interpolate_depth']
