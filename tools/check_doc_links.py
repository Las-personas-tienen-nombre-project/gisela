"""Verify local Markdown destinations and heading anchors without network access.

External URLs are deliberately out of scope. Historical references written as
plain text are not treated as live hyperlinks.
"""

import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\((<[^>]+>|[^)]+)\)")


def heading_ids(document):
    """Return GitHub-style heading IDs and explicit HTML anchors."""
    anchors, used = set(), set()
    fence = None
    for line in document.read_text(encoding="utf-8").splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            if fence is None:
                fence = marker.group(1)
            elif marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        anchors.update(re.findall(r"<[^>]+\b(?:id|name)=[\"\']([^\"\']+)", line))
        match = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        title = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", match.group(1))
        slug = re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")
        candidate, number = slug, 0
        while candidate in used:
            number += 1
            candidate = f"{slug}-{number}"
        used.add(candidate)
        anchors.add(candidate)
    return anchors


def broken_links(root=ROOT):
    errors = []
    cached_anchors = {}
    for document in sorted(root.rglob("*.md")):
        if any(
            part in {".git", ".venv", "build", "dist"} or part.endswith(".egg-info")
            for part in document.relative_to(root).parts
        ):
            continue
        text = document.read_text(encoding="utf-8")
        for match in LINK.finditer(text):
            destination = match.group(1).strip().strip("<>")
            if re.match(
                r"^[a-z][a-z0-9+.-]*:", destination, re.IGNORECASE
            ) or destination.startswith("//"):
                continue
            target, _, fragment = destination.partition("#")
            resolved = document.parent / unquote(target) if target else document
            missing = not resolved.exists()
            if not missing and fragment and resolved.suffix == ".md":
                if resolved not in cached_anchors:
                    cached_anchors[resolved] = heading_ids(resolved)
                missing = unquote(fragment) not in cached_anchors[resolved]
            if missing:
                line = text.count("\n", 0, match.start()) + 1
                errors.append(f"{document.relative_to(root)}:{line}: {destination}")
    return errors


if __name__ == "__main__":
    failures = broken_links()
    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print("OK: all local Markdown link destinations and heading anchors exist")
