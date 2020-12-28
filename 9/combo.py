#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Created on Tue Oct  3 15:44:59 2017 @author: ghost """
""" Created on Tue Jan 16 15:59:01 2018 @author: another ghost """


import os, sys, pandas as pd, datetime as dt
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")


dat10 = pd.read_pickle('data\CnI2010.pickle')
dat11 = pd.read_pickle('data\CnI2011.pickle')
dat12 = pd.read_pickle('data\CnI2012.pickle')
dat13 = pd.read_pickle('data\CnI2013.pickle')
dat14 = pd.read_pickle('data\CnI2014.pickle')
dat15 = pd.read_pickle('data\CnI2015.pickle')
dat16 = pd.read_pickle('data\CnI2016.pickle')
dat17 = pd.read_pickle('data\CnI2017_01_08.pickle')
dat = pd.concat([dat10, dat11, dat12, dat13, dat14, dat15, dat16, dat17], axis=0)

a = dat.groupby(['Obligor_Num', 'archive_date'], as_index = False).snapshot.min()
data = pd.merge(dat, a, on = ['Obligor_Num', 'archive_date', 'snapshot'])




data.loc[pd.isnull(data.EXPOSURE_committed), 'EXPOSURE_committed'] = 0
data.loc[pd.isnull(data.exposure_committed), 'exposure_committed'] = 0
data['commitment'] = [max(x) for x in zip(data.EXPOSURE_committed, data.exposure_committed)]
data.loc[pd.isnull(data.EXPOSURE_outstanding), 'EXPOSURE_outstanding'] = 0
data.loc[pd.isnull(data.exposure_outstanding), 'exposure_outstanding'] = 0
data['outstanding'] = [max(x) for x in zip(data.EXPOSURE_outstanding, data.exposure_outstanding)]
data = data.drop(['EXPOSURE_committed','EXPOSURE_outstanding','exposure_committed','exposure_outstanding',
                  'NET_COMMITMENT_AMOUNT','EADtot','EXPOSURE_ead','exposure_ead','Commitment','Outstanding'], axis = 1)
data = data[data.commitment > 0]

data.rename(columns = {'Obligor_Num':'obligor', 'CIF_Num': 'CIF',
                       'ASSG_DIVISION_NAME':'division',  'ASSG_ORG_UNIT_NAME': 'unit', 'ASSG_REGION_NAME': 'region',
                       'EXPOSURE_seniority': 'seniority', 'Underwriter_Guideline': 'MAUG',
                       'Mgmt_Resp_Adverse_Conditions': 'mgmt_resp', 'Vulnerability_To_Changes': 'vulnerability',
                       'Level_Waiver_Covenant_Mod': 'Waiver_Mod', 'Strength_SOR_Prevent_Default':'SSOR',
                       'Public_Private_Cd' : 'public', 'exposure_neg_pledge':'neg_pledge'}, 
            inplace = True)

data.loc[data.division == 'COMMERCIAL BANKING CONSOLIDATED', 'division'] = 'COMMERCIAL BANKING GROUP'
data = data[data.division.isin(['BUSINESS BANKING GROUP', 'NATIONAL BANKING', 'COMMERCIAL BANKING GROUP'])]
#                                'WEALTH MANAGEMENT','PRCG - PACIFIC RIM CORPORATE GROUP'])]

divisions = {'BUSINESS BANKING GROUP': 'bbg', 'NATIONAL BANKING': 'natb', 'WEALTH MANAGEMENT': 'wealth',
             'COMMERCIAL BANKING GROUP': 'cbgrp',  'PRCG - PACIFIC RIM CORPORATE GROUP': 'PRCG'}
data.division = [divisions[x] for x in data.division]


data.unit = [x.title() for x in data.unit]
data.region = [x.title() for x in data.region]
data.public = [1 if x == 'PUB' else 0 for x in data.public]
data.Customer_Since = pd.to_datetime(data.Customer_Since)
data.archive_date = pd.to_datetime(data.archive_date)
data.loc[pd.isnull(data.Customer_Since), 'Customer_Since'] = dt.date.today()


data.loc[data['Audit_Method'] == 'TaxReturn', 'Audit_Method'] = 'Tax Return'
data = data[~data.EXCPTN_RSN_FAC_LVL_OBR_RATNG.isin(['CMM', 'IPRE'])]
data = data[data.Exception_Reason != 'Currency Mismatch']
data = data[data.CurrencyType != 'CAD']
data = data[data.GDW_SCORECARD_NAME == 'UBOCCI']
data = data[data.obligor > 1]


# removing some fields not useful for machine learning or just extraneous
data = data.drop(['Adjusted_CIF_Number', 'AgencyRating_Justification', 'Approver_Name',
                  'BTMU_Equivalent_Rating', 'BTMU_Equivalent_Rating2', 
                  'ExternalRating', 'ExternalRating_date', 'ExternalRating_value', 
                  'Final_Mapped_Risk_Grade', 'FACILITY_NUMBER', 'Map_Risk_Grade_after_Gtee',
                  'Map_Risk_Grade_after_RLA', 'OFFICER_FIRST_NAME', 'OFFICER_LAST_NAME',
                  'OFFICER_NUMBER', 'PDRR_MAP_RG_ACL', 'Prelim_Map_Risk_Grade', 'Prelim_Map_Risk_Grade_Uncap',
                  'Recommender_Name', 'PD_After_Gtee', 'PD_After_RLA', 'ASSG_RC_CD', 
                  'EXPOSURE_unencumberedAssets', 'EXCPTN_RSN_FAC_LVL_OBR_RATNG', 'Scorecard_Nm',
                  'GDW_SCORECARD_NAME', 'Exception_Reason', 'RC_NM', 'CurrencyType', 'cnt', 'Scorecard_Id', 
                  'exposure_unencumberedAssets', 'exposure_facility_code', 
                  'Qualitative_As_Pct_Possible', 'Qualitative_Section_Notes',
                  'version_num', 'ModelVersion', 'statement_id', 'rc', 'Total_Score_Pct_Possible',
                  'SYSTEM_DATE', 'LASID_System', 'NAICS_Cd', 'REGION_CD', 'PROCESS_DATE', 'SOURCE_SYSTEM', 
                  'RPTG_DIVISION_NAME', 'RPTG_ORG_UNIT_NAME', 'RPTG_RC_CODE', 'RPTG_REGION_NAME'
                  ], axis = 1)

# Removing guaranteed obligors
data = data[pd.isnull(data.Guarantor_Notches)]
data = data.drop(['Guarantor_Notches','Guarantee_Section_Notes','Guarantor_CIF','Guarantor_Condition_1',
                  'Guarantor_Condition_2','Guarantor_Condition_3','Guarantor_Condition_4','Guarantor_Condition_5',
                  'Guarantee_Section_Notes','Guarantor_ArchiveId','Guarantor_Justification','Guarantor_Name',
                  'Guarantor_PD_Risk_Rating','Guarantor_RA_ID','Guarantor_Support_Pct','Guarantor_scorecard_nm',
                  'PD_Risk_Rating_After_Gtee'], axis = 1)

# Removing extra agency fields
data = data.drop(['Moodys_Rating', 'Moodys_Rating_Date', 'Moodys_Rating_type', 'SPRating', 'Sprating_date',
                  'Sprating_type'], axis = 1)

data.loc[pd.isnull(data.neg_pledge), 'neg_pledge'] = data.loc[pd.isnull(data.neg_pledge), 'EXPOSURE_neg_pledge']
data = data.drop(['EXPOSURE_neg_pledge'], axis = 1)
data.loc[pd.isnull(data.exposure_type), 'exposure_type'] = data.loc[pd.isnull(data.exposure_type), 'EXPOSURE_type']
data = data.drop(['EXPOSURE_type'], axis = 1)

data = data.drop(['Override_Reason_1', 'Override_Reason_2', 'Override_Reason_3', 'Override_Section_Notes',
                  'RLA_Reason_1', 'RLA_Reason_2', 'RLA_Reason_3', 'RLA_Section_Notes',
                  'RLA_Justification'], axis = 1)

data.rename(columns = {x : x.lower() for x in list(data.columns)}, inplace = True)


#%% save data 
data.reset_index(drop=True, inplace=True)
data.to_pickle('fulldata.pkl.xz')




# coding: utf-8

# ### 1. Import pickle data and pick factor candidates

# In[1]:


import os, sys, pandas as pd
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")
data = pd.read_pickle(r'data\fulldata.pkl.xz')

df=data.copy()
#%% dependent fields = vulnerability, ssor , mgmt_resp, waiver_mod

