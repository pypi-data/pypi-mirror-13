"""Lazily set up plotting modules

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import lazy_object_proxy as proxy
from importlib import import_module

SETUP_DONE = [False]
"""Global flag indicating if setup has been done
"""


def setup():
    """Setup plotting
    """
    import seaborn as sns
    import matplotlib
    font = {'family': 'normal',
            'weight': 'normal',
            'size': 14}

    matplotlib.rc('font', **font)

    matplotlib.rc('text', usetex=True)
    matplotlib.rc('lines', linewidth=4)
    matplotlib.rc('figure', facecolor='white')

    label_size = 14
    matplotlib.rc('xtick', labelsize=label_size)
    matplotlib.rc('ytick', labelsize=label_size)

    if sns is not None:
        sns.set_style('darkgrid')
        sns.set_palette('colorblind',
                        desat=0.6)
    SETUP_DONE[0] = True


def plotting_module(module_name, sub_name=''):
    """Lazy importer for a plotting module
    """
    def deferred(module_name, sub_name):
        """Defer call to import until later
        """
        if not SETUP_DONE[0]:
            setup()
        mod = import_module(module_name)
        if not sub_name == '':
            return import_module('%s.%s' % (module_name, sub_name))
        else:
            return mod  # pylint: disable=undefined-variable
    return lambda: deferred(module_name, sub_name)

# Pyplot
PLT = proxy.Proxy(plotting_module('matplotlib', 'pyplot'))
# Seaborn
SNS = proxy.Proxy(plotting_module('seaborn'))
