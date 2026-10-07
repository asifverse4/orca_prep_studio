# ORCA Prep Studio

<p align="center">
	<img src="assets/orca-orbit.svg" alt="Animated molecular orbit showing an ORCA input workflow" width="900">
</p>

<p align="center"><strong>Prepare once. Submit everywhere.</strong><br>
A small desktop studio for turning XYZ geometries into ready-to-run ORCA inputs and HPC job scripts.</p>

<p align="center">
	<img src="https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.9 or newer">
	<img src="https://img.shields.io/badge/UI-Tkinter-2C3E50?style=flat-square" alt="Tkinter UI">
	<img src="https://img.shields.io/badge/ORCA-input%20builder-0D9488?style=flat-square" alt="ORCA input builder">
</p>

## What it does

ORCA Prep Studio keeps the repetitive setup work in one focused window:

- Load one `.xyz` file or an entire folder for batch preparation.
- Choose job type, method, basis set, dispersion, solvation, charge, and multiplicity.
- Add frozen atoms and extra ORCA keywords when a calculation needs more control.
- Generate `.inp` files plus optional SLURM or PBS scripts.
- Create a `submit_all.sh` launcher for batch jobs.

## Run it

Python's standard library is the only dependency.

```bash
python prep_studio.py
```

On Linux, install Tkinter first if your Python distribution does not include it:

```bash
sudo apt install python3-tk
```

## Workflow

1. Choose **Single XYZ** for one molecule or **Batch Folder** for several `.xyz` files.
2. Set the molecular properties and calculation parameters.
3. Select **SLURM**, **PBS**, or **None** under HPC Submission.
4. Click **Generate Inputs & Scripts**.

Generated files are written beside the source geometry. A single job produces `<name>.inp` and, when enabled, `<name>.sh`. A batch run also produces `submit_all.sh`.

## XYZ format

The loader expects a standard XYZ file: atom count on line one, an optional comment on line two, then one atom and three coordinates per line.

```text
3
water
O  0.000000  0.000000  0.000000
H  0.758602  0.000000  0.504284
H -0.758602  0.000000  0.504284
```

## Notes

- The generated scripts assume an `orca` executable is available on the cluster path, or at the custom path entered in the UI.
- `module load orca` is included in generated SLURM and PBS scripts so it can be adjusted to match the local cluster module name.
- The tool generates input and submission files; it does not launch ORCA itself.