quality = df.count()/len(df)
quality.sort_values(inplace=True)
quality


# #### Drop factor 'total_debt_by_acf', only 16.2672% valid data
# 

# In[7]:


df.drop( 'total_debt_by_acf', axis=1,inplace=True)


# ### 2. Fill missing data

# #### Treat 'exposure_seniority' and  'secured_or_unsecured' by the same way: Fill all NA as 'unknown type'
# 

# In[9]:


df['exposure_seniority'].fillna('unknown_seniority', inplace=True)
df['secured_or_unsecured'].fillna('unknown_security', inplace=True)


# #### Fill quant factor's NA with its median.

# In[10]:


df = df.fillna(df.median(), inplace=True)


# #### Fill quali factor's NA with its mode.

# In[11]:


cat=['access_outside_capital', 'info_rptg_timely_manner','pct_revenue_3_large_custs',
'management_quality','excp_underwrite_for_leverage', 'market_outlook_of_borrower']  
df[cat] = df[cat].fillna(df[cat].mode().iloc[0])


# In[18]:


nunique = df.nunique().sort_values()
nunique


# >* secured_or_unsecured                9
# * region                             19
# * exposure_type                      71
# * maug                               75
# * unit                              239
# * kmvedf                            714
# * naics_code                        741
# 
# #### Then we decide to drop 'unit' and consolidate other qualitative categorical factors:

# In[13]:


df.drop('unit', axis=1,inplace=True)
df.reset_index(drop=True, inplace=True)


# ### 3. Consolidate qualitative categorical data

# #### Consolidate 'secured_or_unsecured'
# 

# In[16]:


df.groupby('secured_or_unsecured').count()


# #### From the result, we can keep *Secured by blanket lien on total assets*, *Secured by specific collateral*, *Unsecured* and *unknonw*, then consolidate others into 'Unsecured' and 'Secured by others'

# In[19]:


cons_dict = {'Facility (lease)':'Secured by others','S_TYPE_SECURED_BLANKET_LIEN_LARGE':'Secured by others', \
'S_TYPE_UNSECURED_LARGE':'Unsecured','Secured by general pledge of revenue':'Secured by others', \
'Solid Waste Management (UG 410)':'Secured by others'}
df['secured_or_unsecured'].replace(cons_dict, inplace=True)


# In[20]:


df.groupby('secured_or_unsecured').count()


# In[25]:


new_secured_or_unsecured=pd.get_dummies(df['secured_or_unsecured'])
new_secured_or_unsecured.sum()


df.drop('secured_or_unsecured', axis=1,inplace=True)
df = pd.concat([df, new_secured_or_unsecured], axis=1)




# #### Consolidate 'region'
df.groupby('region').count()
df.drop('region', axis=1,inplace=True)



# #### Consolidate 'exposure_type'
df.groupby('exposure_type').count()

# rename all 'F2_TYPE_...'
def rename(L):
    result={}
    for name in L:
        result.update({name:name[8:]})
    return(result)

L=[
'F2_TYPE_ACPTSLCDP',
'F2_TYPE_BONDTAXEX',
'F2_TYPE_BRIDGELOAN',
'F2_TYPE_COMLSBLC',
'F2_TYPE_CREL',
'F2_TYPE_DDTERMLOAN',
'F2_TYPE_EQUIPLEASE',
'F2_TYPE_FRONTING',
'F2_TYPE_ICL',
'F2_TYPE_IGL',
'F2_TYPE_LC',
'F2_TYPE_LCLINE',
'F2_TYPE_LCLINECS',
'F2_TYPE_LINE',
'F2_TYPE_LOC',
'F2_TYPE_NR',
'F2_TYPE_NRTL',
'F2_TYPE_PURCH_AGR',
'F2_TYPE_RC',
'F2_TYPE_RC364DAY',
'F2_TYPE_RC364Dp',
'F2_TYPE_RE',
'F2_TYPE_RRC',
'F2_TYPE_RTL',
'F2_TYPE_SLCAUTO',
'F2_TYPE_SLCDP',
'F2_TYPE_SLCEVG',
'F2_TYPE_SLCFD',
'F2_TYPE_SLCLINE',
'F2_TYPE_SUBLIMITI',
'F2_TYPE_SWINGLINE',
'F2_TYPE_TERMLOAN',
'F2_TYPE_TFLINE',
'F2_TYPE_TL',
'F2_TYPE_TLB',
'F2_TYPE_TLLINE',
'F2_TYPE_TLNAm',
'F2_TYPE_TRANS',
'F2_TYPE_TRANSLINE']

df['exposure_type'].replace(rename(L), inplace=True)
df.groupby('exposure_type').count()

# remove '-','_','/' and capitalized all letters
def rename2(L):
    result={}
    for name in L:
        temp = name.replace("-", "")
        temp = temp.replace("_", "")
        temp = temp.replace("/", "")
        temp = temp.replace(" ", "")
        result.update({name:temp.upper()})
    return(result)
L=[
'ACPTSLCDP',
'BCC',
'BOND-Tax',
'BOND-TaxEx',
'BONDTAXEX',
'BRIDGELOAN',
'Bridge',
'CC',
'COMLSBLC',
'CREL',
'Coml/SBLC',
'DDTERMLOAN',
'EQUIP LSE',
'EQUIPLEASE',
'FRONTING',
'Fronting',
'ICL',
'IGL',
'LC',
'LC Line',
'LC Line-CS',
'LCLINE',
'LCLINECS',
'LINE',
'LOC',
'NR',
'NR-TL',
'NRTL',
'PURCH_AGR',
'RC',
'RC364DAY',
'RC364Dp',
'RE',
'RRC',
'RTL',
'SLC Line',
'SLC-Auto',
'SLC-DP',
'SLC-Evg',
'SLC-FD',
'SLCAUTO',
'SLCDP',
'SLCEVG',
'SLCFD',
'SLCLINE',
'SUBLIMITI',
'SWINGLINE',
'Swingline',
'TERMLOAN',
'TF LINE',
'TFLINE',
'TL',
'TL Line',
'TL-B',
'TL-NAm',
'TLB',
'TLLINE',
'TLNAm',
'TRANS',
'TRANSLINE',
'Trans',
'Trans Line'
]

df['exposure_type'].replace(rename2(L), inplace=True)
df.groupby('exposure_type').count()

# the 4 largest type include about 90% obs, so we put all others into 5th 'others'
L=[
'ACPTSLCDP',
 'BCC',
 'BONDTAX',
 'BONDTAXEX',
 'BRIDGE',
 'BRIDGELOAN',
 'CC',
 'COMLSBLC',
 'DDTERMLOAN',
 'EQUIPLEASE',
 'EQUIPLSE',
 'FRONTING',
 'ICL',
 'IGL',
 'LC',
 'LCLINE',
 'LCLINECS',
 'LOC',
 'NR',
 'NRTL',
 'PURCHAGR',
 'RC364DAY',
 'RC364DP',
 'RE',
 'RRC',
 'RTL',
 'SLCAUTO',
 'SLCDP',
 'SLCEVG',
 'SLCFD',
 'SLCLINE',
 'SUBLIMITI',
 'SWINGLINE',
 'TERMLOAN',
 'TFLINE',
 'TLB',
 'TLLINE',
 'TLNAM',
 'TRANS',
 'TRANSLINE']

rename3 = dict(zip(L,len(L)*['OTHERS']))
df['exposure_type'].replace(rename3, inplace=True)
df.groupby('exposure_type').count()


new_exposure_type=pd.get_dummies(df['exposure_type'])
new_exposure_type.sum()


df.drop('exposure_type', axis=1,inplace=True)
df = pd.concat([df, new_exposure_type], axis=1)


#Consolidate 'maug'
df.groupby('maug').count()

# clean string:
def rename(L):
    result={}
    for name in L:
        result.update({name:name[5:]})
    return(result)

L=['CBUG-125', 'CBUG-130', 'CBUG-135', 'CBUG-185','CBUG-190']

df['maug'].replace(rename(L), inplace=True)
df.groupby('maug').count()

# consolidate rule 'ABC' to 'A00'
def rename2(L):
    result={}
    for name in L:
        result.update({name:name[:1]+'00'})
    return(result)
L=df.groupby('maug').count().index.tolist()

df['maug'].replace( rename2(L), inplace=True)
df.groupby('maug').count()


new_maug=pd.get_dummies(df['maug'])
new_maug.sum()


df.drop('maug', axis=1,inplace=True)
df = pd.concat([df, new_maug], axis=1)



