"""Command-line interface for HopFold."""

from __future__ import annotations

import argparse
from typing import Optional, Sequence

from .designer import HopFoldEngine
from .visualizer import print_dashboard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hopfold",
        description="Hopfield-driven inverse peptide folding targeting regulatory RNA.",
    )
    parser.add_argument("--target", type=str, default="let-7", help="Target microRNA identifier")
    parser.add_argument("--length", type=int, default=18, help="Peptide length in residues")
    parser.add_argument("--steps", type=int, default=35, help="Energy gradient steps")
    parser.add_argument("--beta", type=float, default=2.5, help="Hopfield inverse temperature")
    parser.add_argument("--lr", type=float, default=0.08, help="Optimizer learning rate")
    return parser


def _validate_args(args: argparse.Namespace) -> None:
    if args.length <= 0:
        raise ValueError("--length must be positive")
    if args.steps <= 0:
        raise ValueError("--steps must be positive")
    if args.beta <= 0:
        raise ValueError("--beta must be positive")
    if args.lr <= 0:
        raise ValueError("--lr must be positive")
    if not args.target.strip():
        raise ValueError("--target must be a non-empty string")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        _validate_args(args)
    except ValueError as exc:
        parser.error(str(exc))

    engine = HopFoldEngine(state_dim=64, beta=args.beta)
    result = engine.design(length=args.length, target_mirna=args.target, steps=args.steps, lr=args.lr)

    print_dashboard(
        seq=result.sequence,
        trajectory=result.energy_trajectory,
        perplexity=result.perplexity,
        target=args.target,
        coords=result.backbone_coords,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
