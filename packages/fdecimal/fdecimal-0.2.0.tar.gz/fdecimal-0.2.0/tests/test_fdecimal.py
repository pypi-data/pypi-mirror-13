#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_fdecimal
----------------------------------

Tests for `fdecimal` module.
"""

import unittest
import fdecimal


class AdditionTests(unittest.TestCase):

    def test_type(self):
        self.assertIsInstance(
            7.2 + fdecimal.FDecimal(1.0),
            fdecimal.FDecimal,
        )

    def test_add(self):
        self.assertAlmostEqual(
            fdecimal.FDecimal(10.0),
            fdecimal.FDecimal(5.0) + 5.0,
        )

    def test_radd(self):
        self.assertAlmostEqual(
            fdecimal.FDecimal(10.0),
            5.0 + fdecimal.FDecimal(5.0),
        )


class SubtractionTests(unittest.TestCase):

    def test_type(self):
        self.assertIsInstance(
            7.2 - fdecimal.FDecimal(1.0),
            fdecimal.FDecimal,
        )

    def test_sub(self):
        self.assertAlmostEqual(
            fdecimal.FDecimal(10.0),
            fdecimal.FDecimal(15.0) - 5.0,
        )

    def test_rsub(self):
        self.assertAlmostEqual(
            fdecimal.FDecimal(0.0),
            5.0 - fdecimal.FDecimal(5.0),
        )


class MultiplicationTests(unittest.TestCase):

    def test_type(self):
        self.assertIsInstance(
            7.2 * fdecimal.FDecimal(1.0),
            fdecimal.FDecimal,
        )

    def test_mul(self):
        self.assertAlmostEqual(
            fdecimal.FDecimal(10.0),
            fdecimal.FDecimal(5.0) * 2.0,
        )

    def test_rmul(self):
        self.assertAlmostEqual(
            fdecimal.FDecimal(72.0),
            7.2 * fdecimal.FDecimal(10),
        )


class DivisionTests(unittest.TestCase):

    def test_type(self):
        self.assertIsInstance(
            7.2 / fdecimal.FDecimal(1.0),
            fdecimal.FDecimal,
        )

    def test_div(self):
        self.assertAlmostEqual(
            fdecimal.FDecimal(12.0),
            fdecimal.FDecimal(120) / 9.999999999999,
        )

    def test_rdiv(self):
        self.assertAlmostEqual(
            fdecimal.FDecimal(1.0),
            5.0 / fdecimal.FDecimal(5.0),
        )


if __name__ == '__main__':
    unittest.main()
