"""HopFold: modern Hopfield inverse folding and peptide design."""

from .core import ContinuousHopfieldMemory
from .designer import DesignResult, HopFoldEngine

__version__ = "0.1.0"

__all__ = ["ContinuousHopfieldMemory", "HopFoldEngine", "DesignResult"]
