# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 16:55:04 2020

@author: ub71894
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI_redev")

#%%  process ra occi data
ra = pd.read_excel(r'data\RA_OCCI_20190603.xlsx')
ra.dropna(subset=['CUSTOMERID', 'archive_date', 'Statement_Date'], how='any', inplace=True)
ra['Statement_Date'] = pd.to_datetime(ra['Statement_Date'], errors='coerce')
ra.sort_values(by=['CUSTOMERID',  'archive_date', 'Statement_Date'], inplace=True)
ra.drop_duplicates(subset=['CUSTOMERID', 'archive_date'], keep='last', inplace=True)


#%% 
raw = pd.read_excel(r'data\2_received_fr_Martin\CI_20190701.xls')
raw.dropna(subset=['Statement_Date'], inplace=True) # may not necessary in new data
raw.sort_values(by=['CUSTOMERID',  'Statement_Date', 'statement_id'], inplace=True)
raw.drop_duplicates(subset=['CUSTOMERID',  'Statement_Date'], keep='last', inplace=True)

#%% merge data
dat = pd.merge(ra, raw, on=['CUSTOMERID', 'Statement_Date'], how='inner')
dat['Net_Sales'] =  dat['Net Sales']
dat['year'] = [x.year for x in dat.archive_date]
dat = dat.query('year>=2018')


#%%  
dat_lc = dat.query('Net_Sales>1e9')
# 2652
dat_mm = dat.query('Net_Sales<=1e9')
# 9153

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

dat_lc['model'] = 'LC'
dat_mm['model'] = 'MM'

dat2 = pd.concat([dat_lc, dat_mm], axis=0)

os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\data")
# valid audit method filtering
valid2 = dat2.loc[dat2['Audit_Method'] != 'Proforma']
valid2 = valid2.loc[valid2['Audit_Method'] != 'Projection']
valid2['Gua_override'] =  valid2['PD_Risk_Rating_After_Gtee'] - valid2['PD_Risk_Rating_After_RLA']
valid2 = valid2.query('Gua_override==0')
valid2['RLA_Notches'].fillna(0, inplace=True)
valid2['Override_Action'].fillna(0, inplace=True)






dat = valid2
#%% build ratio

dat['Capitalization'] = dat[ 'CAPITALIZATION']
dat['ACF'] = dat['ACF_y']
dat['Free Operating Cash Flow (FOCF)'] = dat['Free Operating Cash Flow(FOCF)']
dat['DividendCommon'] = dat['Dividends']
dat['Interest Income'] = dat['INTERESTINCOME']


#%%

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


to_rename = {
'Customer_Name':'Customer Long Name',
'FundsFromOperations_Modified':'size@Funds from Operations_Modified',
'FreeOperatingCashFlow_Modified':'size@Free Operating Cash Flow_Modified',
'Audit_Method':'Audit Method'
}
dat.rename(columns=to_rename, inplace=True)


dat_LC = dat.query('model=="LC"')
dat_MM = dat.query('model=="MM"')




dat_LC.to_csv(r'dat_LC_201819.csv')
dat_MM.to_csv(r'dat_MM_201819.csv')# -*- coding: utf-8 -*-
"""
Created on Thu Mar 26 11:56:17 2020

@author: ub71894
"""


import os, sys, pandas as pd, numpy as np
import pickle
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.Process import getPDRR

os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\data")

#%% LC 2017-2019 data

df1 = pd.read_pickle(r'C:\Users\ub71894\Documents\Projects\CNI\src\MFA\test_2017.pkl.xz')
df1 = df1[['AUDITMETHOD',
 'Access_Outside_Capital',
 'Audit Method',
 'CONM',
 'CUSTOMERID',
 'Customer Long Name',
 'Excp_Underwrite_For_Leverage',
 'ExtRating',
 'ExternalRating_PDRR',
 'Final_PD_Risk_Rating',
 'Info_Rptg_Timely_Manner',
 'L_DATE_OF_DEFAULT',
 'Management_Quality',
 'Market_Outlook_Of_Borrower',
 'NAICS',
 'NAICS_Cd',
 'Override_Action',
 'Pct_Revenue_3_Large_Custs',
 'Prelim_PD_Risk_Rating_Uncap',
 'RLA_Notches',
 'Underwriter_Guideline',
 'dataset',
 'def_flag',
 'implied_internal_PD',
 'implied_internal_PDRR',
 'qual1',
 'qual2',
 'qual3',
 'qual4',
 'timestamp',
'prof@UBEBITDA_to_NS', 'cf@TD_to_UBEBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@UBEBITDA_to_IE',
'size@Union Bank EBITDA', 'size@Capitalization', 'ds@Interest Expense']]
df1['archive_date'] = df1['timestamp']
df1['period'] = 'before_prod'

