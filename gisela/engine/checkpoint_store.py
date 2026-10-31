"""Almacenamiento local confiable para estado y recibos en un solo reemplazo.

Bloqueo POSIX exclusivo durante toda la vida del gateway; no es un protocolo
entre servicios remotos ni sustituye autenticación del directorio del anfitrión.
"""
from __future__ import annotations
import fcntl
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

MAX_BYTES = 64 * 1024 * 1024


def _unique_pairs(pairs):
    """Rechaza claves JSON duplicadas en almacenamiento persistente."""
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Clave JSON duplicada')
        value[key] = item
    return value


class StoreFailure(OSError):
    """Fallo de escritura; uncertain indica posible reemplazo ya realizado."""
    def __init__(self, message: str, uncertain: bool = False):
        super().__init__(message)
        self.uncertain = uncertain


class JsonCheckpointStore:
    """Checkpoint íntegro con bloqueo no bloqueante y escritura atómica."""
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._lock_file = None

    def claim(self) -> None:
        """Adquiere exclusión también entre procesos de un mismo anfitrión."""
        if self._lock_file is not None:
            raise StoreFailure('El almacenamiento ya está reclamado')
        if not self.path.parent.is_dir():
            raise StoreFailure('Directorio de checkpoint inexistente')
        lock = self.path.with_name(self.path.name + '.lock')
        fd = os.open(lock, os.O_CREAT | os.O_RDWR, 0o600)
        self._lock_file = os.fdopen(fd, 'rb+')
        try:
            fcntl.flock(self._lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.release()
            raise StoreFailure('Checkpoint abierto por otro proceso') from None

    def release(self) -> None:
        if self._lock_file is not None:
            fcntl.flock(self._lock_file, fcntl.LOCK_UN)
            self._lock_file.close()
            self._lock_file = None

    def load(self) -> dict | None:
        """No asume que los contenidos de un fichero alterado sean confiables."""
        if self._lock_file is None:
            raise StoreFailure('Falta bloqueo de checkpoint')
        if not self.path.exists():
            return None
        try:
            if self.path.stat().st_size > MAX_BYTES:
                raise StoreFailure('Checkpoint excede presupuesto')
            return json.loads(self.path.read_text(encoding='utf-8'),
                              object_pairs_hook=_unique_pairs,
                              parse_constant=lambda _: (_ for _ in ()).throw(ValueError('No finito')))
        except (ValueError, OSError) as exc:
            raise StoreFailure('Checkpoint ilegible') from exc

    def save(self, document: dict) -> None:
        """Confirma estado y recibos en el mismo archivo; fsync y rename."""
        if self._lock_file is None:
            raise StoreFailure('Falta bloqueo de checkpoint')
        encoded = json.dumps(document, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode('utf-8')
        if len(encoded) > MAX_BYTES:
            raise StoreFailure('Checkpoint excede presupuesto')
        temporary = None
        replaced = False
        try:
            with NamedTemporaryFile(dir=self.path.parent, prefix='.gisela_',
                                    delete=False) as stream:
                temporary = Path(stream.name)
                os.chmod(stream.name, 0o600)
                stream.write(encoded)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
            replaced = True
            directory = os.open(self.path.parent, os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        except OSError as exc:
            raise StoreFailure('Fallo de almacenamiento', uncertain=replaced) from exc
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
