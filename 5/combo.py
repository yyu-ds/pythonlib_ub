# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 14:46:06 2019

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

# LC portfolio
dat['Net_Sales'] =  dat['Net Sales']
dat_lc = dat.query('Net_Sales>1e9')

# valid audit method filtering
valid2 = dat_lc.loc[dat_lc['Audit_Method'] != 'Proforma']
valid2 = valid2.loc[valid2['Audit_Method'] != 'Projection']


valid2['Gua_override'] =  valid2['PD_Risk_Rating_After_Gtee'] - valid2['PD_Risk_Rating_After_RLA']
valid2 = valid2.query('Gua_override==0')
valid2['RLA_Notches'].fillna(0, inplace=True)
valid2['Override_Action'].fillna(0, inplace=True)


valid2.to_pickle(r'data\newdata_ready.pkl')# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 14:46:06 2019

@author: ub71894
"""
import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI_redev")

dat = pd.read_pickle(r'data\newdata_ready.pkl')

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

dat.to_pickle(r'data\newdata_addratios.pkl')# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 14:46:06 2019

@author: ub71894
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI_redev")

#%%
olddata = pd.read_pickle(r'C:\Users\ub71894\Documents\Projects\CNI\newdata\combo_1000.pkl.xz')
to_rename = {
'qual1':'Strength_SOR_Prevent_Default',
'qual2':'Level_Waiver_Covenant_Mod',
'qual3':'Mgmt_Resp_Adverse_Conditions',
'qual4':'Vulnerability_To_Changes',
}
olddata.rename(columns=to_rename, inplace=True)

#%%
newdata = pd.read_pickle(r'data\newdata_addratios.pkl')
to_rename = {
'Customer_Name':'Customer Long Name',
'archive_date':'timestamp',
'FundsFromOperations_Modified':'size@Funds from Operations_Modified',
'FreeOperatingCashFlow_Modified':'size@Free Operating Cash Flow_Modified',
'Audit_Method':'Audit Method'
}
newdata.rename(columns=to_rename, inplace=True)

common_cols = list(set(list(olddata))&set(list(newdata)))


#%% merge data
common_cols=[
 'CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'NAICS_Cd',
 'Underwriter_Guideline',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'ExternalRating_PDRR',
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Mgmt_Resp_Adverse_Conditions',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',
 'Info_Rptg_Timely_Manner',
 'Excp_Underwrite_For_Leverage',
 'Pct_Revenue_3_Large_Custs',
 'Override_Action',
 'RLA_Notches',
 'AUDITMETHOD',
 'Audit Method',

 'liq@Union Bank Quick Ratio',

 'liq@Union Bank Current Ratio',

 'prof@NP_exc_EI_to_TA',

 'size@Total Inventory',

 'liq@CA_exc_TI_to_/TL',

 'liq@CA_to_TL',

 'bs@TD_to_UBTangNW',

 'prof@UBEBIT_to_TangA',

 'bs@CPLTD',

 'ds@INTERESTEXPENSE',

 'prof@EBIT_to_TA',

 'size@Current Assets',

 'cf@TD_to_EBIT_exc_Div_exc_Taxes',

 'size@Free Operating Cash Flow (FOCF)',

 'bs@TD_to_Capt',

 'ds@EBIT_exc_Div_exc_Taxes_to_IE',

 'liq@Current Ratio',

 'prof@EBIT_to_NS',

 'size@Free Operating Cash Flow_Modified',

 'cf@FOCF_to_TL',

 'cf@AdjTD_to_NP_and_Dep_and_Amo',

 'bs@SD_to_Capt',

 'prof@RE_to_TA',

 'ds@NP_to_IE',

 'size@Capitalization',

 'bs@TD_to_TNW',

 'prof@DividendCommon',

 'act@NS_to_TA',

 'prof@EBITDA_to_TA',

 'ds@AFTERTAXEXPENSE',

 'ds@EBIT_to_IE',

 'act@NS_to_NAR',

 'size@Amortization',

 'size@Total Net Worth',

 'size@Adjusted Total Debt',

 'bs@TLTD_to_TNW',

 'prof@Gross Profit Margin %',

 'prof@UBEBIT_to_Capt',

 'liq@CA_exc_TI_to_/AdjTD',

 'bs@TD_to_CA_exc_CL',

 'act@NS_to_CL',

 'bs@TLTD_to_Capt',

 'ds@Interest Expense',

 'liq@RE_to_CL',

 'bs@TL_to_Capt',

 'liq@ECE_to_CL',

 'bs@Total LTD',

 'cf@AdjTD_to_EBITDA',

 'cf@TD_to_NP_and_Dep_and_Amo',

 'ds@UBEBITDA_to_IE',

 'bs@TD_to_AdjCapt',

 'size@Net Operating Profit',

 'prof@NOP_to_TangNW',

 'cf@Ending Cash & Equivalents',

 'ds@EBIT_to_DS',

 'prof@EBITDA_to_NS',

 'liq@CA_exc_CL_to_TL',

 'size@Extraordinary Items',

 'prof@Return on Equity',

 'ds@EBITDA_to_IE',

 'ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',

 'ds@UBEBIT_to_IE',

 'liq@CA_exc_TI_to_/TA',

 'prof@NP_exc_EI',

 'size@Total Assets',

 'bs@TD_to_TangNW',

 'cf@AdjTD_to_ACF',

 'prof@NOP_to_NS',

 'liq@ECE_to_CA',

 'size@TangNW_to_TA',

 'size@TNW_to_TA_exc_CA',

 'size@Union Bank EBIT',

 'bs@SD_to_AdjCapt',

 'size@EBITDA',

 'bs@TLTD_to_TangNW',

 'bs@TLTD_to_TLTD_and_TNW',

 'bs@AdjTD_to_AdjCapt',

 'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',

 'ds@ACF_to_DS',

 'prof@PbT_to_TA',

 'bs@CL_to_TangNW',

 'ds@Debt Service',

 'prof@NOP_to_NP',

 'cf@TD_to_EBITDA',

 'cf@SD_to_UBEBITDA',

 'ds@UBEBIT_exc_Div_exc_Taxes_to_DS',

 'liq@CA_exc_TI_to_TD',

 'prof@EBITDA_to_TangA',

 'prof@UBEBIT_to_NS',

 'prof@AFTERTAXINCOME',

 'ds@NS_to_IE',

 'cf@TD_to_ACF',

 'cf@FFO_to_TD',

 'ds@EBIT_exc_Div_exc_Taxes_to_DS',

 'liq@ECE_to_TD',

 'bs@CL_to_Capt',

 'liq@Quick Ratio',

 'size@EBIT',

 'size@Total Debt',

 'ds@DSCR',

 'ds@FFO_to_IE',

 'ds@NP_to_CL',

 'prof@EBIT_to_Capt',

 'size@Retained Earnings',

 'prof@RE_to_TNW',

 'prof@RE_to_UBTangNW',

 'ds@NP_to_TL',

 'prof@Net Profit Margin %',

 'prof@TangA_to_NS',

 'liq@CA_exc_CL_to_TA',

 'prof@UBEBITDA_to_NS',

 'bs@TD_to_TA',

 'size@TNW_to_TA',

 'prof@UBEBITDA_to_Capt',

 'prof@UBEBITDA_to_AdjCapt',

 'cf@TD_COP',

 'cf@AdjTD_to_ACF_and_LE',

 'cf@FOCF_to_TD',

 'size@Total Liabilities',

 'prof@EBIT_to_AdjCapt',

 'prof@Return on Assets',

 'ds@UBEBIT_exc_Div_exc_Taxes_to_IE',

 'prof@CD_to_NP',

 'ds@NP_and_IE_to_IE',

 'prof@EBIT_to_TangA',

 'cf@Depreciation',

 'prof@EBITDA_to_Capt',

 'bs@AdjTD_to_Capt',

 'size@Current Liabilities',

 'liq@CA_to_TA',

 'liq@ECE_to_TL',

 'bs@TLTD_to_AdjCapt',

 'ds@ACF_and_LE_to_DS_and_LE',

 'size@Union Bank EBITDA',

 'ds@UBEBIT_and_LE_to_DS_and_LE',

 'size@Tangible Net Worth',

 'bs@CL_to_TA',

 'bs@TL_to_TA',

 'bs@TL_to_UBTangNW',

 'bs@CL_to_TL',

 'prof@UBEBITDA_to_TangA',

 'cf@AdjTD_to_UBEBITDA',

 'bs@TD_to_TA_exc_TL',

 'size@Profit before Taxes',

 'size@Net Profit',

 'size@UBTangNW_to_TA',

 'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',

 'prof@EBIT_exc_II_to_Capt',

 'bs@TL_to_TL_exc_CL',

 'prof@UBEBIT_to_AdjCapt',

 'bs@TLTD_to_UBTangNW',

 'prof@NOP_to_TNW',

 'cf@ACF',

 'cf@SD_to_EBITDA',

 'size@Net_Sales',

 'act@NS_to_Inv',

 'bs@TL_to_AdjCapt',

 'size@TangNW_to_TA_exc_CA',

 'size@Union Bank Tangible Net Worth',

 'liq@ECE_to_TA',

 'bs@Senior Debt',

 'prof@Operating Profit Margin %',

 'prof@Dividends',

 'ds@TL_to_IE',

 'size@Funds from Operations (FFO)',

 'prof@UBEBIT_to_TA',

 'ds@UBEBIT_to_DS',

 'prof@UBEBITDA_to_TA',

 'size@Net Accounts Receivable',

 'cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div',

 'liq@CA_exc_CL_to_CA',

 'ds@NP_and_IE_to_TL',

 'prof@EBITDA_to_AdjCapt',

 'bs@TLTD_to_TLTD_and_UBTangNW',

 'liq@CA_exc_CL_to_TD',

 'ds@EBIT_and_LE_to_DS_and_LE',

 'bs@CL_to_UBTangNW',

 'ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',

 'bs@CL_to_AdjCapt',

 'prof@DIVIDENDSSTOCK',

 'prof@NOP_to_UBTangNW',

 'act@NS_to_UBTangNW',

 'size@Adjusted Capitalization',

 'bs@TLTD_to_TA',

 'bs@LONGTERMDEBT',

 'size@Funds from Operations_Modified',

 'liq@ECE_to_AdjTD',

 'prof@NOP_to_TA',

 'act@NS_to_TNW',

 'prof@DIVIDENDSPREF',

 'prof@Average Profit Margin, 2 yrs',

 'size@Tangible Assets',

 'prof@Interest Income',

 'size@UBTangNW_to_TA_exc_CA',

 'cf@TD_to_UBEBITDA',

 'cf@TD_to_ACF_and_LE',

 'cf@Lease Expense',

 'liq@CA_exc_CL_to_AdjTD',

 'bs@TL_to_TangNW',

 'liq@CA_exc_CL_to_CL',

 'bs@CL_to_TNW',

 'bs@TL_to_TNW',
]

dat = pd.concat([olddata[common_cols], newdata[common_cols]], axis=0)
dat.to_pickle(r'data\data_1998_2019.pkl')
## -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:53:41 2019

@author: ub71894
"""

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from PDScorecardTool.Process import SomersD
from PDScorecardTool.Process import PD_frPDRR_autoMS, logitPD_frPDRR_autoMS
import pickle
filehandler = open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_LC.pkl','rb')
model = pickle.load(filehandler)


dat = pd.read_pickle(r'data\data_1998_2019.pkl')

dat['Final_beforeRLA'] = dat['Final_PD_Risk_Rating'] - dat['RLA_Notches']
dat['Final_beforeJBA'] = dat['Final_beforeRLA'] - dat[ 'Override_Action'] # 84% equal to Prelim

dat = PD_frPDRR_autoMS(dat, model, 'Final_beforeRLA', timestamp='timestamp')
dat.rename(columns={'PD_frPDRR':'PD_frPDRR_bfRLA'}, inplace=True)
dat = PD_frPDRR_autoMS(dat, model, 'Final_beforeJBA', timestamp='timestamp')
dat.rename(columns={'PD_frPDRR':'PD_frPDRR_bfJBA'}, inplace=True)
dat = PD_frPDRR_autoMS(dat, model, 'Final_PD_Risk_Rating', timestamp='timestamp')

dat = logitPD_frPDRR_autoMS(dat, model, 'Final_beforeRLA', timestamp='timestamp')
dat.rename(columns={'logitPD_frPDRR':'logitPD_frPDRR_bfRLA'}, inplace=True)
dat = logitPD_frPDRR_autoMS(dat, model, 'Final_beforeJBA', timestamp='timestamp')
dat.rename(columns={'logitPD_frPDRR':'logitPD_frPDRR_bfJBA'}, inplace=True)
dat = logitPD_frPDRR_autoMS(dat, model, 'Final_PD_Risk_Rating', timestamp='timestamp')



dat_2010 = dat.query('timestamp>=20100101')
dat_2015 = dat.query('timestamp>=20150101')
dat_newms = dat.query('timestamp>=20160501')
def quality_check(dat, cols):
    pct=[]
    N = len(dat)
    for col in cols:
        pct.append(dat[col].count()/N)

    result=pd.Series(pct, index=cols)
    return(result)



