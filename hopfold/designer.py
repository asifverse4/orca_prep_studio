"""Peptide design engine built on continuous Hopfield dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import torch
from torch import nn
import torch.nn.functional as F

from .core import ContinuousHopfieldMemory

AMINO_ACIDS = list("ACDEFGHIKLMNPQRSTVWY")
AA_TO_IDX = {aa: i for i, aa in enumerate(AMINO_ACIDS)}
IDX_TO_AA = {i: aa for i, aa in enumerate(AMINO_ACIDS)}

MIRNA_SEED_TARGETS = {
    "let-7": "CUACCUCA",
    "mir-21": "UAGCUUA",
    "mir-155": "UAAUGCU",
}


@dataclass
class DesignResult:
    sequence: str
    energy_trajectory: List[float]
    final_energy: float
    perplexity: float
    backbone_coords: torch.Tensor


class HopFoldEngine(nn.Module):
    """Integrates Hopfield memory dynamics with synthetic peptide constraints."""

    def __init__(self, state_dim: int = 64, beta: float = 2.5):
        super().__init__()
        if state_dim <= 0:
            raise ValueError("state_dim must be positive")
        if beta <= 0:
            raise ValueError("beta must be positive")

        self.state_dim = int(state_dim)
        self.hopfield = ContinuousHopfieldMemory(state_dim=self.state_dim, beta=beta)
        self.to_logits = nn.Linear(self.state_dim, len(AMINO_ACIDS))
        self.from_seq = nn.Linear(len(AMINO_ACIDS), self.state_dim)

    def _validate_design_args(self, length: int, target_mirna: str, steps: int, lr: float) -> None:
        if length <= 0:
            raise ValueError("length must be a positive integer")
        if steps <= 0:
            raise ValueError("steps must be a positive integer")
        if lr <= 0:
            raise ValueError("lr must be positive")
        if not isinstance(target_mirna, str) or not target_mirna.strip():
            raise ValueError("target_mirna must be a non-empty string")

    def _mirna_complementarity_penalty(self, seq_logits: torch.Tensor, target_mirna: str) -> torch.Tensor:
        probs = F.softmax(seq_logits, dim=-1)
        pos_indices = [AA_TO_IDX[a] for a in "RK"]
        aro_indices = [AA_TO_IDX[a] for a in "YWF"]

        cationic_density = probs[..., pos_indices].sum(dim=-1).mean()
        aromatic_density = probs[..., aro_indices].sum(dim=-1).mean()

        target_len = len(MIRNA_SEED_TARGETS.get(target_mirna.lower(), "UAGCUUA"))
        target_cationic_bias = min(0.4, target_len * 0.04)
        penalty = (cationic_density - target_cationic_bias) ** 2 + (aromatic_density - 0.2) ** 2
        return penalty * 10.0

    def generate_backbone_coordinates(self, state: torch.Tensor) -> torch.Tensor:
        """Generate synthetic (N, 3) C-alpha-like backbone coordinates."""
        if state.ndim != 2:
            raise ValueError("state must be 2D with shape (length, state_dim)")
        if state.shape[-1] < 3:
            raise ValueError("state_dim must be >= 3 for coordinate generation")
        length = state.size(0)
        if length == 0:
            return torch.empty((0, 3), dtype=state.dtype, device=state.device)

        t = torch.linspace(0, 4 * torch.pi, length, dtype=state.dtype, device=state.device)
        latent_shift = torch.tanh(state[:, :3])
        x = 5.0 * torch.cos(t) + latent_shift[:, 0]
        y = 5.0 * torch.sin(t) + latent_shift[:, 1]
        z = torch.linspace(0, length * 1.5, length, dtype=state.dtype, device=state.device) + latent_shift[:, 2]
        return torch.stack([x, y, z], dim=-1)

    def design(self, length: int = 16, target_mirna: str = "let-7", steps: int = 40, lr: float = 0.08) -> DesignResult:
        """Inverse-fold an amino acid sequence via energy descent."""
        self._validate_design_args(length=length, target_mirna=target_mirna, steps=steps, lr=lr)

        state = torch.randn(length, self.state_dim, requires_grad=True)
        optimizer = torch.optim.AdamW([state], lr=lr, weight_decay=1e-4)

        trajectory: List[float] = []
        for _ in range(steps):
            optimizer.zero_grad()
            h_energy = self.hopfield.energy(state).mean()
            logits = self.to_logits(state)
            r_penalty = self._mirna_complementarity_penalty(logits, target_mirna)

            probs = F.softmax(logits, dim=-1)
            mean_dist = probs.mean(dim=0)
            entropy_loss = torch.sum(mean_dist * torch.log(mean_dist + 1e-9))

            total_loss = h_energy + r_penalty + 0.3 * entropy_loss
            total_loss.backward()
            optimizer.step()
            trajectory.append(float(total_loss.item()))

        with torch.no_grad():
            final_logits = self.to_logits(state)
            chosen_indices = torch.argmax(final_logits, dim=-1)
            sequence = "".join(IDX_TO_AA[idx.item()] for idx in chosen_indices)
            probs = F.softmax(final_logits, dim=-1)
            log_p = F.log_softmax(final_logits, dim=-1)
            token_entropies = -(probs * log_p).sum(dim=-1)
            perplexity = float(torch.exp(token_entropies.mean()).item())
            coords = self.generate_backbone_coordinates(state)

        return DesignResult(
            sequence=sequence,
            energy_trajectory=trajectory,
            final_energy=trajectory[-1],
            perplexity=perplexity,
            backbone_coords=coords,
        )