# Transfer letters to int
cat=['excp_underwrite_for_leverage', 'vulnerability', 'division',
       'access_outside_capital', 'pct_revenue_3_large_custs',
       'market_outlook_of_borrower', 'ssor', 'waiver_mod',
       'exposure_seniority',
       'info_rptg_timely_manner', 'management_quality', 'mgmt_resp']

for variable in cat:
  df[variable] = pd.Categorical(df[variable]).codes


# transfer customer_since to quantitative factor by keeping year digits
temp = df.groupby('obligor', as_index = False).customer_since.min()
temp.columns = ['obligor', 'custmin']
temp['cyear'] = temp['custmin'].transform(lambda x: x.strftime('%Y'))
temp['cyear'] = temp['cyear'].transform(lambda x: int(x))
temp.drop('custmin', axis=1,inplace=True)
df = pd.merge(df, temp, how = 'left', on = 'obligor')



# transfer naics_code into categorical factor by keeping the first two digits
temp = df.groupby('obligor', as_index = False).naics_code.max()
temp.columns = ['obligor', 'naics']
temp['naics'] = temp['naics'].replace({-1:111140})
temp['naics'] = temp['naics'].transform(lambda x: str(int(x/10000)))
df = pd.merge(df, temp, how = 'left', on = 'obligor')

new_naics=pd.get_dummies(df['naics'])
new_naics.sum()
df.drop('naics', axis=1,inplace=True)
df = pd.concat([df, new_naics], axis=1)





#%% Macro
df1 = pd.read_csv('CPIAUCSL.csv')
df1.DATE = df1.DATE.transform(lambda x: x[:7])
df_dict = dict(zip(df1.DATE, df1.CPIAUCSL))
df['CPIAUCSL'] = df['archive_date'].transform(lambda x: x.strftime('%Y-%m'))
df['CPIAUCSL'].replace(to_replace=df_dict, inplace=True)

df2 = pd.read_csv('INDPRO.csv')
df2.DATE = df2.DATE.transform(lambda x: x[:7])
df_dict = dict(zip(df2.DATE, df2.INDPRO))
df['INDPRO'] = df['archive_date'].transform(lambda x: x.strftime('%Y-%m'))
df['INDPRO'].replace(to_replace=df_dict, inplace=True)

df3 = pd.read_csv('UNRATE.csv')
df3.DATE = df3.DATE.transform(lambda x: x[:7])
df_dict = dict(zip(df3.DATE, df3.UNRATE))
df['UNRATE'] = df['archive_date'].transform(lambda x: x.strftime('%Y-%m'))
df['UNRATE'].replace(to_replace=df_dict, inplace=True)

df4 = pd.read_csv('USSLIND.csv')
df4.DATE = df4.DATE.transform(lambda x: x[:7])
df_dict = dict(zip(df4.DATE, df4.USSLIND))
df['USSLIND'] = df['archive_date'].transform(lambda x: x.strftime('%Y-%m'))
df['USSLIND'].replace(to_replace=df_dict, inplace=True)

# convert daily to monthly
df5 = pd.read_csv('DGS10.csv')
df5.index = pd.to_datetime(df5.DATE)
df5.DGS10 = pd.to_numeric(df5.DGS10,errors='coerce')
df5 = df5.resample('M').mean()
df5['DATE'] = df5.index
df5.DATE = df5.DATE.transform(lambda x: x.strftime('%Y-%m'))
df_dict = dict(zip(df5.DATE, df5.DGS10))
df['DGS10'] = df['archive_date'].transform(lambda x: x.strftime('%Y-%m'))
df['DGS10'].replace(to_replace=df_dict, inplace=True)


df6 = pd.read_csv('SP500.csv')
df6.index = pd.to_datetime(df6.DATE)
df6.SP500 = pd.to_numeric(df6.SP500,errors='coerce')
df6 = df6.resample('M').mean()
df6['DATE'] = df6.index
df6.DATE = df6.DATE.transform(lambda x: x.strftime('%Y-%m'))
df_dict = dict(zip(df6.DATE, df6.SP500))
df['SP500'] = df['archive_date'].transform(lambda x: x.strftime('%Y-%m'))
df['SP500'].replace(to_replace=df_dict, inplace=True)


# convert quaterly to monthly
df7 = pd.read_csv('ACILT100.csv')
df7.index = pd.to_datetime(df7.DATE)
df7.ACILT100 = pd.to_numeric(df7.ACILT100,errors='coerce')
df7 = df7.resample('M').bfill()
df7['DATE'] = df7.index
df7.DATE = df7.DATE.transform(lambda x: x.strftime('%Y-%m'))
df_dict = dict(zip(df7.DATE, df7.ACILT100))
df['ACILT100'] = df['archive_date'].transform(lambda x: x.strftime('%Y-%m'))
df['ACILT100'].replace(to_replace=df_dict, inplace=True)
df['ACILT100'] = pd.to_numeric(df['ACILT100'],errors='coerce')



df8 = pd.read_csv('DRBLACBS.csv')
df8.index = pd.to_datetime(df8.DATE)
df8.DRBLACBS = pd.to_numeric(df8.DRBLACBS,errors='coerce')
df8 = df8.resample('M').bfill()
df8['DATE'] = df8.index
df8.DATE = df8.DATE.transform(lambda x: x.strftime('%Y-%m'))
df_dict = dict(zip(df8.DATE, df8.DRBLACBS))
df['DRBLACBS'] = df['archive_date'].transform(lambda x: x.strftime('%Y-%m'))
df['DRBLACBS'].replace(to_replace=df_dict, inplace=True)
df['DRBLACBS'] = pd.to_numeric(df['DRBLACBS'],errors='coerce')

# ACILT100 and DRBLACBS 
df = df.fillna(df.median(), inplace=True)


#%% save data
df.to_pickle('fulldata_cleaned.pkl.xz')
# use most recent model's production data as the test data (CnI 1.2 is in prod since 04/04/2016)
data_test = df.query('archive_date>="20170101"') #5670
data_train = df.query('archive_date<"20170101"')  # 26079
data_test.reset_index(drop=True, inplace=True)
data_train.reset_index(drop=True, inplace=True)
data_test.to_pickle('data_test_2017_cleaned.pkl.xz')
data_train.to_pickle('data_train_2017_cleaned.pkl.xz')




#%% prepare ML ready data
cols=['vulnerability',
 'ssor',
 'mgmt_resp',
 'waiver_mod',
 'division',
 'access_outside_capital',
 'cash_operating_profit',
 'end_cash_equiv_by_tot_liab',
 'ending_cash_equiv',
 'excp_underwrite_for_leverage',
 'info_rptg_timely_manner',
 'kmvedf',
 'management_quality',
 'market_outlook_of_borrower',
 'net_profit',
 'net_profit_margin',
 'net_sales',
 'pct_revenue_3_large_custs',
 'public',
 'quantitative_as_pct_possible',
 'quantitative_score',
 'tangible_net_worth',
 'total_assets',
 'total_debt',
 'total_liab_by_tang_net_worth',
 'total_liabilities',
 'exposure_seniority',
 'commitment',
 'outstanding',
 'Secured by blanket lien on total assets',
 'Secured by others',
 'Secured by specific collateral',
 'Unsecured',
 'unknown_security',
 'CREL',
 'LINE',
 'OTHERS',
 'RC',
 'TL',
 '100',
 '200',
 '300',
 '400',
 '500',
 '600',
 '700',
 '800',
 '900',
 'cyear',
 '11',
 '21',
 '22',
 '23',
 '31',
 '32',
 '33',
 '42',
 '44',
 '45',
 '48',
 '49',
 '51',
 '52',
 '53',
 '54',
 '55',
 '56',
 '61',
 '62',
 '71',
 '72',
 '81',
 '92',
 '99',
 'CPIAUCSL',
 'INDPRO',
 'UNRATE',
 'USSLIND',
 'DGS10',
 'SP500',
 'ACILT100',
 'DRBLACBS']

ML_df = df[cols].copy()

ML_df.to_pickle('fulldata_ready.pkl.xz')
# use most recent model's production data as the test data (CnI 1.2 is in prod since 04/04/2016)
data_test = data_test[cols]
data_train = data_train[cols]
data_test.to_pickle('data_test_ready.pkl.xz')
data_train.to_pickle('data_train_ready.pkl.xz')# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:04:56 2017

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier 
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
import matplotlib.pyplot as plt
import time


def Match(y_true, y_est):
    return (sum((y_true-y_est)==0) / len(y_true))

from sklearn.metrics import  make_scorer
match = make_scorer(Match)
somersd = make_scorer(SomersD)



