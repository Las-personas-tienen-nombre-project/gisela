"""DICE: evaluador matemático independiente de motores, atributos y rasgos."""
from .core import DiceError, compile_profile, evaluate
__all__ = ('DiceError', 'compile_profile', 'evaluate')
