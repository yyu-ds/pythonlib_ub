# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 10:18:56 2020

@author: ub71894
"""

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev2".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from PDScorecardTool.Process import SomersD, MAUG_mapping, getPDRR
from PDScorecardTool.Process import PD_frPDRR_autoMS, logitPD_frPDRR_autoMS
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
from PDScorecardTool.MFA import MFA
from scipy.optimize import fsolve
import scipy.stats as scistat
import time
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle


model_LC1 = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_LC.pkl','rb'))
model_LC2 = pickle.load(open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb'))


model_LC1.quali_factor = model_LC2.quali_factor =[
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital']

model_LC1.quant_factor = model_LC2.quant_factor =[
'EBITDA_by_Net_Sales_12M',
'Total_debt_by_EBITDA',
'TotalAssets',
'Total_debt_by_Capital',
'EBITDA_by_Int_Exp']

model_LC1.Invalid_Neg = model_LC2.Invalid_Neg  = [
0,'EBITDA', 0, 'Capitalization',  'Interest_expense']

def _RLA(data):
    N = len(data)
    n_RLA = len(data.query('RLA_Notches!=0'))    
    return (n_RLA/N)

def _OVD(data):
    N = len(data)   
    n_Override = len(data.query('Override_Action!=0'))
    return (n_Override/N)



#%% 2019 data
data = pd.read_excel(r'C:\Users\ub71894\Documents\Projects\CNI\newdata\2019_RA_OCCI_SINCE_PROD_corrected.xlsx')
data = data.query('sc_segment=="C&I Large Corporate" or sc_segment=="1"')
data.drop_duplicates(subset=['CUSTOMERID'], inplace=True)
data.reset_index(drop=True, inplace=True )
data = MAUG_mapping(data)
data['Sample'] = data['Industry_by_MAUG'].copy()
data['Sample'].replace(pd_core, inplace=True)
data['Sample'].replace(pd_noncore, inplace=True)
######### no mapping for MAUG 172 and MAUG 373, mapping them to non-core
data['Sample'] = ['Non-Core' if x!='Core' else 'Core' for x in data['Sample'].tolist() ]
data['RLA_Notches'].fillna(0, inplace=True)
data['Override_Action'].fillna(0, inplace=True)
data.reset_index(drop=True, inplace=True )
data['TotalAssets'] = np.log(1+data['Total_Assets'])
data.dropna(subset=model_LC1.quant_factor + model_LC1.quali_factor, inplace=True, how='any')

for factor in model_LC1.quant_factor:                       
        data[factor] = data[factor].clip(np.nanmin(data[factor][data[factor] != -np.inf]), np.nanmax(data[factor][data[factor] != np.inf]))





#%% investigation
data_1 = data.query('archive_date<20191214')
data_1_rating = getPDRR(data_1, model_LC1, ms_ver='new')
data_1_rating['diff'] = data_1_rating['Ratings'] - data_1_rating['Prelim_PD_Risk_Rating_Uncap']
sample = data_1_rating.query('diff!=0')
#sample.to_excel('sample.xlsx')
list_id = sample.CUSTOMERID.tolist()

nonmatch = data_1[data_1.CUSTOMERID.isin(list_id)].copy()
nonmatch2 = data_1_rating[data_1_rating.CUSTOMERID.isin(list_id)].copy()
nonmatch['EBITDA_by_Net_Sales_12M_m'] = nonmatch['EBITDA'] / nonmatch['Net_Sales']
nonmatch['Total_debt_by_EBITDA_m'] = nonmatch['Total_Debt'] / nonmatch['EBITDA']
nonmatch['Total_debt_by_Capital_m'] = nonmatch['Total_Debt'] / nonmatch['Capitalization']
nonmatch['EBITDA_by_Int_Exp_m'] = nonmatch['EBITDA'] / nonmatch['Interest_expense']


nonmatch['EBITDA_by_Net_Sales_12M_diff'] = nonmatch['EBITDA_by_Net_Sales_12M_m'] - nonmatch['EBITDA_by_Net_Sales_12M']
nonmatch['Total_debt_by_EBITDA_diff'] = nonmatch['Total_debt_by_EBITDA_m'] - nonmatch['Total_debt_by_EBITDA']
nonmatch['Total_debt_by_Capital_diff'] = nonmatch['Total_debt_by_Capital_m'] - nonmatch['Total_debt_by_Capital']
nonmatch['EBITDA_by_Int_Exp_diff'] = nonmatch['EBITDA_by_Int_Exp_m'] - nonmatch['EBITDA_by_Int_Exp']

aa= pd.concat([nonmatch[[
'Net_Sales',
'Total_Debt',
'EBITDA',
'Total_Assets',
'Capitalization',
'Interest_expense',
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital',
'EBITDA_by_Net_Sales_12M_m','EBITDA_by_Net_Sales_12M',
'Total_debt_by_EBITDA_m','Total_debt_by_EBITDA',
'Total_debt_by_Capital_m','Total_debt_by_Capital',
'EBITDA_by_Int_Exp_m','EBITDA_by_Int_Exp',
]], nonmatch2[['quantscore',
'Quantitative_Score',
'Prelim_PD_Risk_Rating_Uncap',
'Ratings',
]]], axis=1)

bb =  nonmatch2[['EBITDA_by_Net_Sales_12M',
'Total_debt_by_EBITDA',
'Total_debt_by_Capital',
'EBITDA_by_Int_Exp',]]


nonmatch.to_excel('nonmatch.xlsx')


sample = data_1_rating.query('diff==0')
list_id = sample.CUSTOMERID.tolist()
match = data_1[data_1.CUSTOMERID.isin(list_id)].copy()


len(data.query('RLA_Notches!=0')) / len(data) 
#0.3549920760697306
len(nonmatch.query('RLA_Notches!=0')) / len(nonmatch) 
# 0.4166666666666667
len(match.query('RLA_Notches!=0')) / len(match) 
# 0.3476764199655766

len(data.query('Override_Action!=0')) / len(data) 
Out[18]: 0.30427892234548337

len(nonmatch.query('Override_Action!=0')) / len(nonmatch) 
Out[19]: 0.2777777777777778

len(match.query('Override_Action!=0')) / len(match) 
Out[20]: 0.3098106712564544



#%% get all matched records

data_1 = data.query('archive_date<20191214')
data_1 = getPDRR(data_1, model_LC1, ms_ver='new')
data_1['diff'] = data_1['Ratings'] - data_1['Prelim_PD_Risk_Rating_Uncap']
sample1 = data_1.query('diff==0')
list_id1 = sample1.CUSTOMERID.tolist()

data_2 = data.query('archive_date>20191214')
data_2 = getPDRR(data_2, model_LC2, ms_ver='new')
data_2['diff'] = data_2['Ratings'] - data_2['Prelim_PD_Risk_Rating_Uncap']
sample2 = data_2.query('diff==0')
list_id2 = sample2.CUSTOMERID.tolist()

list_id = list_id1 + list_id2
match = data[data.CUSTOMERID.isin(list_id)].copy()
#match.to_excel('match.xlsx')
match.groupby('Sample').apply(_RLA)
'''
Out[6]: 
Sample
Core        0.418367
Non-Core    0.210000
dtype: float64
'''
match.groupby('Sample').apply(_OVD)
'''
Out[7]: 
Sample
Core        0.326531
Non-Core    0.270000
dtype: float64
'''


#%%
dat = match.copy()
dat['Guarantor_Notches'].fillna(0, inplace=True)
dat = dat.query('Guarantor_Notches==0')

dat['target'] = dat['Final_PD_Risk_Rating'] - dat['RLA_Notches']
dat = PD_frPDRR_autoMS(dat, model_LC1, PDRR='target', timestamp='archive_date')
dat = logitPD_frPDRR_autoMS(dat, model_LC1, PDRR='target', timestamp='archive_date')


dat['Final_PD'].mean()
Out[29]: 1.166400679117149

dat['PD_frPDRR'].mean()
Out[30]: 0.7513921901528003

dat['Model_PD'].mean()
Out[31]: 0.7525360957006754


f'{len(dat.query("Override_Action<0")) / len(dat)*100:.2f}% upgrade override'
Out[40]: '20.54% upgrade override'

f'{len(dat.query("Override_Action==0")) / len(dat)*100:.2f}% no override'
Out[41]: '69.10% no override'

f'{len(dat.query("Override_Action>0")) / len(dat)*100:.2f}% downgrade override'
Out[42]: '10.36% downgrade override'




#%% SFA 
list_sd=[]
list_oldsd=[]
for i,name  in enumerate(model_LC1.quant_factor):
    list_sd.append(model_LC1.quant_multiplier[i] * SomersD(dat['target'], dat[name]))
    list_oldsd.append(model_LC1.quant_multiplier[i] * SomersD(dat['Final_PD_Risk_Rating'], dat[name]))
dat_quali = getPDRR(dat, model_LC1, ms_ver='new')
for name in model_LC1.quali_factor:
    list_sd.append(SomersD(dat_quali['target'], dat_quali[name]))
    list_oldsd.append(SomersD(dat_quali['Final_PD_Risk_Rating'], dat_quali[name]))

df_sd = pd.DataFrame()
df_sd['with_FinalPDRR'] = list_oldsd
df_sd['with_newtarget'] = list_sd
df_sd.index = model_LC1.quant_factor + model_LC1.quali_factor
df_sd.to_excel(r'data\SomersD_2019.xlsx')


#%%
sns.relplot(x='Total_Score', y='target', data= dat,hue="Sample")
sns.lmplot(x='Total_Score', y='target', data= dat,hue="Sample")
dat_plot = dat.query('Sample=="Non-Core"')
sns.lmplot(x='Total_Score', y='target', data= dat_plot)
sns.relplot(x='Total_Score', y='Final_PD_Risk_Rating', data= dat,hue="Sample")
sns.lmplot(x='Total_Score', y='Final_PD_Risk_Rating', data= dat,hue="Sample")


#%%
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
def get_intcp(data, CT, slope):
    df= data.copy()
    def _fun(Intercept):
        df['fitted_logit_pd'] = Intercept + slope*df['Total_Score']
        df['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in df['fitted_logit_pd'] ]
        return (df.fitted_pd.mean()-CT)
    intcp = fsolve(_fun, -5)
    return(intcp[0])

def scorecard_single(data, Intercept, slope, ms_ver='new'):
    df = data.copy()
    
    if ms_ver=='old':
        low_pd = MS['old_low']
    else:
        low_pd = MS['new_low']

    df['fitted_logit_pd'] = Intercept + slope*df['Total_Score']
    df['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in df['fitted_logit_pd'] ]
    Ratings = []
    for i in df.iterrows():
        Ratings.append(sum(low_pd<=(i[1].fitted_pd)))
    df['fitted_PDRR'] = Ratings   

    return(df)

N = len(dat)
list_CT =[0.006, 0.0065, 0.007, 0.007513921901528003, 0.008, 0.0085, 0.009, 0.0095, 0.01, 0.0105]
writer = pd.ExcelWriter(r"data\calib.xlsx")

for CT in list_CT:
    print(f'For CT={CT*100:.3f}%')
    pl_slope = list(np.linspace(0.01,0.06,200))
    perf_table = pd.DataFrame()
    for slope in pl_slope:
        Intercept = get_intcp(dat, CT, slope)
        df = scorecard_single(dat, Intercept, slope, ms_ver='new')
        stats = TMstats(df, 'fitted_PDRR', 'target', PDRR=range(1,16))
    
        df['fitted_final'] = df['fitted_PDRR'] + df['RLA_Notches']
        stats.update({'UpgradeOvd':  (df['fitted_final']>df['Final_PD_Risk_Rating']).sum() / N})
        stats.update({'NoOvd':  (df['fitted_final']==df['Final_PD_Risk_Rating']).sum()/ N})
        stats.update({'DowngradeOvd':  (df['fitted_final']<df['Final_PD_Risk_Rating']).sum()/ N})
        
        stats.update({'SomersD':SomersD(df.target, df.fitted_PDRR)})
        stats.update({'Intercept':Intercept, 'slope':slope})
        D, pvalue = scistat.ks_2samp(df.target, df.fitted_PDRR)
        stats.update({'KS_stats':D})
        perf_table = perf_table.append(stats,ignore_index=True)
    
    perf_table = perf_table[['Intercept','slope','UpgradeOvd','DowngradeOvd','NoOvd',
    'SomersD','Match', 'Within_1', 'Within_2', 'Outside_5', 'KS_stats','Downgrade', 'Upgrade']]
    perf_table['diff'] = perf_table['Downgrade'] - perf_table['Upgrade']
    perf_table['existing_KS_stats'],_ = scistat.ks_2samp(df.target, df.Prelim_PD_Risk_Rating_Uncap)
    perf_table.sort_values(by='NoOvd', ascending=False, inplace=True)
    perf_table.to_excel(writer,f'CT={CT*100:.3f}%')

writer.save()  



# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 10:18:56 2020

@author: ub71894
"""