#%%
data_train = pd.read_pickle('data\data_train_ready.pkl.xz')
data_test = pd.read_pickle('data\data_test_ready.pkl.xz')

##################### division='bbg' subsample #############
data_train = data_train.query('division==0')
data_train.drop('division', axis=1,inplace=True)
data_train.reset_index(drop=False, inplace=True)
data_test = data_test.query('division==0')
data_test.drop('division', axis=1,inplace=True)
data_test.reset_index(drop=False, inplace=True)
#choose target factor and generate train data and test data
X_train = data_train.iloc[:,5:]
y_train = data_train.iloc[:,3]
X_test = data_test.iloc[:,5:]
y_test = data_test.iloc[:,3]
    
#%% GradientBoosting
# 1st round
start_time = time.time()
parameters = {'learning_rate':[0.2,0.5,0.8], 'n_estimators':[300,400],'max_depth':[10],'random_state':[1250,1270,1290]}
clf = GradientBoostingClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))

results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})
   

gb_params = {
'learning_rate': 0.2,
'n_estimators': 300,
'max_depth': 10,
'random_state':1251
}


model = GradientBoostingClassifier(**gb_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.59731934731934733


#%% RandomForestClassifier
# 1st round
start_time = time.time()
parameters = {'max_features':[30,40,50], 'n_estimators':[1000,2000,2500, 3000], 'random_state':[1251,1271]}
clf = RandomForestClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})

start_time = time.time()
parameters = {'max_features':[30], 'n_estimators':[1000,2000], 'random_state':[1251,1271,1291]}
clf = RandomForestClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


rf_params = {
'max_features':30,
'n_estimators':2000,
'random_state':1251
}

model = RandomForestClassifier(**rf_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.59324009324009319


#%% ExtraTreesClassifier
# 1st round
start_time = time.time()
parameters = {'max_features':[30,40,50], 'n_estimators':[1000,2000,2500, 3000], 'random_state':[1251,1271]}
clf = ExtraTreesClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


et_params = {
'max_features':50,
'n_estimators':1000,
'random_state':1251
}


model = ExtraTreesClassifier(**et_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.60547785547785549# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:04:56 2017

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier 
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
import matplotlib.pyplot as plt
import time


def Match(y_true, y_est):
    return (sum((y_true-y_est)==0) / len(y_true))

from sklearn.metrics import  make_scorer
match = make_scorer(Match)
somersd = make_scorer(SomersD)



#%%
data_full = pd.read_pickle('df.pkl.xz')
# division='bbg' subsample 
df = data_full.query('division==0')
df.drop('division', axis=1,inplace=True)
df.reset_index(drop=True, inplace=True)

#choose target factor and generate train data and test data
y = df.iloc[:,2]
X = df.iloc[:,4:]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=1251)




#%% GradientBoosting
# 1st round
start_time = time.time()
parameters = {'learning_rate':[0.2,0.5,0.8], 'n_estimators':[300,400],'max_depth':[10],'random_state':[1250,1270,1290]}
clf = GradientBoostingClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))

results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})
   

gb_params = {
'learning_rate': 0.2,
'n_estimators': 300,
'max_depth': 10,
'random_state':1251
}


model = GradientBoostingClassifier(**gb_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.80023571007660577


#%% RandomForestClassifier
# 1st round
start_time = time.time()
parameters = {'max_features':[30,40,50], 'n_estimators':[1000,2000,2500, 3000], 'random_state':[1251,1271]}
clf = RandomForestClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})

start_time = time.time()
parameters = {'max_features':[30], 'n_estimators':[1000,2000], 'random_state':[1251,1271,1291]}
clf = RandomForestClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


rf_params = {
'max_features':30,
'n_estimators':2000,
'random_state':1251
}

