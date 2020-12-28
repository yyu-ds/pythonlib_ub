# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 15:23:01 2020

@author: ru87118
"""

import pandas as pd
import os, sqlite3, csv

dir_name=r'C:\Users\ru87118\Desktop\Compustat\Data'
os.chdir(dir_name)

base_filename='CnI091920_2'
filename_suffix = '.db'
filename = os.path.join(dir_name, base_filename + filename_suffix)
con = sqlite3.connect(filename)

CnIFinancials = pd.read_sql_query("SELECT * FROM CnIFinancials", con)
CnIRatings = pd.read_sql_query("SELECT * FROM CnIRatings", con)

con.close()

#%%
CnIRatings = CnIRatings.sort_values(by=['Gvkey','ratingDate'])
CnIRatings = CnIRatings[CnIRatings['ratingTypeCode']=='STDLONG']
CnIRatings = CnIRatings.drop_duplicates(subset=['Gvkey','ratingDate'],keep='last')
CnIRatings['ratingYear'] = CnIRatings['ratingDate'].str[:4]

#Add records for continuous rating without changes
CnIRatings_ext = CnIRatings
CnIRatings_ext['ratingYear'] = CnIRatings_ext['ratingYear'].astype(int)
init = CnIRatings_ext.iloc[0]
init_year = CnIRatings_ext.iloc[0]['ratingYear']
init_key = CnIRatings_ext.iloc[0]['Gvkey']
for i in range(len(CnIRatings_ext)):
    print(i)
    if CnIRatings_ext.iloc[i]['ratingYear'] > init_year+1 and CnIRatings_ext.iloc[i]['Gvkey'] == init_key:
        for j in range(1, CnIRatings_ext.iloc[i]['ratingYear'] - init_year):
            init['ratingYear'] = init_year + j
            CnIRatings_ext = CnIRatings_ext.append(init)   
    init = CnIRatings_ext.iloc[i]
    init_year = CnIRatings_ext.iloc[i]['ratingYear']
    init_key = CnIRatings_ext.iloc[i]['Gvkey']
    
CnIRatings_ext = CnIRatings_ext.sort_values(by=['Gvkey','ratingDate'])
#%%
CnIFinancials = CnIFinancials[CnIFinancials['datafmt']=='STD']
CnIFinancials['financialYear'] = CnIFinancials['datadate'].str[:4]
CnIFinancials['financialDate'] = CnIFinancials['datadate'].str[4:]
    
CnIFinancials['financialYear'] = CnIFinancials['financialYear'].astype(int)
CnIFinancials['financialDate'] = CnIFinancials['financialDate'].astype(int)
CnIFinancials_annual = CnIFinancials[CnIFinancials['financialDate']==1231]

#%%    
CnIFinancials_annual['financialYearP1'] = CnIFinancials['financialYear'] + 1
data_merge = CnIRatings_ext.merge(CnIFinancials_annual, how='left', left_on=['Gvkey', 'ratingYear'], right_on=['GVKEY', 'financialYearP1'])

#CnIFinancials_annual.to_csv(r'CnIFinancials_annual.csv')
#CnIRatings_ext.to_csv(r'CnIRatings_ext.csv')

#data_merge = pd.read_csv(r'data_merge.csv')
#CnIFinancials_annual = pd.read_csv(r'CnIFinancials_annual.csv')
#CnIRatings_ext = pd.read_csv(r'CnIRatings_ext.csv')

data_merge_dropna = data_merge.dropna(subset=['financialYearP1'])
#data_exam = data_merge_dropna[['GVKEY', 'financialYearP1', 'Gvkey', 'ratingYear', 'ratingSymbol']]
data_merge_dropna.to_csv(r'data_merge.csv')

CnIFinancials_annual['GVKEY'].nunique()
CnIRatings['Gvkey'].nunique()
CnIRatings_ext['Gvkey'].nunique()
data_merge_dropna['GVKEY'].nunique()
print(CnIFinancials_annual.groupby('financialYear')['financialYear'].count())
print(CnIRatings_ext.groupby('ratingYear')['ratingYear'].count())
print(CnIRatings.groupby('ratingYear')['ratingYear'].count())
print(data_merge_dropna.groupby('ratingYear')['ratingYear'].count())

tmp=CnIRatings_ext.groupby('ratingYear')['ratingYear'].count()
tmp=CnIRatings.groupby('ratingYear')['ratingYear'].count()

