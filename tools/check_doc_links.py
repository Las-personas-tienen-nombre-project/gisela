"""Verify local Markdown destinations without requiring network access.

External URLs are deliberately out of scope. Historical references written as
plain text are not treated as live hyperlinks.
"""
from pathlib import Path
import re
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\((<[^>]+>|[^)]+)\)')


def broken_links(root=ROOT):
    errors = []
    for document in sorted(root.rglob('*.md')):
        if any(part in {'.git', '.venv', 'build', 'dist'} for part in document.relative_to(root).parts):
            continue
        text = document.read_text(encoding='utf-8')
        for match in LINK.finditer(text):
            destination = match.group(1).strip().strip('<>')
            if re.match(r'^[a-z][a-z0-9+.-]*:', destination, re.I) or destination.startswith('//'):
                continue
            target = unquote(destination.split('#', 1)[0])
            if target and not (document.parent / target).exists():
                line = text.count('\n', 0, match.start()) + 1
                errors.append(f'{document.relative_to(root)}:{line}: {destination}')
    return errors


if __name__ == '__main__':
    failures = broken_links()
    if failures:
        print('\n'.join(failures))
        raise SystemExit(1)
    print('OK: all local Markdown link destinations exist')
