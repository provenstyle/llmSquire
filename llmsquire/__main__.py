"""Entry point: python -m llmsquire"""
from __future__ import annotations

import os
import sys

# Ensure koans/ directory is importable
_koans_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "koans")
if _koans_dir not in sys.path:
    sys.path.insert(0, os.path.dirname(_koans_dir))


def main():
    """Run the path to enlightenment."""
    from dotenv import load_dotenv
    load_dotenv()

    from llmsquire.sensei import Sensei

    sensei = Sensei()
    sensei.run()


if __name__ == "__main__":
    main()