"""
test_browser.py

Tests for tournament file name validation.
Tournament names may contain letters, digits, underscores and spaces.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from Application.browser import File


def _is_valid(name):
    return File().set_name(name).set_path("/tmp")._is_name_valid()


def test_names_with_spaces_are_valid():
    assert _is_valid("Chess Tournament 2026")
    assert _is_valid("My Cup")
    assert _is_valid("Chess Tournament")
    assert _is_valid("chess_tournament_2026")


def test_invalid_names_are_rejected():
    assert not _is_valid("")
    assert not _is_valid("bad/name")
    assert not _is_valid("bad.name")
    assert not _is_valid("bad-name")
