<div align="center">

# ⚛️ HopFold

**Continuous Hopfield Energy Landscapes for Synthetic Peptide Design**

[![Repository](https://img.shields.io/badge/GitHub-asifverse4%2Forca__prep__studio-181717?logo=github)](https://github.com/asifverse4/orca_prep_studio)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-brightgreen.svg)](#)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1+-ee4c2c.svg)](https://pytorch.org/)

</div>

HopFold is a CPU-friendly Python package that demonstrates how continuous Hopfield energy descent can be used to generate **synthetic, heuristic** peptide candidates and toy backbone projections.

> ⚠️ **Scientific limitation**: Outputs are computational heuristics for experimentation and software demos. They are **not** experimentally validated therapeutics, and the microRNA-targeting/structure signals are synthetic proxies.

## Installation

From this repository:

```bash
pip install .
```

Or editable mode for development:

```bash
pip install -e .
```

Dependencies are intentionally minimal:

- torch
- numpy
- rich

## CLI Usage

After installation, run:

```bash
hopfold --target let-7 --length 18 --steps 35 --beta 2.5 --lr 0.08
```

### CLI options

- `--target`: target microRNA label (heuristic bias only)
- `--length`: peptide length (>0)
- `--steps`: optimization steps (>0)
- `--beta`: Hopfield inverse temperature (>0)
- `--lr`: optimizer learning rate (>0)

The CLI prints a Rich dashboard with sequence summary and ASCII backbone projection.

## Python API

```python
from hopfold.designer import HopFoldEngine

engine = HopFoldEngine(state_dim=64, beta=2.5)
result = engine.design(length=16, target_mirna="let-7", steps=40, lr=0.08)

print(result.sequence)
print(result.final_energy)
print(result.backbone_coords.shape)  # (length, 3)
```

## Testing

Run tests with:

```bash
pytest -q
```

Test coverage includes:

- Hopfield energy descent behavior
- Designer output validity and input validation
- Visualizer handling of empty/degenerate coordinates
- CLI argument validation behavior

## Project layout

```text
hopfold/
├── pyproject.toml
├── requirements.txt
├── hopfold/
│   ├── __init__.py
│   ├── core.py
│   ├── designer.py
│   ├── visualizer.py
│   └── cli.py
└── tests/
    └── test_hopfold.py
```