df2 = pd.read_csv(r'dat_LC_201819.csv')
df2 = df2[['Guarantor_scorecard_nm',
 'archive_date',
 'version_num',
 'CUSTOMERID',
 'ARCHIVEID',
 'PROCESS_DATE',
 'SYSTEM_DATE',
 'Approver_Name',
 'Audit Method',
 'BTMU_Equivalent_Rating',
 'BTMU_Equivalent_Rating2',
 'CIF_Num',
 'Exception_Reason',
 'Final_Mapped_Risk_Grade',
 'Final_PD',
 'Final_PD_Risk_Rating',
 'Guarantee_Section_Notes',
 'Guarantor_CIF',
 'Guarantor_Condition_1',
 'Guarantor_Condition_2',
 'Guarantor_Condition_3',
 'Guarantor_Condition_4',
 'Guarantor_Condition_5',
 'Guarantor_Name',
 'Guarantor_Notches',
 'Guarantor_PD_Risk_Rating',
 'Guarantor_Support_Pct',
 'KMVEDF',
 'LASID_System',
 'Map_Risk_Grade_after_Gtee',
 'Map_Risk_Grade_after_RLA',
 'Model_PD',
 'Moodys_Rating',
 'NAICS_Cd',
 'Obligor_Section_Notes',
 'Override_Action',
 'Override_Category_1',
 'Override_Category_2',
 'Override_Category_3',
 'Override_Section_Notes',
 'PD_After_Gtee',
 'PD_After_RLA',
 'PD_Risk_Rating_After_Gtee',
 'PD_Risk_Rating_After_RLA',
 'Prelim_Map_Risk_Grade',
 'Prelim_Map_Risk_Grade_Uncap',
 'Prelim_PD',
 'Prelim_PD_Risk_Rating',
 'Prelim_PD_Risk_Rating_Uncap',
 'Prelim_PD_Uncap',
 'Public_Private_Cd',
 'Qualitative_As_Pct_Possible',
 'Qualitative_Score',
 'Qualitative_Section_Notes',
 'Quantitative_As_Pct_Possible',
 'Quantitative_Score',
 'Quantitative_Section_Notes',
 'Recommender_Name',
 'RLA_Category_1',
 'RLA_Category_2',
 'RLA_Category_3',
 'RLA_Impact_Level',
 'RLA_Notches',
 'RLA_Section_Notes',
 'Scorecard_Id',
 'Scorecard_Nm',
 'SPRating',
 'Total_Score',
 'Total_Score_Pct_Possible',
 'Underwriter_Guideline',
 'Guarantor_Justification',
 'Override_Justification',
 'Override_Reason_1',
 'Override_Reason_2',
 'Override_Reason_3',
 'RLA_Justification',
 'AgencyRating_Justification',
 'RLA_Reason_1',
 'RLA_Reason_2',
 'RLA_Reason_3',
 'ACF_x',
 'Cash_Operating_Profit',
 'Ending_Cash_Equiv',
 'Net_Profit',
 'Net_Sales',
 'Tangible_Net_Worth',
 'Total_Assets',
 'Total_Debt',
 'Total_Liabilities',
 'Total_Debt_By_ACF',
 'Net_Profit_Margin',
 'Total_Liab_by_Tang_Net_Worth',
 'End_Cash_Equiv_By_Tot_Liab',
 'Access_Outside_Capital',
 'Excp_Underwrite_For_Leverage',
 'Info_Rptg_Timely_Manner',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Market_Outlook_Of_Borrower',
 'Mgmt_Resp_Adverse_Conditions',
 'Pct_Revenue_3_Large_Custs',
 'Strength_SOR_Prevent_Default',
 'Vulnerability_To_Changes',
 'Guarantor_ArchiveId',
 'Guarantor_RA_ID',
 'Sprating_type',
 'Moodys_Rating_type',
 'ExternalRating',
 'ExternalRating_type',
 'ExternalRating_value',
 'ExternalRating_date',
 'ExternalRating_PDRR',
 'Moodys_Rating_Date',
 'Sprating_date',
 'CurrencyType',
 'Borrow_US_entity',
 'Country_grade',
 'Country',
 'Customer_Since',
 'statement_id_x',
 'Statement_Date',
 'Customer Long Name',
 'Obligor_Num',
 'Adjusted_CIF_Number',
 'STATEMENTDATE',
 'statement_id_y',
 'AUDITMETHOD',
 'STATEMENTMONTHS',
 'ACF_y',
 'CAPITALIZATION',
 'ESOPDividends',
 'NETINTANGIBLES',
 'Gross Profit Margin %_1',
 'Free Operating Cash Flow(FOCF)',
 'INTERESTEXPENSE_1',
 'INTERESTINCOME',
 'year',
 'model',
 'Gua_override',
 'prof@UBEBITDA_to_NS', 'cf@TD_to_UBEBITDA', 'size@Total Assets', 'bs@TD_to_Capt', 'ds@UBEBITDA_to_IE',
'size@Union Bank EBITDA', 'size@Capitalization', 'ds@Interest Expense']]

pd_cols= {'Strength_SOR_Prevent_Default':'qual1',
'Level_Waiver_Covenant_Mod':'qual2',
'Vulnerability_To_Changes':'qual4'}
df2.rename(columns=pd_cols, inplace=True)
df2['period'] = 'before_prod'

df3 = pd.read_csv(r'LC_data_sinceprod_APR2019_to_FEB2020.csv')
df3['prof@UBEBITDA_to_NS'] = df3['Internal_EBITDA'] / df3['Net_Sales']
df3['prof@UBEBITDA_to_NS'] = df3['prof@UBEBITDA_to_NS'].mask(df3['prof@UBEBITDA_to_NS'].isna(), df3['EBITDA_by_Net_Sales_12M'])
df3['cf@TD_to_UBEBITDA'] = df3['Total_debt_by_Int_EBITDA'].mask(df3['Total_debt_by_Int_EBITDA'].isna(), df3['Total_debt_by_EBITDA'])
df3['size@Total Assets'] = df3['Total_Assets_LC']
df3['bs@TD_to_Capt'] = df3['Total_debt_by_Capital']
df3['ds@UBEBITDA_to_IE'] = df3['Internal_EBITDA'] / df3['Interest_expense']
df3['ds@UBEBITDA_to_IE'] = df3['ds@UBEBITDA_to_IE'].mask(df3['ds@UBEBITDA_to_IE'].isna(),df3[ 'EBITDA_by_Int_Exp'])
df3['period'] = 'since_prod'

pd_cols= {
'Strength_SOR_Prevent_Default':'qual1',
'Level_Waiver_Covenant_Mod':'qual2',
'Vulnerability_To_Changes':'qual4',
'Internal_EBITDA':'size@Union Bank EBITDA',
'Capitalization':'size@Capitalization',
'Interest_expense':'ds@Interest Expense'
}
df3.rename(columns=pd_cols, inplace=True)



df = pd.concat([df1, df2, df3], axis=0)
df.reset_index(drop=True, inplace=True)
df['archive_date'] = pd.to_datetime(df['archive_date'])
df.sort_values(by=['CUSTOMERID', 'archive_date'], inplace=True)
df['year'] = [x.year for x in df.archive_date]

df_uni = df.drop_duplicates(subset=['CUSTOMERID', 'year'], keep='last')
df_uni = df_uni.query('2016<year<2020')
df_uni.reset_index(drop=True, inplace=True)

df_uni.to_csv(r'LC_20171819.csv')



