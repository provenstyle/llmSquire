"""Entry point: python -m llmsquire [koan ...]"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from typing import List, Optional, Sequence

# Ensure koans/ directory is importable
_koans_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "koans")
if _koans_dir not in sys.path:
    sys.path.insert(0, os.path.dirname(_koans_dir))


def koan_names() -> List[str]:
    """The curriculum's koan names, in order."""
    from llmsquire.path_to_enlightenment import PATH
    return [module.rsplit(".", 1)[-1] for module in PATH]


def resolve_koan(name: str) -> str:
    """Turn a CLI argument into a koans package module name.

    Accepts a bare koan name (about_invocation), a dotted module name
    (koans.about_invocation), or a file path (koans/about_invocation.py).
    """
    name = name.strip().replace("\\", "/")
    if name.endswith(".py"):
        name = name[:-3]
    if "/" in name:
        name = name.rsplit("/", 1)[-1]
    return name if name.startswith("koans.") else f"koans.{name}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="llmsquire",
        description="Run the koans in curriculum order, stopping at the first failure.",
    )
    parser.add_argument(
        "koans",
        nargs="*",
        metavar="KOAN",
        help="koans to run, by name or path (default: the entire path)",
    )
    parser.add_argument(
        "-l", "--list", action="store_true",
        help="list the koans in curriculum order and exit",
    )
    return parser


def select_koans(parser: argparse.ArgumentParser, names: Sequence[str]) -> List[str]:
    """Resolve CLI names to modules in the order given, rejecting unknown ones."""
    selected: List[str] = []
    for name in names:
        module = resolve_koan(name)
        try:
            found = importlib.util.find_spec(module) is not None
        except (ImportError, ValueError):
            found = False
        if not found:
            parser.error(
                f"unknown koan: {name}\n"
                f"Available koans: {', '.join(koan_names())}"
            )
        if module not in selected:
            selected.append(module)
    return selected


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the path to enlightenment — or just the koans named on the command line."""
    from dotenv import load_dotenv
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        for name in koan_names():
            print(name)
        return 0

    from llmsquire.sensei import Sensei

    sensei = Sensei(select_koans(parser, args.koans) or None)
    sensei.run()
    return 0


if __name__ == "__main__":
    main()
