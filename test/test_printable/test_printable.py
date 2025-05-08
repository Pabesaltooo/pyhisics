# test/test_printable.py
from __future__ import annotations
import unittest
from unittest.mock import patch
from pyhsics.printing.printable import Printable, Latex, display  # type: ignore

class Dummy(Printable):
    def __init__(self, value: float) -> None:
        self.value = value

    def __str__(self) -> str:
        return f"Valor = {self.value:.1f}"

    def _repr_latex_(self, name: str | None = None) -> str:
        return f"$V = {self.value:.1f}$"

class TestPrintable(unittest.TestCase):
    def test_str_and_repr(self) -> None:
        d = Dummy(3.14)
        self.assertEqual(str(d), "Valor = 3.1")
        self.assertEqual(repr(d), "Dummy(Valor = 3.1)")

    def test_latex_and_strip(self) -> None:
        d = Dummy(2.0)
        self.assertEqual(d._repr_latex_(), "$V = 2.0$")
        self.assertEqual(d.latex(), "V = 2.0")


if __name__ == "__main__":
    unittest.main()
