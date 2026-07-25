from __future__ import annotations

import hashlib
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.build_pdfs import OUTPUTS


DIST = ROOT / "dist"
CHECKSUMS = ROOT / "SHA256SUMS"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    names = sorted(OUTPUTS.values())
    missing = [name for name in names if not (DIST / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Build all release PDFs first; missing: {missing}")
    lines = [f"{_sha256(DIST / name)}  dist/{name}" for name in names]
    CHECKSUMS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Updated {CHECKSUMS.name} for {len(lines)} PDFs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