#%% quant
pl_candidates = ['liq@Union Bank Quick Ratio',

 'liq@Union Bank Current Ratio',

 'prof@NP_exc_EI_to_TA',

 'size@Total Inventory',

 'liq@CA_exc_TI_to_/TL',

 'liq@CA_to_TL',

 'bs@TD_to_UBTangNW',

 'prof@UBEBIT_to_TangA',

 'bs@CPLTD',

 'ds@INTERESTEXPENSE',

 'prof@EBIT_to_TA',

 'size@Current Assets',

 'cf@TD_to_EBIT_exc_Div_exc_Taxes',

 'size@Free Operating Cash Flow (FOCF)',

 'bs@TD_to_Capt',

 'ds@EBIT_exc_Div_exc_Taxes_to_IE',

 'liq@Current Ratio',

 'prof@EBIT_to_NS',

 'size@Free Operating Cash Flow_Modified',

 'cf@FOCF_to_TL',

 'cf@AdjTD_to_NP_and_Dep_and_Amo',

 'bs@SD_to_Capt',

 'prof@RE_to_TA',

 'ds@NP_to_IE',

 'size@Capitalization',

 'bs@TD_to_TNW',

 'prof@DividendCommon',

 'act@NS_to_TA',

 'prof@EBITDA_to_TA',

 'ds@AFTERTAXEXPENSE',

 'ds@EBIT_to_IE',

 'act@NS_to_NAR',

 'size@Amortization',

 'size@Total Net Worth',

 'size@Adjusted Total Debt',

 'bs@TLTD_to_TNW',

 'prof@Gross Profit Margin %',

 'prof@UBEBIT_to_Capt',

 'liq@CA_exc_TI_to_/AdjTD',

 'bs@TD_to_CA_exc_CL',

 'act@NS_to_CL',

 'bs@TLTD_to_Capt',

 'ds@Interest Expense',

 'liq@RE_to_CL',

 'bs@TL_to_Capt',

 'liq@ECE_to_CL',

 'bs@Total LTD',

 'cf@AdjTD_to_EBITDA',

 'cf@TD_to_NP_and_Dep_and_Amo',

 'ds@UBEBITDA_to_IE',

 'bs@TD_to_AdjCapt',

 'size@Net Operating Profit',

 'prof@NOP_to_TangNW',

 'cf@Ending Cash & Equivalents',

 'ds@EBIT_to_DS',

 'prof@EBITDA_to_NS',

 'liq@CA_exc_CL_to_TL',

 'size@Extraordinary Items',

 'prof@Return on Equity',

 'ds@EBITDA_to_IE',

 'ds@UBEBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',

 'ds@UBEBIT_to_IE',

 'liq@CA_exc_TI_to_/TA',

 'prof@NP_exc_EI',

 'size@Total Assets',

 'bs@TD_to_TangNW',

 'cf@AdjTD_to_ACF',

 'prof@NOP_to_NS',

 'liq@ECE_to_CA',

 'size@TangNW_to_TA',

 'size@TNW_to_TA_exc_CA',

 'size@Union Bank EBIT',

 'bs@SD_to_AdjCapt',

 'size@EBITDA',

 'bs@TLTD_to_TangNW',

 'bs@TLTD_to_TLTD_and_TNW',

 'bs@AdjTD_to_AdjCapt',

 'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',

 'ds@ACF_to_DS',

 'prof@PbT_to_TA',

 'bs@CL_to_TangNW',

 'ds@Debt Service',

 'prof@NOP_to_NP',

 'cf@TD_to_EBITDA',

 'cf@SD_to_UBEBITDA',

 'ds@UBEBIT_exc_Div_exc_Taxes_to_DS',

 'liq@CA_exc_TI_to_TD',

 'prof@EBITDA_to_TangA',

 'prof@UBEBIT_to_NS',

 'prof@AFTERTAXINCOME',

 'ds@NS_to_IE',

 'cf@TD_to_ACF',

 'cf@FFO_to_TD',

 'ds@EBIT_exc_Div_exc_Taxes_to_DS',

 'liq@ECE_to_TD',

 'bs@CL_to_Capt',

 'liq@Quick Ratio',

 'size@EBIT',

 'size@Total Debt',

 'ds@DSCR',

 'ds@FFO_to_IE',

 'ds@NP_to_CL',

 'prof@EBIT_to_Capt',

 'size@Retained Earnings',

 'prof@RE_to_TNW',

 'prof@RE_to_UBTangNW',

 'ds@NP_to_TL',

 'prof@Net Profit Margin %',

 'prof@TangA_to_NS',

 'liq@CA_exc_CL_to_TA',

 'prof@UBEBITDA_to_NS',

 'bs@TD_to_TA',

 'size@TNW_to_TA',

 'prof@UBEBITDA_to_Capt',

 'prof@UBEBITDA_to_AdjCapt',

 'cf@TD_COP',

 'cf@AdjTD_to_ACF_and_LE',

 'cf@FOCF_to_TD',

 'size@Total Liabilities',

 'prof@EBIT_to_AdjCapt',

 'prof@Return on Assets',

 'ds@UBEBIT_exc_Div_exc_Taxes_to_IE',

 'prof@CD_to_NP',

 'ds@NP_and_IE_to_IE',

 'prof@EBIT_to_TangA',

 'cf@Depreciation',

 'prof@EBITDA_to_Capt',

 'bs@AdjTD_to_Capt',

 'size@Current Liabilities',

 'liq@CA_to_TA',

 'liq@ECE_to_TL',

 'bs@TLTD_to_AdjCapt',

 'ds@ACF_and_LE_to_DS_and_LE',

 'size@Union Bank EBITDA',

 'ds@UBEBIT_and_LE_to_DS_and_LE',

 'size@Tangible Net Worth',

 'bs@CL_to_TA',

 'bs@TL_to_TA',

 'bs@TL_to_UBTangNW',

 'bs@CL_to_TL',

 'prof@UBEBITDA_to_TangA',

 'cf@AdjTD_to_UBEBITDA',

 'bs@TD_to_TA_exc_TL',

 'size@Profit before Taxes',

 'size@Net Profit',

 'size@UBTangNW_to_TA',

 'cf@TD_to_NP_and_Dep_and_Amo_exc_Div',

 'prof@EBIT_exc_II_to_Capt',

 'bs@TL_to_TL_exc_CL',

 'prof@UBEBIT_to_AdjCapt',

 'bs@TLTD_to_UBTangNW',

 'prof@NOP_to_TNW',

 'cf@ACF',

 'cf@SD_to_EBITDA',

 'size@Net_Sales',

 'act@NS_to_Inv',

 'bs@TL_to_AdjCapt',

 'size@TangNW_to_TA_exc_CA',

 'size@Union Bank Tangible Net Worth',

 'liq@ECE_to_TA',

 'bs@Senior Debt',

 'prof@Operating Profit Margin %',

 'prof@Dividends',

 'ds@TL_to_IE',

 'size@Funds from Operations (FFO)',

 'prof@UBEBIT_to_TA',

 'ds@UBEBIT_to_DS',

 'prof@UBEBITDA_to_TA',

 'size@Net Accounts Receivable',

 'cf@AdjTD_to_NP_and_Dep_and_Amo_exc_Div',

 'liq@CA_exc_CL_to_CA',

 'ds@NP_and_IE_to_TL',

 'prof@EBITDA_to_AdjCapt',

 'bs@TLTD_to_TLTD_and_UBTangNW',

 'liq@CA_exc_CL_to_TD',

 'ds@EBIT_and_LE_to_DS_and_LE',

 'bs@CL_to_UBTangNW',

 'ds@EBIT_exc_Div_exc_Taxes_and_LE_to_DS_and_LE',

 'bs@CL_to_AdjCapt',

 'prof@DIVIDENDSSTOCK',

 'prof@NOP_to_UBTangNW',

 'act@NS_to_UBTangNW',

 'size@Adjusted Capitalization',

 'bs@TLTD_to_TA',

 'bs@LONGTERMDEBT',

 'size@Funds from Operations_Modified',

 'liq@ECE_to_AdjTD',

 'prof@NOP_to_TA',

 'act@NS_to_TNW',

 'prof@DIVIDENDSPREF',

 'prof@Average Profit Margin, 2 yrs',

 'size@Tangible Assets',

 'prof@Interest Income',

 'size@UBTangNW_to_TA_exc_CA',

 'cf@TD_to_UBEBITDA',

 'cf@TD_to_ACF_and_LE',

 'cf@Lease Expense',

 'liq@CA_exc_CL_to_AdjTD',

 'bs@TL_to_TangNW',

 'liq@CA_exc_CL_to_CL',

 'bs@CL_to_TNW',

 'bs@TL_to_TNW',]



temp = quality_check(dat_2015, pl_candidates)


# quali
pl_candidates = ['Strength_SOR_Prevent_Default',
'Level_Waiver_Covenant_Mod',
'Management_Quality',
'Mgmt_Resp_Adverse_Conditions',
'Vulnerability_To_Changes',
'Access_Outside_Capital',
'Market_Outlook_Of_Borrower',
'Info_Rptg_Timely_Manner',
'Excp_Underwrite_For_Leverage',
'Pct_Revenue_3_Large_Custs',]

temp = quality_check(dat_2015, pl_candidates)


#%% remove bad quality cols
to_remove_cols=['size@Free Operating Cash Flow_Modified',
'prof@Return on Equity',
'prof@Average Profit Margin, 2 yrs',
'Pct_Revenue_3_Large_Custs']

pl_cols = list(dat)
for item in to_remove_cols:
    pl_cols.remove(item)


dat = dat[pl_cols]


#%%  fillna for the 2 dataset repectively
dat_2010 = dat.query('timestamp>=20100101')
dat_2015 = dat.query('timestamp>=20150101')
dat_newms = dat.query('timestamp>=20160501')

to_fillna_cols = list(dat)[21:220]
dat_2010[to_fillna_cols] = dat_2010[to_fillna_cols].fillna(dat_2010[to_fillna_cols].median())
dat_2015[to_fillna_cols] = dat_2015[to_fillna_cols].fillna(dat_2015[to_fillna_cols].median())
dat_newms[to_fillna_cols] = dat_newms[to_fillna_cols].fillna(dat_newms[to_fillna_cols].median())

temp = quality_check(dat_2015, to_fillna_cols)


dat_2010.to_pickle(r'data\dat_2010_filled.pkl')
dat_2015.to_pickle(r'data\dat_2015_filled.pkl')
dat_newms.to_pickle(r'data\dat_newms_filled.pkl')# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:53:41 2019

@author: ub71894
"""

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from PDScorecardTool.Process import SomersD
import matplotlib.pyplot as plt
import seaborn as sns
dat_2010 = pd.read_pickle(r'data\dat_2010_filled.pkl')
dat_2015 = pd.read_pickle(r'data\dat_2015_filled.pkl')
dat_newms = pd.read_pickle(r'data\dat_newms_filled.pkl')



#%% quant
pl_candidates = list(dat_2010)[21:220]
writer = pd.ExcelWriter(r'SFA\SFA_SomersD_updated.xlsx')
pl_data = [dat_2010, dat_2015, dat_newms]
pl_data_name = ['dat_2010', 'dat_2015', 'dat_newms']
pl_target = ['Final_PD_Risk_Rating','Final_beforeRLA','Final_beforeJBA']

pl_somersd=[]
for i,dat in enumerate(pl_data):
    name = pl_data_name[i]
    for target in pl_target:
        pl_sd = []
        for factor in pl_candidates:
            df = dat[[factor,target]].copy()
            df.dropna(how='any', inplace=True)
            df[factor] = df[factor].clip(np.nanmin(df[factor][df[factor] != -np.inf]), np.nanmax(df[factor][df[factor] != np.inf]))
            pl_sd.append(np.abs(SomersD(df[target], df[factor])))
        pl_somersd.append(pl_sd)
  

df_somersd = pd.DataFrame()
df_somersd['2010_Final_PDRR'] = pl_somersd[0]
df_somersd['2010_Final_bfRLA'] = pl_somersd[1]
df_somersd['2010_Final_bfJBA'] = pl_somersd[2]
df_somersd['2015_Final_PDRR'] = pl_somersd[3]
df_somersd['2015_Final_bfRLA'] = pl_somersd[4]
df_somersd['2015_Final_bfJBA'] = pl_somersd[5]
df_somersd['newms_Final_PDRR'] = pl_somersd[6]
df_somersd['newms_Final_bfRLA'] = pl_somersd[7]
df_somersd['newms_Final_bfJBA'] = pl_somersd[8]
df_somersd.index = pl_candidates

df_somersd.to_excel(writer, 'SFA')


writer.save()


#%% quali


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


pl_candidates = list(dat_2010)[8:17]
barplot(dat_2015, subset=pl_candidates, y_col='PD_frPDRR', savefig=True)

# remove 3 candidates
pl_candidates = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]

for name in pl_candidates:
    dat_2015['factor_meanPD'] = dat_2015[name]
    dat_2015['factor_meanPD'].replace(dict(dat_2015.groupby(name).mean()['PD_frPDRR']), inplace=True)
    dat_2015['factor_meanlogitPD'] = [np.log(x/(1-x)) for x in dat_2015['factor_meanPD']]
    s_mean = dat_2015['factor_meanlogitPD'].mean()
    s_std = dat_2015['factor_meanlogitPD'].std()
    dat_2015['factor_score'] = 50*(dat_2015['factor_meanlogitPD'] - s_mean) / s_std
    print(dat_2015.groupby(name).mean()['factor_score'])
    sd = SomersD(dat_2015['Final_PD_Risk_Rating'], dat_2015['factor_score'])
    print('SomersD of {name} is {sd:6.5f}'.format(name=name,sd=sd))
    print('**************************************************************')


# -*- coding: utf-8 -*-
"""
Created on Tue Jul  2 10:53:41 2019

@author: ub71894
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI_redev")

dat_2010 = pd.read_pickle(r'data\dat_2010_filled.pkl')
dat_2015 = pd.read_pickle(r'data\dat_2015_filled.pkl')
dat_newms = pd.read_pickle(r'data\dat_newms_filled.pkl')



dat_2010_train = dat_2010.query('timestamp<=20181231')
dat_2010_test = dat_2010.query('timestamp>20181231')
dat_2015_train = dat_2015.query('timestamp<=20181231')
dat_2015_test = dat_2015.query('timestamp>20181231')
dat_newms_train = dat_newms.query('timestamp<=20181231')
dat_newms_test = dat_newms.query('timestamp>20181231')

dat_2010_train.to_pickle(r'data\dat_2010_train.pkl')
dat_2010_test.to_pickle(r'data\dat_2010_test.pkl') 
dat_2015_train.to_pickle(r'data\dat_2015_train.pkl')
dat_2015_test.to_pickle(r'data\dat_2015_test.pkl') 
dat_newms_train.to_pickle(r'data\dat_newms_train.pkl')
dat_newms_test.to_pickle(r'data\dat_newms_test.pkl') 

mid_point = np.sqrt(cap_mean*floor_mean)
if floor_mean>cap_mean and neg_mean<mid_point: # means it's closer to cap
    pl_invalid_neg.append(factor)
elif floor_mean<cap_mean and neg_mean>mid_point: # means it's closer to cap
    pl_invalid_neg.append(factor)
else:
    pl_invalid_neg.append(0)

# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 16:23:40 2019

