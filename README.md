<div align="center">

# ⚛️ HopFold

**Continuous Hopfield Energy Landscapes for Synthetic Peptide Design**

[![Repository](https://img.shields.io/badge/GitHub-orca__prep__studio-181717?logo=github&style=flat-square)](https://github.com/asifverse4/orca_prep_studio)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white&style=flat-square)](#)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1+-EE4C2C?logo=pytorch&logoColor=white&style=flat-square)](https://pytorch.org/)
[![Animation](https://img.shields.io/badge/3D-Interactive%20Animation-8b5cf6?logo=three.js&logoColor=white&style=flat-square)](#-3d-animation-and-visualization)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)

<br/>

<!-- ================= 3D ANIMATION HERO DISPLAY ================= -->
<p align="center">
  <img src="assets/hopfold-3d.svg" alt="HopFold 3D Animated Peptide Trace" width="100%" />
</p>

<p align="center">
  <b>Heuristic peptide sequence optimization with CPU-friendly, continuous Hopfield energy descent & 3D backbone projection.</b>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-cli-usage">CLI Options</a> •
  <a href="#-3d-animation-and-visualization">3D Animation</a> •
  <a href="#-python-api">Python API</a> •
  <a href="#-scientific-notice">Scientific Notice</a>
</p>

</div>

---

> ⚠️ **Scientific & Medical Notice:** HopFold is an educational algorithm demonstration. Outputs are mathematical heuristics and are **not experimentally validated therapeutics**. Sequences, coordinates, energy minima, and microRNA-targeting biases must **not** be interpreted as biological or clinical predictions.

---

## ✨ Features

- **Continuous Hopfield Descent:** Energy minimization over modern continuous Hopfield landscapes.
- **Sequence & Structure Synthesis:** Generates synthetic peptide sequences alongside toy 3D backbone projections `(N, 3)`.
- **Interactive 3D Visualizer:** Real-time 3D camera rotation and residue path tracing.
- **GIF & MP4 Rendering:** Export animations seamlessly using Pillow or FFmpeg writers.
- **Zero Heavy GPU Requirement:** CPU-friendly, testable in headless CI/CD environments.

---

## ⚡ Quick Start

### 1. Installation

Install the core package:

```bash
pip install .
