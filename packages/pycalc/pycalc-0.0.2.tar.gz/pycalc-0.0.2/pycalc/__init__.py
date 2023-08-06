"""Pcalc, use python as a calculator - from pycalc import *

Written by Peter Duerr
"""

# Plotting
import apipkg

PACKAGES = {
    'sp': "sympy",
    'u': "pycalc.units:sympy.physics.units",
    'np': "numpy",
    'sc': "scipy",
    'pd': "pandas",
    'umath': 'uncertainties.umath',
}
"""Top level packages
"""

PLOTTING_PACKAGES = {
    'plt': 'pycalc.plotting:PLT',
    'sns': 'pycalc.plotting:SNS',
}
"""Plotting modules with auto-setup
"""

CLASSES = {
    'ufloat': 'uncertainties:ufloat',
    'Counter': 'collections:Counter',
}
"""Additional classes to import
"""

SYMPY_VAR_NAMES = ['x', 'y', 'z', 'alpha', 'beta', 'gamma']
SYMPY_VARS = {name: "sympy.abc:%s" % name
              for name in SYMPY_VAR_NAMES}
"""Variables imported from sympy
"""

ALL_IMPORTS = {key: value for dic in [PACKAGES,
                                      CLASSES,
                                      SYMPY_VARS,
                                      PLOTTING_PACKAGES]
               for key, value in dic.items()}

# Lazily import the packages and attributes
apipkg.initpkg(__name__, ALL_IMPORTS)