model = RandomForestClassifier(**rf_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.79728933411903358


#%% ExtraTreesClassifier
# 1st round
start_time = time.time()
parameters = {'max_features':[40,50], 'n_estimators':[1000,2000,2500, 3000], 'random_state':[1251,1271,1291]}
clf = ExtraTreesClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


et_params = {
'max_features':50,
'n_estimators':2500,
'random_state':1251
}


model = ExtraTreesClassifier(**et_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.79728933411903358# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 16:44:18 2017

@author: ub71894 (4e8e6d0b), CSG
"""



import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD, getTMnotches

from xgboost.sklearn import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier 
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from sklearn.externals import joblib
import matplotlib.pyplot as plt
import time

def Match(y_true, y_est):
    return (sum((y_true-y_est)==0) / len(y_true))

from sklearn.metrics import  make_scorer
match = make_scorer(Match)
somersd = make_scorer(SomersD)


data_train = pd.read_pickle('data\data_train_ready.pkl.xz')
data_test = pd.read_pickle('data\data_test_ready.pkl.xz')

##################### division='bbg' subsample #############
data_train = data_train.query('division==0')
data_train.drop('division', axis=1,inplace=True)
data_train.reset_index(drop=False, inplace=True)
data_test = data_test.query('division==0')
data_test.drop('division', axis=1,inplace=True)
data_test.reset_index(drop=False, inplace=True)
#choose target factor and generate train data and test data
X_train = data_train.iloc[:,5:]
y_train = data_train.iloc[:,3]
X_test = data_test.iloc[:,5:]
y_test = data_test.iloc[:,3]

#%%

ntrain = X_train.shape[0]
ntest  = X_test.shape[0]
seed   = 1251
nfolds = 5
kf = KFold(nfolds , random_state = seed)



class SklearnHelper(object):
    def __init__(self,clf, seed = 0 , params = None):
        params["random_state"] = seed
        self.clf = clf(**params)
    def train(self,X_train, y_train):
        self.clf.fit(X_train,y_train)
    def predict(self,x):
        return(self.clf.predict(x))
    def fit(self,x,y):
        return(self.clf.fit(x,y))
    def feature_importance(self,x,y):
        print(self.clf.fit(x,y).feature_importances_)


def get_oof(clf, X_train_df ,y_train_df, X_test_df):
    X_train = X_train_df.as_matrix()
    y_train = y_train_df.as_matrix()
    X_test = X_test_df.as_matrix()

    oof_train = np.zeros((ntrain,))
    oof_test  = np.zeros((ntest,))
    oof_test_skf = np.empty((nfolds, ntest))
    
    for i ,(train_index,test_index) in enumerate(kf.split(X_train)):
        x_tr = X_train[train_index]
        y_tr = y_train[train_index]
        x_te = X_train[test_index]
        
        clf.train(x_tr, y_tr)
        oof_train[test_index] = clf.predict(x_te)
        oof_test_skf[i,:] = clf.predict(X_test)

    oof_test[:] = oof_test_skf.mean(axis=0)
    
    return (oof_train.reshape(-1, 1), oof_test.reshape(-1, 1))



#%% Base First-Level Models
# optimal params from previous find tuning:
 
gb_params = {
'learning_rate': 0.2,
'n_estimators': 300,
'max_depth': 10,
'random_state':1251
}


rf_params = {
'max_features':30,
'n_estimators':2000,
'random_state':1251
}

et_params = {
'max_features':50,
'n_estimators':1000,
'random_state':1251
}

gb = SklearnHelper(clf=GradientBoostingClassifier, seed=seed, params=gb_params)
rf = SklearnHelper(clf=RandomForestClassifier, seed=seed, params=rf_params)
et = SklearnHelper(clf=ExtraTreesClassifier, seed=seed, params=et_params)

gb_oof_train, gb_oof_test = get_oof(gb, X_train, y_train, X_test) 
rf_oof_train, rf_oof_test = get_oof(rf, X_train, y_train, X_test) 
et_oof_train, et_oof_test = get_oof(et, X_train, y_train, X_test) 

# then get the date for second level model

X_train_l2 = np.concatenate((gb_oof_train,  rf_oof_train, et_oof_train), axis=1)
X_test_l2  = np.concatenate((gb_oof_test, rf_oof_test, et_oof_test), axis=1)


#%% second level model

#%% Gradient Boosting parameters
start_time = time.time()
parameters = {'learning_rate':[0.1,0.2,0.3], 'n_estimators':[300,400,500,600,700],'max_depth':[3,5,7,9],'random_state':[1251,1271]}
clf = GradientBoostingClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


gbm = GradientBoostingClassifier(
 n_estimators = 700,
 max_depth =  5,
 learning_rate = 0.1,
 random_state=1251
)

gbm.fit(X_train_l2, y_train)
predictions = gbm.predict(X_test_l2)
#SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.55710955710955712


#%% LR 
start_time = time.time()
parameters = {'C':[3,5,8,10],'penalty':['l2'], 'multi_class':['ovr','multinomial'],'solver':['newton-cg']}
clf =  LogisticRegression()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


lr = LogisticRegression(C=5, penalty='l2', multi_class='multinomial', solver='newton-cg')
lr.fit(X_train_l2, y_train)
predictions = lr.predict(X_test_l2)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.55477855477855476


#%% XGBoost
start_time = time.time()
param_test1 = {
'learning_rate':[0.1,0.2,0.3],
    'seed':[1250,1270,1290],
    'max_depth':range(3,10,2),
    'min_child_weight':range(1,6,2)
}
gridsearch = GridSearchCV(estimator = XGBClassifier( n_estimators=140, subsample=0.8, colsample_bytree=0.8,
                                        objective= 'binary:logistic'), 
                       param_grid = param_test1, scoring=match, cv=5)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


start_time = time.time()
param_test1 = {
'n_estimators': range(50,1500,50),
'seed': [1251,1271,1290]
}
gridsearch = GridSearchCV(estimator = XGBClassifier(subsample=0.8, colsample_bytree=0.8, objective= 'binary:logistic', 
    learning_rate=0.1, max_depth=3,min_child_weight=5), 
                       param_grid = param_test1, scoring=match, cv=5)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})




xgb = XGBClassifier(subsample=0.8, colsample_bytree=0.8, objective= 'binary:logistic', 
    learning_rate=0.1,min_child_weight=5,n_estimators=200, max_depth=3, seed=1251)
xgb.fit(X_train_l2, y_train)
predictions = xgb.predict(X_test_l2)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.55885780885780889



#%% 
from sklearn.externals import joblib
# Save to file in the current working directory
mgmt_resp_file ='mgmt_resp_model.pkl'
joblib.dump(xgb, mgmt_resp_file)

# Load from file

mgmt_resp_file ='mgmt_resp_model.pkl'
joblib_model = joblib.load(mgmt_resp_file)


predictions = joblib_model.predict(X_test_l2)
Match(y_test, predictions)
predictions = pd.Series(predictions)
predictions.to_pickle('mgmt_resp_prediction.pickle')


#%%
import seaborn as sns
from sklearn.metrics import confusion_matrix
conf= pd.DataFrame(confusion_matrix(y_test, predictions))
conf.index.name='True Letters'
conf.columns.name='Predicted Letters'
sns.heatmap(conf, annot=True, fmt="d", linewidths=.5, xticklabels='ABCDEF', yticklabels='ABCDEF', center=0,cmap="YlGnBu")
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:04:56 2017

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier 
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
import matplotlib.pyplot as plt
import time


def Match(y_true, y_est):
    return (sum((y_true-y_est)==0) / len(y_true))

from sklearn.metrics import  make_scorer
match = make_scorer(Match)
somersd = make_scorer(SomersD)



#%%
data_train = pd.read_pickle('data\data_train_ready.pkl.xz')
data_test = pd.read_pickle('data\data_test_ready.pkl.xz')

##################### division='bbg' subsample #############
data_train = data_train.query('division==0')
data_train.drop('division', axis=1,inplace=True)
data_train.reset_index(drop=False, inplace=True)
data_test = data_test.query('division==0')
data_test.drop('division', axis=1,inplace=True)
data_test.reset_index(drop=False, inplace=True)
#choose target factor and generate train data and test data
X_train = data_train.iloc[:,5:]
y_train = data_train.iloc[:,2]
X_test = data_test.iloc[:,5:]
y_test = data_test.iloc[:,2]
    
#%% GradientBoosting
# 1st round
start_time = time.time()
parameters = {'learning_rate':[0.2,0.3,0.5,0.8], 'n_estimators':[300,400,500,600,700],'max_depth':[6,10,12,15],'random_state':[1251,1271]}
clf = GradientBoostingClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))

results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})
   

gb_params = {
'learning_rate': 0.2,
'n_estimators': 300,
'max_depth': 10,
'random_state':1251
}


model = GradientBoostingClassifier(**gb_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.62820512820512819



#%% RandomForestClassifier
# 1st round
start_time = time.time()
parameters = {'max_features':[30,40,50], 'n_estimators':[1000,2000,2500, 3000], 'random_state':[1251,1271]}
clf = RandomForestClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


rf_params = {
'max_features':50,
'n_estimators':3000,
'random_state':1251
}

model = RandomForestClassifier(**rf_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.62412587412587417


#%% ExtraTreesClassifier
# 1st round
start_time = time.time()
parameters = {'max_features':[30,40,50], 'n_estimators':[1000,2000,2500, 3000], 'random_state':[1251,1271]}
clf = ExtraTreesClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})

# 2nd round
start_time = time.time()
parameters = {'max_features':[50], 'n_estimators':[1000,2000,3000], 'random_state':[1250,1270,1290]}
clf = ExtraTreesClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


et_params = {
'max_features':50,
'n_estimators':1000,
'random_state':1251
}


model = ExtraTreesClassifier(**et_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.62296037296037299# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 16:44:18 2017

@author: ub71894 (4e8e6d0b), CSG
"""



import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD, getTMnotches

from xgboost.sklearn import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier 
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from sklearn.externals import joblib
import matplotlib.pyplot as plt
import time

def Match(y_true, y_est):
    return (sum((y_true-y_est)==0) / len(y_true))

from sklearn.metrics import  make_scorer
match = make_scorer(Match)
somersd = make_scorer(SomersD)


data_train = pd.read_pickle('data\data_train_ready.pkl.xz')
data_test = pd.read_pickle('data\data_test_ready.pkl.xz')

##################### division='bbg' subsample #############
data_train = data_train.query('division==0')
data_train.drop('division', axis=1,inplace=True)
data_train.reset_index(drop=False, inplace=True)
data_test = data_test.query('division==0')
data_test.drop('division', axis=1,inplace=True)
data_test.reset_index(drop=False, inplace=True)
#choose target factor and generate train data and test data
X_train = data_train.iloc[:,5:]
y_train = data_train.iloc[:,2]
X_test = data_test.iloc[:,5:]
y_test = data_test.iloc[:,2]

#%%

ntrain = X_train.shape[0]
ntest  = X_test.shape[0]
seed   = 1251
nfolds = 5
kf = KFold(nfolds , random_state = seed)



class SklearnHelper(object):
    def __init__(self,clf, seed = 0 , params = None):
        params["random_state"] = seed
        self.clf = clf(**params)
    def train(self,X_train, y_train):
        self.clf.fit(X_train,y_train)
    def predict(self,x):
        return(self.clf.predict(x))
    def fit(self,x,y):
        return(self.clf.fit(x,y))
    def feature_importance(self,x,y):
        print(self.clf.fit(x,y).feature_importances_)


def get_oof(clf, X_train_df ,y_train_df, X_test_df):
    X_train = X_train_df.as_matrix()
    y_train = y_train_df.as_matrix()
    X_test = X_test_df.as_matrix()

    oof_train = np.zeros((ntrain,))
    oof_test  = np.zeros((ntest,))
    oof_test_skf = np.empty((nfolds, ntest))
    
    for i ,(train_index,test_index) in enumerate(kf.split(X_train)):
        x_tr = X_train[train_index]
        y_tr = y_train[train_index]
        x_te = X_train[test_index]
        
        clf.train(x_tr, y_tr)
        oof_train[test_index] = clf.predict(x_te)
        oof_test_skf[i,:] = clf.predict(X_test)

    oof_test[:] = oof_test_skf.mean(axis=0)
    
    return (oof_train.reshape(-1, 1), oof_test.reshape(-1, 1))



#%% Base First-Level Models
# optimal params from previous find tuning:
 
gb_params = {
'learning_rate': 0.2,
'n_estimators': 300,
'max_depth': 10,
'random_state':1251
}


rf_params = {
'max_features':50,
'n_estimators':3000,
'random_state':1251
}

et_params = {
'max_features':50,
'n_estimators':1000,
'random_state':1251
}

gb = SklearnHelper(clf=GradientBoostingClassifier, seed=seed, params=gb_params)
rf = SklearnHelper(clf=RandomForestClassifier, seed=seed, params=rf_params)
et = SklearnHelper(clf=ExtraTreesClassifier, seed=seed, params=et_params)

gb_oof_train, gb_oof_test = get_oof(gb, X_train, y_train, X_test) 
rf_oof_train, rf_oof_test = get_oof(rf, X_train, y_train, X_test) 
et_oof_train, et_oof_test = get_oof(et, X_train, y_train, X_test) 

# then get the date for second level model

X_train_l2 = np.concatenate((gb_oof_train,  rf_oof_train, et_oof_train), axis=1)
X_test_l2  = np.concatenate((gb_oof_test, rf_oof_test, et_oof_test), axis=1)


#%% second level model

#%% Gradient Boosting parameters
start_time = time.time()
parameters = {'learning_rate':[0.1,0.2,0.3], 'n_estimators':[300,400,500,600,700],'max_depth':[3,5,7,9],'random_state':[1251,1271]}
clf = GradientBoostingClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


gbm = GradientBoostingClassifier(
 n_estimators = 300,
 max_depth =  3,
 learning_rate = 0.1,
 random_state=1251
)

gbm.fit(X_train_l2, y_train)
predictions = gbm.predict(X_test_l2)
#SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.61771561771561767


#%% LR 
start_time = time.time()
parameters = {'C':[3,5,8,10],'penalty':['l2'], 'multi_class':['ovr','multinomial'],'solver':['newton-cg']}
clf =  LogisticRegression()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


lr = LogisticRegression(C=5, penalty='l2', multi_class='multinomial', solver='newton-cg')
lr.fit(X_train_l2, y_train)
predictions = lr.predict(X_test_l2)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.62529137529137524



#%% XGBoost
start_time = time.time()
param_test1 = {
'learning_rate':[0.1,0.2,0.3],
    'seed':[1250,1270,1290],
    'max_depth':range(3,10,2),
    'min_child_weight':range(1,6,2)
}
gridsearch = GridSearchCV(estimator = XGBClassifier( n_estimators=140, subsample=0.8, colsample_bytree=0.8,
                                        objective= 'binary:logistic'), 
                       param_grid = param_test1, scoring=match, cv=5)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


start_time = time.time()
param_test1 = {
'max_depth': range(3,7,2),
'n_estimators': range(50,1500,50),
'seed': [1251,1271,1290]
}
gridsearch = GridSearchCV(estimator = XGBClassifier(subsample=0.8, colsample_bytree=0.8, objective= 'binary:logistic', 
    learning_rate=0.1,min_child_weight=3), 
                       param_grid = param_test1, scoring=match, cv=5)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})




