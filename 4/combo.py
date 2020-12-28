# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 23:29:46 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
dat = pd.read_excel(r'..\newdata\data_201006_201712_addBranch_3_jn_withCIF.xlsx')
dat = dat.query('DataPeriod!="Dev"')

gap = dat.query('DataPeriod=="Gap"')
gap.sort_values(by=['CUSTOMERID','Statement_Date'], inplace=True)
gap.drop_duplicates(subset=['CUSTOMERID','Statement_Date'], keep='last',inplace=True)
gap.dropna(subset=['CUSTOMERID','Statement_Date'], how='any', inplace=True)
gap.reset_index(drop=True, inplace=True)
gap = gap[['CUSTOMERID','ARCHIVEID','Statement_Date','statement_id','Obligor_name']]

gap.to_excel('customer_list_gap.xlsx')



data = dat.query('DataPeriod!="Gap"')
data.sort_values(by=['CUSTOMERID','archive_date'], inplace=True)
data.drop_duplicates(subset=['CUSTOMERID','archive_date'], keep='last',inplace=True)
data.dropna(subset=['CUSTOMERID','archive_date'], how='any', inplace=True)
data.reset_index(drop=True, inplace=True)
#data = data[['CUSTOMERID','archive_date','Obligor_name']]
data = data[['CUSTOMERID','archive_date','ARCHIVEID','Statement_Date','statement_id','Obligor_name']]
data.to_excel('customer_list_prod.xlsx')



# -*- coding: utf-8 -*-
"""
Created on Mon Sep 10 15:28:13 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import getTotalscore, getPDRR, getTM
from PDScorecardTool.Process import normalization, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping, ExtRating_mapping

import pickle

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
filehandler = open(r'spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)
dat = pd.read_pickle(r'MFA\test_2017.pkl.xz')

cols=[
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'size@EBITDA', 'size@Capitalization', 'ds@Interest Expense','size@Net_Sales', 'size@Total Debt', 
 'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital',
 'Override_Action',
 'RLA_Notches',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Underwriter_Guideline',
 'NAICS_Cd',
 ]
 
dat = dat[cols]
dat.dropna(subset=model.quali_factor, how='any', inplace=True)
dat.reset_index(drop=True, inplace=True)
dat['Asset_Size'] = dat['size@Total Assets'].copy()
dat['size@Total Assets'] = np.log(1+dat['size@Total Assets'])

finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        dat[factor] = dat[factor].clip(np.nanmin(dat[factor][dat[factor] != -np.inf]), np.nanmax(dat[factor][dat[factor] != np.inf]))


model_output = getPDRR(dat, model, ms_ver='new')
model_output = NAICS_mapping(model_output)

model_output['Ratings_with_JBA'] = model_output['Ratings'] + model_output[ 'Override_Action'] + model_output[ 'RLA_Notches']




#%%
cdm = pd.read_excel(r'..\newdata\CDM_RA_BRANCH_201806_PULL_v3.xlsx')
cdm_used = cdm[[ 'CUSTOMERID', 'Statement_Date', 'ModelSource', 'Outstanding','Commitment']]
cdm_used.sort_values(by=['CUSTOMERID','Statement_Date'], ascending=False, inplace=True)
cdm_used.drop_duplicates(subset=['CUSTOMERID'], keep='first', inplace=True)
cdm_used.rename(columns={'Statement_Date':'Outstanding_statementdate'}, inplace=True)

new_df = pd.merge(model_output,cdm_used, on=['CUSTOMERID'], how='left')
new_df['Net_Sales_Size'] = new_df['size@Net_Sales']



#%% rename
py_dict={
	'qual1': 'Strength_SOR','qual2': 'Level_Waivers_Mod','qual4': 'Vulnerability',
	 'Prelim_PD_Risk_Rating_Uncap':'Current_Preliminary_PDRR',
	 'Final_PD_Risk_Rating':'Current_Final_PDRR',
	 'Ratings':'New_Primary_PDRR',
	 'Ratings_with_JBA':'New_Final_Rating',
	 'ExternalRating_PDRR':'External_Rating',
	 'ModelSource':'where_to_book',
	 'timestamp':'archive_date'
}

new_df.rename(columns=py_dict, inplace=True)

CPPD_cols=[
 'CUSTOMERID',
 'Customer Long Name',
 'archive_date',
 'Current_Preliminary_PDRR',
 'Current_Final_PDRR',
 'New_Primary_PDRR',
 'New_Final_Rating',
 'External_Rating',
 'where_to_book',
 'Net_Sales_Size',
 'Asset_Size',
 'Industry_by_NAICS',
 'NAICS_Cd',
 'Outstanding_statementdate',
 'Outstanding',
 'Commitment']

new_df2 = new_df[CPPD_cols]




#%%
base = pd.read_pickle(r'..\newdata\data_201006_201712_addBranch_3_jn_withCIF.pkl.xz')
base2 = base[['CUSTOMERID', 'archive_date','CIF_Num']]

new_df = pd.merge(new_df, base2, on=['CUSTOMERID', 'archive_date'], how='left')
new_df2 = pd.merge(new_df2, base2, on=['CUSTOMERID', 'archive_date'], how='left')




#%%

writer = pd.ExcelWriter('Holdout_sampel_CPPD_requested_v3.xlsx')
new_df.to_excel(writer, 'all_columns')
new_df2.to_excel(writer, 'CPPD_columns')
writer.save()


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import NAICS_mapping, getPDRR
import pickle

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
filehandler = open(r'spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)





#%% processing 2017 data
dat_2017 = pd.read_excel(r'..\newdata\CPPD_sample\Large Corporate Branch 2017 Archive Sort.xlsx')
dat_2017['timestamp'] = pd.to_datetime(dat_2017['archive_date'])
dat_2017['ModelSource'] = 'Branch'


cols_dat_2017=[
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'size@EBITDA', 'size@Capitalization', 'ds@Interest Expense','size@Net_Sales', 'size@Total Debt', 
 'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital',
 'Override_Action',
 'RLA_Notches',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Underwriter_Guideline',
 'NAICS_Cd',
 'ModelSource',
 'NET_COMMITMENT_AMOUNT',
 'Cif Number'
 ]

df_2017 = dat_2017[cols_dat_2017].copy()




#%% processing 2018 data
dat_2018 = pd.read_excel(r'..\newdata\CPPD_sample\2018 Large Corporate Financial and Exposure Information Archive Sort Nodup.xlsx')
dat_2018['timestamp'] = pd.to_datetime(dat_2018['archive_date'])

dat_2018['prof@EBITDA_to_NS'] = dat_2018['EBITDA'] / dat_2018['Net_Sales']
dat_2018['cf@TD_to_EBITDA'] = 	dat_2018['Total Debt'] / dat_2018['EBITDA'] 
dat_2018['size@Total Assets'] = dat_2018['Total_Assets']
dat_2018['bs@TD_to_Capt'] = 	dat_2018['Total Debt'] / dat_2018['CAPITALIZATION'] 
dat_2018['ds@EBITDA_to_IE'] = 	dat_2018['EBITDA'] / dat_2018['Interest Expense']

cols_dat_2018=[
'CUSTOMERID', 'Customer_Name', 'timestamp',
'EBITDA', 'CAPITALIZATION', 'Interest Expense', 'Net Sales', 'Total Debt',
'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
'Strength_SOR_Prevent_Default', 'Level_Waiver_Covenant_Mod', 'Management_Quality', 'Vulnerability_To_Changes','Access_Outside_Capital',
'Override_Action',  'RLA_Notches','ExternalRating_PDRR',
'Prelim_PD_Risk_Rating_Uncap', 'Final_PD_Risk_Rating',
'Underwriter_Guideline','NAICS_Cd','ModelSource',
'Commitment', 'CIF_Num'
] 

df_2018 = dat_2018[cols_dat_2018].copy()
py_dict = dict(zip(cols_dat_2018,cols_dat_2017))
df_2018.rename(columns=py_dict, inplace=True)

#%% get CPPD data
df = pd.concat([df_2017,df_2018], axis=0)

dat_Branch = df.query('ModelSource=="Branch"')
len(dat_Branch)  # 428

len(dat_Branch.query('timestamp>=20180101')) # 19
len(dat_Branch.query('20170101<=timestamp<20180101')) # 380




dat_Bank = df.query('ModelSource=="Bank"')
len(dat_Bank)   # 171





#%% apply model

newdf = NAICS_mapping(df)

newdf.dropna(subset=model.quali_factor, how='any', inplace=True)
newdf.reset_index(drop=True, inplace=True)
newdf['Asset_Size'] = newdf['size@Total Assets'].copy()
newdf['Net_Sales_Size'] = newdf['size@Net_Sales'].copy()
newdf['size@Total Assets'] = np.log(1+newdf['size@Total Assets'])

finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        newdf[factor] = newdf[factor].clip(np.nanmin(newdf[factor][newdf[factor] != -np.inf]), np.nanmax(newdf[factor][newdf[factor] != np.inf]))


model_output = getPDRR(newdf, model, ms_ver='new')
model_output['Ratings_with_JBA'] = model_output['Ratings'] + model_output[ 'Override_Action'] + model_output[ 'RLA_Notches']


#%% 
py_dict={
	'qual1': 'Strength_SOR','qual2': 'Level_Waivers_Mod','qual4': 'Vulnerability',
	 'Prelim_PD_Risk_Rating_Uncap':'Current_Preliminary_PDRR',
	 'Final_PD_Risk_Rating':'Current_Final_PDRR',
	 'Ratings':'New_Primary_PDRR',
	 'Ratings_with_JBA':'New_Final_Rating',
	 'ExternalRating_PDRR':'External_Rating',
	 'ModelSource':'where_to_book',
	 'timestamp':'archive_date'
}

model_output.rename(columns=py_dict, inplace=True)



#%%
writer = pd.ExcelWriter('Holdout_sampel_CPPD_requested.xlsx')
model_output.to_excel(writer, '201806_snapshot')
writer.save()


#%%
branch = model_output.query('where_to_book=="Branch"')
len(branch) # 432
branch['NET_COMMITMENT_AMOUNT'].sum()
# 61539949815.340004

bank = model_output.query('where_to_book=="Bank"')
len(bank) #151
bank['NET_COMMITMENT_AMOUNT'].sum()
#8598723645.28import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import NAICS_mapping, getPDRR
import pickle

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
filehandler = open(r'spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)





#%% processing 2017 data
dat_2017 = pd.read_excel(r'..\newdata\CPPD_sample\Large Corporate Branch 2017 with exposures.xlsx')
dat_2017['timestamp'] = pd.to_datetime(dat_2017['archive_date_exposure'])
dat_2017['ModelSource'] = 'Branch'


cols_dat_2017=[
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'size@EBITDA', 'size@Capitalization', 'ds@Interest Expense','size@Net_Sales', 'size@Total Debt', 
 'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital',
 'Override_Action',
 'RLA_Notches',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Underwriter_Guideline',
 'NAICS_Cd',
 'ModelSource',
 'NET_COMMITMENT_AMOUNT',
 'Cif Number'
 ]

df_2017 = dat_2017[cols_dat_2017].copy()




#%% processing 2018 data
dat_2018 = pd.read_excel(r'..\newdata\CPPD_sample\2018 Large Corporate Financial and Exposure Information.xlsx')
dat_2018['timestamp'] = pd.to_datetime(dat_2018['archive_date'])

dat_2018['prof@EBITDA_to_NS'] = dat_2018['EBITDA'] / dat_2018['Net_Sales']
dat_2018['cf@TD_to_EBITDA'] = 	dat_2018['Total Debt'] / dat_2018['EBITDA'] 
dat_2018['size@Total Assets'] = dat_2018['Total_Assets']
dat_2018['bs@TD_to_Capt'] = 	dat_2018['Total Debt'] / dat_2018['CAPITALIZATION'] 
dat_2018['ds@EBITDA_to_IE'] = 	dat_2018['EBITDA'] / dat_2018['Interest Expense']

cols_dat_2018=[
'CUSTOMERID', 'Customer_Name', 'timestamp',
'EBITDA', 'CAPITALIZATION', 'Interest Expense', 'Net Sales', 'Total Debt',
'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
'Strength_SOR_Prevent_Default', 'Level_Waiver_Covenant_Mod', 'Management_Quality', 'Vulnerability_To_Changes','Access_Outside_Capital',
'Override_Action',  'RLA_Notches','ExternalRating_PDRR',
'Prelim_PD_Risk_Rating_Uncap', 'Final_PD_Risk_Rating',
'Underwriter_Guideline','NAICS_Cd','ModelSource',
'Commitment', 'CIF_Num'
] 

df_2018 = dat_2018[cols_dat_2018].copy()
py_dict = dict(zip(cols_dat_2018,cols_dat_2017))
df_2018.rename(columns=py_dict, inplace=True)

#%% get CPPD data
df = pd.concat([df_2017,df_2018], axis=0)

len(df.query('ModelSource=="Branch"')) # 438
len(df.query('ModelSource=="Bank"')) # 161


#%% apply model

newdf = NAICS_mapping(df)

newdf.dropna(subset=model.quali_factor, how='any', inplace=True)
newdf.reset_index(drop=True, inplace=True)
newdf['Asset_Size'] = newdf['size@Total Assets'].copy()
newdf['Net_Sales_Size'] = newdf['size@Net_Sales'].copy()
newdf['size@Total Assets'] = np.log(1+newdf['size@Total Assets'])

finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        newdf[factor] = newdf[factor].clip(np.nanmin(newdf[factor][newdf[factor] != -np.inf]), np.nanmax(newdf[factor][newdf[factor] != np.inf]))


model_output = getPDRR(newdf, model, ms_ver='new')
model_output['Ratings_with_JBA'] = model_output['Ratings'] + model_output[ 'Override_Action'] + model_output[ 'RLA_Notches']


#%% 
py_dict={
	'qual1': 'Strength_SOR','qual2': 'Level_Waivers_Mod','qual4': 'Vulnerability',
	 'Prelim_PD_Risk_Rating_Uncap':'Current_Preliminary_PDRR',
	 'Final_PD_Risk_Rating':'Current_Final_PDRR',
	 'Ratings':'New_Primary_PDRR',
	 'Ratings_with_JBA':'New_Final_Rating',
	 'ExternalRating_PDRR':'External_Rating',
	 'ModelSource':'where_to_book',
	 'timestamp':'archive_date'
}

model_output.rename(columns=py_dict, inplace=True)



#%%
writer = pd.ExcelWriter('Holdout_sampel_CPPD_requested.xlsx')
model_output.to_excel(writer, '201806_snapshot')
writer.save()


#%%
branch = model_output.query('where_to_book=="Branch"')
len(branch) # 432
branch['NET_COMMITMENT_AMOUNT'].sum()
# 61539949815.340004

bank = model_output.query('where_to_book=="Bank"')
len(bank) #151
bank['NET_COMMITMENT_AMOUNT'].sum()
#8598723645.28# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 15:16:15 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Attachdefaults import Attachdefaults

defaults = pd.read_excel(r'C:\Users\ub71894\Documents\Data\MasterDefault\Master_Def_201712_addBranch.xlsx')
defaults['L_OBLIGOR'] = pd.to_numeric(defaults['L_OBLIGOR'], errors='coerce')



#%%
# Historic Gap data
data1_gap = pd.read_excel(r'raw3\GAP_Report_20180702.xlsx', sheetname='PROFILE')
data2_gap = pd.read_excel(r'raw3\GAP_Report_20180702.xlsx', sheetname='FACTORS')

data1_gap.drop_duplicates(subset=['CUSTOMERID', 'STATEMENTDATE'], inplace=True)
data2_gap.drop_duplicates(subset=['CUSTOMERID', 'STATEMENTDATE'], inplace=True)
dat1_gap = data1_gap[['CUSTOMERID', 'STATEMENTDATE','Obligor Number','Tax ID']]

hist_gap = pd.merge(dat1_gap, data2_gap, on=['CUSTOMERID', 'STATEMENTDATE'], how='right')
hist_gap['Obligor Number'] = pd.to_numeric(hist_gap['Obligor Number'], errors='coerce')
#history period is before 2010
hist_gap = hist_gap.query('STATEMENTDATE<=20091231')


data1_prod = pd.read_excel(r'raw3\PROD_Report_20180702.xlsx', sheetname='PROFILE')
data2_prod = pd.read_excel(r'raw3\PROD_Report_20180702.xlsx', sheetname='FACTORS')

data1_prod.drop_duplicates(subset=['CUSTOMERID', 'STATEMENTDATE'], inplace=True)
data2_prod.drop_duplicates(subset=['CUSTOMERID', 'STATEMENTDATE'], inplace=True)
dat1_prod = data1_prod[['CUSTOMERID', 'STATEMENTDATE','Obligor Number','Tax ID']]

hist_prod = pd.merge(dat1_prod, data2_prod, on=['CUSTOMERID', 'STATEMENTDATE'], how='right')
hist_prod['Obligor Number'] = pd.to_numeric(hist_prod['Obligor Number'], errors='coerce')
#history period is before 2010
hist_prod = hist_prod.query('STATEMENTDATE<=20091231')

# combine Gap and historical production data
hist = pd.concat([hist_gap, hist_prod])
# drop duplicates
hist.drop_duplicates(subset=['CUSTOMERID', 'STATEMENTDATE'], inplace=True)



#%% attach defaults
para = {'isthere_def_enddate':True, 'months_default_atleast_last':6, 
'findata_timestamp':'STATEMENTDATE',
'blackout_mo_bf_def_begins':6, 
'blackout_mo_af_def_ends':6, 
'valid_time_window_mo':(6,18)
}
instance = Attachdefaults(hist,'Obligor Number', defaults, 'L_OBLIGOR',**para)
instance.run_and_report()

dat_withdef = instance.full_data

# Use CUSTOMERID as the unique ID for obligors:
from dateutil.relativedelta import relativedelta as rd
days = 7
identifier = 'CUSTOMERID'

IDs = list(set(dat_withdef[identifier].dropna()))
to_remove=[]
for i, ID in enumerate(IDs):
    dat = dat_withdef.query('{identifier}=={ID}'.format(identifier=identifier, ID=ID))
    dat.sort_values(by='STATEMENTDATE',ascending=False, inplace=True)
    hasdefault = dat.def_flag.sum()
    current = pd.to_datetime('2099-12-31')
    if hasdefault==0: # this customer has no default event
        for row in dat.iterrows():            
            if row[1].STATEMENTDATE < current - rd(days=days):
                current = row[1].STATEMENTDATE
                current_index = row[0]
                continue
            else:
                to_remove.append(row[0])
                continue

    else: # this customer has default event and we should keep that observation
        for row in dat.iterrows():            
            if row[1].STATEMENTDATE < current - rd(days=days):
                current = row[1].STATEMENTDATE
                current_index = row[0]
                continue
            else:
                if row[1].def_flag==1: # step*: keep this default and kick the previous one
                    to_remove.append(current_index)
                    current = row[1].STATEMENTDATE
                    current_index = row[0]
                else:
                    to_remove.append(row[0])
                continue
        # recover all defaults that have been dropped in step*       
        for keep in list(dat.query('def_flag==1').index):
            try:
                to_remove.remove(keep)
            except ValueError:
                pass  # do nothing!

dat_hist = dat_withdef.drop(dat_withdef.index[to_remove])


#%% 
dat_hist.to_pickle('dat_hist_7daysclean.pkl.xz')
dat_hist.to_hdf(r'HDF\dat_hist_7daysclean.h5', 'dat', mode='w',complib='bzip2')


# -*- coding: utf-8 -*-
"""
Created on Mon Jul  9 15:28:07 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata")


dat = pd.read_pickle('dat_hist_7daysclean.pkl.xz')
formula = []
#%%
activity = [
'act@NS_to_CL',
'act@NS_to_UBTangNW',
'act@NS_to_TA',
'act@NS_to_NAR',
'act@NS_to_Inv',
'act@NS_to_TNW']

nume = ['Net Sales',]*6
deno = ['Current Liabilities', 'Union Bank Tangible Net Worth', 'Total Assets','Net Accounts Receivable', 'Total Inventory', 'Total Net Worth']

for i, factor in enumerate(activity):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])

#%%
Balance_sheet_leverage=[
'bs@TD_to_TA',
'bs@TD_to_TangNW',
'bs@TD_to_Capt',
'bs@TD_to_AdjCapt',
'bs@TD_to_TNW',
'bs@TD_to_UBTangNW',
'bs@SD_to_Capt',
'bs@SD_to_AdjCapt',
'bs@TLTD_to_TNW',
'bs@TLTD_to_TA',
'bs@TLTD_to_UBTangNW',
'bs@TLTD_to_AdjCapt',
'bs@TLTD_to_TangNW',
'bs@TLTD_to_Capt',
'bs@TL_to_UBTangNW',
'bs@TL_to_TangNW',
'bs@TL_to_TA',
'bs@TL_to_TNW',
'bs@TL_to_AdjCapt',
'bs@TL_to_Capt',
'bs@CL_to_UBTangNW',
'bs@CL_to_TangNW',
'bs@CL_to_TL',
'bs@CL_to_TNW',
'bs@CL_to_AdjCapt',
'bs@CL_to_TA',
'bs@CL_to_Capt',
'bs@AdjTD_to_AdjCapt',
'bs@AdjTD_to_Capt',

'bs@TLTD_to_TLTD_and_TNW',
'bs@TLTD_to_TLTD_and_UBTangNW',
'bs@TD_to_CA_exc_CL',
'bs@TD_to_TA_exc_TL',
'bs@TL_to_TL_exc_CL'
]

nume = ['Total Debt']*6 + ['Senior Debt']*2 + ['LONGTERMDEBT']*6+['Total Liabilities']*6+[ 'Current Liabilities']*7+['Adjusted Total Debt']*2
deno = ['Total Assets', 'Tangible Net Worth','CAPITALIZATION','Adjusted Capitalization', 'Total Net Worth',  'Union Bank Tangible Net Worth',
 'CAPITALIZATION','Adjusted Capitalization',
 'Total Net Worth', 'Total Assets','Union Bank Tangible Net Worth', 'Adjusted Capitalization', 'Tangible Net Worth','CAPITALIZATION',
'Union Bank Tangible Net Worth', 'Tangible Net Worth','Total Assets','Total Net Worth','Adjusted Capitalization', 'CAPITALIZATION',
'Union Bank Tangible Net Worth','Tangible Net Worth', 'Total Liabilities', 'Total Net Worth','Adjusted Capitalization',  'Total Assets','CAPITALIZATION',
 'Adjusted Capitalization', 'CAPITALIZATION'
 ]

for i, factor in enumerate(Balance_sheet_leverage[:-5]):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])

dat['bs@TLTD_to_TLTD_and_TNW'] = dat['LONGTERMDEBT']/(dat['Total LTD']+dat['Total Net Worth'])
dat['bs@TLTD_to_TLTD_and_UBTangNW'] = dat['LONGTERMDEBT']/(dat['Total LTD']+dat[ 'Union Bank Tangible Net Worth'])
dat['bs@TD_to_CA_exc_CL'] = dat['Total Debt']/(dat['Current Assets']-dat['Current Liabilities'])
dat['bs@TD_to_TA_exc_TL'] = dat['Total Debt']/(dat['Total Assets']-dat['Total Liabilities'])
dat['bs@TL_to_TL_exc_CL'] =  dat['Total Liabilities']/(dat['Total Liabilities']-dat['Current Liabilities'])


#%%
cash_flow_leverage=[
'cf@TD_to_UBEBITDA',
'cf@TD_to_EBITDA',
'cf@TD_to_ACF',
'cf@SD_to_UBEBITDA',
'cf@SD_to_EBITDA',
'cf@AdjTD_to_EBITDA',
'cf@AdjTD_to_UBEBITDA',
'cf@AdjTD_to_ACF',
'cf@FOCF_to_TD',
'cf@FFO_to_TD',
'cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div',
'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',
'cf@AdjTD_to_ACF_and_LE',
'cf@AdjTD_to_NP_and_Dep_and_Amo',
'cf@TD_to_NP_and_Dep_and_Amo',
'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',
'cf@TD_to_EBIT_exc_Div_exc_Taxes',
'cf@TD_to_ACF_and_LE',
]

nume = ['Total Debt']*3+ ['Senior Debt']*2+['Adjusted Total Debt']*3+['Free Operating Cash Flow(FOCF)','Funds from Operations (FFO)']
deno = [ 'Union Bank EBITDA', 'EBITDA', 'ACF',
 'Union Bank EBITDA', 'EBITDA',
'EBITDA',  'Union Bank EBITDA', 'ACF',
 'Total Debt', 'Total Debt',
]

for i, factor in enumerate(cash_flow_leverage[:-8]):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])


dat['cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div'] = dat['Adjusted Total Debt']/(dat['Net Profit']+dat['Depreciation']+dat['Amortization']-dat['Dividends'])
dat['cf@AdjTD_to_EBIT_exc_Div_exc_Taxes'] = dat['Adjusted Total Debt'] / (dat['EBIT']-dat['Dividends']-dat['Taxes'])
dat['cf@AdjTD_to_ACF_and_LE'] = dat['Adjusted Total Debt'] / (dat['ACF'] + dat['Lease Expense'])
dat['cf@AdjTD_to_NP_and_Dep_and_Amo'] = dat['Adjusted Total Debt'] / (dat['Net Profit']+dat['Depreciation']+dat['Amortization'])
dat['cf@TD_to_NP_and_Dep_and_Amo'] = dat['Total Debt']/(dat['Net Profit']+dat['Depreciation']+dat['Amortization'])
dat['cf@TD_to_NP_and_Dep_and_Amo_exc_Div'] =  dat['Total Debt']/(dat['Net Profit']+dat['Depreciation']+dat['Amortization']-dat['Dividends'])
dat['cf@TD_to_EBIT_exc_Div_exc_Taxes'] = dat['Total Debt']/(dat['EBIT']-dat['Dividends']-dat['Taxes'])
dat['cf@TD_to_ACF_and_LE'] = dat['Total Debt']/(dat['ACF'] + dat['Lease Expense'])



#%%
debt_service_coverage=[
'ds@NP_to_TL',
'ds@NP_to_CL',
'ds@NP_to_IE',
'ds@UBEBIT_to_IE',
'ds@UBEBIT_to_DS',
'ds@EBIT_to_IE',
'ds@EBIT_to_DS',
'ds@UBEBITDA_to_IE',
'ds@EBITDA_to_IE',
'ds@FFO_to_IE',
'ds@NS_to_IE',
'ds@TL_to_IE',
'ds@ACF_to_DS',
'ds@ACF_and_LE_to_DS_and_LE',
'ds@EBIT_exc_Div_exc_Taxes_to_IE',
'ds@UBEBIT_and_LE_to_DS_and_LE',
'ds@UBEBIT_exc_Div_exc_Taxes_to_IE',
'ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
'ds@UBEBIT_exc_Div_exc_Taxes_to_DS',
'ds@EBIT_exc_Div_exc_Taxes_to_DS',
'ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
'ds@EBIT_and_LE_to_DS_and_LE',
'ds@NP_and_IE_to_IE',
'ds@NP_and_IE_to_TL',
'ds@DSCR']



nume = ['Net Profit']*3+ [ 'Union Bank EBIT']*2+['EBIT']*2+['Union Bank EBITDA', 'EBITDA','Funds from Operations (FFO)', 'Net Sales', 'Total Liabilities','ACF']
deno = [ 'Total Liabilities', 'Current Liabilities','Interest Expense', 
'Interest Expense', 'Debt Service',
'Interest Expense', 'Debt Service',
'Interest Expense','Interest Expense','Interest Expense','Interest Expense','Interest Expense',
'Debt Service']

for i, factor in enumerate(debt_service_coverage[:13]):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])


dat['ds@ACF_and_LE_to_DS_and_LE'] = (dat['ACF'] + dat['Lease Expense']) / (dat['Debt Service'] + dat['Lease Expense']) 
dat['ds@EBIT_exc_Div_exc_Taxes_to_IE'] = (dat['EBIT']-dat['Dividends']-dat['Taxes'] )/ dat['Interest Expense']
dat['ds@UBEBIT_and_LE_to_DS_and_LE'] =  (dat['Union Bank EBIT'] + dat['Lease Expense']) / (dat['Debt Service'] + dat['Lease Expense']) 
dat['ds@UBEBIT_exc_Div_exc_Taxes_to_IE'] = (dat['Union Bank EBIT']-dat['Dividends']-dat['Taxes'] )/ dat['Interest Expense']
dat['ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE'] = (dat['Union Bank EBIT']-dat['Dividends']-dat['Taxes']+dat['Lease Expense'])/ (dat['Debt Service'] + dat['Lease Expense']) 
dat['ds@UBEBIT_exc_Div_exc_Taxes_to_DS']= (dat['Union Bank EBIT']-dat['Dividends']-dat['Taxes'])/ dat['Debt Service']  
dat['ds@EBIT_exc_Div_exc_Taxes_to_DS'] = (dat['EBIT']-dat['Dividends']-dat['Taxes'])/ dat['Debt Service']  
dat['ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE'] = (dat['EBIT']-dat['Dividends']-dat['Taxes']+dat['Lease Expense'])/ (dat['Debt Service'] + dat['Lease Expense']) 
dat['ds@EBIT_and_LE_to_DS_and_LE'] = (dat['EBIT'] + dat['Lease Expense']) / (dat['Debt Service'] + dat['Lease Expense']) 
dat['ds@NP_and_IE_to_IE'] = (dat['Net Profit'] + dat['Interest Expense']) / dat['Interest Expense']
dat['ds@NP_and_IE_to_TL'] = (dat['Net Profit'] + dat['Interest Expense']) / dat['Total Liabilities']
dat['ds@DSCR'] = (dat['Net Profit'] + dat['Depreciation']+ dat['Interest Expense']) / dat['Debt Service']



#%%
liquidity=[
'liq@ECE_to_TD',
'liq@ECE_to_TL',
'liq@ECE_to_AdjTD',
'liq@ECE_to_TA',
'liq@ECE_to_CL',
'liq@ECE_to_CA',
'liq@CA_to_TL',
'liq@CA_to_TA',
'liq@RE_to_CL',
'liq@CA_exc_TI_to_TD',
'liq@CA_exc_TI_to_/TL',
'liq@CA_exc_TI_to_/AdjTD',
'liq@CA_exc_TI_to_/TA',
'liq@CA_exc_CL_to_TD',
'liq@CA_exc_CL_to_TL',
'liq@CA_exc_CL_to_AdjTD',
'liq@CA_exc_CL_to_TA',
'liq@CA_exc_CL_to_CA',
'liq@CA_exc_CL_to_CL',
]

nume = ['Ending Cash & Equivalents']*6+['Current Assets']*2+['Retained Earnings']
deno = [ 'Total Debt','Total Liabilities', 'Adjusted Total Debt','Total Assets', 'Current Liabilities', 'Current Assets',
'Total Liabilities', 'Total Assets',
'Current Liabilities'
]
for i, factor in enumerate(liquidity[:9]):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])


dat['liq@CA_exc_TI_to_TD'] = (dat['Current Assets'] - dat['Total Inventory']) / dat['Total Debt']
dat['liq@CA_exc_TI_to_/TL'] = (dat['Current Assets'] - dat['Total Inventory']) / dat['Total Liabilities']
dat['liq@CA_exc_TI_to_/AdjTD'] = (dat['Current Assets'] - dat['Total Inventory']) / dat[ 'Adjusted Total Debt']
dat['liq@CA_exc_TI_to_/TA'] = (dat['Current Assets'] - dat['Total Inventory']) / dat['Total Assets']
dat['liq@CA_exc_CL_to_TD'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Total Debt']
dat['liq@CA_exc_CL_to_TL'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Total Liabilities']
dat['liq@CA_exc_CL_to_AdjTD'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Adjusted Total Debt']
dat['liq@CA_exc_CL_to_TA'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Total Assets']
dat['liq@CA_exc_CL_to_CA'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Current Assets']
dat['liq@CA_exc_CL_to_CL'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Current Liabilities']



#%%
profitability = [
 'prof@EBIT_to_AdjCapt',
 'prof@EBIT_to_Capt',
 'prof@EBIT_to_NS',
 'prof@EBIT_to_TangA',
 'prof@EBIT_to_TA',
 'prof@EBITDA_to_AdjCapt',
 'prof@EBITDA_to_Capt',
 'prof@EBITDA_to_NS',
 'prof@EBITDA_to_TangA',
 'prof@EBITDA_to_TA',
 'prof@NOP_to_NP',
 'prof@NOP_to_NS',
 'prof@NOP_to_TangNW',
 'prof@NOP_to_TA',
 'prof@NOP_to_TNW',
 'prof@NOP_to_UBTangNW',
 'prof@RE_to_TA',
 'prof@RE_to_TNW',
 'prof@RE_to_UBTangNW',
 'prof@UBEBIT_to_AdjCapt',
 'prof@UBEBIT_to_Capt',
 'prof@UBEBIT_to_NS',
 'prof@UBEBIT_to_TangA',
 'prof@UBEBIT_to_TA',
 'prof@UBEBITDA_to_AdjCapt',
 'prof@UBEBITDA_to_Capt',
 'prof@UBEBITDA_to_NS',
 'prof@UBEBITDA_to_TangA',
 'prof@UBEBITDA_to_TA',
 'prof@PbT_to_TA',
 'prof@CD_to_NP',
 'prof@NP_exc_EI',
 'prof@EBIT_exc_II_to_Capt',
 'prof@NP_exc_EI_to_TA']


nume = ['EBIT']*5+['EBITDA']*5+['Net Operating Profit']*6+['Retained Earnings']*3+['Union Bank EBIT']*5+['Union Bank EBITDA']*5+['Profit before Taxes','ESOPDividends']
deno = ['Adjusted Capitalization', 'CAPITALIZATION', 'Net Sales', 'Tangible Assets', 'Total Assets',
'Adjusted Capitalization', 'CAPITALIZATION', 'Net Sales', 'Tangible Assets', 'Total Assets',
'Net Profit','Net Sales','Tangible Net Worth','Total Assets','Total Net Worth','Union Bank Tangible Net Worth',
'Total Assets','Total Net Worth','Union Bank Tangible Net Worth',
'Adjusted Capitalization','CAPITALIZATION','Net Sales','Tangible Assets','Total Assets',
'Adjusted Capitalization','CAPITALIZATION','Net Sales','Tangible Assets','Total Assets',
'Total Assets','Net Profit']


for i, factor in enumerate(profitability[:31]):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])

dat['prof@NP_exc_EI'] = dat['Net Profit'] - dat['Extraordinary Items']
dat['prof@EBIT_exc_II_to_Capt'] = (dat['EBIT']-dat['INTERESTINCOME']) / dat['CAPITALIZATION']
dat['prof@NP_exc_EI_to_TA'] = (dat['Net Profit']-dat['Extraordinary Items']) / dat['Total Assets']


#%% 
size=[
'size@TangNW_to_TA',
'size@TangNW_to_TA_exc_CA',
'size@UBTangNW_to_TA',
'size@UBTangNW_to_TA_exc_CA',
'size@TNW_to_TA_exc_CA',
'size@TNW_to_TA']

dat['size@TangNW_to_TA'] = dat['Tangible Net Worth'] / dat['Total Assets']
dat['size@TangNW_to_TA_exc_CA'] = dat['Tangible Net Worth'] / (dat['Total Assets']-dat['Current Assets'])
dat['size@UBTangNW_to_TA'] = dat['Union Bank Tangible Net Worth'] / dat['Total Assets']
dat['size@UBTangNW_to_TA_exc_CA'] = dat['Union Bank Tangible Net Worth'] /(dat['Total Assets']-dat['Current Assets'])
dat['size@TNW_to_TA_exc_CA'] = dat['Total Net Worth'] / (dat['Total Assets']-dat['Current Assets'])
dat['size@TNW_to_TA'] = dat['Total Net Worth'] / dat['Total Assets']


#%%
BTMU_factors=[
'BTMU@TD_to_EBITDA',
'BTMU@EBITDA_to_IE',
'BTMU@TNW_to_TA',
'BTMU@TD_to_TNW',
'BTMU@OP_to_Sales',
'BTMU@NP_exc_EI_to_TA',
]

dat['BTMU@TD_to_EBITDA'] = dat['Total Debt'] / dat['EBITDA']
dat['BTMU@EBITDA_to_IE'] = dat['EBITDA'] / dat['Interest Expense']
dat['BTMU@TNW_to_TA'] = dat['Total Net Worth'] / dat['Total Assets']
dat['BTMU@TD_to_TNW'] = dat['Total Debt'] / dat['Total Net Worth']
dat['BTMU@OP_to_Sales'] = dat['Net Operating Profit'] / dat['Net Sales']
dat['BTMU@NP_exc_EI_to_TA']  = (dat['Net Profit'] - dat['Extraordinary Items'])/ dat['Total Assets']


#%%
SP_factors=[
'SP@TD_to_TD_and_TNW',
'SP@EBIT_to_TD_and_TNW',
'SP@EBIT_to_IE',
'SP@EBITDA_to_IE',
]

dat['SP@TD_to_TD_and_TNW'] = dat['Total Debt'] / (dat['Total Debt'] + dat['Total Net Worth'])
dat['SP@EBIT_to_TD_and_TNW'] =  dat['EBIT'] / (dat['Total Debt'] + dat['Total Net Worth'])
dat['SP@EBIT_to_IE'] = dat['EBIT'] / dat['Interest Expense']
dat['SP@EBITDA_to_IE'] = dat['EBITDA'] / dat['Interest Expense']


#%%
to_rename=dict(zip([
'ACF',
 'Adjusted Capitalization',
 'Adjusted Total Debt',
 'Amortization',
 'Average Profit Margin, 2 yrs',
 'CAPITALIZATION',
 'Current Assets',
 'Current Liabilities',
 'Current Ratio',
 'INTERESTEXPENSE',
 'CPLTD',
 'Debt Service',
 'Depreciation',
 'DIVIDENDSSTOCK',
 'ESOPDividends',
 'DIVIDENDSPREF',
 'Dividends',
 'EBIT',
 'EBITDA',
 'Ending Cash & Equivalents',
 'AFTERTAXINCOME',
 'AFTERTAXEXPENSE',
 'Extraordinary Items',
 'Free Operating Cash Flow_Modified',
 'Funds from Operations_Modified',
 'Interest Expense',
 'Total Inventory',
 'Lease Expense',
 'Net Accounts Receivable',
 'Net Operating Profit',
 'Net Profit',
 'Net Sales',
 'Profit before Taxes',
 'Quick Ratio',
 'Retained Earnings',
 'Return on Assets',
 'Return on Equity',
 'Senior Debt',
 'NETTANGIBLES',
 'Tangible Assets',
 'Tangible Net Worth',
 'INCOMETAXEXP',
 'INCOMETAXCREDIT',
 'Taxes',
 'Total Assets',
 'Total Debt',
 'LONGTERMDEBT',
 'CAPLEASEOBLIG',
 'Total LTD',
 'Total Liabilities',
 'Total Net Worth',
 'Union Bank Current Ratio',
 'Union Bank EBIT',
 'Union Bank EBITDA',
 'Union Bank Quick Ratio',
 'Union Bank Tangible Net Worth',
 'Operating Profit Margin %',
 'Net Profit Margin %',
 'Gross Profit Margin %',
 'Gross Profit Margin %.1',
 'Free Operating Cash Flow(FOCF)',
 'Funds from Operations (FFO)',
 'INTERESTEXPENSE_2',
 'CAPINTEREST',
 'INTERESTINCOME',
 'Total Interest Inc(Exp)',
 'INCOMETAXEXP_1',
 'INCOMETAXCREDIT_1',
 'TOTAL INCOME TAX EXPENSE',
 'quant2',
 'quant4',
 'quant5'],[
 	'cf@ACF',
 'size@Adjusted Capitalization',
 'size@Adjusted Total Debt',
 'size@Amortization',
 'prof@Average Profit Margin, 2 yrs',
 'size@Capitalization',
 'size@Current Assets',
 'size@Current Liabilities',
 'liq@Current Ratio',
 'ds@INTERESTEXPENSE',
 'bs@CPLTD',
 'ds@Debt Service',
 'cf@Depreciation',
 'prof@DIVIDENDSSTOCK',
 'prof@DividendCommon',
 'prof@DIVIDENDSPREF',
 'prof@Dividends',
 'size@EBIT',
 'size@EBITDA',
 'cf@Ending Cash & Equivalents',
 'prof@AFTERTAXINCOME',
 'ds@AFTERTAXEXPENSE',
 'size@Extraordinary Items',
 'size@Free Operating Cash Flow_Modified',
 'size@Funds from Operations_Modified',
 'ds@Interest Expense',
 'size@Total Inventory',
 'cf@Lease Expense',
 'size@Net Accounts Receivable',
 'size@Net Operating Profit',
 'size@Net Profit',
 'size@Net_Sales',
 'size@Profit before Taxes',
 'liq@Quick Ratio',
 'size@Retained Earnings',
 'prof@Return on Assets',
 'prof@Return on Equity',
 'bs@Senior Debt',
 'size@NETTANGIBLES',
 'size@Tangible Assets',
 'size@Tangible Net Worth',
 'others@INCOMETAXEXP',
 'others@INCOMETAXCREDIT',
 'others@Taxes',
 'size@Total Assets',
 'size@Total Debt',
 'bs@LONGTERMDEBT',
 'others@CAPLEASEOBLIG',
 'bs@Total LTD',
 'size@Total Liabilities',
 'size@Total Net Worth',
 'liq@Union Bank Current Ratio',
 'size@Union Bank EBIT',
 'size@Union Bank EBITDA',
 'liq@Union Bank Quick Ratio',
 'size@Union Bank Tangible Net Worth',
 'prof@Operating Profit Margin %',
 'prof@Net Profit Margin %',
 'prof@Gross Profit Margin %',
 'prof@Gross Profit Margin %.1',
 'size@Free Operating Cash Flow (FOCF)',
 'size@Funds from Operations (FFO)',
 'ds@INTERESTEXPENSE_2',
 'others@CAPINTEREST',
 'prof@Interest Income',
 'others@Total Interest Inc(Exp)',
 'others@INCOMETAXEXP_1',
 'others@INCOMETAXCREDIT_1',
 'others@TOTAL INCOME TAX EXPENSE',
 'cf@quant2',
 'bs@quant4',
 'liq@quant5']))

dat.rename(columns=to_rename, inplace=True)
dat['Net_Sales'] = dat['size@Net_Sales']

# add current quant2 into the data:
dat['cf@TD_COP'] = dat['size@Total Debt'] / dat['size@Net Operating Profit']
# add one tokyo factor into the data:
dat['prof@TangA_to_NS'] = dat['size@Tangible Assets'] / dat['size@Net_Sales']
# add one tokyo factor into the data:
dat['cf@FOCF_to_TL'] = dat['size@Free Operating Cash Flow (FOCF)'] / dat['size@Total Liabilities']


# remove two audit method 'Proforma' and 'Projection'
valid = dat.loc[dat['AUDITMETHOD'] != 'Proforma']
valid = valid.loc[valid['AUDITMETHOD'] != 'Projection']


valid.to_pickle('dat_hist_7daysclean_addratios_valid.pkl.xz')
valid.to_hdf(r'HDF\dat_hist_7daysclean_addratios_valid.h5', 'dat', mode='w',complib='bzip2')







# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 15:09:46 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata")
spdat = pd.read_excel('S&P Rating Mapping Data 070818.xlsx')
hist = pd.read_pickle('dat_hist_7daysclean_addratios_valid.pkl.xz')
hist['STATEMENTDATE'] = pd.to_datetime(hist['STATEMENTDATE'])


pd_ext_int_ratings_mapping={
'BB-':10,
'BB':9,
'BBB+':5,
'BBB':6,
'BBB-':7,
'BB+':8,
'B':12,
'A+':3,
'B+':11,
'B-':13,
'AA+':2,
'AA':2,
'AA-':3,
'AAA':2,
'A-':4,
'CCC':15,
'A':3,
'CC':15,
'CCC-':15,
'CCC+':15,
}

pd_PDRR_PD_mapping={
2:0.0003,
3:0.0006,
4:0.001,
5:0.0015,
6:0.0025,
7:0.0037,
8:0.0055,
9:0.007,
10:0.011,
11:0.0175,
12:0.0225,
13:0.041,
14:0.08,
15:0.25,
20:1
}

#%%
dat = spdat.dropna(subset=['EIN'])
dat['Tax ID'] = [x.replace('-','') for x in dat['EIN'].tolist()]
cols=['CONM',
'EIN',
'ratingSymbol',
'ratingDate',
'ratingTypeCode',
'priorRatingSymbol',
'ratingActionWord',
'symbolID',
'symbolTypeID',
'symbolValue',
'objectID',
'relatedCompanyID',
'identifierID',
'companyID',
'GVKEY',
'identifierTypeID',
'NAICS',
'Tax ID']
dat = dat[cols]
dat.dropna(subset=['ratingDate','Tax ID'], how='any', inplace=True)

dat = dat.loc[dat['ratingTypeCode'].isin(['FCLONG','STDLONG'])]
dat = dat.loc[~dat['ratingSymbol'].isin(['D', 'NR', 'SD', 'R'])]

sp_rating_symbols = dat['ratingSymbol'].tolist()
for i, rating in enumerate(sp_rating_symbols):
    if '/' in rating:
        sp_rating_symbols[i] = rating[:rating.index('/')]        
dat['ratingSymbol'] = sp_rating_symbols

dat.drop_duplicates(subset=['ratingDate','Tax ID'], inplace=True)
dat['ratingDate'] = pd.to_datetime(dat['ratingDate'])



# get valid obs
new_hist = pd.merge(hist, dat, on=['Tax ID'], how='inner')
new_hist = new_hist.query('ratingDate < STATEMENTDATE')
new_hist.sort_values(by=['CUSTOMERID','STATEMENTDATE','ratingDate'], inplace=True)
new_hist.drop_duplicates(subset=['CUSTOMERID','STATEMENTDATE'], keep='last', inplace=True)
new_hist['lag'] = new_hist.STATEMENTDATE - new_hist.ratingDate 
new_hist.lag.describe()
'''
count                         2196
mean      993 days 08:03:38.036429
std       933 days 09:25:07.011369
min                0 days 12:52:38
25%       298 days 20:34:39.750000
50%              703 days 13:26:29
75%      1407 days 15:04:01.750000
max             5661 days 00:00:00
Name: lag, dtype: object
'''
new_hist[new_hist.lag > pd.Timedelta('3650 days')]
# 49 rows

new_hist['ExtRating'] = new_hist['ratingSymbol']
new_hist['implied_internal_PDRR'] = new_hist['ExtRating']
new_hist['implied_internal_PDRR'] = new_hist['implied_internal_PDRR'].replace(pd_ext_int_ratings_mapping)
new_hist['implied_internal_PD'] = new_hist['implied_internal_PDRR']
new_hist['implied_internal_PD'] = new_hist['implied_internal_PD'].replace(pd_PDRR_PD_mapping)
new_hist = new_hist[['CONM','NAICS','CUSTOMERID','STATEMENTDATE', 'lag','ratingSymbol', 'ExtRating', 'implied_internal_PDRR', 'implied_internal_PD']]



final_data = pd.merge(hist, new_hist, on=['CUSTOMERID','STATEMENTDATE'], how='left')
final_data.reset_index(drop=True, inplace=True)


#%%
final_data.to_pickle(r'dat_hist_7daysclean_addratios_valid_addExtRatings.pkl.xz')
final_data.to_hdf(r'HDF\dat_hist_7daysclean_addratios_valid_addExtRatings.h5', 'dat', mode='w',complib='bzip2')


# -*- coding: utf-8 -*-
"""
Created on Tue Jul 10 09:52:53 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata")
dat = pd.read_pickle('dat_hist_7daysclean_addratios_valid_addExtRatings.pkl.xz')

#%% constant and functions
cutoff = 1000
# 
def isLC(ID, how='mean'):
    global dat_mm, dat_lc
    temp_lc = dat_lc.query('CUSTOMERID=={}'.format(ID))
    temp_mm = dat_mm.query('CUSTOMERID=={}'.format(ID))
    
    if how=='mean':
        return (pd.concat([temp_lc,temp_mm], axis=0)['Net_Sales'].mean()>5e8)      
    elif how=='first':
        return (temp_lc.STATEMENTDATE.min() < temp_mm.STATEMENTDATE.min())     
    elif how=='last':
        return (temp_lc.STATEMENTDATE.max() > temp_mm.STATEMENTDATE.max())
    else:
        raise Exception('"how" must be one of [mean, first, last]')

def addto(adto, ID):
    global dat_mm, dat_lc
    if adto=='LC':
        temp = dat_mm.query('CUSTOMERID=={}'.format(ID))
        dat_lc = pd.concat([dat_lc,temp], axis=0)
    elif adto=='MM':
        temp = dat_lc.query('CUSTOMERID=={}'.format(ID))
        dat_mm = pd.concat([dat_mm,temp], axis=0)
    else:
        raise Exception('LC or MM')

def removefrom(refr, ID):
    global dat_mm, dat_lc
    if refr=='MM':
        dat_mm = dat_mm.query('CUSTOMERID !={}'.format(ID))
    elif refr=='LC':   
        dat_lc = dat_lc.query('CUSTOMERID !={}'.format(ID))
    else:
        raise Exception('LC or MM')



dat_lc = dat.query('Net_Sales>{}'.format(cutoff*1e6))
dat_mm = dat.query('Net_Sales<={}'.format(cutoff*1e6))

lc_customer = set(dat_lc['CUSTOMERID'].tolist())
mm_customer = set(dat_mm['CUSTOMERID'].tolist())
len(lc_customer&mm_customer)

pl_overlap = list(lc_customer&mm_customer)



#%% determinated by the last statement
for ID in pl_overlap:
    if isLC(ID,'last'):
        addto('LC',ID)
        removefrom('MM',ID)       
    else:
        addto('MM',ID)
        removefrom('LC',ID)


# only use obs which has valid external rating for LC
dat_lc = dat_lc.dropna(subset=['ExtRating'])

dat_lc.to_pickle(r'hist_lc_by{cut}_last.pkl.xz'.format(cut=cutoff))
dat_lc.to_hdf(r'HDF\hist_lc_by{cut}_last.h5'.format(cut=cutoff), 'dat', mode='w',complib='bzip2')
dat_lc.to_excel(r'hist_lc_by{cut}_last.xlsx'.format(cut=cutoff))


dat_mm.to_pickle(r'hist_mm_by{cut}_last.pkl.xz'.format(cut=cutoff))
dat_mm.to_hdf(r'HDF\hist_mm_by{cut}_last.h5'.format(cut=cutoff), 'dat', mode='w',complib='bzip2')
dat_mm.to_excel(r'hist_mm_by{cut}_last.xlsx'.format(cut=cutoff))
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 16:19:32 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata\raw2")

# combine the data from CASS
data1 = pd.read_excel('CI_Report_20180419.xlsx', sheetname='CustProfTable')
#data1.rename(columns={'RA Customer ID':'CUSTOMERID', 'STATEMENT ID':'statement_id',  'STATEMENT DATE':'Statement_Date'}, inplace=True)
data2 = pd.read_excel('CI_Report_20180419.xlsx', sheetname='CustFinancialFactor')

data = pd.concat([data1, data2], axis=1)
data.rename(columns={'Archive Date':'archive_date'}, inplace=True)
data.rename(columns={'Obligor Number':'OBLIGOR_NUMBER'}, inplace=True)

# grab some field from current CnI data
prod = pd.read_pickle(r'..\data_201006_201712_addBranch_3_jn_withCIF.pkl.xz')
prod = prod.query('DataPeriod=="Prod" or DataPeriod=="Prod_Branch"')
prod = prod.drop_duplicates(subset=['CUSTOMERID','archive_date'])

cols_need =[
'quant1', 'quant2_COP', 'quant2_ACF', 'quant2', 'quant3', 'quant4', 'quant5', 'qual1', 'qual2', 'qual3',\
 'qual4', 'Prelim_PD_Risk_Rating_Uncap', 'Final_PD_Risk_Rating', 'RLA_Notches','Override_Action','Underwriter_Guideline']

prod = prod[['CUSTOMERID','archive_date']+cols_need]
prod.reset_index(drop=True, inplace=True)

# merge 
new = pd.merge(data, prod, on=['CUSTOMERID','archive_date'], how='inner')


new.to_pickle(r'..\CI_Report_20180419_with_curr_factors&ratings.pkl.xz')

new.to_hdf('..\HDF\CI_Report_20180419_with_curr_factors&ratings.h5', 'dat', mode='w',complib='bzip2')# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 14:40:07 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")


data = pd.read_pickle(r'..\newdata\CI_Report_20180419_with_curr_factors&ratings.pkl.xz')
data['CUSTOMERID'] = pd.to_numeric(data['CUSTOMERID'] )
# check whether the record is 'approved'
gcrrcr = pd.read_pickle(r'..\newdata\Ming_data\gcr_rcr.pkl.xz')
gcrrcr['approved'] = 1

new = pd.merge(data, gcrrcr, on=['CUSTOMERID','Archive ID'], how='left')
new.approved.sum()

new = new.query('approved==1')



new.to_pickle(r'..\newdata\CI_Report_20180419_with_curr_factors&ratings_approved.pkl.xz')
new.to_hdf(r'..\newdata\HDF\CI_Report_20180419_with_curr_factors&ratings_approved.h5', 'dat', mode='w',complib='bzip2')# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 14:43:50 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Attachdefaults import Attachdefaults

defaults = pd.read_excel(r'C:\Users\ub71894\Documents\Data\MasterDefault\Master_Def_201712_addBranch.xlsx')
defaults['L_OBLIGOR'] = pd.to_numeric(defaults['L_OBLIGOR'], errors='coerce')

data = pd.read_pickle(r'..\newdata\CI_Report_20180419_with_curr_factors&ratings.pkl.xz')
data['OBLIGOR_NUMBER'] = pd.to_numeric(data['OBLIGOR_NUMBER'], errors='coerce')

# manually assign obligor number to defaulted Branch customer:
data.loc[data['Customer Long Name']=="Hunt Oil Company",'OBLIGOR_NUMBER']=2
data.loc[data['Customer Long Name']=="Paragon Offshore Limited",'OBLIGOR_NUMBER']=1


#%% attach defaults to prod
para = {'isthere_def_enddate':True, 'months_default_atleast_last':6, 
'findata_timestamp':'archive_date',
'blackout_mo_bf_def_begins':6, 
'blackout_mo_af_def_ends':6, 
'valid_time_window_mo':(6,18)
}
instance = Attachdefaults(data,'OBLIGOR_NUMBER', defaults, 'L_OBLIGOR',**para)
instance.run_and_report()


#%% keeps all 
prod = instance.full_data
#prod.to_pickle(r'..\newdata\prod_allgood.pkl.xz')

#%% drop 
# Use CUSTOMERID as the unique ID for obligors:
from dateutil.relativedelta import relativedelta as rd
days = 7
identifier = 'CUSTOMERID'

IDs = list(set(prod[identifier].dropna()))
to_remove=[]
for i, ID in enumerate(IDs):
    dat = prod.query('{identifier}=={ID}'.format(identifier=identifier, ID=ID))
    dat.sort_values(by='archive_date',ascending=False, inplace=True)
    hasdefault = dat.def_flag.sum()
    current = pd.to_datetime('2099-12-31')
    if hasdefault==0: # this customer has no default event
        for row in dat.iterrows():            
            if row[1].archive_date < current - rd(days=days):
                current = row[1].archive_date
                current_index = row[0]
                continue
            else:
                to_remove.append(row[0])
                continue

    else: # this customer has default event and we should keep that observation
        for row in dat.iterrows():            
            if row[1].archive_date < current - rd(days=days):
                current = row[1].archive_date
                current_index = row[0]
                continue
            else:
                if row[1].def_flag==1: # step*: keep this default and kick the previous one
                    to_remove.append(current_index)
                    current = row[1].archive_date
                    current_index = row[0]
                else:
                    to_remove.append(row[0])
                continue
        # recover all defaults that have been dropped in step*       
        for keep in list(dat.query('def_flag==1').index):
            try:
                to_remove.remove(keep)
            except ValueError:
                pass  # do nothing!


prod_partialgood = prod.drop(prod.index[to_remove])
prod_partialgood.to_pickle(r'..\newdata\prod_allgood_7daysclean.pkl.xz')
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 10:12:08 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
from dateutil.relativedelta import relativedelta as rd

dat = pd.read_excel(r'..\newdata\DRD\NEW_CustFinancialFactor_20180530.xls')
cols = dat.columns.tolist()

dat.drop_duplicates(subset=['CUSTOMERID', 'Statement_Date'], inplace=True)
dat.reset_index(drop=True, inplace=True)


#%%
'''
    Part Three: Apply default logic to the merged data:
        Step_1: Blackout all financial statments which are in the time window 
                ['blackout_mo_bf_def_begins' months before default begins,
                blackout_mo_af_def_ends' months after default ends]    
        Step_2: Pick the financial statments that occur in the 'valid time window'. 
                Usually it's 6-18 months before actual default.
        Step_3: Only keep the latest financial statement if multiple lie in valid 
                time window. In other word, we only select the closest financial 
                statement to the actual default and remove others.
'''
'''
Step_1: Blackout all financial statments which are in the time window 
        ['blackout_mo_bf_def_begins' months before default begins,
        blackout_mo_af_def_ends' months after default ends]    
'''
list_to_remove=[]
for row in dat.iterrows():
    if (row[1]['ISSUER_DEFAULT_DATETIME']-rd(months=6)) \
        <= row[1]['Statement_Date'] \
        <= (row[1]['ISSUER_DEFAULT_DATETIME']+rd(months=12)):
        list_to_remove.append(row[0])
    else:
        continue        

dat.drop(dat.index[list_to_remove], inplace=True)
dat.reset_index(drop=True, inplace=True)


a= dat[['CUSTOMERID','Statement_Date','ISSUER_DEFAULT_DATETIME']]


'''
Step_2: Pick the financial statments that occur in the 'valid time window'. 
        Usually it's 6-18 months before actual default.
'''
  
list_to_remove=[]
for row in dat.iterrows():
    if row[1]['Statement_Date'] >= \
    (row[1]['ISSUER_DEFAULT_DATETIME']-rd(months=6)) or \
       row[1]['Statement_Date'] <= \
    (row[1]['ISSUER_DEFAULT_DATETIME']-rd(months=18)):
        list_to_remove.append(row[0])
    else:
        continue        

dat.drop(dat.index[list_to_remove], inplace=True)
dat.reset_index(drop=True, inplace=True)
a= dat[['CUSTOMERID','Statement_Date','ISSUER_DEFAULT_DATETIME']]




#%%
'''
Step_3: Combine defaults for the same obligor if the second one happened within 1 year of the
    previous one or within previous default's end date.
'''

dat.sort_values(by=['CUSTOMERID','Statement_Date'], inplace=True)
dat.drop_duplicates(subset=['CUSTOMERID','ISSUER_DEFAULT_DATETIME'], keep='last', inplace=True)
dat.reset_index(drop=True, inplace=True)


# rename all cols which are different from production data's
pydict = { 'Obligor_name':'Customer Long Name',
 'ARCHIVEID':'Archive ID',
 'STATEMENTDATE': 'STATEMENT DATE',
 'AUDITMETHOD': 'Audit Method',
'ISSUER_DEFAULT_DATETIME':'L_DATE_OF_DEFAULT',
'ESOPDividends':'DividendCommon', 'InterestIncome': 'Interest Income'}
dat.rename(columns=pydict, inplace=True)

# remove some cols
coltoremove=[ 'MoodysOrgID', 'CIFNum', 'CompID', 'CDL', 'Obligo',
 'TaxID', 'PD_RISK_RATING_DATE',  'STATEMENTMONTHS',]
dat.drop(coltoremove, axis=1, inplace=True)

# initial some cols with prod's median
prod_partialgood = pd.read_pickle(r'..\newdata\prod_allgood_7daysclean.pkl.xz')
dat['quant1'] = prod_partialgood['quant1'].median()
dat['quant2'] = prod_partialgood['quant2'].median()
dat['quant3'] = prod_partialgood['quant3'].median()
dat['quant4'] = prod_partialgood['quant4'].median()
dat['quant5'] = prod_partialgood['quant5'].median()
dat['Final_PD_Risk_Rating'] = prod_partialgood['Final_PD_Risk_Rating'].median()
dat['def_flag']=1


#%%



new = pd.concat([dat, prod_partialgood], axis=0)
new.reset_index(drop=True, inplace=True)

new.to_pickle(r'..\newdata\prod_allgood_7daysclean_addDRD.pkl.xz')
# -*- coding: utf-8 -*-
"""
Created on Tue May  1 12:04:41 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

dat = pd.read_pickle(r'..\newdata\prod_allgood_7daysclean_addDRD.pkl.xz')

formula = []
#%%
activity = [
'act@NS_to_CL',
'act@NS_to_UBTangNW',
'act@NS_to_TA',
'act@NS_to_NAR',
'act@NS_to_Inv',
'act@NS_to_TNW']

nume = ['Net Sales',]*6
deno = ['Current Liabilities', 'Union Bank Tangible Net Worth', 'Total Assets','Net Accounts Receivable', 'Total Inventory', 'Total Net Worth']

for i, factor in enumerate(activity):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])

#%%
Balance_sheet_leverage=[
'bs@TD_to_TA',
'bs@TD_to_TangNW',
'bs@TD_to_Capt',
'bs@TD_to_AdjCapt',
'bs@TD_to_TNW',
'bs@TD_to_UBTangNW',
'bs@SD_to_Capt',
'bs@SD_to_AdjCapt',
'bs@TLTD_to_TNW',
'bs@TLTD_to_TA',
'bs@TLTD_to_UBTangNW',
'bs@TLTD_to_AdjCapt',
'bs@TLTD_to_TangNW',
'bs@TLTD_to_Capt',
'bs@TL_to_UBTangNW',
'bs@TL_to_TangNW',
'bs@TL_to_TA',
'bs@TL_to_TNW',
'bs@TL_to_AdjCapt',
'bs@TL_to_Capt',
'bs@CL_to_UBTangNW',
'bs@CL_to_TangNW',
'bs@CL_to_TL',
'bs@CL_to_TNW',
'bs@CL_to_AdjCapt',
'bs@CL_to_TA',
'bs@CL_to_Capt',
'bs@AdjTD_to_AdjCapt',
'bs@AdjTD_to_Capt',

'bs@TLTD_to_TLTD_and_TNW',
'bs@TLTD_to_TLTD_and_UBTangNW',
'bs@TD_to_CA_exc_CL',
'bs@TD_to_TA_exc_TL',
'bs@TL_to_TL_exc_CL'
]

nume = ['Total Debt']*6 + ['Senior Debt']*2 + ['LONGTERMDEBT']*6+['Total Liabilities']*6+[ 'Current Liabilities']*7+['Adjusted Total Debt']*2
deno = ['Total Assets', 'Tangible Net Worth','Capitalization','Adjusted Capitalization', 'Total Net Worth',  'Union Bank Tangible Net Worth',
 'Capitalization','Adjusted Capitalization',
 'Total Net Worth', 'Total Assets','Union Bank Tangible Net Worth', 'Adjusted Capitalization', 'Tangible Net Worth','Capitalization',
'Union Bank Tangible Net Worth', 'Tangible Net Worth','Total Assets','Total Net Worth','Adjusted Capitalization', 'Capitalization',
'Union Bank Tangible Net Worth','Tangible Net Worth', 'Total Liabilities', 'Total Net Worth','Adjusted Capitalization',  'Total Assets','Capitalization',
 'Adjusted Capitalization', 'Capitalization'
 ]

for i, factor in enumerate(Balance_sheet_leverage[:-5]):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])

dat['bs@TLTD_to_TLTD_and_TNW'] = dat['LONGTERMDEBT']/(dat['Total LTD']+dat['Total Net Worth'])
dat['bs@TLTD_to_TLTD_and_UBTangNW'] = dat['LONGTERMDEBT']/(dat['Total LTD']+dat[ 'Union Bank Tangible Net Worth'])
dat['bs@TD_to_CA_exc_CL'] = dat['Total Debt']/(dat['Current Assets']-dat['Current Liabilities'])
dat['bs@TD_to_TA_exc_TL'] = dat['Total Debt']/(dat['Total Assets']-dat['Total Liabilities'])
dat['bs@TL_to_TL_exc_CL'] =  dat['Total Liabilities']/(dat['Total Liabilities']-dat['Current Liabilities'])


#%%
cash_flow_leverage=[
'cf@TD_to_UBEBITDA',
'cf@TD_to_EBITDA',
'cf@TD_to_ACF',
'cf@SD_to_UBEBITDA',
'cf@SD_to_EBITDA',
'cf@AdjTD_to_EBITDA',
'cf@AdjTD_to_UBEBITDA',
'cf@AdjTD_to_ACF',
'cf@FOCF_to_TD',
'cf@FFO_to_TD',
'cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div',
'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',
'cf@AdjTD_to_ACF_and_LE',
'cf@AdjTD_to_NP_and_Dep_and_Amo',
'cf@TD_to_NP_and_Dep_and_Amo',
'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',
'cf@TD_to_EBIT_exc_Div_exc_Taxes',
'cf@TD_to_ACF_and_LE',
]

nume = ['Total Debt']*3+ ['Senior Debt']*2+['Adjusted Total Debt']*3+['Free Operating Cash Flow (FOCF)','Funds from Operations (FFO)']
deno = [ 'Union Bank EBITDA', 'EBITDA', 'ACF',
 'Union Bank EBITDA', 'EBITDA',
'EBITDA',  'Union Bank EBITDA', 'ACF',
 'Total Debt', 'Total Debt',
]

for i, factor in enumerate(cash_flow_leverage[:-8]):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])


dat['cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div'] = dat['Adjusted Total Debt']/(dat['Net Profit']+dat['Depreciation']+dat['Amortization']-dat['Dividends'])
dat['cf@AdjTD_to_EBIT_exc_Div_exc_Taxes'] = dat['Adjusted Total Debt'] / (dat['EBIT']-dat['Dividends']-dat['Taxes'])
dat['cf@AdjTD_to_ACF_and_LE'] = dat['Adjusted Total Debt'] / (dat['ACF'] + dat['Lease Expense'])
dat['cf@AdjTD_to_NP_and_Dep_and_Amo'] = dat['Adjusted Total Debt'] / (dat['Net Profit']+dat['Depreciation']+dat['Amortization'])
dat['cf@TD_to_NP_and_Dep_and_Amo'] = dat['Total Debt']/(dat['Net Profit']+dat['Depreciation']+dat['Amortization'])
dat['cf@TD_to_NP_and_Dep_and_Amo_exc_Div'] =  dat['Total Debt']/(dat['Net Profit']+dat['Depreciation']+dat['Amortization']-dat['Dividends'])
dat['cf@TD_to_EBIT_exc_Div_exc_Taxes'] = dat['Total Debt']/(dat['EBIT']-dat['Dividends']-dat['Taxes'])
dat['cf@TD_to_ACF_and_LE'] = dat['Total Debt']/(dat['ACF'] + dat['Lease Expense'])



#%%
debt_service_coverage=[
'ds@NP_to_TL',
'ds@NP_to_CL',
'ds@NP_to_IE',
'ds@UBEBIT_to_IE',
'ds@UBEBIT_to_DS',
'ds@EBIT_to_IE',
'ds@EBIT_to_DS',
'ds@UBEBITDA_to_IE',
'ds@EBITDA_to_IE',
'ds@FFO_to_IE',
'ds@NS_to_IE',
'ds@TL_to_IE',
'ds@ACF_to_DS',
'ds@ACF_and_LE_to_DS_and_LE',
'ds@EBIT_exc_Div_exc_Taxes_to_IE',
'ds@UBEBIT_and_LE_to_DS_and_LE',
'ds@UBEBIT_exc_Div_exc_Taxes_to_IE',
'ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
'ds@UBEBIT_exc_Div_exc_Taxes_to_DS',
'ds@EBIT_exc_Div_exc_Taxes_to_DS',
'ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
'ds@EBIT_and_LE_to_DS_and_LE',
'ds@NP_and_IE_to_IE',
'ds@NP_and_IE_to_TL',
'ds@DSCR']



nume = ['Net Profit']*3+ [ 'Union Bank EBIT']*2+['EBIT']*2+['Union Bank EBITDA', 'EBITDA','Funds from Operations (FFO)', 'Net Sales', 'Total Liabilities','ACF']
deno = [ 'Total Liabilities', 'Current Liabilities','Interest Expense', 
'Interest Expense', 'Debt Service',
'Interest Expense', 'Debt Service',
'Interest Expense','Interest Expense','Interest Expense','Interest Expense','Interest Expense',
'Debt Service']

for i, factor in enumerate(debt_service_coverage[:13]):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])


dat['ds@ACF_and_LE_to_DS_and_LE'] = (dat['ACF'] + dat['Lease Expense']) / (dat['Debt Service'] + dat['Lease Expense']) 
dat['ds@EBIT_exc_Div_exc_Taxes_to_IE'] = (dat['EBIT']-dat['Dividends']-dat['Taxes'] )/ dat['Interest Expense']
dat['ds@UBEBIT_and_LE_to_DS_and_LE'] =  (dat['Union Bank EBIT'] + dat['Lease Expense']) / (dat['Debt Service'] + dat['Lease Expense']) 
dat['ds@UBEBIT_exc_Div_exc_Taxes_to_IE'] = (dat['Union Bank EBIT']-dat['Dividends']-dat['Taxes'] )/ dat['Interest Expense']
dat['ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE'] = (dat['Union Bank EBIT']-dat['Dividends']-dat['Taxes']+dat['Lease Expense'])/ (dat['Debt Service'] + dat['Lease Expense']) 
dat['ds@UBEBIT_exc_Div_exc_Taxes_to_DS']= (dat['Union Bank EBIT']-dat['Dividends']-dat['Taxes'])/ dat['Debt Service']  
dat['ds@EBIT_exc_Div_exc_Taxes_to_DS'] = (dat['EBIT']-dat['Dividends']-dat['Taxes'])/ dat['Debt Service']  
dat['ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE'] = (dat['EBIT']-dat['Dividends']-dat['Taxes']+dat['Lease Expense'])/ (dat['Debt Service'] + dat['Lease Expense']) 
dat['ds@EBIT_and_LE_to_DS_and_LE'] = (dat['EBIT'] + dat['Lease Expense']) / (dat['Debt Service'] + dat['Lease Expense']) 
dat['ds@NP_and_IE_to_IE'] = (dat['Net Profit'] + dat['Interest Expense']) / dat['Interest Expense']
dat['ds@NP_and_IE_to_TL'] = (dat['Net Profit'] + dat['Interest Expense']) / dat['Total Liabilities']
dat['ds@DSCR'] = (dat['Net Profit'] + dat['Depreciation']+ dat['Interest Expense']) / dat['Debt Service']



#%%
liquidity=[
'liq@ECE_to_TD',
'liq@ECE_to_TL',
'liq@ECE_to_AdjTD',
'liq@ECE_to_TA',
'liq@ECE_to_CL',
'liq@ECE_to_CA',
'liq@CA_to_TL',
'liq@CA_to_TA',
'liq@RE_to_CL',
'liq@CA_exc_TI_to_TD',
'liq@CA_exc_TI_to_/TL',
'liq@CA_exc_TI_to_/AdjTD',
'liq@CA_exc_TI_to_/TA',
'liq@CA_exc_CL_to_TD',
'liq@CA_exc_CL_to_TL',
'liq@CA_exc_CL_to_AdjTD',
'liq@CA_exc_CL_to_TA',
'liq@CA_exc_CL_to_CA',
'liq@CA_exc_CL_to_CL',
]

nume = ['Ending Cash & Equivalents']*6+['Current Assets']*2+['Retained Earnings']
deno = [ 'Total Debt','Total Liabilities', 'Adjusted Total Debt','Total Assets', 'Current Liabilities', 'Current Assets',
'Total Liabilities', 'Total Assets',
'Current Liabilities'
]
for i, factor in enumerate(liquidity[:9]):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])


dat['liq@CA_exc_TI_to_TD'] = (dat['Current Assets'] - dat['Total Inventory']) / dat['Total Debt']
dat['liq@CA_exc_TI_to_/TL'] = (dat['Current Assets'] - dat['Total Inventory']) / dat['Total Liabilities']
dat['liq@CA_exc_TI_to_/AdjTD'] = (dat['Current Assets'] - dat['Total Inventory']) / dat[ 'Adjusted Total Debt']
dat['liq@CA_exc_TI_to_/TA'] = (dat['Current Assets'] - dat['Total Inventory']) / dat['Total Assets']
dat['liq@CA_exc_CL_to_TD'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Total Debt']
dat['liq@CA_exc_CL_to_TL'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Total Liabilities']
dat['liq@CA_exc_CL_to_AdjTD'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Adjusted Total Debt']
dat['liq@CA_exc_CL_to_TA'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Total Assets']
dat['liq@CA_exc_CL_to_CA'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Current Assets']
dat['liq@CA_exc_CL_to_CL'] = (dat['Current Assets'] - dat['Current Liabilities']) / dat['Current Liabilities']



#%%
profitability = [
 'prof@EBIT_to_AdjCapt',
 'prof@EBIT_to_Capt',
 'prof@EBIT_to_NS',
 'prof@EBIT_to_TangA',
 'prof@EBIT_to_TA',
 'prof@EBITDA_to_AdjCapt',
 'prof@EBITDA_to_Capt',
 'prof@EBITDA_to_NS',
 'prof@EBITDA_to_TangA',
 'prof@EBITDA_to_TA',
 'prof@NOP_to_NP',
 'prof@NOP_to_NS',
 'prof@NOP_to_TangNW',
 'prof@NOP_to_TA',
 'prof@NOP_to_TNW',
 'prof@NOP_to_UBTangNW',
 'prof@RE_to_TA',
 'prof@RE_to_TNW',
 'prof@RE_to_UBTangNW',
 'prof@UBEBIT_to_AdjCapt',
 'prof@UBEBIT_to_Capt',
 'prof@UBEBIT_to_NS',
 'prof@UBEBIT_to_TangA',
 'prof@UBEBIT_to_TA',
 'prof@UBEBITDA_to_AdjCapt',
 'prof@UBEBITDA_to_Capt',
 'prof@UBEBITDA_to_NS',
 'prof@UBEBITDA_to_TangA',
 'prof@UBEBITDA_to_TA',
 'prof@PbT_to_TA',
 'prof@CD_to_NP',
 'prof@NP_exc_EI',
 'prof@EBIT_exc_II_to_Capt',
 'prof@NP_exc_EI_to_TA']


nume = ['EBIT']*5+['EBITDA']*5+['Net Operating Profit']*6+['Retained Earnings']*3+['Union Bank EBIT']*5+['Union Bank EBITDA']*5+['Profit before Taxes','DividendCommon']
deno = ['Adjusted Capitalization', 'Capitalization', 'Net Sales', 'Tangible Assets', 'Total Assets',
'Adjusted Capitalization', 'Capitalization', 'Net Sales', 'Tangible Assets', 'Total Assets',
'Net Profit','Net Sales','Tangible Net Worth','Total Assets','Total Net Worth','Union Bank Tangible Net Worth',
'Total Assets','Total Net Worth','Union Bank Tangible Net Worth',
'Adjusted Capitalization','Capitalization','Net Sales','Tangible Assets','Total Assets',
'Adjusted Capitalization','Capitalization','Net Sales','Tangible Assets','Total Assets',
'Total Assets','Net Profit']


for i, factor in enumerate(profitability[:31]):
    dat[factor] = dat[nume[i]]/dat[deno[i]]
    formula.append(factor+' is build by '+ nume[i]+' by '+deno[i])
    print(formula[-1])

dat['prof@NP_exc_EI'] = dat['Net Profit'] - dat['Extraordinary Items']
dat['prof@EBIT_exc_II_to_Capt'] = (dat['EBIT']-dat['Interest Income']) / dat['Capitalization']
dat['prof@NP_exc_EI_to_TA'] = (dat['Net Profit']-dat['Extraordinary Items']) / dat['Total Assets']


#%% 
size=[
'size@TangNW_to_TA',
'size@TangNW_to_TA_exc_CA',
'size@UBTangNW_to_TA',
'size@UBTangNW_to_TA_exc_CA',
'size@TNW_to_TA_exc_CA',
'size@TNW_to_TA']

dat['size@TangNW_to_TA'] = dat['Tangible Net Worth'] / dat['Total Assets']
dat['size@TangNW_to_TA_exc_CA'] = dat['Tangible Net Worth'] / (dat['Total Assets']-dat['Current Assets'])
dat['size@UBTangNW_to_TA'] = dat['Union Bank Tangible Net Worth'] / dat['Total Assets']
dat['size@UBTangNW_to_TA_exc_CA'] = dat['Union Bank Tangible Net Worth'] /(dat['Total Assets']-dat['Current Assets'])
dat['size@TNW_to_TA_exc_CA'] = dat['Total Net Worth'] / (dat['Total Assets']-dat['Current Assets'])
dat['size@TNW_to_TA'] = dat['Total Net Worth'] / dat['Total Assets']


#%%
BTMU_factors=[
'BTMU@TD_to_EBITDA',
'BTMU@EBITDA_to_IE',
'BTMU@TNW_to_TA',
'BTMU@TD_to_TNW',
'BTMU@OP_to_Sales',
'BTMU@NP_exc_EI_to_TA',
]

dat['BTMU@TD_to_EBITDA'] = dat['Total Debt'] / dat['EBITDA']
dat['BTMU@EBITDA_to_IE'] = dat['EBITDA'] / dat['Interest Expense']
dat['BTMU@TNW_to_TA'] = dat['Total Net Worth'] / dat['Total Assets']
dat['BTMU@TD_to_TNW'] = dat['Total Debt'] / dat['Total Net Worth']
dat['BTMU@OP_to_Sales'] = dat['Net Operating Profit'] / dat['Net Sales']
dat['BTMU@NP_exc_EI_to_TA']  = (dat['Net Profit'] - dat['Extraordinary Items'])/ dat['Total Assets']


#%%
SP_factors=[
'SP@TD_to_TD_and_TNW',
'SP@EBIT_to_TD_and_TNW',
'SP@EBIT_to_IE',
'SP@EBITDA_to_IE',
]

dat['SP@TD_to_TD_and_TNW'] = dat['Total Debt'] / (dat['Total Debt'] + dat['Total Net Worth'])
dat['SP@EBIT_to_TD_and_TNW'] =  dat['EBIT'] / (dat['Total Debt'] + dat['Total Net Worth'])
dat['SP@EBIT_to_IE'] = dat['EBIT'] / dat['Interest Expense']
dat['SP@EBITDA_to_IE'] = dat['EBITDA'] / dat['Interest Expense']


#%%
to_rename=dict(zip([
'ACF',
 'Adjusted Capitalization',
 'Adjusted Total Debt',
 'Amortization',
 'Average Profit Margin, 2 yrs',
 'Capitalization',
 'Current Assets',
 'Current Liabilities',
 'Current Ratio',
 'INTERESTEXPENSE',
 'CPLTD',
 'Debt Service',
 'Depreciation',
 'DIVIDENDSSTOCK',
 'DividendCommon',
 'DIVIDENDSPREF',
 'Dividends',
 'EBIT',
 'EBITDA',
 'Ending Cash & Equivalents',
 'AFTERTAXINCOME',
 'AFTERTAXEXPENSE',
 'Extraordinary Items',
 'Free Operating Cash Flow_Modified',
 'Funds from Operations_Modified',
 'Interest Expense',
 'Total Inventory',
 'Lease Expense',
 'Net Accounts Receivable',
 'Net Operating Profit',
 'Net Profit',
 'Net Sales',
 'Profit before Taxes',
 'Quick Ratio',
 'Retained Earnings',
 'Return on Assets',
 'Return on Equity',
 'Senior Debt',
 'NETTANGIBLES',
 'Tangible Assets',
 'Tangible Net Worth',
 'INCOMETAXEXP',
 'INCOMETAXCREDIT',
 'Taxes',
 'Total Assets',
 'Total Debt',
 'LONGTERMDEBT',
 'CAPLEASEOBLIG',
 'Total LTD',
 'Total Liabilities',
 'Total Net Worth',
 'Union Bank Current Ratio',
 'Union Bank EBIT',
 'Union Bank EBITDA',
 'Union Bank Quick Ratio',
 'Union Bank Tangible Net Worth',
 'Operating Profit Margin %',
 'Net Profit Margin %',
 'Gross Profit Margin %',
 'Gross Profit Margin %.1',
 'Free Operating Cash Flow (FOCF)',
 'Funds from Operations (FFO)',
 'INTERESTEXPENSE_2',
 'CAPINTEREST',
 'Interest Income',
 'Total Interest Inc(Exp)',
 'INCOMETAXEXP_1',
 'INCOMETAXCREDIT_1',
 'TOTAL INCOME TAX EXPENSE',
 'quant2',
 'quant4',
 'quant5'],[
 	'cf@ACF',
 'size@Adjusted Capitalization',
 'size@Adjusted Total Debt',
 'size@Amortization',
 'prof@Average Profit Margin, 2 yrs',
 'size@Capitalization',
 'size@Current Assets',
 'size@Current Liabilities',
 'liq@Current Ratio',
 'ds@INTERESTEXPENSE',
 'bs@CPLTD',
 'ds@Debt Service',
 'cf@Depreciation',
 'prof@DIVIDENDSSTOCK',
 'prof@DividendCommon',
 'prof@DIVIDENDSPREF',
 'prof@Dividends',
 'size@EBIT',
 'size@EBITDA',
 'cf@Ending Cash & Equivalents',
 'prof@AFTERTAXINCOME',
 'ds@AFTERTAXEXPENSE',
 'size@Extraordinary Items',
 'size@Free Operating Cash Flow_Modified',
 'size@Funds from Operations_Modified',
 'ds@Interest Expense',
 'size@Total Inventory',
 'cf@Lease Expense',
 'size@Net Accounts Receivable',
 'size@Net Operating Profit',
 'size@Net Profit',
 'size@Net_Sales',
 'size@Profit before Taxes',
 'liq@Quick Ratio',
 'size@Retained Earnings',
 'prof@Return on Assets',
 'prof@Return on Equity',
 'bs@Senior Debt',
 'size@NETTANGIBLES',
 'size@Tangible Assets',
 'size@Tangible Net Worth',
 'others@INCOMETAXEXP',
 'others@INCOMETAXCREDIT',
 'others@Taxes',
 'size@Total Assets',
 'size@Total Debt',
 'bs@LONGTERMDEBT',
 'others@CAPLEASEOBLIG',
 'bs@Total LTD',
 'size@Total Liabilities',
 'size@Total Net Worth',
 'liq@Union Bank Current Ratio',
 'size@Union Bank EBIT',
 'size@Union Bank EBITDA',
 'liq@Union Bank Quick Ratio',
 'size@Union Bank Tangible Net Worth',
 'prof@Operating Profit Margin %',
 'prof@Net Profit Margin %',
 'prof@Gross Profit Margin %',
 'prof@Gross Profit Margin %.1',
 'size@Free Operating Cash Flow (FOCF)',
 'size@Funds from Operations (FFO)',
 'ds@INTERESTEXPENSE_2',
 'others@CAPINTEREST',
 'prof@Interest Income',
 'others@Total Interest Inc(Exp)',
 'others@INCOMETAXEXP_1',
 'others@INCOMETAXCREDIT_1',
 'others@TOTAL INCOME TAX EXPENSE',
 'cf@quant2',
 'bs@quant4',
 'liq@quant5']))

dat.rename(columns=to_rename, inplace=True)


# add current quant2 into the data:
dat['cf@TD_COP'] = dat['size@Total Debt'] / dat['size@Net Operating Profit']
# add one tokyo factor into the data:
dat['prof@TangA_to_NS'] = dat['size@Tangible Assets'] / dat['size@Net_Sales']
# add one tokyo factor into the data:
dat['cf@FOCF_to_TL'] = dat['size@Free Operating Cash Flow (FOCF)'] / dat['size@Total Liabilities']


dat.to_pickle(r'..\newdata\prod_allgood_7daysclean_addratios_addDRD.pkl.xz') 
# -*- coding: utf-8 -*-
"""
Created on Thu May  3 16:57:43 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

dat = pd.read_pickle(r'..\newdata\prod_allgood_7daysclean_addratios_addDRD.pkl.xz')
dat['Net_Sales'] = dat['size@Net_Sales']


# about 4440 obs has Nan in factors including net sales:
valid = dat.loc[dat['Net_Sales'] == dat['Net_Sales'] ]
nonvalid = dat.loc[dat['Net_Sales'] != dat['Net_Sales'] ]
# remove two audit method 'Proforma' and 'Projection'
valid2 = valid.loc[valid['Audit Method'] != 'Proforma']
valid2 = valid2.loc[valid2['Audit Method'] != 'Projection']



valid2.to_pickle(r'..\newdata\prod_allgood_7daysclean_addratios_addDRD_valid.pkl.xz') 
# -*- coding: utf-8 -*-
"""
Created on Mon May 21 13:45:51 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
dat = pd.read_pickle(r'..\newdata\prod_allgood_7daysclean_addratios_addDRD_valid.pkl.xz')


cutoff = 1000

dat_lc = dat.query('Net_Sales>{}'.format(cutoff*1e6))
dat_mm = dat.query('Net_Sales<={}'.format(cutoff*1e6))

lc_customer = set(dat_lc['CUSTOMERID'].tolist())
mm_customer = set(dat_mm['CUSTOMERID'].tolist())
len(lc_customer&mm_customer)

pl_overlap = list(lc_customer&mm_customer)


#%%
def isLC(ID, how='mean'):
    global dat_mm, dat_lc
    temp_lc = dat_lc.query('CUSTOMERID=={}'.format(ID))
    temp_mm = dat_mm.query('CUSTOMERID=={}'.format(ID))
    
    if how=='mean':
        return (pd.concat([temp_lc,temp_mm], axis=0)['Net_Sales'].mean()>5e8)      
    elif how=='first':
        return (temp_lc.archive_date.min() < temp_mm.archive_date.min())     
    elif how=='last':
        return (temp_lc.archive_date.max() > temp_mm.archive_date.max())
    else:
        raise Exception('"how" must be one of [mean, first, last]')

def addto(adto, ID):
    global dat_mm, dat_lc
    if adto=='LC':
        temp = dat_mm.query('CUSTOMERID=={}'.format(ID))
        dat_lc = pd.concat([dat_lc,temp], axis=0)
    elif adto=='MM':
        temp = dat_lc.query('CUSTOMERID=={}'.format(ID))
        dat_mm = pd.concat([dat_mm,temp], axis=0)
    else:
        raise Exception('LC or MM')

def removefrom(refr, ID):
    global dat_mm, dat_lc
    if refr=='MM':
        dat_mm = dat_mm.query('CUSTOMERID !={}'.format(ID))
    elif refr=='LC':   
        dat_lc = dat_lc.query('CUSTOMERID !={}'.format(ID))
    else:
        raise Exception('LC or MM')


#%%
for ID in pl_overlap:
    if isLC(ID,'last'):
        addto('LC',ID)
        removefrom('MM',ID)       
    else:
        addto('MM',ID)
        removefrom('LC',ID)



#%% attach new quali factors:
data_MM = dat_mm.copy()
data_LC = dat_lc.copy()
data_MM['CUSTOMERID'] = pd.to_numeric(data_MM['CUSTOMERID'])
data_LC['CUSTOMERID'] = pd.to_numeric(data_LC['CUSTOMERID'])


ra_data = pd.read_excel(r'..\newdata\Unweighted Qual Mapping\ra_occi_060418.xlsx')
ra_data = ra_data[['CUSTOMERID', 'ARCHIVEID', 'Access_Outside_Capital', 'Excp_Underwrite_For_Leverage', 'Info_Rptg_Timely_Manner', 'Management_Quality', 'Market_Outlook_Of_Borrower', 'Pct_Revenue_3_Large_Custs']]
ra_data.rename(columns={'ARCHIVEID': 'Archive ID'}, inplace=True)


data_MM = pd.merge(data_MM, ra_data, how = 'left', on = ['CUSTOMERID', 'Archive ID']) 

data_MM['Access_Outside_Capital'].count()/data_MM['CUSTOMERID'].count() #86.4%
data_MM['Excp_Underwrite_For_Leverage'].count()/data_MM['CUSTOMERID'].count() #93.4%
data_MM['Info_Rptg_Timely_Manner'].count()/data_MM['CUSTOMERID'].count() #88.2%
data_MM['Management_Quality'].count()/data_MM['CUSTOMERID'].count() #93.2%
data_MM['Market_Outlook_Of_Borrower'].count()/data_MM['CUSTOMERID'].count() #95.9%
data_MM['Pct_Revenue_3_Large_Custs'].count()/data_MM['CUSTOMERID'].count() #85.6%
       
data_LC = pd.merge(data_LC, ra_data, how = 'left', on = ['CUSTOMERID', 'Archive ID']) 

data_LC['Access_Outside_Capital'].count()/data_LC['CUSTOMERID'].count() #97.8%
data_LC['Excp_Underwrite_For_Leverage'].count()/data_LC['CUSTOMERID'].count() #97.1%
data_LC['Info_Rptg_Timely_Manner'].count()/data_LC['CUSTOMERID'].count() #96.2%
data_LC['Management_Quality'].count()/data_LC['CUSTOMERID'].count() #98.1%
data_LC['Market_Outlook_Of_Borrower'].count()/data_LC['CUSTOMERID'].count() #98.8%
data_LC['Pct_Revenue_3_Large_Custs'].count()/data_LC['CUSTOMERID'].count() #95.3%


#%%
data_MM.to_pickle(r'..\newdata\dat_mm_by{cut}_last_cs.pkl.xz'.format(cut=cutoff))
data_LC.to_pickle(r'..\newdata\dat_lc_by{cut}_last_cs.pkl.xz'.format(cut=cutoff))
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 23 10:43:46 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD, buildpseudodef, buildpseudodef2
import seaborn as sns
import matplotlib.pyplot as plt

def barplot(rawdata, subset, y_col='def_flag', savefig=True):
    '''

    Public method that present distribution plot for quali subset
    It will ignore NA data

    Parameters: 

    rawdata:     DataFrame for plot

    subset:     list of quali factors' name. 

    y_col:      str, default 'def_flag'
                the columns name for y

    savefig:    boolean, default True
                whether save png file in current working directory.  
    
    '''

    
    # add this adjusted mean function in Ver 1.5 for plotting
    def _adjmean(x):
        if x.sum()==0:
            return (1/x.size)
        else:
            return x.mean()

    for factor in subset:
        dataforplot = rawdata.dropna(subset=[factor])
        letter = list(set(dataforplot[factor])) # add in Ver. 1.3
        letter.sort()
        fig = plt.figure(figsize=(10,8))
        fig.suptitle(factor)
        ax1 = fig.add_subplot(111)
        sns.countplot(x=factor, data=dataforplot, ax=ax1,order=letter, alpha=0.7, palette='Blues_d')
        ax1.set_xlabel('Answers')
        ax2 = ax1.twinx()
        sns.pointplot(x=factor, y=y_col, data=dataforplot, ax=ax2, order=letter, ci=0, estimator=_adjmean) # modified in Ver 1.5
        ax2.grid(None)
        ax2.set_ylabel('mean of PD')
        ax2.set_ylim(bottom=0) # add this line in Ver 1.1
        if savefig:
            fig.savefig(factor+'_qualibar.png')


#%%
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
MS_dict = dict(zip(MS['PDRR'],MS['new_mid']))

dat_prod = pd.read_pickle(r'..\newdata\prod_1000.pkl.xz')
cutoff = 20160101
dat_prod = dat_prod.query('timestamp<{}'.format(cutoff)) 



dat_prod['PD_frPDRR'] = dat_prod['Final_PD_Risk_Rating'].transform(lambda x: np.nan if pd.isnull(x) else MS_dict[x]) 

quali_factor=[
 'qual1',
 'qual2',
 'qual3',
 'qual4',
 'Access_Outside_Capital',
 'Excp_Underwrite_For_Leverage',
 'Info_Rptg_Timely_Manner',
 'Management_Quality',
 'Market_Outlook_Of_Borrower',
 'Pct_Revenue_3_Large_Custs']


barplot(dat_prod, subset=quali_factor, y_col='PD_frPDRR', savefig=True)


#%%
for name in quali_factor:
    dat_prod['factor_meanPD'] = dat_prod[name]
    dat_prod['factor_meanPD'].replace(dict(dat_prod.groupby(name).mean()['PD_frPDRR']), inplace=True)
    dat_prod['factor_meanlogitPD'] = [np.log(x/(1-x)) for x in dat_prod['factor_meanPD']]
    s_mean = dat_prod['factor_meanlogitPD'].mean()
    s_std = dat_prod['factor_meanlogitPD'].std()
    dat_prod['factor_score'] = 50*(dat_prod['factor_meanlogitPD'] - s_mean) / s_std
    print(dat_prod.groupby(name).mean()['factor_score'])
    sd = SomersD(dat_prod['Final_PD_Risk_Rating'], dat_prod['factor_score'])
    print('SomersD of {name} is {sd:6.5f}'.format(name=name,sd=sd))
    print('**************************************************************')



'''
qual1
A   -110.262491
B      0.832055
C     63.967162
D     26.720796
Name: factor_score, dtype: float64
SomersD of qual1 is 0.33431
**************************************************************
qual2
A    -18.162094
B     91.122716
C    266.210660
D     78.647786
Name: factor_score, dtype: float64
SomersD of qual2 is 0.13622
**************************************************************
qual3
A     13.779704
B    186.122431
C     69.151848
D     95.057303
E    -63.549017
F    -20.337306
Name: factor_score, dtype: float64
SomersD of qual3 is 0.21810
**************************************************************
qual4
A    -75.319882
B      0.010202
C    102.776161
Name: factor_score, dtype: float64
SomersD of qual4 is 0.25991
**************************************************************
Access_Outside_Capital
A   -48.227694
B    39.522365
C    80.812229
Name: factor_score, dtype: float64
SomersD of Access_Outside_Capital is 0.32562
**************************************************************
Excp_Underwrite_For_Leverage
A    88.570495
B   -28.218535
Name: factor_score, dtype: float64
SomersD of Excp_Underwrite_For_Leverage is 0.12504
**************************************************************
Info_Rptg_Timely_Manner
A     -6.188561
B     90.037347
C    569.343390
Name: factor_score, dtype: float64
SomersD of Info_Rptg_Timely_Manner is 0.01869
**************************************************************
Management_Quality
A    -65.703147
B     -0.494011
C     56.499362
D    121.258098
E    104.841422
Name: factor_score, dtype: float64
SomersD of Management_Quality is 0.32346
**************************************************************
Market_Outlook_Of_Borrower
A    -62.210374
B    -11.040792
C    121.315193
Name: factor_score, dtype: float64
SomersD of Market_Outlook_Of_Borrower is 0.10159
**************************************************************
Pct_Revenue_3_Large_Custs
A   -128.054064
B      1.823769
C     23.092355
Name: factor_score, dtype: float64
SomersD of Pct_Revenue_3_Large_Custs is -0.00804
**************************************************************
'''# -*- coding: utf-8 -*-
"""
Created on Thu Aug 23 15:42:33 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD, buildpseudodef, buildpseudodef2


dat_prod = pd.read_pickle(r'..\newdata\dat_lc_by1000_last.pkl.xz')
dat_hist = pd.read_pickle(r'..\newdata\hist_lc_by1000_last.pkl.xz')


# change name for following work
dat_hist['Final_PD_Risk_Rating'] = dat_hist['implied_internal_PDRR']

# unify timestamp in prod and hist data
dat_prod['timestamp'] = pd.to_datetime(dat_prod['archive_date'])
dat_hist['timestamp'] = pd.to_datetime(dat_hist['STATEMENTDATE'])

# create column to identify dataset source
dat_prod['dataset'] = 'production'
dat_hist['dataset'] = 'historical'

factors_prod = factors_combo= [
'cf@TD_COP',
'prof@TangA_to_NS',
'cf@FOCF_to_TL',
 'cf@ACF',
 'size@Adjusted Capitalization',
 'size@Adjusted Total Debt',
 'size@Amortization',
 'prof@Average Profit Margin, 2 yrs',
 'size@Capitalization',
 'size@Current Assets',
 'size@Current Liabilities',
 'liq@Current Ratio',
 'ds@INTERESTEXPENSE',
 'bs@CPLTD',
 'ds@Debt Service',
 'cf@Depreciation',
 'prof@DIVIDENDSSTOCK',
 'prof@DividendCommon',
 'prof@DIVIDENDSPREF',
 'prof@Dividends',
 'size@EBIT',
 'size@EBITDA',
 'cf@Ending Cash & Equivalents',
 'prof@AFTERTAXINCOME',
 'ds@AFTERTAXEXPENSE',
 'size@Extraordinary Items',
 'size@Free Operating Cash Flow_Modified',
 'size@Funds from Operations_Modified',
 'ds@Interest Expense',
 'size@Total Inventory',
 'cf@Lease Expense',
 'size@Net Accounts Receivable',
 'size@Net Operating Profit',
 'size@Net Profit',
 'size@Net_Sales',
 'size@Profit before Taxes',
 'liq@Quick Ratio',
 'size@Retained Earnings',
 'prof@Return on Assets',
 'prof@Return on Equity',
 'bs@Senior Debt',
 'size@NETTANGIBLES',
 'size@Tangible Assets',
 'size@Tangible Net Worth',
 'size@Total Assets',
 'size@Total Debt',
 'bs@LONGTERMDEBT',
 'bs@Total LTD',
 'size@Total Liabilities',
 'size@Total Net Worth',
 'liq@Union Bank Current Ratio',
 'size@Union Bank EBIT',
 'size@Union Bank EBITDA',
 'liq@Union Bank Quick Ratio',
 'size@Union Bank Tangible Net Worth',
 'prof@Operating Profit Margin %',
 'prof@Net Profit Margin %',
 'prof@Gross Profit Margin %',
 'size@Free Operating Cash Flow (FOCF)',
 'size@Funds from Operations (FFO)',
 'prof@Interest Income',
 'act@NS_to_CL',
 'act@NS_to_UBTangNW',
 'act@NS_to_TA',
 'act@NS_to_NAR',
 'act@NS_to_Inv',
 'act@NS_to_TNW',
 'bs@TD_to_TA',
 'bs@TD_to_TangNW',
 'bs@TD_to_Capt',
 'bs@TD_to_AdjCapt',
 'bs@TD_to_TNW',
 'bs@TD_to_UBTangNW',
 'bs@SD_to_Capt',
 'bs@SD_to_AdjCapt',
 'bs@TLTD_to_TNW',
 'bs@TLTD_to_TA',
 'bs@TLTD_to_UBTangNW',
 'bs@TLTD_to_AdjCapt',
 'bs@TLTD_to_TangNW',
 'bs@TLTD_to_Capt',
 'bs@TL_to_UBTangNW',
 'bs@TL_to_TangNW',
 'bs@TL_to_TA',
 'bs@TL_to_TNW',
 'bs@TL_to_AdjCapt',
 'bs@TL_to_Capt',
 'bs@CL_to_UBTangNW',
 'bs@CL_to_TangNW',
 'bs@CL_to_TL',
 'bs@CL_to_TNW',
 'bs@CL_to_AdjCapt',
 'bs@CL_to_TA',
 'bs@CL_to_Capt',
 'bs@AdjTD_to_AdjCapt',
 'bs@AdjTD_to_Capt',
 'bs@TLTD_to_TLTD_and_TNW',
 'bs@TLTD_to_TLTD_and_UBTangNW',
 'bs@TD_to_CA_exc_CL',
 'bs@TD_to_TA_exc_TL',
 'bs@TL_to_TL_exc_CL',
 'cf@TD_to_UBEBITDA',
 'cf@TD_to_EBITDA',
 'cf@TD_to_ACF',
 'cf@SD_to_UBEBITDA',
 'cf@SD_to_EBITDA',
 'cf@AdjTD_to_EBITDA',
 'cf@AdjTD_to_UBEBITDA',
 'cf@AdjTD_to_ACF',
 'cf@FOCF_to_TD',
 'cf@FFO_to_TD',
 'cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',
 'cf@AdjTD_to_ACF_and_LE',
 'cf@AdjTD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@TD_to_EBIT_exc_Div_exc_Taxes',
 'cf@TD_to_ACF_and_LE',
 'ds@NP_to_TL',
 'ds@NP_to_CL',
 'ds@NP_to_IE',
 'ds@UBEBIT_to_IE',
 'ds@UBEBIT_to_DS',
 'ds@EBIT_to_IE',
 'ds@EBIT_to_DS',
 'ds@UBEBITDA_to_IE',
 'ds@EBITDA_to_IE',
 'ds@FFO_to_IE',
 'ds@NS_to_IE',
 'ds@TL_to_IE',
 'ds@ACF_to_DS',
 'ds@ACF_and_LE_to_DS_and_LE',
 'ds@EBIT_exc_Div_exc_Taxes_to_IE',
 'ds@UBEBIT_and_LE_to_DS_and_LE',
 'ds@UBEBIT_exc_Div_exc_Taxes_to_IE',
 'ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
 'ds@UBEBIT_exc_Div_exc_Taxes_to_DS',
 'ds@EBIT_exc_Div_exc_Taxes_to_DS',
 'ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
 'ds@EBIT_and_LE_to_DS_and_LE',
 'ds@NP_and_IE_to_IE',
 'ds@NP_and_IE_to_TL',
 'liq@ECE_to_TD',
 'liq@ECE_to_TL',
 'liq@ECE_to_AdjTD',
 'liq@ECE_to_TA',
 'liq@ECE_to_CL',
 'liq@ECE_to_CA',
 'liq@CA_to_TL',
 'liq@CA_to_TA',
 'liq@RE_to_CL',
 'liq@CA_exc_TI_to_TD',
 'liq@CA_exc_TI_to_/TL',
 'liq@CA_exc_TI_to_/AdjTD',
 'liq@CA_exc_TI_to_/TA',
 'liq@CA_exc_CL_to_TD',
 'liq@CA_exc_CL_to_TL',
 'liq@CA_exc_CL_to_AdjTD',
 'liq@CA_exc_CL_to_TA',
 'liq@CA_exc_CL_to_CA',
 'liq@CA_exc_CL_to_CL',
 'prof@EBIT_to_AdjCapt',
 'prof@EBIT_to_Capt',
 'prof@EBIT_to_NS',
 'prof@EBIT_to_TangA',
 'prof@EBIT_to_TA',
 'prof@EBITDA_to_AdjCapt',
 'prof@EBITDA_to_Capt',
 'prof@EBITDA_to_NS',
 'prof@EBITDA_to_TangA',
 'prof@EBITDA_to_TA',
 'prof@NOP_to_NP',
 'prof@NOP_to_NS',
 'prof@NOP_to_TangNW',
 'prof@NOP_to_TA',
 'prof@NOP_to_TNW',
 'prof@NOP_to_UBTangNW',
 'prof@RE_to_TA',
 'prof@RE_to_TNW',
 'prof@RE_to_UBTangNW',
 'prof@UBEBIT_to_AdjCapt',
 'prof@UBEBIT_to_Capt',
 'prof@UBEBIT_to_NS',
 'prof@UBEBIT_to_TangA',
 'prof@UBEBIT_to_TA',
 'prof@UBEBITDA_to_AdjCapt',
 'prof@UBEBITDA_to_Capt',
 'prof@UBEBITDA_to_NS',
 'prof@UBEBITDA_to_TangA',
 'prof@UBEBITDA_to_TA',
 'prof@PbT_to_TA',
 'prof@CD_to_NP',
 'prof@NP_exc_EI',
 'prof@EBIT_exc_II_to_Capt',
 'prof@NP_exc_EI_to_TA',
 'size@TangNW_to_TA',
 'size@TangNW_to_TA_exc_CA',
 'size@UBTangNW_to_TA',
 'size@UBTangNW_to_TA_exc_CA',
 'size@TNW_to_TA_exc_CA',
 'size@TNW_to_TA',
 'cf@quant2',
 'bs@quant4',
 'ds@DSCR']

factors_hist = [
'cf@TD_COP',
'prof@TangA_to_NS',
'cf@FOCF_to_TL',
 'cf@ACF',
 'size@Adjusted Capitalization',
 'size@Adjusted Total Debt',
 'size@Amortization',
 'prof@Average Profit Margin, 2 yrs',
 'size@Capitalization',
 'size@Current Assets',
 'size@Current Liabilities',
 'liq@Current Ratio',
 'ds@INTERESTEXPENSE',
 'bs@CPLTD',
 'ds@Debt Service',
 'cf@Depreciation',
 'prof@DIVIDENDSSTOCK',
 'prof@DividendCommon',
 'prof@DIVIDENDSPREF',
 'prof@Dividends',
 'size@EBIT',
 'size@EBITDA',
 'cf@Ending Cash & Equivalents',
 'prof@AFTERTAXINCOME',
 'ds@AFTERTAXEXPENSE',
 'size@Extraordinary Items',
 'ds@Interest Expense',
 'size@Total Inventory',
 'cf@Lease Expense',
 'size@Net Accounts Receivable',
 'size@Net Operating Profit',
 'size@Net Profit',
 'size@Net_Sales',
 'size@Profit before Taxes',
 'liq@Quick Ratio',
 'size@Retained Earnings',
 'prof@Return on Assets',
 'prof@Return on Equity',
 'bs@Senior Debt',
 'size@Tangible Assets',
 'size@Tangible Net Worth',
 'size@Total Assets',
 'size@Total Debt',
 'bs@LONGTERMDEBT',
 'bs@Total LTD',
 'size@Total Liabilities',
 'size@Total Net Worth',
 'liq@Union Bank Current Ratio',
 'size@Union Bank EBIT',
 'size@Union Bank EBITDA',
 'liq@Union Bank Quick Ratio',
 'size@Union Bank Tangible Net Worth',
 'prof@Operating Profit Margin %',
 'prof@Net Profit Margin %',
 'prof@Gross Profit Margin %',
 'size@Free Operating Cash Flow (FOCF)',
 'size@Funds from Operations (FFO)',
 'prof@Interest Income',
 'act@NS_to_CL',
 'act@NS_to_UBTangNW',
 'act@NS_to_TA',
 'act@NS_to_NAR',
 'act@NS_to_Inv',
 'act@NS_to_TNW',
 'bs@TD_to_TA',
 'bs@TD_to_TangNW',
 'bs@TD_to_Capt',
 'bs@TD_to_AdjCapt',
 'bs@TD_to_TNW',
 'bs@TD_to_UBTangNW',
 'bs@SD_to_Capt',
 'bs@SD_to_AdjCapt',
 'bs@TLTD_to_TNW',
 'bs@TLTD_to_TA',
 'bs@TLTD_to_UBTangNW',
 'bs@TLTD_to_AdjCapt',
 'bs@TLTD_to_TangNW',
 'bs@TLTD_to_Capt',
 'bs@TL_to_UBTangNW',
 'bs@TL_to_TangNW',
 'bs@TL_to_TA',
 'bs@TL_to_TNW',
 'bs@TL_to_AdjCapt',
 'bs@TL_to_Capt',
 'bs@CL_to_UBTangNW',
 'bs@CL_to_TangNW',
 'bs@CL_to_TL',
 'bs@CL_to_TNW',
 'bs@CL_to_AdjCapt',
 'bs@CL_to_TA',
 'bs@CL_to_Capt',
 'bs@AdjTD_to_AdjCapt',
 'bs@AdjTD_to_Capt',
 'bs@TLTD_to_TLTD_and_TNW',
 'bs@TLTD_to_TLTD_and_UBTangNW',
 'bs@TD_to_CA_exc_CL',
 'bs@TD_to_TA_exc_TL',
 'bs@TL_to_TL_exc_CL',
 'cf@TD_to_UBEBITDA',
 'cf@TD_to_EBITDA',
 'cf@TD_to_ACF',
 'cf@SD_to_UBEBITDA',
 'cf@SD_to_EBITDA',
 'cf@AdjTD_to_EBITDA',
 'cf@AdjTD_to_UBEBITDA',
 'cf@AdjTD_to_ACF',
 'cf@FOCF_to_TD',
 'cf@FFO_to_TD',
 'cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',
 'cf@AdjTD_to_ACF_and_LE',
 'cf@AdjTD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@TD_to_EBIT_exc_Div_exc_Taxes',
 'cf@TD_to_ACF_and_LE',
 'ds@NP_to_TL',
 'ds@NP_to_CL',
 'ds@NP_to_IE',
 'ds@UBEBIT_to_IE',
 'ds@UBEBIT_to_DS',
 'ds@EBIT_to_IE',
 'ds@EBIT_to_DS',
 'ds@UBEBITDA_to_IE',
 'ds@EBITDA_to_IE',
 'ds@FFO_to_IE',
 'ds@NS_to_IE',
 'ds@TL_to_IE',
 'ds@ACF_to_DS',
 'ds@ACF_and_LE_to_DS_and_LE',
 'ds@EBIT_exc_Div_exc_Taxes_to_IE',
 'ds@UBEBIT_and_LE_to_DS_and_LE',
 'ds@UBEBIT_exc_Div_exc_Taxes_to_IE',
 'ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
 'ds@UBEBIT_exc_Div_exc_Taxes_to_DS',
 'ds@EBIT_exc_Div_exc_Taxes_to_DS',
 'ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
 'ds@EBIT_and_LE_to_DS_and_LE',
 'ds@NP_and_IE_to_IE',
 'ds@NP_and_IE_to_TL',
 'liq@ECE_to_TD',
 'liq@ECE_to_TL',
 'liq@ECE_to_AdjTD',
 'liq@ECE_to_TA',
 'liq@ECE_to_CL',
 'liq@ECE_to_CA',
 'liq@CA_to_TL',
 'liq@CA_to_TA',
 'liq@RE_to_CL',
 'liq@CA_exc_TI_to_TD',
 'liq@CA_exc_TI_to_/TL',
 'liq@CA_exc_TI_to_/AdjTD',
 'liq@CA_exc_TI_to_/TA',
 'liq@CA_exc_CL_to_TD',
 'liq@CA_exc_CL_to_TL',
 'liq@CA_exc_CL_to_AdjTD',
 'liq@CA_exc_CL_to_TA',
 'liq@CA_exc_CL_to_CA',
 'liq@CA_exc_CL_to_CL',
 'prof@EBIT_to_AdjCapt',
 'prof@EBIT_to_Capt',
 'prof@EBIT_to_NS',
 'prof@EBIT_to_TangA',
 'prof@EBIT_to_TA',
 'prof@EBITDA_to_AdjCapt',
 'prof@EBITDA_to_Capt',
 'prof@EBITDA_to_NS',
 'prof@EBITDA_to_TangA',
 'prof@EBITDA_to_TA',
 'prof@NOP_to_NP',
 'prof@NOP_to_NS',
 'prof@NOP_to_TangNW',
 'prof@NOP_to_TA',
 'prof@NOP_to_TNW',
 'prof@NOP_to_UBTangNW',
 'prof@RE_to_TA',
 'prof@RE_to_TNW',
 'prof@RE_to_UBTangNW',
 'prof@UBEBIT_to_AdjCapt',
 'prof@UBEBIT_to_Capt',
 'prof@UBEBIT_to_NS',
 'prof@UBEBIT_to_TangA',
 'prof@UBEBIT_to_TA',
 'prof@UBEBITDA_to_AdjCapt',
 'prof@UBEBITDA_to_Capt',
 'prof@UBEBITDA_to_NS',
 'prof@UBEBITDA_to_TangA',
 'prof@UBEBITDA_to_TA',
 'prof@PbT_to_TA',
 'prof@CD_to_NP',
 'prof@NP_exc_EI',
 'prof@EBIT_exc_II_to_Capt',
 'prof@NP_exc_EI_to_TA',
 'size@TangNW_to_TA',
 'size@TangNW_to_TA_exc_CA',
 'size@UBTangNW_to_TA',
 'size@UBTangNW_to_TA_exc_CA',
 'size@TNW_to_TA_exc_CA',
 'size@TNW_to_TA',
 'ds@DSCR']


extra_cols_prod=[ 'Customer Long Name','CUSTOMERID','timestamp','Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating_Uncap', 'def_flag',\
 'qual1', 'qual2', 'qual3', 'qual4',  'Access_Outside_Capital', 'Excp_Underwrite_For_Leverage', 'Info_Rptg_Timely_Manner', \
 'Management_Quality', 'Market_Outlook_Of_Borrower', 'Pct_Revenue_3_Large_Custs','Underwriter_Guideline','L_DATE_OF_DEFAULT', \
 'Audit Method','dataset','NAICS_Cd', 'ExternalRating_PDRR','RLA_Notches','Override_Action']


extra_cols_hist=['CONM','CUSTOMERID','timestamp','Final_PD_Risk_Rating', 'def_flag', 'AUDITMETHOD',\
'NAICS','L_DATE_OF_DEFAULT', 'ExtRating', 'implied_internal_PDRR', 'implied_internal_PD','dataset']


# use current factors to repalce the constructed factors. Only for prod data
dat_prod['prof@Net Profit Margin %'] = dat_prod['quant1']*100
dat_prod['cf@TD_COP'] = dat_prod['cf@quant2']
dat_prod['size@Total Assets'] = dat_prod['quant3']
dat_prod['bs@TL_to_TNW'] = dat_prod['bs@quant4']
dat_prod['liq@ECE_to_TL'] = dat_prod['liq@quant5']




#%% remove guarantor impact and attach other important columns
dat_prod['Gua_override'] =  dat_prod['PD_Risk_Rating_After_Gtee'] - dat_prod['PD_Risk_Rating_After_RLA']
dat_prod = dat_prod.query('Gua_override==0')
dat_prod['RLA_Notches'].fillna(0, inplace=True)
dat_prod['Override_Action'].fillna(0, inplace=True)



#%%
data_prod = dat_prod[factors_prod+extra_cols_prod].copy()
data_hist = dat_hist[factors_hist+extra_cols_hist].copy()
data_combo = pd.concat([data_prod,data_hist], axis=0)

data_prod.reset_index(drop=True, inplace=True)
data_hist.reset_index(drop=True, inplace=True)
data_combo.reset_index(drop=True, inplace=True)


data_prod.to_pickle(r'..\newdata\prod_1000.pkl.xz')
data_hist.to_pickle(r'..\newdata\hist_1000.pkl.xz')
data_combo.to_pickle(r'..\newdata\combo_1000.pkl.xz')


cutoff = 20160101
X_train = data_combo.query('timestamp<{}'.format(cutoff)) 
X_test = data_combo.query('timestamp>={}'.format(cutoff))  # 18.12%
X_train.to_pickle(r'SFA\train_2016.pkl.xz')
X_test.to_pickle(r'SFA\test_2016.pkl.xz')# -*- coding: utf-8 -*-
"""
Created on Mon May 21 15:47:38 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

factors_prod = factors_combo= [
'cf@TD_COP',
'prof@TangA_to_NS',
'cf@FOCF_to_TL',
 'cf@ACF',
 'size@Adjusted Capitalization',
 'size@Adjusted Total Debt',
 'size@Amortization',
 'prof@Average Profit Margin, 2 yrs',
 'size@Capitalization',
 'size@Current Assets',
 'size@Current Liabilities',
 'liq@Current Ratio',
 'ds@INTERESTEXPENSE',
 'bs@CPLTD',
 'ds@Debt Service',
 'cf@Depreciation',
 'prof@DIVIDENDSSTOCK',
 'prof@DividendCommon',
 'prof@DIVIDENDSPREF',
 'prof@Dividends',
 'size@EBIT',
 'size@EBITDA',
 'cf@Ending Cash & Equivalents',
 'prof@AFTERTAXINCOME',
 'ds@AFTERTAXEXPENSE',
 'size@Extraordinary Items',
 'size@Free Operating Cash Flow_Modified',
 'size@Funds from Operations_Modified',
 'ds@Interest Expense',
 'size@Total Inventory',
 'cf@Lease Expense',
 'size@Net Accounts Receivable',
 'size@Net Operating Profit',
 'size@Net Profit',
 'size@Net_Sales',
 'size@Profit before Taxes',
 'liq@Quick Ratio',
 'size@Retained Earnings',
 'prof@Return on Assets',
 'prof@Return on Equity',
 'bs@Senior Debt',
 'size@NETTANGIBLES',
 'size@Tangible Assets',
 'size@Tangible Net Worth',
 'size@Total Assets',
 'size@Total Debt',
 'bs@LONGTERMDEBT',
 'bs@Total LTD',
 'size@Total Liabilities',
 'size@Total Net Worth',
 'liq@Union Bank Current Ratio',
 'size@Union Bank EBIT',
 'size@Union Bank EBITDA',
 'liq@Union Bank Quick Ratio',
 'size@Union Bank Tangible Net Worth',
 'prof@Operating Profit Margin %',
 'prof@Net Profit Margin %',
 'prof@Gross Profit Margin %',
 'size@Free Operating Cash Flow (FOCF)',
 'size@Funds from Operations (FFO)',
 'prof@Interest Income',
 'act@NS_to_CL',
 'act@NS_to_UBTangNW',
 'act@NS_to_TA',
 'act@NS_to_NAR',
 'act@NS_to_Inv',
 'act@NS_to_TNW',
 'bs@TD_to_TA',
 'bs@TD_to_TangNW',
 'bs@TD_to_Capt',
 'bs@TD_to_AdjCapt',
 'bs@TD_to_TNW',
 'bs@TD_to_UBTangNW',
 'bs@SD_to_Capt',
 'bs@SD_to_AdjCapt',
 'bs@TLTD_to_TNW',
 'bs@TLTD_to_TA',
 'bs@TLTD_to_UBTangNW',
 'bs@TLTD_to_AdjCapt',
 'bs@TLTD_to_TangNW',
 'bs@TLTD_to_Capt',
 'bs@TL_to_UBTangNW',
 'bs@TL_to_TangNW',
 'bs@TL_to_TA',
 'bs@TL_to_TNW',
 'bs@TL_to_AdjCapt',
 'bs@TL_to_Capt',
 'bs@CL_to_UBTangNW',
 'bs@CL_to_TangNW',
 'bs@CL_to_TL',
 'bs@CL_to_TNW',
 'bs@CL_to_AdjCapt',
 'bs@CL_to_TA',
 'bs@CL_to_Capt',
 'bs@AdjTD_to_AdjCapt',
 'bs@AdjTD_to_Capt',
 'bs@TLTD_to_TLTD_and_TNW',
 'bs@TLTD_to_TLTD_and_UBTangNW',
 'bs@TD_to_CA_exc_CL',
 'bs@TD_to_TA_exc_TL',
 'bs@TL_to_TL_exc_CL',
 'cf@TD_to_UBEBITDA',
 'cf@TD_to_EBITDA',
 'cf@TD_to_ACF',
 'cf@SD_to_UBEBITDA',
 'cf@SD_to_EBITDA',
 'cf@AdjTD_to_EBITDA',
 'cf@AdjTD_to_UBEBITDA',
 'cf@AdjTD_to_ACF',
 'cf@FOCF_to_TD',
 'cf@FFO_to_TD',
 'cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',
 'cf@AdjTD_to_ACF_and_LE',
 'cf@AdjTD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@TD_to_EBIT_exc_Div_exc_Taxes',
 'cf@TD_to_ACF_and_LE',
 'ds@NP_to_TL',
 'ds@NP_to_CL',
 'ds@NP_to_IE',
 'ds@UBEBIT_to_IE',
 'ds@UBEBIT_to_DS',
 'ds@EBIT_to_IE',
 'ds@EBIT_to_DS',
 'ds@UBEBITDA_to_IE',
 'ds@EBITDA_to_IE',
 'ds@FFO_to_IE',
 'ds@NS_to_IE',
 'ds@TL_to_IE',
 'ds@ACF_to_DS',
 'ds@ACF_and_LE_to_DS_and_LE',
 'ds@EBIT_exc_Div_exc_Taxes_to_IE',
 'ds@UBEBIT_and_LE_to_DS_and_LE',
 'ds@UBEBIT_exc_Div_exc_Taxes_to_IE',
 'ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
 'ds@UBEBIT_exc_Div_exc_Taxes_to_DS',
 'ds@EBIT_exc_Div_exc_Taxes_to_DS',
 'ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
 'ds@EBIT_and_LE_to_DS_and_LE',
 'ds@NP_and_IE_to_IE',
 'ds@NP_and_IE_to_TL',
 'liq@ECE_to_TD',
 'liq@ECE_to_TL',
 'liq@ECE_to_AdjTD',
 'liq@ECE_to_TA',
 'liq@ECE_to_CL',
 'liq@ECE_to_CA',
 'liq@CA_to_TL',
 'liq@CA_to_TA',
 'liq@RE_to_CL',
 'liq@CA_exc_TI_to_TD',
 'liq@CA_exc_TI_to_/TL',
 'liq@CA_exc_TI_to_/AdjTD',
 'liq@CA_exc_TI_to_/TA',
 'liq@CA_exc_CL_to_TD',
 'liq@CA_exc_CL_to_TL',
 'liq@CA_exc_CL_to_AdjTD',
 'liq@CA_exc_CL_to_TA',
 'liq@CA_exc_CL_to_CA',
 'liq@CA_exc_CL_to_CL',
 'prof@EBIT_to_AdjCapt',
 'prof@EBIT_to_Capt',
 'prof@EBIT_to_NS',
 'prof@EBIT_to_TangA',
 'prof@EBIT_to_TA',
 'prof@EBITDA_to_AdjCapt',
 'prof@EBITDA_to_Capt',
 'prof@EBITDA_to_NS',
 'prof@EBITDA_to_TangA',
 'prof@EBITDA_to_TA',
 'prof@NOP_to_NP',
 'prof@NOP_to_NS',
 'prof@NOP_to_TangNW',
 'prof@NOP_to_TA',
 'prof@NOP_to_TNW',
 'prof@NOP_to_UBTangNW',
 'prof@RE_to_TA',
 'prof@RE_to_TNW',
 'prof@RE_to_UBTangNW',
 'prof@UBEBIT_to_AdjCapt',
 'prof@UBEBIT_to_Capt',
 'prof@UBEBIT_to_NS',
 'prof@UBEBIT_to_TangA',
 'prof@UBEBIT_to_TA',
 'prof@UBEBITDA_to_AdjCapt',
 'prof@UBEBITDA_to_Capt',
 'prof@UBEBITDA_to_NS',
 'prof@UBEBITDA_to_TangA',
 'prof@UBEBITDA_to_TA',
 'prof@PbT_to_TA',
 'prof@CD_to_NP',
 'prof@NP_exc_EI',
 'prof@EBIT_exc_II_to_Capt',
 'prof@NP_exc_EI_to_TA',
 'size@TangNW_to_TA',
 'size@TangNW_to_TA_exc_CA',
 'size@UBTangNW_to_TA',
 'size@UBTangNW_to_TA_exc_CA',
 'size@TNW_to_TA_exc_CA',
 'size@TNW_to_TA',
 'cf@quant2',
 'bs@quant4',
 'ds@DSCR']

factors_hist = [
'cf@TD_COP',
'prof@TangA_to_NS',
'cf@FOCF_to_TL',
 'cf@ACF',
 'size@Adjusted Capitalization',
 'size@Adjusted Total Debt',
 'size@Amortization',
 'prof@Average Profit Margin, 2 yrs',
 'size@Capitalization',
 'size@Current Assets',
 'size@Current Liabilities',
 'liq@Current Ratio',
 'ds@INTERESTEXPENSE',
 'bs@CPLTD',
 'ds@Debt Service',
 'cf@Depreciation',
 'prof@DIVIDENDSSTOCK',
 'prof@DividendCommon',
 'prof@DIVIDENDSPREF',
 'prof@Dividends',
 'size@EBIT',
 'size@EBITDA',
 'cf@Ending Cash & Equivalents',
 'prof@AFTERTAXINCOME',
 'ds@AFTERTAXEXPENSE',
 'size@Extraordinary Items',
 'ds@Interest Expense',
 'size@Total Inventory',
 'cf@Lease Expense',
 'size@Net Accounts Receivable',
 'size@Net Operating Profit',
 'size@Net Profit',
 'size@Net_Sales',
 'size@Profit before Taxes',
 'liq@Quick Ratio',
 'size@Retained Earnings',
 'prof@Return on Assets',
 'prof@Return on Equity',
 'bs@Senior Debt',
 'size@Tangible Assets',
 'size@Tangible Net Worth',
 'size@Total Assets',
 'size@Total Debt',
 'bs@LONGTERMDEBT',
 'bs@Total LTD',
 'size@Total Liabilities',
 'size@Total Net Worth',
 'liq@Union Bank Current Ratio',
 'size@Union Bank EBIT',
 'size@Union Bank EBITDA',
 'liq@Union Bank Quick Ratio',
 'size@Union Bank Tangible Net Worth',
 'prof@Operating Profit Margin %',
 'prof@Net Profit Margin %',
 'prof@Gross Profit Margin %',
 'size@Free Operating Cash Flow (FOCF)',
 'size@Funds from Operations (FFO)',
 'prof@Interest Income',
 'act@NS_to_CL',
 'act@NS_to_UBTangNW',
 'act@NS_to_TA',
 'act@NS_to_NAR',
 'act@NS_to_Inv',
 'act@NS_to_TNW',
 'bs@TD_to_TA',
 'bs@TD_to_TangNW',
 'bs@TD_to_Capt',
 'bs@TD_to_AdjCapt',
 'bs@TD_to_TNW',
 'bs@TD_to_UBTangNW',
 'bs@SD_to_Capt',
 'bs@SD_to_AdjCapt',
 'bs@TLTD_to_TNW',
 'bs@TLTD_to_TA',
 'bs@TLTD_to_UBTangNW',
 'bs@TLTD_to_AdjCapt',
 'bs@TLTD_to_TangNW',
 'bs@TLTD_to_Capt',
 'bs@TL_to_UBTangNW',
 'bs@TL_to_TangNW',
 'bs@TL_to_TA',
 'bs@TL_to_TNW',
 'bs@TL_to_AdjCapt',
 'bs@TL_to_Capt',
 'bs@CL_to_UBTangNW',
 'bs@CL_to_TangNW',
 'bs@CL_to_TL',
 'bs@CL_to_TNW',
 'bs@CL_to_AdjCapt',
 'bs@CL_to_TA',
 'bs@CL_to_Capt',
 'bs@AdjTD_to_AdjCapt',
 'bs@AdjTD_to_Capt',
 'bs@TLTD_to_TLTD_and_TNW',
 'bs@TLTD_to_TLTD_and_UBTangNW',
 'bs@TD_to_CA_exc_CL',
 'bs@TD_to_TA_exc_TL',
 'bs@TL_to_TL_exc_CL',
 'cf@TD_to_UBEBITDA',
 'cf@TD_to_EBITDA',
 'cf@TD_to_ACF',
 'cf@SD_to_UBEBITDA',
 'cf@SD_to_EBITDA',
 'cf@AdjTD_to_EBITDA',
 'cf@AdjTD_to_UBEBITDA',
 'cf@AdjTD_to_ACF',
 'cf@FOCF_to_TD',
 'cf@FFO_to_TD',
 'cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',
 'cf@AdjTD_to_ACF_and_LE',
 'cf@AdjTD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@TD_to_EBIT_exc_Div_exc_Taxes',
 'cf@TD_to_ACF_and_LE',
 'ds@NP_to_TL',
 'ds@NP_to_CL',
 'ds@NP_to_IE',
 'ds@UBEBIT_to_IE',
 'ds@UBEBIT_to_DS',
 'ds@EBIT_to_IE',
 'ds@EBIT_to_DS',
 'ds@UBEBITDA_to_IE',
 'ds@EBITDA_to_IE',
 'ds@FFO_to_IE',
 'ds@NS_to_IE',
 'ds@TL_to_IE',
 'ds@ACF_to_DS',
 'ds@ACF_and_LE_to_DS_and_LE',
 'ds@EBIT_exc_Div_exc_Taxes_to_IE',
 'ds@UBEBIT_and_LE_to_DS_and_LE',
 'ds@UBEBIT_exc_Div_exc_Taxes_to_IE',
 'ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
 'ds@UBEBIT_exc_Div_exc_Taxes_to_DS',
 'ds@EBIT_exc_Div_exc_Taxes_to_DS',
 'ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
 'ds@EBIT_and_LE_to_DS_and_LE',
 'ds@NP_and_IE_to_IE',
 'ds@NP_and_IE_to_TL',
 'liq@ECE_to_TD',
 'liq@ECE_to_TL',
 'liq@ECE_to_AdjTD',
 'liq@ECE_to_TA',
 'liq@ECE_to_CL',
 'liq@ECE_to_CA',
 'liq@CA_to_TL',
 'liq@CA_to_TA',
 'liq@RE_to_CL',
 'liq@CA_exc_TI_to_TD',
 'liq@CA_exc_TI_to_/TL',
 'liq@CA_exc_TI_to_/AdjTD',
 'liq@CA_exc_TI_to_/TA',
 'liq@CA_exc_CL_to_TD',
 'liq@CA_exc_CL_to_TL',
 'liq@CA_exc_CL_to_AdjTD',
 'liq@CA_exc_CL_to_TA',
 'liq@CA_exc_CL_to_CA',
 'liq@CA_exc_CL_to_CL',
 'prof@EBIT_to_AdjCapt',
 'prof@EBIT_to_Capt',
 'prof@EBIT_to_NS',
 'prof@EBIT_to_TangA',
 'prof@EBIT_to_TA',
 'prof@EBITDA_to_AdjCapt',
 'prof@EBITDA_to_Capt',
 'prof@EBITDA_to_NS',
 'prof@EBITDA_to_TangA',
 'prof@EBITDA_to_TA',
 'prof@NOP_to_NP',
 'prof@NOP_to_NS',
 'prof@NOP_to_TangNW',
 'prof@NOP_to_TA',
 'prof@NOP_to_TNW',
 'prof@NOP_to_UBTangNW',
 'prof@RE_to_TA',
 'prof@RE_to_TNW',
 'prof@RE_to_UBTangNW',
 'prof@UBEBIT_to_AdjCapt',
 'prof@UBEBIT_to_Capt',
 'prof@UBEBIT_to_NS',
 'prof@UBEBIT_to_TangA',
 'prof@UBEBIT_to_TA',
 'prof@UBEBITDA_to_AdjCapt',
 'prof@UBEBITDA_to_Capt',
 'prof@UBEBITDA_to_NS',
 'prof@UBEBITDA_to_TangA',
 'prof@UBEBITDA_to_TA',
 'prof@PbT_to_TA',
 'prof@CD_to_NP',
 'prof@NP_exc_EI',
 'prof@EBIT_exc_II_to_Capt',
 'prof@NP_exc_EI_to_TA',
 'size@TangNW_to_TA',
 'size@TangNW_to_TA_exc_CA',
 'size@UBTangNW_to_TA',
 'size@UBTangNW_to_TA_exc_CA',
 'size@TNW_to_TA_exc_CA',
 'size@TNW_to_TA',
 'ds@DSCR']


data_combo = pd.read_pickle(r'SFA\train_2016.pkl.xz')





#%% for historical data
writer = pd.ExcelWriter(r'SFA\LC_SFA_SomersD.xlsx')
pl_data = [data_combo]
pl_target = ['Final_PD_Risk_Rating']

pl_somersd=[]

for i, dat in enumerate(pl_data):  
    pl_sd = []
    for factor in factors_combo:
        df = dat[[factor]+[pl_target[i]]].copy()
        df.dropna(how='any', inplace=True)
        df[factor] = df[factor].clip(np.nanmin(df[factor][df[factor] != -np.inf]), np.nanmax(df[factor][df[factor] != np.inf]))
        pl_sd.append(np.abs(SomersD(df[pl_target[i]], df[factor])))
    pl_somersd.append(pl_sd)
    

df_somersd = pd.DataFrame()
df_somersd['Final_PDRR'] = pl_somersd[0]
df_somersd.index = factors_combo


df_somersd.to_excel(writer, 'combo')

writer.save()



#%%

# -*- coding: utf-8 -*-
"""
Created on Mon May 21 15:47:38 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
import math, re
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

pl_catname = ['bs','cf','ds','liq','act','size','prof']

writer_long = pd.ExcelWriter(r'SFA\LC_SFA_longlist.xlsx')
writer_short = pd.ExcelWriter(r'SFA\LC_SFA_shortlist.xlsx')



#%% for combo data
# auto build list for each category 
df_somersd = pd.read_excel(r'SFA\LC_SFA_SomersD.xlsx', sheetname='combo')
cols = df_somersd.index.tolist()
for cat in pl_catname:
    exec('{}=[]'.format(cat))
    for name in cols:
        if re.search( '^{}'.format(cat), name):
            exec('{}.append(name)'.format(cat))
# we want about 80 factors as our long list factors
rate = 80/len(bs+cf+ds+liq+act+size+prof)


# get long(about 80) and short (about 20) list

py_sdname = df_somersd.columns.tolist()
pl_cat = [bs,cf,ds,liq,act,size,prof]
df_longlist=pd.DataFrame()
df_shortlist=pd.DataFrame()

for i in range(len(py_sdname)):
    pl_cat_long=[]; pl_cat_short=[]  
    for cat in pl_cat:
        n_ = round(rate*len(cat))
        temp = df_somersd.loc[cat,:]
        temp.sort_values(by=py_sdname[i], ascending=False, inplace=True)
        temp = temp.iloc[:n_,:].index.tolist()
        pl_cat_long.append(temp)
        pl_cat_short.append(temp[:(max(math.ceil(n_*0.25),2))])

    df_longlist[py_sdname[i]] = pl_cat_long
    df_shortlist[py_sdname[i]] = pl_cat_short

df_longlist.to_excel(writer_long, 'combo')
df_shortlist.to_excel(writer_short, 'combo')



#%%
writer_long.save()
writer_short.save()

# -*- coding: utf-8 -*-
"""
Created on Tue May 22 15:17:42 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD, buildpseudodef
from sklearn.ensemble.partial_dependence import plot_partial_dependence
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier 
import matplotlib.pyplot as plt


os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
cutoff = 500
filename_inputdata = r'..\newdata\dat_lc_by{cut}_last.pkl.xz'.format(cut=cutoff)
data = pd.read_pickle(filename_inputdata)

df_shortlist = pd.read_excel(r'SFA\SFA_shortlist_lc_by{cut}_last.xlsx'.format(cut=cutoff))
factors_in_shortlist=[]
for cat in df_shortlist['TrueDef'].iteritems():
    exec('factors_in_shortlist+='+cat[1])
num_shortlist = len(factors_in_shortlist)


df_longlist = pd.read_excel(r'SFA\SFA_longlist_lc_by{cut}_last.xlsx'.format(cut=cutoff))
pl_dataname = ['TrueDef','PseudoDef_15','PseudoDef_14-15','PseudoDef_13-15','Final_PDRR']
pl_colname = ['def_flag','def_flag','def_flag','def_flag','Final_PD_Risk_Rating']
pl_data = [data, buildpseudodef(data, def_flag='def_flag', PDRR='Final_PD_Risk_Rating', pseudodef_PDRR=[15]),
    buildpseudodef(data, def_flag='def_flag', PDRR='Final_PD_Risk_Rating', pseudodef_PDRR=[14,15]),
    buildpseudodef(data, def_flag='def_flag', PDRR='Final_PD_Risk_Rating', pseudodef_PDRR=[13,14,15]),
    data]

#%%
df_importance = pd.DataFrame()

for i,dat in enumerate(pl_data):
	temp_a=df_longlist[pl_dataname[i]]
	factors_in_longlist=[]
	for cat in temp_a.iteritems():
		exec('factors_in_longlist+='+cat[1])
	num_cand = len(factors_in_longlist)
	dat = dat[factors_in_longlist+[pl_colname[i]]]
	X_train_raw = dat.iloc[:,:num_cand]
	df_max = X_train_raw.apply(lambda x: np.nanmax(x[x != np.inf]))
	df_min = X_train_raw.apply(lambda x: np.nanmin(x[x != -np.inf]))
	X_train_raw = X_train_raw.clip(df_min,df_max, axis=1)
	X_train_raw = X_train_raw.fillna(X_train_raw.median())
	X_train = X_train_raw.transform(lambda x: 50*(x - x.mean()) / x.std())

	y_train = dat.iloc[:,num_cand]

	feature_importance =np.zeros(num_cand)
	for j in range(2000):
		clf = RandomForestClassifier(n_estimators=100, random_state=j).fit(X_train, y_train)
		feature_importance += clf.feature_importances_

	feature_importance = 100.0 * (feature_importance / feature_importance.max())
	df_importance[pl_dataname[i]] = feature_importance
	sorted_idx = np.argsort(feature_importance)
	sorted_idx = sorted_idx[-(num_shortlist):]
	pos = np.arange(sorted_idx.shape[0]) + .5
	plt.figure()
	plt.barh(pos, feature_importance[sorted_idx], align='center')
	plt.yticks(pos, X_train.columns[sorted_idx].tolist())
	plt.xlabel('Relative Importance')
	plt.title('Variable Importance')
	plt.savefig('importance_'+pl_dataname[i]+'_.png')


df_importance.index = factors_in_longlist

df_importance.to_pickle('importance.pickle')


# -*- coding: utf-8 -*-
"""
Created on Tue May 22 15:17:42 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
import pprint
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD



cutoff = 500
filename_inputdata = r'..\newdata\dat_lc_by{cut}_last.pkl.xz'.format(cut=cutoff)
data = pd.read_pickle(filename_inputdata)

rf_shortlist = pd.read_pickle(r'SFA\importance.pickle')
sfa_shortlist = pd.read_excel(r'SFA\SFA_shortlist_lc_by{cut}_last.xlsx'.format(cut=cutoff))
pl_dataname = ['TrueDef','PseudoDef_15','PseudoDef_14-15','PseudoDef_13-15','Final_PDRR']

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))



#%%
pyd_overlap={}
for dataname in pl_dataname:
	factors_in_sfa_shortlist=[]
	for cat in sfa_shortlist[dataname].iteritems():
	    exec('factors_in_sfa_shortlist+='+cat[1])
	num_shortlist = len(factors_in_sfa_shortlist)
	
	temp = rf_shortlist.sort_values(by=dataname, ascending=False)
	temp = temp.head(num_shortlist)
	factors_in_rf_shortlist = temp.index.tolist()
	
	pyd_overlap.update({dataname:intersection(factors_in_sfa_shortlist, factors_in_rf_shortlist)})


pp = pprint.PrettyPrinter(indent=4)
pp.pprint(pyd_overlap)



#%%
pl_sl_manual = [
'size@Net Profit',
'size@Profit before Taxes',
'size@EBIT',
'size@Total Net Worth',
'size@Union Bank EBIT',
'prof@NP_exc_EI',
'prof@Net Profit Margin %',
'prof@EBIT_to_NS',
'prof@PbT_to_TA',
'prof@NP_exc_EI_to_TA',
'liq@ECE_to_TL',
'liq@ECE_to_AdjTD',
'liq@RE_to_CL',
'ds@NP_to_TL',
'ds@EBIT_to_IE',
'ds@EBITDA_to_IE',
'ds@NP_and_IE_to_IE',
'ds@NP_to_IE',
'bs@TL_to_TA',
'bs@TD_to_Capt',
'bs@AdjTD_to_AdjCapt',
'bs@SD_to_Capt',
'bs@TD_to_AdjCapt',
'cf@TD_to_UBEBITDA',
'cf@SD_to_UBEBITDA',
'cf@AdjTD_to_UBEBITDA',]




temp = rf_shortlist.sort_values(by='Final_PDRR', ascending=False)
temp = temp.head(40)
factors_in_rf_shortlist = temp.index.tolist()

intersection(pl_sl_manual, factors_in_rf_shortlist)



#%%
import statsmodels.api as sm
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
MS_dict = dict(zip(MS['PDRR'],MS['new_mid']))

factors = [
'prof@Net Profit Margin %',
'liq@ECE_to_TL',
'ds@NP_to_TL',
'bs@TL_to_TA',
'cf@AdjTD_to_UBEBITDA',
]
dat = data[factors+['Final_PD_Risk_Rating']]
dat['Final_PD'] = dat['Final_PD_Risk_Rating'].transform(lambda x: np.nan if pd.isnull(x) else MS_dict[x]).tolist()
# convert PD to logit PD
dat['logitPD_frPDRR'] = [np.log(x/(1-x)) for x in dat['Final_PD'].tolist()]
dat.dropna(inplace=True)

for factor in factors:
	dat[factor] = np.clip(dat[factor], np.percentile(dat[factor],5), np.percentile(dat[factor],95))


#dat.describe(percentiles=[0.02,0.05,0.95,0.97,0.99])


dat[factors] = dat[factors].transform(lambda x: (x - x.mean()) / x.std())
dat['intercept'] = 1

X=dat[['intercept']+factors]
y=dat['logitPD_frPDRR']
# Note the difference in argument order


SomersD(y, X[factors[1]])

model = sm.OLS(y, X).fit()
predictions = model.predict(X) # make the predictions by the model

# Print out the statistics
model.summary()



SomersD(y, predictions)

predic = np.round(predictions)
np.sum(np.square(y-predic))


# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 13:52:02 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
import pyupset as pyu
import seaborn as sns
import matplotlib.pyplot as plt
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
dat_combo = pd.read_pickle(r'..\newdata\combo.pkl.xz')


#%% for shortlist, Final PDRR
pl_dataname = ['prod', 'hist', 'combo']
pd_dataset={}
for name in pl_dataname:
    dat = pd.read_excel(r'SFA\LC_SFA_shortlist.xlsx', sheetname=name)
    pl_fac=[]
    for row in dat.iterrows():
       exec('pl_fac+={}'.format(row[1].Final_PDRR))
    temp = pd.DataFrame()
    temp['factors'] = pl_fac
    pd_dataset.update({name:temp})


pyu.plot(pd_dataset, query = [('prod', 'hist'),('prod', 'hist','combo')])
pyu.plot(pd_dataset, query = [('combo',),('combo', 'prod'), ('combo', 'hist'),('prod', 'hist','combo')])


#%%
prod = set(pd_dataset['prod']['factors'].tolist())
hist = set(pd_dataset['hist']['factors'].tolist())
combo = set(pd_dataset['combo']['factors'].tolist())

pl_both = list(prod & hist)
pl_hist = list(hist-prod-combo)
pl_prod = list(prod-combo-hist)
pl_all = list(prod & hist & combo)

#%% only in prod:
clip=[0.05,0.95]
fig,ax=plt.subplots(2,3,figsize=(12,8))
for i,factor in enumerate(pl_prod):
    dat_plot = dat_combo[[factor,'dataset']]
    floor, cap = dat_plot[factor].quantile(clip)
    dat_plot = dat_plot[(dat_plot[factor]>floor) & (dat_plot[factor]<cap)] 
    
    sns.distplot(dat_plot.query('dataset=="production"')[factor], hist=False, kde=True, ax=ax[int(i/3),(i%3)], \
        kde_kws = {'shade': True, 'color': 'r', 'lw': 2, 'label' : 'prod'})
    sns.distplot(dat_plot.query('dataset=="historical"')[factor], hist=False, kde=True, ax=ax[int(i/3),(i%3)], \
        kde_kws = {'shade': True, 'color': 'g', 'lw': 2, 'label' : 'hist'})
fig.savefig('only_in_prod.png')


#%% only in hist:
fig,ax=plt.subplots(3,4,figsize=(16,12))
for i,factor in enumerate(pl_hist):
    dat_plot = dat_combo[[factor,'dataset']]
    floor, cap = dat_plot[factor].quantile(clip)
    dat_plot = dat_plot[(dat_plot[factor]>floor) & (dat_plot[factor]<cap)] 
    
    sns.distplot(dat_plot.query('dataset=="production"')[factor], hist=False, kde=True, ax=ax[int(i/4),(i%4)], \
        kde_kws = {'shade': True, 'color': 'r', 'lw': 2, 'label' : 'prod'})
    sns.distplot(dat_plot.query('dataset=="historical"')[factor], hist=False, kde=True, ax=ax[int(i/4),(i%4)], \
        kde_kws = {'shade': True, 'color': 'g', 'lw': 2, 'label' : 'hist'})
fig.savefig('only_in_hist.png')



#%% only in prod:
clip=[0.05,0.95]
fig,ax=plt.subplots(2,5,figsize=(20,8))
for i,factor in enumerate(pl_both):
    dat_plot = dat_combo[[factor,'dataset']]
    floor, cap = dat_plot[factor].quantile(clip)
    dat_plot = dat_plot[(dat_plot[factor]>floor) & (dat_plot[factor]<cap)] 
    
    sns.distplot(dat_plot.query('dataset=="production"')[factor], hist=False, kde=True, ax=ax[int(i/5),(i%5)], \
        kde_kws = {'shade': True, 'color': 'r', 'lw': 2, 'label' : 'prod'})
    sns.distplot(dat_plot.query('dataset=="historical"')[factor], hist=False, kde=True, ax=ax[int(i/5),(i%5)], \
        kde_kws = {'shade': True, 'color': 'g', 'lw': 2, 'label' : 'hist'})
fig.savefig('only_in_both.png')
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 19 13:52:02 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
import seaborn as sns
import matplotlib.pyplot as plt
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
dat_combo = pd.read_pickle(r'..\newdata\combo_1000.pkl.xz')


# for shortlist, Final PDRR
shortlist=['bs@TD_to_Capt', 'bs@TD_to_TA', 'bs@AdjTD_to_AdjCapt', 'bs@SD_to_Capt',
'cf@Ending Cash & Equivalents', 'cf@quant2', 'cf@ACF',
'ds@EBIT_to_IE', 'ds@EBITDA_to_IE', 'ds@NP_and_IE_to_IE',
'liq@ECE_to_TL', 'liq@RE_to_CL', 'liq@ECE_to_TD',
'act@NS_to_TNW', 'act@NS_to_TA',
'size@Profit before Taxes', 'size@Net Profit', 'size@Retained Earnings', 'size@EBIT',
'prof@NP_exc_EI', 'prof@Net Profit Margin %', 'prof@EBIT_to_NS', 'prof@RE_to_TA', 'prof@Return on Assets']

dat_raw = dat_combo[shortlist+['Final_PD_Risk_Rating',]].copy()
for factor in shortlist:
    dat_raw[factor] = dat_raw[factor].clip(np.nanmin(dat_raw[factor][dat_raw[factor] != -np.inf]), np.nanmax(dat_raw[factor][dat_raw[factor] != np.inf]))


#%%
dat_s1 = dat_s2 = dat_raw.copy()

for factor in shortlist:
    floor, cap = dat_s1[factor].quantile([0.01,0.99])
    dat_s1[factor] = np.clip(dat_s1[factor], floor, cap)   
    
    floor, cap = dat_s2[factor].quantile([0.05,0.95])
    dat_s2[factor] = np.clip(dat_s2[factor], floor, cap)


pl_sd_raw=[];   pl_sd_s1=[];   pl_sd_s2=[]

for factor in shortlist:
    pl_sd_raw.append(SomersD(dat_raw['Final_PD_Risk_Rating'], dat_raw[factor]))
    pl_sd_s1.append(SomersD(dat_s1['Final_PD_Risk_Rating'], dat_s1[factor]))
    pl_sd_s2.append(SomersD(dat_s2['Final_PD_Risk_Rating'], dat_s2[factor]))


df=pd.DataFrame()

df['raw'] = pl_sd_raw
df['f1c99'] = pl_sd_s1
df['f5c95'] = pl_sd_s2
df.set_index = shortlist# -*- coding: utf-8 -*-
"""
Created on Mon May  7 16:54:48 2018

@author: ub71894 (4e8e6d0b), CSG
"""
 
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split

dat = pd.read_pickle(r'..\newdata\combo_1000.pkl.xz')
finallist=[
'prof@EBITDA_to_NS', 'prof@RE_to_TA', 
'cf@TD_to_UBEBITDA','cf@TD_to_EBITDA',
'size@Net_Sales','size@Total Assets','size@Profit before Taxes', 'size@Net Profit', 
'bs@TD_to_Capt', 'bs@TD_to_TA', 
'liq@ECE_to_TL','liq@RE_to_CL', 
'ds@EBIT_to_IE','ds@EBITDA_to_IE']
#%% 
# random split
X_train, X_test = train_test_split(dat, test_size=0.20, random_state=0)
X_train.to_pickle(r'MFA\train_random.pkl.xz')
X_test.to_pickle(r'MFA\test_random.pkl.xz')

# by time window
cutoff = 20160101
X_train = dat.query('timestamp<{}'.format(cutoff)) 
X_test = dat.query('timestamp>={}'.format(cutoff))  # 18.12%
X_train.to_pickle(r'MFA\train_2016.pkl.xz')
X_test.to_pickle(r'MFA\test_2016.pkl.xz')


cutoff = 20170101
X_train = dat.query('timestamp<{}'.format(cutoff)) 
X_test = dat.query('timestamp>={}'.format(cutoff))  # 7.7%
X_train.to_pickle(r'MFA\train_2017.pkl.xz')
X_test.to_pickle(r'MFA\test_2017.pkl.xz')

# time window by masterscale
cutoff = 20160501
X_train = dat.query('timestamp<{}'.format(cutoff)) 
X_test = dat.query('timestamp>={}'.format(cutoff))  # 7.7%
X_train.to_pickle(r'MFA\train_oldms.pkl.xz')
X_test.to_pickle(r'MFA\test_newms.pkl.xz')


#%% plot  

X_train['sample'] = 'train'
X_test['sample'] = 'test'
dat_combo = pd.concat([X_train,X_test])

#%% only in prod:
clip=[0.05,0.95]
fig,ax=plt.subplots(3,5,figsize=(15,12))
for i,factor in enumerate(finallist):
    dat_plot = dat_combo[[factor,'sample']]
    floor, cap = dat_plot[factor].quantile(clip)
    dat_plot = dat_plot[(dat_plot[factor]>floor) & (dat_plot[factor]<cap)] 
    
    sns.distplot(dat_plot.query('sample=="train"')[factor], hist=False, kde=True, ax=ax[int(i/5),(i%5)], \
        kde_kws = {'shade': True, 'color': 'r', 'lw': 2, 'label' : 'train'})
    sns.distplot(dat_plot.query('sample=="test"')[factor], hist=False, kde=True, ax=ax[int(i/5),(i%5)], \
        kde_kws = {'shade': True, 'color': 'g', 'lw': 2, 'label' : 'test'})

fig.savefig(r'MFA\2017.png')


#%%

cov = X_train[finallist].corr()



#%%
# -*- coding: utf-8 -*-
"""
Created on Mon May  7 16:54:48 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm

postfix = "2016"

X_train = pd.read_pickle(r'MFA\train_{}.pkl.xz'.format(postfix))
X_test = pd.read_pickle(r'MFA\test_{}.pkl.xz'.format(postfix))
 


quant_factor = ['Net_Profit_Margin','Total_Debt_By_COP','Total_Assets','Total_Liab_by_Tang_Net_Worth','End_Cash_Equiv_By_Tot_Liab']
quali_factor = ['Strength_SOR_Prevent_Default','Level_Waiver_Covenant_Mod','Mgmt_Resp_Adverse_Conditions','Vulnerability_To_Changes']
PDInfo_file = r'C:\Users\ub71894\Documents\DevRepo\Files\PDModelParameters.xlsx'
masterscale_file = r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx'
model_name = 'C&I'; version = 1.2
model = PDModel(PDInfo_file, model_name, version, quant_factor, quali_factor, masterscale_file)


model.reset()


#%% 
cols_negsource = ['size@EBIT', 'size@EBITDA','size@Union Bank EBIT','size@Union Bank EBITDA','size@Retained Earnings','size@Capitalization',\
'ds@Interest Expense']
#a=X_train[cols_negsource].describe(percentiles=[0.01,0.02,0.05,0.1])


invalid_mapping = {
'prof@EBITDA_to_NS':0,
'prof@RE_to_TA':0,
'cf@TD_to_UBEBITDA':  'size@Union Bank EBITDA',
'cf@TD_to_EBITDA':  'size@EBITDA',
'size@Net_Sales': 0,
'size@Total Assets':0,
'size@Profit before Taxes':0,
'size@Net Profit':0,
'bs@TD_to_Capt':'size@Capitalization',
'bs@TD_to_TA':0,
'liq@ECE_to_TL':0,
'liq@RE_to_CL':0,
'ds@EBIT_to_IE':'ds@Interest Expense',
'ds@EBITDA_to_IE':'ds@Interest Expense'
}


finallist=[
'prof@EBITDA_to_NS', 'prof@RE_to_TA', 
'cf@TD_to_UBEBITDA','cf@TD_to_EBITDA',
'size@Net_Sales','size@Total Assets','size@Profit before Taxes', 'size@Net Profit', 
'bs@TD_to_Capt', 'bs@TD_to_TA', 
'liq@ECE_to_TL','liq@RE_to_CL', 
'ds@EBIT_to_IE','ds@EBITDA_to_IE']


data_train = X_train[finallist+cols_negsource+['Final_PD_Risk_Rating']]
data_train.dropna(subset=finallist+cols_negsource, how='any', inplace=True)
data_train.reset_index(drop=True, inplace=True)
data_train['size@Net_Sales'] = np.log(1+data_train['size@Net_Sales'])
data_train['size@Total Assets'] = np.log(1+data_train['size@Total Assets'])

data_test = X_test[finallist+cols_negsource+['Final_PD_Risk_Rating']]
data_test.dropna(subset=finallist+cols_negsource, how='any', inplace=True)
data_test.reset_index(drop=True, inplace=True)
data_test['size@Net_Sales'] = np.log(1+data_test['size@Net_Sales'])
data_test['size@Total Assets'] = np.log(1+data_test['size@Total Assets'])

#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_train[factor] = data_train[factor].clip(np.nanmin(data_train[factor][data_train[factor] != -np.inf]), np.nanmax(data_train[factor][data_train[factor] != np.inf]))
#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_test[factor] = data_test[factor].clip(np.nanmin(data_test[factor][data_test[factor] != -np.inf]), np.nanmax(data_test[factor][data_test[factor] != np.inf]))

#a=data_train[finallist].describe(percentiles=[0.01,0.05,0.1,0.9,0.95,0.99])
#a=data_test[finallist].describe(percentiles=[0.01,0.05,0.1,0.9,0.95,0.99])
# construct model based on train data:
sfa = []
for factor in finallist:
    sfa.append(SomersD(data_train.Final_PD_Risk_Rating, data_train[factor]))

model.update({'quant_factor':finallist})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*14})
model.update({'Invalid_Neg': [0]*14})
model.update(quanttrans(data_train, model, floor=0.05, cap=0.95))
# use floor=0 for factor 'ds@EBIT_to_IE'
model.floor[-2]=0
pl_invalid = []
for fac in finallist:
    pl_invalid.append(invalid_mapping[fac])
model.Invalid_Neg = pl_invalid


data_train = PD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_train = logitPD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_test = PD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
data_test = logitPD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
#normdata_train = normalization(data_train, model, quant_only=True)

cni_train = MFA(data_train, model, quant_only=True)
cni_test = MFA(data_test, model, quant_only=True)




#%%
normdat_train = cni_train.normdata.copy()
normdat_test = cni_test.normdata.copy()

prof=['prof@EBITDA_to_NS',  'prof@RE_to_TA',] 
cf =['cf@TD_to_UBEBITDA','cf@TD_to_EBITDA',]
size =['size@Net_Sales','size@Total Assets','size@Profit before Taxes', 'size@Net Profit', ]
bs  = ['bs@TD_to_Capt', 'bs@TD_to_TA', ]
liq = ['liq@ECE_to_TL','liq@RE_to_CL', ] 
ds = ['ds@EBIT_to_IE','ds@EBITDA_to_IE']
'''
prof=['prof@EBITDA_to_NS']
cf =['cf@TD_to_EBITDA',]
size =['size@Net_Sales','size@Total Assets',]
bs  = ['bs@TD_to_Capt', ]
liq = ['liq@ECE_to_TL',]
ds = ['ds@EBITDA_to_IE',]
'''

sl_name = ['prof','cf','size','bs','liq','ds']
#sl_name = ['prof','cf','size','bs','ds']
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(sl_name, 6):
    exec('py_list = product({},{},{},{},{},{})'.format(cats[0],cats[1],cats[2],cats[3],cats[4],cats[5]))
    #exec('py_list = product({},{},{},{},{})'.format(cats[0],cats[1],cats[2],cats[3],cats[4]))
    for facs in py_list:
        names = list(facs)
        x_train = sm.add_constant(normdat_train[names], prepend = True)
        x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())
        if 'liq@ECE_to_TL' in names:
            pl_liq_wt.append(result.params.loc['liq@ECE_to_TL']/result.params.iloc[1:].sum())
        else:
            pl_liq_wt.append(0)
        if (np.sign(result.params[1:]).sum()==6):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(normdat_train['logitPD_frPDRR'], result.fittedvalues))
        pl_SD_out.append(SomersD(normdat_test['logitPD_frPDRR'], result.predict(x_test)))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac['pl_liq_wt'] = pl_liq_wt
models_5fac.to_excel(r'MFA\6models_{}.xlsx'.format(postfix))

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:25:09 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm
import seaborn as sns

X_train = pd.read_pickle(r'MFA\train_2016.pkl.xz')
X_test = pd.read_pickle(r'MFA\test_2016.pkl.xz')

quant_factor = ['Net_Profit_Margin','Total_Debt_By_COP','Total_Assets','Total_Liab_by_Tang_Net_Worth','End_Cash_Equiv_By_Tot_Liab']
quali_factor = ['Strength_SOR_Prevent_Default','Level_Waiver_Covenant_Mod','Mgmt_Resp_Adverse_Conditions','Vulnerability_To_Changes']
PDInfo_file = r'C:\Users\ub71894\Documents\DevRepo\Files\PDModelParameters.xlsx'
masterscale_file = r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx'
model_name = 'C&I'; version = 1.2
model = PDModel(PDInfo_file, model_name, version, quant_factor, quali_factor, masterscale_file)
model.reset()


def modelSD(data, pl_factors, pl_wt, dependentvar):
    est = (data[pl_factors]*pl_wt).sum(axis=1)
    return(SomersD(data[dependentvar], est))

#%% 
cols_negsource = ['size@EBIT', 'size@EBITDA','size@Union Bank EBIT','size@Union Bank EBITDA','size@Retained Earnings','size@Capitalization',\
'ds@Interest Expense']
#a=X_train[cols_negsource].describe(percentiles=[0.01,0.02,0.05,0.1])


invalid_mapping = {
'prof@EBITDA_to_NS':0,
'prof@RE_to_TA':0,
'cf@TD_to_UBEBITDA':  'size@Union Bank EBITDA',
'cf@TD_to_EBITDA':  'size@EBITDA',
'size@Net_Sales': 0,
'size@Total Assets':0,
'size@Profit before Taxes':0,
'size@Net Profit':0,
'bs@TD_to_Capt':'size@Capitalization',
'bs@TD_to_TA':0,
'liq@ECE_to_TL':0,
'liq@RE_to_CL':0,
'ds@EBIT_to_IE':'ds@Interest Expense',
'ds@EBITDA_to_IE':'ds@Interest Expense'
}


finallist=[
'prof@EBITDA_to_NS', 'prof@RE_to_TA', 
'cf@TD_to_UBEBITDA','cf@TD_to_EBITDA',
'size@Net_Sales','size@Total Assets','size@Profit before Taxes', 'size@Net Profit', 
'bs@TD_to_Capt', 'bs@TD_to_TA', 
'liq@ECE_to_TL','liq@RE_to_CL', 
'ds@EBIT_to_IE','ds@EBITDA_to_IE']


data_train = X_train[finallist+cols_negsource+['Final_PD_Risk_Rating']]
data_train.dropna(subset=finallist+cols_negsource, how='any', inplace=True)
data_train.reset_index(drop=True, inplace=True)
data_train['size@Net_Sales'] = np.log(1+data_train['size@Net_Sales'])
data_train['size@Total Assets'] = np.log(1+data_train['size@Total Assets'])

data_test = X_test[finallist+cols_negsource+['Final_PD_Risk_Rating']]
data_test.dropna(subset=finallist+cols_negsource, how='any', inplace=True)
data_test.reset_index(drop=True, inplace=True)
data_test['size@Net_Sales'] = np.log(1+data_test['size@Net_Sales'])
data_test['size@Total Assets'] = np.log(1+data_test['size@Total Assets'])

#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_train[factor] = data_train[factor].clip(np.nanmin(data_train[factor][data_train[factor] != -np.inf]), np.nanmax(data_train[factor][data_train[factor] != np.inf]))
#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_test[factor] = data_test[factor].clip(np.nanmin(data_test[factor][data_test[factor] != -np.inf]), np.nanmax(data_test[factor][data_test[factor] != np.inf]))

#a=data_train[finallist].describe(percentiles=[0.01,0.05,0.1,0.9,0.95,0.99])
#a=data_test[finallist].describe(percentiles=[0.01,0.05,0.1,0.9,0.95,0.99])
# construct model based on train data:
sfa = []
for factor in finallist:
    sfa.append(SomersD(data_train.Final_PD_Risk_Rating, data_train[factor]))

model.update({'quant_factor':finallist})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*14})
model.update({'Invalid_Neg': [0]*14})
model.update(quanttrans(data_train, model, floor=0.05, cap=0.95))
# use floor=0 for factor 'ds@EBIT_to_IE'
model.floor[-2]=0
pl_invalid = []
for fac in finallist:
    pl_invalid.append(invalid_mapping[fac])
model.Invalid_Neg = pl_invalid


data_train = PD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_train = logitPD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_test = PD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
data_test = logitPD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
#normdata_train = normalization(data_train, model, quant_only=True)

cni_train = MFA(data_train, model, quant_only=True)
cni_test = MFA(data_test, model, quant_only=True)

normdat_train = cni_train.normdata.copy()
normdat_test = cni_test.normdata.copy()


#%%
order = 2
for name in finallist:
    
    data_plot = normdat_train.copy()
    data_plot=data_plot.groupby(by='logitPD_frPDRR').mean()
    data_plot.reset_index(drop=False, inplace=True)
    g = sns.lmplot(x=name, y="logitPD_frPDRR", data=data_plot, order=order, ci=None, scatter_kws={"s": 20})
    g.savefig(r'MFA\{name}_logitPDplot_order_{order}.png'.format(name=name, order=order))


# conclusion : no more transformation neeeed. pretty clear linear relationship .
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 14:59:10 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm
from sklearn.preprocessing import PolynomialFeatures

postfix = "2016"

X_train = pd.read_pickle(r'MFA\train_{}.pkl.xz'.format(postfix))
X_test = pd.read_pickle(r'MFA\test_{}.pkl.xz'.format(postfix))
 


quant_factor = ['Net_Profit_Margin','Total_Debt_By_COP','Total_Assets','Total_Liab_by_Tang_Net_Worth','End_Cash_Equiv_By_Tot_Liab']
quali_factor = ['Strength_SOR_Prevent_Default','Level_Waiver_Covenant_Mod','Mgmt_Resp_Adverse_Conditions','Vulnerability_To_Changes']
PDInfo_file = r'C:\Users\ub71894\Documents\DevRepo\Files\PDModelParameters.xlsx'
masterscale_file = r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx'
model_name = 'C&I'; version = 1.2
model = PDModel(PDInfo_file, model_name, version, quant_factor, quali_factor, masterscale_file)


model.reset()


#%% 
cols_negsource = ['size@EBIT', 'size@EBITDA','size@Union Bank EBIT','size@Union Bank EBITDA','size@Retained Earnings','size@Capitalization',\
'ds@Interest Expense']
#a=X_train[cols_negsource].describe(percentiles=[0.01,0.02,0.05,0.1])


invalid_mapping = {
'prof@EBITDA_to_NS':0,
'prof@RE_to_TA':0,
'cf@TD_to_UBEBITDA':  'size@Union Bank EBITDA',
'cf@TD_to_EBITDA':  'size@EBITDA',
'size@Net_Sales': 0,
'size@Total Assets':0,
'size@Profit before Taxes':0,
'size@Net Profit':0,
'bs@TD_to_Capt':'size@Capitalization',
'bs@TD_to_TA':0,
'liq@ECE_to_TL':0,
'liq@RE_to_CL':0,
'ds@EBIT_to_IE':'ds@Interest Expense',
'ds@EBITDA_to_IE':'ds@Interest Expense'
}


finallist=[
'prof@EBITDA_to_NS', 'prof@RE_to_TA', 
'cf@TD_to_UBEBITDA','cf@TD_to_EBITDA',
'size@Net_Sales','size@Total Assets','size@Profit before Taxes', 'size@Net Profit', 
'bs@TD_to_Capt', 'bs@TD_to_TA', 
'liq@ECE_to_TL','liq@RE_to_CL', 
'ds@EBIT_to_IE','ds@EBITDA_to_IE']


data_train = X_train[finallist+cols_negsource+['Final_PD_Risk_Rating']]
data_train.dropna(subset=finallist+cols_negsource, how='any', inplace=True)
data_train.reset_index(drop=True, inplace=True)
data_train['size@Net_Sales'] = np.log(1+data_train['size@Net_Sales'])
data_train['size@Total Assets'] = np.log(1+data_train['size@Total Assets'])

data_test = X_test[finallist+cols_negsource+['Final_PD_Risk_Rating']]
data_test.dropna(subset=finallist+cols_negsource, how='any', inplace=True)
data_test.reset_index(drop=True, inplace=True)
data_test['size@Net_Sales'] = np.log(1+data_test['size@Net_Sales'])
data_test['size@Total Assets'] = np.log(1+data_test['size@Total Assets'])

#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_train[factor] = data_train[factor].clip(np.nanmin(data_train[factor][data_train[factor] != -np.inf]), np.nanmax(data_train[factor][data_train[factor] != np.inf]))
#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_test[factor] = data_test[factor].clip(np.nanmin(data_test[factor][data_test[factor] != -np.inf]), np.nanmax(data_test[factor][data_test[factor] != np.inf]))

#a=data_train[finallist].describe(percentiles=[0.01,0.05,0.1,0.9,0.95,0.99])
#a=data_test[finallist].describe(percentiles=[0.01,0.05,0.1,0.9,0.95,0.99])
# construct model based on train data:
sfa = []
for factor in finallist:
    sfa.append(SomersD(data_train.Final_PD_Risk_Rating, data_train[factor]))

model.update({'quant_factor':finallist})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*14})
model.update({'Invalid_Neg': [0]*14})
model.update(quanttrans(data_train, model, floor=0.05, cap=0.95))
# use floor=0 for factor 'ds@EBIT_to_IE'
model.floor[-2]=0
pl_invalid = []
for fac in finallist:
    pl_invalid.append(invalid_mapping[fac])
model.Invalid_Neg = pl_invalid


data_train = PD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_train = logitPD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_test = PD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
data_test = logitPD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
#normdata_train = normalization(data_train, model, quant_only=True)

cni_train = MFA(data_train, model, quant_only=True)
cni_test = MFA(data_test, model, quant_only=True)



normdat_train = cni_train.normdata.copy()
normdat_test = cni_test.normdata.copy()


#%%
pl_model = ['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']

# current model. no interaction
x_train = sm.add_constant(normdat_train[pl_model], prepend = True)
linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
result0 = linear.fit()
result0.summary()
"""
                            OLS Regression Results                            
==============================================================================
Dep. Variable:         logitPD_frPDRR   R-squared:                       0.510
Model:                            OLS   Adj. R-squared:                  0.510
Method:                 Least Squares   F-statistic:                     1109.
Date:                Thu, 27 Sep 2018   Prob (F-statistic):               0.00
Time:                        11:47:05   Log-Likelihood:                -5909.2
No. Observations:                5327   AIC:                         1.183e+04
Df Residuals:                    5321   BIC:                         1.187e+04
Df Model:                           5                                         
Covariance Type:            nonrobust                                         
=====================================================================================
                        coef    std err          t      P>|t|      [0.025      0.975]
-------------------------------------------------------------------------------------
const                -5.1571      0.010   -509.128      0.000      -5.177      -5.137
prof@EBITDA_to_NS     0.0044      0.000     20.257      0.000       0.004       0.005
cf@TD_to_EBITDA       0.0045      0.000     19.364      0.000       0.004       0.005
size@Total Assets     0.0097      0.000     45.396      0.000       0.009       0.010
bs@TD_to_Capt         0.0065      0.000     25.041      0.000       0.006       0.007
ds@EBITDA_to_IE       0.0012      0.000      5.092      0.000       0.001       0.002
==============================================================================
Omnibus:                      266.762   Durbin-Watson:                   0.402
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              975.025
Skew:                           0.072   Prob(JB):                    1.89e-212
Kurtosis:                       5.091   Cond. No.                         72.0
==============================================================================

Warnings:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
"""





#%% interaction
poly = PolynomialFeatures(interaction_only=True,include_bias=False)
data_temp = poly.fit_transform(normdat_train[pl_model])
df = pd.DataFrame(data_temp, columns=poly.get_feature_names(pl_model))
df.iloc[:,5:] = df.iloc[:,5:].transform(lambda x: 50*(x - x.mean()) / x.std())

corr_mat = df.corr()
# corr is ok


x_train = sm.add_constant(df, prepend = True)
linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
result = linear.fit()
result.summary()

"""
                            OLS Regression Results                            
==============================================================================
Dep. Variable:         logitPD_frPDRR   R-squared:                       0.537
Model:                            OLS   Adj. R-squared:                  0.535
Method:                 Least Squares   F-statistic:                     410.0
Date:                Thu, 27 Sep 2018   Prob (F-statistic):               0.00
Time:                        11:57:33   Log-Likelihood:                -5761.9
No. Observations:                5327   AIC:                         1.156e+04
Df Residuals:                    5311   BIC:                         1.166e+04
Df Model:                          15                                         
Covariance Type:            nonrobust                                         
=======================================================================================================
                                          coef    std err          t      P>|t|      [0.025      0.975]
-------------------------------------------------------------------------------------------------------
const                                  -5.1513      0.010   -518.124      0.000      -5.171      -5.132
prof@EBITDA_to_NS                       0.0045      0.000     19.495      0.000       0.004       0.005
cf@TD_to_EBITDA                         0.0035      0.000     10.420      0.000       0.003       0.004
size@Total Assets                       0.0097      0.000     45.059      0.000       0.009       0.010
bs@TD_to_Capt                           0.0068      0.000     22.407      0.000       0.006       0.007
ds@EBITDA_to_IE                         0.0033      0.000      8.458      0.000       0.003       0.004
prof@EBITDA_to_NS cf@TD_to_EBITDA      -0.0009      0.000     -3.126      0.002      -0.001      -0.000
prof@EBITDA_to_NS size@Total Assets    -0.0002      0.000     -0.879      0.380      -0.001       0.000
prof@EBITDA_to_NS bs@TD_to_Capt        -0.0003      0.000     -1.123      0.262      -0.001       0.000
prof@EBITDA_to_NS ds@EBITDA_to_IE      -0.0009      0.000     -3.212      0.001      -0.001      -0.000
cf@TD_to_EBITDA size@Total Assets    5.268e-05      0.000      0.201      0.841      -0.000       0.001
cf@TD_to_EBITDA bs@TD_to_Capt           0.0014      0.000      5.517      0.000       0.001       0.002
cf@TD_to_EBITDA ds@EBITDA_to_IE         0.0021      0.001      3.070      0.002       0.001       0.003
size@Total Assets bs@TD_to_Capt        -0.0025      0.000     -9.234      0.000      -0.003      -0.002
size@Total Assets ds@EBITDA_to_IE       0.0010      0.000      3.381      0.001       0.000       0.002
bs@TD_to_Capt ds@EBITDA_to_IE           0.0005      0.001      0.740      0.460      -0.001       0.002
==============================================================================
Omnibus:                      295.546   Durbin-Watson:                   0.423
Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1133.939
Skew:                           0.116   Prob(JB):                    5.86e-247
Kurtosis:                       5.248   Cond. No.                         90.3
==============================================================================

Warnings:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
"""


# remove insignificant interaction term
df.drop(columns=['prof@EBITDA_to_NS size@Total Assets', 'prof@EBITDA_to_NS bs@TD_to_Capt',\
	'cf@TD_to_EBITDA size@Total Assets','bs@TD_to_Capt ds@EBITDA_to_IE'], inplace=True)

# rerun reg
x_train = sm.add_constant(df, prepend = True)
linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
result = linear.fit()
result.summary()
"""
                            OLS Regression Results                            
==============================================================================
Dep. Variable:         logitPD_frPDRR   R-squared:                       0.536
Model:                            OLS   Adj. R-squared:                  0.535
Method:                 Least Squares   F-statistic:                     559.0
Date:                Thu, 27 Sep 2018   Prob (F-statistic):               0.00
Time:                        12:02:32   Log-Likelihood:                -5763.1
No. Observations:                5327   AIC:                         1.155e+04
Df Residuals:                    5315   BIC:                         1.163e+04
Df Model:                          11                                         
Covariance Type:            nonrobust                                         
=====================================================================================================
                                        coef    std err          t      P>|t|      [0.025      0.975]
-----------------------------------------------------------------------------------------------------
const                                -5.1509      0.010   -520.800      0.000      -5.170      -5.132
prof@EBITDA_to_NS                     0.0045      0.000     20.570      0.000       0.004       0.005
cf@TD_to_EBITDA                       0.0034      0.000     12.725      0.000       0.003       0.004
size@Total Assets                     0.0097      0.000     45.998      0.000       0.009       0.010
bs@TD_to_Capt                         0.0069      0.000     26.193      0.000       0.006       0.007
ds@EBITDA_to_IE                       0.0031      0.000      9.923      0.000       0.003       0.004
prof@EBITDA_to_NS cf@TD_to_EBITDA    -0.0010      0.000     -4.035      0.000      -0.002      -0.001
prof@EBITDA_to_NS ds@EBITDA_to_IE    -0.0010      0.000     -3.834      0.000      -0.001      -0.000
cf@TD_to_EBITDA bs@TD_to_Capt         0.0013      0.000      5.713      0.000       0.001       0.002
cf@TD_to_EBITDA ds@EBITDA_to_IE       0.0024      0.000      6.952      0.000       0.002       0.003
size@Total Assets bs@TD_to_Capt      -0.0026      0.000    -10.879      0.000      -0.003      -0.002
size@Total Assets ds@EBITDA_to_IE     0.0010      0.000      3.611      0.000       0.000       0.002
==============================================================================
Omnibus:                      296.729   Durbin-Watson:                   0.423
Prob(Omnibus):                  0.000   Jarque-Bera (JB):             1137.478
Skew:                           0.120   Prob(JB):                    9.99e-248
Kurtosis:                       5.251   Cond. No.                         79.1
==============================================================================

Warnings:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
"""

# remove interactions that have wrong sign
df.drop(columns=['prof@EBITDA_to_NS cf@TD_to_EBITDA','prof@EBITDA_to_NS ds@EBITDA_to_IE','size@Total Assets bs@TD_to_Capt'], inplace=True)

# rerun reg
x_train = sm.add_constant(df, prepend = True)
linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
result = linear.fit()
result.summary()

"""
                            OLS Regression Results                            
==============================================================================
Dep. Variable:         logitPD_frPDRR   R-squared:                       0.520
Model:                            OLS   Adj. R-squared:                  0.519
Method:                 Least Squares   F-statistic:                     720.3
Date:                Thu, 27 Sep 2018   Prob (F-statistic):               0.00
Time:                        12:04:00   Log-Likelihood:                -5855.4
No. Observations:                5327   AIC:                         1.173e+04
Df Residuals:                    5318   BIC:                         1.179e+04
Df Model:                           8                                         
Covariance Type:            nonrobust                                         
=====================================================================================================
                                        coef    std err          t      P>|t|      [0.025      0.975]
-----------------------------------------------------------------------------------------------------
const                                -5.1527      0.010   -512.780      0.000      -5.172      -5.133
prof@EBITDA_to_NS                     0.0042      0.000     19.086      0.000       0.004       0.005
cf@TD_to_EBITDA                       0.0037      0.000     14.598      0.000       0.003       0.004
size@Total Assets                     0.0097      0.000     45.310      0.000       0.009       0.010
bs@TD_to_Capt                         0.0065      0.000     24.663      0.000       0.006       0.007
ds@EBITDA_to_IE                       0.0025      0.000      9.216      0.000       0.002       0.003
cf@TD_to_EBITDA bs@TD_to_Capt         0.0019      0.000      7.906      0.000       0.001       0.002
cf@TD_to_EBITDA ds@EBITDA_to_IE       0.0009      0.000      3.380      0.001       0.000       0.001
size@Total Assets ds@EBITDA_to_IE    -0.0008      0.000     -3.466      0.001      -0.001      -0.000
==============================================================================
Omnibus:                      256.012   Durbin-Watson:                   0.407
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              922.902
Skew:                           0.036   Prob(JB):                    3.93e-201
Kurtosis:                       5.038   Cond. No.                         77.5
==============================================================================

Warnings:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
"""


# remove interactions that have wrong sign
df.drop(columns=['size@Total Assets ds@EBITDA_to_IE'], inplace=True)

# rerun reg
x_train = sm.add_constant(df, prepend = True)
linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
result = linear.fit()
result.summary()

"""
                            OLS Regression Results                            
==============================================================================
Dep. Variable:         logitPD_frPDRR   R-squared:                       0.519
Model:                            OLS   Adj. R-squared:                  0.518
Method:                 Least Squares   F-statistic:                     819.8
Date:                Thu, 27 Sep 2018   Prob (F-statistic):               0.00
Time:                        12:05:22   Log-Likelihood:                -5861.4
No. Observations:                5327   AIC:                         1.174e+04
Df Residuals:                    5319   BIC:                         1.179e+04
Df Model:                           7                                         
Covariance Type:            nonrobust                                         
===================================================================================================
                                      coef    std err          t      P>|t|      [0.025      0.975]
---------------------------------------------------------------------------------------------------
const                              -5.1518      0.010   -512.341      0.000      -5.171      -5.132
prof@EBITDA_to_NS                   0.0042      0.000     19.097      0.000       0.004       0.005
cf@TD_to_EBITDA                     0.0035      0.000     14.177      0.000       0.003       0.004
size@Total Assets                   0.0097      0.000     45.147      0.000       0.009       0.010
bs@TD_to_Capt                       0.0066      0.000     24.822      0.000       0.006       0.007
ds@EBITDA_to_IE                     0.0027      0.000      9.747      0.000       0.002       0.003
cf@TD_to_EBITDA bs@TD_to_Capt       0.0018      0.000      7.762      0.000       0.001       0.002
cf@TD_to_EBITDA ds@EBITDA_to_IE     0.0015      0.000      6.334      0.000       0.001       0.002
==============================================================================
Omnibus:                      248.471   Durbin-Watson:                   0.408
Prob(Omnibus):                  0.000   Jarque-Bera (JB):              875.868
Skew:                           0.033   Prob(JB):                    6.42e-191
Kurtosis:                       4.985   Cond. No.                         74.6
==============================================================================

Warnings:
[1] Standard Errors assume that the covariance matrix of the errors is correctly specified.
"""
N = len(df); df_R = 5321;	df_F = 5319
SSE_R = (result0.resid**2).sum()
SSE_F = (result.resid**2).sum()

F = (SSE_R-SSE_F)/(df_R-df_F) / (SSE_F/df_F)
#48.21772180652321


from scipy.stats import f
p_value = 1-f.cdf(F, 2,df_F, loc=0, scale=1)
# 1e-16



SomersD( normdat_train['logitPD_frPDRR'],result.fittedvalues)# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:25:09 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm

X_train = pd.read_pickle(r'MFA\train_2016.pkl.xz')
X_test = pd.read_pickle(r'MFA\test_2016.pkl.xz')

quant_factor = ['Net_Profit_Margin','Total_Debt_By_COP','Total_Assets','Total_Liab_by_Tang_Net_Worth','End_Cash_Equiv_By_Tot_Liab']
quali_factor = ['Strength_SOR_Prevent_Default','Level_Waiver_Covenant_Mod','Mgmt_Resp_Adverse_Conditions','Vulnerability_To_Changes']
PDInfo_file = r'C:\Users\ub71894\Documents\DevRepo\Files\PDModelParameters.xlsx'
masterscale_file = r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx'
model_name = 'C&I'; version = 1.2
model = PDModel(PDInfo_file, model_name, version, quant_factor, quali_factor, masterscale_file)
model.reset()


def modelSD(data, pl_factors, pl_wt, dependentvar):
	est = (data[pl_factors]*pl_wt).sum(axis=1)
	return(SomersD(data[dependentvar], est))

#%% 
cols_negsource = ['size@EBIT', 'size@EBITDA','size@Union Bank EBIT','size@Union Bank EBITDA','size@Retained Earnings','size@Capitalization',\
'ds@Interest Expense']
#a=X_train[cols_negsource].describe(percentiles=[0.01,0.02,0.05,0.1])


invalid_mapping = {
'prof@EBITDA_to_NS':0,
'prof@RE_to_TA':0,
'cf@TD_to_UBEBITDA':  'size@Union Bank EBITDA',
'cf@TD_to_EBITDA':  'size@EBITDA',
'size@Net_Sales': 0,
'size@Total Assets':0,
'size@Profit before Taxes':0,
'size@Net Profit':0,
'bs@TD_to_Capt':'size@Capitalization',
'bs@TD_to_TA':0,
'liq@ECE_to_TL':0,
'liq@RE_to_CL':0,
'ds@EBIT_to_IE':'ds@Interest Expense',
'ds@EBITDA_to_IE':'ds@Interest Expense'
}


finallist=[
'prof@EBITDA_to_NS', 'prof@RE_to_TA', 
'cf@TD_to_UBEBITDA','cf@TD_to_EBITDA',
'size@Net_Sales','size@Total Assets','size@Profit before Taxes', 'size@Net Profit', 
'bs@TD_to_Capt', 'bs@TD_to_TA', 
'liq@ECE_to_TL','liq@RE_to_CL', 
'ds@EBIT_to_IE','ds@EBITDA_to_IE']


data_train = X_train[finallist+cols_negsource+['Final_PD_Risk_Rating']]
data_train.dropna(subset=finallist+cols_negsource, how='any', inplace=True)
data_train.reset_index(drop=True, inplace=True)
data_train['size@Net_Sales'] = np.log(1+data_train['size@Net_Sales'])
data_train['size@Total Assets'] = np.log(1+data_train['size@Total Assets'])

data_test = X_test[finallist+cols_negsource+['Final_PD_Risk_Rating']]
data_test.dropna(subset=finallist+cols_negsource, how='any', inplace=True)
data_test.reset_index(drop=True, inplace=True)
data_test['size@Net_Sales'] = np.log(1+data_test['size@Net_Sales'])
data_test['size@Total Assets'] = np.log(1+data_test['size@Total Assets'])

#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_train[factor] = data_train[factor].clip(np.nanmin(data_train[factor][data_train[factor] != -np.inf]), np.nanmax(data_train[factor][data_train[factor] != np.inf]))
#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_test[factor] = data_test[factor].clip(np.nanmin(data_test[factor][data_test[factor] != -np.inf]), np.nanmax(data_test[factor][data_test[factor] != np.inf]))

#a=data_train[finallist].describe(percentiles=[0.01,0.05,0.1,0.9,0.95,0.99])
#a=data_test[finallist].describe(percentiles=[0.01,0.05,0.1,0.9,0.95,0.99])
# construct model based on train data:
sfa = []
for factor in finallist:
    sfa.append(SomersD(data_train.Final_PD_Risk_Rating, data_train[factor]))

model.update({'quant_factor':finallist})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*14})
model.update({'Invalid_Neg': [0]*14})
model.update(quanttrans(data_train, model, floor=0.05, cap=0.95))
# use floor=0 for factor 'ds@EBIT_to_IE'
model.floor[-2]=0
pl_invalid = []
for fac in finallist:
    pl_invalid.append(invalid_mapping[fac])
model.Invalid_Neg = pl_invalid


data_train = PD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_train = logitPD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_test = PD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
data_test = logitPD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
#normdata_train = normalization(data_train, model, quant_only=True)

cni_train = MFA(data_train, model, quant_only=True)
cni_test = MFA(data_test, model, quant_only=True)

normdat_train = cni_train.normdata.copy()
normdat_test = cni_test.normdata.copy()

#%%
pl_6_factors_panel =  ['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'liq@ECE_to_TL', 'ds@EBITDA_to_IE']
#X_train[pl_6_factors_panel].corr().to_excel(r'MFA\6_panel.xlsx')

pl_6_factors_bestin_1 =  ['prof@RE_to_TA', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'liq@ECE_to_TL', 'ds@EBITDA_to_IE']
#X_train[pl_6_factors_bestin_1].corr().to_excel(r'MFA\6_1.xlsx')

# has prof@EBITDA_to_NS
pl_6_factors_bestin_2 = ['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_TA', 'liq@RE_to_CL', 'ds@EBITDA_to_IE']
#X_train[pl_6_factors_bestin_2].corr().to_excel(r'MFA\6_2.xlsx')

pl_6_factors_bestout_1 =  ['prof@RE_to_TA', 'cf@TD_to_UBEBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'liq@ECE_to_TL', 'ds@EBITDA_to_IE']
#X_train[pl_6_factors_bestout_1].corr().to_excel(r'MFA\6_3.xlsx')

# has prof@EBITDA_to_NS
pl_6_factors_bestout_2 =  ['prof@RE_to_TA', 'cf@TD_to_EBITDA', 'size@Net_Sales', 'bs@TD_to_Capt', 'liq@ECE_to_TL', 'ds@EBITDA_to_IE']
#X_train[pl_6_factors_bestout_2].corr().to_excel(r'MFA\6_4.xlsx')
#%%



writer = pd.ExcelWriter(r'MFA\modelperfomance.xlsx')
pl_models= [pl_6_factors_panel,pl_6_factors_bestin_1,pl_6_factors_bestin_2,pl_6_factors_bestout_1,pl_6_factors_bestout_2]
pl_wt_range=[]
for num, finallist in enumerate(pl_models):
	x_train = sm.add_constant(normdat_train[finallist], prepend = True)
	x_test = sm.add_constant(normdat_test[finallist], prepend = True)
	linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
	result = linear.fit()
	#result.summary()	

	stats = result.params[1:] / result.params[1:].sum()

	pl_temp=[]
	for i in range(len(finallist)):	
		pl_temp.append((   max(0.01,round(round(stats[i],2)-0.05,2)),   max(0.01,round(round(stats[i],2)+0.05,2))   ))
	pl_wt_range.append(pl_temp)

	stats.loc['rsquared'] = result.rsquared
	stats.loc['inSD'] = SomersD(normdat_train['logitPD_frPDRR'], result.fittedvalues)
	stats.loc['outSD'] = SomersD(normdat_test['logitPD_frPDRR'], result.predict(x_test))
	stats.to_excel(writer, str(num))

writer.save()


#%%
writer = pd.ExcelWriter(r'MFA\gridsearch_6.xlsx')
pl_models= [pl_6_factors_panel,pl_6_factors_bestin_1,pl_6_factors_bestin_2,pl_6_factors_bestout_1,pl_6_factors_bestout_2]
'''
pl_wt_range=[[(0.1,0.2),(0.12,0.22),(0.3,0.45),(0.15,0.25),(0.07,0.17),(0.01,0.05)],
[(0.15,0.25),(0.12,0.22),(0.35,0.45),(0.01,0.1),(0.07,0.17),(0.01,0.1)],
[(0.1,0.2),(0.12,0.22),(0.3,0.45),(0.13,0.23),(0.07,0.17),(0.01,0.05)],
[(0.2,0.3),(0.05,0.15),(0.25,0.35),(0.05,0.15),(0.15,0.25),(0.01,0.1)],
[(0.12,0.22),(0.1,0.2),(0.3,0.4),(0.13,0.23),(0.07,0.17),(0.01,0.05)]
]
'''
for num, finallist in enumerate(pl_models):
	stats = cni_train.ARgridsearch(quant_factor=finallist,quant_weight_range=pl_wt_range[num], \
		delta_factor=0.01,isthere_def=False, dependentvar='logitPD_frPDRR')
	stats.to_excel(writer, str(num))

writer.save()


#%% print range for presentation:
count=0
for ranges in pl_wt_range:
	count+=1
	print('Below is for model {:d}'.format(count))
	for each in ranges:
		print('({b:.0f}%,{e:.0f}%)'.format(b=each[0]*100, e=each[1]*100))


#%%
print(modelSD(normdat_train, pl_factors=pl_models[0], pl_wt=[0.13,0.15,0.37,0.15,0.14,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[0], pl_wt=[0.13,0.15,0.37,0.15,0.14,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[0], pl_wt=[0.14,0.16,0.34,0.15,0.17,0.04], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[0], pl_wt=[0.14,0.16,0.34,0.15,0.17,0.04], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[0], pl_wt=[0.15,0.15,0.35,0.15,0.15,0.05], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[0], pl_wt=[0.15,0.15,0.35,0.15,0.15,0.05], dependentvar='logitPD_frPDRR'))





print(modelSD(normdat_train, pl_factors=pl_models[1], pl_wt=[0.16,0.12,0.32,0.2,0.14,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[1], pl_wt=[0.16,0.12,0.32,0.2,0.14,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[1], pl_wt=[0.16,0.18,0.38,0.03,0.18,0.07], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[1], pl_wt=[0.16,0.18,0.38,0.03,0.18,0.07], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[1], pl_wt=[0.15,0.15,0.4,0.05,0.2,0.05], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[1], pl_wt=[0.15,0.15,0.4,0.05,0.2,0.05], dependentvar='logitPD_frPDRR'))



print(modelSD(normdat_train, pl_factors=pl_models[2], pl_wt=[0.17,0.15,0.4,0.03,0.15,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[2], pl_wt=[0.17,0.15,0.4,0.03,0.15,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[2], pl_wt=[0.16,0.14,0.31,0.19,0.14,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[2], pl_wt=[0.16,0.14,0.31,0.19,0.14,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[2], pl_wt=[0.15,0.15,0.3,0.2,0.15,0.05], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[2], pl_wt=[0.15,0.15,0.3,0.2,0.15,0.05], dependentvar='logitPD_frPDRR'))



print(modelSD(normdat_train, pl_factors=pl_models[3], pl_wt=[0.18,0.15,0.4,0.01,0.16,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[3], pl_wt=[0.18,0.15,0.4,0.01,0.16,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[3], pl_wt=[0.16,0.14,0.31,0.19,0.14,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[3], pl_wt=[0.16,0.14,0.31,0.19,0.14,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[3], pl_wt=[0.15,0.15,0.3,0.2,0.15,0.05], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[3], pl_wt=[0.15,0.15,0.3,0.2,0.15,0.05], dependentvar='logitPD_frPDRR'))



print(modelSD(normdat_train, pl_factors=pl_models[4], pl_wt=[0.19,0.13,0.4,0.02,0.16,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[4], pl_wt=[0.19,0.13,0.4,0.02,0.16,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[4], pl_wt=[0.16,0.14,0.31,0.19,0.14,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[4], pl_wt=[0.16,0.14,0.31,0.19,0.14,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[4], pl_wt=[0.15,0.15,0.3,0.2,0.15,0.05], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[4], pl_wt=[0.15,0.15,0.3,0.2,0.15,0.05], dependentvar='logitPD_frPDRR'))





#%%
pl_5_factors_panel =  ['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
#X_train[pl_5_factors_panel].corr().to_excel(r'MFA\5_panel.xlsx')

pl_5_factors_bestin_1 =  ['prof@RE_to_TA', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
#X_train[pl_5_factors_bestin_1].corr().to_excel(r'MFA\5_1.xlsx')

#has prof@EBITDA_to_NS
pl_5_factors_bestin_2 = ['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_TA', 'ds@EBITDA_to_IE']
#X_train[pl_5_factors_bestin_2].corr().to_excel(r'MFA\5_2.xlsx')


pl_5_factors_bestout_1 = ['prof@RE_to_TA', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_TA', 'ds@EBITDA_to_IE']
#X_train[pl_5_factors_bestout_1].corr().to_excel(r'MFA\5_3.xlsx')

# has net profit
pl_5_factors_bestout_2 = ['prof@RE_to_TA', 'cf@TD_to_UBEBITDA', 'size@Total Assets', 'bs@TD_to_TA', 'ds@EBITDA_to_IE']

#X_train[pl_5_factors_bestout_2].corr().to_excel(r'MFA\5_4.xlsx')
#%%



writer = pd.ExcelWriter(r'MFA\modelperfomance_5.xlsx')
pl_models= [pl_5_factors_panel,pl_5_factors_bestin_1,pl_5_factors_bestin_2,pl_5_factors_bestout_1,pl_5_factors_bestout_2]

pl_wt_range=[]
for num, finallist in enumerate(pl_models):
	x_train = sm.add_constant(normdat_train[finallist], prepend = True)
	x_test = sm.add_constant(normdat_test[finallist], prepend = True)
	linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
	result = linear.fit()
	#result.summary()	

	stats = result.params[1:] / result.params[1:].sum()

	pl_temp=[]
	for i in range(len(finallist)):	
		pl_temp.append((   max(0.01,round(round(stats[i],2)-0.05,2)),   max(0.01,round(round(stats[i],2)+0.05,2))   ))
	pl_wt_range.append(pl_temp)

	stats.loc['rsquared'] = result.rsquared
	stats.loc['inSD'] = SomersD(normdat_train['logitPD_frPDRR'], result.fittedvalues)
	stats.loc['outSD'] = SomersD(normdat_test['logitPD_frPDRR'], result.predict(x_test))
	stats.to_excel(writer, str(num))

writer.save()

#%%
writer = pd.ExcelWriter(r'MFA\gridsearch_5.xlsx')
pl_models= [pl_5_factors_panel,pl_5_factors_bestin_1,pl_5_factors_bestin_2,pl_5_factors_bestout_1,pl_5_factors_bestout_2]
'''
pl_wt_range=[[(0.12,0.2),(0.12,0.22),(0.3,0.45),(0.15,0.25),(0.07,0.17)],
[(0.15,0.25),(0.15,0.25),(0.3,0.45),(0.1,0.2),(0.05,0.15)],
[(0.1,0.2),(0.12,0.22),(0.3,0.45),(0.15,0.25),(0.07,0.17)],
[(0.1,0.2),(0.01,0.1),(0.4,0.5),(0.22,0.32),(0.01,0.1)],
[(0.1,0.2),(0.01,0.1),(0.4,0.55),(0.2,0.3),(0.01,0.1)]
]
'''
for num, finallist in enumerate(pl_models):
	stats = cni_train.ARgridsearch(quant_factor=finallist,quant_weight_range=pl_wt_range[num], \
		delta_factor=0.01,isthere_def=False, dependentvar='logitPD_frPDRR')
	stats.to_excel(writer, str(num))

writer.save()


#%% print range for presentation:
count=5
for ranges in pl_wt_range:
	count+=1
	print('Below is for model {:d}'.format(count))
	for each in ranges:
		print('({b:.0f}%,{e:.0f}%)'.format(b=each[0]*100, e=each[1]*100))

#%%
print(modelSD(normdat_train, pl_factors=pl_models[0], pl_wt=[0.15,0.18,0.38,0.23,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[0], pl_wt=[0.15,0.18,0.38,0.23,0.06], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[0], pl_wt=[0.17,0.18,0.36,0.25,0.04], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[0], pl_wt=[0.17,0.18,0.36,0.25,0.04], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[0], pl_wt=[0.15,0.15,0.35,0.2,0.15], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[0], pl_wt=[0.15,0.15,0.35,0.2,0.15], dependentvar='logitPD_frPDRR'))



print(modelSD(normdat_train, pl_factors=pl_models[1], pl_wt=[0.2,0.17,0.42,0.1,0.11], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[1], pl_wt=[0.2,0.17,0.42,0.1,0.11], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[1], pl_wt=[0.19,0.19,0.42,0.1,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[1], pl_wt=[0.19,0.19,0.42,0.1,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[1], pl_wt=[0.2,0.2,0.4,0.1,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[1], pl_wt=[0.2,0.2,0.4,0.1,0.1], dependentvar='logitPD_frPDRR'))


print(modelSD(normdat_train, pl_factors=pl_models[2], pl_wt=[0.21,0.18,0.42,0.07,0.12], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[2], pl_wt=[0.21,0.18,0.42,0.07,0.12], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[2], pl_wt=[0.21,0.15,0.34,0.25,0.05], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[2], pl_wt=[0.21,0.15,0.34,0.25,0.05], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[2], pl_wt=[0.2,0.15,0.35,0.25,0.05], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[2], pl_wt=[0.2,0.15,0.35,0.25,0.05], dependentvar='logitPD_frPDRR'))



print(modelSD(normdat_train, pl_factors=pl_models[3], pl_wt=[0.22,0.15,0.42,0.08,0.13], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[3], pl_wt=[0.22,0.15,0.42,0.08,0.13], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[3], pl_wt=[0.2,0.21,0.42,0.06,0.11], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[3], pl_wt=[0.2,0.21,0.42,0.06,0.11], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[3], pl_wt=[0.2,0.2,0.4,0.1,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[3], pl_wt=[0.2,0.2,0.4,0.1,0.1], dependentvar='logitPD_frPDRR'))



print(modelSD(normdat_train, pl_factors=pl_models[4], pl_wt=[0.2,0.14,0.42,0.12,0.12], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[4], pl_wt=[0.2,0.14,0.42,0.12,0.12], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[4], pl_wt=[0.22,0.18,0.42,0.07,0.11], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[4], pl_wt=[0.22,0.18,0.42,0.07,0.11], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_train, pl_factors=pl_models[4], pl_wt=[0.2,0.2,0.4,0.1,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_models[4], pl_wt=[0.2,0.2,0.4,0.1,0.1], dependentvar='logitPD_frPDRR'))

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:25:09 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans,qualitrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm

X_train = pd.read_pickle(r'MFA\train_2016.pkl.xz')
X_test = pd.read_pickle(r'MFA\test_2016.pkl.xz')

quant_factor = ['Net_Profit_Margin','Total_Debt_By_COP','Total_Assets','Total_Liab_by_Tang_Net_Worth','End_Cash_Equiv_By_Tot_Liab']
quali_factor = ['Strength_SOR_Prevent_Default','Level_Waiver_Covenant_Mod','Mgmt_Resp_Adverse_Conditions','Vulnerability_To_Changes']
PDInfo_file = r'C:\Users\ub71894\Documents\DevRepo\Files\PDModelParameters.xlsx'
masterscale_file = r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx'
model_name = 'C&I'; version = 1.2
model = PDModel(PDInfo_file, model_name, version, quant_factor, quali_factor, masterscale_file)
model.reset()

def modelSD(data, pl_factors, pl_wt, dependentvar):
	est = (data[pl_factors]*pl_wt).sum(axis=1)
	return(SomersD(data[dependentvar], est))


#%% 
cols_negsource = ['size@EBIT', 'size@EBITDA','size@Union Bank EBIT','size@Union Bank EBITDA','size@Retained Earnings','size@Capitalization',\
'ds@Interest Expense']
#a=X_train[cols_negsource].describe(percentiles=[0.01,0.02,0.05,0.1])


invalid_mapping = {
'prof@EBITDA_to_NS':0,
'prof@RE_to_TA':0,
'cf@TD_to_UBEBITDA':  'size@Union Bank EBITDA',
'cf@TD_to_EBITDA':  'size@EBITDA',
'size@Net_Sales': 0,
'size@Total Assets':0,
'size@Profit before Taxes':0,
'size@Net Profit':0,
'bs@TD_to_Capt':'size@Capitalization',
'bs@TD_to_TA':0,
'liq@ECE_to_TL':0,
'liq@RE_to_CL':0,
'ds@EBIT_to_IE':'ds@Interest Expense',
'ds@EBITDA_to_IE':'ds@Interest Expense'
}
pl_qualifactors=[ 'qual1', 'qual2',  'Management_Quality','qual4', 'Access_Outside_Capital']

finallist=[
'prof@EBITDA_to_NS', 'prof@RE_to_TA', 
'cf@TD_to_UBEBITDA','cf@TD_to_EBITDA',
'size@Net_Sales','size@Total Assets','size@Profit before Taxes', 'size@Net Profit', 
'bs@TD_to_Capt', 'bs@TD_to_TA', 
'liq@ECE_to_TL','liq@RE_to_CL', 
'ds@EBIT_to_IE','ds@EBITDA_to_IE']


data_train = X_train[finallist+cols_negsource+pl_qualifactors+['Final_PD_Risk_Rating']]
data_train.dropna(subset=pl_qualifactors, how='any', inplace=True)
data_train.reset_index(drop=True, inplace=True)
data_train['size@Net_Sales'] = np.log(1+data_train['size@Net_Sales'])
data_train['size@Total Assets'] = np.log(1+data_train['size@Total Assets'])

data_test = X_test[finallist+cols_negsource+pl_qualifactors+['Final_PD_Risk_Rating']]
data_test.dropna(subset=pl_qualifactors, how='any', inplace=True)
data_test.reset_index(drop=True, inplace=True)
data_test['size@Net_Sales'] = np.log(1+data_test['size@Net_Sales'])
data_test['size@Total Assets'] = np.log(1+data_test['size@Total Assets'])

#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_train[factor] = data_train[factor].clip(np.nanmin(data_train[factor][data_train[factor] != -np.inf]), np.nanmax(data_train[factor][data_train[factor] != np.inf]))
#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_test[factor] = data_test[factor].clip(np.nanmin(data_test[factor][data_test[factor] != -np.inf]), np.nanmax(data_test[factor][data_test[factor] != np.inf]))

#a=data_train[finallist].describe(percentiles=[0.01,0.05,0.1,0.9,0.95,0.99])
#a=data_test[finallist].describe(percentiles=[0.01,0.05,0.1,0.9,0.95,0.99])
# construct model based on train data:
sfa = []
for factor in finallist:
    sfa.append(SomersD(data_train.Final_PD_Risk_Rating, data_train[factor]))

model.update({'quant_factor':finallist})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*14})
model.update({'Invalid_Neg': [0]*14})
model.update(quanttrans(data_train, model, floor=0.05, cap=0.95))
# use floor=0 for factor 'ds@EBIT_to_IE'
model.floor[-2]=0
pl_invalid = []
for fac in finallist:
    pl_invalid.append(invalid_mapping[fac])
model.Invalid_Neg = pl_invalid


data_train = PD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_train = logitPD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_test = PD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
data_test = logitPD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
#normdata_train = normalization(data_train, model, quant_only=True)

model.update({'quali_factor':pl_qualifactors})
model.update(qualitrans(data_train, model, isthere_def=False, dependentvar='PD_frPDRR', output=True))
model.qualimapping[0]['D'] = 64.99754649555864
model.qualimapping[2]['E'] = 118.48350997018787

cni_train = MFA(data_train, model, quant_only=False)
cni_test = MFA(data_test, model, quant_only=False)

normdat_train = cni_train.normdata.copy()
normdat_test = cni_test.normdata.copy()




#%%
#linear reg

x_train = sm.add_constant(normdat_train[pl_qualifactors], prepend = True)
x_test = sm.add_constant(normdat_test[pl_qualifactors], prepend = True)
linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
result = linear.fit()
#result.summary()   

stats = result.params[1:] / result.params[1:].sum()
stats.loc['rsquared'] = result.rsquared
stats.loc['inSD'] = SomersD(normdat_train['logitPD_frPDRR'], result.fittedvalues)
stats.loc['outSD'] = SomersD(normdat_test['logitPD_frPDRR'], result.predict(x_test))
pl_wt_range=[]
for i in range(5):	
	pl_wt_range.append((max(0.01,round(round(stats[i],2)-0.05,2)),   max(0.01,round(round(stats[i],2)+0.05,2))))


#%% print range for presentation:


for each in pl_wt_range:
	print('({b:.0f}%,{e:.0f}%)'.format(b=each[0]*100, e=each[1]*100))


#%%
writer = pd.ExcelWriter(r'MFA\gridsearch_quali.xlsx')
stats = cni_train.ARgridsearch(quali_factor=pl_qualifactors, quali_weight_range=pl_wt_range, delta_factor=0.01, isthere_def=False, dependentvar='logitPD_frPDRR')
stats.to_excel(writer, 'in-sample')

stats = cni_test.ARgridsearch(quali_factor=pl_qualifactors, quali_weight_range=pl_wt_range, delta_factor=0.01, isthere_def=False, dependentvar='logitPD_frPDRR')
stats.to_excel(writer, 'out-of_sample')
writer.save()

#%%
#linear reg

x_train = sm.add_constant(normdat_train[pl_qualifactors], prepend = True)
x_test = sm.add_constant(normdat_test[pl_qualifactors], prepend = True)
linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
result = linear.fit()
#result.summary()   

stats = result.params[1:] / result.params[1:].sum()
stats.loc['rsquared'] = result.rsquared
stats.loc['inSD'] = SomersD(normdat_train['logitPD_frPDRR'], result.fittedvalues)
stats.loc['outSD'] = SomersD(normdat_test['logitPD_frPDRR'], result.predict(x_test))


#%%
#proposal


print(modelSD(normdat_train, pl_factors=pl_qualifactors, pl_wt=[0.32,0.22,0.16,0.16,0.14], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_qualifactors, pl_wt=[0.32,0.22,0.16,0.16,0.14], dependentvar='logitPD_frPDRR'))



print(modelSD(normdat_train, pl_factors=pl_qualifactors, pl_wt=[0.33,0.21,0.08,0.2,0.18], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_qualifactors, pl_wt=[0.33,0.21,0.08,0.2,0.18], dependentvar='logitPD_frPDRR'))

0.33,0.21,0.08,0.2,0.18


print(modelSD(normdat_train, pl_factors=pl_qualifactors, pl_wt=[0.32,0.23,0.16,0.14,0.15], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_qualifactors, pl_wt=[0.32,0.23,0.16,0.14,0.15], dependentvar='logitPD_frPDRR'))

0.32,0.23,0.16,0.14,0.15


print(modelSD(normdat_train, pl_factors=pl_qualifactors, pl_wt=[0.3,0.25,0.2,0.15,0.1], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_qualifactors, pl_wt=[0.3,0.25,0.2,0.15,0.1], dependentvar='logitPD_frPDRR'))
0.3,0.25,0.2,0.15,0.1


print(modelSD(normdat_train, pl_factors=pl_qualifactors, pl_wt=[0.25,0.25,0.15,0.2,0.15], dependentvar='logitPD_frPDRR'))
print(modelSD(normdat_test, pl_factors=pl_qualifactors, pl_wt=[0.25,0.25,0.15,0.2,0.15], dependentvar='logitPD_frPDRR'))

0.25,0.25,0.15,0.2,0.15
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:25:09 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans,qualitrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm

X_train = pd.read_pickle(r'MFA\train_2016.pkl.xz')

quant_factor = ['Net_Profit_Margin','Total_Debt_By_COP','Total_Assets','Total_Liab_by_Tang_Net_Worth','End_Cash_Equiv_By_Tot_Liab']
quali_factor = ['Strength_SOR_Prevent_Default','Level_Waiver_Covenant_Mod','Mgmt_Resp_Adverse_Conditions','Vulnerability_To_Changes']
PDInfo_file = r'C:\Users\ub71894\Documents\DevRepo\Files\PDModelParameters.xlsx'
masterscale_file = r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx'
model_name = 'C&I'; version = 1.2
model = PDModel(PDInfo_file, model_name, version, quant_factor, quali_factor, masterscale_file)
model.reset()

#%% 
cols_negsource = ['size@EBIT', 'size@EBITDA','size@Union Bank EBIT','size@Union Bank EBITDA','size@Retained Earnings','size@Capitalization',\
'ds@Interest Expense']
#a=X_train[cols_negsource].describe(percentiles=[0.01,0.02,0.05,0.1])


invalid_mapping = {
'prof@EBITDA_to_NS':0,
'prof@RE_to_TA':0,
'cf@TD_to_UBEBITDA':  'size@Union Bank EBITDA',
'cf@TD_to_EBITDA':  'size@EBITDA',
'size@Net_Sales': 0,
'size@Total Assets':0,
'size@Profit before Taxes':0,
'size@Net Profit':0,
'bs@TD_to_Capt':'size@Capitalization',
'bs@TD_to_TA':0,
'liq@ECE_to_TL':0,
'liq@RE_to_CL':0,
'ds@EBIT_to_IE':'ds@Interest Expense',
'ds@EBITDA_to_IE':'ds@Interest Expense'
}
pl_qualifactors=[ 'qual1', 'qual2',  'Management_Quality','qual4', 'Access_Outside_Capital']

finallist=[
'prof@EBITDA_to_NS', 'prof@RE_to_TA', 
'cf@TD_to_UBEBITDA','cf@TD_to_EBITDA',
'size@Net_Sales','size@Total Assets','size@Profit before Taxes', 'size@Net Profit', 
'bs@TD_to_Capt', 'bs@TD_to_TA', 
'liq@ECE_to_TL','liq@RE_to_CL', 
'ds@EBIT_to_IE','ds@EBITDA_to_IE']


data_train = X_train[finallist+cols_negsource+pl_qualifactors+['Final_PD_Risk_Rating']]
#data_train.dropna(subset=finallist+cols_negsource, how='any', inplace=True)
data_train.dropna(subset=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE'], \
	how='any', inplace=True)

data_train.reset_index(drop=True, inplace=True)
data_train['size@Net_Sales'] = np.log(1+data_train['size@Net_Sales'])
data_train['size@Total Assets'] = np.log(1+data_train['size@Total Assets'])


#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_train[factor] = data_train[factor].clip(np.nanmin(data_train[factor][data_train[factor] != -np.inf]), np.nanmax(data_train[factor][data_train[factor] != np.inf]))
sfa = []
for factor in finallist:
    sfa.append(SomersD(data_train.Final_PD_Risk_Rating, data_train[factor]))

model.update({'quant_factor':finallist})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*14})
model.update({'Invalid_Neg': [0]*14})
model.update(quanttrans(data_train, model, floor=0.05, cap=0.95))
# use floor=0 for factor 'ds@EBIT_to_IE'
model.floor[-2]=0
pl_invalid = []
for fac in finallist:
    pl_invalid.append(invalid_mapping[fac])
model.Invalid_Neg = pl_invalid


data_train = PD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_train = logitPD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')

#normdata_train = normalization(data_train, model, quant_only=True)

#%% 
quant_factor = ['prof@EBITDA_to_NS', 'prof@RE_to_TA', 'cf@TD_to_UBEBITDA', 'cf@TD_to_EBITDA', 'size@Net_Sales',\
 'size@Total Assets', 'size@Profit before Taxes', 'size@Net Profit', 'bs@TD_to_Capt', 'bs@TD_to_TA', \
 'liq@ECE_to_TL', 'liq@RE_to_CL', 'ds@EBIT_to_IE', 'ds@EBITDA_to_IE']

pl_index = [0,3,5,8,13]
quant_factor_final = [quant_factor[x] for x in pl_index]
model.update({'quant_factor':quant_factor_final})

model.update({'quant_multiplier': [model.quant_multiplier[x] for x in pl_index]})
model.update({'quant_log': [model.quant_log[x] for x in pl_index]})
model.update({'Invalid_Neg': [model.Invalid_Neg[x] for x in pl_index]})
model.update({'cap': [model.cap[x] for x in pl_index]})
model.update({'floor': [model.floor[x] for x in pl_index]})
model.update({'doc_mean': [model.doc_mean[x] for x in pl_index]})
model.update({'doc_std': [model.doc_std[x] for x in pl_index]})



model.save(r'spec\model_quant_cfms.pkl')
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:25:09 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans,qualitrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm
import pickle
 
X_train = pd.read_pickle(r'MFA\train_2016.pkl.xz')
#X_train = X_train.query('timestamp>20100101')
X_test = pd.read_pickle(r'MFA\test_2016.pkl.xz')

filehandler = open(r'spec\model_quant_cfms.pkl','rb')
model = pickle.load(filehandler)


#%% 
cols_negsource = ['size@EBIT', 'size@EBITDA','size@Union Bank EBIT','size@Union Bank EBITDA','size@Retained Earnings','size@Capitalization',\
'ds@Interest Expense']
#a=X_train[cols_negsource].describe(percentiles=[0.01,0.02,0.05,0.1])


invalid_mapping = {
'prof@EBITDA_to_NS':0,
'prof@RE_to_TA':0,
'cf@TD_to_UBEBITDA':  'size@Union Bank EBITDA',
'cf@TD_to_EBITDA':  'size@EBITDA',
'size@Net_Sales': 0,
'size@Total Assets':0,
'size@Profit before Taxes':0,
'size@Net Profit':0,
'bs@TD_to_Capt':'size@Capitalization',
'bs@TD_to_TA':0,
'liq@ECE_to_TL':0,
'liq@RE_to_CL':0,
'ds@EBIT_to_IE':'ds@Interest Expense',
'ds@EBITDA_to_IE':'ds@Interest Expense'
}
pl_qualifactors=[ 'qual1', 'qual2',  'Management_Quality','qual4', 'Access_Outside_Capital']

finallist=[
'prof@EBITDA_to_NS', 'prof@RE_to_TA', 
'cf@TD_to_UBEBITDA','cf@TD_to_EBITDA',
'size@Net_Sales','size@Total Assets','size@Profit before Taxes', 'size@Net Profit', 
'bs@TD_to_Capt', 'bs@TD_to_TA', 
'liq@ECE_to_TL','liq@RE_to_CL', 
'ds@EBIT_to_IE','ds@EBITDA_to_IE']


data_train = X_train[finallist+cols_negsource+pl_qualifactors+['Final_PD_Risk_Rating']]
data_train.dropna(subset=pl_qualifactors, how='any', inplace=True)
data_train.reset_index(drop=True, inplace=True)
data_train['size@Net_Sales'] = np.log(1+data_train['size@Net_Sales'])
data_train['size@Total Assets'] = np.log(1+data_train['size@Total Assets'])

data_test = X_test[finallist+cols_negsource+pl_qualifactors+['Final_PD_Risk_Rating']]
data_test.dropna(subset=pl_qualifactors, how='any', inplace=True)
data_test.reset_index(drop=True, inplace=True)
data_test['size@Net_Sales'] = np.log(1+data_test['size@Net_Sales'])
data_test['size@Total Assets'] = np.log(1+data_test['size@Total Assets'])

#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_train[factor] = data_train[factor].clip(np.nanmin(data_train[factor][data_train[factor] != -np.inf]), np.nanmax(data_train[factor][data_train[factor] != np.inf]))
#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_test[factor] = data_test[factor].clip(np.nanmin(data_test[factor][data_test[factor] != -np.inf]), np.nanmax(data_test[factor][data_test[factor] != np.inf]))


data_train = PD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_train = logitPD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_test = PD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
data_test = logitPD_frPDRR(data_test, model, 'Final_PD_Risk_Rating')
#normdata_train = normalization(data_train, model, quant_only=True)

model.update({'quali_factor':pl_qualifactors})
model.update(qualitrans(data_train, model, isthere_def=False, dependentvar='PD_frPDRR', output=False))
model.qualimapping[0]['D'] = 64.99754649556864
model.qualimapping[2]['E'] = 118.48350997018787



model.quant_weight = [0.15, 0.15, 0.35, 0.2, 0.15]
model.quali_weight= [0.25, 0.25, 0.15, 0.2, 0.15]

cni_train = MFA(data_train, model, quant_only=False)
cni_test = MFA(data_test, model, quant_only=False)

#%%

#cni_train.modelAR(quant_weight=0, quali_weight=model.quali_weight, quantweight=0, isthere_def=False, dependentvar='logitPD_frPDRR', use_msms=True)
#cni_test.modelAR(quant_weight=0, quali_weight=model.quali_weight, quantweight=0, isthere_def=False, dependentvar='logitPD_frPDRR', use_msms=True)

# get optimal quant module weight and graph
cni_train.plotAR(quant_weight=model.quant_weight, quali_weight=model.quali_weight, quantweight_range=[0,1], isthere_def=False, dependentvar='logitPD_frPDRR', savefig=True)
# quantweight=0.55

# update model.quantmean, model.qualimean, model.quantstd and model.qualistd
cni_train.modelAR(quant_weight=model.quant_weight, quali_weight=model.quali_weight, quantweight=0.55, \
	isthere_def=False, dependentvar='logitPD_frPDRR', use_msms=False, update_msms=True)

model.save(r'spec\model_bf_calib.pkl')

cni_test.modelAR(quant_weight=model.quant_weight, quali_weight=model.quali_weight, quantweight=0.55, \
	isthere_def=False, dependentvar='logitPD_frPDRR', use_msms=True)

# get table for grid search result on quantweight
pl_qtweight=[]; pl_sd1=[]; pl_sd2=[]
for i in range(81):
	# set quantweight: from 0.1 to 0.9
	qtwt = (i+10)/100
	pl_qtweight.append('{:d}%'.format(i+10))
	temp1 = cni_train.modelAR(quant_weight=model.quant_weight, quali_weight=model.quali_weight, quantweight=qtwt, \
			isthere_def=False, dependentvar='logitPD_frPDRR', use_msms=True).loc['SomersD','AR']
	pl_sd1.append(temp1)
	temp2 = cni_test.modelAR(quant_weight=model.quant_weight, quali_weight=model.quali_weight, quantweight=qtwt, \
			isthere_def=False, dependentvar='logitPD_frPDRR', use_msms=True).loc['SomersD','AR']
	pl_sd2.append(temp2)

table_qtwt = pd.DataFrame()
table_qtwt['quantmodule_weight'] = pl_qtweight
table_qtwt['model in-sample SomersD'] = pl_sd1
table_qtwt['model out-of-sample SomersD'] = pl_sd2

table_qtwt.to_excel(r'MFA\quantmodule.xlsx')# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 16:24:53 2018

@author: ub71894 (4e8e6d0b), CSG
""" 
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans,qualitrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm
import pickle


filehandler = open(r'spec\model_bf_calib.pkl','rb')
model = pickle.load(filehandler)


data_train = pd.read_pickle(r'MFA\train_2016.pkl.xz')
data_test_2017 = pd.read_pickle(r'MFA\test_2017.pkl.xz')




#%% 
data_train.dropna(subset=model.quali_factor, how='any', inplace=True)
data_train.reset_index(drop=True, inplace=True)
# log trans
data_train['size@Total Assets'] = np.log(1+data_train['size@Total Assets'])
# fill inf
finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        data_train[factor] = data_train[factor].clip(np.nanmin(data_train[factor][data_train[factor] != -np.inf]), np.nanmax(data_train[factor][data_train[factor] != np.inf]))
# get existing model's Final PDRR implied PD and logit PD
data_train = PD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_train = logitPD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')


data_test_2017.dropna(subset=model.quali_factor, how='any', inplace=True)
data_test_2017.reset_index(drop=True, inplace=True)
# log trans
data_test_2017['size@Total Assets'] = np.log(1+data_test_2017['size@Total Assets'])
# fill inf
finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        data_test_2017[factor] = data_test_2017[factor].clip(np.nanmin(data_test_2017[factor][data_test_2017[factor] != -np.inf]), np.nanmax(data_test_2017[factor][data_test_2017[factor] != np.inf]))
# get existing model's Final PDRR implied PD and logit PD
data_test_2017 = PD_frPDRR(data_test_2017, model, 'Final_PD_Risk_Rating', ms_ver='new')
data_test_2017 = logitPD_frPDRR(data_test_2017, model, 'Final_PD_Risk_Rating', ms_ver='new')




cni_train = MFA(data_train, model, quant_only=False)
cni_train.modelAR(quant_weight=model.quant_weight, quali_weight=model.quali_weight, quantweight=0.55, \
	isthere_def=False, dependentvar='logitPD_frPDRR', use_msms=True)


cni_test_2017 = MFA(data_test_2017, model, quant_only=False)
cni_test_2017.modelAR(quant_weight=model.quant_weight, quali_weight=model.quali_weight, quantweight=0.55, \
	isthere_def=False, dependentvar='logitPD_frPDRR', use_msms=True)






norm_train_2010_2016 = cni_train.normdata.copy()
norm_test_2017 = cni_test_2017.normdata.copy()


norm_train_2010_2016.to_pickle(r'calib\norm_2010_2016.pkl.xz')
norm_test_2017.to_pickle(r'calib\norm_test_2017.pkl.xz')
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 11:35:38 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\calib")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import statsmodels.formula.api as smf
import seaborn as sns
import pickle
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import copy
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
CT = 0.0105
# load model setting
filehandler = open(r'..\spec\model_bf_calib.pkl','rb')
model = pickle.load(filehandler)

 
#%%
def SegLR(data, cutoff_score, cutoff_logitPD_frPDRR):
    # get params for single line
    res_full = smf.ols(formula='logitPD_frPDRR ~Totalscore', data=data).fit()
    # get params for double lines
    data1 = data.query('Totalscore<={}'.format(cutoff_score))
    data2 = data.query('Totalscore>{}'.format(cutoff_score))
    res1 = smf.ols(formula='I(logitPD_frPDRR-cutoff_logitPD_frPDRR) ~ I(Totalscore-cutoff_score)+0', data=data1).fit()
    res2 = smf.ols(formula='I(logitPD_frPDRR-cutoff_logitPD_frPDRR) ~ I(Totalscore-cutoff_score)+0', data=data2).fit()

    temp = {'Intercept':[],'slope':[],'cutoff_score':[],'cutoff_PD':[],'totalSSR':[],'Intercept1':[],'Intercept2':[],\
    'slope1':[],'slope2':[]}
    # params for single line
    temp['Intercept']               = res_full.params[0]
    temp['slope']                   = res_full.params[1]
    # params for double lines
    temp['cutoff_score']            = cutoff_score
    temp['cutoff_logitPD_frPDRR']   = cutoff_logitPD_frPDRR
    temp['cutoff_PD']               = np.exp(cutoff_logitPD_frPDRR) / (1+np.exp(cutoff_logitPD_frPDRR))
    temp['totalSSR']                = res1.ssr + res2.ssr
    temp['Intercept1']              = cutoff_logitPD_frPDRR - res1.params[0]*cutoff_score
    temp['slope1']                  = res1.params[0]
    temp['Intercept2']              = cutoff_logitPD_frPDRR - res2.params[0]*cutoff_score
    temp['slope2']                  = res2.params[0]

    return(temp)



def UpdateInterceptbyCT(dat, CT, **kw):
    data = dat.copy()
    newparam = copy.deepcopy(kw)

    Intercept = kw.pop('Intercept')
    slope = kw.pop('slope')
    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')
    CT = CT 

    def _func(x): # get shift for single line
        _Intercept = Intercept+ x
        logit_PD_est = []
        data['logit_PD_est'] = _Intercept + slope*data['Totalscore']
        data['PD_est'] = data['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        return (data.PD_est.mean()-CT)

    def _func2(x): # get shift for double lines
        _Intercept1 = Intercept1 +x
        _Intercept2 = Intercept2 +x
        logit_PD_est = []
        for score in data['Totalscore']:
            if score <= cutoff_score:
                logit_PD_est.append(_Intercept1+slope1*score)
            else:
                logit_PD_est.append(_Intercept2+slope2*score)
        data['logit_PD_est'] = logit_PD_est
        data['PD_est'] = data['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        return (data.PD_est.mean()-CT)

    shift_single = fsolve(_func, 0.01)
    shift_double = fsolve(_func2, 0.01)

    newparam.update({'Intercept_origin': Intercept, 'shift_single':shift_single[0],'Intercept': Intercept+shift_single[0],\
        'Intercept1_origin': Intercept1, 'Intercept2_origin': Intercept2, 'shift_double':shift_double[0],\
        'Intercept1': Intercept1+shift_double[0], 'Intercept2': Intercept2+shift_double[0]})
    
    return(newparam)


# make change to make paras comes from bin data ,but plot all data.
def SegLRplot(data_all, **kw):

    cutoff_score = kw.pop('cutoff_score')
    cutoff_logitPD_frPDRR = kw.pop('cutoff_logitPD_frPDRR')
    Intercept_origin = kw.pop('Intercept_origin')
    Intercept1_origin = kw.pop('Intercept1_origin')
    Intercept2_origin = kw.pop('Intercept2_origin')
    Intercept = kw.pop('Intercept')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope = kw.pop('slope')    
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    fig, ax = plt.subplots()
    ax.scatter(data_all.Totalscore,data_all.logitPD_frPDRR, s=25)    
    # lines before CT shift
    X1_plot = np.linspace(-50,cutoff_score,200)
    ax.plot(X1_plot, (Intercept1_origin + slope1*X1_plot), label="Seg 1_bf_CT")
    X2_plot = np.linspace(cutoff_score,100,200)
    ax.plot(X2_plot, (Intercept2_origin + slope2*X2_plot), label="Seg 2_bf_CT")
    X_full_plot = np.linspace(-50,100,200)
    ax.plot(X_full_plot, X_full_plot*slope + Intercept_origin, label="SingleLine_bf_CT")
    # lines after CT shift
    ax.plot(X1_plot, (Intercept1 + slope1*X1_plot), label="Seg 1_af_CT")
    ax.plot(X2_plot, (Intercept2 + slope2*X2_plot), label="Seg 2_af_CT")
    ax.plot(X_full_plot, X_full_plot*slope + Intercept, label="SingleLine_af_CT")

    legend = ax.legend(loc='upper left', shadow=True)

    plt.show()


def Segscorecard_afcali(data, MS, **kw):

    cutoff_score = kw.pop('cutoff_score')
    cutoff_logitPD_frPDRR = kw.pop('cutoff_logitPD_frPDRR')
    Intercept = kw.pop('Intercept')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope = kw.pop('slope')    
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')


    data1 = data.query('Totalscore<={}'.format(cutoff_score))
    data2 = data.query('Totalscore>{}'.format(cutoff_score))
    data1['fitted_logit_pd_afcali'] = Intercept1 + slope1*data1['Totalscore']
    data2['fitted_logit_pd_afcali'] = Intercept2 + slope2*data2['Totalscore']
    data1['fitted_pd_afcali'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in data1['fitted_logit_pd_afcali'] ]
    data2['fitted_pd_afcali'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in data2['fitted_logit_pd_afcali'] ]
    Ratings = []
    for i in data1.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd_afcali)))
    data1['fitted_PDRR_afcali'] = Ratings   
    Ratings = []
    for i in data2.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd_afcali)))
    data2['fitted_PDRR_afcali'] = Ratings 
    dat = pd.concat([data1,data2])
    temp = pd.merge(data, dat[['CUSTOMERID','timestamp', 'fitted_logit_pd_afcali','fitted_pd_afcali','fitted_PDRR_afcali']], on=['CUSTOMERID','timestamp'], how='inner')
    
    temp['fitted_logit_pd_afcali_SL'] = Intercept + slope*temp['Totalscore']
    temp['fitted_pd_afcali_SL'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in temp['fitted_logit_pd_afcali_SL'] ]
    Ratings = []
    for i in temp.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd_afcali_SL)))
    temp['fitted_PDRR_afcali_SL'] = Ratings   

    return(temp)



#%%
# load calibration data and calculate total score based on model setting
#dat = pd.read_pickle('norm_test_2017.pkl.xz')
dat = pd.read_pickle('norm_2010_2016.pkl.xz')
dat['quantscore'] = (model.quant_weight * dat[model.quant_factor].values).sum(axis=1)
dat['quantscore'] = 50*( dat['quantscore'] - model.quantmean) / model.quantstd
dat['qualiscore'] = (model.quali_weight * dat[model.quali_factor].values).sum(axis=1)
dat['qualiscore'] = 50*( dat['qualiscore'] - model.qualimean) / model.qualistd
dat['Totalscore'] = dat['quantscore']*model.quantweight + dat['qualiscore'] *model.qualiweight

# double check
print(SomersD(dat.Final_PD_Risk_Rating, dat.Totalscore))


#%%
dat['bin'] = pd.qcut(dat['Totalscore'], 20)
sns.lmplot(x="Totalscore", y='logitPD_frPDRR', data=dat)

dat_bin = dat.groupby(by='bin').mean()[['logitPD_frPDRR','Totalscore']]
res = smf.ols(formula='logitPD_frPDRR ~Totalscore', data=dat_bin).fit()
Intercept = res.params[0]; slope=res.params[1]
sns.lmplot(x="Totalscore", y='logitPD_frPDRR', data=dat_bin)


df=pd.DataFrame()
for cutoff in range(-40,50):
    cutoff_logitPD = Intercept + slope * cutoff   
    df = df.append(SegLR(dat_bin, cutoff, cutoff_logitPD), ignore_index=True)

cutoff_score = 43
df.loc[df['cutoff_score']==cutoff_score, 'cutoff_logitPD_frPDRR'].values[0]
cutoff_logitPD = df.loc[df['cutoff_score']==cutoff_score, 'cutoff_logitPD_frPDRR'].values[0] # -4.173395974061328

calib_params = SegLR(dat_bin, cutoff_score, cutoff_logitPD)
updated_params = UpdateInterceptbyCT(dat, CT, **calib_params)
SegLRplot(dat, **updated_params)



#%%
dat_befadjCT = Segscorecard_afcali(dat, MS, **calib_params)
dat_aftadjCT = Segscorecard_afcali(dat, MS, **updated_params)
CreateBenchmarkMatrix(dat_befadjCT, 'Matrix_Output_tradition.xlsx', 'bfCT', 'fitted_PDRR_afcali','Final_PD_Risk_Rating',  PDRR=range(1,16))
CreateBenchmarkMatrix(dat_befadjCT, 'Matrix_Output_tradition.xlsx', 'bfCT_SL', 'fitted_PDRR_afcali_SL','Final_PD_Risk_Rating',  PDRR=range(1,16))

CreateBenchmarkMatrix(dat_aftadjCT, 'Matrix_Output_tradition.xlsx', 'afCT', 'fitted_PDRR_afcali','Final_PD_Risk_Rating',  PDRR=range(1,16))
CreateBenchmarkMatrix(dat_aftadjCT, 'Matrix_Output_tradition.xlsx', 'afCT_SL', 'fitted_PDRR_afcali_SL','Final_PD_Risk_Rating',  PDRR=range(1,16))
















#%%

def fun(data, seg1_slope_range, seg1_slope_delta, cutoff_score_range, CT, sl_line_intcp, sl_line_slope, measure):
    df=pd.DataFrame()
    for cutoff_score in cutoff_score_range:
        cutoff_logitPD = cutoff_score * sl_line_slope + sl_line_intcp

        temp_df=pd.DataFrame()
        for slope1 in seg1_slope_range:
            Intercept1 = cutoff_logitPD - slope1*cutoff_score
            temp_df = temp_df.append(fun2(data, cutoff_score, cutoff_logitPD, slope1, Intercept1, CT), ignore_index=True)
        
        df =df.append(maxrow...)

    return(df)

def fun2(data, cutoff_score, cutoff_logitPD, slope1, Intercept1, CT):
    data1 = data.query('Totalscore<={}'.format(cutoff_score))
    data2 = data.query('Totalscore>{}'.format(cutoff_score))

    data1_sum_estPD = calsumPD(data1, slope1, Intercept1)
    data2_sum_estPD = CT*len(data) - data1_sum_estPD

    def _solve_slope2():

    slope2 = _solve_slope2(data2_sum_estPD)
    Intercept2 = cutoff_logitPD - slope2*cutoff_score
    
    def getmeasure():
    getmeasure(slope1,2, intercept1,2 data , meausre)

    pd_result={'slope1':slope1, 'Intercept1':Intercept1,'slope2':slope2, 'Intercept2':Intercept2，'measure_score':measure_score}
    return (pd_result)# -*- coding: utf-8 -*-
"""
Created on Fri Aug 10 11:35:38 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\calib")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import statsmodels.formula.api as smf
import seaborn as sns
import pickle
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import copy
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import scipy.stats as scistat
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping, ExtRating_mapping

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
CT = 0.0105
# load model setting
filehandler = open(r'..\spec\model_bf_calib.pkl','rb')
model = pickle.load(filehandler)


#%%


# make change to make paras comes from bin data ,but plot all data.
def LRplot(data_all, Intercept, slope):
  
    fig, ax = plt.subplots()
    ax.scatter(data_all.Totalscore,data_all.logitPD_frPDRR, s=25)    
    X_full_plot = np.linspace(-50,100,200)
    ax.plot(X_full_plot, X_full_plot*slope + Intercept, label="SingleLine")
    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()

def LRplot_mullines(data_all, pl_Intercept, pl_slope, pl_label):
  
    fig, ax = plt.subplots()
    ax.scatter(data_all.Totalscore,data_all.logitPD_frPDRR, s=25)    
    X_full_plot = np.linspace(-50,100,200)
    for i in range(len(pl_slope)):
        ax.plot(X_full_plot, X_full_plot*pl_slope[i] + pl_Intercept[i], label=pl_label[i])
    plt.xlabel('Total Score',color='b')   
    plt.ylabel('logit PD',color='b')
    legend = ax.legend(loc='upper left', shadow=True)
    ax2 = ax.twinx()
    ax2.scatter(data_all.Totalscore,data_all.logitPD_frPDRR, s=25)    
    pl_logitPD = data_all['logitPD_frPDRR'].unique()
    pl_logitPD.sort()
    pl_PDRR = list(np.arange(2,2+len(pl_logitPD)))
    plt.yticks(pl_logitPD, pl_PDRR)
    plt.ylabel('Final PDRR', color='r')
    plt.show()


def scorecard_single(data, Intercept, slope, ms_ver='new'):
    df = data.copy()
    
    if ms_ver=='old':
        low_pd = MS['old_low']
    else:
        low_pd = MS['new_low']

    df['fitted_logit_pd'] = Intercept + slope*df['Totalscore']
    df['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in df['fitted_logit_pd'] ]
    Ratings = []
    for i in df.iterrows():
        Ratings.append(sum(low_pd<=(i[1].fitted_pd)))
    df['fitted_PDRR'] = Ratings   

    return(df)


def get_intcp(data, CT, slope):
    df= data.copy()
    def _fun(Intercept):
        df['fitted_logit_pd'] = Intercept + slope*df['Totalscore']
        df['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in df['fitted_logit_pd'] ]
        return (df.fitted_pd.mean()-CT)

    intcp = fsolve(_fun, -5)
    return(intcp[0])






#%%
# load calibration data and calculate total score based on model setting
#dat = pd.read_pickle('norm_test_2017.pkl.xz')
dat = pd.read_pickle('norm_2010_2016.pkl.xz')
dat['quantscore'] = (model.quant_weight * dat[model.quant_factor].values).sum(axis=1)
dat['quantscore'] = 50*( dat['quantscore'] - model.quantmean) / model.quantstd
dat['qualiscore'] = (model.quali_weight * dat[model.quali_factor].values).sum(axis=1)
dat['qualiscore'] = 50*( dat['qualiscore'] - model.qualimean) / model.qualistd
dat['Totalscore'] = dat['quantscore']*model.quantweight + dat['qualiscore'] *model.qualiweight

dat_2017 = pd.read_pickle('norm_test_2017.pkl.xz')
dat_2017['quantscore'] = (model.quant_weight * dat_2017[model.quant_factor].values).sum(axis=1)
dat_2017['quantscore'] = 50*( dat_2017['quantscore'] - model.quantmean) / model.quantstd
dat_2017['qualiscore'] = (model.quali_weight * dat_2017[model.quali_factor].values).sum(axis=1)
dat_2017['qualiscore'] = 50*( dat_2017['qualiscore'] - model.qualimean) / model.qualistd
dat_2017['Totalscore'] = dat_2017['quantscore']*model.quantweight + dat_2017['qualiscore'] *model.qualiweight



# double check
print(SomersD(dat.Final_PD_Risk_Rating, dat.Totalscore))
print(SomersD(dat_2017.Final_PD_Risk_Rating, dat_2017.Totalscore))


#%%

pl_slope = list(np.linspace(0.01,0.06,200))
perf_table = pd.DataFrame()
for slope in pl_slope:
    Intercept = get_intcp(dat, CT, slope)
    df = scorecard_single(dat, Intercept, slope, ms_ver='old')
    stats = TMstats(df, 'fitted_PDRR', 'Final_PD_Risk_Rating', PDRR=range(1,16))
    stats.update({'SomersD':SomersD(df.Final_PD_Risk_Rating, df.fitted_PDRR)})
    stats.update({'Intercept':Intercept, 'slope':slope})
    D, pvalue = scistat.ks_2samp(df.Final_PD_Risk_Rating, df.fitted_PDRR)
    stats.update({'KS_stats':D})
    perf_table = perf_table.append(stats,ignore_index=True)

perf_table = perf_table[['Intercept','slope','SomersD','Match', 'Within_1', 'Within_2', 'Outside_5', 'KS_stats','Downgrade', 'Upgrade']]
perf_table['diff'] = perf_table['Downgrade'] - perf_table['Upgrade']
perf_table['existing_KS_stats'],_ = scistat.ks_2samp(df.Final_PD_Risk_Rating, df.Prelim_PD_Risk_Rating_Uncap)
perf_table.to_excel('perf_table.xlsx')

pl_slope = list(np.linspace(0.01,0.06,200))
perf_table_test_2017 = pd.DataFrame()
for slope in pl_slope:
    Intercept = get_intcp(dat, CT, slope)
    df = scorecard_single(dat_2017, Intercept, slope, ms_ver='new')
    stats = TMstats(df, 'fitted_PDRR', 'Final_PD_Risk_Rating', PDRR=range(1,16))
    stats.update({'SomersD':SomersD(df.Final_PD_Risk_Rating, df.fitted_PDRR)})
    stats.update({'Intercept':Intercept, 'slope':slope})
    D, pvalue = scistat.ks_2samp(df.Final_PD_Risk_Rating, df.fitted_PDRR)
    stats.update({'KS_stats':D})
    perf_table_test_2017 = perf_table_test_2017.append(stats,ignore_index=True)

perf_table_test_2017 = perf_table_test_2017[['Intercept','slope','SomersD','Match', 'Within_1', 'Within_2', 'Outside_5', 'KS_stats','Downgrade', 'Upgrade']]
perf_table_test_2017['diff'] = perf_table_test_2017['Downgrade'] - perf_table_test_2017['Upgrade']
perf_table_test_2017['existing_KS_stats'],_ = scistat.ks_2samp(df.Final_PD_Risk_Rating, df.Prelim_PD_Risk_Rating_Uncap)
perf_table_test_2017.to_excel('perf_table_test_2017.xlsx')



#%%
model.intercept1 = model.intercept2 = -5.05561066503429
model.slope1 = model.slope2 = 0.0238190954773869
model.cutoff = 99999999
model.model_name = 'CNI_LargeCorporate'
model.version = 1.0
#model.save(r'..\spec\model_af_calib.pkl')


#%% TM
prop_intcp = model.intercept1
prop_slope = model.slope1
df = scorecard_single(dat, prop_intcp, prop_slope, ms_ver='old')
#df = ExtRating_mapping(df)

df['fitted_PDRR_after_JBA'] = df['fitted_PDRR'] + df['RLA_Notches'] + df['Override_Action']
df['fitted_PDRR_after_JBA'] = df['fitted_PDRR_after_JBA'].clip(lower=1,upper=15)

CreateBenchmarkMatrix(df, 'in-sample.xlsx', 'TM',  'fitted_PDRR', 'Final_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(df, 'in-sample.xlsx', 'TM',  'fitted_PDRR', 'Prelim_PD_Risk_Rating_Uncap', PDRR=range(1,16))
print(SomersD(df['Final_PD_Risk_Rating'], df['fitted_PDRR']))
print(SomersD(df['Final_PD_Risk_Rating'], df['fitted_PDRR_after_JBA']))


CreateBenchmarkMatrix(df, 'in-sample.xlsx', 'TM_JBA',  'fitted_PDRR_after_JBA', 'Final_PD_Risk_Rating', PDRR=range(1,16))

#CreateBenchmarkMatrix(df, 'in-sample.xlsx', 'Final_Ext',  'Final_PD_Risk_Rating', 'ExternalRating',  PDRR=range(1,16))
#CreateBenchmarkMatrix(df, 'in-sample.xlsx', 'Prelim_Ext',  'Prelim_PD_Risk_Rating_Uncap', 'ExternalRating',  PDRR=range(1,16))
#CreateBenchmarkMatrix(df, 'in-sample.xlsx', 'New_Ext',  'fitted_PDRR', 'ExternalRating', PDRR=range(1,16))

CreateBenchmarkMatrix(df, 'in-sample.xlsx', 'Final_ExtPDRR',  'Final_PD_Risk_Rating', 'ExternalRating_PDRR',  PDRR=range(1,16))
CreateBenchmarkMatrix(df, 'in-sample.xlsx', 'Prelim_ExtPDRR',  'Prelim_PD_Risk_Rating_Uncap', 'ExternalRating_PDRR',  PDRR=range(1,16))
CreateBenchmarkMatrix(df, 'in-sample.xlsx', 'New_ExtPDRR',  'fitted_PDRR', 'ExternalRating_PDRR', PDRR=range(1,16))


#df2= df.dropna(subset=['ExternalRating'])
#print(SomersD(df2['ExternalRating'], df2['Final_PD_Risk_Rating']))
#print(SomersD(df2['ExternalRating'], df2['Prelim_PD_Risk_Rating_Uncap']))
#print(SomersD(df2['ExternalRating'], df2['fitted_PDRR']))



df3= df.dropna(subset=['ExternalRating_PDRR'])
print(SomersD(df3['ExternalRating_PDRR'], df3['Final_PD_Risk_Rating']))
print(SomersD(df3['ExternalRating_PDRR'], df3['Prelim_PD_Risk_Rating_Uncap']))
print(SomersD(df3['ExternalRating_PDRR'], df3['fitted_PDRR']))
'''
0.7690584446687939
0.6503047140404271
0.6933110293955093
'''





df_test = scorecard_single(dat_2017, prop_intcp, prop_slope, ms_ver='new')
#df_test = ExtRating_mapping(df_test)

df_test['fitted_PDRR_after_JBA'] = df_test['fitted_PDRR'] + df_test['RLA_Notches'] + df_test['Override_Action']
df_test['fitted_PDRR_after_JBA'] = df_test['fitted_PDRR_after_JBA'].clip(lower=1,upper=15)

CreateBenchmarkMatrix(df_test, 'out-of-sample.xlsx', 'TM',  'fitted_PDRR', 'Final_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(df_test, 'out-of-sample.xlsx', 'TM',  'fitted_PDRR', 'Prelim_PD_Risk_Rating_Uncap', PDRR=range(1,16))
print(SomersD(df_test['Final_PD_Risk_Rating'], df_test['fitted_PDRR']))
print(SomersD(df_test['Final_PD_Risk_Rating'], df_test['fitted_PDRR_after_JBA']))


CreateBenchmarkMatrix(df_test, 'out-of-sample.xlsx', 'TM_JBA', 'fitted_PDRR_after_JBA','Final_PD_Risk_Rating', PDRR=range(1,16))
#CreateBenchmarkMatrix(df_test, 'out-of-sample.xlsx', 'Final_Ext',  'Final_PD_Risk_Rating', 'ExternalRating',  PDRR=range(1,16))
#CreateBenchmarkMatrix(df_test, 'out-of-sample.xlsx', 'Prelim_Ext',  'Prelim_PD_Risk_Rating_Uncap', 'ExternalRating',  PDRR=range(1,16))
#CreateBenchmarkMatrix(df_test, 'out-of-sample.xlsx', 'New_Ext',  'fitted_PDRR', 'ExternalRating', PDRR=range(1,16))


CreateBenchmarkMatrix(df_test, 'out-of-sample.xlsx', 'Final_ExtPDRR',  'Final_PD_Risk_Rating', 'ExternalRating_PDRR',  PDRR=range(1,16))
CreateBenchmarkMatrix(df_test, 'out-of-sample.xlsx', 'Prelim_ExtPDRR',  'Prelim_PD_Risk_Rating_Uncap', 'ExternalRating_PDRR',  PDRR=range(1,16))
CreateBenchmarkMatrix(df_test, 'out-of-sample.xlsx', 'New_ExtPDRR',  'fitted_PDRR', 'ExternalRating_PDRR', PDRR=range(1,16))


#df_test2= df_test.dropna(subset=['ExternalRating'])
#print(SomersD(df_test2['ExternalRating'], df_test2['Final_PD_Risk_Rating']))
#print(SomersD(df_test2['ExternalRating'], df_test2['Prelim_PD_Risk_Rating_Uncap']))
#print(SomersD(df_test2['ExternalRating'], df_test2['fitted_PDRR']))


df_test3= df_test.dropna(subset=['ExternalRating_PDRR'])
print(SomersD(df_test3['ExternalRating_PDRR'], df_test3['Final_PD_Risk_Rating']))
print(SomersD(df_test3['ExternalRating_PDRR'], df_test3['Prelim_PD_Risk_Rating_Uncap']))
print(SomersD(df_test3['ExternalRating_PDRR'], df_test3['fitted_PDRR']))

'''
0.8272043974663343
0.6663629288859555
0.6751992355658881
'''




#%% plot
pl_Intercept = [-4.93683334709647, prop_intcp]
pl_slope = [0.020847537189529877, prop_slope]
pl_label = [ 'Naive calibration','Proposed calibration']
LRplot_mullines(dat, pl_Intercept, pl_slope, pl_label)







#%% industry seg analysis
df = NAICS_mapping(df)
df = MAUG_mapping(df)
df_test = NAICS_mapping(df_test)
df_test = MAUG_mapping(df_test)

def cal_uprate(data):
    return (data.fitted_PDRR < data.Final_PD_Risk_Rating).sum() / len(data)

def cal_downrate(data):
    return (data.fitted_PDRR > data.Final_PD_Risk_Rating).sum() / len(data)

def cal_updown_ratio(data):
    return (data.fitted_PDRR < data.Final_PD_Risk_Rating).sum() / (data.fitted_PDRR > data.Final_PD_Risk_Rating).sum()

def _sd(data):
    if len(data)<5:
        return np.nan
    else:
        try:
            return(SomersD(data.Final_PD_Risk_Rating, data.fitted_PDRR))
        except ZeroDivisionError:
            return np.nan

writer = pd.ExcelWriter('industry_seg.xlsx')

df_count = df.groupby('Industry_by_NAICS').count()['Totalscore']
df_sd = df.groupby('Industry_by_NAICS').apply(_sd)
df_finalpd = df.groupby('Industry_by_NAICS').mean()['PD_frPDRR']
df_fittedpd = df.groupby('Industry_by_NAICS').mean()['fitted_pd']
df_updown = df.groupby('Industry_by_NAICS').apply(cal_updown_ratio)

df2 = pd.concat([df_count,df_sd, df_finalpd, df_fittedpd, df_updown], axis=1)
df2.columns=['Count','SomersD','Avg_FinalPD','Avg_fittedPD','Upgrade/Downgrade ratio']
df2.to_excel(writer, 'in-sample')


df_test_count = df_test.groupby('Industry_by_NAICS').count()['Totalscore']
df_test_sd = df_test.groupby('Industry_by_NAICS').apply(_sd)
df_test_finalpd = df_test.groupby('Industry_by_NAICS').mean()['PD_frPDRR']
df_test_fittedpd = df_test.groupby('Industry_by_NAICS').mean()['fitted_pd']
df_test_updown = df_test.groupby('Industry_by_NAICS').apply(cal_updown_ratio)

df_test2 = pd.concat([df_test_count,df_test_sd, df_test_finalpd, df_test_fittedpd, df_test_updown], axis=1)
df_test2.columns=['Count','SomersD','Avg_FinalPD','Avg_fittedPD','Upgrade/Downgrade ratio']
df_test2.to_excel(writer, 'out-of-sample')
writer.save()

# Finance and Insurance breakdown
df_FI = df.query('Industry_by_NAICS=="Finance and Insurance"')
df_FI = df_FI[['MAUG','Industry_by_MAUG']]
df_FI.groupby('Industry_by_MAUG').count()
'''
                                                 MAUG
Industry_by_MAUG                                     
Auto and Auto Parts                                 5
Business Diversity Lending                          1
General Industries                                 30
Health Care                                         3
Placeholder for pending Utilities Latin America     8
Retail                                              1
'''

df_test_FI = df_test.query('Industry_by_NAICS=="Finance and Insurance"')
df_test_FI = df_test_FI[['MAUG','Industry_by_MAUG']]
df_test_FI.groupby('Industry_by_MAUG').count()
'''
                    MAUG
Industry_by_MAUG        
General Industries     4
Insurance              2
Technology             1
'''


#%% PDRR dist
writer = pd.ExcelWriter('PDRR_dist.xlsx')
df_count = df.groupby('Final_PD_Risk_Rating').count()['Totalscore']
df_updown = df.groupby('Final_PD_Risk_Rating').apply(cal_updown_ratio)

df2 = pd.concat([df_count, df_updown], axis=1)
df2.columns=['Count','Upgrade/Downgrade ratio']
df2.to_excel(writer, 'in-sample')

df_test_count = df_test.groupby('Final_PD_Risk_Rating').count()['Totalscore']
df_test_updown = df_test.groupby('Final_PD_Risk_Rating').apply(cal_updown_ratio)

df_test2 = pd.concat([df_test_count, df_test_updown], axis=1)
df_test2.columns=['Count','Upgrade/Downgrade ratio']
df_test2.to_excel(writer, 'out-of-sample')
writer.save()




#%%
import seaborn as sns

df_fr = (df['Final_PD_Risk_Rating'].value_counts(normalize=True)
        .rename('percentage')
        .mul(100)
        .reset_index()
        .sort_values('index'))
df_fr['sample'] = 'Calibration Sample'
df_test_fr = (df_test['Final_PD_Risk_Rating'].value_counts(normalize=True)
        .rename('percentage')
        .mul(100)
        .reset_index()
        .sort_values('index'))
df_test_fr['sample'] = '2017 Sample'
combo = pd.concat([df_fr,df_test_fr], axis=0)
combo.rename(columns={'index':'Final_PD_Risk_Rating'}, inplace=True)
sns.barplot(x="Final_PD_Risk_Rating", y="percentage",  hue="sample", data=combo)


# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 15:22:00 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata\raw2")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import pickle

def scorecard_single(data, Intercept, slope, ms_ver='new'):
    df = data.copy()
    
    if ms_ver=='old':
        low_pd = MS['old_low']
    else:
        low_pd = MS['new_low']

    df['fitted_logit_pd'] = Intercept + slope*df['Totalscore']
    df['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in df['fitted_logit_pd'] ]
    Ratings = []
    for i in df.iterrows():
        Ratings.append(sum(low_pd<=(i[1].fitted_pd)))
    df['fitted_PDRR'] = Ratings   

    return(df)


# combine the data from CASS
data1 = pd.read_excel('CI_Report_20180419.xlsx', sheetname='CustProfTable')
#data1.rename(columns={'RA Customer ID':'CUSTOMERID', 'STATEMENT ID':'statement_id',  'STATEMENT DATE':'Statement_Date'}, inplace=True)
data2 = pd.read_excel('CI_Report_20180419.xlsx', sheetname='CustFinancialFactor')

data = pd.concat([data1, data2], axis=1)
data.rename(columns={'Archive Date':'archive_date'}, inplace=True)
data.rename(columns={'Obligor Number':'OBLIGOR_NUMBER'}, inplace=True)

# grab some field from current CnI data
prod = pd.read_pickle(r'..\data_201006_201712_addBranch_3_jn_withCIF.pkl.xz')
prod = prod.query('DataPeriod=="Prod" or DataPeriod=="Prod_Branch"')
prod = prod.drop_duplicates(subset=['CUSTOMERID','archive_date'])

cols_need =[
'quant1', 'quant2_COP', 'quant2_ACF', 'quant2', 'quant3', 'quant4', 'quant5', 'qual1', 'qual2', 'qual3',\
 'qual4', 'Prelim_PD_Risk_Rating_Uncap', 'Final_PD_Risk_Rating', 'RLA_Notches','Override_Action','Underwriter_Guideline']

prod = prod[['CUSTOMERID','archive_date']+cols_need]
prod.reset_index(drop=True, inplace=True)

# merge 
new = pd.merge(data, prod, on=['CUSTOMERID','archive_date'], how='inner')

os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
gcrrcr = pd.read_pickle(r'..\newdata\Ming_data\gcr_rcr.pkl.xz')
gcrrcr['approved'] = 1

new2 = pd.merge(new, gcrrcr, on=['CUSTOMERID','Archive ID'], how='left')
new2.approved.sum()
new2 = new2.query('approved==1')





def findname(target, ps):
    pl = ps.tolist()
    for name in pl:
        if target.lower() in name.lower():
            print('yes and the name is '+name)
            break
    else:
        print('No '+target)
        
#%%
pl_target=[
 'general motor','apple inc','dell inc', 'Ford Motor Company','Ge Company','Hewlett-Packard Company',\
 'International Business Machines Corporation','Cisco Systems Inc','Xerox','Emc Corporation' ]


for target in pl_target:
    findname(target, new['Customer Long Name'])

for target in pl_target:
    findname(target, new2['Customer Long Name'])
       
    
#%%
pl_CPPD_name = []
for target in pl_target:
    pl = new['Customer Long Name'].tolist()
    for name in pl:
        if target.lower() in name.lower():
            pl_CPPD_name.append(name)
            break
pl_CPPD_name[4] = 'Ge Company'

df=pd.DataFrame()
for name in pl_CPPD_name:
    temp = new[new['Customer Long Name']==name]
    df = df.append(temp)


df2 = pd.merge(df, gcrrcr, on=['CUSTOMERID','Archive ID'], how='left')
df2.approved.sum()
#15
df2.to_pickle(r'calib\CPPD_df.pkl.xz')
df2.to_excel(r'calib\CPPD_df.xlsx')
# send to Jack to attach new quali factors

#%% build quant factos:
df_CPPD = pd.read_excel(r'calib\CPPD_df_jn.xlsx')
df_CPPD['prof@EBITDA_to_NS'] = df_CPPD['EBITDA'] / df_CPPD['Net Sales']
df_CPPD['cf@TD_to_EBITDA']  = df_CPPD['Total Debt'] / df_CPPD[ 'EBITDA']
df_CPPD['size@Total Assets'] = df_CPPD['Total Assets']
df_CPPD['bs@TD_to_Capt']    = df_CPPD['Total Debt'] / df_CPPD['Capitalization']
df_CPPD['ds@EBITDA_to_IE']  = df_CPPD['EBITDA'] / df_CPPD['Interest Expense']

df_CPPD['size@EBITDA'] =  df_CPPD['EBITDA']
df_CPPD['size@Capitalization'] =  df_CPPD['Capitalization']
df_CPPD['ds@Interest Expense'] = df_CPPD['Interest Expense']

#%% build quali factos:
pl_qualifactors=[ 'qual1', 'qual2',  'Management_Quality','qual4', 'Access_Outside_Capital']



filehandler = open('model_LC_before_calib.pkl','rb')
model = pickle.load(filehandler)

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')

#%%
cni_CPPD = MFA(df_CPPD, model, quant_only=False)

dat = cni_CPPD.normdata.copy()

dat['quantscore'] = (model.quant_weight * dat[model.quant_factor].values).sum(axis=1)
dat['quantscore'] = 50*( dat['quantscore'] - model.quantmean) / model.quantstd
dat['qualiscore'] = (model.quali_weight * dat[model.quali_factor].values).sum(axis=1)
dat['qualiscore'] = 50*( dat['qualiscore'] - model.qualimean) / model.qualistd
dat['Totalscore'] = dat['quantscore']*model.quantweight + dat['qualiscore'] *model.qualiweight



prop_intcp = -5.10302054407123
prop_slope = 0.0280904522613065
df = scorecard_single(dat, prop_intcp, prop_slope, ms_ver='old')#
CreateBenchmarkMatrix(df, 'CPPD.xlsx', 'TM',  'fitted_PDRR', 'Final_PD_Risk_Rating', PDRR=range(1,16))


cppd = df[['Final_PD_Risk_Rating','fitted_PDRR']]


#%%
pl_names = ['General Motors Company',
 'Ford Motor Company',
 'Apple Inc.',
 'Ge Company',
 'Hewlett-Packard Company',
 'International Business Machines Corporation',
 'Dell Inc.',
 'Cisco Systems Inc',
 'Emc Corporation',
 'Xerox Corporation']


df.loc[df['Customer Long Name']==pl_names[0], ['archive_date','Customer Long Name','Final_PD_Risk_Rating','fitted_PDRR']]
df.loc[df['Customer Long Name']==pl_names[1], ['archive_date','Customer Long Name','Final_PD_Risk_Rating','fitted_PDRR']]
df.loc[df['Customer Long Name']==pl_names[2], ['archive_date','Customer Long Name','Final_PD_Risk_Rating','fitted_PDRR']]
df.loc[df['Customer Long Name']==pl_names[3], ['archive_date','Customer Long Name','Final_PD_Risk_Rating','fitted_PDRR']]
df.loc[df['Customer Long Name']==pl_names[4], ['archive_date','Customer Long Name','Final_PD_Risk_Rating','fitted_PDRR']]
df.loc[df['Customer Long Name']==pl_names[5], ['archive_date','Customer Long Name','Final_PD_Risk_Rating','fitted_PDRR']]
df.loc[df['Customer Long Name']==pl_names[6], ['archive_date','Customer Long Name','Final_PD_Risk_Rating','fitted_PDRR']]
df.loc[df['Customer Long Name']==pl_names[7], ['archive_date','Customer Long Name','Final_PD_Risk_Rating','fitted_PDRR']]
df.loc[df['Customer Long Name']==pl_names[8], ['archive_date','Customer Long Name','Final_PD_Risk_Rating','fitted_PDRR']]
df.loc[df['Customer Long Name']==pl_names[9], ['archive_date','Customer Long Name','Final_PD_Risk_Rating','fitted_PDRR']]# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 14:07:53 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import statsmodels.formula.api as smf
import seaborn as sns
import pickle
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import copy
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import scipy.stats as scistat
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping, ExtRating_mapping

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
# load model setting
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)


def scorecard_single(data, Intercept, slope, ms_ver='new'):
    df = data.copy()
    
    if ms_ver=='old':
        low_pd = MS['old_low']
    else:
        low_pd = MS['new_low']

    df['fitted_logit_pd'] = Intercept + slope*df['Totalscore']
    df['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in df['fitted_logit_pd'] ]
    Ratings = []
    for i in df.iterrows():
        Ratings.append(sum(low_pd<=(i[1].fitted_pd)))
    df['fitted_PDRR'] = Ratings   

    return(df)




#%%
dat = pd.read_pickle(r'..\calib\norm_2010_2016.pkl.xz')
dat['quantscore'] = (model.quant_weight * dat[model.quant_factor].values).sum(axis=1)
dat['quantscore'] = 50*( dat['quantscore'] - model.quantmean) / model.quantstd
dat['qualiscore'] = (model.quali_weight * dat[model.quali_factor].values).sum(axis=1)
dat['qualiscore'] = 50*( dat['qualiscore'] - model.qualimean) / model.qualistd
dat['Totalscore'] = dat['quantscore']*model.quantweight + dat['qualiscore'] *model.qualiweight

dat_2017 = pd.read_pickle(r'..\calib\norm_test_2017.pkl.xz')
dat_2017['quantscore'] = (model.quant_weight * dat_2017[model.quant_factor].values).sum(axis=1)
dat_2017['quantscore'] = 50*( dat_2017['quantscore'] - model.quantmean) / model.quantstd
dat_2017['qualiscore'] = (model.quali_weight * dat_2017[model.quali_factor].values).sum(axis=1)
dat_2017['qualiscore'] = 50*( dat_2017['qualiscore'] - model.qualimean) / model.qualistd
dat_2017['Totalscore'] = dat_2017['quantscore']*model.quantweight + dat_2017['qualiscore'] *model.qualiweight



# double check
print(SomersD(dat.Final_PD_Risk_Rating, dat.Totalscore))
print(SomersD(dat_2017.Final_PD_Risk_Rating, dat_2017.Totalscore))




#%% In-sample TM with Benchmark
df = scorecard_single(dat, model.intercept1, model.slope1, ms_ver='old')
df['fitted_PDRR_after_JBA'] = df['fitted_PDRR'] + df['RLA_Notches'] + df['Override_Action']
df['fitted_PDRR_after_JBA'] = df['fitted_PDRR_after_JBA'].clip(lower=1,upper=15)
df['Prelim_PD_Risk_Rating'] = df['Prelim_PD_Risk_Rating_Uncap'] 
#df = ExtRating_mapping(df)
#  S&P
CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'fitted_PDRR',  'fitted_PDRR', 'ExternalRating_PDRR' , PDRR=range(1,16))
CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'fitted_PDRR_JBA',  'fitted_PDRR_after_JBA', 'ExternalRating_PDRR', PDRR=range(1,16))
CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'Prelim',  'Prelim_PD_Risk_Rating', 'ExternalRating_PDRR' , PDRR=range(1,16))
CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'Final', 'Final_PD_Risk_Rating', 'ExternalRating_PDRR' , PDRR=range(1,16))

#CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'fitted_PDRR_own',  'fitted_PDRR', 'ExternalRating' , PDRR=range(1,16))
#CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'fitted_PDRR_JBA_own',  'fitted_PDRR_after_JBA', 'ExternalRating', PDRR=range(1,16))
#CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'Prelim_own',  'Prelim_PD_Risk_Rating', 'ExternalRating' , PDRR=range(1,16))
#CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'Final_own', 'Final_PD_Risk_Rating', 'ExternalRating' , PDRR=range(1,16))


df2= df.dropna(subset=['ExternalRating_PDRR'])
print(SomersD(df2['ExternalRating_PDRR'], df2['fitted_PDRR']))
print(SomersD(df2['ExternalRating_PDRR'], df2['fitted_PDRR_after_JBA']))
print(SomersD(df2['ExternalRating_PDRR'], df2['Prelim_PD_Risk_Rating']))
print(SomersD(df2['ExternalRating_PDRR'], df2['Final_PD_Risk_Rating']))
'''
0.6933110293955093
0.7172238966551462
0.6503047140404271
0.7690584446687939
'''


#df3= df.dropna(subset=['ExternalRating'])
#print(SomersD(df3['ExternalRating'], df3['fitted_PDRR']))
#print(SomersD(df3['ExternalRating'], df3['fitted_PDRR_after_JBA']))
#print(SomersD(df3['ExternalRating'], df3['Prelim_PD_Risk_Rating']))
#print(SomersD(df3['ExternalRating'], df3['Final_PD_Risk_Rating']))




#%% CreditBenchmark
CB = pd.read_excel(r'..\..\newdata\CreditBenchmark\Consolidated Credit Benchmark PD 08312018.xlsx')

newdf = pd.merge(df, CB, on=['CUSTOMERID'], how='left')
newdf.dropna(subset=['CB_Effective_Date'], inplace=True)
newdf = newdf.query('timestamp<CB_Effective_Date')
newdf.sort_values(by=['CUSTOMERID','timestamp'], inplace=True)
newdf.drop_duplicates(subset=['CUSTOMERID','CB_Effective_Date'], keep='last', inplace=True)
#a = newdf[['CUSTOMERID','timestamp','CB_Effective_Date']]
Ratings = []
for i in newdf.iterrows():
    Ratings.append(sum(model.MS['old_low']<=(i[1].Risk_Entity_PD_Average)))
newdf['CB_Ratings'] = Ratings


# 
CreateBenchmarkMatrix(newdf, 'BM_CB.xlsx', 'fitted_PDRR',  'fitted_PDRR', 'CB_Ratings' , PDRR=range(1,16))
CreateBenchmarkMatrix(newdf, 'BM_CB.xlsx', 'fitted_PDRR_JBA',  'fitted_PDRR_after_JBA', 'CB_Ratings', PDRR=range(1,16))
CreateBenchmarkMatrix(newdf, 'BM_CB.xlsx', 'Prelim',  'Prelim_PD_Risk_Rating', 'CB_Ratings' , PDRR=range(1,16))
CreateBenchmarkMatrix(newdf, 'BM_CB.xlsx', 'Final', 'Final_PD_Risk_Rating', 'CB_Ratings' , PDRR=range(1,16))


newdf2= newdf.dropna(subset=['CB_Ratings'])
print(SomersD(newdf2['CB_Ratings'], newdf2['fitted_PDRR']))
print(SomersD(newdf2['CB_Ratings'], newdf2['fitted_PDRR_after_JBA']))
print(SomersD(newdf2['CB_Ratings'], newdf2['Prelim_PD_Risk_Rating']))
print(SomersD(newdf2['CB_Ratings'], newdf2['Final_PD_Risk_Rating']))

'''
0.6035347675041485
0.6062654966699064
0.600339901623955
0.7298741770733912
'''



#%%
CreateBenchmarkMatrix(df, 'CPPD_extra_TM.xlsx', 'fitted_vs_Final',  'fitted_PDRR', 'Final_PD_Risk_Rating' , PDRR=range(1,16))
CreateBenchmarkMatrix(df, 'CPPD_extra_TM.xlsx', 'Prelim_vs_Final',  'Prelim_PD_Risk_Rating', 'Final_PD_Risk_Rating' , PDRR=range(1,16))
print(SomersD(df['Final_PD_Risk_Rating'], df['fitted_PDRR']))
print(SomersD(df['Final_PD_Risk_Rating'], df['Prelim_PD_Risk_Rating']))
'''
0.7195750255126443
0.8277613585993182
'''
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 14:07:53 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import statsmodels.formula.api as smf
import seaborn as sns
import pickle
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import copy
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import scipy.stats as scistat
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping, ExtRating_mapping

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
# load model setting
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)


def scorecard_single(data, Intercept, slope, ms_ver='new'):
    df = data.copy()
    
    if ms_ver=='old':
        low_pd = MS['old_low']
    else:
        low_pd = MS['new_low']

    df['fitted_logit_pd'] = Intercept + slope*df['Totalscore']
    df['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in df['fitted_logit_pd'] ]
    Ratings = []
    for i in df.iterrows():
        Ratings.append(sum(low_pd<=(i[1].fitted_pd)))
    df['fitted_PDRR'] = Ratings   

    return(df)




#%%
dat_2017 = pd.read_pickle(r'..\calib\norm_test_2017.pkl.xz')
dat_2017['quantscore'] = (model.quant_weight * dat_2017[model.quant_factor].values).sum(axis=1)
dat_2017['quantscore'] = 50*( dat_2017['quantscore'] - model.quantmean) / model.quantstd
dat_2017['qualiscore'] = (model.quali_weight * dat_2017[model.quali_factor].values).sum(axis=1)
dat_2017['qualiscore'] = 50*( dat_2017['qualiscore'] - model.qualimean) / model.qualistd
dat_2017['Totalscore'] = dat_2017['quantscore']*model.quantweight + dat_2017['qualiscore'] *model.qualiweight


# double check
print(SomersD(dat_2017.Final_PD_Risk_Rating, dat_2017.Totalscore))




#%% Out-sample TM with Benchmark
df = scorecard_single(dat_2017, model.intercept1, model.slope1, ms_ver='new') # new version of masterscale
df['fitted_PDRR_after_JBA'] = df['fitted_PDRR'] + df['RLA_Notches'] + df['Override_Action']
df['fitted_PDRR_after_JBA'] = df['fitted_PDRR_after_JBA'].clip(lower=1,upper=15)
df['Prelim_PD_Risk_Rating'] = df['Prelim_PD_Risk_Rating_Uncap'] 


#  S&P
CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'fitted_PDRR',  'fitted_PDRR', 'ExternalRating_PDRR' , PDRR=range(1,16))
CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'fitted_PDRR_JBA',  'fitted_PDRR_after_JBA', 'ExternalRating_PDRR', PDRR=range(1,16))
CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'Prelim',  'Prelim_PD_Risk_Rating', 'ExternalRating_PDRR' , PDRR=range(1,16))
CreateBenchmarkMatrix(df, 'BM_SP.xlsx', 'Final', 'Final_PD_Risk_Rating', 'ExternalRating_PDRR' , PDRR=range(1,16))


df2= df.dropna(subset=['ExternalRating_PDRR'])
print(SomersD(df2['ExternalRating_PDRR'], df2['fitted_PDRR']))
print(SomersD(df2['ExternalRating_PDRR'], df2['fitted_PDRR_after_JBA']))
print(SomersD(df2['ExternalRating_PDRR'], df2['Prelim_PD_Risk_Rating']))
print(SomersD(df2['ExternalRating_PDRR'], df2['Final_PD_Risk_Rating']))
'''
0.6751992355658881
0.739787022351817
0.6663629288859555
0.8272043974663343
'''



#%% CreditBenchmark
CB = pd.read_excel(r'..\..\newdata\CreditBenchmark\Consolidated Credit Benchmark PD 08312018.xlsx')

newdf = pd.merge(df, CB, on=['CUSTOMERID'], how='left')
newdf.dropna(subset=['CB_Effective_Date'], inplace=True)
# remove CB rating if it happened before timestamp(archive_date)
newdf = newdf.query('timestamp<CB_Effective_Date') 
# drop duplicated CB ratings and keep the one which is closest to the timestamp 
newdf.sort_values(by=['CUSTOMERID','timestamp','CB_Effective_Date'], inplace=True)
newdf.drop_duplicates(subset=['CUSTOMERID','timestamp'], keep='first', inplace=True)


Ratings = []
for i in newdf.iterrows():
    Ratings.append(sum(model.MS['new_low']<=(i[1].Risk_Entity_PD_Average)))  # new version of masterscale
newdf['CB_Ratings'] = Ratings


# 
CreateBenchmarkMatrix(newdf, 'BM_CB.xlsx', 'fitted_PDRR',  'fitted_PDRR', 'CB_Ratings' , PDRR=range(1,16))
CreateBenchmarkMatrix(newdf, 'BM_CB.xlsx', 'fitted_PDRR_JBA',  'fitted_PDRR_after_JBA', 'CB_Ratings', PDRR=range(1,16))
CreateBenchmarkMatrix(newdf, 'BM_CB.xlsx', 'Prelim',  'Prelim_PD_Risk_Rating', 'CB_Ratings' , PDRR=range(1,16))
CreateBenchmarkMatrix(newdf, 'BM_CB.xlsx', 'Final', 'Final_PD_Risk_Rating', 'CB_Ratings' , PDRR=range(1,16))


newdf2= newdf.dropna(subset=['CB_Ratings'])
print(SomersD(newdf2['CB_Ratings'], newdf2['fitted_PDRR']))
print(SomersD(newdf2['CB_Ratings'], newdf2['fitted_PDRR_after_JBA']))
print(SomersD(newdf2['CB_Ratings'], newdf2['Prelim_PD_Risk_Rating']))
print(SomersD(newdf2['CB_Ratings'], newdf2['Final_PD_Risk_Rating']))

'''
0.6534855757153527
0.7000961284034312
0.6560076902722745
0.810369139768019
'''




# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:25:09 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix
import xlwings as xw

def PDRR_Matrix(frm,to,frm_lab,to_lab):
    frm.name='frm'
    to.name='to'

    
    
    n=len(frm)
    n0=((frm-to)==0).sum() 
    n1=(abs(frm-to)<=1).sum()
    n2=(abs(frm-to)<=2).sum()
    s1=((frm-to)>0).sum()
    s2=((frm-to)<0).sum()
    
    tmp_dt=pd.concat([frm, to], axis=1).reset_index()
#     print(tmp_dt)
    for i in range(1,16):
        for j in range(1,16):
            tmp_dt=tmp_dt.append({'frm':i,'to':j,'index':None},ignore_index=True)
#     print(tmp_dt)

    f=lambda x:x.count()                                     
    ridx=['frm']                          
    cidx=['to']                                                       
    tmp_tbl=tmp_dt.pivot_table(index=ridx,columns=cidx,values='index',aggfunc=f)
    tmp_tbl=tmp_tbl.applymap(lambda x:x if x>0 else np.nan)    
    import xlwings as xw
    from xlwings import constants
    wb = xw.Book()  # this will create a new workbook
    sht=wb.sheets['Sheet1']
    offset='C3'
    sht.range(offset).value = tmp_tbl
    sht[offset].value='PDRR'

    x0=offset[0]
    y0=int(offset[1])
    sht[chr(ord(x0))+str(y0+16)].column_width
    sht[chr(ord(x0))+str(y0+16)].value='Total'
    sht[chr(ord(x0)+16)+str(y0)].value='Total'
    sht[chr(ord(x0))+str(y0+16)].api.Font.Bold=True
    sht[chr(ord(x0)+16)+str(y0)].api.Font.Bold=True
    
    e=chr(ord(x0)-1)+str(y0)+':'+chr(ord(x0)-1)+str(y0+16)
    sht[e].api.MergeCells=True
    sht[e].api.VerticalAlignment = constants.VAlign.xlVAlignCenter
    sht[e].api.Orientation = constants.Orientation.xlUpward
    sht[e].value=frm_lab
    sht[e].api.Font.Bold=True
    sht[e].column_width=3
    
    e=chr(ord(x0))+str(y0-1)+':'+chr(ord(x0)+16)+str(y0-1)
    sht[e].api.MergeCells=True
    sht[e].api.HorizontalAlignment = constants.HAlign.xlHAlignCenter
    sht[e].value=to_lab
    sht[e].api.Font.Bold=True
    
    for i in range(1,16):
        sht[chr(ord(x0) + 16)+str(y0+i)].value='=sum('+chr(ord(x0) + 1)+str(y0+i)+':'+chr(ord(x0) + 15)+str(y0+i)+')'
        sht[chr(ord(x0) + 16)+str(y0+i)].api.Font.Bold=True
        sht[chr(ord(x0))+str(y0+i)].api.Font.Bold=True
    for i in range(1,16):
        sht[chr(ord(x0) + i)+str(y0+16)].value='=sum('+chr(ord(x0) + i)+str(y0+1)+':'+chr(ord(x0) + i)+str(y0+15)+')'
        sht[chr(ord(x0) + i)+str(y0+16)].api.Font.Bold=True
        sht[chr(ord(x0) + i)+str(y0)].api.Font.Bold=True

    sht[chr(ord(x0) + 16)+str(y0+16)].value='=sum('+chr(ord(x0) + 16)+str(y0+1)+':'+chr(ord(x0) + 16)+str(y0+15)+')'
    sht[chr(ord(x0) + 16)+str(y0+16)].api.Font.Bold=True

    for i in range(1,16):
        sht[chr(ord(x0) + i)+str(y0+i)].color=(255, 255, 0)
    for i in range(1,15):
        sht[chr(ord(x0)+1 + i)+str(y0+i)].color=(255, 255, 220)
        sht[chr(ord(x0) + i)+str(y0+1+i)].color=(255, 255, 220)
    for i in range(1,14):
        sht[chr(ord(x0)+2 + i)+str(y0+i)].color=(255, 255, 220)
        sht[chr(ord(x0) + i)+str(y0+2+i)].color=(255, 255, 220)
    for i in range(1,13):
        sht[chr(ord(x0)+3 + i)+str(y0+i)].color=(252, 165, 35)
        sht[chr(ord(x0) + i)+str(y0+3+i)].color=(252, 165, 35)

    sht[chr(ord(x0) + 13)+str(y0+18)].value='Count'  
    sht[chr(ord(x0) + 14)+str(y0+18)].value='(%)'  
    sht[chr(ord(x0) + 13)+str(y0+18)].api.HorizontalAlignment = constants.HAlign.xlHAlignCenter
    sht[chr(ord(x0) + 14)+str(y0+18)].api.HorizontalAlignment = constants.HAlign.xlHAlignCenter
    sht[chr(ord(x0) + 13)+str(y0+18)].api.Font.Bold=True 
    sht[chr(ord(x0) + 14)+str(y0+18)].api.Font.Bold=True  

    sht[chr(ord(x0) + 12)+str(y0+19)].value='Exact Match'    
    sht[chr(ord(x0) + 12)+str(y0+20)].value='Within One Notch'  
    sht[chr(ord(x0) + 12)+str(y0+21)].value='Within Two Notches'      
    sht[chr(ord(x0) + 12)+str(y0+19)].api.Font.Bold=True   
    sht[chr(ord(x0) + 12)+str(y0+20)].api.Font.Bold=True  
    sht[chr(ord(x0) + 12)+str(y0+21)].api.Font.Bold=True
    sht[chr(ord(x0) + 12)+str(y0+19)].api.HorizontalAlignment = constants.HAlign.xlHAlignRight  
    sht[chr(ord(x0) + 12)+str(y0+20)].api.HorizontalAlignment = constants.HAlign.xlHAlignRight 
    sht[chr(ord(x0) + 12)+str(y0+21)].api.HorizontalAlignment = constants.HAlign.xlHAlignRight

    sht[chr(ord(x0) + 6)+str(y0+18)].value='Count'  
    sht[chr(ord(x0) + 7)+str(y0+18)].value='(%)'  
    sht[chr(ord(x0) + 6)+str(y0+18)].api.HorizontalAlignment = constants.HAlign.xlHAlignCenter 
    sht[chr(ord(x0) + 7)+str(y0+18)].api.HorizontalAlignment = constants.HAlign.xlHAlignCenter
    sht[chr(ord(x0) + 6)+str(y0+18)].api.Font.Bold=True 
    sht[chr(ord(x0) + 7)+str(y0+18)].api.Font.Bold=True  

    sht[chr(ord(x0) + 13)+str(y0+19)].value=n0    
    sht[chr(ord(x0) + 13)+str(y0+20)].value=n1  
    sht[chr(ord(x0) + 13)+str(y0+21)].value=n2  

    sht[chr(ord(x0) + 14)+str(y0+19)].value=n0/n    
    sht[chr(ord(x0) + 14)+str(y0+20)].value=n1/n  
    sht[chr(ord(x0) + 14)+str(y0+21)].value=n2/n  
    sht[chr(ord(x0) + 14)+str(y0+19)].number_format = '0.0%'  
    sht[chr(ord(x0) + 14)+str(y0+20)].number_format = '0.0%'
    sht[chr(ord(x0) + 14)+str(y0+21)].number_format = '0.0%'

    sht[chr(ord(x0)+5)+str(y0+19)].value='Exact Match'    
    sht[chr(ord(x0)+5)+str(y0+20)].value='Upgrade'  
    sht[chr(ord(x0)+5)+str(y0+21)].value='Downgrade'  
    sht[chr(ord(x0)+5)+str(y0+22)].value='Total'   
    sht[chr(ord(x0)+5)+str(y0+19)].api.Font.Bold=True   
    sht[chr(ord(x0)+5)+str(y0+20)].api.Font.Bold=True  
    sht[chr(ord(x0)+5)+str(y0+21)].api.Font.Bold=True
    sht[chr(ord(x0)+5)+str(y0+22)].api.Font.Bold=True
    sht[chr(ord(x0)+5)+str(y0+19)].api.HorizontalAlignment = constants.HAlign.xlHAlignRight
    sht[chr(ord(x0)+5)+str(y0+20)].api.HorizontalAlignment = constants.HAlign.xlHAlignRight
    sht[chr(ord(x0)+5)+str(y0+21)].api.HorizontalAlignment = constants.HAlign.xlHAlignRight
    sht[chr(ord(x0)+5)+str(y0+22)].api.HorizontalAlignment = constants.HAlign.xlHAlignRight

    sht[chr(ord(x0) + 6)+str(y0+19)].value=n0    
    sht[chr(ord(x0) + 6)+str(y0+20)].value=s1  
    sht[chr(ord(x0) + 6)+str(y0+21)].value=s2  
    sht[chr(ord(x0) + 6)+str(y0+22)].value=n 

    sht[chr(ord(x0) + 7)+str(y0+19)].value=n0/n    
    sht[chr(ord(x0) + 7)+str(y0+20)].value=s1/n  
    sht[chr(ord(x0) + 7)+str(y0+21)].value=s2/n  
    sht[chr(ord(x0) + 7)+str(y0+22)].value=n/n  

    sht[chr(ord(x0) + 7)+str(y0+19)].number_format = '0.0%'    
    sht[chr(ord(x0) + 7)+str(y0+20)].number_format = '0.0%' 
    sht[chr(ord(x0) + 7)+str(y0+21)].number_format = '0.0%' 
    sht[chr(ord(x0) + 7)+str(y0+22)].number_format = '0%' 

    size=4
    rng_list=[
        chr(ord(x0))+str(y0)+':'+chr(ord(x0))+str(y0+16)
    ,chr(ord(x0)+16)+str(y0)+':'+chr(ord(x0)+16)+str(y0+16)
    ,chr(ord(x0))+str(y0)+':'+chr(ord(x0)+16)+str(y0)
    ,chr(ord(x0))+str(y0+16)+':'+chr(ord(x0)+16)+str(y0+16)
    ]
    
    for e in range(1,16):
        sht[chr(ord(x0)+e)+str(y0)].column_width=6

    for e in rng_list:
        rng=sht[e].api
        rng.Borders(1).Weight=size
    #     rng.api.Borders(1).Color=(255, 0, 0)
        rng.Borders(2).Weight=size
        rng.Borders(3).Weight=size
        rng.Borders(4).Weight=size
        rng.HorizontalAlignment = constants.HAlign.xlHAlignCenter
#         rng.column_width=6
#         .column_width=3

#%%
dat = pd.read_excel(r'Holdout_sampel_CPPD_requested.xlsx')

'''
'New_Primary_PDRR',
'External_Rating',
'Current_Preliminary_PDRR',
'Current_Final_PDRR',
'where_to_book',
'''
dat_Bank = dat.query('where_to_book=="Bank"')
dat_Branch = dat.query('where_to_book=="Branch"')



#%%
PDRR_Matrix(dat['Current_Preliminary_PDRR'], dat['New_Primary_PDRR'], 'Current_Preliminary_PDRR','New_Primary_PDRR')
PDRR_Matrix(dat['Current_Final_PDRR'], dat['New_Primary_PDRR'], 'Current_Final_PDRR','New_Primary_PDRR')
dat.dropna(subset=['External_Rating'], inplace=True)
PDRR_Matrix(dat['External_Rating'], dat['New_Primary_PDRR'], 'External_Rating','New_Primary_PDRR')
PDRR_Matrix(dat['External_Rating'], dat['Current_Preliminary_PDRR'], 'External_Rating','Current_Preliminary_PDRR')


#%%

PDRR_Matrix(dat_Branch['Current_Preliminary_PDRR'], dat_Branch['New_Primary_PDRR'], 'Current_Preliminary_PDRR','New_Primary_PDRR')
PDRR_Matrix(dat_Branch['Current_Final_PDRR'], dat_Branch['New_Primary_PDRR'], 'Current_Final_PDRR','New_Primary_PDRR')
dat_Branch.dropna(subset=['External_Rating'], inplace=True)
PDRR_Matrix(dat_Branch['External_Rating'], dat_Branch['New_Primary_PDRR'], 'External_Rating','New_Primary_PDRR')
PDRR_Matrix(dat_Branch['External_Rating'], dat_Branch['Current_Preliminary_PDRR'], 'External_Rating','Current_Preliminary_PDRR')


#%%

PDRR_Matrix(dat_Bank['Current_Preliminary_PDRR'], dat_Bank['New_Primary_PDRR'], 'Current_Preliminary_PDRR','New_Primary_PDRR')
PDRR_Matrix(dat_Bank['Current_Final_PDRR'], dat_Bank['New_Primary_PDRR'], 'Current_Final_PDRR','New_Primary_PDRR')
dat_Bank.dropna(subset=['External_Rating'], inplace=True)
PDRR_Matrix(dat_Bank['External_Rating'], dat_Bank['New_Primary_PDRR'], 'External_Rating','New_Primary_PDRR')
PDRR_Matrix(dat_Bank['External_Rating'], dat_Bank['Current_Preliminary_PDRR'], 'External_Rating','Current_Preliminary_PDRR')

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:25:09 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')

from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import normalization, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import getTotalscore, getPDRR, getTM
import pickle
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping, ExtRating_mapping

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)

data_train = pd.read_pickle(r'..\MFA\train_2016.pkl.xz')
cols=[
 'CONM',
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'size@EBITDA', 'size@Capitalization', 'ds@Interest Expense',
 'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital',
 'Override_Action',
 'RLA_Notches',
 'ExtRating',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Underwriter_Guideline',
 'NAICS',
 'NAICS_Cd',
 'dataset',
 'def_flag',
 'L_DATE_OF_DEFAULT'
 ]
dat = data_train[cols].copy()
dat.dropna(subset=model.quali_factor, how='any', inplace=True)
# log trans
dat['size@Total Assets'] = np.log(1+dat['size@Total Assets'])
# fill inf
finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        dat[factor] = dat[factor].clip(np.nanmin(dat[factor][dat[factor] != -np.inf]), np.nanmax(dat[factor][dat[factor] != np.inf]))
# get existing model's Final PDRR implied PD and logit PD
dat = PD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')
dat = logitPD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')



#%%

train_mfa = getPDRR(dat, model, ms_ver='old')
dfdef = train_mfa.query('def_flag==1')
dfdef.to_excel(r'def\dfdef.xlsx')


#%% pseudo def
from PDScorecardTool.Process import buildpseudodef


psu_data = buildpseudodef(train_mfa, def_flag='def_flag', PDRR='Final_PD_Risk_Rating', pseudodef_PDRR=[13,14,15])
psudfdef = psu_data.query('def_flag==1')

CreateBenchmarkMatrix(psudfdef, 'pseudodef_TM.xlsx','TM','Ratings','Final_PD_Risk_Rating',  PDRR=range(1,16) )

psudfdef.to_excel(r'def\psudfdef.xlsx')# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 15:22:00 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')

from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import normalization, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import getTotalscore, getPDRR, getTM
import pickle
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping, ExtRating_mapping
from PDScorecardTool.Process import SomersD


MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)

os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata\raw2")
prod = pd.read_pickle(r'..\data_201006_201712_addBranch_3_jn_withCIF.pkl.xz')
prod = prod.query('DataPeriod=="Prod" or DataPeriod=="Prod_Branch"')
prod = prod.drop_duplicates(subset=['CUSTOMERID','archive_date'])
cols_need =['NET_COMMITMENT_AMOUNT', 'NET_OUTSTANDING_AMOUNT', 'EXPOSURE']
prod = prod[['CUSTOMERID','archive_date']+cols_need]
prod.reset_index(drop=True, inplace=True)
prod['timestamp'] = prod['archive_date']

os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
data_train = pd.read_pickle(r'..\MFA\train_2016.pkl.xz')
data_train= pd.merge(data_train, prod, on=['CUSTOMERID','timestamp'], how='left')

cols=[
 'CONM',
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'size@EBITDA', 'size@Capitalization', 'ds@Interest Expense',
 'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital',
 'Override_Action',
 'RLA_Notches',
 'ExtRating',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Underwriter_Guideline',
 'NAICS',
 'NAICS_Cd',
 'dataset',
 'def_flag',
 'L_DATE_OF_DEFAULT','NET_COMMITMENT_AMOUNT', 'NET_OUTSTANDING_AMOUNT', 'EXPOSURE'
 ]
dat = data_train[cols].copy()
dat.dropna(subset=model.quali_factor, how='any', inplace=True)
# log trans
dat['size@Total Assets'] = np.log(1+dat['size@Total Assets'])
# fill inf
finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        dat[factor] = dat[factor].clip(np.nanmin(dat[factor][dat[factor] != -np.inf]), np.nanmax(dat[factor][dat[factor] != np.inf]))
# get existing model's Final PDRR implied PD and logit PD
dat = PD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')
dat = logitPD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')



#%%
writer = pd.ExcelWriter('top_commit_customer_with_commit.xlsx')
train_mfa = getPDRR(dat, model, ms_ver='old')
train_mfa['fitted_PDRR'] = train_mfa['Ratings']
df_ind = NAICS_mapping(train_mfa)
df_ind = MAUG_mapping(df_ind)


def top_commit_customer(dat):
    idx = dat['NET_COMMITMENT_AMOUNT'].idxmax(skipna=True)
    return(dat.loc[idx,['archive_date','CUSTOMERID', 'Customer Long Name','NET_COMMITMENT_AMOUNT', 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating', 'fitted_PDRR', 'SPRating', 'ExternalRating_PDRR']])

def _sd(data):
    if len(data)<=5:
        return np.nan
    else:
        return SomersD(data.Final_PD_Risk_Rating, data.fitted_PDRR)


df_ind['Rating_diff'] = df_ind['fitted_PDRR'] - df_ind['Final_PD_Risk_Rating']

seg_count = df_ind['Industry_by_NAICS'].value_counts()
rating_diff = np.abs(df_ind.groupby(by='Industry_by_NAICS').mean()['Rating_diff'])
sd = df_ind.groupby('Industry_by_NAICS').apply(_sd)
tot_commit = df_ind.groupby('Industry_by_NAICS').sum()['NET_COMMITMENT_AMOUNT']
result = pd.concat([seg_count, tot_commit, sd, rating_diff], axis=1)
result.columns = ['counts', 'Total_Commitment', 'SomersD', 'Ave_Rating_Diff',]
result.sort_values(by=['counts'], ascending=False, inplace=True)
result.to_excel(writer,'all')



df_ind_unique = df_ind.copy()
df_ind_unique.sort_values(by=['CUSTOMERID','timestamp'], inplace=True)
df_ind_unique.drop_duplicates(subset=['CUSTOMERID'], keep='last', inplace=True)

seg_count = df_ind_unique['Industry_by_NAICS'].value_counts()
rating_diff = np.abs(df_ind_unique.groupby(by='Industry_by_NAICS').mean()['Rating_diff'])
sd = df_ind_unique.groupby('Industry_by_NAICS').apply(_sd)
tot_commit = df_ind_unique.groupby('Industry_by_NAICS').sum()['NET_COMMITMENT_AMOUNT']
result = pd.concat([seg_count, tot_commit, sd, rating_diff], axis=1)
result.columns = ['counts', 'Total_Commitment', 'SomersD', 'Ave_Rating_Diff',]
result.sort_values(by=['counts'], ascending=False, inplace=True)
result.to_excel(writer,'unique')



#df_ind.groupby(by=['Industry_by_NAICS']).apply(top_commit_customer).to_excel(writer,'top_customer')
writer.save()

#%%
top = df_ind.groupby(by=['Industry_by_NAICS']).apply(top_commit_customer)

SomersD(top.Final_PD_Risk_Rating, top.Prelim_PD_Risk_Rating_Uncap)
#0.75
SomersD(top.Final_PD_Risk_Rating, top.fitted_PDRR)
# 0.7596153846153846

top['diff_final-ext'] = top.Final_PD_Risk_Rating- top.ExternalRating_PDRR
top['diff_new-ext'] = top.fitted_PDRR - top.ExternalRating_PDRR
top['diff_final-ext'].mean()
# -0.7
top['diff_new-ext'].mean()
# 0.1
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 20 15:22:00 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')

from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import normalization, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import getTotalscore, getPDRR, getTM
import pickle
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix
from PDScorecardTool.Process import NAICS_mapping
from PDScorecardTool.Process import SomersD
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

#%%

def top_commit_customer(dat):
    idx = dat['NET_COMMITMENT_AMOUNT'].idxmax(skipna=True)
    return(dat.loc[idx,['archive_date','CUSTOMERID', 'Customer Long Name','NET_COMMITMENT_AMOUNT', 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating', 'fitted_PDRR', 'SPRating', 'ExternalRating_PDRR']])

def _sd(data):
    if len(data)<=5:
        return np.nan
    else:
        return SomersD(data.Final_PD_Risk_Rating, data.fitted_PDRR)


def kmean_seg(dat, model, k=2, top_k=10, col='NET_COMMITMENT_AMOUNT'):
	data = dat.copy()

	table_count = data.groupby('Industry_by_NAICS').sum()[col].sort_values(ascending=False)
	pl_top_k = list(table_count.index)[:top_k] 
	table_count2 = data.groupby('Industry_by_NAICS').size()
	df = pd.concat([table_count, table_count2], axis=1)
	df.columns = [col,'counts']
	df.sort_values(col,ascending=False, inplace=True)
	top_k_coverage = df.counts[:top_k].sum()/df.counts.sum()

	# get top_k seg and remaining data:
	data_left = data.copy()
	data_top_k=pd.DataFrame()
	for ind in pl_top_k:
		data_left = data_left.query('Industry_by_NAICS !="{a0}"'.format(a0=ind))
		data_top_k = pd.concat([data_top_k,data.query('Industry_by_NAICS =="{a0}"'.format(a0=ind))], axis=0)

	# implement k-means
	data_left.reset_index(drop=True, inplace=True)
	pl_fac = model.quant_factor + model.quali_factor
	X = data_left[pl_fac]
	mms = MinMaxScaler()
	X_transformed = mms.fit_transform(X)
	kmeans = KMeans(n_clusters=k, random_state=0).fit(X_transformed)

	# replace small group with kmean group
	data_left['Industry_by_NAICS'] = kmeans.labels_
	data_left['Industry_by_NAICS'] = ['Industry_KmeanGroup_'+str(x) for x in data_left['Industry_by_NAICS']]


	data_kmean = pd.concat([data_top_k, data_left], axis=0)
	kmean_result = data_left.groupby(by='Industry_by_NAICS').size()

	return (data_kmean, kmean_result, top_k_coverage)

#%%

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)

os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata\raw2")
prod = pd.read_pickle(r'..\data_201006_201712_addBranch_3_jn_withCIF.pkl.xz')
prod = prod.query('DataPeriod=="Prod" or DataPeriod=="Prod_Branch"')
prod = prod.drop_duplicates(subset=['CUSTOMERID','archive_date'])
cols_need =['NET_COMMITMENT_AMOUNT', 'NET_OUTSTANDING_AMOUNT', 'EXPOSURE']
prod = prod[['CUSTOMERID','archive_date']+cols_need]
prod.reset_index(drop=True, inplace=True)
prod['timestamp'] = prod['archive_date']

os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
data_train = pd.read_pickle(r'..\MFA\train_2016.pkl.xz')
data_train= pd.merge(data_train, prod, on=['CUSTOMERID','timestamp'], how='left')

cols=[
 'CONM',
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'size@EBITDA', 'size@Capitalization', 'ds@Interest Expense',
 'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital',
 'Override_Action',
 'RLA_Notches',
 'ExtRating',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Underwriter_Guideline',
 'NAICS',
 'NAICS_Cd',
 'dataset',
 'def_flag',
 'L_DATE_OF_DEFAULT','NET_COMMITMENT_AMOUNT', 'NET_OUTSTANDING_AMOUNT', 'EXPOSURE'
 ]
dat = data_train[cols].copy()
dat.dropna(subset=model.quali_factor, how='any', inplace=True)
# log trans
dat['size@Total Assets'] = np.log(1+dat['size@Total Assets'])
# fill inf
finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        dat[factor] = dat[factor].clip(np.nanmin(dat[factor][dat[factor] != -np.inf]), np.nanmax(dat[factor][dat[factor] != np.inf]))
# get existing model's Final PDRR implied PD and logit PD
dat = PD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')
dat = logitPD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')



train_mfa = getPDRR(dat, model, ms_ver='old')
train_mfa['fitted_PDRR'] = train_mfa['Ratings']
data = NAICS_mapping(train_mfa)
data['Rating_diff'] = data['fitted_PDRR'] - data['Final_PD_Risk_Rating']


data, km, rate = kmean_seg(data, model, k=2, top_k=10, col='NET_COMMITMENT_AMOUNT')

#%%
writer = pd.ExcelWriter('ind_seg_kmean_commit.xlsx')

seg_count = data['Industry_by_NAICS'].value_counts()
rating_diff = np.abs(data.groupby(by='Industry_by_NAICS').mean()['Rating_diff'])
sd = data.groupby('Industry_by_NAICS').apply(_sd)
tot_commit = data.groupby('Industry_by_NAICS').sum()['NET_COMMITMENT_AMOUNT']
result = pd.concat([seg_count, tot_commit, sd, rating_diff], axis=1)
result.columns = ['counts', 'Total_Commitment', 'SomersD', 'Ave_Rating_Diff',]
result.sort_values(by=['counts'], ascending=False, inplace=True)
result.to_excel(writer,'all')



data_unique = data.copy()
data_unique.sort_values(by=['CUSTOMERID','timestamp'], inplace=True)
data_unique.drop_duplicates(subset=['CUSTOMERID'], keep='last', inplace=True)

seg_count = data_unique['Industry_by_NAICS'].value_counts()
rating_diff = np.abs(data_unique.groupby(by='Industry_by_NAICS').mean()['Rating_diff'])
sd = data_unique.groupby('Industry_by_NAICS').apply(_sd)
tot_commit = data_unique.groupby('Industry_by_NAICS').sum()['NET_COMMITMENT_AMOUNT']
result = pd.concat([seg_count, tot_commit, sd, rating_diff], axis=1)
result.columns = ['counts', 'Total_Commitment', 'SomersD', 'Ave_Rating_Diff',]
result.sort_values(by=['counts'], ascending=False, inplace=True)
result.to_excel(writer,'unique')



writer.save()

# -*- coding: utf-8 -*-
"""
Created on Fri Sep  7 13:03:22 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import pickle
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import copy
import scipy.stats as scistat
from sklearn.model_selection import KFold


MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
CT = 0.0105 
# load model setting
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)


#%%


# make change to make paras comes from bin data ,but plot all data.
def LRplot(data_all, Intercept, slope):
  
    fig, ax = plt.subplots()
    ax.scatter(data_all.Totalscore,data_all.logitPD_frPDRR, s=25)    
    X_full_plot = np.linspace(-50,100,200)
    ax.plot(X_full_plot, X_full_plot*slope + Intercept, label="SingleLine")
    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()

def LRplot_mullines(data_all, pl_Intercept, pl_slope, pl_labe):
  
    fig, ax = plt.subplots()
    ax.scatter(data_all.Totalscore,data_all.logitPD_frPDRR, s=25)    
    X_full_plot = np.linspace(-50,100,200)
    for i in range(len(pl_slope)):
        ax.plot(X_full_plot, X_full_plot*pl_slope[i] + pl_Intercept[i], label=pl_label[i])
    plt.xlabel('Total Score',color='b')   
    plt.ylabel('logit PD',color='b')
    legend = ax.legend(loc='upper left', shadow=True)
    ax2 = ax.twinx()
    ax2.scatter(data_all.Totalscore,data_all.logitPD_frPDRR, s=25)    
    pl_logitPD = data_all['logitPD_frPDRR'].unique()
    pl_logitPD.sort()
    pl_PDRR = list(np.arange(2,2+len(pl_logitPD)))
    plt.yticks(pl_logitPD, pl_PDRR)
    plt.ylabel('Final PDRR', color='r')
    plt.show()


def scorecard_single(data, Intercept, slope, ms_ver='new'):
    df = data.copy()
    
    if ms_ver=='old':
        low_pd = MS['old_low']
    else:
        low_pd = MS['new_low']

    df['fitted_logit_pd'] = Intercept + slope*df['Totalscore']
    df['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in df['fitted_logit_pd'] ]
    Ratings = []
    for i in df.iterrows():
        Ratings.append(sum(low_pd<=(i[1].fitted_pd)))
    df['fitted_PDRR'] = Ratings   

    return(df)


def get_intcp(data, CT, slope):
    df= data.copy()
    def _fun(Intercept):
        df['fitted_logit_pd'] = Intercept + slope*df['Totalscore']
        df['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in df['fitted_logit_pd'] ]
        return (df.fitted_pd.mean()-CT)

    intcp = fsolve(_fun, -5)
    return(intcp[0])






#%%
# load calibration data and calculate total score based on model setting
#dat = pd.read_pickle('norm_test_2017.pkl.xz')
dat = pd.read_pickle(r'..\calib\norm_2010_2016.pkl.xz')
dat['quantscore'] = (model.quant_weight * dat[model.quant_factor].values).sum(axis=1)
dat['quantscore'] = 50*( dat['quantscore'] - model.quantmean) / model.quantstd
dat['qualiscore'] = (model.quali_weight * dat[model.quali_factor].values).sum(axis=1)
dat['qualiscore'] = 50*( dat['qualiscore'] - model.qualimean) / model.qualistd
dat['Totalscore'] = dat['quantscore']*model.quantweight + dat['qualiscore'] *model.qualiweight


# double check
print(SomersD(dat.Final_PD_Risk_Rating, dat.Totalscore))





#%%

pl_slope = list(np.linspace(0.01,0.06,200))
seed = 0
writer = pd.ExcelWriter(r'kfold\calibration_seed_{}.xlsx'.format(seed))

kf = KFold(n_splits=5, shuffle=True, random_state=seed)
s=1
for train_index, test_index in kf.split(dat):
	dat_sample = dat.iloc[train_index]
	perf_table = pd.DataFrame()
	for slope in pl_slope:
	    Intercept = get_intcp(dat_sample, CT, slope)
	    df = scorecard_single(dat_sample, Intercept, slope, ms_ver='old')
	    stats = TMstats(df, 'fitted_PDRR', 'Final_PD_Risk_Rating', PDRR=range(1,16))
	    stats.update({'SomersD':SomersD(df.Final_PD_Risk_Rating, df.fitted_PDRR)})
	    stats.update({'Intercept':Intercept, 'slope':slope})
	    D, pvalue = scistat.ks_2samp(df.Final_PD_Risk_Rating, df.fitted_PDRR)
	    stats.update({'KS_stats':D})
	    perf_table = perf_table.append(stats,ignore_index=True)	

	perf_table = perf_table[['Intercept','slope','SomersD','Match', 'Within_1', 'Within_2', 'Outside_5', 'KS_stats','Downgrade', 'Upgrade']]
	perf_table['diff'] = perf_table['Downgrade'] - perf_table['Upgrade']
	perf_table['existing_KS_stats'],_ = scistat.ks_2samp(df.Final_PD_Risk_Rating, df.Prelim_PD_Risk_Rating_Uncap)
	perf_table.to_excel(writer, str(s))
	s+=1
writer.save()


#%%
df1 = pd.read_excel('calibration_seed_0.xlsx',sheet_name='1')
df2 = pd.read_excel('calibration_seed_0.xlsx',sheet_name='2')
df3 = pd.read_excel('calibration_seed_0.xlsx',sheet_name='3')
df4 = pd.read_excel('calibration_seed_0.xlsx',sheet_name='4')
df5 = pd.read_excel('calibration_seed_0.xlsx',sheet_name='5')


df = (df1+df2+df3+df4+df5)/5
df.to_excel('kfold_indoc.xlsx')# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 22:58:42 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm
from sklearn.model_selection import KFold


X_train = pd.read_pickle(r'..\MFA\train_2016.pkl.xz')

quant_factor = ['Net_Profit_Margin','Total_Debt_By_COP','Total_Assets','Total_Liab_by_Tang_Net_Worth','End_Cash_Equiv_By_Tot_Liab']
quali_factor = ['Strength_SOR_Prevent_Default','Level_Waiver_Covenant_Mod','Mgmt_Resp_Adverse_Conditions','Vulnerability_To_Changes']
PDInfo_file = r'C:\Users\ub71894\Documents\DevRepo\Files\PDModelParameters.xlsx'
masterscale_file = r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx'
model_name = 'C&I'; version = 1.2
model = PDModel(PDInfo_file, model_name, version, quant_factor, quali_factor, masterscale_file)
model.reset()


def modelSD(data, pl_factors, pl_wt, dependentvar):
	est = (data[pl_factors]*pl_wt).sum(axis=1)
	return(SomersD(data[dependentvar], est))

#%% 
cols_negsource = ['size@EBIT', 'size@EBITDA','size@Union Bank EBIT','size@Union Bank EBITDA','size@Retained Earnings','size@Capitalization',\
'ds@Interest Expense']
#a=X_train[cols_negsource].describe(percentiles=[0.01,0.02,0.05,0.1])


invalid_mapping = {
'prof@EBITDA_to_NS':0,
'prof@RE_to_TA':0,
'cf@TD_to_UBEBITDA':  'size@Union Bank EBITDA',
'cf@TD_to_EBITDA':  'size@EBITDA',
'size@Net_Sales': 0,
'size@Total Assets':0,
'size@Profit before Taxes':0,
'size@Net Profit':0,
'bs@TD_to_Capt':'size@Capitalization',
'bs@TD_to_TA':0,
'liq@ECE_to_TL':0,
'liq@RE_to_CL':0,
'ds@EBIT_to_IE':'ds@Interest Expense',
'ds@EBITDA_to_IE':'ds@Interest Expense'
}


finallist=[
'prof@EBITDA_to_NS', 'prof@RE_to_TA', 
'cf@TD_to_UBEBITDA','cf@TD_to_EBITDA',
'size@Net_Sales','size@Total Assets','size@Profit before Taxes', 'size@Net Profit', 
'bs@TD_to_Capt', 'bs@TD_to_TA', 
'liq@ECE_to_TL','liq@RE_to_CL', 
'ds@EBIT_to_IE','ds@EBITDA_to_IE']


data_train = X_train[finallist+cols_negsource+['Final_PD_Risk_Rating']]
data_train.dropna(subset=finallist+cols_negsource, how='any', inplace=True)
data_train.reset_index(drop=True, inplace=True)
data_train['size@Net_Sales'] = np.log(1+data_train['size@Net_Sales'])
data_train['size@Total Assets'] = np.log(1+data_train['size@Total Assets'])


#data_train.describe(percentiles=[0.05,0.95])
for factor in finallist:                       
        data_train[factor] = data_train[factor].clip(np.nanmin(data_train[factor][data_train[factor] != -np.inf]), np.nanmax(data_train[factor][data_train[factor] != np.inf]))

# construct model based on train data:
sfa = []
for factor in finallist:
    sfa.append(SomersD(data_train.Final_PD_Risk_Rating, data_train[factor]))

model.update({'quant_factor':finallist})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*14})
model.update({'Invalid_Neg': [0]*14})
model.update(quanttrans(data_train, model, floor=0.05, cap=0.95))
# use floor=0 for factor 'ds@EBIT_to_IE'
model.floor[-2]=0
pl_invalid = []
for fac in finallist:
    pl_invalid.append(invalid_mapping[fac])
model.Invalid_Neg = pl_invalid


data_train = PD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')
data_train = logitPD_frPDRR(data_train, model, 'Final_PD_Risk_Rating', ms_ver='old')

cni_train = MFA(data_train, model, quant_only=True)

normdat_train = cni_train.normdata.copy()


#%%

finallist =  ['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']

x_train = sm.add_constant(normdat_train[finallist], prepend = True)
linear = sm.OLS(normdat_train['logitPD_frPDRR'], x_train, missing='drop')
result = linear.fit()
#result.summary()	

stats = result.params[1:] / result.params[1:].sum()

pl_temp=[]
for i in range(len(finallist)):	
	pl_temp.append((max(0.01,round(round(stats[i],2)-0.05,2)),   max(0.01,round(round(stats[i],2)+0.05,2))   ))
pl_wt_range = pl_temp


#%%
seed = 0
writer = pd.ExcelWriter(r'kfold\gridsearch_seed_{}.xlsx'.format(seed))
kf = KFold(n_splits=5,shuffle=True, random_state=seed)
s=1
for train_index, test_index in kf.split(data_train):
	dat_sample = data_train.iloc[train_index]
	cni_train = MFA(dat_sample, model, quant_only=True)
	stats = cni_train.ARgridsearch(quant_factor=finallist,quant_weight_range=pl_wt_range, \
		delta_factor=0.01,isthere_def=False, dependentvar='logitPD_frPDRR')
	stats.to_excel(writer, str(s))
	s+=1
writer.save()
 
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\calib")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
import pickle
import copy
from PDScorecardTool.Process import getTM
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats


MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')

# load model setting
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)
filehandler = open(r'..\spec\model_af_calib_missing2017.pkl','rb')
model_old = pickle.load(filehandler)

data_train = pd.read_pickle(r'..\MFA\train_2016.pkl.xz')

cols=[
 'CONM',
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'size@EBITDA', 'size@Capitalization', 'ds@Interest Expense',
 'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital',
 'Override_Action',
 'RLA_Notches',
 'ExtRating',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Underwriter_Guideline',
 'NAICS',
 'NAICS_Cd',
 'dataset',
 'def_flag',
 'L_DATE_OF_DEFAULT'
 ]
dat = data_train[cols].copy()
dat.dropna(subset=model.quali_factor, how='any', inplace=True)
# log trans
dat['size@Total Assets'] = np.log(1+dat['size@Total Assets'])
# fill inf
finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        dat[factor] = dat[factor].clip(np.nanmin(dat[factor][dat[factor] != -np.inf]), np.nanmax(dat[factor][dat[factor] != np.inf]))







#%% TM

getTM(dat, model_old, model, ms_ver='old', PDRR_range=(1,16))
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:25:09 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')

from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import normalization, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import getTotalscore, getPDRR, getTM
import pickle
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping, ExtRating_mapping

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)

data_train = pd.read_pickle(r'..\MFA\train_2016.pkl.xz')
cols=[
 'CONM',
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'size@EBITDA', 'size@Capitalization', 'ds@Interest Expense',
 'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital',
 'Override_Action',
 'RLA_Notches',
 'ExtRating',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Underwriter_Guideline',
 'NAICS',
 'NAICS_Cd',
 'dataset',
 'def_flag',
 'L_DATE_OF_DEFAULT'
 ]
dat = data_train[cols].copy()
dat.dropna(subset=model.quali_factor, how='any', inplace=True)
# log trans
dat['size@Total Assets'] = np.log(1+dat['size@Total Assets'])
# fill inf
finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        dat[factor] = dat[factor].clip(np.nanmin(dat[factor][dat[factor] != -np.inf]), np.nanmax(dat[factor][dat[factor] != np.inf]))
# get existing model's Final PDRR implied PD and logit PD
dat = PD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')
dat = logitPD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')



#%%
import seaborn as sns
train_mfa = getPDRR(dat, model, ms_ver='old')


data_plot1 = train_mfa.copy()
data_plot1['PD_Risk_Rating'] = [int(x) for x in data_plot1['Final_PD_Risk_Rating']]
data_plot1['Rating'] = 'Existing final PDRR'
data_plot1['percentage'] = 1/len(data_plot1)

data_plot2 = train_mfa.copy()
data_plot2['PD_Risk_Rating'] = [int(x) for x in data_plot2['Ratings']]
data_plot2['Rating'] = 'New fitted PDRR'
data_plot2['percentage'] = 1/len(data_plot2)

data_plot = pd.concat([data_plot1, data_plot2], axis=0)
 
sns.barplot(x='PD_Risk_Rating', y='percentage', hue='Rating', data=data_plot, estimator=sum, palette='pastel')
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  6 10:50:52 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD, buildpseudodef, buildpseudodef2
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans,qualitrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm
import pickle


filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)
data_train = pd.read_pickle(r'..\MFA\train_2016.pkl.xz')
data_train.dropna(subset=model.quali_factor, how='any', inplace=True)
data_train.reset_index(drop=True, inplace=True)

# make pseudo default at final PDRR=13, 14, 15
data_train2 = buildpseudodef(data_train, def_flag='def_flag', PDRR='Final_PD_Risk_Rating', pseudodef_PDRR=[13,14,15])

model.update(qualitrans(data_train2, model, isthere_def=True, dependentvar='def_flag', output=True))
# only the qual1 needs override on answer D
model.qualimapping[0]['D'] = 80.08158642587831

model.save(r'quali_mapping\model_qualimapping_by_pseudodef.pkl')


#%%

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')

from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import normalization, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import getTotalscore, getPDRR, getTM
import pickle
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)
filehandler = open(r'quali_mapping\model_qualimapping_by_pseudodef.pkl','rb')
model_qualimapping = pickle.load(filehandler)


data_train = pd.read_pickle(r'..\MFA\train_2016.pkl.xz')
cols=[
 'CONM',
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'size@EBITDA', 'size@Capitalization', 'ds@Interest Expense',
 'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital',
 'Override_Action',
 'RLA_Notches',
 'SPRating',
 'ExtRating',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Underwriter_Guideline',
 'NAICS',
 'NAICS_Cd',
 'dataset',
 'def_flag',
 'L_DATE_OF_DEFAULT',
 ]
dat = data_train[cols].copy()
dat.dropna(subset=model.quali_factor, how='any', inplace=True)
# log trans
dat['size@Total Assets'] = np.log(1+dat['size@Total Assets'])
# fill inf
finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        dat[factor] = dat[factor].clip(np.nanmin(dat[factor][dat[factor] != -np.inf]), np.nanmax(dat[factor][dat[factor] != np.inf]))
# get existing model's Final PDRR implied PD and logit PD
dat = PD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')
dat = logitPD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')


#%%
getTM(dat, model, model_qualimapping, ms_ver='old', PDRR_range=(1,15))

#%%
#%%
train_mfa = getPDRR(dat, model_qualimapping, ms_ver='old')
CreateBenchmarkMatrix(train_mfa, 'TM.xlsx', 'fitted_vs_Final',  'Ratings', 'Final_PD_Risk_Rating',PDRR=range(1,16))
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 31 13:25:09 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD, buildpseudodef, buildpseudodef2
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import quanttrans,qualitrans, normalization, PD_frPDRR, logitPD_frPDRR
from itertools import combinations, product
import statsmodels.api as sm
import pickle


filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)
data_train = pd.read_pickle(r'..\MFA\train_2016.pkl.xz')
data_train.dropna(subset=model.quant_factor, how='any', inplace=True)
data_train.reset_index(drop=True, inplace=True)


# log trans
data_train['size@Total Assets'] = np.log(1+data_train['size@Total Assets'])
# fill inf
finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        data_train[factor] = data_train[factor].clip(np.nanmin(data_train[factor][data_train[factor] != -np.inf]), np.nanmax(data_train[factor][data_train[factor] != np.inf]))

cache = model.Invalid_Neg
model.Invalid_Neg = [0]*5
model.update(quanttrans(data_train, model, floor=0.01, cap=0.99))
# use floor=0 for factor 'cf@TD_to_EBITDA' and 'ds@EBITDA_to_IE'
model.floor[1]=0;  model.floor[4]=0
model.Invalid_Neg = cache

model.save(r'quant_f1c99\model_quant_f1c99.pkl')


#%%
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')

from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import normalization, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import getTotalscore, getPDRR, getTM
import pickle
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)
filehandler = open(r'quant_f1c99\model_quant_f1c99.pkl','rb')
model_quantf1c99 = pickle.load(filehandler)


data_train = pd.read_pickle(r'..\MFA\train_2016.pkl.xz')
cols=[
 'CONM',
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'size@EBITDA', 'size@Capitalization', 'ds@Interest Expense',
 'prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE',
 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital',
 'Override_Action',
 'RLA_Notches',
 'SPRating',
 'ExtRating',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Underwriter_Guideline',
 'NAICS',
 'NAICS_Cd',
 'dataset',
 'def_flag',
 'L_DATE_OF_DEFAULT',
 ]
dat = data_train[cols].copy()
dat.dropna(subset=model.quali_factor, how='any', inplace=True)
# log trans
dat['size@Total Assets'] = np.log(1+dat['size@Total Assets'])
# fill inf
finallist=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE']
for factor in finallist:                       
        dat[factor] = dat[factor].clip(np.nanmin(dat[factor][dat[factor] != -np.inf]), np.nanmax(dat[factor][dat[factor] != np.inf]))
# get existing model's Final PDRR implied PD and logit PD
dat = PD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')
dat = logitPD_frPDRR(dat, model, 'Final_PD_Risk_Rating', ms_ver='old')


#%%
getTM(dat, model, model_quantf1c99, ms_ver='old', PDRR_range=(1,15))


#%%
#%%
train_mfa = getPDRR(dat, model_quantf1c99, ms_ver='old')
CreateBenchmarkMatrix(train_mfa, 'TM.xlsx', 'fitted_vs_Final',  'Ratings', 'Final_PD_Risk_Rating',PDRR=range(1,16))

# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 15:55:58 2019

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')

rawdata = pd.read_excel(r'newdata\2018_CASS_CDM_Data.xlsx')

# about 4440 obs has Nan in factors including net sales:
valid = rawdata.loc[rawdata['NetSales'] == rawdata['NetSales'] ]
nonvalid = rawdata.loc[rawdata['NetSales'] != rawdata['NetSales'] ]
# remove two audit method 'Proforma' and 'Projection'
valid2 = valid.loc[valid['Audit Method'] != 'Proforma']
valid2 = valid2.loc[valid2['Audit Method'] != 'Projection']

#%% remove guarantor impact and attach other important columns
valid2['Gua_override'] =  valid2['PD_Risk_Rating_After_Gtee'] - valid2['PD_Risk_Rating_After_RLA']
valid3 = valid2.query('Gua_override==0')
valid3['RLA_Notches'].fillna(0, inplace=True)
valid3['Override_Action'].fillna(0, inplace=True)


data = valid3.copy()

#%% build ratios
data['prof@NOP_to_NS'] 		= data[ 'NetOpProfit'] / data['NetSales']
data['cf@TD_to_UBEBITDA']	= data['TotalDebt' ] / data[  'UBOCEBITDA']
data['bs@TD_to_Capt']		= data['TotalDebt' ] / data[ 'CAPITALIZATION']
data['liq@ECE_to_TL']		= data['CashAndEquivs' ] / data[ 'TotalLiabs' ]
data['size@TangNW_to_TA']	= data[ 'UBOCTNW'] / data['TOTALASSETS']


data['prof@EBITDA_to_NS']	= data[ 'EBITDA'] / data['NetSales' ]
data['cf@TD_to_EBITDA']		= data[ 'TotalDebt'] / data[ 'EBITDA' ]
data['size@Total Assets']	= data['quant3']
data['bs@TD_to_Capt']		= data[ 'TotalDebt'] / data['CAPITALIZATION' ]
data['ds@EBITDA_to_IE']		= data[ 'EBITDA' ] / data[  'InterestExpense']

# for 'invalid negative' tag
data['size@EBITDA']			= data['EBITDA']	
data['size@Capitalization']	= data['CAPITALIZATION']	
data['ds@Interest Expense']	= data['InterestExpense']
data['UBEBITDA']			= data['UBOCEBITDA']
data['Capt']				= data['CAPITALIZATION']

data['Net_Sales'] = data['NetSales']


data.to_csv(r'..\newdata\2018_CASS_CDM_Data_cleaned.csv')





# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 10:53:41 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
import pickle
from PDScorecardTool.Process import getPDRR

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
filehandler = open(r'..\MM\model_spec_calib.pkl','rb')
MM_model = pickle.load(filehandler)
filehandler = open(r'spec\model_af_calib.pkl','rb')
LC_model = pickle.load(filehandler)
# set boundary range
boundaries = (8e8, 12e8)
all_factors = list(set(LC_model.quant_factor+LC_model.quali_factor+  MM_model.quant_factor+MM_model.quali_factor))


#%% MM data and processing
#dat = pd.read_excel(r'..\newdata\dat_mm_by1000_last_cs.xlsx')
#dat.to_pickle(r'..\newdata\dat_mm_by1000_last_cs.pkl')
MM_dat = pd.read_pickle(r'..\newdata\dat_mm_by1000_last_cs.pkl')

# remove guarantor impacted obs
MM_dat['Gua_override'] =  MM_dat['PD_Risk_Rating_After_Gtee'] - MM_dat['PD_Risk_Rating_After_RLA']
MM_dat = MM_dat.query('Gua_override==0')
MM_dat['RLA_Notches'].fillna(0, inplace=True)
MM_dat['Override_Action'].fillna(0, inplace=True)

# get development sample
MM_dat_dev = MM_dat.query('archive_date<20160101')

boundary_data_MM =  MM_dat_dev.query('Net_Sales>{}'.format(boundaries[0]))
boundary_data_MM['portfolio'] = 'MM'


#%% LC data and processing
LC_dat = pd.read_pickle(r'..\newdata\prod_1000.pkl.xz')
LC_dat['archive_date'] = LC_dat['timestamp']
LC_dat['Net_Sales'] = LC_dat['size@Net_Sales']
# get development sample
LC_dat_dev = LC_dat.query('archive_date<20160101')

boundary_data_LC =  LC_dat_dev.query('Net_Sales<{}'.format(boundaries[1]))
boundary_data_LC['portfolio'] = 'LC'


#%% get dat for analysis and processing
boundary_data = pd.concat([boundary_data_LC, boundary_data_MM], axis=0)

# remove all obs with missing data
boundary_data.dropna(subset=all_factors, how='any', inplace=True)
boundary_data.reset_index(drop=True, inplace=True)

# transform
boundary_data['liq@ECE_to_TL'] = np.log(boundary_data['liq@ECE_to_TL'])
boundary_data['UBEBITDA'] = boundary_data['size@Union Bank EBITDA']
boundary_data['size@Total Assets'] = np.log(1+boundary_data['size@Total Assets'])

# replace +-inf with max and min:
for factor in list(set(LC_model.quant_factor+MM_model.quant_factor)):                       
        boundary_data[factor] = boundary_data[factor].clip(np.nanmin(boundary_data[factor][boundary_data[factor] != -np.inf]), np.nanmax(boundary_data[factor][boundary_data[factor] != np.inf]))


#%% get rating from two models. using old masterscale
# get MM rating
ratings_MM = getPDRR(boundary_data, MM_model, ms_ver='old')
ratings_MM.rename(columns={'Ratings':'Ratings_MM'}, inplace=True)
ratings_MM.rename(columns={'PD':'PD_MM'}, inplace=True)
# get LC rating
ratings_LC = getPDRR(boundary_data, LC_model, ms_ver='old')
ratings_LC.rename(columns={'Ratings':'Ratings_LC'}, inplace=True)
ratings_LC.rename(columns={'PD':'PD_LC'}, inplace=True)
# combine them 
dat_ratings = pd.concat([ratings_MM, ratings_LC[['PD_LC','Ratings_LC']]], axis=1)
dat_ratings.to_csv('dat_ratings.csv')
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 10:53:41 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
import pickle
import seaborn as sns
from PDScorecardTool.Process import getPDRR, SomersD, NAICS_mapping
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix

# boundary sample
dat = pd.read_csv('dat_ratings.csv')
# MM portfolio in boundary sample
dat_MM = dat.query('portfolio=="MM"')
# LC portfolio in boundary sample
dat_LC = dat.query('portfolio=="LC"')


#%% analysis on boundary sample
# two model's prelim PDRR distribution on Boundary sample
data_plot1 = dat.copy()
data_plot1['PDRR from CnI Model'] = data_plot1['Ratings_MM']
data_plot1['Rating'] = 'Rating by MM model'
data_plot1['percentage'] = 1/len(data_plot1)

data_plot2 = dat.copy()
data_plot2['PDRR from CnI Model'] = data_plot2['Ratings_LC']
data_plot2['Rating'] = 'Rating by LC model'
data_plot2['percentage'] = 1/len(data_plot2)

data_plot = pd.concat([data_plot1, data_plot2], axis=0)
 
sns.barplot(x='PDRR from CnI Model', y='percentage', hue='Rating', data=data_plot, estimator=sum, palette='pastel')

dat['Ratings_MM'].mean()
dat['Ratings_LC'].mean()
dat['PD_MM'].mean()
dat['PD_LC'].mean()



# LC portfolio
data_plot1 = dat_LC.copy()
data_plot1['PDRR from CnI Model'] = data_plot1['Ratings_MM']
data_plot1['Rating'] = 'Rating by MM model'
data_plot1['percentage'] = 1/len(data_plot1)

data_plot2 = dat_LC.copy()
data_plot2['PDRR from CnI Model'] = data_plot2['Ratings_LC']
data_plot2['Rating'] = 'Rating by LC model'
data_plot2['percentage'] = 1/len(data_plot2)

data_plot = pd.concat([data_plot1, data_plot2], axis=0)
 
sns.barplot(x='PDRR from CnI Model', y='percentage', hue='Rating', data=data_plot, estimator=sum, palette='pastel')


print(dat_LC['Ratings_MM'].mean())
print(dat_LC['Ratings_LC'].mean())
print(dat_LC['PD_MM'].mean()/100)
print(dat_LC['PD_LC'].mean()/100)

CreateBenchmarkMatrix(dat_LC, 'boundary.xlsx','LC_portfolio','Ratings_MM','Ratings_LC',  PDRR=range(1,16) )

#%%

dat_MM = NAICS_mapping(dat_MM)
dat_LC = NAICS_mapping(dat_LC)
dat = NAICS_mapping(dat)



dat['diff'] = np.abs(dat['Ratings_MM'] - dat['Ratings_LC'])
dat_present = dat[['diff','Ratings_MM','Ratings_LC', 'Final_PD_Risk_Rating','portfolio', 'Industry_by_NAICS']].copy()
outliers = dat_present.query('diff>=4')# -*- coding: utf-8 -*-
"""
Created on Fri Nov  2 10:52:36 2018

@author: ub71894 (4e8e6d0b), CSG

"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.MFA import MFA

from PDScorecardTool.Process import NAICS_mapping, SomersD, PD_frPDRR, logitPD_frPDRR
import pickle
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

filehandler = open(r'spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)
pl_fac = model.quant_factor + model.quali_factor

#norm_train_2010_2016 = pd.read_pickle(r'calib\norm_2010_2016.pkl.xz')
#norm_test_2017 = pd.read_pickle(r'calib\norm_test_2017.pkl.xz')
#data = pd.concat([norm_train_2010_2016, norm_test_2017], axis=0)


data = pd.read_pickle(r'..\newdata\combo_1000.pkl.xz')


data.dropna(subset=model.quali_factor, how='any', inplace=True)
data.reset_index(drop=True, inplace=True)
# log trans
data['size@Total Assets'] = np.log(1+data['size@Total Assets'])
# fill inf
for factor in model.quant_factor:                       
        data[factor] = data[factor].clip(np.nanmin(data[factor][data[factor] != -np.inf]), np.nanmax(data[factor][data[factor] != np.inf]))
# get existing model's Final PDRR implied PD and logit PD
data = PD_frPDRR(data, model, 'Final_PD_Risk_Rating', ms_ver='old')
data = logitPD_frPDRR(data, model, 'Final_PD_Risk_Rating', ms_ver='old')

cni = MFA(data, model, quant_only=False)
cni.modelAR(quant_weight=model.quant_weight, quali_weight=model.quali_weight, quantweight=0.55, \
	isthere_def=False, dependentvar='logitPD_frPDRR', use_msms=True)
data = cni.normdata.copy()

data['JBA'] = data['RLA_Notches']+data['Override_Action']
data = NAICS_mapping(data)


#%% load commitment data
prod = pd.read_pickle(r"C:\Users\ub71894\Documents\Projects\CNI\newdata\data_201006_201712_addBranch_3_jn_withCIF.pkl.xz")
prod = prod.drop_duplicates(subset=['CUSTOMERID','archive_date'])
cols_need =['NET_COMMITMENT_AMOUNT', 'NET_OUTSTANDING_AMOUNT', 'EXPOSURE']
prod = prod[['CUSTOMERID','archive_date']+cols_need]
prod.reset_index(drop=True, inplace=True)
prod['timestamp'] = prod['archive_date']


data  = pd.merge(data, prod, on=['CUSTOMERID','timestamp'], how='left')

# unique customer by keeping the latest statement
data.sort_values(by=['CUSTOMERID','timestamp'], inplace=True)
data_unique_last = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')

# unique customer by keeping the max committment statement
data.sort_values(by=['CUSTOMERID','NET_COMMITMENT_AMOUNT'], inplace=True)
data_unique_max = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')




#%% all, by counts 
table_count = data.groupby('Industry_by_NAICS').size().sort_values(ascending=False)

pl_top10 = list(table_count.index)[:10] 
table_count[:10].sum()/table_count.sum()
# 0.8986384266263238
'''
['Manufacturing',
 'Wholesale Trade',
 'Retail Trade',
 'Health Care and Social Assistance',
 'Professional, Scientific, and Technical Services',
 'Information',
 'Administrative and Support and Waste Management and Remediation Services',
 'Transportation and Warehousing',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Finance and Insurance']

'''

#%% all, by commmitment size
table_count = data.groupby('Industry_by_NAICS').sum()['NET_COMMITMENT_AMOUNT'].sort_values(ascending=False)
pl_top10 = list(table_count.index)[:10] 

table_count2 = data.groupby('Industry_by_NAICS').size()
df = pd.concat([table_count, table_count2], axis=1)
df.columns = ['NET_COMMITMENT_AMOUNT','counts']
df.sort_values('NET_COMMITMENT_AMOUNT',ascending=False, inplace=True)
df.counts[:10].sum()/df.counts.sum()

# 0.885590015128593
'''
['Manufacturing',
 'Wholesale Trade',
 'Retail Trade',
 'Health Care and Social Assistance',
 'Professional, Scientific, and Technical Services',
 'Administrative and Support and Waste Management and Remediation Services',
 'Information',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Real Estate and Rental and Leasing',
 'Finance and Insurance']

'''


#%% last, by counts 
table_count = data_unique_last.groupby('Industry_by_NAICS').size().sort_values(ascending=False)

pl_top10 = list(table_count.index)[:10] 
table_count[:10].sum()/table_count.sum()
# 0.9026063100137174
'''
['Manufacturing',
 'Wholesale Trade',
 'Retail Trade',
 'Information',
 'Transportation and Warehousing',
 'Health Care and Social Assistance',
 'Professional, Scientific, and Technical Services',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Finance and Insurance',
 'Administrative and Support and Waste Management and Remediation Services']

'''


#%%  last, by commmitment size
table_count = data_unique_last.groupby('Industry_by_NAICS').sum()['NET_COMMITMENT_AMOUNT'].sort_values(ascending=False)
pl_top10 = list(table_count.index)[:10] 

table_count2 = data_unique_last.groupby('Industry_by_NAICS').size()
df = pd.concat([table_count, table_count2], axis=1)
df.columns = ['NET_COMMITMENT_AMOUNT','counts']
df.sort_values('NET_COMMITMENT_AMOUNT',ascending=False, inplace=True)
df.counts[:10].sum()/df.counts.sum()

# 0.8986384266263238
'''
['Manufacturing',
 'Retail Trade',
 'Wholesale Trade',
 'Health Care and Social Assistance',
 'Information',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Professional, Scientific, and Technical Services',
 'Finance and Insurance',
 'Administrative and Support and Waste Management and Remediation Services',
 'Transportation and Warehousing']

'''


#%% max, by counts 
table_count = data_unique_max.groupby('Industry_by_NAICS').size().sort_values(ascending=False)

pl_top10 = list(table_count.index)[:10] 
table_count[:10].sum()/table_count.sum()
# 0.897119341563786
'''
['Manufacturing',
 'Wholesale Trade',
 'Retail Trade',
 'Information',
 'Transportation and Warehousing',
 'Professional, Scientific, and Technical Services',
 'Health Care and Social Assistance',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Finance and Insurance',
 'Administrative and Support and Waste Management and Remediation Services']

'''


#%%  max, by commmitment size
table_count = data_unique_max.groupby('Industry_by_NAICS').sum()['NET_COMMITMENT_AMOUNT'].sort_values(ascending=False)
pl_top10 = list(table_count.index)[:10] 

table_count2 = data_unique_max.groupby('Industry_by_NAICS').size()
df = pd.concat([table_count, table_count2], axis=1)
df.columns = ['NET_COMMITMENT_AMOUNT','counts']
df.sort_values('NET_COMMITMENT_AMOUNT',ascending=False, inplace=True)
df.counts[:10].sum()/df.counts.sum()

# 0.8986384266263238
'''
['Manufacturing',
 'Retail Trade',
 'Wholesale Trade',
 'Health Care and Social Assistance',
 'Information',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Professional, Scientific, and Technical Services',
 'Finance and Insurance',
 'Administrative and Support and Waste Management and Remediation Services',
 'Transportation and Warehousing']

'''

pl1 = ['Manufacturing',
 'Wholesale Trade',
 'Retail Trade',
 'Health Care and Social Assistance',
 'Professional, Scientific, and Technical Services',
 'Information',
 'Administrative and Support and Waste Management and Remediation Services',
 'Transportation and Warehousing',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Finance and Insurance']

pl2 = ['Manufacturing',
 'Wholesale Trade',
 'Retail Trade',
 'Health Care and Social Assistance',
 'Professional, Scientific, and Technical Services',
 'Administrative and Support and Waste Management and Remediation Services',
 'Information',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Real Estate and Rental and Leasing',
 'Finance and Insurance']

pl3 = ['Manufacturing',
 'Wholesale Trade',
 'Retail Trade',
 'Information',
 'Transportation and Warehousing',
 'Health Care and Social Assistance',
 'Professional, Scientific, and Technical Services',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Finance and Insurance',
 'Administrative and Support and Waste Management and Remediation Services']

pl4 = ['Manufacturing',
 'Retail Trade',
 'Wholesale Trade',
 'Health Care and Social Assistance',
 'Information',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Professional, Scientific, and Technical Services',
 'Finance and Insurance',
 'Administrative and Support and Waste Management and Remediation Services',
 'Transportation and Warehousing']

pl5 = ['Manufacturing',
 'Wholesale Trade',
 'Retail Trade',
 'Information',
 'Transportation and Warehousing',
 'Professional, Scientific, and Technical Services',
 'Health Care and Social Assistance',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Finance and Insurance',
 'Administrative and Support and Waste Management and Remediation Services']

pl6 = ['Manufacturing',
 'Retail Trade',
 'Wholesale Trade',
 'Health Care and Social Assistance',
 'Information',
 'Mining, Quarrying, and Oil and Gas Extraction',
 'Professional, Scientific, and Technical Services',
 'Finance and Insurance',
 'Administrative and Support and Waste Management and Remediation Services',
 'Transportation and Warehousing']

tops = list(set(pl1+pl2+pl3+pl4+pl5+pl6))








data_left = data_unique_max.copy()
for ind in tops:
	data_left = data_left.query('Industry_by_NAICS !="{a0}"'.format(a0=ind))

data_left.reset_index(drop=True, inplace=True)

X = data_left[pl_fac]
mms = MinMaxScaler()
X_transformed = mms.fit_transform(X)

#%%
Sum_of_squared_distances = []
K = range(2,21)
for k in K:
    km = KMeans(n_clusters=k)
    km = km.fit(X_transformed)
    Sum_of_squared_distances.append(km.inertia_)


plt.plot(K, Sum_of_squared_distances, 'bx-')
plt.xlabel('k')
plt.ylabel('Sum_of_squared_distances')
plt.title('Elbow Method For Optimal k')
plt.show()


#%%
k=2
kmeans = KMeans(n_clusters=k, random_state=0).fit(X_transformed)

data_left['kmean_group'] = kmeans.labels_
data_left.groupby(by='kmean_group').size()


'''
kmean_group
0    23
1    42
dtype: int64
'''
# RLA
data_left.groupby(by='kmean_group')['RLA_Notches'].agg(['mean','std','max','min'])
data_left.RLA_Notches.agg(['mean','std','max','min'])
'''
                 mean       std  max  min
kmean_group                              
0            0.434783  0.662371  2.0  0.0
1            0.571429  0.859463  3.0  0.0

mean    0.523077
std     0.792695
max     3.000000
min     0.000000
Name: RLA_Notches, dtype: float64

'''


# Override

data_left.groupby(by='kmean_group')['Override_Action'].agg(['mean','std','max','min'])
data_left.Override_Action.agg(['mean','std','max','min'])


'''
                 mean       std  max  min
kmean_group                              
0           -0.043478  1.988107  5.0 -7.0
1           -0.023810  0.517409  2.0 -2.0
mean   -0.030769
std     1.237048
max     5.000000
min    -7.000000
Name: Override_Action, dtype: float64

'''

# JBA

data_left.groupby(by='kmean_group')['JBA'].agg(['mean','std','max','min'])
data_left.JBA.agg(['mean','std','max','min'])

'''
                 mean       std  max  min
kmean_group                              
0            0.391304  2.147708  5.0 -7.0
1            0.547619  1.063872  3.0 -2.0
mean    0.492308
std     1.521955
max     5.000000
min    -7.000000
Name: JBA, dtype: float64

'''



#%% for func developing
data
model
k=2
top_k=10
col='NET_COMMITMENT_AMOUNT'

table_count = data.groupby('Industry_by_NAICS').sum()[col].sort_values(ascending=False)
pl_top_k = list(table_count.index)[:top_k] 
table_count2 = data.groupby('Industry_by_NAICS').size()
df = pd.concat([table_count, table_count2], axis=1)
df.columns = [col,'counts']
df.sort_values(col,ascending=False, inplace=True)
top_k_coverage = df.counts[:top_k].sum()/df.counts.sum()


data_left = data.copy()
data_top_k=pd.DataFrame()
for ind in pl_top_k:
	data_left = data_left.query('Industry_by_NAICS !="{a0}"'.format(a0=ind))
	data_top_k = pd.concat([data_top_k,data.query('Industry_by_NAICS =="{a0}"'.format(a0=ind))], axis=0)


data_left.reset_index(drop=True, inplace=True)
pl_fac = model.quant_factor + model.quali_factor
X = data_left[pl_fac]
mms = MinMaxScaler()
X_transformed = mms.fit_transform(X)
kmeans = KMeans(n_clusters=k, random_state=0).fit(X_transformed)

data_left['Industry_by_NAICS'] = kmeans.labels_
data_left['Industry_by_NAICS'] = ['Industry_KmeanGroup_'+str(x) for x in data_left['Industry_by_NAICS']]

data_kmean = pd.concat([data_top_k, data_left], axis=0)
data_left.groupby(by='Industry_by_NAICS').size()




# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 14:39:33 2019

@author: ub71894
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src\test")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
import seaborn as sns
import pickle
import matplotlib.pyplot as plt
import copy
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping, ExtRating_mapping
sns.set(palette='muted')

def override_(x):
    if x<0:
        return ('Upgrade')
    elif x>0:
        return ('Downgrade')
    else:
        return('No')



MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
# load model setting
filehandler = open(r'..\spec\model_af_calib.pkl','rb')
model = pickle.load(filehandler)

#%%
dat = pd.read_pickle(r'..\calib\norm_2010_2016.pkl.xz')
dat['quantscore'] = (model.quant_weight * dat[model.quant_factor].values).sum(axis=1)
dat['quantscore'] = 50*( dat['quantscore'] - model.quantmean) / model.quantstd
dat['qualiscore'] = (model.quali_weight * dat[model.quali_factor].values).sum(axis=1)
dat['qualiscore'] = 50*( dat['qualiscore'] - model.qualimean) / model.qualistd
dat['Totalscore'] = dat['quantscore']*model.quantweight + dat['qualiscore'] *model.qualiweight

dat_2017 = pd.read_pickle(r'..\calib\norm_test_2017.pkl.xz')
dat_2017['quantscore'] = (model.quant_weight * dat_2017[model.quant_factor].values).sum(axis=1)
dat_2017['quantscore'] = 50*( dat_2017['quantscore'] - model.quantmean) / model.quantstd
dat_2017['qualiscore'] = (model.quali_weight * dat_2017[model.quali_factor].values).sum(axis=1)
dat_2017['qualiscore'] = 50*( dat_2017['qualiscore'] - model.qualimean) / model.qualistd
dat_2017['Totalscore'] = dat_2017['quantscore']*model.quantweight + dat_2017['qualiscore'] *model.qualiweight



# double check
print(SomersD(dat.Final_PD_Risk_Rating, dat.Totalscore))
print(SomersD(dat_2017.Final_PD_Risk_Rating, dat_2017.Totalscore))


#%%
fig, ax = plt.subplots(figsize=(15,10))
sns.regplot(x='Totalscore',y='Final_PD_Risk_Rating', data=dat)
fig, ax = plt.subplots(figsize=(15,10))
sns.regplot(x='Totalscore',y='Final_PD_Risk_Rating', data=dat_2017)

#%% out-of-sample 
data = dat_2017.copy()
data['RLA'] = ['Yes' if x!=0 else 'No' for x in data[ 'RLA_Notches']]
data['Override'] = data['Override_Action'].transform(override_)
data['size'] = np.log(data['size@Net_Sales'])
data = MAUG_mapping(data)
data["Industry_by_MAUG2"] = data["Industry_by_MAUG"]
pd_rename={
'Midstream Energy':'Others',                         
'Media and Telecom':'Others',                        
'Asian Corporate Banking':'Others',                 
'Commodity Finance':'Others',                        
'Engineering and Construction':'Others',             
'Trading Asset Reliant':'Others',                    
'Auto and Auto Parts':'Others',                      
'Insurance':'Others',                                
'Independent Refining':'Others',                     
'Leasing Companies':'Others',                        
'Agribusiness':'Others'}                             
data["Industry_by_MAUG2"] = data["Industry_by_MAUG2"].replace(pd_rename)


#fig, ax = plt.subplots(figsize=(25,18))
sns.relplot(x='Totalscore', y='Final_PD_Risk_Rating', data= data,
            col="RLA", # Categorical variables that will determine the faceting of the grid.
            hue="Override", # Grouping variable that will produce elements with different colors.
            style="Industry_by_MAUG2", 
            size="size", # Grouping variable that will produce elements with different sizes.
            )


#%% core and non-core
df = data.query('Final_PD_Risk_Rating<=4')
df['Industry_by_MAUG'].value_counts()
'''
General Industries              42
Health Care                     24
Retail                           7
Technology                       7
Media and Telecom                5
Food and Beverage                4
Engineering and Construction     3
Auto and Auto Parts              1
Independent Refining             1
Name: Industry_by_MAUG, dtype: int64
'''
data['Industry_by_MAUG'].value_counts()
'''
General Industries                        377
Health Care                               108
Commercial Finance Loans                   98
Technology                                 90
Food and Beverage                          54
Retail                                     40
Independent Exploration and Production     39
Midstream Energy                           36
Media and Telecom                          32
Asian Corporate Banking                    28
Commodity Finance                          26
Engineering and Construction               23
Trading Asset Reliant                       8
Auto and Auto Parts                         8
Insurance                                   5
Independent Refining                        5
Leasing Companies                           2
Agribusiness                                1
Name: Industry_by_MAUG, dtype: int64

'''
data["Core"] = data["Industry_by_MAUG"]
pd_rename={
'General Industries':'Yes',                      
'Health Care':'Yes',                             
'Commercial Finance Loans':'Yes',                
'Technology':'Yes',                              
'Food and Beverage':'Yes',                       
'Retail':'Yes',                                  
'Independent Exploration and Production':'Yes',  
'Midstream Energy':'Non',                        
'Media and Telecom':'Non',                       
'Asian Corporate Banking':'Non',                 
'Commodity Finance':'Non',                       
'Engineering and Construction':'Non',            
'Trading Asset Reliant':'Non',                   
'Auto and Auto Parts':'Non',                     
'Insurance':'Non',                               
'Independent Refining':'Non',                    
'Leasing Companies':'Non',                       
'Agribusiness':'Non'}                             
data["Core"] = data["Core"].replace(pd_rename)


sns.relplot(x='Totalscore', y='Final_PD_Risk_Rating', data= data,
            col="RLA", # Categorical variables that will determine the faceting of the grid.
            hue="Core", # Grouping variable that will produce elements with different colors.
            style="Override", 
            )


#%% size impact
data["size"] = data['size@Net_Sales']
data["size"] = data["size"].transform(lambda x: 'Large' if x>4e9 else 'Small')


sns.relplot(x='Totalscore', y='Final_PD_Risk_Rating', data= data,
            col="RLA", # Categorical variables that will determine the faceting of the grid.
            hue="size", # Grouping variable that will produce elements with different colors.
            )




#
data = NAICS_mapping(data)
data['Industry_by_NAICS'].value_counts()




#%% in-sample 
data = dat.copy()
data['RLA'] = ['Yes' if x!=0 else 'No' for x in data[ 'RLA_Notches']]
data['Override'] = data['Override_Action'].transform(override_)
data['size'] = np.log(data['size@Net_Sales'])
data = MAUG_mapping(data)
data.dropna(subset=['Industry_by_MAUG'], inplace=True)
data["Industry_by_MAUG2"] = data["Industry_by_MAUG"]
pd_rename={
'Homeowner Association Loans':'Others',
'Institutional Real Estate Lending':'Others',
'Business Diversity Lending':'Others',
'Trading Asset Reliant':'Others',
'Media and Telecom':'Others',
'Finance and Mortgage Companies':'Others',
'Placeholder for pending Utilities Latin America':'Others',
'Placeholder for pending Metals and Mining Latin America':'Others',
'Leasing and Asset Finance Division':'Others',
'Investor Perm Loans':'Others',
'Japanese Corporate Banking in Canada':'Others',
'Engineering and Construction':'Others',
'Entertainment':'Others',
'Wine Industry':'Others',
'Business Banking':'Others'}                             
data["Industry_by_MAUG2"] = data["Industry_by_MAUG2"].replace(pd_rename)


#fig, ax = plt.subplots(figsize=(25,18))
sns.relplot(x='Totalscore', y='Final_PD_Risk_Rating', data= data,
            col="RLA", # Categorical variables that will determine the faceting of the grid.
            hue="Override", # Grouping variable that will produce elements with different colors.
            style="Industry_by_MAUG2", 
            size="size", # Grouping variable that will produce elements with different sizes.
            )


#%%
data["Core"] = data["Industry_by_MAUG"]
pd_rename={
'General Industries':'Yes',
'Commercial Finance Loans':'Yes',
'Health Care':'Yes',
'Technology':'Yes',
'Retail':'Yes',
'Auto and Auto Parts':'Yes',
'Asian Corporate Banking':'Yes',
'Homeowner Association Loans':'Yes',
'Institutional Real Estate Lending':'Yes',
'Business Diversity Lending':'Non',
'Trading Asset Reliant':'Non',
'Media and Telecom':'Non',
'Finance and Mortgage Companies':'Non',
'Placeholder for pending Utilities Latin America':'Non',
'Placeholder for pending Metals and Mining Latin America':'Non',
'Leasing and Asset Finance Division':'Non',
'Investor Perm Loans':'Non',
'Japanese Corporate Banking in Canada':'Non',
'Engineering and Construction':'Non',
'Entertainment':'Non',
'Wine Industry':'Non',
'Business Banking':'Non',}                             
data["Core"] = data["Core"].replace(pd_rename)




sns.relplot(x='Totalscore', y='Final_PD_Risk_Rating', data= data,
            col="RLA", # Categorical variables that will determine the faceting of the grid.
            hue="Core", # Grouping variable that will produce elements with different colors.
            style="Override", 
            )

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 10:25:41 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata")


prod = pd.read_pickle(r'data_201006_201712_addBranch_3_jn_withCIF.pkl.xz')
prod = prod.query('DataPeriod=="Prod" or DataPeriod=="Prod_Branch"')
prod = prod.drop_duplicates(subset=['CUSTOMERID','archive_date'])

cols = ['CUSTOMERID','archive_date',
'RLA_Category_1',
'RLA_Category_2',
'RLA_Category_3',
'RLA_Impact_Level',
'RLA_Section_Notes',
'Override_Category_1',
'Override_Category_2',
'Override_Category_3',
'Override_Justification',
'Override_Reason_1',
'Override_Reason_2',
'Override_Reason_3',
'RLA_Justification',
'RLA_Reason_1',
'RLA_Reason_2',
'RLA_Reason_3']

prod = prod[cols]


dat_mm = pd.read_pickle('dat_mm_by1000_last.pkl.xz')
dat_mm.CUSTOMERID = pd.to_numeric(dat_mm['CUSTOMERID'])
dat_mm.archive_date = pd.to_datetime(dat_mm['archive_date'])

dat_lc = pd.read_pickle('dat_lc_by1000_last.pkl.xz')
dat_lc.CUSTOMERID = pd.to_numeric(dat_lc['CUSTOMERID'])
dat_lc.archive_date = pd.to_datetime(dat_lc['archive_date'])


new_mm = pd.merge(dat_mm, prod, on=['CUSTOMERID','archive_date'], how='inner')
new_lc = pd.merge(dat_lc, prod, on=['CUSTOMERID','archive_date'], how='inner')


new_mm.to_pickle('dat_mm_by1000_last_addreasons.pkl.xz')
new_lc.to_pickle('dat_lc_by1000_last_addreasons.pkl.xz')


#%% calibrationdata:
prod = pd.read_pickle(r'data_201006_201712_addBranch_3_jn_withCIF.pkl.xz')
prod = prod.query('DataPeriod=="Prod" or DataPeriod=="Prod_Branch"')
prod = prod.drop_duplicates(subset=['CUSTOMERID','archive_date'])

cols = ['CUSTOMERID','archive_date',
'RLA_Category_1',
'RLA_Category_2',
'RLA_Category_3',
'RLA_Impact_Level',
'RLA_Notches',
'RLA_Section_Notes',
'Override_Category_1',
'Override_Category_2',
'Override_Category_3',
'Override_Justification',
'Override_Reason_1',
'Override_Reason_2',
'Override_Reason_3',
'RLA_Justification',
'RLA_Reason_1',
'RLA_Reason_2',
'RLA_Reason_3',
'Override_Action',
]

prod = prod[cols]



dat = pd.read_pickle(r'..\src\calib\norm_2010_2016.pkl.xz')
prod['timestamp'] = prod['archive_date']
new_dat = pd.merge(dat, prod, on=['CUSTOMERID','timestamp'], how='inner')




df = new_dat [['CUSTOMERID',
'Override_Category_1',
'Override_Category_2',
'Override_Category_3',
'Override_Justification',
'Override_Reason_1',
'Override_Reason_2',
'Override_Reason_3',
'Override_Action']]


pl_reason = df['Override_Category_1'].dropna().tolist()

for name in pl_reason:
    if 'Gur' in name:
        print(name)
    elif 'Gua' in name:
        print(name)
ID = 240943
df.loc[df['CUSTOMERID']==ID]

#%%

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 17 10:25:00 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata")

dat = pd.read_pickle('dat_mm_by500_last.pkl.xz')

dat.rename(columns={'Underwriter_Guideline':'MAUG'}, inplace=True)
dat.dropna(subset=['MAUG'], inplace=True)


sofar_mapping = {
 'MAUG_105': 'General Industries',
 'MAUG_110': 'Entertainment',
 'MAUG_115': 'Media and Telecom',
 'MAUG_120': 'Food and Beverage',
 'MAUG_125': 'Health Care',
 'MAUG_130': 'Insurance',
 'MAUG_135': 'Power & Utilities',
 'MAUG_140': 'Independent Exploration and Production',
 'MAUG_143': 'Midstream Energy',
 'MAUG_145': 'Independent Refining',
 'MAUG_147': 'Drilling and Oilfield Services',
 'MAUG_150': 'Auto and Auto Parts',
 'MAUG_155': 'Agribusiness',
 'MAUG_160': 'Wine Industry',
 'MAUG_165': 'Technology',
 'MAUG_170': 'Leasing Companies',
 'MAUG_175': 'Engineering and Construction',
 'MAUG_180': 'Retail',
 'MAUG_205': 'Asian Corporate Banking',
 'MAUG_210': 'Japanese Corporate Banking in Canada',
 'MAUG_215': 'Asian Corporate Leasing & Finance',
 'MAUG_305': 'Business Banking',
 'MAUG_307': 'Small Business Banking',
 'MAUG_310': 'Business Diversity Lending',
 'MAUG_320': 'Corporate Leasing Transactions',
 'MAUG_325': 'Leasing and Asset Finance Division',
 'MAUG_330': 'Project Finance',
 'MAUG_333': 'Commodity Finance',
 'MAUG_335': 'Mezzanine Finance',
 'MAUG_340': 'Commercial Finance Loans',
 'MAUG_345': 'Commodity and Structured Trade Finance',
 'MAUG_350': 'Trading Asset Reliant',
 'MAUG_355': 'Capital Call Bridge / Subscription Lending',
 'MAUG_360': 'Securities Broker / Dealers',
 'MAUG_365': 'Asset Managers',
 'MAUG_367': 'Investment Funds (Mutual Funds)',
 'MAUG_370': 'Clearinghouses and Exchanges',
 'MAUG_375': 'Industrial Development Bonds',
 'MAUG_380': 'Insured Domestic Institutions',
 'MAUG_381': 'Foreign Banks',
 'MAUG_383': 'Global Financial Solutions',
 'MAUG_385': 'Securitization',
 'MAUG_390': 'Debt Obligation and Passive Equity Investments',
 'MAUG_395': 'Individuals',
 'MAUG_405': 'Real Estate Industries',
 'MAUG_410': 'Institutional Real Estate Lending',
 'MAUG_415': 'Homeowner Association Loans',
 'MAUG_420': 'Retail Equity Equivalent Loan Program',
 'MAUG_425': 'Debtor-in-Possession Loans',
 'MAUG_430': 'Finance and Mortgage Companies',
 'MAUG_435': 'Investor Perm Loans',
 'MAUG_505': 'Community Development Financing',
 'MAUG_510': 'Public Finance',
 'MAUG_515': 'Non-Profit Organizations',
 'MAUG_605': 'Brazil Agribusiness',
 'MAUG_610': 'Placeholder for pending General Corporate Latin America',
 'MAUG_615': 'Placeholder for pending Retail Latin America',
 'MAUG_620': 'Placeholder for pending Utilities Latin America',
 'MAUG_625': 'Placeholder for pending Oil & Gas Latin America',
 'MAUG_630': 'Placeholder for pending Metals and Mining Latin America',
 'MAUG_635': 'Placeholder for pending Food and Beverage Latin America'
 }




dat.loc[:, 'MAUG'] = dat.loc[:, 'MAUG'].transform(lambda x: 'MAUG_'+x)
# 440 is old UG code and it still exist after 20160723
dat['MAUG'] = dat['MAUG'].replace(to_replace={'MAUG_440':'MAUG_125'})
# 490 is old UG code and it still exist after 20160723
dat['MAUG'] = dat['MAUG'].replace(to_replace={'MAUG_490':'MAUG_305'})

bb = dat.query('MAUG=="MAUG_305"')

#%%

import seaborn as sns
import matplotlib.pyplot as plt
sns.distplot(bb['Net_Sales'], hist=False, color="g", kde_kws={"shade": True})

#%%
pl_cutoffs = [5e6, 10e6, 20e6, 50e6, 100e6] 
for cutoff in pl_cutoffs:
    sm = bb.query('Net_Sales<{}'.format(cutoff))
    lg = bb.query('Net_Sales>={}'.format(cutoff))
    print('len of sm is ' + str(len(sm)))
    print('len of lg is ' + str(len(lg)))
    print('def of sm is ' + str(sm.def_flag.sum()))
    print('def of lg is ' + str(lg.def_flag.sum()))import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Attachdefaults import Attachdefaults

data = pd.read_pickle(r'..\newdata\data_201006_201712_addBranch_3_jn_withCIF.pkl.xz')
data.archive_date.min()
# Timestamp('2010-01-04 00:00:00')
data_bank = data.query('DataPeriod=="Prod"')
data_branch = data.query('DataPeriod=="Prod_Branch"')

defaults = pd.read_excel(r'C:\Users\ub71894\Documents\Data\MasterDefault\Master_Def_201712_addBranch.xlsx')


#%%
def1 = defaults.query('Scorecard=="C&I"')
#1468 since 1997
def2 = def1.query('L_DATE_OF_DEFAULT>20100704') # six month after Timestamp('2010-01-04 00:00:00')
# 236
def3 = def2.drop_duplicates(subset=['L_OBLIGOR','L_DATE_OF_DEFAULT'])
# 143
def4 = def3.drop_duplicates(subset=['L_OBLIGOR'])
# 134
def4['L_OBLIGOR'] = pd.to_numeric(def4['L_OBLIGOR'], errors='coerce')



def_branch = def4.query('M_Branch_Data=="Y"')
# 1 miss in match due to financial statement is not in valid time window
def_bank = def4.query('M_Branch_Data!="Y"')
# 133

bad = pd.merge(data_bank, def_bank, left_on='OBLIGOR_NUMBER', right_on='L_OBLIGOR', how='inner')

len(bad.CUSTOMERID.unique())
#103# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 11:16:53 2018

@author: ru87118
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')

import pickle
from PDScorecardTool.Process import SomersD
from PDScorecardTool.MFA import MFA
from scipy.optimize import fsolve

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')

#dat = pd.read_excel(r'..\newdata\dat_mm_by1000_last_cs.xlsx')
#dat.to_pickle(r'..\newdata\dat_mm_by1000_last_cs.pkl')
dat = pd.read_pickle(r'..\newdata\dat_mm_by1000_last_cs.pkl')

# remove guarantor impacted obs
dat['Gua_override'] =  dat['PD_Risk_Rating_After_Gtee'] - dat['PD_Risk_Rating_After_RLA']
dat = dat.query('Gua_override==0')
dat['RLA_Notches'].fillna(0, inplace=True)
dat['Override_Action'].fillna(0, inplace=True)



#dat = NAICS_mapping(dat)


#%% 
#quant score
filehandler = open(r'..\MM\model_spec_calib.pkl','rb')
model = pickle.load(filehandler)

finallist=[
'prof@NOP_to_NS',
'cf@TD_to_UBEBITDA',
'bs@TD_to_Capt',
'liq@ECE_to_TL',
'size@TangNW_to_TA'
]

dat_prod = dat.copy()
dat_prod.dropna(subset=finallist+model.quali_factor, how='any', inplace=True)
dat_prod.reset_index(drop=True, inplace=True)

dat_prod['liq@ECE_to_TL'] = np.log(dat_prod['liq@ECE_to_TL'])
dat_prod['UBEBITDA'] = dat_prod['size@Union Bank EBITDA']

cni_prod = MFA(dat_prod, model, quant_only=True)

normdat_prod = cni_prod.normdata.copy()                     

normdat_prod['quant_score'] = (0.1*normdat_prod[finallist[0]]+0.25*normdat_prod[finallist[1]]+0.25*normdat_prod[finallist[2]]+0.2*normdat_prod[finallist[3]]+0.2*normdat_prod[finallist[4]])

#%%
#qual score
'''
Empirical PD Mapping
'''
normdat_prod.loc[normdat_prod['qual1'] == 'A','qual1_score']=-111.008112
normdat_prod.loc[normdat_prod['qual1'] == 'B','qual1_score']=-32.333280
normdat_prod.loc[normdat_prod['qual1'] == 'C','qual1_score']=51.533197
normdat_prod.loc[normdat_prod['qual1'] == 'D','qual1_score']=51.533197
SomersD(normdat_prod['def_flag'],normdat_prod['qual1_score'])

normdat_prod.loc[normdat_prod['qual2'] == 'A','qual2_score']=-29.345706
normdat_prod.loc[normdat_prod['qual2'] == 'B','qual2_score']=58.589597
normdat_prod.loc[normdat_prod['qual2'] == 'C','qual2_score']=147.910114
normdat_prod.loc[normdat_prod['qual2'] == 'D','qual2_score']=59.154191
SomersD(normdat_prod['def_flag'],normdat_prod['qual2_score'])

normdat_prod.loc[normdat_prod['qual3'] == 'A','qual3_score']=-4.355004
normdat_prod.loc[normdat_prod['qual3'] == 'B','qual3_score']=(4.355004+39.244999)/2
normdat_prod.loc[normdat_prod['qual3'] == 'C','qual3_score']=39.244999
normdat_prod.loc[normdat_prod['qual3'] == 'D','qual3_score']=71.674722
normdat_prod.loc[normdat_prod['qual3'] == 'E','qual3_score']=-100.605271
normdat_prod.loc[normdat_prod['qual3'] == 'F','qual3_score']=59.357814
SomersD(normdat_prod['def_flag'],normdat_prod['qual3_score'])

normdat_prod.loc[normdat_prod['qual4'] == 'A','qual4_score']=-92.725013
normdat_prod.loc[normdat_prod['qual4'] == 'B','qual4_score']=-48.020554
normdat_prod.loc[normdat_prod['qual4'] == 'C','qual4_score']=45.765402
SomersD(normdat_prod['def_flag'],normdat_prod['qual4_score'])

normdat_prod['Management_Quality_score']=191.974630
normdat_prod.loc[normdat_prod['Management_Quality'] == 'A','Management_Quality_score']=-87.120842
normdat_prod.loc[normdat_prod['Management_Quality'] == 'B','Management_Quality_score']=-44.904700
normdat_prod.loc[normdat_prod['Management_Quality'] == 'C','Management_Quality_score']=23.602512
normdat_prod.loc[normdat_prod['Management_Quality'] == 'D','Management_Quality_score']=76.907123
normdat_prod.loc[normdat_prod['Management_Quality'] == 'E','Management_Quality_score']=191.974630
SomersD(normdat_prod['def_flag'],normdat_prod['Management_Quality_score'])

normdat_prod['qual_score'] = (0.25*normdat_prod['qual1_score']+0.15*normdat_prod['qual2_score']+0.1*normdat_prod['qual3_score']+0.3*normdat_prod['qual4_score']+0.2*normdat_prod['Management_Quality_score'])


|#%%
normdat_prod['comb_score'] = 0.6*(normdat_prod['quant_score']-model.quantmean)/model.quantstd*50 + 0.4*(normdat_prod['qual_score']-model.qualimean)/model.qualistd*50
normdat_prod['LogitPD'] = model.slope1*normdat_prod['comb_score']+model.intercept1
normdat_prod['PD'] = normdat_prod['LogitPD'].apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
np.mean(normdat_prod['PD'])
Ratings = []
for i in normdat_prod.iterrows():
    Ratings.append(sum(model.MS['new_low']<=(i[1].PD/100)))
normdat_prod['Ratings'] = Ratings

normdat_prod['Ratings_capped'] = normdat_prod['Ratings']
normdat_prod.loc[(normdat_prod['size@Total Assets']<100000000) & (normdat_prod['Ratings']<7),'Ratings_capped'] = 7

normdat_prod.loc[(np.isnan(normdat_prod['Override_Action'])),'Override_Action'] = 0
normdat_prod.loc[(np.isnan(normdat_prod['RLA_Notches'])),'RLA_Notches'] = 0
normdat_prod['Ratings_final'] = normdat_prod['Ratings_capped']+normdat_prod['RLA_Notches']+normdat_prod['Override_Action']


normdat_prod.to_pickle('MM_model.pkl')# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 16:02:23 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

dat = pd.read_pickle(r'..\newdata\prod_allgood_7daysclean_addratios_valid.pkl.xz')
factors_cols = [
 'cf@ACF',
 'size@Adjusted Capitalization',
 'size@Adjusted Total Debt',
 'size@Amortization',
 'prof@Average Profit Margin, 2 yrs',
 'size@Capitalization',
 'size@Current Assets',
 'size@Current Liabilities',
 'liq@Current Ratio',
 'ds@INTERESTEXPENSE',
 'bs@CPLTD',
 'ds@Debt Service',
 'cf@Depreciation',
 'prof@DIVIDENDSSTOCK',
 'prof@DividendCommon',
 'prof@DIVIDENDSPREF',
 'prof@Dividends',
 'size@EBIT',
 'size@EBITDA',
 'cf@Ending Cash & Equivalents',
 'prof@AFTERTAXINCOME',
 'ds@AFTERTAXEXPENSE',
 'size@Extraordinary Items',
 'size@Free Operating Cash Flow_Modified',
 'size@Funds from Operations_Modified',
 'ds@Interest Expense',
 'size@Total Inventory',
 'cf@Lease Expense',
 'size@Net Accounts Receivable',
 'size@Net Operating Profit',
 'size@Net Profit',
 'size@Net_Sales',
 'size@Profit before Taxes',
 'liq@Quick Ratio',
 'size@Retained Earnings',
 'prof@Return on Assets',
 'prof@Return on Equity',
 'bs@Senior Debt',
 'size@NETTANGIBLES',
 'size@Tangible Assets',
 'size@Tangible Net Worth',
 'others@INCOMETAXEXP',
 'others@INCOMETAXCREDIT',
 'others@Taxes',
 'size@Total Assets',
 'size@Total Debt',
 'bs@LONGTERMDEBT',
 'others@CAPLEASEOBLIG',
 'bs@Total LTD',
 'size@Total Liabilities',
 'size@Total Net Worth',
 'liq@Union Bank Current Ratio',
 'size@Union Bank EBIT',
 'size@Union Bank EBITDA',
 'liq@Union Bank Quick Ratio',
 'size@Union Bank Tangible Net Worth',
 'prof@Operating Profit Margin %',
 'prof@Net Profit Margin %',
 'prof@Gross Profit Margin %',
 'prof@Gross Profit Margin %.1',
 'size@Free Operating Cash Flow (FOCF)',
 'size@Funds from Operations (FFO)',
 'ds@INTERESTEXPENSE_2',
 'others@CAPINTEREST',
 'prof@Interest Income',
 'others@Total Interest Inc(Exp)',
 'others@INCOMETAXEXP_1',
 'others@INCOMETAXCREDIT_1',
 'others@TOTAL INCOME TAX EXPENSE',
 
 'act@NS_to_CL',
 'act@NS_to_UBTangNW',
 'act@NS_to_TA',
 'act@NS_to_NAR',
 'act@NS_to_Inv',
 'act@NS_to_TNW',
 'bs@TD_to_TA',
 'bs@TD_to_TangNW',
 'bs@TD_to_Capt',
 'bs@TD_to_AdjCapt',
 'bs@TD_to_TNW',
 'bs@TD_to_UBTangNW',
 'bs@SD_to_Capt',
 'bs@SD_to_AdjCapt',
 'bs@TLTD_to_TNW',
 'bs@TLTD_to_TA',
 'bs@TLTD_to_UBTangNW',
 'bs@TLTD_to_AdjCapt',
 'bs@TLTD_to_TangNW',
 'bs@TLTD_to_Capt',
 'bs@TL_to_UBTangNW',
 'bs@TL_to_TangNW',
 'bs@TL_to_TA',
 'bs@TL_to_TNW',
 'bs@TL_to_AdjCapt',
 'bs@TL_to_Capt',
 'bs@CL_to_UBTangNW',
 'bs@CL_to_TangNW',
 'bs@CL_to_TL',
 'bs@CL_to_TNW',
 'bs@CL_to_AdjCapt',
 'bs@CL_to_TA',
 'bs@CL_to_Capt',
 'bs@AdjTD_to_AdjCapt',
 'bs@AdjTD_to_Capt',
 'bs@TLTD_to_TLTD_and_TNW',
 'bs@TLTD_to_TLTD_and_UBTangNW',
 'bs@TD_to_CA_exc_CL',
 'bs@TD_to_TA_exc_TL',
 'bs@TL_to_TL_exc_CL',
 'cf@TD_to_UBEBITDA',
 'cf@TD_to_EBITDA',
 'cf@TD_to_ACF',
 'cf@SD_to_UBEBITDA',
 'cf@SD_to_EBITDA',
 'cf@AdjTD_to_EBITDA',
 'cf@AdjTD_to_UBEBITDA',
 'cf@AdjTD_to_ACF',
 'cf@FOCF_to_TD',
 'cf@FFO_to_TD',
 'cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',
 'cf@AdjTD_to_ACF_and_LE',
 'cf@AdjTD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@TD_to_EBIT_exc_Div_exc_Taxes',
 'cf@TD_to_ACF_and_LE',
 'ds@NP_to_TL',
 'ds@NP_to_CL',
 'ds@NP_to_IE',
 'ds@UBEBIT_to_IE',
 'ds@UBEBIT_to_DS',
 'ds@EBIT_to_IE',
 'ds@EBIT_to_DS',
 'ds@UBEBITDA_to_IE',
 'ds@EBITDA_to_IE',
 'ds@FFO_to_IE',
 'ds@NS_to_IE',
 'ds@TL_to_IE',
 'ds@ACF_to_DS',
 'ds@ACF_and_LE_to_DS_and_LE',
 'ds@EBIT_exc_Div_exc_Taxes_to_IE',
 'ds@UBEBIT_and_LE_to_DS_and_LE',
 'ds@UBEBIT_exc_Div_exc_Taxes_to_IE',
 'ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
 'ds@UBEBIT_exc_Div_exc_Taxes_to_DS',
 'ds@EBIT_exc_Div_exc_Taxes_to_DS',
 'ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
 'ds@EBIT_and_LE_to_DS_and_LE',
 'ds@NP_and_IE_to_IE',
 'ds@NP_and_IE_to_TL',
 'liq@ECE_to_TD',
 'liq@ECE_to_TL',
 'liq@ECE_to_AdjTD',
 'liq@ECE_to_TA',
 'liq@ECE_to_CL',
 'liq@ECE_to_CA',
 'liq@CA_to_TL',
 'liq@CA_to_TA',
 'liq@RE_to_CL',
 'liq@CA_exc_TI_to_TD',
 'liq@CA_exc_TI_to_/TL',
 'liq@CA_exc_TI_to_/AdjTD',
 'liq@CA_exc_TI_to_/TA',
 'liq@CA_exc_CL_to_TD',
 'liq@CA_exc_CL_to_TL',
 'liq@CA_exc_CL_to_AdjTD',
 'liq@CA_exc_CL_to_TA',
 'liq@CA_exc_CL_to_CA',
 'liq@CA_exc_CL_to_CL',
 'prof@EBIT_to_AdjCapt',
 'prof@EBIT_to_Capt',
 'prof@EBIT_to_NS',
 'prof@EBIT_to_TangA',
 'prof@EBIT_to_TA',
 'prof@EBITDA_to_AdjCapt',
 'prof@EBITDA_to_Capt',
 'prof@EBITDA_to_NS',
 'prof@EBITDA_to_TangA',
 'prof@EBITDA_to_TA',
 'prof@NOP_to_NP',
 'prof@NOP_to_NS',
 'prof@NOP_to_TangNW',
 'prof@NOP_to_TA',
 'prof@NOP_to_TNW',
 'prof@NOP_to_UBTangNW',
 'prof@RE_to_TA',
 'prof@RE_to_TNW',
 'prof@RE_to_UBTangNW',
 'prof@UBEBIT_to_AdjCapt',
 'prof@UBEBIT_to_Capt',
 'prof@UBEBIT_to_NS',
 'prof@UBEBIT_to_TangA',
 'prof@UBEBIT_to_TA',
 'prof@UBEBITDA_to_AdjCapt',
 'prof@UBEBITDA_to_Capt',
 'prof@UBEBITDA_to_NS',
 'prof@UBEBITDA_to_TangA',
 'prof@UBEBITDA_to_TA',
 'prof@PbT_to_TA',
 'prof@CD_to_NP',
 'prof@NP_exc_EI',
 'prof@EBIT_exc_II_to_Capt',
 'prof@NP_exc_EI_to_TA',
 'size@TangNW_to_TA',
 'size@TangNW_to_TA_exc_CA',
 'size@UBTangNW_to_TA',
 'size@UBTangNW_to_TA_exc_CA',
 'size@TNW_to_TA_exc_CA',
 'size@TNW_to_TA',
 'BTMU@TD_to_EBITDA',
 'BTMU@EBITDA_to_IE',
 'BTMU@TNW_to_TA',
 'BTMU@TD_to_TNW',
 'BTMU@OP_to_Sales',
 'BTMU@NP_exc_EI_to_TA',
 'SP@TD_to_TD_and_TNW',
 'SP@EBIT_to_TD_and_TNW',
 'SP@EBIT_to_IE',
 'SP@EBITDA_to_IE',
 'quant1', 'quant2', 'quant3', 'quant4', 'quant5',
 'Net_Sales']

target_cols=[ 'Prelim_PD_Risk_Rating_Uncap', 'Final_PD_Risk_Rating', 'def_flag']

data = dat[factors_cols+target_cols].copy()

#%% get SFA 
pl_cutoff = [400, 500, 600]
LC_def=pd.DataFrame();  LC_PDRR=pd.DataFrame(); LC_quality=pd.DataFrame()
MM_def=pd.DataFrame();  MM_PDRR=pd.DataFrame(); MM_quality=pd.DataFrame()

for cut in pl_cutoff:
    cutoff = cut*1e6
    #LC
    dat_LC = data.query('Net_Sales>={}'.format(cutoff))
    N = len(dat_LC)
    pl_quality=[];  pl_somersd_def=[];   pl_somersd_PDRR=[]    
    for factor in factors_cols:
        df = dat_LC[[factor, 'def_flag','Final_PD_Risk_Rating']].copy()
        df.dropna(how='any', inplace=True)
        pl_quality.append(len(df)/N)
        pl_somersd_def.append(np.abs(SomersD(df.def_flag, df[factor])))
        pl_somersd_PDRR.append(np.abs(SomersD(df.Final_PD_Risk_Rating, df[factor])))
    LC_def['Cutoff_at_'+str(cut)+'MM'] = pl_somersd_def
    LC_PDRR['Cutoff_at_'+str(cut)+'MM'] = pl_somersd_PDRR
    LC_quality['Cutoff_at_'+str(cut)+'MM'] = pl_quality
    LC_def.index=LC_PDRR.index=LC_quality.index=factors_cols
    #MM
    dat_MM = data.query('Net_Sales<{}'.format(cutoff))
    N = len(dat_MM)
    pl_quality=[];  pl_somersd_def=[];   pl_somersd_PDRR=[]    
    for factor in factors_cols:
        df = dat_MM[[factor, 'def_flag','Final_PD_Risk_Rating']].copy()
        df.dropna(how='any', inplace=True)
        pl_quality.append(len(df)/N)
        pl_somersd_def.append(np.abs(SomersD(df.def_flag, df[factor])))
        pl_somersd_PDRR.append(np.abs(SomersD(df.Final_PD_Risk_Rating, df[factor])))
    MM_def['Cutoff_at_'+str(cut)+'MM'] = pl_somersd_def
    MM_PDRR['Cutoff_at_'+str(cut)+'MM'] = pl_somersd_PDRR
    MM_quality['Cutoff_at_'+str(cut)+'MM'] = pl_quality
    MM_def.index=MM_PDRR.index=MM_quality.index=factors_cols


LC_def['diff_400&500'] = np.abs(LC_def['Cutoff_at_400MM']-LC_def['Cutoff_at_500MM'])
LC_def['diff_500&600'] = np.abs(LC_def['Cutoff_at_500MM']-LC_def['Cutoff_at_600MM'])
LC_def = LC_def[['Cutoff_at_400MM','diff_400&500','Cutoff_at_500MM','diff_500&600','Cutoff_at_600MM']]
LC_def.sort_values(by='Cutoff_at_500MM', inplace=True, ascending=False)

MM_def['diff_400&500'] = np.abs(MM_def['Cutoff_at_400MM']-MM_def['Cutoff_at_500MM'])
MM_def['diff_500&600'] = np.abs(MM_def['Cutoff_at_500MM']-MM_def['Cutoff_at_600MM'])
MM_def = MM_def[['Cutoff_at_400MM','diff_400&500','Cutoff_at_500MM','diff_500&600','Cutoff_at_600MM']]
MM_def.sort_values(by='Cutoff_at_500MM', inplace=True, ascending=False)

LC_PDRR['diff_400&500'] = np.abs(LC_PDRR['Cutoff_at_400MM']-LC_PDRR['Cutoff_at_500MM'])
LC_PDRR['diff_500&600'] = np.abs(LC_PDRR['Cutoff_at_500MM']-LC_PDRR['Cutoff_at_600MM'])
LC_PDRR = LC_PDRR[['Cutoff_at_400MM','diff_400&500','Cutoff_at_500MM','diff_500&600','Cutoff_at_600MM']]
LC_PDRR.sort_values(by='Cutoff_at_500MM', inplace=True, ascending=False)

MM_PDRR['diff_400&500'] = np.abs(MM_PDRR['Cutoff_at_400MM']-MM_PDRR['Cutoff_at_500MM'])
MM_PDRR['diff_500&600'] = np.abs(MM_PDRR['Cutoff_at_500MM']-MM_PDRR['Cutoff_at_600MM'])
MM_PDRR = MM_PDRR[['Cutoff_at_400MM','diff_400&500','Cutoff_at_500MM','diff_500&600','Cutoff_at_600MM']]
MM_PDRR.sort_values(by='Cutoff_at_500MM', inplace=True, ascending=False)

LC_quality.sort_values(by='Cutoff_at_500MM', inplace=True, ascending=False)
MM_quality.sort_values(by='Cutoff_at_500MM', inplace=True, ascending=False)


#%%
writer = pd.ExcelWriter(r'SFA\SFA_overall_quant.xlsx')

LC_def.to_excel(writer, 'LC_def')
LC_PDRR.to_excel(writer, 'LC_PDRR')
LC_quality.to_excel(writer, 'LC_quality')

MM_def.to_excel(writer, 'MM_def')
MM_PDRR.to_excel(writer, 'MM_PDRR')
MM_quality.to_excel(writer, 'MM_quality')

writer.save()

# -*- coding: utf-8 -*-
"""
Created on Tue May  1 11:30:40 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD

cutoff = 5e8
dat = pd.read_pickle(r'..\newdata\prod_allgood_7daysclean_addratios_valid.pkl.xz')
dat.rename(columns={'Net Sales':'Net_Sales'}, inplace=True)
dat_LC = dat.query('Net_Sales>={}'.format(cutoff))
dat_MM = dat.query('Net_Sales<{}'.format(cutoff))

LC_def = pd.read_excel(r'SFA\SFA_overall_quant.xlsx', sheetname='LC_def')
LC_PDRR = pd.read_excel(r'SFA\SFA_overall_quant.xlsx', sheetname='LC_PDRR')
MM_def = pd.read_excel(r'SFA\SFA_overall_quant.xlsx', sheetname='MM_def')
MM_PDRR = pd.read_excel(r'SFA\SFA_overall_quant.xlsx', sheetname='MM_PDRR')

bs=[
'bs@AdjTD_to_AdjCapt',
'bs@AdjTD_to_Capt',
'bs@CL_to_AdjCapt',
'bs@CL_to_Capt',
'bs@CL_to_TA',
'bs@CL_to_TL',
'bs@CL_to_TNW',
'bs@CL_to_TangNW',
'bs@CL_to_UBTangNW',
'bs@CPLTD',
'bs@LONGTERMDEBT',
'bs@SD_to_AdjCapt',
'bs@SD_to_Capt',
'bs@Senior Debt',
'bs@TD_to_AdjCapt',
'bs@TD_to_CA_exc_CL',
'bs@TD_to_Capt',
'bs@TD_to_TA',
'bs@TD_to_TA_exc_TL',
'bs@TD_to_TNW',
'bs@TD_to_TangNW',
'bs@TD_to_UBTangNW',
'bs@TLTD_to_AdjCapt',
'bs@TLTD_to_Capt',
'bs@TLTD_to_TA',
'bs@TLTD_to_TLTD_and_TNW',
'bs@TLTD_to_TLTD_and_UBTangNW',
'bs@TLTD_to_TNW',
'bs@TLTD_to_TangNW',
'bs@TLTD_to_UBTangNW',
'bs@TL_to_AdjCapt',
'bs@TL_to_Capt',
'bs@TL_to_TA',
'bs@TL_to_TL_exc_CL',
'bs@TL_to_TNW',
'bs@TL_to_TangNW',
'bs@TL_to_UBTangNW',
'bs@Total LTD']


cf=[
'cf@ACF',
'cf@AdjTD_to_ACF',
'cf@AdjTD_to_ACF_and_LE',
'cf@AdjTD_to_EBITDA',
'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',
'cf@AdjTD_to_NP_and_Dep_and_Amo',
'cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div',
'cf@AdjTD_to_UBEBITDA',
'cf@Depreciation',
'cf@Ending Cash & Equivalents',
'cf@FFO_to_TD',
'cf@FOCF_to_TD',
'cf@Lease Expense',
'cf@SD_to_EBITDA',
'cf@SD_to_UBEBITDA',
'cf@TD_to_ACF',
'cf@TD_to_ACF_and_LE',
'cf@TD_to_EBITDA',
'cf@TD_to_EBIT_exc_Div_exc_Taxes',
'cf@TD_to_NP_and_Dep_and_Amo',
'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',
'cf@TD_to_UBEBITDA']

ds=[
'ds@ACF_and_LE_to_DS_and_LE',
'ds@ACF_to_DS',
'ds@AFTERTAXEXPENSE',
'ds@Debt Service',
'ds@EBITDA_to_IE',
'ds@EBIT_and_LE_to_DS_and_LE',
'ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
'ds@EBIT_exc_Div_exc_Taxes_to_DS',
'ds@EBIT_exc_Div_exc_Taxes_to_IE',
'ds@EBIT_to_DS',
'ds@EBIT_to_IE',
'ds@FFO_to_IE',
'ds@INTERESTEXPENSE',
'ds@INTERESTEXPENSE_2',
'ds@Interest Expense',
'ds@NP_and_IE_to_IE',
'ds@NP_and_IE_to_TL',
'ds@NP_to_CL',
'ds@NP_to_IE',
'ds@NP_to_TL',
'ds@NS_to_IE',
'ds@TL_to_IE',
'ds@UBEBITDA_to_IE',
'ds@UBEBIT_and_LE_to_DS_and_LE',
'ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',
'ds@UBEBIT_exc_Div_exc_Taxes_to_DS',
'ds@UBEBIT_exc_Div_exc_Taxes_to_IE',
'ds@UBEBIT_to_DS',
'ds@UBEBIT_to_IE']

liq=[
'liq@CA_exc_CL_to_AdjTD',
'liq@CA_exc_CL_to_CA',
'liq@CA_exc_CL_to_CL',
'liq@CA_exc_CL_to_TA',
'liq@CA_exc_CL_to_TD',
'liq@CA_exc_CL_to_TL',
'liq@CA_exc_TI_to_/AdjTD',
'liq@CA_exc_TI_to_/TA',
'liq@CA_exc_TI_to_/TL',
'liq@CA_exc_TI_to_TD',
'liq@CA_to_TA',
'liq@CA_to_TL',
'liq@Current Ratio',
'liq@ECE_to_AdjTD',
'liq@ECE_to_CA',
'liq@ECE_to_CL',
'liq@ECE_to_TA',
'liq@ECE_to_TD',
'liq@ECE_to_TL',
'liq@Quick Ratio',
'liq@RE_to_CL',
'liq@Union Bank Current Ratio',
'liq@Union Bank Quick Ratio']


act = [
'act@NS_to_CL',
'act@NS_to_Inv',
'act@NS_to_NAR',
'act@NS_to_TA',
'act@NS_to_TNW',
'act@NS_to_UBTangNW']

curr_factors=[
 'quant2',
 'quant4']

prof=[
'prof@AFTERTAXINCOME',
'prof@Average Profit Margin, 2 yrs',
'prof@CD_to_NP',
'prof@DIVIDENDSPREF',
'prof@DIVIDENDSSTOCK',
'prof@DividendCommon',
'prof@Dividends',
'prof@EBITDA_to_AdjCapt',
'prof@EBITDA_to_Capt',
'prof@EBITDA_to_NS',
'prof@EBITDA_to_TA',
'prof@EBITDA_to_TangA',
'prof@EBIT_exc_II_to_Capt',
'prof@EBIT_to_AdjCapt',
'prof@EBIT_to_Capt',
'prof@EBIT_to_NS',
'prof@EBIT_to_TA',
'prof@EBIT_to_TangA',
'prof@Gross Profit Margin %',
'prof@Gross Profit Margin %.1',
'prof@Interest Income',
'prof@NOP_to_NP',
'prof@NOP_to_NS',
'prof@NOP_to_TA',
'prof@NOP_to_TNW',
'prof@NOP_to_TangNW',
'prof@NOP_to_UBTangNW',
'prof@NP_exc_EI',
'prof@NP_exc_EI_to_TA',
'prof@Net Profit Margin %',
'prof@Operating Profit Margin %',
'prof@PbT_to_TA',
'prof@RE_to_TA',
'prof@RE_to_TNW',
'prof@RE_to_UBTangNW',
'prof@Return on Assets',
'prof@Return on Equity',
'prof@UBEBITDA_to_AdjCapt',
'prof@UBEBITDA_to_Capt',
'prof@UBEBITDA_to_NS',
'prof@UBEBITDA_to_TA',
'prof@UBEBITDA_to_TangA',
'prof@UBEBIT_to_AdjCapt',
'prof@UBEBIT_to_Capt',
'prof@UBEBIT_to_NS',
'prof@UBEBIT_to_TA',
'prof@UBEBIT_to_TangA']


size=[
'size@Adjusted Capitalization',
'size@Adjusted Total Debt',
'size@Amortization',
'size@Capitalization',
'size@Current Assets',
'size@Current Liabilities',
'size@EBIT',
'size@EBITDA',
'size@Extraordinary Items',
'size@Free Operating Cash Flow (FOCF)',
'size@Free Operating Cash Flow_Modified',
'size@Funds from Operations (FFO)',
'size@Funds from Operations_Modified',
'size@NETTANGIBLES',
'size@Net Accounts Receivable',
'size@Net Operating Profit',
'size@Net Profit',
'size@Net_Sales',
'size@Profit before Taxes',
'size@Retained Earnings',
'size@TNW_to_TA',
'size@TNW_to_TA_exc_CA',
'size@TangNW_to_TA',
'size@TangNW_to_TA_exc_CA',
'size@Tangible Assets',
'size@Tangible Net Worth',
'size@Total Assets',
'size@Total Debt',
'size@Total Inventory',
'size@Total Liabilities',
'size@Total Net Worth',
'size@UBTangNW_to_TA',
'size@UBTangNW_to_TA_exc_CA',
'size@Union Bank EBIT',
'size@Union Bank EBITDA',
'size@Union Bank Tangible Net Worth']

len(bs+cf+ds+liq+act+size+prof)
#201

rate = 80/201


#%% LC, final PDRR,  
n_bs = round(rate*len(bs))
LC_PDRR_bs = LC_PDRR.loc[bs,:]
LC_PDRR_bs.sort_values(by='Cutoff_at_500MM', ascending=False, inplace=True)
LC_PDRR_bs = LC_PDRR_bs.iloc[:n_bs,:]
bs = LC_PDRR_bs.index.tolist()


n_cf = round(rate*len(cf))
LC_PDRR_cf = LC_PDRR.loc[cf,:]
LC_PDRR_cf.sort_values(by='Cutoff_at_500MM', ascending=False, inplace=True)
LC_PDRR_cf = LC_PDRR_cf.iloc[:n_cf,:]
cf = LC_PDRR_cf.index.tolist()


n_ds = round(rate*len(ds))
LC_PDRR_ds = LC_PDRR.loc[ds,:]
LC_PDRR_ds.sort_values(by='Cutoff_at_500MM', ascending=False, inplace=True)
LC_PDRR_ds = LC_PDRR_ds.iloc[:n_ds,:]
ds = LC_PDRR_ds.index.tolist()

n_liq = round(rate*len(liq))
LC_PDRR_liq = LC_PDRR.loc[liq,:]
LC_PDRR_liq.sort_values(by='Cutoff_at_500MM', ascending=False, inplace=True)
LC_PDRR_liq = LC_PDRR_liq.iloc[:n_liq,:]
liq = LC_PDRR_liq.index.tolist()


n_prof = round(rate*len(prof))
LC_PDRR_prof = LC_PDRR.loc[prof,:]
LC_PDRR_prof.sort_values(by='Cutoff_at_500MM', ascending=False, inplace=True)
LC_PDRR_prof = LC_PDRR_prof.iloc[:n_prof,:]
prof = LC_PDRR_prof.index.tolist()


n_size = round(rate*len(size))
LC_PDRR_size = LC_PDRR.loc[size,:]
LC_PDRR_size.sort_values(by='Cutoff_at_500MM', ascending=False, inplace=True)
LC_PDRR_size = LC_PDRR_size.iloc[:n_size,:]
size = LC_PDRR_size.index.tolist()


n_act = round(rate*len(act))
LC_PDRR_act = LC_PDRR.loc[act,:]
LC_PDRR_act.sort_values(by='Cutoff_at_500MM', ascending=False, inplace=True)
LC_PDRR_act = LC_PDRR_act.iloc[:n_act,:]
act = LC_PDRR_act.index.tolist()


# get the long list of quant factors.
longlist = bs+cf+ds+liq+act+size+prof
len(longlist)

#%% get short list

#for 'bs','cf','ds','liq','size', and 'prof', we choose top 4 candidates
shortlist = bs[:4] + cf[:4] + ds[:4] + liq[:4] + size[:4] + prof[:4] +act + curr_factors
LC_PDRR_shortlist = LC_PDRR.loc[shortlist,:]
LC_corr = dat_LC[shortlist].corr()
LC_corr.to_excel('corr_LC.xlsx')



# get a final list:

finallist = bs[:3] + cf[:3] + ds[:3] + liq[:3] + size[:3] + prof[:3] + act[:2] + curr_factors[:2]
LC_PDRR_finallist = LC_PDRR.loc[finallist,:]
LC_corr = dat_LC[finallist].corr()
LC_corr.to_excel('corr_LC_final.xlsx')

finallist=[
 'bs@TL_to_TA',
 #'bs@AdjTD_to_AdjCapt',			removed. correlated with 'bs@TL_to_TA'
 #'bs@TD_to_Capt',					removed. smaller somersd
 #'cf@Ending Cash & Equivalents',	removed. business concern 
 'cf@AdjTD_to_UBEBITDA',
 #'cf@ACF',							removed. smaller somersd
 #'ds@NP_to_TL',					removed. correlated with other 3 candidates
 #'ds@NP_to_CL',					removed. correlated with other 3 candidates
 'ds@NP_to_IE',
 'liq@ECE_to_TL',
 #'liq@ECE_to_CL',					removed. correlated with  'liq@ECE_to_TL'
 #'liq@ECE_to_CA',					removed. smaller somersd
 'size@Net Profit',
 #'size@Profit before Taxes',		removed. correlated with  'size@Net Profit'
 #'size@Retained Earnings',			removed. smaller somersd
 #'prof@NP_exc_EI',					removed. correlated with  'size@Net Profit'
 'prof@Net Profit Margin %',
 #'prof@EBIT_to_NS',				removed. correlated with  'prof@Net Profit Margin %'
 'act@NS_to_TNW',
 #'act@NS_to_TA',					removed. smaller somersd
 'quant2',
 #'quant4'							removed. smaller somersd
 ]





cols = LC_corr.columns.tolist()
pl_best=[]; pl_others=[]
for name in cols:
    temp = sum(np.abs(LC_corr[name])>0.7)
    if temp==1:
        pl_best.append(name)
    else:
        pl_others.append(name)


# -*- coding: utf-8 -*-
"""
Created on Tue Oct  2 10:22:58 2018

@author: ub71894 (4e8e6d0b), CSG
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import SomersD
from PDScorecardTool.PDModel import PDModel
from PDScorecardTool.MFA import MFA
from PDScorecardTool.Process import getTotalscore, getPDRR, getTM

postfix = "2016"
X_train = pd.read_pickle(r'MFA\train_{}.pkl.xz'.format(postfix))

quant_factor = ['Net_Profit_Margin','Total_Debt_By_COP','Total_Assets','Total_Liab_by_Tang_Net_Worth','End_Cash_Equiv_By_Tot_Liab']
quali_factor = ['Strength_SOR_Prevent_Default','Level_Waiver_Covenant_Mod','Mgmt_Resp_Adverse_Conditions','Vulnerability_To_Changes']
PDInfo_file = r'C:\Users\ub71894\Documents\DevRepo\Files\PDModelParameters.xlsx'
masterscale_file = r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx'
model_name = 'C&I'; version = 1.2
model = PDModel(PDInfo_file, model_name, version, quant_factor, quali_factor, masterscale_file)


X_train['Net_Profit_Margin'] = X_train['prof@Net Profit Margin %'] / 100
X_train['Total_Debt_By_COP'] = X_train['cf@TD_COP']
X_train['Total_Assets'] = X_train['size@Total Assets']
X_train['Total_Liab_by_Tang_Net_Worth'] = X_train['bs@TL_to_TNW']
X_train['End_Cash_Equiv_By_Tot_Liab'] = X_train['liq@ECE_to_TL']


X_train['Strength_SOR_Prevent_Default'] = X_train['qual1']
X_train['Level_Waiver_Covenant_Mod'] = X_train['qual2']
X_train['Mgmt_Resp_Adverse_Conditions'] = X_train['qual3']
X_train['Vulnerability_To_Changes'] = X_train['qual4']

X_train['Cash_Operating_Profit'] = -100
X_train['Tangible_Net_Worth'] =  X_train['size@Tangible Net Worth']



cols=[ 'CUSTOMERID', 'timestamp', 'Prelim_PD_Risk_Rating_Uncap', 'Final_PD_Risk_Rating',
		'Cash_Operating_Profit', 'Tangible_Net_Worth']\
	 + model.quant_factor + model.quali_factor

df = X_train[cols].copy()
# quant2: COP
df = df.query('timestamp>20120101')
#%%

df2 = getPDRR(df, model, ms_ver='old')

df2['diff'] = df2['Ratings'] - df2['Prelim_PD_Risk_Rating_Uncap']# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 10:16:23 2018

"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")

data_train = pd.read_pickle(r'MFA\train_2016.pkl.xz')
data_train['archive_date'] = data_train['timestamp']

prod = pd.read_excel(r'..\newdata\CNI_RA_VIEW_cs.xlsx')
prod.drop_duplicates(subset=['CUSTOMERID','archive_date'], inplace=True)
prod = prod.drop_duplicates(subset=['CUSTOMERID','archive_date'])
cols=[
 'CUSTOMERID',
 'archive_date', 
 'RLA_Category_1',
 'RLA_Category_2',
 'RLA_Category_3',
 'RLA_Justification',
 'Override_Category_1',
 'Override_Category_2',
 'Override_Category_3',
 'Override_Justification',
 'Override_Reason_1',
 'Override_Reason_2',
 'Override_Reason_3',
 ]

prod = prod[cols]

newdata = pd.merge(data_train, prod, on=['CUSTOMERID','archive_date'], how='left')
newdata = newdata.query('dataset=="production"')
cols=[
 'CUSTOMERID',
 'Customer Long Name',
 'archive_date',
 'ExternalRating_PDRR',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'NAICS',
 'NAICS_Cd',
 'RLA_Notches',
 'RLA_Category_1',
 'RLA_Category_2',
 'RLA_Category_3',
 'RLA_Justification',
 'Override_Action',
 'Override_Category_1',
 'Override_Category_2',
 'Override_Category_3',
 'Override_Reason_1',
 'Override_Reason_2',
 'Override_Reason_3',
 'Override_Justification']


df = newdata[cols]
df['year'] = [x.year for x in df['archive_date']]
df['count']=1

#%% RLA rate in train sample (prod<20160101)
N = len(df) # 3831
len(df.query('RLA_Notches!=0')) / N
#0.22996606630122685



#%% Override rate in train sample (prod<20160101)
N = len(df) # 3831
len(df.query('Override_Action!=0')) / N
#0.25554685460715215



#%% summary
writer = pd.ExcelWriter('RLA_Override_breakdown.xlsx')
rla1=df.groupby(by=['RLA_Category_1']).count()['count']
rla2=df.groupby(by=['RLA_Category_2']).count()['count']
rla3=df.groupby(by=['RLA_Category_3']).count()['count']
res = pd.concat([rla1,rla2,rla3])
res = res.reset_index().groupby(by='index').sum()
newindex = []
for id in res.index.tolist():
    newid = 'RLA_'+id
    newindex.append(newid)
res.index = newindex
res.to_excel(writer, 'RLA_all')

Override1=df.groupby(by=['Override_Category_1']).count()['count']
Override2=df.groupby(by=['Override_Category_2']).count()['count']
Override3=df.groupby(by=['Override_Category_3']).count()['count']
res2 = pd.concat([Override1,Override2,Override3])
res2 = res2.reset_index().groupby(by='index').sum()
newindex = []
for id in res2.index.tolist():
    newid = 'Override_'+id
    newindex.append(newid)
res2.index = newindex
res2.to_excel(writer, 'Override_all')



#%%
rla1=df.groupby(by=['RLA_Category_1','year']).count()['count']
rla2=df.groupby(by=['RLA_Category_2','year']).count()['count']
rla3=df.groupby(by=['RLA_Category_3','year']).count()['count']
res = pd.concat([rla1,rla2,rla3])
res = res.reset_index().groupby(by=['RLA_Category_1','year']).sum()
res = res.reset_index()

res2 = pd.pivot_table(res, values='count', index=['RLA_Category_1'], columns=['year'])
res2['sum'] = res2.sum(axis=1)
res2.to_excel(writer, 'RLA_by_year')


Override1=df.groupby(by=['Override_Category_1','year']).count()['count']
Override2=df.groupby(by=['Override_Category_2','year']).count()['count']
Override3=df.groupby(by=['Override_Category_3','year']).count()['count']
res3 = pd.concat([Override1,Override2,Override3])
res3 = res3.reset_index().groupby(by=['Override_Category_1','year']).sum()
res3 = res3.reset_index()

res4 = pd.pivot_table(res3, values='count', index=['Override_Category_1'], columns=['year'])
res4['sum'] = res4.sum(axis=1)
res4.to_excel(writer, 'Override_by_year')





#%%
#df2 = df.query('Override_Category_1=="Structured"')
#df2.to_excel('temp.xlsx')
df2 = pd.read_excel('temp.xlsx')
res5 = df2.groupby(by=['Override_Reason_1']).count()['count']
res5.to_excel(writer, 'StructuredOverride_all')


res6 = pd.pivot_table(df2, values='count', index=['Override_Reason_1'], columns=['year'],aggfunc='sum' )
res6['sum'] = res6.sum(axis=1)

res6.to_excel(writer, 'StructuredOverride_by_year')
writer.save()
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 10 16:19:05 2018

@author: ub71894 (4e8e6d0b), CSG
"""

'''
1. Quant development sample	
2. Qual development sample	
3. Out of sample – rating related	
4. Out of sample – default related	
'''

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src")

# whole train sample
#X_train = pd.read_pickle(r'MFA\train_2016.pkl.xz')
#X_train.to_csv(r'train_2016.csv')
X_train = pd.read_csv(r'train_2016.csv')

#X_test = pd.read_pickle(r'MFA\test_2017.pkl.xz')
#X_test.to_csv(r'test_2017.csv')
X_test = pd.read_csv(r'test_2017.csv')


#%% 1. Quant development sample	

dat = X_train.copy()
dat.dropna(subset=['prof@EBITDA_to_NS', 'cf@TD_to_EBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@EBITDA_to_IE'], \
	how='any', inplace=True)  # drop 6 obs
dat.reset_index(drop=True, inplace=True)


'''
dat.timestamp.min()
Out[36]: Timestamp('1998-01-03 00:00:00')

dat.timestamp.max()
Out[37]: Timestamp('2015-12-31 00:00:00')
'''

# #def
dat.def_flag.sum()
# 6

# #Obs
len(dat)
# 5383

# #Unique Obligors
len(dat['CUSTOMERID'].unique())
# 424


#%% 2. Qual development sample	
dat = X_train.copy()
pl_qualifactors=[ 'qual1', 'qual2',  'Management_Quality','qual4', 'Access_Outside_Capital']
dat.dropna(subset=pl_qualifactors, how='any', inplace=True) # drop 1689
dat.reset_index(drop=True, inplace=True)


'''
dat.timestamp.min()
Out[62]: '2010-01-04'

dat.timestamp.max()
Out[63]: '2015-12-31'
'''

# #def
dat.def_flag.sum()
# 5

# #Obs
len(dat)
# 3700

# #Unique Obligors
len(dat['CUSTOMERID'].unique())
# 406



#%% 3. Out of sample – rating related	
dat = X_test.copy()
pl_qualifactors=[ 'qual1', 'qual2',  'Management_Quality','qual4', 'Access_Outside_Capital']
dat.dropna(subset=pl_qualifactors, how='any', inplace=True) # drop 27
dat.reset_index(drop=True, inplace=True)


'''
dat.timestamp.min()
Out[75]: '2017-01-03'

dat.timestamp.max()
Out[76]: '2017-12-28'
'''

# #def
dat.def_flag.sum()
# 0

# #Obs
len(dat)
# 980

# #Unique Obligors
len(dat['CUSTOMERID'].unique())
# 495
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 11 15:09:46 2018

@author: ub71894 (4e8e6d0b), CSG
"""


import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\newdata")

#dat = pd.read_pickle('dat_hist_7daysclean_addratios_valid.pkl.xz')


lc_hist = pd.read_pickle('hist_lc_by500_last.pkl.xz')
lc_hist = lc_hist[['CUSTOMERID','STATEMENTDATE','Tax ID']]
lc_hist.drop_duplicates(subset=['CUSTOMERID','STATEMENTDATE'], inplace=True)

lc = pd.read_pickle('dat_lc_by500_last.pkl.xz')
lc = lc[['CUSTOMERID','archive_date','Tax ID']]
lc.drop_duplicates(subset=['CUSTOMERID','archive_date'], inplace=True)






dat = pd.read_excel('S&P Rating Mapping Data 070818.xlsx')
dat.dropna(subset=['EIN'], inplace=True)
dat['Tax ID'] = [x.replace('-','') for x in dat['EIN'].tolist()]
dat = dat[['ratingDate','Tax ID']]
dat.dropna(subset=['ratingDate','Tax ID'], how='any', inplace=True)
dat.drop_duplicates(subset=['ratingDate','Tax ID'], inplace=True)



#%% for hist
new_hist = pd.merge(mm_hist, dat, on=['Tax ID'], how='inner')
new_hist['ratingDate'] = pd.to_datetime(new_hist['ratingDate'])
new_hist['STATEMENTDATE'] = pd.to_datetime(new_hist['STATEMENTDATE'])
new_hist_prior = new_hist.query('ratingDate < STATEMENTDATE')
new_hist_prior.sort_values(by=['CUSTOMERID','STATEMENTDATE','ratingDate'], inplace=True)
new_hist_prior.drop_duplicates(subset=['CUSTOMERID','STATEMENTDATE'], keep='last', inplace=True)
new_hist_prior['lag'] = new_hist_prior.STATEMENTDATE - new_hist_prior.ratingDate 

new_hist_prior.lag.describe()
new_hist_prior.STATEMENTDATE.describe()
'''
count                         1959
mean      964 days 15:32:54.233792
std       981 days 04:03:12.125825
min                0 days 12:52:38
25%       262 days 22:59:38.500000
50%              657 days 13:04:36
75%      1335 days 00:20:59.500000
max             6318 days 00:00:00
Name: lag, dtype: object
'''
new_hist_prior[new_hist_prior.lag < pd.Timedelta('730 days')]



#%% for curr
new = pd.merge(lc, dat, on=['Tax ID'], how='inner')
new['ratingDate'] = pd.to_datetime(new['ratingDate'])
new['archive_date'] = pd.to_datetime(new['archive_date'])
new_prior = new.query('ratingDate < archive_date')
new_prior.sort_values(by=['CUSTOMERID','archive_date','ratingDate'], inplace=True)
new_prior.drop_duplicates(subset=['CUSTOMERID','archive_date'], keep='last', inplace=True)
new_prior['lag'] = new_prior.archive_date - new_prior.ratingDate 

new_prior.lag.describe()
'''
                             lag
count                       1460
mean   1155 days 04:53:29.634931
std    1230 days 00:27:48.158680
min              0 days 09:20:26
25%     328 days 08:43:43.250000
50%            821 days 06:51:19
75%    1521 days 06:34:28.250000
max           9431 days 00:00:00
'''

new_prior[new_prior.lag < pd.Timedelta('730 days')]
['00_customerlist.py', '01_CPPD_preapre_requested_sample.py', '01_CPPD_preapre_requested_sample_2019.py', '01_CPPD_preapre_requested_sample_new.py', '01_histdata_01_combine_adddef.py', '01_histdata_02_buildratios_auditvalid.py', '01_histdata_03_attachExtRating.py', '01_histdata_04_defineLCMM.py', '01_proddata_01_combine_raw_data.py', '01_proddata_02_filter_non-approved.py', '01_proddata_03_attach_def.py', '01_proddata_04_addDRD.py', '01_proddata_05_build_ratios.py', '01_proddata_06_filtering_audit_method.py', '01_proddata_07_defineLCMM.py', '02_LC_qualiSFA_01.py', '02_LC_quantSFA_00_preparedata.py', '02_LC_quantSFA_01_overall.py', '02_LC_quantSFA_02_get_long&short_list.py', '02_LC_quantSFA_03_shortlist_byRF.py', '02_LC_quantSFA_03_shortlist_mix.py', '02_LC_quantSFA_analyzelist.py', '02_LC_quantSFA_capfloor_test.py', '03_MFA_01_sampling.py', '03_MFA_02_quant_modelselction.py', '03_MFA_03_quant_finetuning.py', '03_MFA_03_quant_intersection_investigation.py', '03_MFA_04_quant_gridsearch.py', '03_MFA_05_quali_gridsearch.py', '03_MFA_06_get_model_spec.py', '03_MFA_07_moduleweight.py', '04_calibration_01_preparedata.py', '04_calibration_02_tuning_double_lines.py', '04_calibration_03_tuning_single_line.py', '04_calibration_04_CPPD_sample.py', '05_test_benchmark.py', '05_test_benchmark_outofsample.py', '05_test_CPPD.py', '05_test_default_analysis.py', '05_test_industry_seg.py', '05_test_industry_seg_kmeans.py', '05_test_kfold_calib.py', '05_test_kfold_MFA.py', '05_test_model.py', '05_test_PDRR_dist.py', '05_test_quali.py', '05_test_quant_f1c99.py', '06_moretests_00_clean_2018data.py', '06_moretests_01_BoundaryAnalysis_getRatings.py', '06_moretests_02_BoundaryAnalysis_analyse.py', '06_moretests_03_kmean_SegAna.py', '07_core_noncore.py', 'attach_reasons.py', 'businessbanking.py', 'default_analysis.py', 'moretests_BoundaryAnalysis.py', 'old_02_quantSFA_01_overall.py', 'old_02_quantSFA_02_get_long&short_list.py', 'replicate_old_model.py', 'RLA_Override.py', 'stats_for_lily.py', 'temp.py']
[35, 159, 298, 424, 536, 1055, 1188, 1270, 1308, 1332, 1416, 1532, 2042, 2068, 2174, 2356, 2842, 3298, 3359, 3437, 3575, 3661, 3717, 3795, 3969, 4101, 4476, 4833, 5038, 5152, 5286, 5362, 5633, 6017, 6198, 6357, 6491, 6707, 6781, 6917, 7081, 7232, 7366, 7427, 7502, 7598, 7702, 7763, 7843, 7922, 8344, 8597, 8709, 8815, 8850, 8967, 9282, 9641, 9695, 9840, 9951, 10036]
