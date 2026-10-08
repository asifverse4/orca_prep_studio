import pytest
import torch

from hopfold.cli import main
from hopfold.core import ContinuousHopfieldMemory
from hopfold.designer import AMINO_ACIDS, HopFoldEngine
from hopfold.visualizer import render_ascii_backbone


def test_hopfield_energy_generally_decreases_with_descent() -> None:
    torch.manual_seed(0)
    memory = ContinuousHopfieldMemory(state_dim=32, num_memories=16, beta=2.0)
    state = torch.randn(8, 32, requires_grad=True)
    optimizer = torch.optim.SGD([state], lr=0.1)

    energies = []
    for _ in range(12):
        optimizer.zero_grad()
        loss = memory.energy(state).sum()
        loss.backward()
        optimizer.step()
        energies.append(float(loss.item()))

    assert energies[-1] < energies[0]


def test_designer_output_validity() -> None:
    torch.manual_seed(1)
    engine = HopFoldEngine(state_dim=32, beta=1.5)
    length = 12
    steps = 10
    result = engine.design(length=length, target_mirna="let-7", steps=steps, lr=0.06)

    assert len(result.sequence) == length
    assert all(aa in AMINO_ACIDS for aa in result.sequence)
    assert len(result.energy_trajectory) == steps
    assert result.backbone_coords.shape == (length, 3)
    assert result.perplexity > 0


def test_invalid_design_input_rejected() -> None:
    engine = HopFoldEngine(state_dim=16, beta=1.2)
    with pytest.raises(ValueError, match="length"):
        engine.design(length=0)
    with pytest.raises(ValueError, match="steps"):
        engine.design(length=8, steps=0)


def test_visualizer_handles_empty_and_degenerate_coords() -> None:
    empty = torch.empty((0, 3))
    art = render_ascii_backbone(empty, width=7, height=3)
    rows = art.splitlines()
    assert len(rows) == 3
    assert all(len(row) == 7 for row in rows)

    degenerate = torch.tensor([[1.0, 1.0, 1.0], [1.0, 1.0, 1.0]])
    art2 = render_ascii_backbone(degenerate, width=10, height=4)
    assert "@" in art2
    assert "#" in art2


def test_visualizer_invalid_shape_rejected() -> None:
    with pytest.raises(ValueError, match="shape"):
        render_ascii_backbone(torch.randn(3, 2))


def test_cli_rejects_invalid_length() -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--length", "0"])
    assert exc.value.code == 2
