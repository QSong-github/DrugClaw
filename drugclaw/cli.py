from __future__ import annotations

import argparse
import sys
from typing import List

from .config import Config
from .main_system import DrugClawSystem
from .models import ThinkingMode


DEMO_PRESETS = {
    "adr": {
        "query": "What are the known adverse drug reactions of aspirin?",
        "mode": ThinkingMode.SIMPLE.value,
        "resource_filter": ["SIDER", "FAERS"],
        "description": "ADR query with the most stable default resources.",
    },
    "dti": {
        "query": "What are the known drug targets of imatinib?",
        "mode": ThinkingMode.SIMPLE.value,
        "resource_filter": ["ChEMBL", "DGIdb", "Open Targets Platform"],
        "description": "Drug-target query across three public sources.",
    },
    "label": {
        "query": "What prescribing and safety information is available for metformin?",
        "mode": ThinkingMode.SIMPLE.value,
        "resource_filter": ["DailyMed", "openFDA Human Drug", "MedlinePlus Drug Info"],
        "description": "Drug labeling and patient information query.",
    },
}


def _parse_resource_filter(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="drugclaw",
        description="CLI entrypoint for fast DrugClaw demos and manual queries.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser(
        "run",
        help="Run a custom query with configurable mode and resource filter.",
    )
    run_parser.add_argument(
        "--query",
        required=True,
        help="Natural-language query to send to DrugClaw.",
    )
    run_parser.add_argument(
        "--mode",
        choices=[ThinkingMode.GRAPH.value, ThinkingMode.SIMPLE.value, ThinkingMode.WEB_ONLY.value],
        default=ThinkingMode.SIMPLE.value,
        help="Thinking mode. SIMPLE is the safest default for first-time usage.",
    )
    run_parser.add_argument(
        "--key-file",
        default="navigator_api_keys.json",
        help="Path to navigator_api_keys.json.",
    )
    run_parser.add_argument(
        "--resource-filter",
        type=_parse_resource_filter,
        default=None,
        help="Comma-separated skill names, e.g. 'SIDER,FAERS'.",
    )

    demo_parser = subparsers.add_parser(
        "demo",
        help="Run a curated demo query intended for first-time users.",
    )
    demo_parser.add_argument(
        "--preset",
        choices=sorted(DEMO_PRESETS),
        default="label",
        help="Choose a built-in demo scenario.",
    )
    demo_parser.add_argument(
        "--key-file",
        default="navigator_api_keys.json",
        help="Path to navigator_api_keys.json.",
    )

    return parser


def _run_query(
    *,
    query: str,
    thinking_mode: str,
    key_file: str,
    resource_filter: List[str] | None,
) -> int:
    config = Config(key_file=key_file)
    system = DrugClawSystem(config)

    result = system.query(
        query,
        thinking_mode=thinking_mode,
        resource_filter=resource_filter or [],
    )

    print(result["answer"])
    return 0 if result.get("success") else 1


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.command == "run":
        return _run_query(
            query=args.query,
            thinking_mode=args.mode,
            key_file=args.key_file,
            resource_filter=args.resource_filter,
        )

    preset = DEMO_PRESETS[args.preset]
    print(f"[DrugClaw demo] preset={args.preset} - {preset['description']}")
    print(f"[DrugClaw demo] query={preset['query']}")
    print(f"[DrugClaw demo] resource_filter={preset['resource_filter']}")
    return _run_query(
        query=preset["query"],
        thinking_mode=preset["mode"],
        key_file=args.key_file,
        resource_filter=preset["resource_filter"],
    )
