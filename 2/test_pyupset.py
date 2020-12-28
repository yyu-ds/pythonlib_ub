
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\python\Testcode")


set1 = [1,2,3,4,5,6]
set2 = [2,3,4,7,8,9]
set3 = [1,3,5,7,9,10]
df1=pd.DataFrame()
df2=pd.DataFrame()
df3=pd.DataFrame()
df1['num'] = set1
df2['num'] = set2
df3['num'] = set3

df = {'set1':df1, 'set2':df2, 'set3':df3}
pyu.plot(df)


with open('test_data_dict.pckl', 'rb') as f:
    data_dict = load(f)
pyu.plot(data_dict)