import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev2".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from PDScorecardTool.Process import SomersD, MAUG_mapping, getPDRR
from PDScorecardTool.Process import PD_frPDRR_autoMS, logitPD_frPDRR_autoMS
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
from PDScorecardTool.MFA import MFA
from scipy.optimize import fsolve
import scipy.stats as scistat
import time
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from core_list import pd_core, pd_noncore
import pickle
import missingno as msno

model_LC1 = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_LC.pkl','rb'))
model_LC2 = pickle.load(open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb'))


model_LC1.quali_factor = model_LC2.quali_factor =[
 'Strength_SOR_Prevent_Default',
 'Level_Waiver_Covenant_Mod',
 'Management_Quality',
 'Vulnerability_To_Changes',
 'Access_Outside_Capital']

model_LC1.quant_factor = model_LC2.quant_factor =[
'EBITDA_by_Net_Sales_12M',
'Total_debt_by_EBITDA',
'TotalAssets',
'Total_debt_by_Capital',
'EBITDA_by_Int_Exp']

model_LC1.Invalid_Neg = model_LC2.Invalid_Neg  = [
0,'EBITDA', 0, 'Capitalization',  'Interest_expense']

def _RLA(data):
    N = len(data)
    n_RLA = len(data.query('RLA_Notches!=0'))    
    return (n_RLA/N)

def _OVD(data):
    N = len(data)   
    n_Override = len(data.query('Override_Action!=0'))
    return (n_Override/N)



#%% 2019 data
data = pd.read_excel(r'C:\Users\ub71894\Documents\Projects\CNI\newdata\2019_RA_OCCI_SINCE_PROD_corrected.xlsx')
data = data.query('sc_segment=="C&I Large Corporate" or sc_segment=="1"')
data['Guarantor_Notches'].fillna(0, inplace=True)
data = data.query('Guarantor_Notches==0')
data['RLA_Notches'].fillna(0, inplace=True)
data['Override_Action'].fillna(0, inplace=True)
data['target'] = data['Final_PD_Risk_Rating'] - data['RLA_Notches']
data.reset_index(drop=True, inplace=True)

list_cols=[
 'ACF',
 'Cash_Operating_Profit',
 'Ending_Cash_Equiv',
 'Net_Profit',
 'Net_Sales',
 'Tangible_Net_Worth',
 'Total_Assets',
 'Total_Debt',
 'Total_Liabilities',
 'Net_Profit_Margin',
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
 'EBITDA',
 'Capitalization',
 'Total_Assets_LC',
 'Net_Op_Profit',
 'Internal_EBITDA',
 'Interest_expense',
 'Obligor_size'

]

dat = data[list_cols].copy()
msno.matrix(dat)

# remove low quality column:
list_cols=[
 'Ending_Cash_Equiv',
 'Net_Sales',
 'Tangible_Net_Worth',
 'Total_Assets',
 'Total_Debt',
 'Total_Liabilities',
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
 'EBITDA',
 'Capitalization',
 'Total_Assets_LC',
 'Interest_expense',
 'target',
 'Final_PD_Risk_Rating'
]


dat = data[list_cols].copy()
#msno.matrix(dat)


#%% build ratios
list_quantitem=[
'Ending_Cash_Equiv',
'Net_Sales',
'Tangible_Net_Worth',
'Total_Assets',
'Total_Debt',
'Total_Liabilities',
'EBITDA',
'Capitalization']

list_sd=[]
list_pct=[]
list_ratio_name=[]
N=len(dat)
for a,b in itertools.combinations(list_quantitem,2):
    ratio_name = f'{a}_by_{b}'
    list_ratio_name.append(ratio_name)
    dat[ratio_name] = dat[a] / dat[b]
    temp =  dat.dropna(subset=[ratio_name])
    list_pct.append(len(temp)/N)
    list_sd.append(np.abs(SomersD(temp['target'], temp[ratio_name])))
for name in list_quantitem:
    list_ratio_name.append(name)
    temp =  dat.dropna(subset=[name])
    list_pct.append(len(temp)/N)
    list_sd.append(np.abs(SomersD(temp['target'], temp[name])))


df_sd = pd.DataFrame()
df_sd['SomersD'] = list_sd
df_sd['Quality'] = list_pct
df_sd.index = list_ratio_name# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 10:18:56 2020

@author: ub71894
"""
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev2".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import quanttrans, qualitrans
from PDScorecardTool.MFA import MFA

import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from itertools import combinations, product
import statsmodels.api as sm
import time
import pickle
filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

data = pd.read_pickle(r'C:\Users\ub71894\Documents\Projects\CNI\src\MFA\train_2016.pkl.xz')
pl_qualifactors=[ 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital']
data.dropna(subset=pl_qualifactors, how='any', inplace=True)
data = logitPD_frPDRR(data, model, 'Final_PD_Risk_Rating', ms_ver='old')
data = PD_frPDRR(data, model, 'Final_PD_Risk_Rating', ms_ver='old')
data.reset_index(drop=True, inplace=True)
target = 'Final_PD_Risk_Rating'  # setting
target_logitPD = 'logitPD_frPDRR' 
target_PD = 'PD_frPDRR'  # setting

floor=0.05 # setting
cap=0.95 # setting

pl_candidates = [
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
 'cf@TD_to_UBEBITDA',
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
 'liq@ECE_to_TL',
 'liq@Quick Ratio',
 'liq@RE_to_CL',
 'liq@Union Bank Current Ratio',
 'liq@Union Bank Quick Ratio',
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

#%% SFA
pl_sd = []
for factor in pl_candidates:
    df = data[[factor,target]].copy()
    df.dropna(how='any', inplace=True)
    pl_sd.append(np.abs(SomersD(df[target], df[factor])))

df_somersd = pd.DataFrame()
df_somersd['SD'] = pl_sd
df_somersd.index = pl_candidates
df_somersd.sort_values(by=['SD'], inplace=True, ascending=False)


top = 50
pl_top_candidates=list(df_somersd.index)[:top]


# check sign
sfa = []
for factor in pl_top_candidates:
    sfa.append(SomersD(data[target], data[factor]))
np.sign(sfa)


#%% correlation cluster
# initial 
f, ax = plt.subplots(figsize=(20, 12))
sns.heatmap(data[pl_top_candidates].corr(), linewidths=.3, cmap='Blues', ax=ax)
# after clustering
cat=cluster_corr(data, pl_top_candidates)
plot_cluster_corr(data, cat)

print('The number of categories is {}'.format(len(cat)))
# 18

## trim cat list if more than 5 factor
pl_candidates=[]
pl_cat=[]
for pl_cand in cat:
    if len(pl_cand)>1:
        pl_cat.append(pl_cand[:1])
        pl_candidates+=pl_cand[:1]
    else:
        pl_cat.append(pl_cand)
        pl_candidates+=pl_cand


#%% processing and normalization:
# replace inf -inf
for factor in pl_candidates:                       
        data[factor] = data[factor].clip(
            np.nanmin(data[factor][data[factor] != -np.inf]),
            np.nanmax(data[factor][data[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_candidates: 
    if data[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        data[factor] = data[factor].clip(1, np.inf)
        data[factor] = np.log(data[factor])

# sort
pl_candidates = pl_dollar + pl_ratio


#%% auto invalid negtive identification:
pl_invalid_neg = []
for factor in pl_ratio:
    df = data[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()
    mid_point = np.sqrt(cap_mean*floor_mean)

    if floor_mean>cap_mean and neg_mean<mid_point: # means it's closer to cap
        pl_invalid_neg.append(factor)
    elif floor_mean<cap_mean and neg_mean>mid_point: # means it's closer to cap
        pl_invalid_neg.append(factor)
    else:
        pl_invalid_neg.append(0)

# prepare  not finish
sfa = []
for factor in pl_candidates:
    sfa.append(SomersD(data[target], data[factor]))

model.update({'quant_factor':pl_candidates})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(data, model, floor=floor, cap=cap)) # setting


cni_train = MFA(data, model, quant_only=False)
df_norm = cni_train.normdata.copy()



#%%
num_of_params = 6
N_iter=0
pl_models=[];  pl_R2=[];  pl_SD_in=[];  
pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]

for cats in combinations(np.arange(len(cat)), num_of_params):
    temp=[]
    for i in range(num_of_params):
        temp.append(pl_cat[cats[i]])

    exec(f'py_list = product(*{temp})')
    for facs in py_list:      
        N_iter+=1


#%%

start_time = time.time()
count=0
epoch = int(N_iter/100)
pl_models=[];  pl_R2=[];  pl_SD_in=[];  pl_SD_out=[]; pl_pvals=[];pl_liq_wt=[]; pl_sign=[]
for cats in combinations(np.arange(len(cat)), num_of_params):
    temp=[]
    for i in range(num_of_params):
        temp.append(pl_cat[cats[i]])

    exec(f'py_list = product(*{temp})')
    for facs in py_list:
        names = list(facs)
        x_train = sm.add_constant(df_norm[names], prepend = True)
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
            print(r'Estimated remaining time:{:.0f} seconds'.format(lefttime))

models = pd.DataFrame()
models['models'] = pl_models
models['R2'] = pl_R2
models['SD_insample'] = pl_SD_in
#models['SD_outsample'] = pl_SD_out
models['max_pvalue'] = pl_pvals
models['sign'] = pl_sign
models.to_excel(f'model_with{num_of_params}_factors.xlsx')
print("--- %s seconds ---" % (time.time() - start_time))



#%%
with open("pl_top_candidates.txt", "wb") as fp:   #Pickling
    pickle.dump(pl_top_candidates, fp)


pl_cat2 = [x[0]  for x in pl_cat]
with open("pl_cat.txt", "wb") as fp:   #Pickling
    pickle.dump(pl_cat2, fp)

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 10:18:56 2020

@author: ub71894
"""
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev2".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))
from newfunc import cluster_corr, plot_cluster_corr
from PDScorecardTool.Process import SomersD, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import quanttrans, qualitrans
from PDScorecardTool.MFA import MFA

import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')
from itertools import combinations, product
import statsmodels.api as sm
import time
import pickle
filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl'.format(usrid),'rb')
model = pickle.load(filehandler)

data = pd.read_pickle(r'C:\Users\ub71894\Documents\Projects\CNI\src\MFA\train_2016.pkl.xz')
pl_qualifactors=[ 'qual1', 'qual2', 'Management_Quality', 'qual4', 'Access_Outside_Capital']
data.dropna(subset=pl_qualifactors, how='any', inplace=True)
data = logitPD_frPDRR(data, model, 'Final_PD_Risk_Rating', ms_ver='old')
data = PD_frPDRR(data, model, 'Final_PD_Risk_Rating', ms_ver='old')
data.reset_index(drop=True, inplace=True)
target = 'Final_PD_Risk_Rating'  # setting
target_logitPD = 'logitPD_frPDRR' 
target_PD = 'PD_frPDRR'  # setting

floor=0.05 # setting
cap=0.95 # setting

pl_candidates = [
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
 'cf@TD_to_UBEBITDA',
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
 'liq@ECE_to_TL',
 'liq@Quick Ratio',
 'liq@RE_to_CL',
 'liq@Union Bank Current Ratio',
 'liq@Union Bank Quick Ratio',
 'prof@AFTERTAXINCOME',
 'prof@CD_to_NP',
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
 'size@Funds from Operations (FFO)',
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

#data.columns[data.isnull().mean() >0.2]

#%% processing and normalization:
# replace inf -inf
for factor in pl_candidates:                       
        data[factor] = data[factor].clip(
            np.nanmin(data[factor][data[factor] != -np.inf]),
            np.nanmax(data[factor][data[factor] != np.inf]))

# find dollar value factors:
pl_dollar = []
pl_ratio = []
for factor in pl_candidates: 
    if data[factor].mean()>1e6:
        pl_dollar.append(factor)
    else:
        pl_ratio.append(factor)

# replace all non-positive dollar value factor with 1 and log transform
for factor in pl_dollar:                       
        data[factor] = data[factor].clip(1, np.inf)
        data[factor] = np.log(data[factor])

# sort
pl_candidates = pl_dollar + pl_ratio


#%% auto invalid negtive identification:
pl_invalid_neg = []
for factor in pl_ratio:
    df = data[[factor, target_PD]].copy()
    # rename
    df.rename(columns={factor:'ratio'}, inplace=True)
    df_pos = df.query('ratio>0')
    floor_mean = df_pos.query('ratio<={}'.format(df_pos.ratio.quantile(floor)))[target_PD].mean()   
    cap_mean = df_pos.query('ratio>={}'.format(df_pos.ratio.quantile(cap)))[target_PD].mean()   
    neg_mean = df.query('ratio<=0')[target_PD].mean()
    mid_point = np.sqrt(cap_mean*floor_mean)

    if floor_mean>cap_mean and neg_mean<mid_point: # means it's closer to cap
        pl_invalid_neg.append(factor)
    elif floor_mean<cap_mean and neg_mean>mid_point: # means it's closer to cap
        pl_invalid_neg.append(factor)
    else:
        pl_invalid_neg.append(0)

# prepare  not finish
sfa = []
for factor in pl_candidates:
    sfa.append(SomersD(data[target], data[factor]))

model.update({'quant_factor':pl_candidates})
model.update({'quant_multiplier': np.sign(sfa)})
model.update({'quant_log': [0]*len(pl_candidates)})
model.update({'Invalid_Neg': [0]*len(pl_dollar)+pl_invalid_neg})
model.update(quanttrans(data, model, floor=floor, cap=cap)) # setting


cni_train = MFA(data, model, quant_only=False)
df_norm = cni_train.normdata.copy()

df_norm.to_pickle(r'data\df_norm_all.pkl')



with open("pl_candidates.txt", "wb") as fp:   #Pickling
    pickle.dump(pl_candidates, fp)

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 10:18:56 2020

@author: ub71894
"""
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev2".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))

from PDScorecardTool.Process import SomersD, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import getPDRR
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.feature_selection import SelectFromModel
from sklearn.preprocessing import PolynomialFeatures
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='Set1')
import statsmodels.api as sm
import pickle
filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl'.format(usrid),'rb')
model_LC = pickle.load(filehandler)

with open("pl_top_candidates.txt", "rb") as fp:   # Unpickling
    pl_top_candidates = pickle.load(fp)
with open("pl_cat.txt", "rb") as fp:   # Unpickling
    pl_cat = pickle.load(fp)


target = 'Final_PD_Risk_Rating'  # setting
target_logitPD = 'logitPD_frPDRR' 
target_PD = 'PD_frPDRR'  # setting
floor=0.05 # setting
cap=0.95 # setting


df_norm = pd.read_pickle(r'data\df_norm_all.pkl')
'''
list_models=[
['size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL', 'cf@TD_COP'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL', 'cf@AdjTD_to_UBEBITDA', 'cf@TD_COP'],
['size@Profit before Taxes', 'size@Total Net Worth', 'liq@ECE_to_TL', 'size@Retained Earnings', 'prof@EBIT_to_NS', 'ds@EBIT_and_LE_to_DS_and_LE', 'bs@TD_to_Capt'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_CL', 'liq@ECE_to_CA', 'liq@ECE_to_TD', 'cf@AdjTD_to_UBEBITDA', 'cf@TD_COP'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_CL', 'liq@ECE_to_CA', 'liq@ECE_to_AdjTD', 'liq@ECE_to_TD', 'cf@AdjTD_to_UBEBITDA', 'size@TNW_to_TA']
]

list_mse = []
for model in list_models:
    x_train = sm.add_constant(df_norm[model], prepend = True)
    linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
    result = linear.fit(disp=0)
    list_mse.append(result.mse_resid)
'''

#%%
list_models_forced=[
['size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL', 'cf@TD_COP'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL', 'liq@ECE_to_AdjTD', 'cf@TD_COP'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL', 'liq@ECE_to_AdjTD', 'size@TNW_to_TA', 'cf@TD_COP'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL', 'liq@ECE_to_AdjTD', 'cf@AdjTD_to_UBEBITDA', 'size@TNW_to_TA', 'cf@TD_COP'],
['size@Profit before Taxes', 'size@Total Net Worth', 'prof@Net Profit Margin %', 'liq@ECE_to_TL', 'liq@ECE_to_AdjTD', 'prof@EBIT_to_NS', 'cf@AdjTD_to_UBEBITDA', 'size@TNW_to_TA', 'cf@TD_COP']
]

list_mse_forced = []
list_matchrate_forced = []
for model in list_models_forced:
    df_LR = df_norm.dropna(subset=model, how='any')[model+[target, target_logitPD]].copy()

    x_train = sm.add_constant(df_LR[model], prepend = True)
    linear = sm.OLS(df_LR[target_logitPD], x_train, missing='drop')
    result = linear.fit(disp=0)
    list_mse_forced.append(result.mse_resid)

    pds = result.fittedvalues.apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))

    ms_ver = 'old'
    if ms_ver=='old':
        low_pd = model_LC.MS['old_low']
    else:
        low_pd = model_LC.MS['new_low']
    ratings = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_forced.append((df_LR[target]==ratings).sum() / len(df_LR))

list_mse_forced_withquali = []
list_matchrate_forced_withquali = []
for model in list_models_forced:
    fullmodel = model+model_LC.quali_factor
    df_LR = df_norm.dropna(subset=fullmodel, how='any')[fullmodel+[target, target_logitPD]].copy()
    x_train = sm.add_constant(df_LR[fullmodel], prepend = True)
    linear = sm.OLS(df_LR[target_logitPD], x_train, missing='drop')
    result = linear.fit(disp=0)
    list_mse_forced_withquali.append(result.mse_resid)

    pds = result.fittedvalues.apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))

    ms_ver = 'old'
    if ms_ver=='old':
        low_pd = model_LC.MS['old_low']
    else:
        low_pd = model_LC.MS['new_low']
    ratings = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_forced_withquali.append((df_LR[target]==ratings).sum() / len(df_LR))


#%% get current model's mse
data = pd.read_pickle(r'C:\Users\ub71894\Documents\Projects\CNI\src\MFA\train_2016.pkl.xz')
#data.reset_index(drop=True, inplace=True)
data.dropna(subset=model_LC.quali_factor+model_LC.quant_factor, how='any', inplace=True)
data = logitPD_frPDRR(data, model_LC, 'Final_PD_Risk_Rating', ms_ver= 'old')
# log trans
data['size@Total Assets'] = np.log(1+data['size@Total Assets'])
# fill inf
for factor in model_LC.quant_factor:                       
        data[factor] = data[factor].clip(np.nanmin(data[factor][data[factor] != -np.inf]), np.nanmax(data[factor][data[factor] != np.inf]))
data1 = getPDRR(data, model_LC, ms_ver='old')
(data1['Final_PD_Risk_Rating']==data1['Ratings']).sum()


# same quant factors in LR
x_train = sm.add_constant(data1[model_LC.quant_factor], prepend = True)
linear = sm.OLS(data1['logitPD_frPDRR'], x_train, missing='drop')
result = linear.fit(disp=0)
curr_model_inLR = result.mse_resid
list_mse_forced.append(curr_model_inLR)
pds = result.fittedvalues.apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
Ratings = []
ms_ver = 'old'
if ms_ver=='old':
    low_pd = model_LC.MS['old_low']
else:
    low_pd = model_LC.MS['new_low']
ratings = [sum(low_pd<=(x/100)) for x in pds]
list_matchrate_forced.append((data1[target]==ratings).sum() / len(data1))


# current model 
y=data1['logitPD_frPDRR']
yhat= data1.logitPD
curr_model = mean_squared_error(y, yhat)
list_mse_forced_withquali.append(curr_model)
list_matchrate_forced_withquali.append((data1[target]==data1['Ratings']).sum() / len(data1))


df_plot1 = pd.DataFrame()
df_plot1['MSE'] = list_mse_forced
df_plot1['MatchRate'] = list_matchrate_forced
df_plot1['xlim'] = [3,4,5,6,7,8,9,10]
df_plot1['Model'] = 'QuantOnly'
df_plot2 = pd.DataFrame()
df_plot2['MSE'] = list_mse_forced_withquali
df_plot2['MatchRate'] = list_matchrate_forced_withquali
df_plot2['xlim'] = [3,4,5,6,7,8,9,10]
df_plot2['Model'] = 'Quant+FixedQuali'
df_plot = pd.concat([df_plot1, df_plot2], axis=0)

#ax = sns.scatterplot(x="xlim", y="MSE", hue="Model",data=df_plot)
#ax.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9','LC model'])


#ax2 = sns.scatterplot(x="xlim", y="MatchRate", hue="Model",data=df_plot)
#ax2.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9','LC model'])





#%% ML methods
data = pd.read_pickle(r'C:\Users\ub71894\Documents\Projects\CNI\src\MFA\train_2016.pkl.xz')
#data.reset_index(drop=True, inplace=True)
data.dropna(subset=model_LC.quali_factor+model_LC.quant_factor, how='any', inplace=True)
data = logitPD_frPDRR(data, model_LC, 'Final_PD_Risk_Rating', ms_ver= 'old')
# log trans
data['size@Total Assets'] = np.log(1+data['size@Total Assets'])
# fill inf
for factor in model_LC.quant_factor:                       
        data[factor] = data[factor].clip(np.nanmin(data[factor][data[factor] != -np.inf]), np.nanmax(data[factor][data[factor] != np.inf]))
data1 = getPDRR(data, model_LC, ms_ver='old')


from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.svm import LinearSVR
from xgboost.sklearn import XGBRegressor
from sklearn.model_selection import train_test_split, KFold, GridSearchCV, RandomizedSearchCV

X_train = df_norm[pl_cat].copy()
y_train = df_norm['logitPD_frPDRR'].values
y_train_PDRR = df_norm['Final_PD_Risk_Rating'].values

#%% 
gbdt_params = {
'n_estimators':15,
'learning_rate':0.5,
"max_depth":15,
"reg_alpha":0.5
}
rf_params = {
'n_estimators':15,
#'min_samples_split':2,
#'min_samples_leaf':2,
'max_depth':15
}
ms_ver = 'old'
if ms_ver=='old':
    low_pd = model_LC.MS['old_low']
else:
    low_pd = model_LC.MS['new_low']


#%%  quant only
list_mse_quantonly_dt = []
list_mse_quantonly_rt = []
list_mse_quantonly_gbdt = []
list_mse_quantonly_svr = []
list_matchrate_quantonly_dt = []
list_matchrate_quantonly_rt = []
list_matchrate_quantonly_gbdt = []
list_matchrate_quantonly_svr = []
list_model_quantonly = []
for number in range(3,11):
    # select model by feature importance form RandomForest
    sel = SelectFromModel(RandomForestRegressor(n_estimators = 100), threshold=-np.inf, max_features=number)
    sel.fit(X_train, y_train)
    if number<10:
        selected_model = X_train.columns[(sel.get_support())].tolist()
        X_train_selectedmodel = df_norm[selected_model].copy()
    else: # for LC model  
        selected_model = model_LC.quant_factor
        X_train_selectedmodel = data1[selected_model].copy()
        y_train = data1['logitPD_frPDRR']
        y_train_PDRR = data1['Final_PD_Risk_Rating']

    list_model_quantonly.append(selected_model)
    print(f'the seleted model is   {selected_model}')

    model = DecisionTreeRegressor(max_depth=15)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_quantonly_dt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_quantonly_dt.append(accuracy_score(y_train_PDRR, predictions_PDRR))

    model = RandomForestRegressor(**rf_params)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_quantonly_rt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_quantonly_rt.append(accuracy_score(y_train_PDRR, predictions_PDRR))


    model = XGBRegressor(**gbdt_params)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_quantonly_gbdt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_quantonly_gbdt.append(accuracy_score(y_train_PDRR, predictions_PDRR))

    
    model = SVR()
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_quantonly_svr.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_quantonly_svr.append(accuracy_score(y_train_PDRR, predictions_PDRR))



#%%  quant+quali only
X_train = df_norm[pl_cat].copy()
y_train = df_norm['logitPD_frPDRR'].values
y_train_PDRR = df_norm['Final_PD_Risk_Rating'].values


list_mse_full_dt = []
list_mse_full_rt = []
list_mse_full_gbdt = []
list_mse_full_svr = []
list_matchrate_full_dt = []
list_matchrate_full_rt = []
list_matchrate_full_gbdt = []
list_matchrate_full_svr = []

for number in range(3,11):
    # select model by feature importance form RandomForest
    sel = SelectFromModel(RandomForestRegressor(n_estimators = 100), threshold=-np.inf, max_features=number)
    sel.fit(X_train, y_train)
    if number<10:
        selected_model = X_train.columns[(sel.get_support())].tolist()
        X_train_selectedmodel = df_norm[selected_model].copy()
    else:
        selected_model = model_LC.quant_factor + model_LC.quali_factor
        X_train_selectedmodel = data1[selected_model].copy()
        y_train = data1['logitPD_frPDRR']
        y_train_PDRR = data1['Final_PD_Risk_Rating']

    print(f'the seleted model is   {selected_model}')
    

    model = DecisionTreeRegressor(max_depth=15)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_full_dt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_full_dt.append(accuracy_score(y_train_PDRR, predictions_PDRR))

    model = RandomForestRegressor(**rf_params)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_full_rt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_full_rt.append(accuracy_score(y_train_PDRR, predictions_PDRR))


    model = XGBRegressor(**gbdt_params)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_full_gbdt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_full_gbdt.append(accuracy_score(y_train_PDRR, predictions_PDRR))

    
    model = SVR()
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_full_svr.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_full_svr.append(accuracy_score(y_train_PDRR, predictions_PDRR))


df_plot1 = pd.DataFrame()
df_plot1['MSE'] = list_mse_forced
df_plot1['MatchRate'] = list_matchrate_forced
df_plot1['xlim'] = [3,4,5,6,7,8,9,10]
df_plot1['Model'] = 'Scorecard_QuantOnly'
df_plot2 = pd.DataFrame()
df_plot2['MSE'] = list_mse_forced_withquali
df_plot2['MatchRate'] = list_matchrate_forced_withquali
df_plot2['xlim'] = [3,4,5,6,7,8,9,10]
df_plot2['Model'] = 'Scorecard_Full'

df_plot3 = pd.DataFrame()
df_plot3['MSE'] = list_mse_quantonly_dt
df_plot3['MatchRate'] = list_matchrate_quantonly_dt
df_plot3['xlim'] = [3,4,5,6,7,8,9,10]
df_plot3['Model'] = 'DecisionTree_QuantOnly'
df_plot4 = pd.DataFrame()
df_plot4['MSE'] = list_mse_full_dt
df_plot4['MatchRate'] = list_matchrate_full_dt
df_plot4['xlim'] = [3,4,5,6,7,8,9,10]
df_plot4['Model'] = 'DecisionTree_Full'

df_plot5 = pd.DataFrame()
df_plot5['MSE'] = list_mse_quantonly_rt
df_plot5['MatchRate'] = list_matchrate_quantonly_rt
df_plot5['xlim'] = [3,4,5,6,7,8,9,10]
df_plot5['Model'] = 'RandomForest_QuantOnly'
df_plot6 = pd.DataFrame()
df_plot6['MSE'] = list_mse_full_rt
df_plot6['MatchRate'] = list_matchrate_full_rt
df_plot6['xlim'] = [3,4,5,6,7,8,9,10]
df_plot6['Model'] = 'RandomForest_Full'

df_plot7 = pd.DataFrame()
df_plot7['MSE'] = list_mse_quantonly_gbdt
df_plot7['MatchRate'] = list_matchrate_quantonly_gbdt
df_plot7['xlim'] = [3,4,5,6,7,8,9,10]
df_plot7['Model'] = 'GBDT_QuantOnly'
df_plot8 = pd.DataFrame()
df_plot8['MSE'] = list_mse_full_gbdt
df_plot8['MatchRate'] = list_matchrate_full_gbdt
df_plot8['xlim'] = [3,4,5,6,7,8,9,10]
df_plot8['Model'] = 'GBDT_Full'

df_plot9 = pd.DataFrame()
df_plot9['MSE'] = list_mse_quantonly_svr
df_plot9['MatchRate'] = list_matchrate_quantonly_svr
df_plot9['xlim'] = [3,4,5,6,7,8,9,10]
df_plot9['Model'] = 'SupportVector_QuantOnly'
df_plot10 = pd.DataFrame()
df_plot10['MSE'] = list_mse_full_svr
df_plot10['MatchRate'] = list_matchrate_full_svr
df_plot10['xlim'] = [3,4,5,6,7,8,9,10]
df_plot10['Model'] = 'SupportVector_Full'

df_plot = pd.concat([df_plot1, df_plot2, df_plot3, df_plot4, df_plot5,
    df_plot6, df_plot7, df_plot8, df_plot9, df_plot10], axis=0)
df_plot['Type'] = 'based_18_candidates'

ax = sns.scatterplot(x="xlim", y="MSE", hue="Model",data=df_plot)
ax.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9','LC model'])


ax2 = sns.scatterplot(x="xlim", y="MatchRate", hue="Model",data=df_plot)
ax2.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9','LC model'])

































# from 200 candidates:
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% 
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.svm import LinearSVR
from xgboost.sklearn import XGBRegressor
from sklearn.model_selection import train_test_split, KFold, GridSearchCV, RandomizedSearchCV
with open("pl_candidates.txt", "rb") as fp:   # Unpickling
    pl_cat = pickle.load(fp)

X_train = df_norm[pl_cat].copy()
y_train = df_norm['logitPD_frPDRR'].values
y_train_PDRR = df_norm['Final_PD_Risk_Rating'].values

#%% 
gbdt_params = {
'n_estimators':15,
'learning_rate':0.5,
"max_depth":15,
"reg_alpha":0.5
}
rf_params = {
'n_estimators':15,
#'min_samples_split':2,
#'min_samples_leaf':2,
'max_depth':15
}
ms_ver = 'old'
if ms_ver=='old':
    low_pd = model_LC.MS['old_low']
else:
    low_pd = model_LC.MS['new_low']


#%%  quant only
list_mse_quantonly_dt = []
list_mse_quantonly_rt = []
list_mse_quantonly_gbdt = []
list_mse_quantonly_svr = []
list_matchrate_quantonly_dt = []
list_matchrate_quantonly_rt = []
list_matchrate_quantonly_gbdt = []
list_matchrate_quantonly_svr = []
list_model_quantonly=[]
for number in range(3,10):
    # select model by feature importance form RandomForest
    sel = SelectFromModel(RandomForestRegressor(n_estimators = 100), threshold=-np.inf, max_features=number)
    sel.fit(X_train, y_train)

    selected_model = X_train.columns[(sel.get_support())].tolist()
    X_train_selectedmodel = df_norm[selected_model].copy()
    list_model_quantonly.append(selected_model)

    print(f'the seleted model is   {selected_model}')

    model = DecisionTreeRegressor(max_depth=15)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_quantonly_dt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_quantonly_dt.append(accuracy_score(y_train_PDRR, predictions_PDRR))

    model = RandomForestRegressor(**rf_params)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_quantonly_rt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_quantonly_rt.append(accuracy_score(y_train_PDRR, predictions_PDRR))


    model = XGBRegressor(**gbdt_params)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_quantonly_gbdt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_quantonly_gbdt.append(accuracy_score(y_train_PDRR, predictions_PDRR))

    
    model = SVR()
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_quantonly_svr.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_quantonly_svr.append(accuracy_score(y_train_PDRR, predictions_PDRR))



#%%  quant+quali only
X_train = df_norm[pl_cat].copy()
y_train = df_norm['logitPD_frPDRR'].values
y_train_PDRR = df_norm['Final_PD_Risk_Rating'].values


list_mse_full_dt = []
list_mse_full_rt = []
list_mse_full_gbdt = []
list_mse_full_svr = []
list_matchrate_full_dt = []
list_matchrate_full_rt = []
list_matchrate_full_gbdt = []
list_matchrate_full_svr = []
list_model_full=[]

for number in range(3,10):
    # select model by feature importance form RandomForest
    sel = SelectFromModel(RandomForestRegressor(n_estimators = 100), threshold=-np.inf, max_features=number)
    sel.fit(X_train, y_train)

    selected_model = X_train.columns[(sel.get_support())].tolist()
    X_train_selectedmodel = df_norm[selected_model].copy()
    list_model_full.append(selected_model)

    print(f'the seleted model is   {selected_model}')
    

    model = DecisionTreeRegressor(max_depth=15)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_full_dt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_full_dt.append(accuracy_score(y_train_PDRR, predictions_PDRR))

    model = RandomForestRegressor(**rf_params)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_full_rt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_full_rt.append(accuracy_score(y_train_PDRR, predictions_PDRR))


    model = XGBRegressor(**gbdt_params)
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_full_gbdt.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_full_gbdt.append(accuracy_score(y_train_PDRR, predictions_PDRR))

    
    model = SVR()
    model.fit(X_train_selectedmodel, y_train) 
    predictions = model.predict(X_train_selectedmodel)
    list_mse_full_svr.append(mean_squared_error(y_train, predictions))
    pds = pd.Series(predictions).apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    Ratings = []
    predictions_PDRR = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_full_svr.append(accuracy_score(y_train_PDRR, predictions_PDRR))


df_plot3 = pd.DataFrame()
df_plot3['MSE'] = list_mse_quantonly_dt
df_plot3['MatchRate'] = list_matchrate_quantonly_dt
df_plot3['xlim'] = [3,4,5,6,7,8,9]
df_plot3['Model'] = 'DecisionTree_QuantOnly'
df_plot4 = pd.DataFrame()
df_plot4['MSE'] = list_mse_full_dt
df_plot4['MatchRate'] = list_matchrate_full_dt
df_plot4['xlim'] = [3,4,5,6,7,8,9]
df_plot4['Model'] = 'DecisionTree_Full'

df_plot5 = pd.DataFrame()
df_plot5['MSE'] = list_mse_quantonly_rt
df_plot5['MatchRate'] = list_matchrate_quantonly_rt
df_plot5['xlim'] = [3,4,5,6,7,8,9]
df_plot5['Model'] = 'RandomForest_QuantOnly'
df_plot6 = pd.DataFrame()
df_plot6['MSE'] = list_mse_full_rt
df_plot6['MatchRate'] = list_matchrate_full_rt
df_plot6['xlim'] = [3,4,5,6,7,8,9]
df_plot6['Model'] = 'RandomForest_Full'

df_plot7 = pd.DataFrame()
df_plot7['MSE'] = list_mse_quantonly_gbdt
df_plot7['MatchRate'] = list_matchrate_quantonly_gbdt
df_plot7['xlim'] = [3,4,5,6,7,8,9]
df_plot7['Model'] = 'GBDT_QuantOnly'
df_plot8 = pd.DataFrame()
df_plot8['MSE'] = list_mse_full_gbdt
df_plot8['MatchRate'] = list_matchrate_full_gbdt
df_plot8['xlim'] = [3,4,5,6,7,8,9]
df_plot8['Model'] = 'GBDT_Full'

df_plot9 = pd.DataFrame()
df_plot9['MSE'] = list_mse_quantonly_svr
df_plot9['MatchRate'] = list_matchrate_quantonly_svr
df_plot9['xlim'] = [3,4,5,6,7,8,9]
df_plot9['Model'] = 'SupportVector_QuantOnly'
df_plot10 = pd.DataFrame()
df_plot10['MSE'] = list_mse_full_svr
df_plot10['MatchRate'] = list_matchrate_full_svr
df_plot10['xlim'] = [3,4,5,6,7,8,9]
df_plot10['Model'] = 'SupportVector_Full'

df_plot2 = pd.concat([df_plot3, df_plot4, df_plot5,
    df_plot6, df_plot7, df_plot8, df_plot9, df_plot10], axis=0)

df_plot2['Type'] = 'based_all_candidates'

ax = sns.scatterplot(x="xlim", y="MSE", hue="Model",data=df_plot2)
ax.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9'])

ax2 = sns.scatterplot(x="xlim", y="MatchRate", hue="Model",data=df_plot2)
ax2.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9'])



df_plot_combo = pd.concat([df_plot, df_plot2], axis=0)
df_plot_combo.to_pickle(r'df_plot_combo.pkl')


ax3 = sns.scatterplot(x="xlim", y="MatchRate", hue="Model", style="Type", data=df_plot_combo)
ax3.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9','LC'])
ax4 = sns.scatterplot(x="xlim", y="MSE", hue="Model", style="Type", data=df_plot_combo)
ax4.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9','LC'])



markers = {"based_all_candidates": "o", "based_18_candidates": "^"}
ax = sns.scatterplot(x="xlim", y="MSE", hue="Model",style="Type", markers=markers, s=60,data=df_plot_combo)
ax.legend(fancybox=True, framealpha=0.1)
ax.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9','LC'])

ax2 = sns.scatterplot(x="xlim", y="MatchRate", hue="Model",style="Type", markers=markers, s=60, data=df_plot_combo)
ax2.legend(fancybox=True, framealpha=0.1)
ax2.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9','LC'])




#%%
list_model_full = [
['liq@ECE_to_TL', 'size@Net Profit', 'size@Profit before Taxes'],
 ['liq@ECE_to_TL',
  'size@Net Profit',
  'size@Profit before Taxes',
  'size@Total Net Worth'],
 ['liq@ECE_to_TL',
  'prof@NP_exc_EI',
  'size@Net Profit',
  'size@Profit before Taxes',
  'size@Total Net Worth'],
 ['cf@TD_COP',
  'liq@ECE_to_TL',
  'prof@NP_exc_EI',
  'size@Net Profit',
  'size@Profit before Taxes',
  'size@Total Net Worth'],
 ['cf@TD_COP',
  'ds@UBEBITDA_to_IE',
  'liq@ECE_to_TL',
  'prof@NP_exc_EI',
  'size@Net Profit',
  'size@Profit before Taxes',
  'size@Total Net Worth'],
 ['act@NS_to_UBTangNW',
  'cf@TD_COP',
  'ds@UBEBITDA_to_IE',
  'liq@ECE_to_TL',
  'prof@NP_exc_EI',
  'size@Net Profit',
  'size@Profit before Taxes',
  'size@Total Net Worth'],
 ['act@NS_to_UBTangNW',
  'cf@TD_COP',
  'ds@UBEBITDA_to_IE',
  'liq@ECE_to_TL',
  'prof@NP_exc_EI',
  'prof@Net Profit Margin %',
  'size@Net Profit',
  'size@Profit before Taxes',
  'size@Total Net Worth']]


list_mse_MLinLR=[]
list_matchrate_MLinLR = []
#%% interaction

for pl_model in list_model_full:
    poly = PolynomialFeatures(interaction_only=False, include_bias=False)
    data_temp = poly.fit_transform(df_norm[pl_model])
    df = pd.DataFrame(data_temp, columns=poly.get_feature_names(pl_model))
    df.iloc[:,5:] = df.iloc[:,5:].transform(lambda x: 50*(x - x.mean()) / x.std())
    #corr_mat = df.corr()
    
    x_train = sm.add_constant(df, prepend = True)
    linear = sm.OLS(df_norm[target_logitPD], x_train, missing='drop')
    result = linear.fit(disp=0)
    list_mse_MLinLR.append(result.mse_resid)
    
    pds = result.fittedvalues.apply(lambda x: 100*np.exp(x)/(1+np.exp(x)))
    ms_ver = 'old'
    if ms_ver=='old':
        low_pd = model_LC.MS['old_low']
    else:
        low_pd = model_LC.MS['new_low']
    ratings = [sum(low_pd<=(x/100)) for x in pds]
    list_matchrate_MLinLR.append((df_norm[target]==ratings).sum() / len(df_norm))


df_plot_combo = pd.read_pickle(r'df_plot_combo.pkl')

df_plot = pd.DataFrame()
df_plot['MSE'] = list_mse_MLinLR
df_plot['MatchRate'] = list_matchrate_MLinLR
df_plot['xlim'] = [3,4,5,6,7,8,9]
df_plot['Model'] = 'Scorecard_QauntOnly_MLselected'
df_plot['Type'] = 'based_all_candidates'

df_plot_combo2 = pd.concat([df_plot_combo, df_plot], axis=0)
df_plot_combo2.to_pickle(r'df_plot_combo2.pkl')


markers = {"based_all_candidates": "o", "based_18_candidates": "^"}

ax = sns.scatterplot(x="xlim", y="MSE", hue="Model",style="Type", markers=markers, s=60,data=df_plot_combo2)
ax.legend(fancybox=True, framealpha=0.1)
ax.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9','LC'])

ax2 = sns.scatterplot(x="xlim", y="MatchRate", hue="Model",style="Type", markers=markers, s=60, data=df_plot_combo2)
ax2.legend(fancybox=True, framealpha=0.1)
ax2.set(xticklabels=['','model_3','model_4','model_5','model_6','model_7','model_8','model_9','LC'])
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 10:18:56 2020

@author: ub71894
"""
import os, sys, pandas as pd, numpy as np
path = os.getcwd()
if 'ub71894' in path:
    usrid = 'ub71894'
else:
    usrid = 'N304232'
os.chdir(r"C:\Users\{}\Documents\Projects\CNI_redev2".format(usrid))
sys.path.append(r'C:\Users\{}\Documents\DevRepo'.format(usrid))

from PDScorecardTool.Process import SomersD, PD_frPDRR, logitPD_frPDRR
from PDScorecardTool.Process import getPDRR
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.feature_selection import SelectFromModel
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='Set1')
import statsmodels.api as sm
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

import graphviz 
from sklearn import tree
os.environ['PATH'] += os.pathsep + r'C:\Users\ub71894\AppData\Graphviz2.38'
os.environ['PATH'] += os.pathsep + r'C:\Users\ub71894\AppData\Graphviz2.38\bin'



import pickle
filehandler = open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl'.format(usrid),'rb')
model_LC = pickle.load(filehandler)

with open("pl_top_candidates.txt", "rb") as fp:   # Unpickling
    pl_top_candidates = pickle.load(fp)
with open("pl_cat.txt", "rb") as fp:   # Unpickling
    pl_cat = pickle.load(fp)


target = 'Final_PD_Risk_Rating'  # setting
target_logitPD = 'logitPD_frPDRR' 
target_PD = 'PD_frPDRR'  # setting
floor=0.05 # setting
cap=0.95 # setting


df_norm = pd.read_pickle(r'data\df_norm_all.pkl')

X_train = df_norm[pl_cat].copy()
y_train = df_norm['logitPD_frPDRR'].values
y_train_PDRR = df_norm['Final_PD_Risk_Rating'].values


# select model by feature importance form RandomForest
number = 5
sel = SelectFromModel(RandomForestRegressor(n_estimators = 100), threshold=-np.inf, max_features=number)
sel.fit(X_train, y_train)
selected_model = X_train.columns[(sel.get_support())].tolist()
X_train_selectedmodel = df_norm[selected_model].copy()
print(f'the seleted model is   {selected_model}')


# plot the tree
model = DecisionTreeRegressor(max_depth=15)
model.fit(X_train_selectedmodel, y_train) 
dot_data = tree.export_graphviz(model, out_file=None, 
                    feature_names=selected_model,
                    #class_names=['Non-Conservative','Conservative'],
                    filled=True, rounded=True,  
                    special_characters=True)  

graph = graphviz.Source(dot_data) 
graph.render("Tree_5quants")


#%%


pd_core={
'General Industries':'Core',
'Technology':'Core',
'Media and Telecom':'Core',
'Food and Beverage':'Core',
'Retail':'Core',
'Midstream Energy':'Core',
'Engineering and Construction':'Core',
'Trading Asset Reliant':'Core',
'Auto and Auto Parts':'Core',
'Wine Industry':'Core',
}

pd_noncore={
'Commercial Finance Loans':'Non-Core',
'Health Care':'Non-Core',
'Asian Corporate Banking':'Non-Core',
'Commodity Finance':'Non-Core',
'Independent Exploration and Production':'Non-Core',
'Independent Refining':'Non-Core',
'Leasing Companies':'Non-Core',
'Agribusiness':'Non-Core',
'Drilling and Oilfield Services':'Non-Core',
'Corporate Leasing Transactions':'Non-Core',
'Leasing and Asset Finance Division':'Non-Core',
'Institutional Real Estate Lending':'Non-Core',
'Homeowner Association Loans':'Non-Core',
'Placeholder for pending Utilities Latin America':'Non-Core',
'Power & Utilities':'Non-Core',
'Placeholder for pending Metals and Mining Latin America':'Non-Core',
'Entertainment':'Non-Core',
'Insurance':'Non-Core',
'Business Banking':'Non-Core',
'Business Diversity Lending':'Non-Core',
'Investor Perm Loans':'Non-Core',
'Japanese Corporate Banking in Canada':'Non-Core',
'Non-Profit Organizations':'Non-Core',
}import os, sys, pandas as pd, numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(palette='muted')



def cluster_corr(dat, pl_cols):
    pl_cat1 = [pl_cols[0],]
    pl_cat2 = []

    for name in pl_cols[1:]:
        if dat[[name]+pl_cat1].corr().iloc[0,1:].mean() > 0.75:
            pl_cat1.append(name)
        else:
            pl_cat2.append(name)
    if len(pl_cat2)==0:
        return((pl_cat1,))
    else:
        return((pl_cat1,) + cluster_corr(dat, pl_cat2))


def plot_cluster_corr(dat, cat_tuple):
    cols = []
    for cat in cat_tuple:
        cols = cols+cat

    f, ax = plt.subplots(figsize=(10*len(cols)/25, 6*len(cols)/25))
    sns.heatmap(dat[cols].corr(), linewidths=.3, cmap='Blues', ax=ax)


def quanttrans(data, model, floor=0.05, cap=0.95):
    """
    This function calculates the floor, cap, mean and std of the data. The output
    can be used as the updated parameters for quantitative factors normailization.
    Modified in Ver. 1.4

    Parameters:

        data:   the input dataset in DataFrame. Make sure no NA in quant
                factors

        model:  PDModel class

        floor:  float, default 0.05
                quantile for floor 

        cap:    float, default 0.95
                quantile for cap 

        
    Return:
        a dictionary that saves floor, cap, doc_mean, doc_std
    
    """    
    normdata = data.copy()


    # get new cap and floor from valid observations:
    floor_list=[];  cap_list=[]

    for i, factor in enumerate(model.quant_factor):
        if not model.Invalid_Neg[i]:
            floor_list.append(normdata[factor].quantile(floor))
            cap_list.append(normdata[factor].quantile(cap))
        else:
            floor_list.append(normdata[factor][normdata[factor]>0].quantile(floor))
            cap_list.append(normdata[factor][normdata[factor]>0].quantile(cap))


    # Invalid_Neg
    for i,neg in enumerate(model.Invalid_Neg):
        if neg:
            col=model.quant_factor[i]
            normdata[col][normdata[col]<0] = cap_list[i]
           
    # cap/floor for quant factors:
    for i, col in enumerate(model.quant_factor):
        normdata[col] = np.clip(normdata[col], floor_list[i], cap_list[i])        

    # quant factors transformation:
    for i, col in enumerate(model.quant_factor):
        if model.quant_log[i]:
            normdata[col] = np.log(normdata[col])

    # get new mean and std:
    doc_mean=[];    doc_std=[]

    for i, col in enumerate(model.quant_factor):
        doc_mean.append(normdata[col].mean())     
        doc_std.append(normdata[col].std())     

    dictionary = {'floor':floor_list, 'cap':cap_list, 'doc_mean':doc_mean, 'doc_std':doc_std}
    
    return(dictionary)


['01_prelim_analysis.py', '02_re_mfa.py', '03_get_multifactor_models.py', '03_get_normdataforallfactors.py', '04_compare_models.py', '05_plot_tree.py', 'core_list.py', 'newfunc.py']
[318, 488, 912, 1224, 2012, 2093, 2132, 2228]
