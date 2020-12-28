#%%
import numpy as np
from pandas import Series, DataFrame
import pandas as pd

obj=Series(range(4), index=['d', 'a', 'b', 'c'])


#%%

frame = DataFrame(np.arange(8).reshape((2, 4)), index=['three', 'one'],
.....: columns=['d', 'a', 'b', 'c'])

frame = DataFrame({'b': [4.3, 7, -3, 2], 'a': [0, 1, 0, 1],'c': [-2, 5, 8, -2.5]})


df = DataFrame(np.random.randn(4, 3), index=['a', 'a', 'b', 'b'])

df = DataFrame([[1.4, np.nan], [7.1, -4.5],
.....: [np.nan, np.nan], [0.75, -1.3]],
.....: index=['a', 'b', 'c', 'd'],
.....: columns=['one', 'two'])

#%%
dat = DataFrame(np.random.randn(100, 2), columns=['a', 'b'])

#%%

data = {'state':['Ohio','Ohio','Ohio','Nevada','Nevada'],'year':[2000,2001,2002,2001,2002],'pop':[1.5,1.7,3.6,2.4,2.9]}
df = DataFrame(data)

aa.groupby('year')['pop'].mean()
