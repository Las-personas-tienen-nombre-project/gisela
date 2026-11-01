"""TRAITS: Trait Rules and Attribute Interaction Tracking System."""

from .contracts import TraitsError, compile_catalog, has_trait, validate_assignments
from .evaluator import evaluate

__all__ = (
    "TraitsError",
    "compile_catalog",
    "evaluate",
    "has_trait",
    "validate_assignments",
)
