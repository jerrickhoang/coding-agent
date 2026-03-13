"""Tests for utils — expect add to be fixed to subtract for task success."""

import pytest
from utils import add, greet


def test_add():
    assert add(2, 3) == -1  # Task: change add() to subtract so this passes


def test_greet():
    assert greet("world") == "Hello, world!"