@author: ub71894
"""




import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]

#%%
dat = pd.read_pickle(r'data\dat_2010_train.pkl') # setting
target = 'Final_PD_Risk_Rating'  # setting
target_PD = 'PD_frPDRR'  # setting
target_logitPD = 'logitPD_frPDRR'  # setting
sd_col_name = '2010_Final_PDRR'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

sd = pd.read_excel(r'SFA\SFA_SomersD_updated.xlsx')
sd.sort_values(by=[sd_col_name], inplace=True, ascending=False)
pl_top_candidates=list(sd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(factor) 
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)

#######################################
mid_point = np.sqrt(cap_mean*floor_mean)
if floor_mean>cap_mean and neg_mean<mid_point: # means it's closer to cap
    pl_invalid_neg.append(factor)
elif floor_mean<cap_mean and neg_mean>mid_point: # means it's closer to cap
    pl_invalid_neg.append(factor)
else:
    pl_invalid_neg.append(0)

#################################################

# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand



#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)+model.quali_factor
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(6+num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\B_model_595.xlsx')

print("--- %s seconds ---" % (time.time() - start_time))






#%% model spec
model_spec=['size@Profit before Taxes',
 'size@Union Bank EBITDA',
 'prof@Net Profit Margin %',
 'liq@ECE_to_TL',
 'bs@TD_to_Capt',
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower']




x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values

df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.7646263010040603

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)



#%% test data
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')

for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.7560859818013979

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]

#%%
dat = pd.read_pickle(r'data\dat_2010_train.pkl') # setting
target = 'Final_beforeRLA'  # setting
target_PD = 'PD_frPDRR_bfRLA'  # setting
target_logitPD = 'logitPD_frPDRR_bfRLA'  # setting
sd_col_name = '2010_Final_bfRLA'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

sd = pd.read_excel(r'SFA\SFA_SomersD_updated.xlsx')
sd.sort_values(by=[sd_col_name], inplace=True, ascending=False)
pl_top_candidates=list(sd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand





#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)+model.quali_factor
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(6+num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\C_model_595.xlsx')

print("--- %s seconds ---" % (time.time() - start_time))





#%% model spec
model_spec=['size@Tangible Assets',
 'prof@Net Profit Margin %',
 'liq@ECE_to_TL',
 'cf@AdjTD_to_UBEBITDA',
 'bs@TD_to_Capt',
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes']



x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values

df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
#  0.821084984262708

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)




#%% test data
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')

for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.8285275911327443



import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]

#%%
dat = pd.read_pickle(r'data\dat_2015_train.pkl') # setting
target = 'Final_PD_Risk_Rating'  # setting
target_PD = 'PD_frPDRR'  # setting
target_logitPD = 'logitPD_frPDRR'  # setting
sd_col_name = '2015_Final_PDRR'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

sd = pd.read_excel(r'SFA\SFA_SomersD_updated.xlsx')
sd.sort_values(by=[sd_col_name], inplace=True, ascending=False)
pl_top_candidates=list(sd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand



#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)+model.quali_factor
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(6+num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\E_model_595.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%% model spec
model_spec=['prof@RE_to_TA',
 'size@Tangible Assets',
 'prof@Net Profit Margin %',
 'cf@SD_to_UBEBITDA',
 'bs@TD_to_Capt',
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital']



x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values

df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.7634826065431127

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)



#%% test data
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')

for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.7691151259396017
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]

#%%
dat = pd.read_pickle(r'data\dat_2015_train.pkl') # setting
target = 'Final_beforeRLA'  # setting
target_PD = 'PD_frPDRR_bfRLA'  # setting
target_logitPD = 'logitPD_frPDRR_bfRLA'  # setting
sd_col_name = '2015_Final_bfRLA'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

sd = pd.read_excel(r'SFA\SFA_SomersD_updated.xlsx')
sd.sort_values(by=[sd_col_name], inplace=True, ascending=False)
pl_top_candidates=list(sd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)+model.quali_factor
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(6+num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\F_model_595.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))





#%% model spec
model_spec=['size@Tangible Assets',
 'prof@Net Profit Margin %',
 'prof@PbT_to_TA',
 'bs@AdjTD_to_AdjCapt',
 'liq@ECE_to_TL',
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes', 
 'Access_Outside_Capital']




x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values


df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.8155052175814408

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)


#%% test data
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')

for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.8320988307496958
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]

#%%
dat = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
target = 'Final_PD_Risk_Rating'  # setting
target_PD = 'PD_frPDRR'  # setting
target_logitPD = 'logitPD_frPDRR'  # setting
sd_col_name = 'newms_Final_PDRR'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

sd = pd.read_excel(r'SFA\SFA_SomersD_updated.xlsx')
sd.sort_values(by=[sd_col_name], inplace=True, ascending=False)
pl_top_candidates=list(sd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)+model.quali_factor
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(6+num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\H_model_595.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%% model spec
model_spec=['prof@RE_to_TA',
 'size@Tangible Assets',
 'prof@Net Profit Margin %',
 'cf@SD_to_UBEBITDA',
 'bs@TD_to_Capt',
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes', 'Market_Outlook_Of_Borrower']



x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
result.summary()


df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.7854120814919969

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)


#%% test data
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')

for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.7650270341553475


#%% test on core data:
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = MAUG_mapping(dat_test)
dat_test['core'] = dat_test['Industry_by_MAUG'].copy()
dat_test['core'].replace(pd_core, inplace=True)
dat_test['core'].replace(pd_noncore, inplace=True)
dat_test = dat_test.query('core=="Core"')


for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])

# 0.764019811471481
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans,MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]

#%%
dat = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
target = 'Final_beforeRLA'  # setting
target_PD = 'PD_frPDRR_bfRLA'  # setting
target_logitPD = 'logitPD_frPDRR_bfRLA'  # setting
sd_col_name = 'newms_Final_bfRLA'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

sd = pd.read_excel(r'SFA\SFA_SomersD_updated.xlsx')
sd.sort_values(by=[sd_col_name], inplace=True, ascending=False)
pl_top_candidates=list(sd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)+model.quali_factor
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(6+num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\I_model_595.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))




#%% model spec
model_spec=['size@Tangible Assets',
 'ds@EBITDA_to_IE',
 'prof@Net Profit Margin %',
 'cf@SD_to_UBEBITDA',
 'bs@TL_to_TA',
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes']


x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
result.summary()

df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.8205808757791079

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)


#%% test data
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')

for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.7920480397862547




#%% test on core data:
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = MAUG_mapping(dat_test)
dat_test['core'] = dat_test['Industry_by_MAUG'].copy()
dat_test['core'].replace(pd_core, inplace=True)
dat_test['core'].replace(pd_noncore, inplace=True)
dat_test = dat_test.query('core=="Core"')


for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])

# 0.770495738806866
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]


#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = MAUG_mapping(data)
data['core'] = data['Industry_by_MAUG'].copy()
data['core'].replace(pd_core, inplace=True)
data['core'].replace(pd_noncore, inplace=True)

dat = data.query('core=="Core"')
target = 'Final_PD_Risk_Rating'  # setting
target_PD = 'PD_frPDRR'  # setting
target_logitPD = 'logitPD_frPDRR'  # setting
sd_col_name = 'newms_Final_PDRR'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

pl_candidates = list(dat)[21:220]
pl_sd = []
for factor in pl_candidates:
    df = dat[[factor,target]].copy()
    df.dropna(how='any', inplace=True)
    df[factor] = df[factor].clip(np.nanmin(df[factor][df[factor] != -np.inf]), np.nanmax(df[factor][df[factor] != np.inf]))
    pl_sd.append(np.abs(SomersD(df[target], df[factor])))


df_somersd = pd.DataFrame()
df_somersd['SD'] = pl_sd
df_somersd.index = pl_candidates
df_somersd.sort_values(by=['SD'], inplace=True, ascending=False)

pl_top_candidates=list(df_somersd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)+model.quali_factor
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(6+num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\H_model_core.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%% model spec
model_spec=['size@Tangible Assets',
 'ds@NP_to_TL',
 'prof@EBIT_to_NS',
 'prof@RE_to_TA',
 'cf@SD_to_UBEBITDA',
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital', 
 'Market_Outlook_Of_Borrower']



x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
result.summary()


df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.7839421683239131

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)


#%% test core data

dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = MAUG_mapping(dat_test)
dat_test['core'] = dat_test['Industry_by_MAUG'].copy()
dat_test['core'].replace(pd_core, inplace=True)
dat_test['core'].replace(pd_noncore, inplace=True)
dat_test = dat_test.query('core=="Core"')


for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.7716088832081802

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]

#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = MAUG_mapping(data)
data['core'] = data['Industry_by_MAUG'].copy()
data['core'].replace(pd_core, inplace=True)
data['core'].replace(pd_noncore, inplace=True)

dat = data.query('core=="Core"')
target = 'Final_beforeRLA'  # setting
target_PD = 'PD_frPDRR_bfRLA'  # setting
target_logitPD = 'logitPD_frPDRR_bfRLA'  # setting
sd_col_name = 'newms_Final_bfRLA'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

pl_candidates = list(dat)[21:220]
pl_sd = []
for factor in pl_candidates:
    df = dat[[factor,target]].copy()
    df.dropna(how='any', inplace=True)
    df[factor] = df[factor].clip(np.nanmin(df[factor][df[factor] != -np.inf]), np.nanmax(df[factor][df[factor] != np.inf]))
    pl_sd.append(np.abs(SomersD(df[target], df[factor])))


df_somersd = pd.DataFrame()
df_somersd['SD'] = pl_sd
df_somersd.index = pl_candidates
df_somersd.sort_values(by=['SD'], inplace=True, ascending=False)

pl_top_candidates=list(df_somersd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)+model.quali_factor
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(6+num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\I_model_core.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%% model spec
model_spec=['size@Tangible Assets',
 'ds@EBITDA_to_IE',
 'prof@Net Profit Margin %',
 'cf@SD_to_UBEBITDA',
 'prof@RE_to_TA',
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Market_Outlook_Of_Borrower']

x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
result.summary()


df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.8032340222017845

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)


#%% test data

dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = MAUG_mapping(dat_test)
dat_test['core'] = dat_test['Industry_by_MAUG'].copy()
dat_test['core'].replace(pd_core, inplace=True)
dat_test['core'].replace(pd_noncore, inplace=True)
dat_test = dat_test.query('core=="Core"')


for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.7512103388948905
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]


#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = data.query('Final_PD_Risk_Rating<=4')
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
dat = data.copy()
#dat = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')



target = 'Final_PD_Risk_Rating'  # setting
target_PD = 'PD_frPDRR'  # setting
target_logitPD = 'logitPD_frPDRR'  # setting
sd_col_name = 'newms_Final_PDRR'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

pl_candidates = list(dat)[21:220]
pl_sd = []
for factor in pl_candidates:
    df = dat[[factor,target]].copy()
    df.dropna(how='any', inplace=True)
    df[factor] = df[factor].clip(np.nanmin(df[factor][df[factor] != -np.inf]), np.nanmax(df[factor][df[factor] != np.inf]))
    pl_sd.append(np.abs(SomersD(df[target], df[factor])))


df_somersd = pd.DataFrame()
df_somersd['SD'] = pl_sd
df_somersd.index = pl_candidates
df_somersd.sort_values(by=['SD'], inplace=True, ascending=False)

pl_top_candidates=list(df_somersd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)+model.quali_factor
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(6+num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\H_model_good.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%% model spec
model_spec=['size@Total Debt',
 'ds@EBIT_and_LE_to_DS_and_LE',
 'size@Union Bank Tangible Net Worth',
 'bs@AdjTD_to_AdjCapt',
 'prof@RE_to_TNW',
 'Strength_SOR_Prevent_Default',
 #'Level_Waiver_Covenant_Mod',
 'Management_Quality', 'Vulnerability_To_Changes', 'Access_Outside_Capital', 'Market_Outlook_Of_Borrower']




x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
result.summary()


df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.6569222449224853

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)


#%% test core data

dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = dat_test.query('Final_PD_Risk_Rating<=4')

for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.645

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]


#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = data.query('Final_PD_Risk_Rating<=4')
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
#dat = data.copy()
dat = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')



target = 'Final_PD_Risk_Rating'  # setting
target_PD = 'PD_frPDRR'  # setting
target_logitPD = 'logitPD_frPDRR'  # setting
sd_col_name = 'newms_Final_PDRR'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

pl_candidates = list(dat)[21:220]
pl_sd = []
for factor in pl_candidates:
    df = dat[[factor,target]].copy()
    df.dropna(how='any', inplace=True)
    df[factor] = df[factor].clip(np.nanmin(df[factor][df[factor] != -np.inf]), np.nanmax(df[factor][df[factor] != np.inf]))
    pl_sd.append(np.abs(SomersD(df[target], df[factor])))


df_somersd = pd.DataFrame()
df_somersd['SD'] = pl_sd
df_somersd.index = pl_candidates
df_somersd.sort_values(by=['SD'], inplace=True, ascending=False)

pl_top_candidates=list(df_somersd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\H_model_good_nodup.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%% model spec
model_spec=['size@Current Assets', 'bs@AdjTD_to_Capt', 'prof@UBEBITDA_to_TangA']



x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
result.summary()


df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.46956829440905873

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)


#%% test core data

dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = dat_test.query('Final_PD_Risk_Rating<=4')

for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.44333333333333336

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from scipy.optimize import differential_evolution
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = [
'Strength_SOR_Prevent_Default',
'Level_Waiver_Covenant_Mod',
'Management_Quality',
'Vulnerability_To_Changes',
'Access_Outside_Capital',
'Market_Outlook_Of_Borrower'
]



def apply_bin(w):
    if w[0]>w[1]:
        w[0], w[1] = w[1], w[0]
    try:
        dat['bin'] = pd.qcut(dat[factor],  [0, w[0], w[1], 1.] ,labels=['1','2','3']) 
        temp = dat.groupby(by=['bin'])[target_PD].mean()
        dat[factor] = dat['bin'].replace(temp.to_dict())
    except ValueError:
        dat[factor] = 0


def _sd_bin(w):
    if w[0]>w[1]:
        w[0], w[1] = w[1], w[0]
    try:
        dat['bin'] = pd.qcut(dat[factor],  [0, w[0], w[1], 1.] ,labels=['1','2','3'])  
    except ValueError:
        return(0)
    temp = dat.groupby(by=['bin'])[target_PD].mean()
    dat['bin2'] = dat['bin'].replace(temp.to_dict())

    return(-np.abs(SomersD(dat[target], dat['bin2'])))


def apply_bin_test(data, pl_factors,  pl_bins):
    dat = data.copy()
    for i, factor in enumerate(pl_factors):
        try:
            dat['bin'] = pd.qcut(dat[factor],  [0, pl_bins[i][0], pl_bins[i][1], 1.] ,labels=['1','2','3']) 
            temp = dat.groupby(by=['bin'])[target_PD].mean()
            dat[factor] = dat['bin'].replace(temp.to_dict())
        except ValueError:
            dat[factor] = 0
    return (dat)

def load_bin(pl_factors):
    pl_bins = list()
    for factor in pl_factors:
        exec('pl_bins.append('+df_somersd.loc[factor, 'best_bin']+')')
    return (pl_bins)


def _calib(alpha):
    low_pd = model.MS['new_low']
    Intercept = alpha[0]
    slope =     alpha[1]
    dat['fitted_logit_pd'] = Intercept + slope * dat['TotalScore']
    dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat['fitted_logit_pd'] ]
    Ratings = []
    for i, row in dat.iterrows():
        Ratings.append(sum(low_pd<=(row.fitted_pd)))
    dat['fitted_PDRR'] = Ratings   

    return (-len(dat.query('{}==fitted_PDRR'.format(target))) / len(dat))


def calib_sd(alpha):
    low_pd = model.MS['new_low']
    Intercept = alpha[0]
    slope =     alpha[1]
    dat['fitted_logit_pd'] = Intercept + slope * dat['TotalScore']
    dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat['fitted_logit_pd'] ]
    Ratings = []
    for i, row in dat.iterrows():
        Ratings.append(sum(low_pd<=(row.fitted_pd)))
    dat['fitted_PDRR'] = Ratings   

    return (SomersD(dat[target], dat['fitted_PDRR']))



#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = data.query('Final_PD_Risk_Rating<=4')
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
#dat = data.copy()
dat = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')



target = 'Final_PD_Risk_Rating'  # setting
target_PD = 'PD_frPDRR'  # setting
target_logitPD = 'logitPD_frPDRR'  # setting
sd_col_name = 'newms_Final_PDRR'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

pl_candidates = list(dat)[21:220]

#%% binning


bounds = [(0,1), (0, 1)]
pl_best_bin=[]
for i,factor in enumerate(pl_candidates):
    res = differential_evolution(_sd_bin, bounds)
    print('factor #{} is binned'.format(i))
    apply_bin(res.x)
    pl_best_bin.append(list(res.x))



#%% SFA
pl_sd = []
for factor in pl_candidates:
    df = dat[[factor,target]].copy()
    df.dropna(how='any', inplace=True)
    pl_sd.append(np.abs(SomersD(df[target], df[factor])))


df_somersd = pd.DataFrame()
df_somersd['best_bin'] = pl_best_bin
df_somersd['SD'] = pl_sd
df_somersd.index = pl_candidates
df_somersd.sort_values(by=['SD'], inplace=True, ascending=False)
df_somersd.to_excel(r'SFA\SFA_best_bin_0730.xlsx')

pl_top_candidates=list(df_somersd.index)[:top]

# check sign
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))
np.sign(sfa)

#%%
df_somersd = pd.read_excel(r'SFA\SFA_best_bin_0730.xlsx')
df_somersd.index = df_somersd.Factor
dat = pd.read_pickle('binned_data.pkl')
#%% correlation cluster
# initial 
f, ax = plt.subplots(figsize=(20, 12))
sns.heatmap(dat[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(dat, pl_top_candidates)
plot_cluster_corr(dat, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]],pl_cat[cats[3]],pl_cat[cats[4]] 
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]],pl_cat[cats[3]],pl_cat[cats[4]] 
        ))

    for facs in py_list:
        names = list(facs)
        x_train = sm.add_constant(dat[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(dat[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(dat[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\H_model_good_nodup_5_bin_0730.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%% model spec
model_spec=['size@Retained Earnings', 
            'prof@NOP_to_NP', 
            'prof@TangA_to_NS', 
            'liq@ECE_to_CA', 
            'ds@NS_to_IE']



x_train = sm.add_constant(dat[model_spec], prepend = True)
linear = sm.OLS(dat[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
result.summary()

bounds = [(0.10,0.40), (0.10,0.40),(0.10,0.40),(0.10,0.40),(0.10,0.40)]
def _fun(w):
    tolscr = (w*dat[model_spec]).sum(axis=1)
    return(-SomersD(dat[target_logitPD], tolscr))

res = differential_evolution(_fun,bounds)





dat['TotalScore'] = (dat[model_spec]*weights).sum(axis=1)
SomersD(dat[target_logitPD], dat['TotalScore'])
# 0.7753007784854918

aa=dat.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= dat)


#%% test core data
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = dat_test.query('Final_PD_Risk_Rating<=4')


pl_factors = model_spec
pl_bins = load_bin(model_spec)

dat_test = apply_bin_test(dat_test, pl_factors,  pl_bins)
dat_test['TotalScore'] = (dat_test[model_spec]*weights).sum(axis=1)
SomersD(dat_test[target_logitPD], dat_test['TotalScore'])
# 0.6683333333333333



#%% calibration
mfa_result = pd.read_excel(r'MFA\H_model_good_nodup_5_bin_0730.xlsx')
mfa_result = mfa_result.query('sign=="correct" and max_pvalue<0.01')
mfa_result['sum_accu'] = mfa_result['R2'] + mfa_result['SD_insample']
mfa_result.sort_values(by=['sum_accu'], ascending=False, inplace=True)
mfa_result.reset_index(drop=True, inplace=True)

# collect quant factors from top 100 best models 
aa=mfa_result.head(2000)
pl_top_models = []
for index, df in aa.iterrows():
    exec('pl_top_models.append('+ df.models+')')



bounds = [(-10,0), (0, 0.2)]
pl_prior_sd_totalscore = []
pl_prior_sd_rating = []
pl_prior_match = []
pl_model_calib = []
pl_poster_sd_rating = []
pl_poster_match = []
pl_weights = []
pl_tolscore_mean = []
pl_tolscore_std = []


low_pd = model.MS['new_low']
start_time = time.time()
for i, model_spec in enumerate(pl_top_models):
    x_train = sm.add_constant(dat[model_spec], prepend = True)
    linear = sm.OLS(dat[target_logitPD], x_train, missing='drop')
    result = linear.fit(disp=0)
    stats = result.params[1:] / result.params[1:].sum()
    weights = stats.values
    pl_weights.append(weights)
    #result.summary()
    dat['TotalScore'] = (dat[model_spec]*weights).sum(axis=1)

    pl_tolscore_mean.append(dat.TotalScore.mean())
    pl_tolscore_std.append(dat.TotalScore.std())
    dat['TotalScore']= 50*(dat.TotalScore-dat.TotalScore.mean())/dat.TotalScore.std()
    # SomersD (with score) before calibration optimization
    pl_prior_sd_totalscore.append(SomersD(dat[target_logitPD], dat['TotalScore']))
    # Match Rate and SomersD(with rating) before calibration optimization
    dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in result.predict() ]
    Ratings = []
    for PD in dat['fitted_pd']:
        Ratings.append(sum(low_pd<=(PD)))
    dat['fitted_PDRR'] = Ratings   
    pl_prior_sd_rating.append(SomersD(dat[target], dat['fitted_PDRR']))
    pl_prior_match.append(len(dat.query('{}==fitted_PDRR'.format(target))) / len(dat))

    # optimized calibration by maximize match rate
    res = differential_evolution(_calib, bounds)
    print('model #{} is calibrated'.format(i))
    pl_model_calib.append(res.x)
    pl_poster_sd_rating.append(calib_sd(res.x))
    pl_poster_match.append(-res.fun)


df_result = pd.DataFrame()
df_result['model'] = pl_top_models
df_result['weights'] = pl_weights
df_result['pl_tolscore_mean'] = pl_pl_tolscore_mean
df_result['pl_tolscore_std'] = pl_pl_tolscore_std
df_result['params'] = pl_model_calib
df_result['prior_sd_totalscore'] = pl_prior_sd_totalscore
df_result['prior_sd_rating'] = pl_prior_sd_rating
df_result['prior_match'] = pl_prior_match
df_result['poster_sd_rating'] = pl_poster_sd_rating
df_result['poster_match'] = pl_poster_match


df_result.to_pickle('opt_calib_for_top2000_MFA.pkl')
df_result = pd.read_pickle('opt_calib_for_top2000_MFA.pkl')
#df_result.to_excel('df_result.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#  compare with LC
# test sample performance
# no opt on weights
#%%  test 

# A/A test
# dat_test = dat.copy()  
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = dat_test.query('Final_PD_Risk_Rating<=4')
df_params = pd.read_pickle('opt_calib_for_top2000_MFA.pkl')
low_pd = model.MS['new_low']

pl_prior_sd_totalscore = []
pl_poster_sd_rating = []
pl_poster_match = []
for i in range(2000):
    model_spec = df_params.loc[i,'model']
    pl_best_bin = load_bin(model_spec)
    model_weights = df_params.loc[i,'weights']
    tolscore_mean = df_params.loc[i,'tolscore_mean']
    tolscore_std = df_params.loc[i,'tolscore_std']

    dat_test_binned = apply_bin_test(dat_test, model_spec,  pl_best_bin)
    dat_test_binned['TotalScore'] = (dat_test_binned[model_spec]*model_weights).sum(axis=1)
    temp_sd = SomersD(dat_test_binned[target_logitPD], dat_test_binned['TotalScore'])
    pl_prior_sd_totalscore.append(temp_sd)

    # Match Rate and SomersD(with rating) before calibration optimization
    Intercept = df_params.loc[i,'params'][0]
    slope =     df_params.loc[i,'params'][1]
    dat_test_binned['TotalScore']= 50*(dat_test_binned.TotalScore-tolscore_mean)/tolscore_std
    dat_test_binned['fitted_logit_pd'] = Intercept + slope * dat_test_binned['TotalScore']
    dat_test_binned['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat_test_binned['fitted_logit_pd'] ]
    Ratings = []
    for i, row in dat_test_binned.iterrows():
        Ratings.append(sum(low_pd<=(row.fitted_pd)))
    dat_test_binned['fitted_PDRR'] = Ratings   

    temp_sd = SomersD(dat_test_binned[target], dat_test_binned['fitted_PDRR'])
    pl_poster_sd_rating.append(temp_sd)
    pl_poster_match.append(len(dat_test_binned.query('{}==fitted_PDRR'.format(target))) / len(dat_test_binned))




test_result = df_params.copy()
test_result['test_sd_prior'] = pl_prior_sd_totalscore
test_result['test_sd_post_rating']= pl_poster_sd_rating
test_result['test_post_match']= pl_poster_match

test_result.to_pickle('test_result.pkl')
test_result = pd.read_pickle('test_result.pkl')


test_result_filtered = test_result.query('test_sd_prior < prior_sd_totalscore')
test_result_filtered = test_result_filtered.query('test_sd_post_rating < poster_sd_rating')
test_result_filtered = test_result_filtered.query('test_post_match < poster_match')




#%%
best_model = ['size@Retained Earnings',
  'size@Current Liabilities',
  'bs@SD_to_Capt',
  'prof@TangA_to_NS',
  'ds@DSCR']


i=906
print(best_model == test_result.loc[i,'model'])
pl_best_bin = load_bin(best_model)
model_weights = test_result.loc[i,'weights']
tolscore_mean = test_result.loc[i,'tolscore_mean']
tolscore_std = test_result.loc[i,'tolscore_std']


dat_test_binned = apply_bin_test(dat_test, best_model,  pl_best_bin)
dat_test_binned['TotalScore'] = (dat_test_binned[best_model]*model_weights).sum(axis=1)
SomersD(dat_test_binned[target_logitPD], dat_test_binned['TotalScore'])
# 0.7066666666666667
# Match Rate and SomersD(with rating) before calibration optimization
Intercept = test_result.loc[i,'params'][0]
slope =     test_result.loc[i,'params'][1]
low_pd = model.MS['new_low']
dat_test_binned['TotalScore']= 50*(dat_test_binned.TotalScore-tolscore_mean)/tolscore_std
dat_test_binned['fitted_logit_pd'] = Intercept + slope * dat_test_binned['TotalScore']
dat_test_binned['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat_test_binned['fitted_logit_pd'] ]
Ratings = []
for i, row in dat_test_binned.iterrows():
    Ratings.append(sum(low_pd<=(row.fitted_pd)))
dat_test_binned['fitted_PDRR'] = Ratings   

SomersD(dat_test_binned[target], dat_test_binned['fitted_PDRR'])
# 0.575
len(dat_test_binned.query('{}==fitted_PDRR'.format(target))) / len(dat_test_binned)
# 0.7333333333333333

#%%s
f, ax = plt.subplots(figsize=(10, 11))
sns.heatmap(test_result.corr(), linewidths=.3, cmap='Blues', ax=ax)

aa = dat_test_binned[['fitted_PDRR', target]]


#%%
dat1 = dat_test_binned[['CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'NAICS_Cd',
 'Underwriter_Guideline',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Override_Action',
 'RLA_Notches',
 'PD_frPDRR',
 'logitPD_frPDRR',
 'TotalScore',]]
dat1['model'] = 'Binning'

dat2 = pd.read_pickle('LC_norm_test.pkl')[['CUSTOMERID',
 'Customer Long Name',
 'timestamp',
 'NAICS_Cd',
 'Underwriter_Guideline',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Override_Action',
 'RLA_Notches',
 'PD_frPDRR',
 'logitPD_frPDRR',
 'Totalscore']]
dat2['model'] = 'LC'
dat2.rename(columns={'Totalscore':'TotalScore'}, inplace=True)
dat_plot = pd.concat([dat1, dat2])


#%% original score
g = sns.FacetGrid(dat_plot, col="model",margin_titles=True, height=4)
g.map(plt.scatter, "TotalScore", "logitPD_frPDRR", color="#338844", edgecolor="white", s=50, lw=1)
x1 =-150; x2 = 120
y11=Intercept + slope*(x1)
y21=Intercept + slope*(x2)
y12=model.intercept1 + model.slope1*(x1)
y22=model.intercept1 + model.slope1*(x2)
for i,ax in enumerate(g.axes.flat):
    if i==0:
        ax.plo
        t((x1, x2), (y11, y21), c=".2", ls="--")
    else:
        ax.plot((x1, x2), (y12, y22), c=".2", ls="--")
g.set(xlim=(-200, 150), ylim=(-9, -6))



#%% scaled LC score
dat1_std = dat1['TotalScore'].std()
dat2_std = dat2['TotalScore'].std()
dat2['TotalScore'] = dat2['TotalScore']*dat1_std/dat2_std
dat1_mean = dat1['TotalScore'].mean()
dat2_mean = dat2['TotalScore'].mean()
dat2['TotalScore'] = dat2['TotalScore'] - (dat2_mean - dat1_mean)
dat_plot2 = pd.concat([dat1, dat2])

g = sns.FacetGrid(dat_plot2, col="model", margin_titles=True, height=4)
g.map(plt.scatter, "TotalScore", "logitPD_frPDRR", color="#338844", edgecolor="white", s=50, lw=1)
x1_scaled = x1*dat1_std/dat2_std-(dat2_mean - dat1_mean)
x2_scaled = x2*dat1_std/dat2_std-(dat2_mean - dat1_mean)
for i,ax in enumerate(g.axes.flat):
    if i==0:
        ax.plot((x1, x2), (y11, y21), c=".2", ls="--")
    else:
        ax.plot((x1_scaled, x2_scaled), (y12, y22), c=".2", ls="--")
g.set(xlim=(-150, 100), ylim=(-9, -6))


#%% refit scaled LC score
bounds = [(-10,0), (0, 0.2)]
dat = dat2.copy()
res = differential_evolution(_calib, bounds)
print(res.x)
print(calib_sd(res.x))
print(-res.fun)

g = sns.FacetGrid(dat_plot2, col="model", margin_titles=True, height=4)
g.map(plt.scatter, "TotalScore", "logitPD_frPDRR", color="#338844", edgecolor="white", s=50, lw=1)
y12=res.x[0] + res.x[1]*(x1)
y22=res.x[0] + res.x[1]*(x2)
for i,ax in enumerate(g.axes.flat):
    if i==0:
        ax.plot((x1, x2), (y11, y21), c=".2", ls="--")
    else:
        ax.plot((x1, x2), (y12, y22), c=".2", ls="--")
g.set(xlim=(-150, 100), ylim=(-9, -6))



import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from scipy.optimize import differential_evolution
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]


#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = data.query('Final_PD_Risk_Rating<=4')
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
#dat = data.copy()
dat = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')



target = 'Final_PD_Risk_Rating'  # setting
target_PD = 'PD_frPDRR'  # setting
target_logitPD = 'logitPD_frPDRR'  # setting
sd_col_name = 'newms_Final_PDRR'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

pl_candidates = list(dat)[21:220]

#%% binning
def apply_bin(w):
    try:
        dat['bin'] = pd.qcut(dat[factor],  [0, w[0], w[1], 1.] ,labels=['1','2','3']) 
        temp = dat.groupby(by=['bin'])[target_PD].mean()
        dat[factor] = dat['bin'].replace(temp.to_dict())
    except ValueError:
        dat[factor] = 0



def sd_bin(w):
    if w[0]>w[1]:
        w[0], w[1] = w[1], w[0]
    try:
        dat['bin'] = pd.qcut(dat[factor],  [0, w[0], w[1], 1.] ,labels=['1','2','3'])  
    except ValueError:
        return(0)
    temp = dat.groupby(by=['bin'])[target_PD].mean()
    dat['bin2'] = dat['bin'].replace(temp.to_dict())

    return(-np.abs(SomersD(dat[target], dat['bin2'])))


bounds = [(0,1), (0, 1)]
for i,factor in enumerate(pl_candidates):
    res = differential_evolution(sd_bin, bounds)
    print('factor #{} is binned'.format(i))
    apply_bin(res.x)



#%% SFA
pl_sd = []
for factor in pl_candidates:
    df = dat[[factor,target]].copy()
    df.dropna(how='any', inplace=True)
    pl_sd.append(np.abs(SomersD(df[target], df[factor])))


df_somersd = pd.DataFrame()
df_somersd['SD'] = pl_sd
df_somersd.index = pl_candidates
df_somersd.sort_values(by=['SD'], inplace=True, ascending=False)

pl_top_candidates=list(df_somersd.index)[:top]


sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

np.sign(sfa)

  
#%% correlation cluster
# initial 
f, ax = plt.subplots(figsize=(20, 12))
sns.heatmap(dat[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(dat, pl_top_candidates)
#plot_cluster_corr(dat, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]]
        ))

    for facs in py_list:
        names = list(facs)
        x_train = sm.add_constant(dat[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(dat[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(dat[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\H_model_good_nodup_3_bin.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%% model spec
model_spec=['size@Current Assets', 'bs@AdjTD_to_Capt', 'prof@UBEBITDA_to_TangA']



x_train = sm.add_constant(dat[model_spec], prepend = True)
linear = sm.OLS(dat[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
result.summary()


dat['TotalScore'] = (dat[model_spec]*weights).sum(axis=1)
SomersD(dat[target_logitPD], dat['TotalScore'])
# 0.46956829440905873

aa=dat.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= dat)


#%% test core data

dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = dat_test.query('Final_PD_Risk_Rating<=4')

for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
dat_test = cni_test.normdata.copy()

dat_test['TotalScore'] = (dat_test[model_spec]*weights).sum(axis=1)
SomersD(dat_test[target_logitPD], dat_test['TotalScore'])
# 0.44333333333333336

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]


#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = data.query('Final_PD_Risk_Rating<=4')
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
dat = data.copy()
#dat = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')


target = 'Final_beforeRLA'  # setting
target_PD = 'PD_frPDRR_bfRLA'  # setting
target_logitPD = 'logitPD_frPDRR_bfRLA'  # setting
sd_col_name = 'newms_Final_bfRLA'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

pl_candidates = list(dat)[21:220]
pl_sd = []
for factor in pl_candidates:
    df = dat[[factor,target]].copy()
    df.dropna(how='any', inplace=True)
    df[factor] = df[factor].clip(np.nanmin(df[factor][df[factor] != -np.inf]), np.nanmax(df[factor][df[factor] != np.inf]))
    pl_sd.append(np.abs(SomersD(df[target], df[factor])))


df_somersd = pd.DataFrame()
df_somersd['SD'] = pl_sd
df_somersd.index = pl_candidates
df_somersd.sort_values(by=['SD'], inplace=True, ascending=False)

pl_top_candidates=list(df_somersd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)+model.quali_factor
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(6+num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\I_model_good.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%% model spec
model_spec=['size@Current Assets',
 'size@Net Accounts Receivable',
 'cf@FOCF_to_TL',
 'liq@ECE_to_TL',
 'cf@AdjTD_to_EBIT_exc_Div_exc_Taxes',
 'Strength_SOR_Prevent_Default',
 #'Level_Waiver_Covenant_Mod',
 #'Management_Quality',
 'Vulnerability_To_Changes', 
 'Access_Outside_Capital',
 #'Market_Outlook_Of_Borrower'
 ]

x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
result.summary()


df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.598279107286905

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)


#%% test data

dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = dat_test.query('Final_PD_Risk_Rating<=4')


for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.5658307210031348
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]


#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = data.query('Final_PD_Risk_Rating<=4')
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
#dat = data.copy()
dat = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')


target = 'Final_beforeRLA'  # setting
target_PD = 'PD_frPDRR_bfRLA'  # setting
target_logitPD = 'logitPD_frPDRR_bfRLA'  # setting
sd_col_name = 'newms_Final_bfRLA'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting

pl_candidates = list(dat)[21:220]
pl_sd = []
for factor in pl_candidates:
    df = dat[[factor,target]].copy()
    df.dropna(how='any', inplace=True)
    df[factor] = df[factor].clip(np.nanmin(df[factor][df[factor] != -np.inf]), np.nanmax(df[factor][df[factor] != np.inf]))
    pl_sd.append(np.abs(SomersD(df[target], df[factor])))


df_somersd = pd.DataFrame()
df_somersd['SD'] = pl_sd
df_somersd.index = pl_candidates
df_somersd.sort_values(by=['SD'], inplace=True, ascending=False)

pl_top_candidates=list(df_somersd.index)[:top]


#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% correlation cluster
# initial 
#f, ax = plt.subplots(figsize=(20, 12))
#sns.heatmap(df_norm[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(df_norm, pl_top_candidates)
#plot_cluster_corr(df_norm, cat)

print('The number of categories is {}'.format(len(cat)))

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>5:
        pl_cat.append(pl_cand[:5])
        pl_candidates+=pl_cand[:5]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand




#%% subset search
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))
    for facs in py_list:       
        N_iter+=1


start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    exec('py_list = product({},{},{},{},{})'.format(pl_cat[cats[0]], 
        pl_cat[cats[1]], pl_cat[cats[2]], pl_cat[cats[3]], pl_cat[cats[4]]
        ))

    for facs in py_list:
        names = list(facs)
        x_train = sm.add_constant(df_norm[names], prepend = True)
        #x_test = sm.add_constant(normdat_test[names], prepend = True)
        linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
        result = linear.fit(disp=0)
        pl_pvals.append(result.pvalues.max())

        if (np.sign(result.params[1:]).sum()==(num_of_params)):
            pl_sign.append('correct')
        else:
            pl_sign.append('wrong')
        pl_models.append(names)
        pl_R2.append(result.rsquared)
        pl_SD_in.append(SomersD(df_norm[target_logitPD], result.fittedvalues))
        
        count+=1
        if count % epoch ==0:
            print(r'{} % calculation is finished'.format(count/epoch))
            lefttime = (time.time() - start_time)/(count/epoch/100) - (time.time() - start_time)
            print(r'Estimated remaining time:{} seconds'.format(lefttime))

models_5fac = pd.DataFrame()
models_5fac['models'] = pl_models
models_5fac['R2'] = pl_R2
models_5fac['SD_insample'] = pl_SD_in
#models_5fac['SD_outsample'] = pl_SD_out
models_5fac['max_pvalue'] = pl_pvals
models_5fac['sign'] = pl_sign
models_5fac.to_excel(r'MFA\I_model_good_nodup.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%% model spec
model_spec=['size@Current Assets', 'cf@AdjTD_to_EBITDA', 'liq@ECE_to_CA']


x_train = sm.add_constant(df_norm[model_spec], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
result.summary()


df_norm['TotalScore'] = (df_norm[model_spec]*weights).sum(axis=1)
SomersD(df_norm[target_logitPD], df_norm['TotalScore'])
# 0.5533980582524272

aa=df_norm.groupby(by=target)['TotalScore'].mean()
sns.regplot(x='TotalScore',y=target, data= df_norm)


#%% test data

dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = dat_test.query('Final_PD_Risk_Rating<=4')


for factor in pl_top_candidates:                       
        dat_test[factor] = dat_test[factor].clip(
            np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]),
            np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
for factor in pl_dollar:                       
        dat_test[factor] = dat_test[factor].clip(1, np.inf)
        dat_test[factor] = np.log(dat_test[factor])

cni_test = MFA(dat_test, model, quant_only=False)
df_norm_test = cni_test.normdata.copy()

df_norm_test['TotalScore'] = (df_norm_test[model_spec]*weights).sum(axis=1)
SomersD(df_norm_test[target_logitPD], df_norm_test['TotalScore'])
# 0.5924764890282131


# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 11:09:42 2020

@author: ub71894
"""

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from PDScorecardTool.Process import SomersD, MAUG_mapping, getPDRR
from PDScorecardTool.MFA import MFA
import time
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
from list_maug import list_maug
filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb')
model_LC = pickle.load(filehandler)

