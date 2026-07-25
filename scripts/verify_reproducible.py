from __future__ import annotations

import hashlib
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def _hashes() -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(DIST.glob("*.pdf"))
    }


def main() -> int:
    before = _hashes()
    if len(before) != 4:
        print("Build all four PDFs before checking reproducibility.", file=sys.stderr)
        return 1
    subprocess.run([sys.executable, "scripts/build_pdfs.py"], cwd=ROOT, check=True)
    after = _hashes()
    changed = {
        name: (before.get(name), after.get(name))
        for name in sorted(set(before) | set(after))
        if before.get(name) != after.get(name)
    }
    if changed:
        for name, (old, new) in changed.items():
            print(f"{name}: {old} != {new}", file=sys.stderr)
        return 1
    print("Reproducibility check passed for all four PDFs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
