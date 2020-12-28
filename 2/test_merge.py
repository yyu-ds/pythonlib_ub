# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 15:25:23 2015

@author: ub71894
"""
from pandas import Series, DataFrame 
import pandas as pd
import numpy as np


df1 = pd.DataFrame({'key': ['b', 'b', 'a', 'c', 'a', 'a', 'b'],'data1': range(7)})
df2 = pd.DataFrame({'key': ['a', 'b', 'd'],'data2': range(3)})
pd.merge(df1, df2)


left = pd.DataFrame({'key1': ['foo', 'foo', 'bar'], 'key2': ['one', 'two', 'one'],'lval': [1, 2, 3]})

right = pd.DataFrame({'key1': ['foo', 'foo', 'bar', 'bar'],'key2': ['one', 'one', 'one', 'two'],'rval': [4, 5, 6, 7]})


pd.merge(left, right, on=['key1', 'key2'], how='outer')


arr = np.arange(12).reshape((3, 4))

pd.concat([arr, arr])

s1 = pd.Series([0, 1], index=['a', 'b'])
s2 = pd.Series([2, 3, 4], index=['c', 'd', 'e'])
s3 = pd.Series([5, 6], index=['f', 'g'])

s4 = pd.concat([s1 * 5, s3])



data = DataFrame({'food': ['bacon', 'pulled pork', 'bacon', 'Pastrami',
'corned beef', 'Bacon', 'pastrami', 'honey ham',
'nova lox'],
'ounces': [4, 3, 12, 6, 7.5, 8, 3, 5, 6]})

meat_to_animal = {
'bacon': 'pig',
'pulled pork': 'pig',
'pastrami': 'cow',
'corned beef': 'cow',
'honey ham': 'pig',
'nova lox': 'salmon'
}
data['animal'] = data['food'].map(str.lower).map(meat_to_animal)

#%%

ages = [20, 22, 25, 27, 21, 23, 37, 31, 61, 45, 41, 32]
bins = [18, 25, 35, 60, 100]
cats = pd.cut(ages, bins)
group_names = ['Youth', 'YoungAdult', 'MiddleAged', 'Senior']
cats = pd.cut(ages, bins, labels=group_names)


data=np.random.randn(1000)
cc =pd.qcut(data,[0,0.1,0.5,0.9,1.0])
pd.value_counts(cc)
#%%

np.random.seed(12345)
data = DataFrame(np.random.randn(1000, 4))

data.describe()



df = DataFrame({'key': ['b', 'b', 'a', 'c', 'a', 'b'], 'data1': range(6)})
dummies = pd.get_dummies(df['key'], prefix='key')


#%%
import json
from pandas import Series, DataFrame 
import pandas as pd

db = json.load(open('foods-2011-10-03.json'))
nutrients = []

info_keys = ['description', 'group', 'id', 'manufacturer']
info = DataFrame(db, columns=info_keys)
col_mapping = {'description' : 'food', 'group' : 'fgroup'}
info = info.rename(columns=col_mapping, copy=False)

for rec in db:
    fnuts = DataFrame(rec['nutrients'])
    fnuts['id'] = rec['id']
    nutrients.append(fnuts)


nutrients = pd.concat(nutrients, ignore_index=True)
nutrients = nutrients.drop_duplicates()
col_mapping = {'description' : 'nutrient','group' : 'nutgroup'}
nutrients = nutrients.rename(columns=col_mapping, copy=False)

ndata = pd.merge(nutrients, info, on='id', how='outer')



result = ndata.groupby(['nutrient', 'fgroup'])['value'].quantile(0.5)



result['Zinc, Zn'].order().plot(kind='barh')

by_nutrient = ndata.groupby(['nutgroup', 'nutrient'])

get_maximum(c[['food','value']])
get_maximum(c[['value','food']])
get_maximum(c)
b[['food','value']]





tt = pd.DataFrame({'name': ['Yu', 'Zheng'],'age': [31, 32],'height':[173,164]})

tt2 = pd.DataFrame({'name': ['Yu2', 'Zheng'],'weight': [164, 110],'size':[10,8]})

tt3 = pd.DataFrame({'name': ['Huang', 'Lu'],'age': [50, 60],'height':[133,124]})

pd.merge(tt, tt2, how='outer',on='name')
pd.merge(tt, tt3,how='outer')











