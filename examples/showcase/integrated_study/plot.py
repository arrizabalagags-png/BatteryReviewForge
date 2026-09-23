"""Standalone reproducible showcase step."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import GENERATORS, render
if __name__ == '__main__':
    render('integrated_study')
