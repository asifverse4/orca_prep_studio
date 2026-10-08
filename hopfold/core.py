"""Core continuous Hopfield memory module."""

from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class ContinuousHopfieldMemory(nn.Module):
    r"""Continuous modern Hopfield network as an associative energy landscape.

    E(z) = - (1 / beta) * logsumexp(beta * Mz) + (1 / 2) * ||z||^2
    """

    def __init__(self, state_dim: int = 64, num_memories: int = 128, beta: float = 1.0):
        super().__init__()
        if state_dim <= 0:
            raise ValueError("state_dim must be positive")
        if num_memories <= 0:
            raise ValueError("num_memories must be positive")
        if beta <= 0:
            raise ValueError("beta must be positive")

        self.state_dim = int(state_dim)
        self.num_memories = int(num_memories)
        self.beta = float(beta)

        raw_memory = torch.randn(self.num_memories, self.state_dim)
        self.memory_bank = nn.Parameter(F.normalize(raw_memory, p=2, dim=-1, eps=1e-12))

    def _validate_state_shape(self, state: torch.Tensor) -> None:
        if state.ndim == 0:
            raise ValueError("state must have at least one dimension")
        if state.shape[-1] != self.state_dim:
            raise ValueError(f"state last dimension must be {self.state_dim}, got {state.shape[-1]}")

    def energy(self, state: torch.Tensor) -> torch.Tensor:
        """Compute per-sample Hopfield energy."""
        self._validate_state_shape(state)
        norm_state = F.normalize(state, p=2, dim=-1, eps=1e-12)
        affinity = torch.matmul(norm_state, self.memory_bank.T) * self.beta
        lse = torch.logsumexp(affinity, dim=-1)
        quadratic = 0.5 * torch.sum(state * state, dim=-1)
        return -(1.0 / self.beta) * lse + quadratic

    def retrieve(self, query: torch.Tensor) -> torch.Tensor:
        """Single-step synchronous continuous attractor update."""
        self._validate_state_shape(query)
        norm_q = F.normalize(query, p=2, dim=-1, eps=1e-12)
        scores = F.softmax(self.beta * torch.matmul(norm_q, self.memory_bank.T), dim=-1)
        return torch.matmul(scores, self.memory_bank)