xgb = XGBClassifier(subsample=0.8, colsample_bytree=0.8, objective= 'binary:logistic', 
    learning_rate=0.1,min_child_weight=3,n_estimators=50, max_depth=3, seed=1251)
xgb.fit(X_train_l2, y_train)
predictions = xgb.predict(X_test_l2)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.62878787878787878



#%% 
from sklearn.externals import joblib
# Save to file in the current working directory
ssor_file ='ssor_model.pkl'
joblib.dump(xgb, ssor_file)

# Load from file

ssor_file ='ssor_model.pkl'
joblib_model = joblib.load(ssor_file)


predictions = joblib_model.predict(X_test_l2)
Match(y_test, predictions)
predictions = pd.Series(predictions)
predictions.to_pickle('ssor_prediction.pickle')


#%%
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix
import seaborn as sns
combo = pd.DataFrame({'True':y_test,'Predictions':predictions})
CreateBenchmarkMatrix(combo,'Matrix_Output.xlsx', 'Benchmarking Matrix','True', 'Predictions', PDRR=(1,9))

sns.heatmap(combo, center=0)


from sklearn.metrics import confusion_matrix
conf= pd.DataFrame(confusion_matrix(y_test, predictions))
conf.index.name='True Letters'
conf.columns.name='Predicted Letters'
sns.heatmap(conf, annot=True, fmt="d", linewidths=.5, xticklabels='ABCD', yticklabels='ABCD', center=0,cmap="YlGnBu")
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:04:56 2017

@author: ub71894 (4e8e6d0b), CSG
""" 

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\projects\machinelearning")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier 
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
import matplotlib.pyplot as plt
import time


def Match(y_true, y_est):
    return (sum((y_true-y_est)==0) / len(y_true))

from sklearn.metrics import  make_scorer
match = make_scorer(Match)
somersd = make_scorer(SomersD)



#%%
data_train = pd.read_pickle('data\data_train_ready.pkl.xz')
data_test = pd.read_pickle('data\data_test_ready.pkl.xz')

##################### division='bbg' subsample #############
data_train = data_train.query('division==0')
data_train.drop('division', axis=1,inplace=True)
data_train.reset_index(drop=False, inplace=True)
data_test = data_test.query('division==0')
data_test.drop('division', axis=1,inplace=True)
data_test.reset_index(drop=False, inplace=True)
#choose target factor and generate train data and test data
X_train = data_train.iloc[:,5:]
y_train = data_train.iloc[:,1]
X_test = data_test.iloc[:,5:]
y_test = data_test.iloc[:,1]
    
#%% GradientBoosting
# 1st round
start_time = time.time()
parameters = {'learning_rate':[0.2,0.5,0.8], 'n_estimators':[300,400],'max_depth':[10],'random_state':[1250,1270,1290]}
clf = GradientBoostingClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))

results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})
   

gb_params = {
'learning_rate': 0.8,
'n_estimators': 300,
'max_depth': 10,
'random_state':1251
}


model = GradientBoostingClassifier(**gb_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.93298368298368295



#%% RandomForestClassifier
# 1st round
start_time = time.time()
parameters = {'max_features':[30,40,50], 'n_estimators':[1000,2000,2500, 3000], 'random_state':[1251,1271]}
clf = RandomForestClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


rf_params = {
'max_features':30,
'n_estimators':1000,
'random_state':1251
}

model = RandomForestClassifier(**rf_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.93939393939393945


#%% ExtraTreesClassifier
# 1st round
start_time = time.time()
parameters = {'max_features':[30,40,50], 'n_estimators':[1000,2000,2500, 3000], 'random_state':[1251,1271]}
clf = ExtraTreesClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})

# 2nd round
start_time = time.time()
parameters = {'max_features':[30], 'n_estimators':[1000,2000,3000], 'random_state':[1250,1270,1290]}
clf = ExtraTreesClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


et_params = {
'max_features':30,
'n_estimators':2000,
'random_state':1251
}


model = ExtraTreesClassifier(**et_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.94522144522144524# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 16:44:18 2017

@author: ub71894 (4e8e6d0b), CSG
"""



import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD, getTMnotches

from xgboost.sklearn import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier 
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from sklearn.externals import joblib
import matplotlib.pyplot as plt
import time

def Match(y_true, y_est):
    return (sum((y_true-y_est)==0) / len(y_true))

from sklearn.metrics import  make_scorer
match = make_scorer(Match)
somersd = make_scorer(SomersD)


data_train = pd.read_pickle('data\data_train_ready.pkl.xz')
data_test = pd.read_pickle('data\data_test_ready.pkl.xz')

##################### division='bbg' subsample #############
data_train = data_train.query('division==0')
data_train.drop('division', axis=1,inplace=True)
data_train.reset_index(drop=False, inplace=True)
data_test = data_test.query('division==0')
data_test.drop('division', axis=1,inplace=True)
data_test.reset_index(drop=False, inplace=True)
#choose target factor and generate train data and test data
X_train = data_train.iloc[:,5:]
y_train = data_train.iloc[:,1]
X_test = data_test.iloc[:,5:]
y_test = data_test.iloc[:,1]

#%%

ntrain = X_train.shape[0]
ntest  = X_test.shape[0]
seed   = 1251
nfolds = 5
kf = KFold(nfolds , random_state = seed)



class SklearnHelper(object):
    def __init__(self,clf, seed = 0 , params = None):
        params["random_state"] = seed
        self.clf = clf(**params)
    def train(self,X_train, y_train):
        self.clf.fit(X_train,y_train)
    def predict(self,x):
        return(self.clf.predict(x))
    def fit(self,x,y):
        return(self.clf.fit(x,y))
    def feature_importance(self,x,y):
        print(self.clf.fit(x,y).feature_importances_)


def get_oof(clf, X_train_df ,y_train_df, X_test_df):
    X_train = X_train_df.as_matrix()
    y_train = y_train_df.as_matrix()
    X_test = X_test_df.as_matrix()

    oof_train = np.zeros((ntrain,))
    oof_test  = np.zeros((ntest,))
    oof_test_skf = np.empty((nfolds, ntest))
    
    for i ,(train_index,test_index) in enumerate(kf.split(X_train)):
        x_tr = X_train[train_index]
        y_tr = y_train[train_index]
        x_te = X_train[test_index]
        
        clf.train(x_tr, y_tr)
        oof_train[test_index] = clf.predict(x_te)
        oof_test_skf[i,:] = clf.predict(X_test)

    oof_test[:] = oof_test_skf.mean(axis=0)
    
    return (oof_train.reshape(-1, 1), oof_test.reshape(-1, 1))



