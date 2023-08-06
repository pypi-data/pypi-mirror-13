#!/usr/bin/python
# -*- encoding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt

# not used right now

contourf = {
    'colorbar':True,
    'cmap': plt.cm.jet,
    'levels': np.linspace(-100,100,21),
    'extend': 'both',
    'shrink': .8,
    'pad': .05,
    'extendfrac':'auto',
    'fontsize':20,
    }

contour = {
    # either colors or cmap must be None
    'inline':1,
    'fontsize':10,
    'fmt':'%1.1f',
    'colorlabel':True,
    'levels':[0],
    'linestyles':('-'),
    'linewidths':(1,)
    }

