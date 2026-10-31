"""GISELA sha256_counter_v1: extracción reproducible, no RNG del anfitrión.

La clase es inmutable. Un intento falla sin modificar el estado confirmado.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib

DOMAIN = b'GISELA-RNG-v1\n'
MAX_COUNTER = 9007199254740991
MAX_SIDES = 9007199254740991
SPACE = 1 << 256

@dataclass(frozen=True)
class RNGState:
    """Estado inmutable de semilla y contador para sha256_counter_v1."""
    seed: str
    counter: int = 0
    algorithm: str = 'sha256_counter_v1'

    def __post_init__(self):
        """Rechaza algoritmo, semilla o contador ajenos al perfil vigente."""
        if (self.algorithm != 'sha256_counter_v1' or
                not isinstance(self.seed, str) or len(self.seed) != 64 or
                any(c not in '0123456789abcdef' for c in self.seed) or
                type(self.counter) is not int or not 0 <= self.counter <= MAX_COUNTER):
            raise ValueError('Estado del RNG invalido')

    def as_json(self) -> dict:
        """Entrega los campos persistentes en un objeto nuevo."""
        return {'algorithm': self.algorithm, 'seed': self.seed, 'counter': self.counter}


def draw(state: RNGState, sides: int) -> tuple[int, RNGState]:
    """Entrega un entero uniforme entre 1 y sides y un estado nuevo.

    El muestreo por rechazo evita sesgo de módulo. La entrada permanece intacta
    ante éxito o error; H2 todavía no llama esta función desde los nodos.
    """
    if type(sides) is not int or not 1 <= sides <= MAX_SIDES:
        raise ValueError('sides debe ser entero entre 1 y 2^53-1')
    limit = SPACE - SPACE % sides
    counter = state.counter
    seed = bytes.fromhex(state.seed)
    while True:
        if counter >= MAX_COUNTER:
            raise OverflowError('Contador RNG agotado')
        block = hashlib.sha256(DOMAIN + seed + counter.to_bytes(8,'big')).digest()
        counter += 1
        value = int.from_bytes(block, 'big')
        if value < limit:
            return 1 + value % sides, RNGState(seed=state.seed, counter=counter)
