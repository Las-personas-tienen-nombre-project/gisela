"""Fallo tipado durante creación o restauración de sesiones."""
from dataclasses import dataclass


@dataclass(frozen=True)
class EngineFailure(Exception):
    """Impide entregar una sesión inconsistente al anfitrión."""
    code: str
    message: str

    def __str__(self):
        """Mantiene un mensaje legible en las excepciones de Python."""
        return self.message