model_LC.quali_factor = [
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital']


def _RLA(data):
    N = len(data)
    n_RLA = len(data.query('RLA_Notches!=0'))    
    return (n_RLA/N)

def _OVD(data):
    N = len(data)   
    n_Override = len(data.query('Override_Action!=0'))
    return (n_Override/N)


#%%  pre_2019 data
data1 = pd.read_pickle(r'data\dat_2010_train.pkl') 
data2 = pd.read_pickle(r'data\dat_2010_test.pkl')
data = pd.concat([data1, data2], axis=0)

data = MAUG_mapping(data)
data.dropna(subset=['Industry_by_MAUG'], inplace=True)
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
data = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')
data['size@Total Assets'] = np.log(1+data['size@Total Assets'])
# fill inf
for factor in model_LC.quant_factor:                       
        data[factor] = data[factor].clip(np.nanmin(data[factor][data[factor] != -np.inf]), np.nanmax(data[factor][data[factor] != np.inf]))
data_pre2019 = getPDRR(data, model_LC, ms_ver='new')
data_pre2019['Sample'] = data_pre2019['Industry_by_MAUG'].copy()
data_pre2019['Sample'].replace(pd_core, inplace=True)
data_pre2019['Sample'].replace(pd_noncore, inplace=True)
data_pre2019['Qualitative_Score'] = data_pre2019['qualiscore']
data_pre2019['Quantitative_Score'] = data_pre2019['quantscore']
data_pre2019['Total_Score'] = data_pre2019['score']
data_pre2019['archive_date'] = data_pre2019['timestamp']
data_pre2019['Customer_Name'] = data_pre2019['Customer Long Name']

data_pre2019 = data_pre2019[[
'CUSTOMERID',
'archive_date',
'Customer_Name',
'Total_Score', 
'Qualitative_Score', 
'Quantitative_Score', 
'Final_PD_Risk_Rating',
'Industry_by_MAUG',
'Sample',
'Override_Action',
'RLA_Notches',
]]


#%% 2019 data
data_2019 = pd.read_excel(r'C:\Users\ub71894\Documents\Projects\CNI\newdata\2019_RA_OCCI_SINCE_PROD.xlsx')
data_2019 = data_2019.query('sc_segment=="C&I Large Corporate" or sc_segment=="1"')
data_2019.dropna(subset=['Underwriter_Guideline'], inplace=True)
data_2019.drop_duplicates(subset=['CUSTOMERID'], inplace=True)
data_2019.reset_index(drop=True, inplace=True )
data_2019 = MAUG_mapping(data_2019)
data_2019['Sample'] = data_2019['Industry_by_MAUG'].copy()
data_2019['Sample'].replace(pd_core, inplace=True)
data_2019['Sample'].replace(pd_noncore, inplace=True)

######### no mapping for MAUG 172 and MAUG 373, mapping them to non-core
data_2019['Sample'] = ['Non-Core' if x!='Core' else 'Core' for x in data_2019['Sample'].tolist() ]

data_2019 = data_2019[[
'CUSTOMERID',
'archive_date',
'Customer_Name',
'Total_Score', 
'Qualitative_Score', 
'Quantitative_Score', 
'Final_PD_Risk_Rating',
'Industry_by_MAUG',
'Sample',
'Override_Action',
'RLA_Notches',
]]


data_concat = pd.concat([data_pre2019, data_2019], axis=0)
data_concat['RLA_Notches'].fillna(0, inplace=True)
data_concat['Override_Action'].fillna(0, inplace=True)
data_concat['RLA'] = ['Yes' if x!=0 else 'No' for x in data_concat['RLA_Notches']]
data_concat['Override'] = ['Yes' if x!=0 else 'No' for x in data_concat['Override_Action']]

sns.relplot(x='Total_Score', y='Final_PD_Risk_Rating', data= data_concat,hue="Sample",)


#%% involving statistics
list_cols = ['Total_Score', 'Qualitative_Score', 'Quantitative_Score']
list_inds = list(data_concat['Industry_by_MAUG'].unique())


df_drawback = pd.DataFrame()

for field in list_cols:
    sd_withall = SomersD(data_concat['Final_PD_Risk_Rating'], data_concat[field])
    pl_drawback=[]
    pl_drawback_ave=[]
    for ind in list_inds:
        dat = data_concat.query(f'Industry_by_MAUG!="{ind}"')
        temp_sd = SomersD(dat['Final_PD_Risk_Rating'], dat[field])

        drawback = sd_withall - temp_sd
        drawback_ave = drawback/(len(data_concat)-len(dat))
        pl_drawback.append(drawback)
        pl_drawback_ave.append(drawback_ave)
    df_drawback[field] = pl_drawback
    df_drawback[field+'_ave'] = pl_drawback_ave

df_drawback.index = list_inds
df_drawback['counts'] = data_concat['Industry_by_MAUG'].value_counts()
df_drawback['SDImpact'] = ['Worse' if x>=0 else 'Better' for x in df_drawback['Total_Score']]
df_drawback['sample'] = list_inds
df_drawback['sample'].replace(pd_core, inplace=True)
df_drawback['sample'].replace(pd_noncore, inplace=True)
df_drawback['sample'] = ['Non-Core' if x!='Core' else 'Core' for x in df_drawback['sample'].tolist() ]


ax = sns.scatterplot(x="Quantitative_Score_ave", y="Qualitative_Score_ave",hue="SDImpact", size = "counts",
    style="sample", data=df_drawback)


aa = pd.concat([data_concat.groupby('Industry_by_MAUG').apply(_RLA), data_concat.groupby('Industry_by_MAUG').apply(_OVD)], axis=1)
aa.columns = ['RLA_Rate','Override_Rate']
table = pd.concat([df_drawback, aa], axis=1)
table.to_excel(r'src\LC_table.xlsx')# -*- coding: utf-8 -*-
"""
Created on Fri Jan 17 14:34:34 2020

@author: ub71894
"""
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from PDScorecardTool.Process import SomersD, MAUG_mapping, getPDRR
from PDScorecardTool.MFA import MFA
import time
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
from list_maug import list_maug
filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb')
model_LC = pickle.load(filehandler)

model_LC.quali_factor = [
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital']
#%%
data1 = pd.read_pickle(r'data\dat_2010_train.pkl') 
data2 = pd.read_pickle(r'data\dat_2010_test.pkl')

data = pd.concat([data1, data2], axis=0)


data = MAUG_mapping(data)
data.dropna(subset=['Industry_by_MAUG'], inplace=True)
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
data = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')

data['size@Total Assets'] = np.log(1+data['size@Total Assets'])
# fill inf
for factor in model_LC.quant_factor:                       
        data[factor] = data[factor].clip(np.nanmin(data[factor][data[factor] != -np.inf]), np.nanmax(data[factor][data[factor] != np.inf]))


data_getPDRR = getPDRR(data, model_LC, ms_ver='new')
data_getPDRR['Sample'] = data_getPDRR['Industry_by_MAUG'].copy()
data_getPDRR['Sample'].replace(pd_core, inplace=True)
data_getPDRR['Sample'].replace(pd_noncore, inplace=True)
data_getPDRR['Totalscore'] = data_getPDRR['score']
data_getPDRR['RLA'] = ['Yes' if x!=0 else 'No' for x in data_getPDRR[ 'RLA_Notches']]


sns.relplot(x='Totalscore', y='Final_PD_Risk_Rating', data= data_getPDRR,hue="Sample",)


#%% involving statistics
list_cols = model_LC.quant_factor + \
            model_LC.quali_factor + \
            ['quantscore', 'qualiscore','Ratings']

list_inds = list(data_getPDRR['Industry_by_MAUG'].unique())


df_drawback = pd.DataFrame()

for field in list_cols:
    sd_withall = SomersD(data_getPDRR['Final_PD_Risk_Rating'], data_getPDRR[field])
    pl_drawback=[]
    pl_drawback_ave=[]
    for ind in list_inds:
        dat = data_getPDRR.query(f'Industry_by_MAUG!="{ind}"')
        temp_sd = SomersD(dat['Final_PD_Risk_Rating'], dat[field])

        drawback = sd_withall - temp_sd
        drawback_ave = drawback/(len(data_getPDRR)-len(dat))
        pl_drawback.append(drawback)
        pl_drawback_ave.append(drawback_ave)
    df_drawback[field] = pl_drawback
    df_drawback[field+'_ave'] = pl_drawback_ave

df_drawback.index = list_inds
df_drawback['counts'] = data_getPDRR['Industry_by_MAUG'].value_counts()
df_drawback['SDImpact'] = ['Worse' if x>=0 else 'Better' for x in df_drawback['Ratings']]
df_drawback['sample'] = list_inds
df_drawback['sample'].replace(pd_core, inplace=True)
df_drawback['sample'].replace(pd_noncore, inplace=True)

ax = sns.scatterplot(x="quantscore_ave", y="qualiscore_ave",hue="SDImpact", size = "counts",
    style="sample", data=df_drawback)# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 14:23:50 2019

@author: ub71894
"""


import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, getPDRR
from PDScorecardTool.Process import quanttrans,qualitrans, normalization, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)
model.quali_factor = [
'Strength_SOR_Prevent_Default',
'Level_Waiver_Covenant_Mod',
'Management_Quality',
'Vulnerability_To_Changes',
'Access_Outside_Capital']

#dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
#dat_test = dat_test.query('Final_PD_Risk_Rating<=4')
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = data.query('Final_PD_Risk_Rating<=4')
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
#dat = data.copy()
dat_test = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')

#%%
dat_test.dropna(subset=model.quali_factor, how='any', inplace=True)
dat_test.reset_index(drop=True, inplace=True)
# log trans
dat_test['size@Total Assets'] = np.log(1+dat_test['size@Total Assets'])
# fill inf
for factor in model.quant_factor:                       
        dat_test[factor] = dat_test[factor].clip(np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]), np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))
# get existing model's Final PDRR implied PD and logit PD
dat_test = PD_frPDRR(dat_test, model, 'Final_PD_Risk_Rating', ms_ver='new')
dat_test = logitPD_frPDRR(dat_test, model, 'Final_PD_Risk_Rating', ms_ver='new')



cni_test_2017 = MFA(dat_test, model, quant_only=False)
cni_test_2017.modelAR(quant_weight=model.quant_weight, quali_weight=model.quali_weight, quantweight=0.55, \
    isthere_def=False, dependentvar='logitPD_frPDRR', use_msms=True)

norm_test_2017 = cni_test_2017.normdata.copy()

#%%

norm_test_2017['quantscore'] = (model.quant_weight * norm_test_2017[model.quant_factor].values).sum(axis=1)
norm_test_2017['quantscore'] = 50*( norm_test_2017['quantscore'] - model.quantmean) / model.quantstd
norm_test_2017['qualiscore'] = (model.quali_weight * norm_test_2017[model.quali_factor].values).sum(axis=1)
norm_test_2017['qualiscore'] = 50*( norm_test_2017['qualiscore'] - model.qualimean) / model.qualistd
norm_test_2017['Totalscore'] = norm_test_2017['quantscore']*model.quantweight + norm_test_2017['qualiscore'] *model.qualiweight



print(SomersD(norm_test_2017.Final_PD_Risk_Rating, norm_test_2017.Totalscore))


temp_df = getPDRR(dat_test, model, ms_ver='new')
SomersD(temp_df.Final_PD_Risk_Rating, temp_df.score)

SomersD(temp_df.Final_PD_Risk_Rating, temp_df.Ratings)

len(temp_df.query('Final_PD_Risk_Rating==Ratings')) / len(temp_df)


norm_test_2017['Final_beforeRLA'] = norm_test_2017['Final_PD_Risk_Rating'] - norm_test_2017['RLA_Notches']
print(SomersD(norm_test_2017.Final_beforeRLA, norm_test_2017.Totalscore))




#%%  2019/09/03 for doc 
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, getPDRR
import pickle
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats

filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb')
model = pickle.load(filehandler)
model.quali_factor = [
'Strength_SOR_Prevent_Default',
'Level_Waiver_Covenant_Mod',
'Management_Quality',
'Vulnerability_To_Changes',
'Access_Outside_Capital']



data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = data.query('Final_PD_Risk_Rating<=4')
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
dat = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')
dat['size@Total Assets'] = np.log(1+dat['size@Total Assets'])

dat_test  = pd.read_pickle(r'data\dat_newms_test.pkl')
dat_test = dat_test.query('Final_PD_Risk_Rating<=4')
dat_test.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
# dat_test = dat_test.drop_duplicates(subset=['CUSTOMERID'], keep='last')
dat_test['size@Total Assets'] = np.log(1+dat_test['size@Total Assets'])


#%% LC 
for factor in model.quant_factor:                       
        dat[factor] = dat[factor].clip(np.nanmin(dat[factor][dat[factor] != -np.inf]), np.nanmax(dat[factor][dat[factor] != np.inf]))
        dat_test[factor] = dat_test[factor].clip(np.nanmin(dat_test[factor][dat_test[factor] != -np.inf]), np.nanmax(dat_test[factor][dat_test[factor] != np.inf]))


dat_PDRR = getPDRR(dat, model, ms_ver='new')
SomersD(dat_PDRR.Final_PD_Risk_Rating, dat_PDRR.Ratings)
#0.3331564048124558
CreateBenchmarkMatrix(dat_PDRR, 'LC_newms.xlsx', 'Final', 'Ratings', 'Final_PD_Risk_Rating', PDRR=range(1,16))


dat_test_PDRR = getPDRR(dat_test, model, ms_ver='new')
SomersD(dat_test_PDRR.Final_PD_Risk_Rating, dat_test_PDRR.Ratings)
# 0.39166666666666666
CreateBenchmarkMatrix(dat_test_PDRR, 'LC_newms_test.xlsx', 'Final',  'Ratings', 'Final_PD_Risk_Rating', PDRR=range(1,16))







#%% binning
import statsmodels.api as sm
def apply_bin(w):
    if w[0]>w[1]:
        w[0], w[1] = w[1], w[0]
    try:
        dat['bin'] = pd.qcut(dat[factor],  [0, w[0], w[1], 1.] ,labels=['1','2','3']) 
        temp = dat.groupby(by=['bin'])[target_PD].mean()
        dat[factor] = dat['bin'].replace(temp.to_dict())
    except ValueError:
        dat[factor] = 0


def _sd_bin(w):
    if w[0]>w[1]:
        w[0], w[1] = w[1], w[0]
    try:
        dat['bin'] = pd.qcut(dat[factor],  [0, w[0], w[1], 1.] ,labels=['1','2','3'])  
    except ValueError:
        return(0)
    temp = dat.groupby(by=['bin'])[target_PD].mean()
    dat['bin2'] = dat['bin'].replace(temp.to_dict())

    return(-np.abs(SomersD(dat[target], dat['bin2'])))


def apply_bin_test(data, pl_factors,  pl_bins):
    dat = data.copy()
    for i, factor in enumerate(pl_factors):
        try:
            dat['bin'] = pd.qcut(dat[factor],  [0, pl_bins[i][0], pl_bins[i][1], 1.] ,labels=['1','2','3']) 
            temp = dat.groupby(by=['bin'])[target_PD].mean()
            dat[factor] = dat['bin'].replace(temp.to_dict())
        except ValueError:
            dat[factor] = 0
    return (dat)

def load_bin(pl_factors):
    pl_bins = list()
    for factor in pl_factors:
        exec('pl_bins.append('+df_somersd.loc[factor, 'best_bin']+')')
    return (pl_bins)


def _calib(alpha):
    low_pd = model.MS['new_low']
    Intercept = alpha[0]
    slope =     alpha[1]
    dat['fitted_logit_pd'] = Intercept + slope * dat['TotalScore']
    dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat['fitted_logit_pd'] ]
    Ratings = []
    for i, row in dat.iterrows():
        Ratings.append(sum(low_pd<=(row.fitted_pd)))
    dat['fitted_PDRR'] = Ratings   

    return (-len(dat.query('{}==fitted_PDRR'.format(target))) / len(dat))


def calib_sd(alpha):
    low_pd = model.MS['new_low']
    Intercept = alpha[0]
    slope =     alpha[1]
    dat['fitted_logit_pd'] = Intercept + slope * dat['TotalScore']
    dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat['fitted_logit_pd'] ]
    Ratings = []
    for i, row in dat.iterrows():
        Ratings.append(sum(low_pd<=(row.fitted_pd)))
    dat['fitted_PDRR'] = Ratings   

    return (SomersD(dat[target], dat['fitted_PDRR']))




target = 'Final_PD_Risk_Rating'  # setting
target_PD = 'PD_frPDRR'  # setting
target_logitPD = 'logitPD_frPDRR'  # setting
sd_col_name = 'newms_Final_PDRR'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting



df_somersd = pd.read_excel(r'SFA\SFA_best_bin_0730.xlsx')
df_somersd.index = df_somersd.Factor
dat = pd.read_pickle('binned_data.pkl')
dat_test  = pd.read_pickle(r'data\dat_2015_test.pkl')
dat_test = dat_test.query('Final_PD_Risk_Rating<=4')
df_params = pd.read_pickle('opt_calib_for_top2000_MFA.pkl')
low_pd = model.MS['new_low']

best=906
best_model = ['size@Retained Earnings',
  'size@Current Liabilities',
  'bs@SD_to_Capt',
  'prof@TangA_to_NS',
  'ds@DSCR']
Intercept = df_params.loc[best,'params'][0]
slope =     df_params.loc[best,'params'][1]



x_train = sm.add_constant(dat[best_model], prepend = True)
linear = sm.OLS(dat[target_logitPD], x_train, missing='drop')
result = linear.fit(disp=0)
stats = result.params[1:] / result.params[1:].sum()
weights = stats.values
dat['TotalScore'] = (dat[best_model]*weights).sum(axis=1)



dat['TotalScore']= 50*(dat.TotalScore-dat.TotalScore.mean())/dat.TotalScore.std()
dat['fitted_logit_pd'] = Intercept + slope * dat['TotalScore']
dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat['fitted_logit_pd'] ]
Ratings = []
for i, row in dat.iterrows():
    Ratings.append(sum(low_pd<=(row.fitted_pd)))
dat['fitted_PDRR'] = Ratings   

SomersD(dat[target], dat['fitted_PDRR'])
# 0.6217268223637651
CreateBenchmarkMatrix(dat, 'Binning_newms.xlsx', 'Final',  'fitted_PDRR', 'Final_PD_Risk_Rating', PDRR=range(1,16))







# test sample
model_spec = df_params.loc[best,'model']
pl_best_bin = load_bin(model_spec)
model_weights = df_params.loc[best,'weights']
tolscore_mean = df_params.loc[best,'tolscore_mean']
tolscore_std = df_params.loc[best,'tolscore_std']

dat_test_binned = apply_bin_test(dat_test, model_spec,  pl_best_bin)
dat_test_binned['TotalScore'] = (dat_test_binned[model_spec]*model_weights).sum(axis=1)
dat_test_binned['TotalScore']= 50*(dat_test_binned.TotalScore-tolscore_mean)/tolscore_std
dat_test_binned['fitted_logit_pd'] = Intercept + slope * dat_test_binned['TotalScore']
dat_test_binned['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat_test_binned['fitted_logit_pd'] ]
Ratings = []
for i, row in dat_test_binned.iterrows():
    Ratings.append(sum(low_pd<=(row.fitted_pd)))
dat_test_binned['fitted_PDRR'] = Ratings   

SomersD(dat_test_binned[target], dat_test_binned['fitted_PDRR'])
CreateBenchmarkMatrix(dat_test_binned, 'Binning_newms_test.xlsx', 'Final',  'fitted_PDRR', 'Final_PD_Risk_Rating', PDRR=range(1,16))

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 15:46:33 2019

@author: ub71894
"""


import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]


#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = data.query('Final_PD_Risk_Rating<=4')
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
dat = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')



target = 'Final_beforeRLA'  # setting
target_PD = 'PD_frPDRR_bfRLA'  # setting
target_logitPD = 'logitPD_frPDRR_bfRLA'  # setting
sd_col_name = 'newms_Final_bfRLA'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting


mfa_result = pd.read_excel(r'MFA\I_model_good_nodup_3.xlsx')
mfa_result = mfa_result.query('sign=="correct"')
mfa_result.sort_values(by=['SD_insample'], ascending=False, inplace=True)
mfa_result.reset_index(drop=True, inplace=True)

# collect quant factors from top 20 best models 
aa=mfa_result.head(20)
pl_top_candidates = []
for index, df in aa.iterrows():
    exec('pl_top_candidates +='+ df.models)
pl_top_candidates = list(set(pl_top_candidates))



#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% find outlier

# find outlier candidates
pl_outliers = []
for factor in pl_top_candidates:    
    x_train = sm.add_constant(df_norm[factor], prepend = True)
    linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
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
threshold = 8
pd_outliers=df_norm.where(freq_out>=threshold).dropna(how='all')

temp = pd_outliers[['Customer Long Name',
 'timestamp',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Override_Action',
 'RLA_Notches',]]





#%% plot example
factor=pl_top_candidates[10]
x_train = sm.add_constant(df_norm[factor], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
lm = linear.fit(disp=0)

fig = plt.figure()
ax = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
ax.scatter(df_norm[factor], df_norm[target_logitPD])
ax.plot(np.sort(df_norm[factor]), lm.predict()[np.argsort(df_norm[factor])],
    color='green',
    label="regression line")
ax.legend()
sm.graphics.influence_plot(lm, ax = ax2, criterion="cooks")
plt.show()
#%%

# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 15:46:33 2019

@author: ub71894
"""


import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, MAUG_mapping, getPDRR
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb')
model_LC = pickle.load(filehandler)

model_LC.quali_factor = [
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital']
#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = MAUG_mapping(data)
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
data = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')

data['size@Total Assets'] = np.log(1+data['size@Total Assets'])
# fill inf
for factor in model_LC.quant_factor:                       
        data[factor] = data[factor].clip(np.nanmin(data[factor][data[factor] != -np.inf]), np.nanmax(data[factor][data[factor] != np.inf]))


data_getPDRR = getPDRR(data, model_LC, ms_ver='new')
data_getPDRR['Sample'] = data_getPDRR['Industry_by_MAUG'].copy()
data_getPDRR['Sample'].replace(pd_core, inplace=True)
data_getPDRR['Sample'].replace(pd_noncore, inplace=True)
data_getPDRR['Totalscore'] = data_getPDRR['score']
data_getPDRR['RLA'] = ['Yes' if x!=0 else 'No' for x in data_getPDRR[ 'RLA_Notches']]


sns.relplot(x='Totalscore', y='Final_PD_Risk_Rating', data= data_getPDRR,hue="Sample",)


#%% involving statistics
list_cols = model_LC.quant_factor + \
            model_LC.quali_factor + \
            ['quantscore', 'qualiscore','Ratings']

list_inds = list(data_getPDRR['Industry_by_MAUG'].unique())


df_drawback = pd.DataFrame()

for field in list_cols:
    sd_withall = SomersD(data_getPDRR['Final_PD_Risk_Rating'], data_getPDRR[field])
    pl_drawback=[]
    pl_drawback_ave=[]
    for ind in list_inds:
        dat = data_getPDRR.query(f'Industry_by_MAUG!="{ind}"')
        temp_sd = SomersD(dat['Final_PD_Risk_Rating'], dat[field])

        drawback = sd_withall - temp_sd
        drawback_ave = drawback/(len(data_getPDRR)-len(dat))
        pl_drawback.append(drawback)
        pl_drawback_ave.append(drawback_ave)
    df_drawback[field] = pl_drawback
    df_drawback[field+'_ave'] = pl_drawback_ave

df_drawback.index = list_inds
df_drawback['counts'] = data_getPDRR['Industry_by_MAUG'].value_counts()
df_drawback['SDImpact'] = ['Worse' if x>=0 else 'Better' for x in df_drawback['Ratings']]
df_drawback['sample'] = list_inds
df_drawback['sample'].replace(pd_core, inplace=True)
df_drawback['sample'].replace(pd_noncore, inplace=True)

ax = sns.scatterplot(x="quantscore_ave", y="qualiscore_ave",hue="SDImpact", size = "counts",
    style="sample", data=df_drawback)# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 15:46:33 2019

@author: ub71894
"""


import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, quanttrans, qualitrans, MAUG_mapping, getPDRR
from PDScorecardTool.MFA import MFA
import statsmodels.api as sm
import time
from itertools import combinations, product
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
filehandler = open(r'C:\Users\{}\Documents\DevRepo\Files\model_LC.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

pl_qualifactors = ['Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
 'Market_Outlook_Of_Borrower',]


#%%
data = pd.read_pickle(r'data\dat_newms_train.pkl') # setting
data = data.query('Final_PD_Risk_Rating<=4')
data.sort_values(by=['CUSTOMERID', 'timestamp'], ascending=True, inplace=True)
dat = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')



target = 'Final_PD_Risk_Rating'  # setting
target_PD = 'PD_frPDRR'  # setting
target_logitPD = 'logitPD_frPDRR'  # setting
sd_col_name = 'newms_Final_PDRR'  # setting
top = 50   # setting
limit = 5 # limitation for each category
num_of_params = 5 # setting need to change line 144 if this setting has been changed
floor=0.05 # setting
cap=0.95 # setting


mfa_result = pd.read_excel(r'MFA\H_model_good_nodup_3.xlsx')
mfa_result = mfa_result.query('sign=="correct"')
mfa_result.sort_values(by=['SD_insample'], ascending=False, inplace=True)
mfa_result.reset_index(drop=True, inplace=True)

# collect quant factors from top 20 best models 
aa=mfa_result.head(20)
pl_top_candidates = []
for index, df in aa.iterrows():
    exec('pl_top_candidates +='+ df.models)
pl_top_candidates = list(set(pl_top_candidates))



#%% processing and normalization:

# replace inf -inf
for factor in pl_top_candidates:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_top_candidates: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])

# sort
pl_top_candidates = pl_dollar + pl_ratio
    
#%% auto invalid negtive
pl_invalid_neg = []
for factor in pl_ratio:
    df = dat[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()

    if floor_mean>cap_mean:
        if neg_mean>floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean < cap_mean:
            pl_invalid_neg.append(factor)
        elif floor_mean/neg_mean <  neg_mean/cap_mean:
            pl_invalid_neg.append(0)
        else:
            pl_invalid_neg.append(0)
    else:
        if neg_mean < floor_mean:
            pl_invalid_neg.append(0)
        elif neg_mean > cap_mean:
            pl_invalid_neg.append(factor)
        elif cap_mean/neg_mean <  neg_mean/floor_mean:
            pl_invalid_neg.append(factor)    
        else:
            pl_invalid_neg.append(0)



# prepare  not finish
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(dat[target], dat[factor]))

model.update({'quant_factor':pl_top_candidates})
model.update({'quali_factor':pl_qualifactors})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_top_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(dat, model, floor=floor, cap=cap)) # setting
model.update(qualitrans(dat, model, isthere_def=False, dependentvar=target_PD, output=True))


