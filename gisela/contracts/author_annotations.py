"""DSL 1.7 inert author annotations: RFC 6901 validation and opt-in inspection.

Only admitted package objects may be passed to the public inspector; normal
session observation has no dependency on this module.
"""

from __future__ import annotations

from copy import deepcopy

MAX_POINTER_DEPTH = 64
MAX_POINTER_LENGTH = 2048
MAX_RECORDS = 4096
MAX_TEXT_BYTES = 1024 * 1024
MAX_TEXT_CHARS = 8192


class InvalidTarget(ValueError):
    """An addressed note does not identify an admissible narrative location."""


def _escape(part: str) -> str:
    return part.replace("~", "~0").replace("/", "~1")


def _decode_segment(segment: str) -> str:
    """Validate escapes before decoding one JSON Pointer segment."""
    i = 0
    while i < len(segment):
        if segment[i] == "~":
            if i + 1 >= len(segment) or segment[i + 1] not in "01":
                raise InvalidTarget("Malformed ~ escape in JSON Pointer")
            i += 2
        else:
            i += 1
    return segment.replace("~1", "/").replace("~0", "~")


def _array_index(key: str, size: int) -> int:
    """Require a canonical decimal index within the current array."""
    if not key.isascii() or not key.isdecimal() or (len(key) > 1 and key[0] == "0"):
        raise InvalidTarget("Array index is not canonical decimal")
    if len(key) > 16 or int(key) >= size:
        raise InvalidTarget("Array index is out of bounds")
    return int(key)


def _resolve(package: dict, target: str) -> object:
    """Resolve a canonical RFC 6901 pointer without coercion or guesswork."""
    if target == "":
        return package
    if not isinstance(target, str) or len(target) > MAX_POINTER_LENGTH:
        raise InvalidTarget("Pointer exceeds the character budget")
    if not target.startswith("/"):
        raise InvalidTarget("Pointer must be empty or start with /")
    segments = target[1:].split("/")
    if len(segments) > MAX_POINTER_DEPTH:
        raise InvalidTarget("Pointer exceeds 64 segments")
    current: object = package
    for segment in segments:
        key = _decode_segment(segment)
        if key in ("annotations", "author_annotations"):
            raise InvalidTarget("Annotation metadata cannot be a target")
        if isinstance(current, dict):
            if key not in current:
                raise InvalidTarget("Object member does not exist")
            current = current[key]
        elif isinstance(current, list):
            current = current[_array_index(key, len(current))]
        else:
            raise InvalidTarget("Cannot traverse a scalar value")
    return current


def _local_notes(package: dict):
    """Yield local annotations with their owner pointer in canonical DFS order."""

    def walk(value, path):
        if isinstance(value, dict):
            notes = value.get("annotations", [])
            if isinstance(notes, list):
                for note in notes:
                    if isinstance(note, dict) and "audience" in note and "text" in note:
                        yield path, note
            for key, child in value.items():
                if key not in ("annotations", "author_annotations"):
                    yield from walk(child, path + "/" + _escape(key))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                yield from walk(child, path + "/" + str(index))

    yield from walk(package, "")


def _text_value(annotation: dict) -> str:
    item = annotation["text"]
    if isinstance(item, str):
        return item
    return item.get("text", item.get("text_key", ""))


def validate_author_annotations(package: dict) -> list[tuple[str, str, str]]:
    """Return (diagnostic code, JSON Pointer, explanation) for DSL 1.7 notes.

    The schema must already have accepted shapes and allowed audience types.
    """
    issues: list[tuple[str, str, str]] = []
    seen: set[str] = set()
    total_count = 0
    total_bytes = 0

    def account(note: dict, path: str):
        nonlocal total_count, total_bytes
        total_count += 1
        if note["audience"] == "info":
            info_text = note["text"]
            if isinstance(info_text, dict) and "text_key" in info_text:
                base = package["manifest"]["language"]
                if info_text["text_key"] not in package.get("strings", {}).get(
                    base, {}
                ):
                    issues.append(
                        (
                            "MISSING_AUTHOR_TEXT",
                            path,
                            "Author text_key is missing in the base language",
                        )
                    )
            plain = _text_value(note)
            if len(plain) > MAX_TEXT_CHARS:
                issues.append(
                    ("AUTHOR_TEXT_LIMIT", path, "Info text exceeds 8192 characters")
                )
            total_bytes += len(plain.encode("utf-8"))

    for owner, note in _local_notes(package):
        account(note, owner + "/annotations")
    for i, entry in enumerate(package.get("author_annotations", [])):
        path = f"/author_annotations/{i}/target"
        target = entry["target"]
        if target in seen:
            issues.append(
                ("AUTHOR_POINTER_DUPLICATE", path, "Duplicate addressed target")
            )
        seen.add(target)
        try:
            _resolve(package, target)
        except InvalidTarget as exc:
            issues.append(("AUTHOR_POINTER_INVALID", path, str(exc)))
        for j, note in enumerate(entry["annotations"]):
            account(note, f"/author_annotations/{i}/annotations/{j}")
    if total_count > MAX_RECORDS:
        issues.append(
            (
                "AUTHOR_ANNOTATION_LIMIT",
                "/author_annotations",
                "More than 4096 annotations",
            )
        )
    if total_bytes > MAX_TEXT_BYTES:
        issues.append(
            (
                "AUTHOR_TEXT_BUDGET",
                "/author_annotations",
                "Info text exceeds 1 MiB UTF-8",
            )
        )
    return issues


def inspect_author_annotations(admitted) -> tuple[dict, ...]:
    """Explicit author-only view, including unreachable branch annotations.

    Requires a previously admitted package; never use this in player Observe.
    The output is detached and retains raw localization objects unchanged.
    """
    from .admit_package import AdmittedPackage

    if not isinstance(admitted, AdmittedPackage):
        raise TypeError("Expected an AdmittedPackage; validate the package first")
    package = admitted.materialize()
    result: list[dict] = []

    def append(target: str, note: dict, source: str):
        result.append(
            {
                "order": len(result),
                "target": target,
                "audience": note["audience"],
                "text": deepcopy(note["text"]),
                "source": source,
            }
        )

    for target, note in _local_notes(package):
        append(target, note, "local")
    for item in package.get("author_annotations", []):
        for note in item["annotations"]:
            append(item["target"], note, "addressed")
    return tuple(result)