#%% Base First-Level Models
# optimal params from previous find tuning:
 
gb_params = {
'learning_rate': 0.8,
'n_estimators': 300,
'max_depth': 10,
'random_state':1251
}


rf_params = {
'max_features':30,
'n_estimators':1000,
'random_state':1251
}

et_params = {
'max_features':30,
'n_estimators':2000,
'random_state':1251
}

gb = SklearnHelper(clf=GradientBoostingClassifier, seed=seed, params=gb_params)
rf = SklearnHelper(clf=RandomForestClassifier, seed=seed, params=rf_params)
et = SklearnHelper(clf=ExtraTreesClassifier, seed=seed, params=et_params)

gb_oof_train, gb_oof_test = get_oof(gb, X_train, y_train, X_test) 
rf_oof_train, rf_oof_test = get_oof(rf, X_train, y_train, X_test) 
et_oof_train, et_oof_test = get_oof(et, X_train, y_train, X_test) 

# then get the date for second level model

X_train_l2 = np.concatenate((gb_oof_train,  rf_oof_train, et_oof_train), axis=1)
X_test_l2  = np.concatenate((gb_oof_test, rf_oof_test, et_oof_test), axis=1)


#%% second level model

#%% Gradient Boosting parameters
start_time = time.time()
parameters = {'learning_rate':[0.1,0.2,0.3], 'n_estimators':[300,400,500,600,700],'max_depth':[3,5,7,9],'random_state':[1251,1271]}
clf = GradientBoostingClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


gbm = GradientBoostingClassifier(
 n_estimators = 300,
 max_depth =  3,
 learning_rate = 0.1,
 random_state=1251
)

gbm.fit(X_train_l2, y_train)
predictions = gbm.predict(X_test_l2)
#SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.94755244755244761


#%% LR 
start_time = time.time()
parameters = {'C':[3,5,8,10],'penalty':['l2'], 'multi_class':['ovr','multinomial'],'solver':['newton-cg']}
clf =  LogisticRegression()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


lr = LogisticRegression(C=5, penalty='l2', multi_class='multinomial', solver='newton-cg')
lr.fit(X_train_l2, y_train)
predictions = lr.predict(X_test_l2)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.94871794871794868



#%% XGBoost
start_time = time.time()
param_test1 = {
'learning_rate':[0.1,0.2,0.3],
    'seed':[1250,1270,1290],
    'max_depth':range(3,10,2),
    'min_child_weight':range(1,6,2)
}
gridsearch = GridSearchCV(estimator = XGBClassifier( n_estimators=140, subsample=0.8, colsample_bytree=0.8,
                                        objective= 'binary:logistic'), 
                       param_grid = param_test1, scoring=match, cv=5)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


start_time = time.time()
param_test1 = {
'min_child_weight':range(1,6,2),
'n_estimators': range(50,1500,50),
'seed': [1251,1271,1290]
}
gridsearch = GridSearchCV(estimator = XGBClassifier(subsample=0.8, colsample_bytree=0.8, objective= 'binary:logistic', 
    learning_rate=0.1, max_depth=3), 
                       param_grid = param_test1, scoring=match, cv=5)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})




xgb = XGBClassifier(subsample=0.8, colsample_bytree=0.8, objective= 'binary:logistic', 
    learning_rate=0.1,min_child_weight=1,n_estimators=50, max_depth=3, seed=1251)
xgb.fit(X_train_l2, y_train)
predictions = xgb.predict(X_test_l2)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.94755244755244761



#%% 
from sklearn.externals import joblib
# Save to file in the current working directory
vulnerability_file ='vulnerability_model.pkl'
joblib.dump(lr, vulnerability_file)

# Load from file

vulnerability_file ='vulnerability_model.pkl'
joblib_model = joblib.load(vulnerability_file)


predictions = joblib_model.predict(X_test_l2)
Match(y_test, predictions)
predictions = pd.Series(predictions)
predictions.to_pickle('vulnerability_prediction.pickle')


#%%
import seaborn as sns
from sklearn.metrics import confusion_matrix
conf= pd.DataFrame(confusion_matrix(y_test, predictions))
conf.index.name='True Letters'
conf.columns.name='Predicted Letters'
sns.heatmap(conf, annot=True, fmt="d", linewidths=.5, xticklabels='ABCD', yticklabels='ABCD', center=0,cmap="YlGnBu")
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:04:56 2017

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier 
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
import matplotlib.pyplot as plt
import time


def Match(y_true, y_est):
    return (sum((y_true-y_est)==0) / len(y_true))

from sklearn.metrics import  make_scorer
match = make_scorer(Match)
somersd = make_scorer(SomersD)



#%%
data_train = pd.read_pickle('data\data_train_ready.pkl.xz')
data_test = pd.read_pickle('data\data_test_ready.pkl.xz')

##################### division='bbg' subsample #############
data_train = data_train.query('division==0')
data_train.drop('division', axis=1,inplace=True)
data_train.reset_index(drop=False, inplace=True)
data_test = data_test.query('division==0')
data_test.drop('division', axis=1,inplace=True)
data_test.reset_index(drop=False, inplace=True)
#choose target factor and generate train data and test data
X_train = data_train.iloc[:,5:]
y_train = data_train.iloc[:,4]
X_test = data_test.iloc[:,5:]
y_test = data_test.iloc[:,4]
    
#%% GradientBoosting
# 1st round
start_time = time.time()
parameters = {'learning_rate':[0.2,0.5,0.8], 'n_estimators':[300,400],'max_depth':[10],'random_state':[1250,1270,1290]}
clf = GradientBoostingClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))

results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})
   

gb_params = {
'learning_rate': 0.2,
'n_estimators': 300,
'max_depth': 10,
'random_state':1270
}


model = GradientBoostingClassifier(**gb_params)
model.fit(X_train, y_train)


predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.55594405594405594


#%% RandomForestClassifier
# 1st round
start_time = time.time()
parameters = {'max_features':[50], 'n_estimators':[1000,2000,2500, 3000], 'random_state':[1251,1271,1291]}
clf = RandomForestClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


rf_params = {
'max_features':50,
'n_estimators':1000,
'random_state':1251
}

