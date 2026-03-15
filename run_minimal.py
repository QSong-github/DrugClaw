"""
Minimal runnable entrypoint for DrugClaw.

Uses the shortest stable path through the system:
  - explicit local key file
  - SIMPLE mode
  - pure online labeling resources
"""
from __future__ import annotations

import sys

from drugclaw.cli import main


if __name__ == "__main__":
    argv = sys.argv[1:]
    if argv:
        raise SystemExit(main(argv))
    raise SystemExit(main(["demo", "--preset", "label"]))
