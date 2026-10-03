"""Inspect existing outputs without publishing or calling a model."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from recipe_runtime import verify
from cli_runtime import configure_utf8

if __name__ == "__main__":
    configure_utf8()
    parser = argparse.ArgumentParser(description="核对图件文件/输入哈希；不声称完成科学审查")
    parser.add_argument("--working", type=Path, required=True)
    args = parser.parse_args()
    errors = verify(args.working)
    print("\n".join(errors) if errors else "Technical file/data-record checks PASS; author scientific/visual review remains pending.")
    raise SystemExit(1 if errors else 0)