model = RandomForestClassifier(**rf_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.56876456876456871


#%% ExtraTreesClassifier
# 1st round
start_time = time.time()
parameters = {'max_features':[30,40,50], 'n_estimators':[1000,2000,2500, 3000], 'random_state':[1251,1271]}
clf = ExtraTreesClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


et_params = {
'max_features':50,
'n_estimators':1000,
'random_state':1251
}


model = ExtraTreesClassifier(**et_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.57284382284382285

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 27 16:44:18 2017

@author: ub71894 (4e8e6d0b), CSG
"""



import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD, getTMnotches

from xgboost.sklearn import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import AdaBoostClassifier, ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier 
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
from sklearn.externals import joblib
import matplotlib.pyplot as plt
import time

def Match(y_true, y_est):
    return (sum((y_true-y_est)==0) / len(y_true))

from sklearn.metrics import  make_scorer
match = make_scorer(Match)
somersd = make_scorer(SomersD)


data_train = pd.read_pickle('data\data_train_ready.pkl.xz')
data_test = pd.read_pickle('data\data_test_ready.pkl.xz')

##################### division='bbg' subsample #############
data_train = data_train.query('division==0')
data_train.drop('division', axis=1,inplace=True)
data_train.reset_index(drop=False, inplace=True)
data_test = data_test.query('division==0')
data_test.drop('division', axis=1,inplace=True)
data_test.reset_index(drop=False, inplace=True)
#choose target factor and generate train data and test data
X_train = data_train.iloc[:,5:]
y_train = data_train.iloc[:,4]
X_test = data_test.iloc[:,5:]
y_test = data_test.iloc[:,4]

#%%

ntrain = X_train.shape[0]
ntest  = X_test.shape[0]
seed   = 1251
nfolds = 5
kf = KFold(nfolds , random_state = seed)



class SklearnHelper(object):
    def __init__(self,clf, seed = 0 , params = None):
        params["random_state"] = seed
        self.clf = clf(**params)
    def train(self,X_train, y_train):
        self.clf.fit(X_train,y_train)
    def predict(self,x):
        return(self.clf.predict(x))
    def fit(self,x,y):
        return(self.clf.fit(x,y))
    def feature_importance(self,x,y):
        print(self.clf.fit(x,y).feature_importances_)


def get_oof(clf, X_train_df ,y_train_df, X_test_df):
    X_train = X_train_df.as_matrix()
    y_train = y_train_df.as_matrix()
    X_test = X_test_df.as_matrix()

    oof_train = np.zeros((ntrain,))
    oof_test  = np.zeros((ntest,))
    oof_test_skf = np.empty((nfolds, ntest))
    
    for i ,(train_index,test_index) in enumerate(kf.split(X_train)):
        x_tr = X_train[train_index]
        y_tr = y_train[train_index]
        x_te = X_train[test_index]
        
        clf.train(x_tr, y_tr)
        oof_train[test_index] = clf.predict(x_te)
        oof_test_skf[i,:] = clf.predict(X_test)

    oof_test[:] = oof_test_skf.mean(axis=0)
    
    return (oof_train.reshape(-1, 1), oof_test.reshape(-1, 1))



#%% Base First-Level Models
# optimal params from previous find tuning:
 
gb_params = {
'learning_rate': 0.8,
'n_estimators': 300,
'max_depth': 10,
'random_state':1251
}


rf_params = {
'max_features':50,
'n_estimators':1000,
'random_state':1251
}

et_params = {
'max_features':50,
'n_estimators':1000,
'random_state':1251
}

gb = SklearnHelper(clf=GradientBoostingClassifier, seed=seed, params=gb_params)
rf = SklearnHelper(clf=RandomForestClassifier, seed=seed, params=rf_params)
et = SklearnHelper(clf=ExtraTreesClassifier, seed=seed, params=et_params)

gb_oof_train, gb_oof_test = get_oof(gb, X_train, y_train, X_test) 
rf_oof_train, rf_oof_test = get_oof(rf, X_train, y_train, X_test) 
et_oof_train, et_oof_test = get_oof(et, X_train, y_train, X_test) 

# then get the date for second level model

X_train_l2 = np.concatenate((gb_oof_train,  rf_oof_train, et_oof_train), axis=1)
X_test_l2  = np.concatenate((gb_oof_test, rf_oof_test, et_oof_test), axis=1)


#%% second level model

#%% Gradient Boosting parameters
start_time = time.time()
parameters = {'learning_rate':[0.1,0.2,0.3], 'n_estimators':[300,400,500,600,700],'max_depth':[3,5,7,9],'random_state':[1251,1271]}
clf = GradientBoostingClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


gbm = GradientBoostingClassifier(
 n_estimators = 300,
 max_depth =  5,
 learning_rate = 0.1,
 random_state=1251
)

gbm.fit(X_train_l2, y_train)
predictions = gbm.predict(X_test_l2)
#SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.5466200466200466


#%% LR 
start_time = time.time()
parameters = {'C':[3,5,8,10],'penalty':['l2'], 'multi_class':['ovr','multinomial'],'solver':['newton-cg']}
clf =  LogisticRegression()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


lr = LogisticRegression(C=5, penalty='l2', multi_class='multinomial', solver='newton-cg')
lr.fit(X_train_l2, y_train)
predictions = lr.predict(X_test_l2)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.55769230769230771



#%% XGBoost
start_time = time.time()
param_test1 = {
'learning_rate':[0.1,0.2,0.3],
    'seed':[1250,1270,1290],
    'max_depth':range(3,10,2),
    'min_child_weight':range(1,6,2)
}
gridsearch = GridSearchCV(estimator = XGBClassifier( n_estimators=140, subsample=0.8, colsample_bytree=0.8,
                                        objective= 'binary:logistic'), 
                       param_grid = param_test1, scoring=match, cv=5)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})


start_time = time.time()
param_test1 = {
'n_estimators': range(50,1500,50),
'seed': [1251,1271,1290]
}
gridsearch = GridSearchCV(estimator = XGBClassifier(subsample=0.8, colsample_bytree=0.8, objective= 'binary:logistic', 
    learning_rate=0.1, max_depth=5, min_child_weight=5), 
                       param_grid = param_test1, scoring=match, cv=5)
gridsearch.fit(X_train_l2, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})




xgb = XGBClassifier(subsample=0.8, colsample_bytree=0.8, objective= 'binary:logistic', 
    learning_rate=0.1,min_child_weight=5,n_estimators=50, max_depth=5, seed=1251)
xgb.fit(X_train_l2, y_train)
predictions = xgb.predict(X_test_l2)
SomersD(y_test, predictions)
Match(y_test, predictions)
# 0.5466200466200466


#%% 
from sklearn.externals import joblib
# Save to file in the current working directory
waiver_mod_file ='waiver_mod_model.pkl'
joblib.dump(lr, waiver_mod_file)

# Load from file

waiver_mod_file ='waiver_mod_model.pkl'
joblib_model = joblib.load(waiver_mod_file)


predictions = joblib_model.predict(X_test_l2)
Match(y_test, predictions)
predictions = pd.Series(predictions)
predictions.to_pickle('waiver_mod_prediction.pickle')


#%%
import seaborn as sns
from sklearn.metrics import confusion_matrix
conf= pd.DataFrame(confusion_matrix(y_test, predictions))
conf.index.name='True Letters'
conf.columns.name='Predicted Letters'
sns.heatmap(conf, annot=True, fmt="d", linewidths=.5, xticklabels='ABCD', yticklabels='ABCD', center=0,cmap="YlGnBu")
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 12:04:56 2017

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\python\othercode\cat_SFA_chris")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split, KFold, GridSearchCV
import matplotlib.pyplot as plt
import time


def Match(y_true, y_est):
    return (sum((y_true-y_est)==0) / len(y_true))

from sklearn.metrics import  make_scorer
match = make_scorer(Match)
somersd = make_scorer(SomersD)



#%%
data_train = pd.read_pickle('data\data_train_ready.pkl.xz')
data_test = pd.read_pickle('data\data_test_ready.pkl.xz')

##################### division='bbg' subsample #############
data_train = data_train.query('division==0')
data_train.drop('division', axis=1,inplace=True)
data_train.reset_index(drop=False, inplace=True)
data_test = data_test.query('division==0')
data_test.drop('division', axis=1,inplace=True)
data_test.reset_index(drop=False, inplace=True)
#choose target factor and generate train data and test data
X_train = data_train.iloc[:,5:]
y_train = data_train.iloc[:,4]
X_test = data_test.iloc[:,5:]
y_test = data_test.iloc[:,4]
    


#%% Neural Networks
start_time = time.time()
parameters = {'hidden_layer_sizes':[(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10)], 'activation':['logistic', 'tanh', 'relu'],\
'alpha':[0.1,0.01,0.001,0.0001],'random_state':[1250,1270]}
clf = MLPClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})
   

start_time = time.time()
parameters = {'hidden_layer_sizes':[(4,)*2,(5,)*2,(6,)*2,(4,)*3,(5,)*3,(6,)*3,(4,)*4,(5,)*4,(6,)*4,(4,)*5,(5,)*5,(6,)*5,
(4,)*6,(5,)*6,(6,)*6,(4,)*7,(5,)*7,(6,)*7,(4,)*8,(5,)*8,(6,)*8,(4,)*9,(5,)*9,(6,)*9,(4,)*10,(5,)*10,(6,)*10], 
'activation':['logistic'],'alpha':[0.1],'random_state':[1250,1270,1290]}
clf = MLPClassifier()
gridsearch = GridSearchCV(clf, parameters, cv=5, scoring=match)
gridsearch.fit(X_train, y_train)
print("--- %s seconds ---" % (time.time() - start_time))
results = gridsearch.cv_results_
models = pd.DataFrame({'score':results['mean_test_score'],'rank':results['rank_test_score'], 'params':results['params']})
   






nn_params = {
'hidden_layer_sizes': (4,4,4),
'activation': 'relu',
'alpha': 0.001,
'random_state':1251
}


model = MLPClassifier(**nn_params)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
Match(y_test, predictions)
# 0.55594405594405594

['1_data_01_clean.py', '1_data_02_prepareMLdata.py', '2_MLStacking_mgmt_resp_layer1.py', '2_MLStacking_mgmt_resp_layer1_cv.py', '2_MLStacking_mgmt_resp_layer2.py', '2_MLStacking_ssor_layer1.py', '2_MLStacking_ssor_layer2.py', '2_MLStacking_vulnerability_layer1.py', '2_MLStacking_vulnerability_layer2.py', '2_MLStacking_waiver_mod_layer1.py', '2_MLStacking_waiver_mod_layer2.py', '3_NN_waiver_mod_layer1.py']
[116, 689, 822, 954, 1199, 1335, 1589, 1725, 1972, 2100, 2346, 2435]
