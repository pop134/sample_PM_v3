"""Export the OpenAPI spec to a JSON file (WBS 1.2.4, part 2/2).

Usage: python -m scripts.export_openapi [output_path]
Generates the contract the frontend integrates against, so it can be committed
or published in CI without a running server.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from app.main import create_app


def generate_openapi() -> dict:
    """Return the app's OpenAPI schema as a dict."""
    return create_app().openapi()


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    out = Path(argv[0]) if argv else Path("openapi.json")
    out.write_text(json.dumps(generate_openapi(), indent=2))
    print(f"Wrote OpenAPI spec to {out}")


if __name__ == "__main__":  # pragma: no cover
    main()
