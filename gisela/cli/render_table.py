"""Accessible fixed-width rendering of validated, projected public tables."""

from __future__ import annotations


def show_table(region: dict, indent: str = "") -> None:
    headers = region.get("headers", [])
    rows = region.get("rows", [])
    if not headers:
        print(indent + "  Tabla no disponible.")
        return
    columns = list(zip(headers, *rows)) if rows else [(heading,) for heading in headers]
    widths = [min(24, max(len(str(cell)) for cell in col)) for col in columns]
    total = sum(widths) + 3 * len(widths)
    if total > 100:
        _vertical(headers, rows, indent)
    else:
        _horizontal(region, widths, indent)
    if region.get("truncated"):
        print(indent + "  [Tabla recortada al límite declarado]")


def _horizontal(region: dict, widths: list[int], indent: str) -> None:
    headers = region["headers"]
    align = region.get("align", ["left"] * len(headers))
    print(
        indent
        + "  "
        + " | ".join(_format(x, w, a) for x, w, a in zip(headers, widths, align))
    )
    print(indent + "  " + "-+-".join("-" * w for w in widths))
    for row in region["rows"]:
        print(
            indent
            + "  "
            + " | ".join(_format(x, w, a) for x, w, a in zip(row, widths, align))
        )


def _format(value: str, width: int, align: str) -> str:
    text = str(value).replace("\x1b", "?").replace("\n", " ")[:width]
    return text.rjust(width) if align == "right" else text.ljust(width)


def _vertical(headers: list, rows: list, indent: str) -> None:
    for index, row in enumerate(rows, 1):
        print(indent + f"  Registro {index}")
        for header, value in zip(headers, row):
            print(indent + "    " + str(header) + ": " + str(value))