cni_train = MFA(dat, model, quant_only=False)
df_norm = cni_train.normdata.copy()


#%% find outlier

# find outlier candidates
pl_outliers = []
for factor in pl_top_candidates:    
    x_train = sm.add_constant(df_norm[factor], prepend = True)
    linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
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
threshold = 8
pd_outliers=df_norm.where(freq_out>=threshold).dropna(how='all')


temp = pd_outliers[['Customer Long Name',
 'timestamp',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Override_Action',
 'RLA_Notches',]]








#%% plot example
factor=pl_top_candidates[10]
x_train = sm.add_constant(df_norm[factor], prepend = True)
linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
lm = linear.fit(disp=0)

fig = plt.figure()
ax = fig.add_subplot(211)
ax2 = fig.add_subplot(212)
ax.scatter(df_norm[factor], df_norm[target_logitPD])
ax.plot(np.sort(df_norm[factor]), lm.predict()[np.argsort(df_norm[factor])],
    color='green',
    label="regression line")
ax.legend()
sm.graphics.influence_plot(lm, ax = ax2, criterion="cooks")
plt.show()



#%% on current LC model

filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb')
model_LC = pickle.load(filehandler)
model_LC.quali_factor = [
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital']

dat2 = data.drop_duplicates(subset=['CUSTOMERID'], keep='last')
dat2.reset_index(drop=True, inplace=True)
dat2['size@Total Assets'] = np.log(1+dat2['size@Total Assets'])
# fill inf
for factor in model.quant_factor:                       
        dat2[factor] = dat2[factor].clip(np.nanmin(dat2[factor][dat2[factor] != -np.inf]), np.nanmax(dat2[factor][dat2[factor] != np.inf]))


dat2_getPDRR = getPDRR(dat2, model_LC, ms_ver='new')
SomersD(dat2_getPDRR[target], dat2_getPDRR['quantscore'])
# in-sample SomersD : 0.1886058032554848


for factor in model_LC.quant_factor:
    print(factor+"'s SomersD is {}".format(SomersD(dat2_getPDRR[target], dat2_getPDRR[factor])))

'''
prof@UBEBITDA_to_NS's SomersD is -0.05042462845010616
cf@TD_to_UBEBITDA's SomersD is 0.043878273177636234
size@Total Assets's SomersD is 0.27335456475583864
bs@TD_to_Capt's SomersD is 0.15038924274593066
ds@UBEBITDA_to_IE's SomersD is 0.09465675866949752
'''


# find outlier candidates
pl_outliers = []
for factor in model_LC.quant_factor:    
    x_train = sm.add_constant(dat2_getPDRR[factor], prepend = True)
    linear = sm.OLS(dat2_getPDRR[target_logitPD], x_train, missing='drop')
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
pd_outliers=dat2_getPDRR.where(freq_out>=threshold).dropna(how='all')


df_outlier = pd_outliers[[
'CUSTOMERID',
'Customer Long Name',
 'timestamp',
 'Prelim_PD_Risk_Rating_Uncap',
 'Final_PD_Risk_Rating',
 'Override_Action',
 'RLA_Notches',
 'Ratings']]
df_outlier.to_excel('outliers_noncore.xlsx')
df_outlier['Sample'] = 'Non-Core'
newdf = pd.merge(dat2_getPDRR, df_outlier[['CUSTOMERID','Sample']], on=['CUSTOMERID'],how='left')
newdf['Sample'].fillna('Core', inplace=True)
newdf['Totalscore'] = newdf['score']
newdf['RLA'] = ['Yes' if x!=0 else 'No' for x in newdf[ 'RLA_Notches']]
sns.relplot(x='Totalscore', y='Final_PD_Risk_Rating', data= newdf,hue="Sample",)


# -*- coding: utf-8 -*-
"""
Created on Mon Aug  5 13:21:35 2019

@author: ub71894
"""

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from scipy import stats
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from scipy.optimize import differential_evolution
from sklearn.metrics import f1_score, roc_auc_score, precision_score, recall_score, precision_recall_curve
from inspect import signature


dat_dev = pd.read_pickle(r'C:\Users\ub71894\Documents\Projects\CNI\src\MFA\train_2016.pkl.xz')
dat_2010 = pd.read_pickle(r'data\dat_2010_train.pkl')
dat_2015 = pd.read_pickle(r'data\dat_2015_train.pkl')
dat_newms = pd.read_pickle(r'data\dat_newms_train.pkl')

pl_dataset = [dat_dev, dat_2010, dat_2015, dat_newms]
pl_name = ['dev', 'since2010', 'since2015', 'since_newms']

pl_factor=[]
pl_ks = []
pl_pv = []
pl_data = []

for i, dat in enumerate(pl_dataset):

    cols = list(dat.filter(like='@', axis=1))
    pl_factor += cols
    dat1 = dat.query( 'Final_PD_Risk_Rating<=4')
    dat2 = dat.query( 'Final_PD_Risk_Rating>=5')

    for name in cols:
        tmp_ks, tmp_pv = stats.ks_2samp(dat1[name], dat2[name])
        pl_ks.append(tmp_ks)
        pl_pv.append(tmp_pv)
        pl_data.append(pl_name[i])

df = pd.DataFrame()
df['factor'] = pl_factor
df['KS stats'] = pl_ks
df['pvalue'] = pl_pv
df['data'] = pl_data


#%% pick top 20 
df2 = df.query('data=="dev"').sort_values(by=['KS stats'], ascending=False)
df2.to_excel('ks_result.xlsx')
pl_indicator = df2.head(20)['factor'].tolist()
dat = dat_dev.copy()


# replace inf -inf
for factor in pl_indicator:                       
        dat[factor] = dat[factor].clip(
            np.nanmin(dat[factor][dat[factor] != -np.inf]),
            np.nanmax(dat[factor][dat[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_indicator: 
    if dat[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        dat[factor] = dat[factor].clip(1, np.inf)
        dat[factor] = np.log(dat[factor])



#%% plot factor distribution for good customer and other 
factor_index = 0
for pic in range(5):
    f, axes = plt.subplots(2,2, figsize=(10, 10))
    for img_r in range(2):
        for img_c in range(2):
            factor = pl_indicator[factor_index]
            dat1 = dat.query( 'Final_PD_Risk_Rating<=4').dropna(subset=[factor])
            dat2 = dat.query( 'Final_PD_Risk_Rating>=5').dropna(subset=[factor])
            sns.distplot( dat1[factor] , color="skyblue", label="Good Customers",ax=axes[img_r, img_c])
            sns.distplot( dat2[factor] , color="red", label="Others",ax=axes[img_r, img_c])
            factor_index += 1
    f.savefig('indicator_dist_{}.png'.format(pic))




#%% find the best cutoff by maximizing f1-score
#factor = 'size@Retained Earnings'
def _good_accu(quantile):
    cutoff = dat[factor].quantile(quantile[0])
    dat['pred'] = 0
    dat.loc[dat[factor]>=cutoff, 'pred'] = 1
    return(-f1_score(dat['GoodCustomer'], dat['pred'])  )


factor_index = 0
pl_f1 = []
pl_cutoff_quantile=[]
pl_cutoff=[]
pl_ave_pre=[]
for pic in range(5):
    f, axes = plt.subplots(2,2, figsize=(10, 10))
    for img_r in range(2):
        for img_c in range(2):
            factor = pl_indicator[factor_index]
            factor_index+=1
            dat = dat_dev.copy()
            dat['GoodCustomer'] = 0
            dat.loc[dat['Final_PD_Risk_Rating']<=4, 'GoodCustomer'] = 1
            #N_totalgood = dat['GoodCustomer'].sum()
            bounds = [(0.01,0.99),]
            res = differential_evolution(_good_accu, bounds)
            print('The best quantile to maximize F1-score is {:.5f}'.format(res.x[0]))
            pl_f1.append(-res.fun)
            pl_cutoff_quantile.append(res.x[0])
            cutoff = dat[factor].quantile(res.x[0])
            pl_cutoff.append(cutoff)
            dat['pred'] = 0
            dat.loc[dat[factor]>=cutoff, 'pred'] = 1
            precision_bestf1 = precision_score(dat['GoodCustomer'], dat['pred'])
            recall_bestf1 = recall_score(dat['GoodCustomer'], dat['pred'])

            precision=[]
            recall=[]
            for i in range(101):
                cutoff = dat[factor].quantile(i/100)
                dat['pred'] = 0
                dat.loc[dat[factor]>=cutoff, 'pred'] = 1
                precision.append(precision_score(dat['GoodCustomer'], dat['pred']))
                recall.append(recall_score(dat['GoodCustomer'], dat['pred']))

            average_precision = np.array(precision).mean()
            average_recall = np.array(recall).mean()
            pl_ave_pre.append(average_precision)
            pl_ave_rec.append(average_recall)
            # In matplotlib < 1.5, plt.fill_between does not have a 'step' argument
            
            step_kwargs = ({'step': 'post'}
                           if 'step' in signature(plt.fill_between).parameters
                           else {})
            axes[img_r,img_c].step(recall, precision, color='b', alpha=0.2,
                     where='post')
            axes[img_r,img_c].fill_between(recall, precision, alpha=0.2, color='b', **step_kwargs)
            axes[img_r,img_c].scatter(recall_bestf1,precision_bestf1, color='r')
            axes[img_r,img_c].set_xlabel('Recall')
            axes[img_r,img_c].set_ylabel('Precision')
            axes[img_r,img_c].set_ylim([0.0, 1.05])
            axes[img_r,img_c].set_xlim([0.0, 1.0])
            axes[img_r,img_c].set_title('Precision-Recall curve: {}'.format(factor))



    f.savefig('Precision-Recall curve_{}.png'.format(pic))


result=pd.DataFrame()
result['Factor'] = pl_indicator
result['Best F1-score'] = pl_f1
result['cutoff_quantile'] = pl_cutoff_quantile
result['cutoff_value'] = pl_cutoff
result['Average_Precison'] = pl_ave_pre
result['Average_Recall'] = pl_ave_rec
result.to_excel(r'indicator\result2.xlsx')



'''
truepos = len(dat.query('GoodCustomer==1 and pred==1'))
trueneg = len(dat.query('GoodCustomer==0 and pred==0'))
falsepos = len(dat.query('GoodCustomer==0 and pred==1'))
falseneg = len(dat.query('GoodCustomer==1 and pred==0'))
recall = truepos / (truepos + falseneg)
precision = truepos / (truepos + falsepos)
f1 =  2 * (precision * recall) / (precision + recall)
'''
import os, sys, pandas as pd, numpy as np


dat = pd.read_pickle(r'C:\Users\ub71894\Documents\Projects\CNI_redev\data\dat_newms_train.pkl') # setting
dat2 = dat.query('Final_PD_Risk_Rating<=4')

data_Ming = pd.read_pickle(r'C:\Users\ub71894\Documents\Data\Ming\branch_4snapshots_unique.pkl')
dat_Ming2 = data_Ming.query('Final_PD_Risk_Rating<=4')
dat_Ming2.sort_values(by=['CUSTOMERID', 'archive_date'], ascending=True, inplace=True)
dat_Ming3 = dat_Ming2.drop_duplicates(subset=['CUSTOMERID'], keep='last')
dat_Ming = dat_Ming3.query('20160501<=archive_date<=20181231')



curr = set(dat.CUSTOMERID)
curr_good = set(dat2.CUSTOMERID)
ming = set(dat_Ming.CUSTOMERID)

pl_missing = list(ming-curr_good)
print(pl_missing)

df_missing = pd.DataFrame()
for custid in pl_missing:
    df_missing =pd.concat([df_missing,dat_Ming.query('CUSTOMERID=={}'.format(custid)) ], axis=0)



#%% tokyo list
pl_tokyo=['Apple',
'Oracle Corp',
'Comcast Corporation',
'Motorola Solutions',
'Moody',
'Avnet Inc',
'Salesforce.com Inc',
'Automatic Data Processing',
'Hearst Corporation',
'Texas Instruments Inc',
'Frontier Communications',
'The Walt Disney Company',
'Omnicom Group Inc',
'Microsoft Corp',
'AT&T',
'Plexus Corp',
'Amazon.com Inc',
'Xilinx Inc',]




pl_tokyo2=['Apple',
'Oracle',
'Comcast',
'Motorola',
'Moody',
'Avnet',
'Salesforce',
'Automatic Data Processing',
'Hearst',
'Texas Instruments',
'Frontier',
'Disney',
'Omnicom',
'Microsoft',
'AT&T',
'Plexus',
'Amazon',
'Xilinx',]



pl_dat = list(dat['Customer Long Name'].unique())
pl_dat_ming = list(data_Ming['Customer_Name'].unique())

for name in pl_tokyo2:
    for target in pl_dat:
        if name in target:
            print(name +' is in dat: '+target)
        else:
            pass
'''
no AT&T 
Apple is in dat: Apple Inc.
Oracle is in dat: Oracle Corporation
Comcast is in dat: Comcast Corporation
Motorola is in dat: Motorola Solutions, Inc.
Moody is in dat: Moody's Corporation
Avnet is in dat: Avnet, Inc.
Salesforce is in dat: Salesforce.Com, Inc.
Automatic Data Processing is in dat: Automatic Data Processing, Inc.
Hearst is in dat: The Hearst Corporation
Texas Instruments is in dat: Texas Instruments Incorporated
Frontier is in dat: Frontier Communications Corporation
Disney is in dat: The Walt Disney Company
Omnicom is in dat: Omnicom Group Inc.
Microsoft is in dat: Microsoft Corporation
Plexus is in dat: Plexus Corp.
Amazon is in dat: Amazon.Com, Inc.
Xilinx is in dat: Xilinx, Inc.

'''


for name in pl_tokyo2:
    for target in pl_dat_ming:
        if name in target:
            print(name +' is in dat: '+target)
        else:
            pass
'''
No Apple, AT&T , Microsoft, Omnicom 

Oracle is in dat: Oracle Corporation
Comcast is in dat: Comcast Corporation
Motorola is in dat: Motorola Solutions, Inc.
Moody is in dat: Moody's Corporation
Avnet is in dat: Avnet, Inc.
Salesforce is in dat: Salesforce.Com, Inc.
Automatic Data Processing is in dat: Automatic Data Processing, Inc.
Hearst is in dat: The Hearst Corporation
Texas Instruments is in dat: Texas Instruments Incorporated
Frontier is in dat: Frontier Communications Corporation
Disney is in dat: The Walt Disney Company
Plexus is in dat: Plexus Corp.
Amazon is in dat: Amazon.Com, Inc.
Xilinx is in dat: Xilinx, Inc.

'''
Net Operating Profit / Net Sales (+/0: Floor)
Net Operating Profit / Net Sales (-/0: Floor)
Net Operating Profit / Net Sales (0/0: 0)
Net Operating Profit / Net Sales (+/-: Keep as the answer)
Net Operating Profit / Net Sales (-/-: Keep as the answer)
Net Operating Profit / Net Sales (0/-: 0)
Total Debt / Internal EBITDA (+/0: Cap)
Total Debt / Internal EBITDA (-/0: Floor)
Total Debt / Internal EBITDA (0/0: 0)
Total Debt / Internal EBITDA (+/-: Keep and Invalid Neg will apply)
Total Debt / Internal EBITDA (-/-: Keep as the answer)
Total Debt / Internal EBITDA (0/-: Invalid Negative Treatment)
Tangible Net Worth / Total Assets (+/0: Floor)
Tangible Net Worth / Total Assets (-/0: Floor)
Tangible Net Worth / Total Assets (0/0: 0)
Tangible Net Worth / Total Assets (+/-: Keep as the answer)
Tangible Net Worth / Total Assets (-/-: Keep as the answer)
Tangible Net Worth / Total Assets (0/-: 0)
Total Debt / Capitalization (+/0: Cap)
Total Debt / Capitalization (-/0: Floor)
Total Debt / Capitalization (0/0: 0)
Total Debt / Capitalization (+/-: Keep and Invalid Neg will apply)
Total Debt / Capitalization (-/-: Keep as the answer)
Total Debt / Capitalization (0/-: Invalid Negative Treatment)
ln(ECE / Total Liabilities) (+/0: Cap)
ln(ECE / Total Liabilities)  (-/0: Floor)
ln(ECE / Total Liabilities)  (0/0: Floor)
ln(ECE / Total Liabilities) (+/-: Cap)
ln(ECE / Total Liabilities)  (-/-: Keep as the answer)
ln(ECE / Total Liabilities) (0/+: Floor)
ln(ECE / Total Liabilities)  (0/-: Floor)
ln(ECE / Total Liabilities)  (-/+: Floor)
['01_data_01_merge.py', '01_data_02_buildratios.py', '01_data_03_combine.py', '02_SFA_01_dataquality.py', '02_SFA_02.py', '03_MFA_01_data.py', '03_MFA_02_col_B_595.py', '03_MFA_02_col_C_595.py', '03_MFA_02_col_E_595.py', '03_MFA_02_col_F_595.py', '03_MFA_02_col_H_595.py', '03_MFA_02_col_I_595.py', '03_MFA_03_core_H.py', '03_MFA_03_core_I.py', '03_MFA_03_good_H.py', '03_MFA_03_good_H_nodup.py', '03_MFA_03_good_H_nodup_bin_regression.py', '03_MFA_03_good_H_nodup_bin_SD.py', '03_MFA_03_good_I.py', '03_MFA_03_good_I_nodup.py', '04_core_ind_analysis.py', '04_core_ind_analysis_initial.py', '0x_apply_currmodel_on_test_sample.py', '0x_good_outlier_I.py', 'core_maug_outlier_H.py', 'core_stats_outlier_H.py', 'investigate_234_indicator.py', 'missing_inSDF.py', 'specialcase.py']
[45, 558, 1024, 1533, 1667, 1696, 1973, 2224, 2468, 2715, 2986, 3258, 3531, 3801, 4068, 4328, 4900, 5126, 5395, 5655, 5816, 5910, 6212, 6410, 6502, 6780, 6972, 7100, 7132]
