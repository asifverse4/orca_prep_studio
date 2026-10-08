"""ASCII visualization and rich dashboard output for HopFold."""

from __future__ import annotations

from typing import Sequence, Union

import numpy as np
import torch
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

ArrayLike = Union[np.ndarray, torch.Tensor, Sequence[Sequence[float]]]


def _to_numpy_coords(coords: ArrayLike) -> np.ndarray:
    if isinstance(coords, torch.Tensor):
        arr = coords.detach().cpu().numpy()
    else:
        arr = np.asarray(coords, dtype=float)

    if arr.ndim != 2 or arr.shape[-1] != 3:
        raise ValueError("coords must have shape (N, 3)")
    return arr


def render_ascii_backbone(coords: ArrayLike, width: int = 50, height: int = 12) -> str:
    """Project 3D C-alpha coordinates onto a 2D ASCII terminal canvas."""
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")

    coord_array = _to_numpy_coords(coords)
    if coord_array.shape[0] == 0:
        return "\n".join(" " * width for _ in range(height))

    proj_x = coord_array[:, 0] * 0.707 - coord_array[:, 1] * 0.707
    proj_y = coord_array[:, 0] * 0.408 + coord_array[:, 1] * 0.408 - coord_array[:, 2] * 0.816

    min_x, max_x = float(np.min(proj_x)), float(np.max(proj_x))
    min_y, max_y = float(np.min(proj_y)), float(np.max(proj_y))

    range_x = max(max_x - min_x, 1e-8)
    range_y = max(max_y - min_y, 1e-8)

    grid = [[" " for _ in range(width)] for _ in range(height)]

    for idx, (px, py) in enumerate(zip(proj_x, proj_y)):
        col = int((px - min_x) / range_x * (width - 1))
        row = int((py - min_y) / range_y * (height - 1))
        col = max(0, min(width - 1, col))
        row = max(0, min(height - 1, row))

        if idx == 0:
            char = "@"
        elif idx == len(coord_array) - 1:
            char = "#"
        else:
            char = "*"
        grid[row][col] = char

    return "\n".join("".join(r) for r in grid)


def print_dashboard(seq: str, trajectory: Sequence[float], perplexity: float, target: str, coords: ArrayLike) -> None:
    """Render the execution dashboard via Rich."""
    ascii_art = render_ascii_backbone(coords)

    table = Table(title="HopFold Optimization Summary", expand=True)
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Designed Sequence", f"[bold green]{seq}[/bold green]")
    table.add_row("Peptide Length", str(len(seq)))
    table.add_row("microRNA Target", target)
    if trajectory:
        table.add_row("Initial Energy", f"{trajectory[0]:.4f}")
        table.add_row("Final Hopfield Energy", f"{trajectory[-1]:.4f}")
    else:
        table.add_row("Initial Energy", "n/a")
        table.add_row("Final Hopfield Energy", "n/a")
    table.add_row("Sequence Perplexity", f"{perplexity:.2f}")

    console.print(Panel(ascii_art, title="3D Projected C-alpha Trace", border_style="green"))
    console.print(table)
