"""Estilos ANSI de la interfaz; nunca alteran el contenido narrativo."""

from __future__ import annotations

import os
import sys

PALETTE = {
    "default": "0",
    "red": "31",
    "yellow": "33",
    "green": "32",
    "cyan": "36",
    "blue": "34",
    "magenta": "35",
    "white": "37",
    "scene_title": "1;36",
    "description": "0",
    "person": "36",
    "portable_object": "33",
    "fixed_object": "33",
    "exit": "32",
    "action": "1;32",
    "dialogue": "35",
    "warning": "1;31",
    "debug": "2;37",
    "information": "36",
}


class Styler:
    def __init__(self, mode: str = "auto", stream=None):
        self.stream = stream or sys.stdout
        if mode == "never":
            self.enabled = False
        elif mode == "always":
            self.enabled = True
        else:
            self.enabled = (
                "NO_COLOR" not in os.environ
                and os.environ.get("TERM", "") != "dumb"
                and self.stream.isatty()
                and self._terminal_supports_ansi()
            )

    def _terminal_supports_ansi(self) -> bool:
        if os.name != "nt":
            return True
        try:
            import ctypes

            kernel = ctypes.windll.kernel32
            handle = kernel.GetStdHandle(-11)
            mode = ctypes.c_uint()
            if not kernel.GetConsoleMode(handle, ctypes.byref(mode)):
                return False
            return bool(kernel.SetConsoleMode(handle, mode.value | 0x0004))
        except (AttributeError, OSError, ValueError):
            return False

    def paint(self, role: str, value: str) -> str:
        if not self.enabled:
            return value
        return f"\x1b[{PALETTE[role]}m{value}\x1b[0m"
