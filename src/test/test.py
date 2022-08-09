# -*- coding: utf-8 -*-
"""
@author: dyx
@time: 2021/4/15 16:25
@des:
"""

import matplotlib as mpl

mpl.use('Agg')

import matplotlib.pyplot as plt

fig = plt.figure(figsize=(5.5,3),dpi=300)

ax = fig.add_subplot(111)

ax.grid(True,which='both')

ax.plot([0,1,2,3],[5,2,6,3],'o')

xlabel = ax.set_xlabel('xlab')

ax.set_ylabel('ylab')

fig.savefig(r'D:\001Project\006SanQing\RSPlatForm\src\test\test.png',bbox_extra_artists=[xlabel], bbox_inches='tight')
 