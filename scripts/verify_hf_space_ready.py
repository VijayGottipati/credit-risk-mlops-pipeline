"""Verify repo files needed for Hugging Face Docker Spaces (local check, no API calls)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    errors: list[str] = []

    dockerfile = ROOT / "Dockerfile"
    if not dockerfile.exists():
        errors.append("Missing Dockerfile at repo root.")
    else:
        text = dockerfile.read_text(encoding="utf-8")
        if "uvicorn" not in text:
            errors.append("Dockerfile should start uvicorn for FastAPI.")
        if "7860" not in text and "${PORT" not in text:
            errors.append("Dockerfile should expose/use port 7860 or $PORT for HF.")

    readme = ROOT / "README.md"
    if readme.exists():
        head = readme.read_text(encoding="utf-8")[:800]
        if "sdk: docker" not in head:
            errors.append("README.md frontmatter should include 'sdk: docker' for HF card.")
        if "app_port:" not in head:
            errors.append("README.md frontmatter should include 'app_port: 7860'.")

    api = ROOT / "api" / "main.py"
    if not api.exists():
        errors.append("Missing api/main.py")

    if errors:
        print("Issues:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("OK: Dockerfile, README HF frontmatter, and api/main.py look ready for HF Spaces.")
    print("Next: in HF Space settings, connect this GitHub repo or push with HF_TOKEN (see README).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