# get norm data
model_LC = pickle.load(open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb'))


df_uni.dropna(subset=model_LC.quant_factor + model_LC.quali_factor, how='any', inplace=True)
df_uni['size@Total Assets'] = np.log(1+df_uni['size@Total Assets'])
# fill inf
for factor in model_LC.quant_factor:                       
        df_uni[factor] = df_uni[factor].clip(np.nanmin(df_uni[factor][df_uni[factor] != -np.inf]), np.nanmax(df_uni[factor][df_uni[factor] != np.inf]))


df_uni_norm = getPDRR(df_uni, model_LC, ms_ver='new')
# use RA' Total_Score and Prelim_PD_Risk_Rating for all 'since_prod' obs
df_uni_norm['Total_Score'] = df_uni_norm['Total_Score'].mask(df_uni_norm['period']=='before_prod', df_uni_norm.score)
df_uni_norm['Prelim_PD_Risk_Rating'] = df_uni_norm['Prelim_PD_Risk_Rating'].mask(df_uni_norm['period']=='before_prod', df_uni_norm.Ratings)

df_uni_norm.reset_index(drop=True, inplace=True)
df_uni_norm.to_csv(r'LC_20171819_norm.csv')




#%% MM
df1 = pd.read_excel(r'C:\Users\ub71894\Documents\Projects\CNI_redev\data\MM\normdat_test_after_calib.xlsx')
df2 = pd.read_excel(r'dat_MM_201819_output.xlsx')
df3 = pd.read_excel(r'MM_data_sinceprod_APR2019_to_FEB2020_output.xlsx')

df1['period'] = 'before_prod'
df2['period'] = 'before_prod'
df3['period'] = 'since_prod'
pd_cols= {'Strength_SOR_Prevent_Default':'qual1',
'Level_Waiver_Covenant_Mod':'qual2',
'Mgmt_Resp_Adverse_Conditions':'qual3',
'Vulnerability_To_Changes':'qual4'}
df2.rename(columns=pd_cols, inplace=True)
df3.rename(columns=pd_cols, inplace=True)

df = pd.concat([df1, df2, df3], axis=0)
cols_toremove=[
 'BTMU@EBITDA_to_IE',
 'BTMU@NP_exc_EI_to_TA',
 'BTMU@OP_to_Sales',
 'BTMU@TD_to_EBITDA',
 'BTMU@TD_to_TNW',
 'BTMU@TNW_to_TA',
 'SP@EBITDA_to_IE',
 'SP@EBIT_to_IE',
 'SP@EBIT_to_TD_and_TNW',
 'SP@TD_to_TD_and_TNW',
 'act@NS_to_CL',
 'act@NS_to_Inv',
 'act@NS_to_NAR',
 'act@NS_to_TA',
 'act@NS_to_TNW',
 'act@NS_to_UBTangNW',
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
 'bs@Total LTD',
 'bs@quant4',
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
 'cf@FOCF_to_TL',
 'cf@Lease Expense',
 'cf@SD_to_EBITDA',
 'cf@SD_to_UBEBITDA',
 'cf@TD_COP',
 'cf@TD_to_ACF',
 'cf@TD_to_ACF_and_LE',
 'cf@TD_to_EBITDA',
 'cf@TD_to_EBIT_exc_Div_exc_Taxes',
 'cf@TD_to_NP_and_Dep_and_Amo',
 'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',
 'cf@quant2',
 'ds@ACF_and_LE_to_DS_and_LE',
 'ds@ACF_to_DS',
 'ds@AFTERTAXEXPENSE',
 'ds@DSCR',
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
 'ds@UBEBIT_to_IE',
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
 'liq@Quick Ratio',
 'liq@RE_to_CL',
 'liq@Union Bank Current Ratio',
 'liq@Union Bank Quick Ratio',
 'liq@quant5',
 'others@CAPINTEREST',
 'others@CAPLEASEOBLIG',
 'others@INCOMETAXCREDIT',
 'others@INCOMETAXCREDIT_1',
 'others@INCOMETAXEXP',
 'others@INCOMETAXEXP_1',
 'others@TOTAL INCOME TAX EXPENSE',
 'others@Taxes',
 'others@Total Interest Inc(Exp)',
 'prof@AFTERTAXINCOME',
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
 'prof@TangA_to_NS',
 'prof@UBEBITDA_to_AdjCapt',
 'prof@UBEBITDA_to_Capt',
 'prof@UBEBITDA_to_NS',
 'prof@UBEBITDA_to_TA',
 'prof@UBEBITDA_to_TangA',
 'prof@UBEBIT_to_AdjCapt',
 'prof@UBEBIT_to_Capt',
 'prof@UBEBIT_to_NS',
 'prof@UBEBIT_to_TA',
 'prof@UBEBIT_to_TangA',
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
 'size@Union Bank Tangible Net Worth',
]


df.drop(columns=cols_toremove, inplace=True)
df.reset_index(drop=True, inplace=True)
df['archive_date'] = pd.to_datetime(df['archive_date'])
df.sort_values(by=['CUSTOMERID', 'archive_date'], inplace=True)
df['year'] = [x.year for x in df.archive_date]

df_uni = df.drop_duplicates(subset=['CUSTOMERID', 'year'], keep='last')
df_uni = df_uni.query('2016<year<2020')
df_uni.reset_index(drop=True, inplace=True)



df_uni['Total_Score'] = df_uni['Total_Score'].mask(df_uni['period']=='before_prod', df_uni.score)
df_uni['Prelim_PD_Risk_Rating_Uncap'] = df_uni['Prelim_PD_Risk_Rating_Uncap'].mask(df_uni['period']=='before_prod', df_uni.Ratings)

df_uni.to_csv(r'MM_20171819_norm.csv')


# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 17:21:54 2020

@author: ub71894
"""


import os, sys, pandas as pd, numpy as np
import pickle
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src")
from PDScorecardTool.Process import logitPD_frPDRR, SomersD 
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping, google_color
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')

import pickle
filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb')
model_LC = pickle.load(filehandler)

dat = pd.read_csv(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\data\LC_20171819_norm.csv')
dat['archive_date'] = pd.to_datetime(dat['archive_date'])
dat = MAUG_mapping(dat)
dat = NAICS_mapping(dat, first_digits=3)
dat = logitPD_frPDRR(dat, model_LC, PDRR = 'Final_PD_Risk_Rating')

# remove Aviation leasing company from pre-201910 data
mask = (dat['Industry_by_MAUG']=="MAUG_172" )&(dat['archive_date']<'2019-10-01' )
dat = dat[~mask]
dat.reset_index(drop=False, inplace=True)


# find outlier candidates
pl_outliers = []
for factor in (model_LC.quant_factor):    
    x_train = sm.add_constant(dat[factor], prepend = True)
    linear = sm.OLS(dat['logitPD_frPDRR'], x_train, missing='drop')
    lm = linear.fit(disp=0)
    #create instance of influence
    # outliers by > 3 mean of cooks' distance
    influence = lm.get_influence()
    cooks_d = pd.Series(influence.cooks_distance[0])
    ps_cooks  = cooks_d[cooks_d>3*cooks_d.mean()]
    # outliers 10 largest leverage
    leverage = pd.Series(influence.hat_matrix_diag)
    ps_lv = leverage.nlargest(10)
    pl_outliers = pl_outliers+ list(ps_cooks.index) + list(ps_lv.index)

outliers = pd.Series(pl_outliers)
freq_out = outliers.value_counts()
#threshold = 3
#pd_outliers3=dat.where(freq_out>=threshold).dropna(how='all')
threshold = 4
pd_outliers4=dat.where(freq_out>=threshold).dropna(how='all')
#threshold = 5
#pd_outliers5=dat.where(freq_out>=threshold).dropna(how='all')




#%%
df_outlier = pd_outliers4[[
'CUSTOMERID',
'Customer Long Name',
 'Customer_Name',
 'timestamp',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Override_Action', 
 'RLA_Notches',
 'Ratings']]
df_outlier.to_excel('LC_stats_outliers_noncore.xlsx')


dat['group'] = 'core'
dat['group'] = dat['group'].mask(dat.CUSTOMERID.isin(list(df_outlier['CUSTOMERID'].unique())), 'non-core')
dat['Total Score'] = dat['Total_Score']
dat['RLA'] = ['Yes' if x!=0 else 'No' for x in dat[ 'RLA_Notches']]


f= sns.relplot(x='Total Score', y='Final_PD_Risk_Rating', data= dat, hue="group", alpha=0.7, palette="husl", height=9)
f.savefig('LC_stat_corenoncore.png')



dat['group'] = 'Primary'
dat['group'] = dat['group'].mask(dat.CUSTOMERID.isin(list(df_outlier['CUSTOMERID'].unique())), 'Secondary')
dat['Total Score'] = dat['Total_Score']
dat['RLA'] = ['Yes' if x!=0 else 'No' for x in dat[ 'RLA_Notches']]


f= sns.relplot(x='Total Score', y='Final_PD_Risk_Rating', data= dat, hue="group", alpha=0.7, palette=google_color[:2][::-1], height=9)
f.savefig('LC_stat_PrimarySecondary.png')



#%%
dat_core = dat.query('group=="core"')
dat_noncore = dat.query('group=="non-core"')

print(SomersD(dat['Final_PD_Risk_Rating'], dat['Prelim_PD_Risk_Rating']))
print(SomersD(dat_core['Final_PD_Risk_Rating'], dat_core['Prelim_PD_Risk_Rating']))
print(SomersD(dat_noncore['Final_PD_Risk_Rating'], dat_noncore['Prelim_PD_Risk_Rating']))

'''
0.706533671470515
0.6944543617080412
0.6944262295081968
'''


CreateBenchmarkMatrix(dat, 'LC_TM_stats.xlsx', 'All', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(dat_core, 'LC_TM_stats.xlsx', 'core', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(dat_noncore, 'LC_TM_stats.xlsx', 'non-core', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))



# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 17:21:54 2020

@author: ub71894
"""


import os, sys, pandas as pd, numpy as np
import pickle
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src")
from PDScorecardTool.Process import logitPD_frPDRR, SomersD 
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')

import pickle
model_MM = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_MM_old.pkl','rb'))

dat = pd.read_csv(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\data\MM_20171819_norm.csv')
dat['archive_date'] = pd.to_datetime(dat['archive_date'])
dat = MAUG_mapping(dat)
dat = NAICS_mapping(dat, first_digits=3)


# remove Aviation leasing company from pre-201910 data
mask = (dat['Industry_by_MAUG']=="MAUG_172" )&(dat['archive_date']<'2019-10-01' )
dat = dat[~mask]

dat = logitPD_frPDRR(dat, model_MM, PDRR = 'Final_PD_Risk_Rating')
dat.reset_index(drop=False, inplace=True)



# find outlier candidates
pl_outliers = []
for factor in (model_MM.quant_factor):    
    x_train = sm.add_constant(dat[factor], prepend = True)
    linear = sm.OLS(dat['logitPD_frPDRR'], x_train, missing='drop')
    lm = linear.fit(disp=0)
    #create instance of influence
    # outliers by > 3 mean of cooks' distance
    influence = lm.get_influence()
    cooks_d = pd.Series(influence.cooks_distance[0])
    ps_cooks  = cooks_d[cooks_d>3*cooks_d.mean()]
    # outliers 10 largest leverage
    leverage = pd.Series(influence.hat_matrix_diag)
    ps_lv = leverage.nlargest(10)
    pl_outliers = pl_outliers+ list(ps_cooks.index) + list(ps_lv.index)

outliers = pd.Series(pl_outliers)
freq_out = outliers.value_counts()
threshold = 3
pd_outliers3=dat.where(freq_out>=threshold).dropna(how='all')
threshold = 4
pd_outliers4=dat.where(freq_out>=threshold).dropna(how='all')
threshold = 5
pd_outliers5=dat.where(freq_out>=threshold).dropna(how='all')




#%%
df_outlier = pd_outliers4[[
'CUSTOMERID',
'Customer Long Name',
 'Customer_Name',
 'archive_date',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Override_Action', 
 'RLA_Notches',
 'Ratings']]
df_outlier.to_excel('MM_stats_outliers_noncore.xlsx')


dat['group'] = 'Primary'
dat['group'] = dat['group'].mask(dat.CUSTOMERID.isin(list(df_outlier['CUSTOMERID'].unique())), 'Secondary')
dat['Total Score'] = dat['Total_Score']
dat['RLA'] = ['Yes' if x!=0 else 'No' for x in dat[ 'RLA_Notches']]


f= sns.relplot(x='Total Score', y='Final_PD_Risk_Rating', data= dat, hue="group", alpha=0.7, palette=google_color[:2][::-1], height=9)
f.savefig('MM_stat_PrimarySecondary.png')





#%%
dat_core = dat.query('group=="core"')
dat_noncore = dat.query('group=="non-core"')

print(SomersD(dat['Final_PD_Risk_Rating'], dat['Prelim_PD_Risk_Rating']))
print(SomersD(dat_core['Final_PD_Risk_Rating'], dat_core['Prelim_PD_Risk_Rating']))
print(SomersD(dat_noncore['Final_PD_Risk_Rating'], dat_noncore['Prelim_PD_Risk_Rating']))
'''

0.7280475825650617
0.7134010784357536
0.7901079097639881

'''

CreateBenchmarkMatrix(dat, 'MM_TM_stats.xlsx', 'All', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(dat_core, 'MM_TM_stats.xlsx', 'core', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(dat_noncore, 'MM_TM_stats.xlsx', 'non-core', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))



# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 17:21:54 2020

@author: ub71894
"""
import os, sys, pandas as pd, numpy as np
import pickle
import seaborn as sns
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src")
from PDScorecardTool.Process import SomersD, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping
from PDScorecardTool.Process import func_sd, func_rla, func_ovd, google_color
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import matplotlib.pyplot as plt

dat = pd.read_csv(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\data\LC_20171819_norm.csv')
dat['archive_date'] = pd.to_datetime(dat['archive_date'])
dat = MAUG_mapping(dat)
dat = NAICS_mapping(dat)

# remove Aviation leasing company from pre-201910 data
mask = (dat['Industry_by_MAUG']=="MAUG_172" )&(dat['archive_date']<'2019-10-01' )
dat = dat[~mask]
# remove unknown MAUG, just one obs
mask = (dat['Industry_by_MAUG']=="MAUG_373" )
dat = dat[~mask]

len(dat['Industry_by_MAUG'].unique())
# 23
len(dat['Industry_by_NAICS'].unique())
# 20




#%% by MAUG
by_name = 'Industry_by_MAUG'
table = pd.concat([dat.groupby(by_name).count()['CUSTOMERID'],
                dat.groupby(by_name).apply(func_sd),
                dat.groupby(by_name).apply(func_rla), 
                dat.groupby(by_name).apply(func_ovd)], axis=1)

table.columns = ['Count', 'SomersD','RLA_Rate','Override_Rate']
table.sort_values(by='Count', ascending=False, inplace=True)
table.to_excel(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src\LC_Ind_MAUG.xlsx')






#%% breakdown some indutries for closer look
output_file = pd.ExcelWriter(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src\LC_ind_breakdown.xlsx')
cols=['Independent Exploration and Production',
'Independent Refining',
'Drilling and Oilfield Services',
'MAUG_172',
'Trading Asset Reliant',
'Corporate Leasing Transactions',
'Leasing Companies',
'Leasing and Asset Finance Division',
'Business Banking',
]


for field in cols:
    temp = dat[dat['Industry_by_MAUG']==field].copy()
    temp['Name'] = temp['Customer Long Name'].mask(pd.isnull(temp['Customer Long Name']), temp['Customer_Name'])
    temp = temp[['Industry_by_MAUG','Name','archive_date','Final_PD_Risk_Rating']]
    temp.sort_values(by=['archive_date'])
    temp.to_excel(output_file, field[:20])

output_file.save()



#%% check NAICS industry among all other 'core' MAUG industry
core_maug=[
'General Industries',
'Technology',
'Health Care',
'Asian Corporate Banking',
'Commercial Finance Loans',
'Media and Telecom',
'Food and Beverage',
'Retail',
'Engineering and Construction',
'Auto and Auto Parts',
]

df_core = dat[dat['Industry_by_MAUG'].isin(core_maug)].copy()

# by NAICS
by_name = 'Industry_by_NAICS'
table = pd.concat([df_core.groupby(by_name).count()['CUSTOMERID'],
                df_core.groupby(by_name).apply(func_sd),
                df_core.groupby(by_name).apply(func_rla), 
                df_core.groupby(by_name).apply(func_ovd)], axis=1)

table.columns = ['Count', 'SomersD','RLA_Rate','Override_Rate']
table.sort_values(by='Count', ascending=False, inplace=True)

table['RednRed'] = 0
table.loc[ (table.RLA_Rate>0.45) & (table.Override_Rate>0.3) , 'RednRed'] =1
table.query('RednRed==1')['Count'].sum()


table['YellownRed'] = 0
table.loc[ (table.RLA_Rate>=0.3) & (table.RLA_Rate<=0.45) & (table.Override_Rate>0.3) , 'YellownRed'] =1
table.loc[ (table.Override_Rate>=0.2) & (table.Override_Rate<=0.3) & (table.RLA_Rate>0.45) , 'YellownRed'] =1


table.to_excel('LC_NAICS_step2_removeagribusiness.xlsx')




#%% after manual tag

noncore_maug=[
'Midstream Energy',
'Commodity Finance',
'Independent Exploration and Production',
'Independent Refining',
'Drilling and Oilfield Services',
'Trading Asset Reliant',
'Insurance',
'MAUG_172',
'Corporate Leasing Transactions',
'Leasing and Asset Finance Division',
'Leasing Companies',
'Business Banking',
'Agribusiness',
]

noncore_naics = ['Mining, Quarrying, and Oil and Gas Extraction',]

# begin to tag data:
dat['group'] = 'core'
dat['group'] = dat['group'].mask(dat['Industry_by_MAUG'].isin(noncore_maug), 'non-core')
dat['group'] = dat['group'].mask(dat['Industry_by_NAICS'].isin(noncore_naics), 'non-core')
dat['group'].value_counts()
'''
core        1846
non-core     249
Name: group, dtype: int64

'''

# rename
dat['group'] = 'Primary'
dat['group'] = dat['group'].mask(dat['Industry_by_MAUG'].isin(noncore_maug), 'Secondary')
dat['group'] = dat['group'].mask(dat['Industry_by_NAICS'].isin(noncore_naics), 'Secondary')
dat['group'].value_counts()
'''
Primary      1844
Secondary     251
Name: group, dtype: int64
'''

# scatter plot
f= sns.relplot(x='Total_Score', y='Final_PD_Risk_Rating', data= dat, hue="group", alpha=0.7, palette="husl", height=9)
f.savefig('LC_Ind_corenoncore.png')

# re scatter plot
f= sns.relplot(x='Total_Score', y='Final_PD_Risk_Rating', data= dat, hue="group", alpha=0.7, palette=google_color[:2], height=9)
f.savefig(r'output\LC_Ind_PrimarySecondary.png')



# TM
dat_core = dat.query('group=="Primary"')
dat_noncore = dat.query('group=="Secondary"')

CreateBenchmarkMatrix(dat, 'LC_TM_Ind_removeagribusiness.xlsx', 'All', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(dat_core, 'LC_TM_Ind_removeagribusiness.xlsx', 'core', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(dat_noncore, 'LC_TM_Ind_removeagribusiness.xlsx', 'non-core', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))


# Plot distributions
list_data = [dat, dat_core, dat_noncore]
list_data_name = ['Full Dataset', 'Primary', 'Secondary']

df_plot=pd.DataFrame()
for i, df in enumerate(list_data):
    tmp = df['Final_PD_Risk_Rating'].value_counts(normalize=True).sort_index()
    df_plot[list_data_name[i]] = tmp
df_plot.index = [int(x) for x in df_plot.index]


f,ax=plt.subplots(1,1,figsize=(12,8))
_ax = df_plot.plot(kind='bar', alpha=0.75,ax=ax, rot=0, color=google_color[:3])
# manipulate
vals = _ax.get_yticks()
_ax.set_yticklabels(['{:3.2f}%'.format(x*100) for x in vals])
_ax.set_xlabel('Final PDRR')
_ax.set_ylabel('Percent')

f.savefig('LC_Ind_PrimarySecondary_Dist.png')




#%% mean PD and CT
model_LC = pickle.load(open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb'))


dat_core = PD_frPDRR(dat_core, model_LC, 'Final_PD_Risk_Rating')
dat_core['PD_frPDRR'].mean()
# 0.010549078091106253

dat_noncore = PD_frPDRR(dat_noncore, model_LC, 'Final_PD_Risk_Rating')
dat_noncore['PD_frPDRR'].mean()
#  0.024314342629482084


dat_core = PD_frPDRR(dat_core, model_LC, 'Prelim_PD_Risk_Rating')
dat_core['PD_frPDRR'].mean()
# 0.007676030368763505

dat_noncore = PD_frPDRR(dat_noncore, model_LC, 'Prelim_PD_Risk_Rating')
dat_noncore['PD_frPDRR'].mean()
#  0.011044223107569716



#%% Rating Dist
df_plot = dat_core['Final_PD_Risk_Rating'].value_counts(normalize=True).sort_index()
plt.bar(df_plot.index, df_plot)
plt.xlabel(f"Core Rating Dist of Final PDRR")




dat_core['percentage'] = 1/len(dat_core)
dat_noncore['percentage'] = 1/len(dat_noncore)
data_plot = pd.concat([dat_core, dat_noncore], axis=0)
f = plt.figure(figsize=(12, 8))
data_plot['Final_PD_Risk_Rating'] = [int(x) for x in data_plot['Final_PD_Risk_Rating']]
sns.barplot(x='Final_PD_Risk_Rating', y='percentage', hue='group', data=data_plot, estimator=sum, palette='pastel')





#%% breakdown some indutries for closer look
output_file = pd.ExcelWriter(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src\LC_ind_breakdown_OG.xlsx')
cols=[
'Independent Exploration and Production',
'Independent Refining',
'Drilling and Oilfield Services',
]


for field in cols:
    temp = dat[dat['Industry_by_MAUG']==field].copy()
    temp['Name'] = temp['Customer Long Name'].mask(pd.isnull(temp['Customer Long Name']), temp['Customer_Name'])
    temp = temp[['Industry_by_MAUG','Name','CUSTOMERID','archive_date','Prelim_PD_Risk_Rating','Final_PD_Risk_Rating']]
    temp.sort_values(by=['archive_date'], inplace=True)
    temp.to_excel(output_file, field[:20])

output_file.save()
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 17:21:54 2020

@author: ub71894
"""
import os, sys, pandas as pd, numpy as np
import pickle
import seaborn as sns
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src")
from PDScorecardTool.Process import SomersD, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping
from PDScorecardTool.Process import func_sd, func_rla, func_ovd
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import matplotlib.pyplot as plt

dat = pd.read_csv(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\data\LC_20171819_norm.csv')
dat['archive_date'] = pd.to_datetime(dat['archive_date'])
dat = MAUG_mapping(dat)
dat = NAICS_mapping(dat)

# remove Aviation leasing company from pre-201910 data
mask = (dat['Industry_by_MAUG']=="MAUG_172" )&(dat['archive_date']<'2019-10-01' )
dat = dat[~mask]

len(dat['Industry_by_MAUG'].unique())
# 24
len(dat['Industry_by_NAICS'].unique())
# 20




#%% by MAUG
by_name = 'Industry_by_MAUG'
table = pd.concat([dat.groupby(by_name).count()['CUSTOMERID'],
                dat.groupby(by_name).apply(func_sd),
                dat.groupby(by_name).apply(func_rla), 
                dat.groupby(by_name).apply(func_ovd)], axis=1)

table.columns = ['Count', 'SomersD','RLA_Rate','Override_Rate']
table.sort_values(by='Count', ascending=False, inplace=True)
table.to_excel(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src\LC_Ind_MAUG.xlsx')






#%% breakdown some indutries for closer look
output_file = pd.ExcelWriter(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src\LC_ind_breakdown.xlsx')
cols=['Independent Exploration and Production',
'Independent Refining',
'Drilling and Oilfield Services',
'MAUG_172',
'Trading Asset Reliant',
'Corporate Leasing Transactions',
'Leasing Companies',
'Leasing and Asset Finance Division',
'Business Banking',
'MAUG_373',
]


for field in cols:
    temp = dat[dat['Industry_by_MAUG']==field].copy()
    temp['Name'] = temp['Customer Long Name'].mask(pd.isnull(temp['Customer Long Name']), temp['Customer_Name'])
    temp = temp[['Industry_by_MAUG','Name','archive_date','Final_PD_Risk_Rating']]
    temp.sort_values(by=['archive_date'])
    temp.to_excel(output_file, field[:20])

output_file.save()



#%% check NAICS industry among all other 'core' MAUG industry
core_maug=[
'General Industries',
'Technology',
'Health Care',
'Asian Corporate Banking',
'Commercial Finance Loans',
'Media and Telecom',
'Food and Beverage',
'Retail',
'Engineering and Construction',
'Auto and Auto Parts',
'Agribusiness',
]

df_core = dat[dat['Industry_by_MAUG'].isin(core_maug)].copy()

# by NAICS
by_name = 'Industry_by_NAICS'
table = pd.concat([df_core.groupby(by_name).count()['CUSTOMERID'],
                df_core.groupby(by_name).apply(func_sd),
                df_core.groupby(by_name).apply(func_rla), 
                df_core.groupby(by_name).apply(func_ovd)], axis=1)

table.columns = ['Count', 'SomersD','RLA_Rate','Override_Rate']
table.sort_values(by='Count', ascending=False, inplace=True)

table['RednRed'] = 0
table.loc[ (table.RLA_Rate>0.45) & (table.Override_Rate>0.3) , 'RednRed'] =1
table.query('RednRed==1')['Count'].sum()


table['YellownRed'] = 0
table.loc[ (table.RLA_Rate>=0.3) & (table.RLA_Rate<=0.45) & (table.Override_Rate>0.3) , 'YellownRed'] =1
table.loc[ (table.Override_Rate>=0.2) & (table.Override_Rate<=0.3) & (table.RLA_Rate>0.45) , 'YellownRed'] =1


table.to_excel('LC_NAICS_step2.xlsx')




#%% breakdown 2 reds by NAICS indutries
output_file = pd.ExcelWriter(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src\LC_ind_breakdown2.xlsx')
cols=[
'Air Transportation',
'Beverage and Tobacco Product Manufacturing',
'Broadcasting (except Internet)',
'Couriers and Messengers',
'Funds, Trusts, and Other Financial Vehicles ',
'Health and Personal Care Stores ',
'Insurance Carriers and Related Activities',
'Miscellaneous Store Retailers ',
'Oil and Gas Extraction',
'Other Information Services',
'Pipeline Transportation',
'Support Activities for Agriculture and Forestry',
'Support Activities for Mining',
]


for field in cols:
    temp = df_core[df_core['Industry_by_NAICS']==field].copy()
    temp['Name'] = temp['Customer Long Name'].mask(pd.isnull(temp['Customer Long Name']), temp['Customer_Name'])
    temp = temp[['Industry_by_NAICS','Name','archive_date','Prelim_PD_Risk_Rating','Final_PD_Risk_Rating']]
    temp.sort_values(by=['archive_date'])
    temp.to_excel(output_file, field[:10])

output_file.save()




#%% breakdown red+yellow by NAICS indutries
output_file = pd.ExcelWriter(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src\LC_ind_breakdown3.xlsx')
cols=['Accommodation',
'Clothing and Clothing Accessories Stores ',
'Computer and Electronic Product Manufacturing',
'Credit Intermediation and Related Activities',
'Electronics and Appliance Stores ',
'Food Manufacturing',
'Food Services and Drinking Places',
'General Merchandise Stores ',
'Heavy and Civil Engineering Construction',
'Mining (except Oil and Gas)',
'Performing Arts, Spectator Sports, and Related Industries',
'Petroleum and Coal Products Manufacturing',
'Professional, Scientific, and Technical Services',
'Publishing Industries (except Internet)',
'Rail Transportation',
'Utilities ',
'Water Transportation',
]


for field in cols:
    temp = df_core[df_core['Industry_by_NAICS']==field].copy()
    temp['Name'] = temp['Customer Long Name'].mask(pd.isnull(temp['Customer Long Name']), temp['Customer_Name'])
    temp = temp[['Industry_by_NAICS','Name','archive_date','Prelim_PD_Risk_Rating','Final_PD_Risk_Rating']]
    temp.sort_values(by=['archive_date'])
    temp.to_excel(output_file, field[:10])

output_file.save()





















#%% after manual tag
df_naics = pd.read_excel('LC_NAICS_forcore.xlsx')
df_naics_noncore = df_naics.query('tag==1')
noncore_naics = df_naics_noncore['Industry'].tolist()

['Heavy and Civil Engineering Construction',
 'Mining (except Oil and Gas)',
 'Performing Arts, Spectator Sports, and Related Industries',
 'Petroleum and Coal Products Manufacturing',
 'Air Transportation',
 'Funds, Trusts, and Other Financial Vehicles ',
 'Health and Personal Care Stores ',
 'Insurance Carriers and Related Activities',
 'Oil and Gas Extraction',
 'Other Information Services',
 'Support Activities for Agriculture and Forestry',
 'Support Activities for Mining']



noncore_maug = [i for i in dat['Industry_by_MAUG'].unique().tolist() if i not in core_maug]


# begin to tag data:
dat['group'] = 'core'
dat['group'] = dat['group'].mask(dat['Industry_by_MAUG'].isin(noncore_maug), 'non-core')
dat['group'] = dat['group'].mask(dat['Industry_by_NAICS'].isin(noncore_naics), 'non-core')



sns.relplot(x='Total_Score', y='Final_PD_Risk_Rating', data= dat,hue="group")

dat_core = dat.query('group=="core"')
dat_noncore = dat.query('group=="non-core"')

CreateBenchmarkMatrix(dat, 'TM.xlsx', 'All', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(dat_core, 'TM.xlsx', 'core', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(dat_noncore, 'TM.xlsx', 'non-core', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))





#%% mean PD and CT
model_LC = pickle.load(open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb'))



dat_core = PD_frPDRR(dat_core, model_LC, 'Final_PD_Risk_Rating')
dat_core['PD_frPDRR'].mean()
# 0.010659799260433133

dat_noncore = PD_frPDRR(dat_noncore, model_LC, 'Final_PD_Risk_Rating')
dat_noncore['PD_frPDRR'].mean()
#  0.02651182266009854



dat_core = PD_frPDRR(dat_core, model_LC, 'Prelim_PD_Risk_Rating')
dat_core['PD_frPDRR'].mean()
# 0.008084521922873697

dat_noncore = PD_frPDRR(dat_noncore, model_LC, 'Prelim_PD_Risk_Rating')
dat_noncore['PD_frPDRR'].mean()
#  0.008020689655172403



#%% Rating Dist
df_plot = dat_core['Final_PD_Risk_Rating'].value_counts(normalize=True).sort_index()
plt.bar(df_plot.index, df_plot, color = colours[0])
plt.xlabel(f"Core Rating Dist of Final PDRR")




dat_core['percentage'] = 1/len(dat_core)
dat_noncore['percentage'] = 1/len(dat_noncore)
data_plot = pd.concat([dat_core, dat_noncore], axis=0)
f = plt.figure(figsize=(12, 8))
data_plot['Final_PD_Risk_Rating'] = [int(x) for x in data_plot['Final_PD_Risk_Rating']]
sns.barplot(x='Final_PD_Risk_Rating', y='percentage', hue='group', data=data_plot, estimator=sum, palette='pastel')



#%% Size Dist
f = plt.figure(figsize=(12, 8))
sns.violinplot(x='group', y='size@Total Assets',data=data_plot, palette='pastel')

f = plt.figure(figsize=(12, 8))
sns.violinplot(x='group', y='Net_Sales',data=data_plot.query('Net_Sales<2.75e11'), palette='pastel',scale="area", inner="quartile")
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 17:21:54 2020

@author: ub71894
"""
import os, sys, pandas as pd, numpy as np
import pickle
import seaborn as sns
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src")
from PDScorecardTool.Process import SomersD, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import MAUG_mapping, NAICS_mapping
from PDScorecardTool.Process import func_sd, func_rla, func_ovd, google_color
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import matplotlib.pyplot as plt

model_MM = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_MM_old.pkl','rb'))

dat = pd.read_csv(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\data\MM_20171819_norm.csv')
dat['archive_date'] = pd.to_datetime(dat['archive_date'])
dat = MAUG_mapping(dat)
dat = NAICS_mapping(dat)


# remove Aviation leasing company from pre-201910 data
mask = (dat['Industry_by_MAUG']=="MAUG_172" )&(dat['archive_date']<'2019-10-01' )
dat = dat[~mask]

# remove unknown MAUG, just one obs
mask = (dat['Industry_by_MAUG']=="MAUG_373" )
dat = dat[~mask]


len(dat['Industry_by_MAUG'].unique())
# 30
len(dat['Industry_by_NAICS'].unique())
# 21




#%% by MAUG
by_name = 'Industry_by_MAUG'
table = pd.concat([dat.groupby(by_name).count()['CUSTOMERID'],
                dat.groupby(by_name).apply(func_sd),
                dat.groupby(by_name).apply(func_rla), 
                dat.groupby(by_name).apply(func_ovd)], axis=1)

table.columns = ['Count', 'SomersD','RLA_Rate','Override_Rate']
table.sort_values(by='Count', ascending=False, inplace=True)
table.to_excel(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src\MM_Ind_MAUG.xlsx')








#%% check NAICS industry among all other 'core' MAUG industry
core_maug=[
'General Industries',
'Asian Corporate Banking',
'Non-Profit Organizations',
'Trading Asset Reliant',
'Health Care',
'Technology',
'Food and Beverage',
'Commercial Finance Loans',
'Media and Telecom',
'Wine Industry',
'Retail',
'Homeowner Association Loans',
'MAUG_306',
'MAUG_185',
]

df_core = dat[dat['Industry_by_MAUG'].isin(core_maug)].copy()

# by NAICS
by_name = 'Industry_by_NAICS'
table = pd.concat([df_core.groupby(by_name).count()['CUSTOMERID'],
                df_core.groupby(by_name).apply(func_sd),
                df_core.groupby(by_name).apply(func_rla), 
                df_core.groupby(by_name).apply(func_ovd)], axis=1)

table.columns = ['Count', 'SomersD','RLA_Rate','Override_Rate']
table.sort_values(by='Count', ascending=False, inplace=True)

table['RednRed'] = 0
table.loc[ (table.RLA_Rate>0.45) & (table.Override_Rate>0.3) , 'RednRed'] =1
table.query('RednRed==1')['Count'].sum()


table['YellownRed'] = 0
table.loc[ (table.RLA_Rate>=0.3) & (table.RLA_Rate<=0.45) & (table.Override_Rate>0.3) , 'YellownRed'] =1
table.loc[ (table.Override_Rate>=0.2) & (table.Override_Rate<=0.3) & (table.RLA_Rate>0.45) , 'YellownRed'] =1


table.to_excel('MM_NAICS_step2_removeagribusiness.xlsx')






#%% after manual tag
noncore_maug=[
'Business Banking',
'Leasing Companies',
'Midstream Energy',
'Commodity Finance',
'Drilling and Oilfield Services',
'Business Diversity Lending',
'Asian Corporate Leasing & Finance',
'Insurance',
'Small Business Banking',
'Independent Exploration and Production',
'MAUG_172',
'Auto and Auto Parts',
'Public Finance',
'Engineering and Construction',
'Independent Refining',
'Agribusiness',
]

noncore_naics = ['Mining, Quarrying, and Oil and Gas Extraction',]

# begin to tag data:
dat['group'] = 'core'
dat['group'] = dat['group'].mask(dat['Industry_by_MAUG'].isin(noncore_maug), 'non-core')
dat['group'] = dat['group'].mask(dat['Industry_by_NAICS'].isin(noncore_naics), 'non-core')
dat['group'].value_counts()
'''
core        4231
non-core    1233
Name: group, dtype: int64

'''
# rename
dat['group'] = 'Primary'
dat['group'] = dat['group'].mask(dat['Industry_by_MAUG'].isin(noncore_maug), 'Secondary')
dat['group'] = dat['group'].mask(dat['Industry_by_NAICS'].isin(noncore_naics), 'Secondary')
dat['group'].value_counts()
'''
Primary      3853
Secondary    1611
Name: group, dtype: int64
'''


# scatter plot
f= sns.relplot(x='Total_Score', y='Final_PD_Risk_Rating', data= dat, hue="group", alpha=0.7, palette="husl", height=9)
f.savefig('MM_Ind_corenoncore.png')


# re scatter plot
f= sns.relplot(x='Total_Score', y='Final_PD_Risk_Rating', data= dat, hue="group", alpha=0.7, palette=google_color[:2], height=9)
f.savefig(r'output\MM_Ind_PrimarySecondary.png')





# TM
dat_core = dat.query('group=="Primary"')
dat_noncore = dat.query('group=="Secondary"')

CreateBenchmarkMatrix(dat, 'MM_TM_Ind_removeagribusiness.xlsx', 'All', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(dat_core, 'MM_TM_Ind_removeagribusiness.xlsx', 'Primary', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))
CreateBenchmarkMatrix(dat_noncore, 'MM_TM_Ind_removeagribusiness.xlsx', 'Secondary', 'Final_PD_Risk_Rating', 'Prelim_PD_Risk_Rating', PDRR=range(1,16))




# Plot distributions
list_data = [dat, dat_core, dat_noncore]
list_data_name = ['Full Dataset', 'Primary', 'Secondary']

df_plot=pd.DataFrame()
for i, df in enumerate(list_data):
    tmp = df['Final_PD_Risk_Rating'].value_counts(normalize=True).sort_index()
    df_plot[list_data_name[i]] = tmp
df_plot.index = [int(x) for x in df_plot.index]


f,ax=plt.subplots(1,1,figsize=(12,8))
_ax = df_plot.plot(kind='bar', alpha=0.75,ax=ax, rot=0, color=google_color[:3])
# manipulate
vals = _ax.get_yticks()
_ax.set_yticklabels(['{:3.2f}%'.format(x*100) for x in vals])
_ax.set_xlabel('Final PDRR')
_ax.set_ylabel('Percent')

f.savefig('MM_Ind_PrimarySecondary_Dist.png')






#%% mean PD and CT
dat_core = PD_frPDRR(dat_core, model_MM, 'Final_PD_Risk_Rating')
dat_core['PD_frPDRR'].mean()
# 0.022788995587853047

dat_noncore = PD_frPDRR(dat_noncore, model_MM, 'Final_PD_Risk_Rating')
dat_noncore['PD_frPDRR'].mean()
#  0.031041340782122718


dat_core = PD_frPDRR(dat_core, model_MM, 'Prelim_PD_Risk_Rating')
dat_core['PD_frPDRR'].mean()
# 0.019108225005908315

dat_noncore = PD_frPDRR(dat_noncore, model_MM, 'Prelim_PD_Risk_Rating')
dat_noncore['PD_frPDRR'].mean()
#  0.02886569343065683





#%% breakdown some indutries for closer look
output_file = pd.ExcelWriter(r'C:\Users\ub71894\Documents\Projects\CNI\IssueClosure_2020\core-noncore\src\MM_ind_breakdown_OG.xlsx')
cols=[
'Independent Exploration and Production',
'Independent Refining',
'Drilling and Oilfield Services',
]


for field in cols:
    temp = dat[dat['Industry_by_MAUG']==field].copy()
    temp['Name'] = temp['Customer Long Name'].mask(pd.isnull(temp['Customer Long Name']), temp['Customer_Name'])
    temp = temp[['Industry_by_MAUG','Name','CUSTOMERID','archive_date','Prelim_PD_Risk_Rating','Final_PD_Risk_Rating']]
    temp.sort_values(by=['archive_date'], inplace=True)
    temp.to_excel(output_file, field[:20])

output_file.save()
['01_get2018-19data.py', '02_getnormdata.py', '03_Stat_LC.py', '03_Stat_MM.py', '04_Ind_LC.py', '04_Ind_LC_original.py', '04_Ind_MM.py']
[629, 1147, 1268, 1382, 1646, 1937, 2178]
