import runpy
import sys
from pathlib import Path

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))
runpy.run_module("src.main", {}, "__main__")
