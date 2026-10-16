import sys
from pathlib import Path

# Add src to sys.path so tests can import debim_standards without prior installation
repo_root = Path(__file__).resolve().parent.parent
src_dir = repo_root / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))
