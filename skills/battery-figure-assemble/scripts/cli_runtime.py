"""Portable Unicode output for scientific CLIs, including Windows Chinese paths."""
import sys


def configure_utf8():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors='backslashreplace')
