"""Defines additional units for pycalc
"""
import sympy.physics.units

sympy.physics.units.B = sympy.physics.units.Unit('byte', 'B')
sympy.physics.units.b = sympy.Rational(1, 8) * sympy.physics.units.B
sympy.physics.units.KiB = 1024 * sympy.physics.units.B
sympy.physics.units.MiB = 1024**2 * sympy.physics.units.B
