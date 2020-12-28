

import os
os.chdir(r"C:\Users\ub71894\Documents\Data")
import pandas as pd 
import numpy as np

data = pd.read_excel(r'ind dev quant.xls')

data2 = pd.read_excel(r'ind dev quant.xls')

quant_factor = ['quant1','quant2','quant3','quant4']

floor = [0.024234, 1.84363, 76699.5, 15196]
cap = [2.33655, 406.7364, 36700450, 5856121]
  


# cap/floor:
for i, col in enumerate(quant_factor):
    data[col] = np.clip(data[col], floor[i], cap[i])


#data['quant1'].fillna(data['quant1'].mean(), inplace=True)

data[quant_factor].describe()



len(data.query('quant1!=quant1'))
len(data.query('quant2!=quant2'))
len(data.query('quant3!=quant3'))
len(data.query('quant4!=quant4'))

len(data.query('quant1!=quant1 or quant2!=quant2 '))

len(data.query('quant1!=quant1 or quant3!=quant3 '))

len(data.query('quant1!=quant1 or quant4!=quant4 '))

len(data.query('quant2!=quant2 or quant3!=quant3 '))

len(data.query('quant4!=quant4 or quant3!=quant3 '))















#%%

data = pd.read_excel(r'ind dev quant.xls')
data.dropna(subset=['quant4','quant3'], how='any', inplace=True)

data.loc[data.quant2<0,"quant2"]=np.nan

# cap/floor:
for i, col in enumerate(quant_factor):
    data[col] = np.clip(data[col], floor[i], cap[i])

data.quant2.fillna(406.7364, inplace=True)
data['quant1'].fillna(data['quant1'].mean(), inplace=True)



data[quant_factor].describe()
