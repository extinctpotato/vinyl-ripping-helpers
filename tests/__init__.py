import os
from pathlib import Path

try:
    import pytest
except ImportError:
    raise SystemExit("pytest missing: install using your package manager")

DATA_DIR = Path(__file__).resolve().parent.joinpath("data")
