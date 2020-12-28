# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 14:34:21 2015

@author: ub71894
"""

from pandas import Series, DataFrame 
import pandas as pd
import numpy as np
from numpy.random import randn
import matplotlib.pyplot as plt

fig = plt.figure()

ax1 = fig.add_subplot(2,2,1)
ax2 = fig.add_subplot(2,2,2)
ax3 = fig.add_subplot(2,2,3)

from numpy.random import randn
plt.plot(randn(50).cumsum(),'k--')


_ = ax1.hist(randn(100), bins=20, color='k', alpha=0.3)

ax2.scatter(np.arange(30), np.arange(30) + 3 * randn(30))
#%%
fig, axes = plt.subplots(2, 2, sharex=True, sharey=True)
for i in range(2):
    for j in range(2):
        axes[i, j].hist(np.random.randn(500), bins=50, color='k', alpha=0.5)
plt.subplots_adjust(wspace=0.2, hspace=0.1)

#%% Best way
f,ax=plt.subplots()

data = randn(30).cumsum()

ax.plot(data, 'k--', label='Default')
ax.plot(data, 'k-', drawstyle='steps-post', label='steps-post')
ax.legend(loc='best')
ax.set_xlabel('dsfa')
ax.arrow(3,6)
#%%
f,ax=plt.subplots()

df = DataFrame(np.random.randn(10, 4).cumsum(0),columns=['A', 'B', 'C', 'D'],
               index=np.arange(0, 100, 10))
df.plot(ax=ax,kind='bar')

fig, axes = plt.subplots(2, 1)
data = Series(np.random.rand(16), index=list('abcdefghijklmnop'))
data.plot(kind='bar', ax=axes[0], color='k', alpha=0.7)
data.plot(kind='barh', ax=axes[1], color='k', alpha=0.7)

#%% 
import matplotlib
matplotlib.style.use('ggplot')

ts = pd.Series(np.random.randn(1000), index=pd.date_range('1/1/2000', periods=1000))
ts = ts.cumsum()

df = pd.DataFrame(np.random.randn(1000, 4), index=ts.index, columns=list('ABCD'))
df = df.cumsum()
plt.figure(); df.plot();

f,ax=plt.subplots()
comp1 = np.random.normal(0, 1, size=200) # N(0, 1)
comp2 = np.random.normal(10, 2, size=200) # N(10, 4)
values = Series(np.concatenate([comp1, comp2]))
values.hist(bins=100, alpha=0.3, color='k', normed=True,ax=ax)
values.plot(kind='kde', style='b--',ax=ax)


#%%
macro = pd.read_csv('macrodata.csv')
data = macro[['cpi', 'm1', 'tbilrate', 'unemp']]
trans_data = np.log(data).diff().dropna()


f1,ax1=plt.subplots(1,2)
f2,ax2=plt.subplots(2,1)

f1 = plt.figure(1)
plt.axes(ax1[0])
plt.scatter(trans_data['m1'], trans_data['unemp'])
plt.title('Changes in log %s vs. log %s' % ('m1', 'unemp'))
plt.axes(ax1[1])
plt.scatter(trans_data['m1'], trans_data['unemp'])
plt.title('2 second')

f2 = plt.figure(2)
plt.axes(ax2[0])
plt.scatter(trans_data['m1'], trans_data['unemp'])
plt.title('Changes in log %s vs. log %s' % ('m1', 'unemp'))
plt.axes(ax2[1])
plt.scatter(trans_data['m1'], trans_data['unemp'])
plt.title('2 second')


pd.scatter_matrix(trans_data, diagonal='kde', color='k', alpha=0.3)









