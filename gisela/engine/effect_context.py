"""Contexto explícito de una operación causal, sin autoridad de commit."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class EffectContext:
    """Agrupa fuente, decisiones y definiciones sin parámetros posicionales."""
    source: str
    decisions: object = None
    definitions: object = None
