# -*- coding: utf-8 -*-
"""
Created on Mon Jun 19 14:55:06 2017

Process capital call timing and rate data and save them in pickle data

original part is in file dev_0_timeg.py

@author: ub71894 (4e8e6d0b), CSG
"""


import os, pandas as pd, datetime as dt, numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import time
from numba import jit
sns.set(style="white", palette="muted", color_codes=True)
os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")


#%% 
data = pd.read_excel(r'../data/capital_call_date.xlsx', sheetname='Consolidated')
data.rename(columns={'% of Total Commitment':'Total_CCR'}, inplace=True)
# delete distribution records
data = data.query('Total_CCR>=0')
names = list(set(data.Fund))
data['year'] = [x.year for x in data['Date of Capital Call']]
data['count'] = 1



#%%
initialdeltas=[];   timedeltas=[]
fundtype_ini=[];    fundtype_later=[]

for name in names:
    df = data.query('Fund=="{name}"'.format(name=name))
    # some loan's timeline is not sorted.
    df.sort_values(by='Date of Capital Call', inplace=True)

    # get the increment and convert to year
    initialdeltas += [(df['Date of Capital Call'].iloc[0]-df['Start Date (Credit Agreement)'].iloc[0]).days/365]
    fundtype_ini += [df['Type of Fund'].iloc[0]]

    deltas_of_this_fund = [x.days/365 for x in df['Date of Capital Call'].diff().dropna()]
    timedeltas += deltas_of_this_fund
    fundtype_later += len(deltas_of_this_fund)*[df['Type of Fund'].iloc[0]]


#%% delta_t
initial = pd.DataFrame()
initial['delta_t'] = initialdeltas
initial['type'] = fundtype_ini
# remove outliers:
initial = initial.query("delta_t<5.5")
initial = initial.query("delta_t>0")
initial.reset_index(drop=True, inplace=True)
initial.groupby(by='type').mean()



#%%
later = pd.DataFrame()
later['delta_t'] = timedeltas
later['type'] = fundtype_later
later.groupby(by='type').mean()







#%% save data
temp = initial['delta_t']
temp.to_pickle('hist_init_t.pickle')

timedeltas = later['delta_t']
timedeltas.drop_duplicates(inplace=True)
timedeltas.to_pickle('hist_latter_t.pickle')


hist_cc=data['Total_CCR']
hist_cc.dropna(inplace=True)
hist_cc.drop_duplicates(inplace=True)
hist_cc.to_pickle('hist_cc.pickle')
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 15:07:58 2017

Calculate CT from historic data

@author: ub71894 (4e8e6d0b), CSG
"""


import os, pandas as pd, numpy as np

os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')


#%% first naive try
data = pd.read_excel('../data/data_for_CT.xlsx')

data['WAPD'] = pd.to_numeric(data['WAPD'],errors='coerce')
data.dropna(subset=['WAPD'], inplace=True)
data['WAPD2'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['WAPD'] ]
data['WAPD2'].mean()
#0.0014736842105263163





#%% get mean PD from all loans
filenames = []
for root, dirs, files in os.walk('..\data\daily2'):
    for name in files:
        filenames.append(name)

re=pd.DataFrame()
for i,file in enumerate(filenames):
    filename = '../data/daily2/'+file
    dat =  pd.read_excel(filename, sheetname='Current')
    val_mask = dat['RC(s) Selected:']=='Officer Name + Number'
    skiprows = dat['RC(s) Selected:'][val_mask].index[0]+2
    
    data = pd.read_excel(filename, sheetname='Current', skiprows=skiprows)
    data['WAPD'] = pd.to_numeric(data['WAPD'],errors='coerce')
    data.dropna(subset=['WAPD'], inplace=True)
    data['WAPD2'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['WAPD'] ]
    # drop last row which is the average
    data = data.iloc[:-1,:]

    re = pd.concat([re,data])
    print(data['WAPD2'].mean())

re['WAPD2'].mean()





#%% detect which doesn't have LGD
filenames = []
for root, dirs, files in os.walk('..\data\daily2'):
    for name in files:
        filenames.append(name)

nolgd=[]
for i,file in enumerate(filenames):
    filename = '../data/daily2/'+file
    dat =  pd.read_excel(filename, sheetname='Current')
    val_mask = dat['RC(s) Selected:']=='Officer Name + Number'
    skiprows = dat['RC(s) Selected:'][val_mask].index[0]+2
    
    data = pd.read_excel(filename, sheetname='Current', skiprows=skiprows)
    if 'LGD Risk Rating'  in data.columns.tolist():
        pass
    else:
        nolgd.append(file)
nolgd



#%% get mean PD from subscription only loans

filenames = []
for root, dirs, files in os.walk('..\data\daily3'):
    for name in files:
        filenames.append(name)

re=pd.DataFrame()
for i,file in enumerate(filenames):
    filename = '../data/daily3/'+file
    dat =  pd.read_excel(filename, sheetname='Current')
    val_mask = dat['RC(s) Selected:']=='Officer Name + Number'
    skiprows = dat['RC(s) Selected:'][val_mask].index[0]+2
    
    data = pd.read_excel(filename, sheetname='Current', skiprows=skiprows)
    data = data[data['LGD Risk Rating']!="I"]
    data['WAPD'] = pd.to_numeric(data['WAPD'],errors='coerce')
    data.dropna(subset=['WAPD'], inplace=True)
    data['WAPD2'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['WAPD'] ]
    # drop last row which is the average
    data = data.iloc[:-1,:]
    re = pd.concat([re,data])
    print(data['WAPD2'].mean())

re['WAPD2'].mean()





#%% get mean PD from subscription only loans

import dateutil.parser as dparser
 

filenames = []
for root, dirs, files in os.walk('..\data\daily3'):
    for name in files:
        filenames.append(name)

re=pd.DataFrame()
for i,file in enumerate(filenames):
    filename = '../data/daily3/'+file
    timestamp = dparser.parse(file,fuzzy=True)
    dat =  pd.read_excel(filename, sheetname='Current')
    val_mask = dat['RC(s) Selected:']=='Officer Name + Number'
    skiprows = dat['RC(s) Selected:'][val_mask].index[0]+2
    
    data = pd.read_excel(filename, sheetname='Current', skiprows=skiprows)
    #data = data[data['LGD Risk Rating']!="I"]
    data['WAPD'] = pd.to_numeric(data['WAPD'],errors='coerce')
    data.dropna(subset=['WAPD'], inplace=True)
    data['WAPD2'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['WAPD'] ]
    # drop last row which is the average
    data = data.iloc[:-1,:]
    data['timestamp'] = timestamp
    re = pd.concat([re,data])
    print(data['WAPD2'].mean())

re = re[[
 'Commitment',
 'Country Code',
 'Customer Name + Number',
 'LGD Risk Rating',
 'Outstanding',
 'WAPD',
 'WAPD2',
 'timestamp']
]
re.sort_values(by=['Customer Name + Number','timestamp'], inplace=True)
re.drop_duplicates(subset=['Customer Name + Number'], keep='last', inplace=True)

# mean withou adjusting Bridge loans:
re['WAPD'].mean()
#4.190909
re['WAPD2'].mean()
#0.0015336363636363638


# mean with adjusting Bridge loans:
re_adj = re.copy()
re_adj.loc[re_adj['LGD Risk Rating']=='I','WAPD'] = re_adj.loc[re_adj['LGD Risk Rating']=='I','WAPD'] -1
re_adj['WAPD2'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in re_adj['WAPD'] ]

re_adj['WAPD'].mean()
#4.072727272727272
re_adj['WAPD2'].mean()
#0.0014336363636363644

#%%
re.to_pickle('1year.pickle')
re_adj.to_pickle('1year_adj.pickle')
re.to_excel('1year.xlsx')
re_adj.to_excel('1year_adj.xlsx')







#%% get mean PD from all but upgrading Bridge loans 1 notch, 20160916

filenames = []
for root, dirs, files in os.walk('..\data\daily3'):
    for name in files:
        filenames.append(name)

re=pd.DataFrame()
for i,file in enumerate(filenames):
    filename = '../data/daily3/'+file
    dat =  pd.read_excel(filename, sheetname='Current')
    val_mask = dat['RC(s) Selected:']=='Officer Name + Number'
    skiprows = dat['RC(s) Selected:'][val_mask].index[0]+2
    
    data = pd.read_excel(filename, sheetname='Current', skiprows=skiprows)
    data['WAPD'] = pd.to_numeric(data['WAPD'],errors='coerce')
    data.dropna(subset=['WAPD'], inplace=True)

    data.loc[data['LGD Risk Rating']=='I','WAPD'] = data.loc[data['LGD Risk Rating']=='I','WAPD'] -1

    data['WAPD2'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['WAPD'] ]
    # drop last row which is the average
    data = data.iloc[:-1,:]
    re = pd.concat([re,data])
    print(data['WAPD2'].mean())
    
re.rename(columns={'Customer Name + Number':'FundName'}, inplace=True)
re=re.query('FundName!="ARES CAPITAL CORPORATION 205033447" ')
re=re.query('FundName!="ARES HOLDINGS L.P. 208450407"')
re=re.query('FundName!="KAYNE ANDERSON CAPITAL ADVISORS, LP 205197810"' )
re=re.query('FundName!="OAKTREE CAPITAL MANAGEMENT LP 205506618"')

re['WAPD2'].mean()
#0.0014223385689354083
re['WAPD'].mean()
#4.041012216404886




#%% get mean PD from PDRR(2-6) but upgrading Bridge loans 1 notch, 20160917

filenames = []
for root, dirs, files in os.walk('..\data\daily3'):
    for name in files:
        filenames.append(name)

re=pd.DataFrame()
for i,file in enumerate(filenames):
    filename = '../data/daily3/'+file
    dat =  pd.read_excel(filename, sheetname='Current')
    val_mask = dat['RC(s) Selected:']=='Officer Name + Number'
    skiprows = dat['RC(s) Selected:'][val_mask].index[0]+2
    
    data = pd.read_excel(filename, sheetname='Current', skiprows=skiprows)
    data['WAPD'] = pd.to_numeric(data['WAPD'],errors='coerce')
    data.dropna(subset=['WAPD'], inplace=True)

    data.loc[data['LGD Risk Rating']=='I','WAPD'] = data.loc[data['LGD Risk Rating']=='I','WAPD'] -1

    data['WAPD2'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['WAPD'] ]
    # drop last row which is the average
    data = data.iloc[:-1,:]
    data = data[data['WAPD']<=6]
    re = pd.concat([re,data])
    print(data['WAPD2'].mean())

re.rename(columns={'Customer Name + Number':'FundName'}, inplace=True)
re=re.query('FundName!="ARES CAPITAL CORPORATION 205033447" ')
re=re.query('FundName!="ARES HOLDINGS L.P. 208450407"')
re=re.query('FundName!="KAYNE ANDERSON CAPITAL ADVISORS, LP 205197810"' )
re=re.query('FundName!="OAKTREE CAPITAL MANAGEMENT LP 205506618"')

re['WAPD2'].mean()
#0.000884936831875613
re['WAPD'].mean()
#3.611273080660836# -*- coding: utf-8 -*-
"""
Created on Thu Fri Aug 15 11:52:00 2017

Read structure data and fill NA in col 'S&PRating' by the rule shown in comments
of line 17-21
@author: ub71894 (4e8e6d0b), CSG
"""


import os, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")
strucdata = pd.read_excel('../data/StructureFile.xlsx', sheetname='insample')


strucdata['SPR'] = strucdata['S&PRating'].copy()
strucdata1 = strucdata.query('SPR=="NR" and Individuals=="N"') # PDRR 8
strucdata2 = strucdata.query('SPR=="NR" and Individuals=="Y"') # PDRR 13
strucdata3 = strucdata.query('SPR=="NR" and Individuals=="U"') # PDRR 13
strucdata4 = strucdata.query('SPR=="NR" and Individuals=="P"') # PDRR 11
strucdata5 = strucdata.query('SPR=="NRNI"') # PDRR 13
strucdata6 = strucdata.query('SPR!="NRNI" and SPR!="NR"')

strucdata1['S&PRating']= 'BB+'
strucdata2['S&PRating']= 'B'
strucdata3['S&PRating']= 'B'
strucdata4['S&PRating']= 'BB-'
strucdata5['S&PRating']= 'B'

strucdata['S&PRating'].describe()
strucdata= pd.concat([strucdata1,strucdata2,strucdata3,strucdata4,strucdata5,strucdata6], axis=0)
strucdata.sort_values(by='FundName', inplace=True)
strucdata.reset_index(drop=True, inplace=True)

#funds = pd.read_excel('../data/Funds_0811.xlsx')
#funds = funds[['FundName','Institutional']].copy()
#strucdata = pd.merge(strucdata, funds, on='FundName', how='inner')
strucdata['FundsFinancePreliminaryPDRR'].fillna('NotSpecified', inplace=True)
strucdata['FundsFinanceFinalPDRR'].fillna('NotSpecified', inplace=True)
strucdata['MinimumApplicableS&PRating'].fillna('NotSpecified', inplace=True)
strucdata.to_pickle('strucdata.pickle')
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 15:56:14 2017

Organized MC script. original is from dev_1_MC_6.py

@author: ub71894 (4e8e6d0b), CSG
"""

import os, pandas as pd, numpy as np
from scipy.stats import norm
from numba import jit
import time
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style="white", palette="muted", color_codes=True)
os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")
from FFMC import gen_delta_t, gen_cc, gen_def, load_loan_info, SomersD

ms = pd.read_pickle('ms.pickle')
strucdata = pd.read_pickle('strucdata.pickle')
hist_init_t_all = pd.read_pickle('hist_init_t.pickle')
hist_latter_t = pd.read_pickle('hist_latter_t.pickle')
hist_cc = pd.read_pickle('hist_cc.pickle')
names = set(strucdata.FundName)

# remove 8 loans which have no current PDRR
toremove = set(['GS Mezz VI',
 'Hines Poland Sustainable Income Fund (EURO)',
 'TPG Capital Partners',
 'Carmel V',
 'GSO COF III',
 'MS Asia IV',
 'H2 Core RE Debt Fund',
 'American RE Partners II'])
names = list(names-toremove)




#%% Run MC 
start_time = time.time()
N=10000   # total number of MC is 10000*50 = 500,000
rho = 0.66  # which will match target CT = 9.2 bps   
usage=1 # for conservativeness, we use usage=1 at all points
loan_def_per10k=[]

np.random.seed(2018) # fixed random seed. convinient for validation and check.

for loan in names:

    loan_info = load_loan_info(strucdata, loan, ms)
    tenor = loan_info['tenor']
    # construct init t sample based on tenor
    hist_init_t = hist_init_t_all.loc[hist_init_t_all<tenor]
    total_commit = loan_info['total_commit']
    investors_pd = loan_info['investors_pd']
    investors_pct = loan_info['investors_pct']
    #investors_adrate = loan_info['investors_adrate']
    facility_size = loan_info['facility_size']
    weighted_adrate = loan_info['weighted_adrate']  
    
    ##########################  

    ss=[];  ss_yr=[]    

    for path in range(50):  

        delta_t, tau = gen_delta_t(hist_init_t, hist_latter_t, N, tenor)
        tccr, rccr = gen_cc(hist_cc, delta_t)
        def_flag = gen_def(N, tau, investors_pd, tccr, delta_t, rho, amplitude=1, gamma=0)    

        s=0;  s_yr=0;   ind=[]
        for i in range(N):
            for t in range(tau[i]):
                rcc = total_commit*rccr[i,t] # remaining capital call
                bb = rcc * weighted_adrate   # borrowing base
                outstanding = min(bb, facility_size) * usage # outstanding or bank exposure
                undefpct = np.dot(investors_pct, (1-def_flag[i,t,:]))
                rucc = rcc*undefpct
                if outstanding > rucc:
                    s += 1 
                    #s_yr += 1/np.sum(delta_t[i,:(t+1)])
                    ind.append((i,t))
                    break
        s = s/tenor
        ss.append(s)     
        #ss_yr.append(s_yr)
        
    loan_def_per10k.append(np.mean(ss))

print("--- %s seconds ---" % (time.time() - start_time))
                      
#%%
np.mean(loan_def_per10k)/10000


#%%
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
funds = pd.read_excel(r'C:\Users\ub71894\Documents\Projects\FFS\data\Funds_0821.xlsx')
final_pd=[]; final_PDRR=[]; types=[]

for loan in names:  
        # load loan info
        loan_info = load_loan_info(strucdata, loan, ms)       
        final_rating = loan_info['final_rating']         
        ifinal_pd = MS.query("PDRR=={final_rating}".format(final_rating=final_rating))['new_mid'].values[0]    
        final_pd.append(ifinal_pd) 
        final_PDRR.append(final_rating)
        types.append(funds.query('FundName=="{}"'.format(loan))['DealType'].values[0])
        
df = pd.DataFrame()
df['FundName'] =names
df['type'] = types
df['MC_pd'] = loan_def_per10k
df['MC_pd'] = df['MC_pd']/10000
df['final_pd'] = final_pd

Ratings = []
for i in df.iterrows():
    Ratings.append(sum(MS['new_low']<=(i[1].MC_pd)))

df['MC_PDRR'] = Ratings
df['final_PDRR'] = final_PDRR
df['rating_diff'] = abs(df['MC_PDRR'] - df['final_PDRR'])


# then we summarized all result and save it into pickle data
df.to_pickle('result_info3_66.pickle')




# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 15:56:14 2017

Organized MC script. original is from dev_1_MC_6.py

@author: ub71894 (4e8e6d0b), CSG
"""

import os, pandas as pd, numpy as np
from scipy.stats import norm
from numba import jit
import time
import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style="white", palette="muted", color_codes=True)
os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")
from FFMC import gen_delta_t, gen_cc, gen_def, load_loan_info, SomersD

ms = pd.read_pickle('ms.pickle')
strucdata = pd.read_pickle('strucdata.pickle')
hist_init_t_all = pd.read_pickle('hist_init_t.pickle')
hist_latter_t = pd.read_pickle('hist_latter_t.pickle')
hist_cc = pd.read_pickle('hist_cc.pickle')
names = set(strucdata.FundName)

# remove 8 loans which have no current PDRR
toremove = set(['GS Mezz VI',
 'Hines Poland Sustainable Income Fund (EURO)',
 'TPG Capital Partners',
 'Carmel V',
 'GSO COF III',
 'MS Asia IV',
 'H2 Core RE Debt Fund',
 'American RE Partners II'])
names = list(names-toremove)




#%% Run MC 
start_time = time.time()
N=10000   # total number of MC is 10000*50 = 500,000
rho = 0.66  # which will match target CT = 9.2 bps   
usage=1 # for conservativeness, we use usage=1 at all points
loan_def_per10k=[]
recovery_ratio={} #  add in 20180313  
np.random.seed(2018) # fixed random seed. convinient for validation and check.

for loan in names:

    loan_info = load_loan_info(strucdata, loan, ms)
    tenor = loan_info['tenor']
    # construct init t sample based on tenor
    hist_init_t = hist_init_t_all.loc[hist_init_t_all<tenor]
    total_commit = loan_info['total_commit']
    investors_pd = loan_info['investors_pd']
    investors_pct = loan_info['investors_pct']
    #investors_adrate = loan_info['investors_adrate']
    facility_size = loan_info['facility_size']
    weighted_adrate = loan_info['weighted_adrate']  
    
    ##########################  

    ss=[];  ss_yr=[] ; ratio=[] # add in 20180313  

    for path in range(50):  

        delta_t, tau = gen_delta_t(hist_init_t, hist_latter_t, N, tenor)
        tccr, rccr = gen_cc(hist_cc, delta_t)
        def_flag = gen_def(N, tau, investors_pd, tccr, delta_t, rho, amplitude=1, gamma=0)    

        s=0;  s_yr=0;   ind=[];     
        for i in range(N):
            for t in range(tau[i]):
                rcc = total_commit*rccr[i,t] # remaining capital call
                bb = rcc * weighted_adrate   # borrowing base
                outstanding = min(bb, facility_size) * usage # outstanding or bank exposure
                undefpct = np.dot(investors_pct, (1-def_flag[i,t,:]))
                rucc = rcc*undefpct
                if outstanding > rucc:
                    s += 1 
                    #s_yr += 1/np.sum(delta_t[i,:(t+1)])
                    #ind.append((i,t))
                    ratio.append(rucc/outstanding)
                    break
        s = s/tenor
        ss.append(s) 
        
        #ss_yr.append(s_yr)
        
    loan_def_per10k.append(np.mean(ss))
    recovery_ratio.update({loan:ratio})
print("--- %s seconds ---" % (time.time() - start_time))
np.save('recovery_ratio.npy', recovery_ratio)               
#%%

all_ratios = []
for value in recovery_ratio.values():
    all_ratios +=value
np.mean(all_ratios)
# remove all single investor
all_ratios2 = [x for x in all_ratios if x > 0.0]
np.mean(all_ratios2)


np.mean(loan_def_per10k)/10000


#%%
all_ratios = []
for value in recovery_ratio.values():
    all_ratios +=value

np.mean(all_ratios)
Out[51]: 0.59176970178475463

all_ratios2 = [x for x in all_ratios if x > 0.0]

np.mean(all_ratios2)
Out[53]: 0.753586344019191# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 13:15:21 2017

@author: ub71894 (4e8e6d0b), CSG
"""

import os, pandas as pd, numpy as np
import statsmodels.api as sm 
os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")
from FFMC import SomersD
import time
from itertools import combinations, product
import sys
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix

#%%
def modelSD(data, factors, y_col, PDRR, signs=False, weights=False):
    '''
    if weight is not assigned, it will run linear regression to get weight,
    then use weight to estimated PD and PDRR, then calculate SomersD bewteen 
    input PDRR and estimated PDRR
    if weight is assigned, it will use it to get total score then run linear regression
    to get estimated PD and PDRR, then calculate SomersD bewteen input PDRR and estimated PDRR

    '''
    dat = data[factors].copy()
    y = data[y_col].copy()
    inde = sm.add_constant(dat, prepend = True)
    res = sm.OLS(y, inde).fit()
    if not signs:
        signs = []
        for factor in factors:
            signs.append(np.sign(res.params[factor]))

    for i,col in enumerate(factors):
        dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()

    if weights:
        dat['score'] = (weights * dat[factors].values).sum(axis=1)
        inde = sm.add_constant(dat['score'], prepend = True)
        res = sm.OLS(y, inde).fit()
        fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
        Ratings = []
        for i in fitted_pd:
            Ratings.append(sum(MS['new_low']<=i))

        return(weights, signs, SomersD(data[PDRR], Ratings))

    else:
        inde = sm.add_constant(dat, prepend = True)
        res = sm.OLS(y, inde).fit()
        coeff = res.params.iloc[1:]
        coeffsum = coeff.sum()
        weights = [x/coeffsum for x in res.params.iloc[1:]]
        fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
        Ratings = []
        for i in fitted_pd:
            Ratings.append(sum(MS['new_low']<=i))

        return(res, weights, signs, SomersD(data[PDRR], Ratings))


def scorecard(data, factors, signs, y_col, weights):
    '''
    Apply determinated weight and sign to calculated new columns:
    'total_score', 'fitted_logit_pd','fitted_pd' and 'fitted_PDRR'
    then return the new DataFrame

    '''
    dat = data.copy()
    for i,col in enumerate(factors):
        dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()

    dat['total_score'] = (weights * dat[factors].values).sum(axis=1)

    y = data[y_col].copy()
    inde = sm.add_constant(dat['total_score'], prepend = True)
    res = sm.OLS(y, inde).fit()
    dat['fitted_logit_pd'] = res.fittedvalues
    dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat['fitted_logit_pd'] ]

    Ratings = []
    for i in dat.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd)))
    dat['fitted_PDRR'] = Ratings   
    return(dat)




#%% load data and modify some of them:
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
toremove = ['GS Mezz VI','Hines Poland Sustainable Income Fund (EURO)',
'TPG Capital Partners','Carmel V','GSO COF III','MS Asia IV',
'H2 Core RE Debt Fund','American RE Partners II']
# read MC result
mc = pd.read_pickle('result_info3_66.pickle')
mc = mc[['FundName','MC_pd','MC_PDRR']]

# read Business suggested PDRR
mix = pd.read_excel('MC_results.xlsx')
mix = mix[['names','Business suggested PDRR']]
mix.rename(columns={'names':'FundName'}, inplace=True)
mix = mix[~mix['FundName'].isin(toremove)]
mix['mix_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in mix['Business suggested PDRR'] ]
mix['logit_mix_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in mix['mix_pd'] ]

# read current model and fund data
dat = pd.read_excel('..\data\Funds_0821.xlsx')
data = dat[~dat['FundName'].isin(toremove)]
# transformation
data['Institutional'].replace({'I':1,'NI':0}, inplace=True)
data['MandatoryPrepayment'].replace({'Y':1,'N':0}, inplace=True)
data['DealType'].replace({'Subscription':1,'Bridge':0}, inplace=True)
data['CreditQuality'].replace({'Excellent':1, 'Average':2, 'Below Average':3}, inplace=True)
data['BB-FS'] = data['EffectiveAdvanceRate']* data['FundCommitment'] / data['FacilitySize']

data['FundBorrowingBase'] = [np.log(x) for x in data['FundBorrowingBase']]
data['FundUnpaidCommitment'] = [np.log(x) for x in data['FundUnpaidCommitment']]
data['FundCommitment'] = [np.log(x) for x in data['FundCommitment']]
data['FacilitySize'] = [np.log(x) for x in data['FacilitySize']]
data['TotalAssets'].fillna(data['TotalAssets'].min(), inplace=True)
data['TotalAssets'] = [np.log(x) for x in data['TotalAssets']]
data['TotalAssets+UnpaidCommitment'].fillna(data['TotalAssets+UnpaidCommitment'].min(), inplace=True)
data['TotalAssets+UnpaidCommitment'] = [np.log(x) for x in data['TotalAssets+UnpaidCommitment']]
data['PartnerCapital'].fillna(data['PartnerCapital'].min(), inplace=True)
data['PartnerCapital'][data['PartnerCapital']<=0] =1
data['PartnerCapital'] = [np.log(x) for x in data['PartnerCapital']]
data['NumberOfIncluded_120'] = np.clip(data['NumberOfIncluded'], -10, 120) 
data['NumberOfInvestors_120'] = np.clip(data['NumberOfInvestors'], -10, 120)  

data['final_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['FundsFinanceFinalPDRR'] ]
data['final_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['FundsFinanceFinalPDRR'] ]
data['logit_final_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in data['final_pd'] ]
# merge them together
data = pd.merge(data, mc, on='FundName', how='inner')
data = pd.merge(data, mix, on='FundName', how='inner')
data['logit_MC_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in data['MC_pd'] ]




#%%  2.
factors = ['CC_HHI', 'BB-FS', 'FundCommitment','CreditQuality', 'Institutional', 'Overcapitalization']
signs =  [1.0, -1.0, -1.0, 1.0, -1.0, -1.0]
y_col = 'logit_mix_pd'
PDRR = 'Business suggested PDRR'



weights_1 = [0.02,  0.22, 0.06,  0.15, 0.38, 0.17]
weights_2 = [0.05,  0.20, 0.05,  0.15, 0.35, 0.20]
weights_3 = [0.01,  0.22, 0.05,  0.20, 0.35, 0.17]
weights_4 = [0.05,  0.20, 0.05,  0.20, 0.35, 0.15] # chosen model so far


temp_1 = modelSD(data, factors, y_col, PDRR, signs, weights=weights_1)
temp_2 = modelSD(data, factors, y_col, PDRR, signs, weights=weights_2)
temp_3 = modelSD(data, factors, y_col, PDRR, signs, weights=weights_3)
temp_4 = modelSD(data, factors, y_col, PDRR, signs, weights=weights_4)




scorecard_1 = scorecard(data, factors, signs, y_col, weights_1)
SomersD(scorecard_1['Business suggested PDRR'], scorecard_1.fitted_PDRR)

scorecard_2 = scorecard(data, factors, signs, y_col, weights_2)
SomersD(scorecard_2['Business suggested PDRR'], scorecard_2.fitted_PDRR)

scorecard_3 = scorecard(data, factors, signs, y_col, weights_3)
SomersD(scorecard_3['Business suggested PDRR'], scorecard_3.fitted_PDRR)

scorecard_4 = scorecard(data, factors, signs, y_col, weights_4)
SomersD(scorecard_4['Business suggested PDRR'], scorecard_4.fitted_PDRR)






#%% temp analysis on 3 examples
result_1 = scorecard_1[['FundName', 'Business suggested PDRR','fitted_PDRR' ]].\
query('FundName=="Energy Capital Partners III" or FundName=="GIP III" or FundName=="Starwood Opps Fund X"')

result_2 = scorecard_2[['FundName', 'Business suggested PDRR','fitted_PDRR' ]].\
query('FundName=="Energy Capital Partners III" or FundName=="GIP III" or FundName=="Starwood Opps Fund X"')

result_3 = scorecard_3[['FundName', 'Business suggested PDRR','fitted_PDRR' ]].\
query('FundName=="Energy Capital Partners III" or FundName=="GIP III" or FundName=="Starwood Opps Fund X"')

result_4 = scorecard_4[['FundName', 'Business suggested PDRR','fitted_PDRR' ]].\
query('FundName=="Energy Capital Partners III" or FundName=="GIP III" or FundName=="Starwood Opps Fund X"')

# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 10:33:20 2017

More functions which were used in development are in dev_2_calibration.py. 

@author: ub71894 (4e8e6d0b), CSG
"""


import os, pandas as pd, numpy as np
import statsmodels.api as sm 
import statsmodels.formula.api as smf
os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")
from FFMC import SomersD
import sys
import copy
from scipy.optimize import fsolve
import seaborn as sns
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import matplotlib.pyplot as plt


#%%
def modelSD(data, factors, y_col, PDRR, signs=False, weights=False):
    '''
    if weight is not assigned, it will run linear regression to get weight,
    then use weight to estimated PD and PDRR, then calculate SomersD bewteen 
    input PDRR and estimated PDRR
    if weight is assigned, it will use it to get total score then run linear regression
    to get estimated PD and PDRR, then calculate SomersD bewteen input PDRR and estimated PDRR

    '''
    dat = data[factors].copy()
    y = data[y_col].copy()
    inde = sm.add_constant(dat, prepend = True)
    res = sm.OLS(y, inde).fit()
    if not signs:
        signs = []
        for factor in factors:
            signs.append(np.sign(res.params[factor]))

    for i,col in enumerate(factors):
        dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()

    if weights:
        dat['score'] = (weights * dat[factors].values).sum(axis=1)
        inde = sm.add_constant(dat['score'], prepend = True)
        res = sm.OLS(y, inde).fit()
        fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
        Ratings = []
        for i in fitted_pd:
            Ratings.append(sum(MS['new_low']<=i))

        return(weights, signs, SomersD(data[PDRR], Ratings))

    else:
        inde = sm.add_constant(dat, prepend = True)
        res = sm.OLS(y, inde).fit()
        coeff = res.params.iloc[1:]
        coeffsum = coeff.sum()
        weights = [x/coeffsum for x in res.params.iloc[1:]]
        fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
        Ratings = []
        for i in fitted_pd:
            Ratings.append(sum(MS['new_low']<=i))

        return(res, weights, signs, SomersD(data[PDRR], Ratings))


def scorecard(data, factors, signs, y_col, weights, norm_by_preset=False, means=None, stds=None):
    '''
    Apply determinated weight and sign to calculated new columns:
    'total_score', 'fitted_logit_pd','fitted_pd' and 'fitted_PDRR'
    then return the new DataFrame

    '''
    dat = data.copy()
    if norm_by_preset:
        for i,col in enumerate(factors):
            dat[col]  = signs[i]*50*(dat[col] - means[i] ) / stds[i]
    else:
        for i,col in enumerate(factors):
            dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()

    dat['total_score'] = (weights * dat[factors].values).sum(axis=1)

    y = data[y_col].copy()
    inde = sm.add_constant(dat['total_score'], prepend = True)
    res = sm.OLS(y, inde).fit()
    dat['fitted_logit_pd'] = res.fittedvalues
    dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat['fitted_logit_pd'] ]

    Ratings = []
    for i in dat.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd)))
    dat['fitted_PDRR'] = Ratings   
    return(dat)






def SegLR(data, cutoff_score, cutoff_logit_PD):

    data1 = data.query('total_score<=@cutoff_score')
    data2 = data.query('total_score>@cutoff_score')
    res1 = smf.ols(formula='I(logit_mix_pd-cutoff_logit_PD) ~ I(total_score-cutoff_score)+0', data=data1).fit()
    res2 = smf.ols(formula='I(logit_mix_pd-cutoff_logit_PD) ~ I(total_score-cutoff_score)+0', data=data2).fit()

    temp = {'cutoff_score':[],'cutoff_PD':[],'totalSSR':[],'Intercept1':[],'Intercept2':[],'slope1':[],'slope2':[]}
    temp['cutoff_score'] = cutoff_score
    temp['cutoff_logit_PD'] = cutoff_logit_PD
    temp['cutoff_PD'] = np.exp(cutoff_logit_PD) / (1+np.exp(cutoff_logit_PD))
    temp['totalSSR'] = res1.ssr + res2.ssr
    temp['Intercept1'] = cutoff_logit_PD - res1.params[0]*cutoff_score
    temp['slope1'] = res1.params[0]
    temp['Intercept2'] = cutoff_logit_PD - res2.params[0]*cutoff_score
    temp['slope2'] = res2.params[0]

    return( temp)


def SegLRplot(data, CT, **kw):

    data_forsingleline = data.copy()
    res_full = smf.ols(formula='logit_mix_pd ~total_score', data=data_forsingleline).fit()
    
    def _func(x):
        _Intercept = res_full.params[0] +x
        data_forsingleline['logit_PD_est'] = _Intercept + res_full.params[1]*data_forsingleline['total_score']
        data_forsingleline['PD_est'] = data_forsingleline['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        return (data_forsingleline.PD_est.mean()-CT)
    shift = fsolve(_func, 0.01)

    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    fig, ax = plt.subplots()
    ax.scatter(data.total_score,data.logit_mix_pd,s=25)    
    X1_plot = np.linspace(-50,cutoff_score,200)
    ax.plot(X1_plot, (Intercept1 + slope1*X1_plot), label="Seg 1")
    X2_plot = np.linspace(cutoff_score,100,200)
    ax.plot(X2_plot, (Intercept2 + slope2*X2_plot), label="Seg 2")
    X_full_plot = np.linspace(-50,100,200)
    ax.plot(X_full_plot, X_full_plot*res_full.params[1] + res_full.params[0]+shift[0], label="No Seg")
    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()


def Segscorecard(data, cutoff_score, cutoff_logit_PD):

    data1 = data.query('total_score<=@cutoff_score')
    data2 = data.query('total_score>@cutoff_score')
    res1 = smf.ols(formula='I(logit_mix_pd-cutoff_logit_PD) ~ I(total_score-cutoff_score)+0', data=data1).fit()
    res2 = smf.ols(formula='I(logit_mix_pd-cutoff_logit_PD) ~ I(total_score-cutoff_score)+0', data=data2).fit()

    data1['fitted_logit_pd'] = res1.fittedvalues + cutoff_logit_PD
    data2['fitted_logit_pd'] = res2.fittedvalues + cutoff_logit_PD
    data1['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in data1['fitted_logit_pd'] ]
    data2['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in data2['fitted_logit_pd'] ]
    Ratings = []
    for i in data1.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd)))
    data1['fitted_PDRR_withcutoff'] = Ratings   
    Ratings = []
    for i in data2.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd)))
    data2['fitted_PDRR_withcutoff'] = Ratings 
    dat = pd.concat([data1,data2])
    temp = pd.merge(data, dat, on=['FundName','logit_mix_pd','total_score','fitted_PDRR'], how='inner', suffixes=('', '_cali'))
    return( temp)


def Segscorecard_afcali(data, **kw):

    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    data1 = data.query('total_score<=@cutoff_score')
    data2 = data.query('total_score>@cutoff_score')
    data1['fitted_logit_pd_afcali'] = Intercept1 + slope1*data1['total_score']
    data2['fitted_logit_pd_afcali'] = Intercept2 + slope2*data2['total_score']
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
    temp = pd.merge(data, dat[['FundName', 'fitted_logit_pd_afcali','fitted_pd_afcali','fitted_PDRR_afcali']], on=['FundName'], how='inner')
    return( temp)



def UpdateInterceptbyCT(dat, CT, **kw):
    data = dat.copy()
    newparam = copy.deepcopy(kw)
    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')
    CT = CT 

    def _func(x):
        _Intercept1 = Intercept1 +x
        _Intercept2 = Intercept2 +x
        logit_PD_est = []
        for score in data['total_score']:
            if score <= cutoff_score:
                logit_PD_est.append(_Intercept1+slope1*score)
            else:
                logit_PD_est.append(_Intercept2+slope2*score)
        data['logit_PD_est'] = logit_PD_est
        data['PD_est'] = data['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        return (data.PD_est.mean()-CT)

    shift = fsolve(_func, 0.01)
    newparam.update({'Intercept1_origin': Intercept1, 'Intercept2_origin': Intercept2,\
        'shift':shift[0],'Intercept1': Intercept1+shift[0], 'Intercept2': Intercept2+shift[0]})
    
    return(newparam)


def UpdateInterceptbyCT_singleline(data, CT):

    data_forsingleline = data.copy()
    res_full = smf.ols(formula='logit_mix_pd ~total_score', data=data_forsingleline).fit()
    newparam={}
    def _func(x):
        _Intercept = res_full.params[0] +x
        data_forsingleline['logit_PD_est'] = _Intercept + res_full.params[1]*data_forsingleline['total_score']
        data_forsingleline['PD_est'] = data_forsingleline['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))        
        return (data_forsingleline.PD_est.mean()-CT)
        
    shift = fsolve(_func, 0.01)
    newparam.update({'Intercept_origin': res_full.params[0],'Intercept': res_full.params[0]+shift[0], 'shift':shift[0], 'slope':res_full.params[1]})
    
    return(newparam)

def Scorecard_part1_afcali(data, **kwargs):

    data1 = data.copy()
    kw = copy.deepcopy(kwargs)
    Intercept = kw.pop('Intercept')
    slope = kw.pop('slope')


    data1['fitted_logit_pd_afcali'] = Intercept + slope*data1['total_score']
    data1['fitted_pd_afcali'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in data1['fitted_logit_pd_afcali'] ]

    Ratings = []
    for i in data1.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd_afcali)))
    data1['fitted_PDRR_afcali'] = Ratings   
    temp = pd.merge(data, data1[['FundName', 'fitted_logit_pd_afcali','fitted_pd_afcali','fitted_PDRR_afcali']], on=['FundName'], how='inner')
    return( temp)

def findcutoff_forpart2(data2, kwargs, search=(0,100)):

    kw1 = copy.deepcopy(kwargs)
    data_part2 = data2.copy()
    Intercept = kw1.pop('Intercept')
    slope = kw1.pop('slope')
    PDRR_sum=[]
    for x in range(search[0],search[1]):
        y = Intercept + slope * x   

        res2 = smf.ols(formula='I(logit_mix_pd-y) ~ I(total_score-x)+0', data=data_part2).fit() 


        data_part2['fitted_logit_pd'] = res2.fittedvalues + y
        data_part2['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in data_part2['fitted_logit_pd'] ] 
        Ratings = []
        for i in data_part2.iterrows():
            Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd)))
        data_part2['fitted_PDRR'] = Ratings 

        PDRR_sum.append(data_part2['fitted_pd'].sum())
    return(PDRR_sum)


def SegLRplot_dev(data, **kwargs):
    kw = copy.deepcopy(kwargs)
    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    fig, ax = plt.subplots()
    ax.scatter(data.total_score,data.logit_mix_pd,s=25, color='lightcoral',label="Development Data")    
    X1_plot = np.linspace(-80,cutoff_score,200)
    ax.plot(X1_plot, (Intercept1 + slope1*X1_plot), label="Seg 1")
    X2_plot = np.linspace(cutoff_score,100,200)
    ax.plot(X2_plot, (Intercept2 + slope2*X2_plot), label="Seg 2")
    y=[-8.11,-7.42,-6.91,-6.50,-5.99,-5.60,-5.20,-4.95,-4.50]
    labels = ['-8.11(PDRR 2)','-7.42(PDRR 3)','-6.91(PDRR 4)','-6.50(PDRR 5)','-5.99(PDRR 6)','-5.60(PDRR 7)','-5.20(PDRR 8)','-4.95(PDRR 9)','-4.50(PDRR 10)']
    plt.yticks(y, labels)
    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()

def SegLRplot_snap(data, **kwargs):
    kw = copy.deepcopy(kwargs)
    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    fig, ax = plt.subplots()
    ax.scatter(data.total_score,data.logit_mix_pd,s=25, color='lightcoral',label="End of Aaugust Snapshot")    
    X1_plot = np.linspace(-80,cutoff_score,200)
    ax.plot(X1_plot, (Intercept1 + slope1*X1_plot), label="Seg 1")
    X2_plot = np.linspace(cutoff_score,100,200)
    ax.plot(X2_plot, (Intercept2 + slope2*X2_plot), label="Seg 2")
    y=[-8.11,-7.42,-6.91,-6.50,-5.99,-5.60,-5.20,-4.95,-4.50]
    labels = ['-8.11(PDRR 2)','-7.42(PDRR 3)','-6.91(PDRR 4)','-6.50(PDRR 5)','-5.99(PDRR 6)','-5.60(PDRR 7)','-5.20(PDRR 8)','-4.95(PDRR 9)','-4.50(PDRR 10)']
    plt.yticks(y, labels)
    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()

#%% load data and modify some of them:
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
toremove = ['GS Mezz VI','Hines Poland Sustainable Income Fund (EURO)',
'TPG Capital Partners','Carmel V','GSO COF III','MS Asia IV',
'H2 Core RE Debt Fund','American RE Partners II']
# read MC result
mc = pd.read_pickle('result_info3_66.pickle')
mc = mc[['FundName','MC_pd','MC_PDRR']]

# read Business suggested PDRR
mix = pd.read_excel('MC_results.xlsx')
mix = mix[['names','Business suggested PDRR']]
mix.rename(columns={'names':'FundName'}, inplace=True)
mix = mix[~mix['FundName'].isin(toremove)]
mix['mix_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in mix['Business suggested PDRR'] ]
mix['logit_mix_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in mix['mix_pd'] ]

# read current model and fund data
dat = pd.read_excel('..\data\Funds_0821.xlsx')
data = dat[~dat['FundName'].isin(toremove)]
# transformation
data['Institutional'].replace({'I':1,'NI':0}, inplace=True)
data['MandatoryPrepayment'].replace({'Y':1,'N':0}, inplace=True)
data['DealType'].replace({'Subscription':1,'Bridge':0}, inplace=True)
data['CreditQuality'].replace({'Excellent':1, 'Average':2, 'Below Average':3}, inplace=True)
data['BB-FS'] = data['EffectiveAdvanceRate']* data['FundCommitment'] / data['FacilitySize']

data['FundBorrowingBase'] = [np.log(x) for x in data['FundBorrowingBase']]
data['FundUnpaidCommitment'] = [np.log(x) for x in data['FundUnpaidCommitment']]
data['FundCommitment'] = [np.log(x) for x in data['FundCommitment']]
data['FacilitySize'] = [np.log(x) for x in data['FacilitySize']]
data['TotalAssets'].fillna(data['TotalAssets'].min(), inplace=True)
data['TotalAssets'] = [np.log(x) for x in data['TotalAssets']]
data['TotalAssets+UnpaidCommitment'].fillna(data['TotalAssets+UnpaidCommitment'].min(), inplace=True)
data['TotalAssets+UnpaidCommitment'] = [np.log(x) for x in data['TotalAssets+UnpaidCommitment']]
data['PartnerCapital'].fillna(data['PartnerCapital'].min(), inplace=True)
data['PartnerCapital'][data['PartnerCapital']<=0] =1
data['PartnerCapital'] = [np.log(x) for x in data['PartnerCapital']]
data['NumberOfIncluded_120'] = np.clip(data['NumberOfIncluded'], -10, 120) 
data['NumberOfInvestors_120'] = np.clip(data['NumberOfInvestors'], -10, 120)  

data['final_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['FundsFinanceFinalPDRR'] ]
data['final_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['FundsFinanceFinalPDRR'] ]
data['logit_final_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in data['final_pd'] ]
# merge them together
data = pd.merge(data, mc, on='FundName', how='inner')
data = pd.merge(data, mix, on='FundName', how='inner')
data['logit_MC_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in data['MC_pd'] ]



#%% 
factors = ['CC_HHI', 'BB-FS', 'FundCommitment','CreditQuality', 'Institutional', 'Overcapitalization']
signs =  [1.0, -1.0, -1.0, 1.0, -1.0, -1.0]
y_col = 'logit_mix_pd'
PDRR = 'Business suggested PDRR'
ww = [0.05,  0.20, 0.05,  0.20, 0.35, 0.15]

temp_ww = modelSD(data, factors, y_col, PDRR, signs, weights=ww)
scorecard_ww = scorecard(data, factors, signs, y_col, ww)







#%%  cut the data into part1 and part2
data1 = scorecard_ww.query('total_score<=50')
data2 = scorecard_ww.query('total_score>50')
CT_all = scorecard_ww['mix_pd'].mean()
CT_part1 = data1['mix_pd'].mean() #0.0008549180327868864
CT_part2 = data2['mix_pd'].mean() #0.0046749999999999995

# part1: unrestricted linear regression, then shift intercept by match CT_PDRR_part1 
kw=UpdateInterceptbyCT_singleline(data1, CT_part1)
data1_afcali = Scorecard_part1_afcali(data1, **kw)
#stats = TMstats(data1_afcali, 'fitted_PDRR_afcali', PDRR, PDRR=range(1,10)) 
#CreateBenchmarkMatrix(data1_afcali, 'TM_part1.xlsx','sheet1', 'fitted_PDRR_afcali', PDRR,PDRR=range(1,10))

# part2: deteck cutoff_score betweem 38 and 56 which make the whole sample match CT_PDRR_all

#findcutoff_forpart2(data2, kw, search=(38,57))

# choose the most left possible breaking point for conservativeness
x=38 
y = kw['Intercept'] + kw['slope'] * x   

# find the slope2 which make data2 match CT_part2
def _func(beta):
    data2['logit_PD_est'] = y-beta*x+beta*data2['total_score']
    data2['PD_est'] = data2['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))        
    return (data2.PD_est.mean()-CT_part2)
    
slope2 = fsolve(_func, 0.01)[0]
Intercept2=y-slope2*x

newkw={'cutoff_score':x,'Intercept1':kw['Intercept'], 'slope1':kw['slope'],'Intercept2':Intercept2, 'slope2':slope2}

SegLRplot_dev(scorecard_ww, **newkw)
scorecard_ww_afcali = Segscorecard_afcali(scorecard_ww, **newkw)
stats = TMstats(scorecard_ww_afcali, 'fitted_PDRR_afcali', PDRR,PDRR=range(1,11)) 
CreateBenchmarkMatrix(scorecard_ww_afcali, 'TM_Business.xlsx','sheet1', 'fitted_PDRR_afcali', PDRR,PDRR=range(1,11))
CreateBenchmarkMatrix(scorecard_ww_afcali, 'TM_curr.xlsx','sheet1', 'fitted_PDRR_afcali', 'FundsFinanceFinalPDRR',PDRR=range(1,11))


'''
newkw:
{'Intercept1': -7.0307977604823337,
 'Intercept2': -7.847440309079623,
 'cutoff_score': 38,
 'slope1': 0.012527306256767979,
 'slope2': 0.034017899640907165}
 
toreport = pd.read_excel('..\data\FactorScoreRating.xlsx')
temp = scorecard_ww_afcali[['FundName','total_score','fitted_PDRR_afcali']]
temp.rename(columns={'FundName':'Name', 'total_score':'total score new model','fitted_PDRR_afcali':'PDRR new model'}, inplace=True)
toreport = pd.merge(toreport,temp, on='Name', how='inner')
toreport.to_excel('..\data\FactorScoreRating_20170918.xlsx')
'''


#%% apply model on snapshot data:
# load data and modify some of them:
factors = ['CC_HHI', 'BB-FS', 'FundCommitment','InvestorStrength', 'Institutional', 'Overcapitalization']

# get current snapshot 
dat1 = pd.read_excel('..\data\Snapshot Data 0916 a.xlsx')
dat1.drop('InvestorStrength',axis=1, inplace=True)
dat_rafael = pd.read_excel('..\data\Copy of StructureFile0914-v2.xlsx')
dat_rafael = dat_rafael[['Fund Name','Investor Strength']]
dat_rafael.rename(columns={'Investor Strength':'InvestorStrength'}, inplace=True)

dat1 = pd.merge(dat1, dat_rafael, on='Fund Name', how='inner')
dat1.dropna(subset=factors, how='any',inplace=True)
dat1['Institutional'].replace({'Institutional':1,'Individual':0}, inplace=True)
dat1['Institutional'].replace({'Institutional ':1,'Individual ':0}, inplace=True)
dat1['InvestorStrength'].replace({'Excellent':1, 'Average':2, 'Below Average':3}, inplace=True)
dat1['InvestorStrength'].replace({'Excellent ':1, 'Average ':2, 'Below Average ':3}, inplace=True)

# get snapshot rating 
dat2 = pd.read_pickle('1year.pickle') # this data is after upgrading 1 notch for Bridge loan
dat2 = dat2[['Customer Name + Number','LGD Risk Rating','WAPD','WAPD2','timestamp']]
dat2.rename(columns={'Customer Name + Number':'Fund Name'}, inplace=True)

# merge them together
data = pd.merge(dat1, dat2, on='Fund Name', how='inner')
data.rename(columns={'WAPD':'Current PDRR', 'WAPD2':'PD'}, inplace=True)
data['logit_PD'] = [( lambda x: np.log(x/(1-x)))(x) for x in data['PD'] ]
data.drop('FundName',axis=1, inplace=True)
data.rename(columns={'Fund Name':'FundName'}, inplace=True)


y_col = 'logit_PD'
PDRR = 'Current PDRR'
means = [0.198838, 2.800621, 20.923944, 1.323077, 0.938462, 2.882200]
stds = [ 0.275367, 3.511428, 1.209870, 0.516629, 0.241245, 3.224261]

scorecard_snapshot = scorecard(data, factors, signs, y_col, ww, norm_by_preset=True, means=means, stds=stds)
scorecard_snapshot_afcali = Segscorecard_afcali(scorecard_snapshot, **newkw)
stats = TMstats(scorecard_snapshot_afcali, 'fitted_PDRR_afcali', PDRR, PDRR=range(1,12)) 
CreateBenchmarkMatrix(scorecard_snapshot_afcali, 'TM_snapshot.xlsx','sheet1', 'fitted_PDRR_afcali',PDRR, PDRR=range(1,12))

#plot
scorecard_snapshot.rename(columns={'logit_PD':'logit_mix_pd'}, inplace=True)
SegLRplot_snap(scorecard_snapshot, **newkw)
#get data
scorecard_snapshot_afcali.to_excel('snapshot_afcali.xlsx')# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 10:33:20 2017

More functions which were used in development are in dev_2_calibration.py. 

@author: ub71894 (4e8e6d0b), CSG
"""


import os, pandas as pd, numpy as np
import statsmodels.api as sm 
import statsmodels.formula.api as smf
os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")
from FFMC import SomersD
import sys
import copy
from scipy.optimize import fsolve
import seaborn as sns
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import matplotlib.pyplot as plt


#%%
def modelSD(data, factors, y_col, PDRR, signs=False, weights=False, norm_by_preset=False, means=None, stds=None):
    '''
    if weight is not assigned, it will run linear regression to get weight,
    then use weight to estimated PD and PDRR, then calculate SomersD bewteen 
    input PDRR and estimated PDRR
    if weight is assigned, it will use it to get total score then run linear regression
    to get estimated PD and PDRR, then calculate SomersD bewteen input PDRR and estimated PDRR

    '''
    dat = data[factors].copy()
    y = data[y_col].copy()
    inde = sm.add_constant(dat, prepend = True)
    res = sm.OLS(y, inde).fit()
    if not signs:
        signs = []
        for factor in factors:
            signs.append(np.sign(res.params[factor]))

    if norm_by_preset:
        for i,col in enumerate(factors):
            dat[col]  = signs[i]*50*(dat[col] - means[i] ) / stds[i]
    else:
        for i,col in enumerate(factors):
            dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()
            
    if weights:
        dat['score'] = (weights * dat[factors].values).sum(axis=1)
        inde = sm.add_constant(dat['score'], prepend = True)
        res = sm.OLS(y, inde).fit()
        fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
        Ratings = []
        for i in fitted_pd:
            Ratings.append(sum(MS['new_low']<=i))

        return(weights, signs, SomersD(data[PDRR], Ratings))

    else:
        inde = sm.add_constant(dat, prepend = True)
        res = sm.OLS(y, inde).fit()
        coeff = res.params.iloc[1:]
        coeffsum = coeff.sum()
        weights = [x/coeffsum for x in res.params.iloc[1:]]
        fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
        Ratings = []
        for i in fitted_pd:
            Ratings.append(sum(MS['new_low']<=i))

        return(res, weights, signs, SomersD(data[PDRR], Ratings))


def scorecard(data, factors, signs, y_col, weights, norm_by_preset=False, means=None, stds=None):
    '''
    Apply determinated weight and sign to calculated new columns:
    'total_score', 'fitted_logit_pd','fitted_pd' and 'fitted_PDRR'
    then return the new DataFrame

    '''
    dat = data.copy()
    if norm_by_preset:
        for i,col in enumerate(factors):
            dat[col]  = signs[i]*50*(dat[col] - means[i] ) / stds[i]
    else:
        for i,col in enumerate(factors):
            dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()

    dat['total_score'] = (weights * dat[factors].values).sum(axis=1)

    y = data[y_col].copy()
    inde = sm.add_constant(dat['total_score'], prepend = True)
    res = sm.OLS(y, inde).fit()
    dat['fitted_logit_pd'] = res.fittedvalues
    dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat['fitted_logit_pd'] ]

    Ratings = []
    for i in dat.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd)))
    dat['fitted_PDRR'] = Ratings   
    return(dat)





def SegLR(data, cutoff_score, cutoff_logit_PD):

    data1 = data.query('total_score<=@cutoff_score')
    data2 = data.query('total_score>@cutoff_score')
    res1 = smf.ols(formula='I(logit_PD-cutoff_logit_PD) ~ I(total_score-cutoff_score)+0', data=data1).fit()
    res2 = smf.ols(formula='I(logit_PD-cutoff_logit_PD) ~ I(total_score-cutoff_score)+0', data=data2).fit()

    temp = {'cutoff_score':[],'cutoff_PD':[],'totalSSR':[],'Intercept1':[],'Intercept2':[],'slope1':[],'slope2':[]}
    temp['cutoff_score'] = cutoff_score
    temp['cutoff_logit_PD'] = cutoff_logit_PD
    temp['cutoff_PD'] = np.exp(cutoff_logit_PD) / (1+np.exp(cutoff_logit_PD))
    temp['totalSSR'] = res1.ssr + res2.ssr
    temp['Intercept1'] = cutoff_logit_PD - res1.params[0]*cutoff_score
    temp['slope1'] = res1.params[0]
    temp['Intercept2'] = cutoff_logit_PD - res2.params[0]*cutoff_score
    temp['slope2'] = res2.params[0]

    return( temp)


def SegLRplot(data, CT, **kw):

    data_forsingleline = data.copy()
    res_full = smf.ols(formula='logit_PD ~total_score', data=data_forsingleline).fit()
    
    def _func(x):
        _Intercept = res_full.params[0] +x
        data_forsingleline['logit_PD_est'] = _Intercept + res_full.params[1]*data_forsingleline['total_score']
        data_forsingleline['PD_est'] = data_forsingleline['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        return (data_forsingleline.PD_est.mean()-CT)
    shift = fsolve(_func, 0.01)

    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    fig, ax = plt.subplots()
    ax.scatter(data.total_score,data.logit_PD,s=25)    
    X1_plot = np.linspace(-50,cutoff_score,200)
    ax.plot(X1_plot, (Intercept1 + slope1*X1_plot), label="Seg 1")
    X2_plot = np.linspace(cutoff_score,100,200)
    ax.plot(X2_plot, (Intercept2 + slope2*X2_plot), label="Seg 2")
    X_full_plot = np.linspace(-50,100,200)
    ax.plot(X_full_plot, X_full_plot*res_full.params[1] + res_full.params[0]+shift[0], label="No Seg")
    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()



def SegLRplot_PDRR(data, CT_PDRR, **kw):

    data_forsingleline = data.copy()
    res_full = smf.ols(formula='logit_PD ~total_score', data=data_forsingleline).fit()
    
    def _func(x):
        _Intercept = res_full.params[0] +x
        data_forsingleline['logit_PD_est'] = _Intercept + res_full.params[1]*data_forsingleline['total_score']
        data_forsingleline['PD_est'] = data_forsingleline['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        data_forsingleline['PDRR_est'] = [sum(MS['new_low']<=x) for x in data_forsingleline['PD_est']]
        return (data_forsingleline.PDRR_est.mean()-CT_PDRR)
    shift = fsolve(_func, 0.01)

    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    fig, ax = plt.subplots()
    ax.scatter(data.total_score,data.logit_PD,s=25)    
    X1_plot = np.linspace(-50,cutoff_score,200)
    ax.plot(X1_plot, (Intercept1 + slope1*X1_plot), label="Seg 1")
    X2_plot = np.linspace(cutoff_score,100,200)
    ax.plot(X2_plot, (Intercept2 + slope2*X2_plot), label="Seg 2")
    X_full_plot = np.linspace(-50,100,200)
    ax.plot(X_full_plot, X_full_plot*res_full.params[1] + res_full.params[0]+shift[0], label="No Seg")
    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()




def Segscorecard_afcali(data, **kw):

    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    data1 = data.query('total_score<=@cutoff_score')
    data2 = data.query('total_score>@cutoff_score')
    data1['fitted_logit_pd_afcali'] = Intercept1 + slope1*data1['total_score']
    data2['fitted_logit_pd_afcali'] = Intercept2 + slope2*data2['total_score']
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
    temp = pd.merge(data, dat[['Fund Name', 'fitted_logit_pd_afcali','fitted_pd_afcali','fitted_PDRR_afcali']], on=['Fund Name'], how='inner')
    return( temp)



def UpdateInterceptbyCT(dat, CT, **kw):
    data = dat.copy()
    newparam = copy.deepcopy(kw)
    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')
    CT = CT 

    def _func(x):
        _Intercept1 = Intercept1 +x
        _Intercept2 = Intercept2 +x
        logit_PD_est = []
        for score in data['total_score']:
            if score <= cutoff_score:
                logit_PD_est.append(_Intercept1+slope1*score)
            else:
                logit_PD_est.append(_Intercept2+slope2*score)
        data['logit_PD_est'] = logit_PD_est
        data['PD_est'] = data['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        return (data.PD_est.mean()-CT)

    shift = fsolve(_func, 0.01)
    newparam.update({'Intercept1_origin': Intercept1, 'Intercept2_origin': Intercept2,\
        'shift':shift[0],'Intercept1': Intercept1+shift[0], 'Intercept2': Intercept2+shift[0]})
    
    return(newparam)


def UpdateInterceptbyCT_PDRR(dat, CT_PDRR, **kw):
    data = dat.copy()
    newparam = copy.deepcopy(kw)
    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')
    CT_PDRR = CT_PDRR 

    def _func(x):
        _Intercept1 = Intercept1 +x
        _Intercept2 = Intercept2 +x
        logit_PD_est = []
        for score in data['total_score']:
            if score <= cutoff_score:
                logit_PD_est.append(_Intercept1+slope1*score)
            else:
                logit_PD_est.append(_Intercept2+slope2*score)
        data['logit_PD_est'] = logit_PD_est
        data['PD_est'] = data['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        data['PDRR_est'] = [sum(MS['new_low']<=x[0]) for x in data['PD_est']]
    
        return (data.PDRR_est.mean()-CT_PDRR)

    shift = fsolve(_func, 0.01)
    newparam.update({'Intercept1_origin': Intercept1, 'Intercept2_origin': Intercept2,\
        'shift':shift[0],'Intercept1': Intercept1+shift[0], 'Intercept2': Intercept2+shift[0]})
    
    return(newparam)

#%% load data and modify some of them:
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
factors = ['CC_HHI', 'BB-FS', 'FundCommitment','InvestorStrength', 'Institutional', 'Overcapitalization']

# get current snapshot 
dat1 = pd.read_excel('..\data\Snapshot Data 0916 a.xlsx')
dat1.dropna(subset=factors, how='any',inplace=True)
dat1['Institutional'].replace({'Institutional':1,'Individual':0}, inplace=True)
dat1['Institutional'].replace({'Institutional ':1,'Individual ':0}, inplace=True)
dat1['InvestorStrength'].replace({'Excellent':1, 'Average':2, 'Below Average':3}, inplace=True)
dat1['InvestorStrength'].replace({'Excellent ':1, 'Average ':2, 'Below Average ':3}, inplace=True)

# get snapshot rating 
dat2 = pd.read_pickle('1year_adj.pickle') # this data is after upgrading 1 notch for Bridge loan
dat2 = dat2[['Customer Name + Number','LGD Risk Rating','WAPD','WAPD2','timestamp']]
dat2.rename(columns={'Customer Name + Number':'Fund Name'}, inplace=True)

# merge them together
data = pd.merge(dat1, dat2, on='Fund Name', how='inner')
data.rename(columns={'WAPD':'Current PDRR', 'WAPD2':'PD'}, inplace=True)
data['logit_PD'] = [( lambda x: np.log(x/(1-x)))(x) for x in data['PD'] ]
#data.to_excel('data_calibration.xlsx')
#data.to_pickle('data_calibration.pickle')



#%% 

signs =  [1.0, -1.0, -1.0, 1.0, -1.0, -1.0]
y_col = 'logit_PD'
PDRR = 'Current PDRR'
ww = [0.05,  0.20, 0.05,  0.20, 0.35, 0.15]
means = [0.198838, 2.800621, 20.923944, 1.323077, 0.938462, 2.882200]
stds = [ 0.275367, 3.511428, 1.209870, 0.516629, 0.241245, 3.224261]
CT = 0.001422  # as (20170916)
CT_PDRR = 4.04

temp_ww = modelSD(data, factors, y_col, PDRR, signs, weights=ww, norm_by_preset=True, means=means, stds=stds)
scorecard_ww = scorecard(data, factors, signs, y_col, ww, norm_by_preset=True, means=means, stds=stds)

#%% go through all possible cutoff score

# for each score, go through all possible logit_pd (10%,90%)
q10 = scorecard_ww['logit_PD'].quantile(0.1)
q90 = scorecard_ww['logit_PD'].quantile(0.9)
somestat = [];  saveall={}
for p in range(100):

    cutoff_score = -10+p  
       

    y=[];  y_afcali=[];  intercept_1=[];  intercept_2=[]
    slope1=[];  slope2=[];  correct_slopesign=[];   somersd=[]
    match=[];  w1=[];  w2=[];  o5=[];  up=[];  down=[];   
    cc3=[]; cc34=[]; cc35=[]; cc36=[]
    for i in range(100):
        cutoff_logit_PD = q10+i/100*(q90-q10)
        
        seg_params = SegLR(scorecard_ww, cutoff_score, cutoff_logit_PD)
        seg_params_afcali = UpdateInterceptbyCT(scorecard_ww, CT, **seg_params)
        scorecard_ww_afcali = Segscorecard_afcali(scorecard_ww, **seg_params_afcali)
        stats = TMstats(scorecard_ww_afcali, PDRR, 'fitted_PDRR_afcali', PDRR=range(1,10)) 

        y.append(cutoff_logit_PD)
        y_afcali.append(cutoff_logit_PD+seg_params_afcali['shift'])
        intercept_1.append(seg_params_afcali['Intercept1'])
        intercept_2.append(seg_params_afcali['Intercept2'])
        slope1.append(seg_params_afcali['slope1'])
        slope2.append(seg_params_afcali['slope2'])
        correct_slopesign.append((True if (seg_params_afcali['slope1']>0 and seg_params_afcali['slope2']>0) else False))
        somersd.append(SomersD(scorecard_ww_afcali[PDRR], scorecard_ww_afcali['fitted_PDRR_afcali']))
        match.append(stats['Match'])
        w1.append(stats['Within_1'])
        w2.append(stats['Within_2'])
        o5.append(stats['Outside_5'])
        up.append(stats['Upgrade'])
        down.append(stats['Downgrade'])
        cc3.append(stats['CC_3'])
        cc34.append(stats['CC_3-4'])
        cc35.append(stats['CC_3-5'])
        cc36.append(stats['CC_3-6'])    

    df= pd.DataFrame()
    df['y'] = y;    df['y_afcali'] = y_afcali;   df['cutoff_score'] =  cutoff_score
    df['Intercept1'] = intercept_1;    df['Intercept2'] = intercept_2
    df['slope1'] = slope1;    df['slope2'] = slope2
    df['correct_slopesign'] = correct_slopesign;    df['SomersD'] = somersd;    df['Match'] = match;    df['Within_1'] = w1
    df['Within_2'] = w2;    df['Outside_5'] = o5;    df['Upgrade'] = up;    df['Downgrade'] = down
    df['CC_3'] = cc3;    df['CC_3-4'] = cc34;    df['CC_3-5'] = cc35;    df['CC_3-6'] = cc36   
    
    saveall[cutoff_score]=df
    somestat.append(df.query('correct_slopesign==True')['Upgrade'].min())


#%% UpdateInterceptbyCT_PDRR
# for each score, go through all possible logit_pd (10%,90%)
q10 = scorecard_ww['logit_PD'].quantile(0.1)
q90 = scorecard_ww['logit_PD'].quantile(0.9)
somestat = [];  saveall={}
for p in range(100):

    cutoff_score = -10+p  
       

    y=[];  y_afcali=[];  intercept_1=[];  intercept_2=[]
    slope1=[];  slope2=[];  correct_slopesign=[];   somersd=[]
    match=[];  w1=[];  w2=[];  o5=[];  up=[];  down=[];   
    cc3=[]; cc34=[]; cc35=[]; cc36=[]
    for i in range(100):
        cutoff_logit_PD = q10+i/100*(q90-q10)
        
        seg_params = SegLR(scorecard_ww, cutoff_score, cutoff_logit_PD)
        seg_params_afcali = UpdateInterceptbyCT_PDRR(scorecard_ww, CT_PDRR, **seg_params)
        scorecard_ww_afcali = Segscorecard_afcali(scorecard_ww, **seg_params_afcali)
        stats = TMstats(scorecard_ww_afcali, PDRR, 'fitted_PDRR_afcali', PDRR=range(1,10)) 

        y.append(cutoff_logit_PD)
        y_afcali.append(cutoff_logit_PD+seg_params_afcali['shift'])
        intercept_1.append(seg_params_afcali['Intercept1'])
        intercept_2.append(seg_params_afcali['Intercept2'])
        slope1.append(seg_params_afcali['slope1'])
        slope2.append(seg_params_afcali['slope2'])
        correct_slopesign.append((True if (seg_params_afcali['slope1']>0 and seg_params_afcali['slope2']>0) else False))
        somersd.append(SomersD(scorecard_ww_afcali[PDRR], scorecard_ww_afcali['fitted_PDRR_afcali']))
        match.append(stats['Match'])
        w1.append(stats['Within_1'])
        w2.append(stats['Within_2'])
        o5.append(stats['Outside_5'])
        up.append(stats['Upgrade'])
        down.append(stats['Downgrade'])
        cc3.append(stats['CC_3'])
        cc34.append(stats['CC_3-4'])
        cc35.append(stats['CC_3-5'])
        cc36.append(stats['CC_3-6'])    

    df= pd.DataFrame()
    df['y'] = y;    df['y_afcali'] = y_afcali;   df['cutoff_score'] =  cutoff_score
    df['Intercept1'] = intercept_1;    df['Intercept2'] = intercept_2
    df['slope1'] = slope1;    df['slope2'] = slope2
    df['correct_slopesign'] = correct_slopesign;    df['SomersD'] = somersd;    df['Match'] = match;    df['Within_1'] = w1
    df['Within_2'] = w2;    df['Outside_5'] = o5;    df['Upgrade'] = up;    df['Downgrade'] = down
    df['CC_3'] = cc3;    df['CC_3-4'] = cc34;    df['CC_3-5'] = cc35;    df['CC_3-6'] = cc36   
    
    saveall[cutoff_score]=df
    somestat.append(df.query('correct_slopesign==True')['Upgrade'].min())



#%% when fixing cutoff score, get the matrix for all stats measure
num=[]; re=pd.DataFrame()
for p in range(30):
    cutoff_score = -10+p  
    df = saveall[cutoff_score].copy()
    df = df.query('correct_slopesign==True')
    re = pd.concat([re,df])
up = re['Upgrade'].quantile(q=0.05)
cc = re['CC_3-4'].quantile(q=0.05)
sd = re['SomersD'].quantile(q=0.95)
re=re.query('Upgrade<=@up and CC_3-4<=@cc and SomersD>@sd')
re.reset_index(drop=True, inplace=True)
# re has 68 obs, chose the one that has the biggest SomersD since upgrade and CC3-4 is similar


index = 12 # higher slope and good SomersD
kw = dict(re.loc[index,:])


SegLRplot(scorecard_ww, CT, **kw)

cutoff_logit_PD = kw['y']
seg_params = SegLR(scorecard_ww, cutoff_score, cutoff_logit_PD)
seg_params_afcali = UpdateInterceptbyCT(scorecard_ww, CT, **seg_params)
scorecard_ww_afcali = Segscorecard_afcali(scorecard_ww, **seg_params_afcali)

stats = TMstats(scorecard_ww_afcali, PDRR, 'fitted_PDRR_afcali', PDRR=range(1,10)) 
CreateBenchmarkMatrix(scorecard_ww_afcali, 'TM.xlsx','sheet1', PDRR,'fitted_PDRR_afcali', PDRR=range(1,10))




#%% when fixing cutoff score, get the matrix for all stats measure
num=[]; re=pd.DataFrame()
for p in range(30):
    cutoff_score = -10+p  
    df = saveall[cutoff_score].copy()
    df = df.query('correct_slopesign==True')
    re = pd.concat([re,df])
up = re['Upgrade'].quantile(q=0.1)
cc = re['CC_3-4'].quantile(q=0.1)
sd = re['SomersD'].quantile(q=0.9)
re=re.query('Upgrade<=@up and CC_3-4<=@cc and SomersD>@sd')
re.reset_index(drop=True, inplace=True)

# re has 3 obs, chose the one that has the biggest slopes since other measure are the same



index = 1 # higher slope and good SomersD
kw = dict(re.loc[index,:])


SegLRplot_PDRR(scorecard_ww, CT_PDRR, **kw)

cutoff_logit_PD = q10+index/100*(q90-q10)
seg_params = SegLR(scorecard_ww, cutoff_score, cutoff_logit_PD)
seg_params_afcali = UpdateInterceptbyCT_PDRR(scorecard_ww, CT_PDRR, **seg_params)
scorecard_ww_afcali = Segscorecard_afcali(scorecard_ww, **seg_params_afcali)

stats = TMstats(scorecard_ww_afcali, PDRR, 'fitted_PDRR_afcali', PDRR=range(1,10)) 
CreateBenchmarkMatrix(scorecard_ww_afcali, 'TM_PDRR.xlsx','sheet1', PDRR,'fitted_PDRR_afcali', PDRR=range(1,10))
# -*- coding: utf-8 -*-
"""
Created on Fri Sep  1 10:33:20 2017

More functions which were used in development are in dev_2_calibration.py. 

@author: ub71894 (4e8e6d0b), CSG
"""


import os, pandas as pd, numpy as np
import statsmodels.api as sm 
import statsmodels.formula.api as smf
os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")
from FFMC import SomersD
import sys
import copy
from scipy.optimize import fsolve
import seaborn as sns
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.CreateBenchmarkMatrix import CreateBenchmarkMatrix, TMstats
import matplotlib.pyplot as plt


#%%
def modelSD(data, factors, y_col, PDRR, signs=False, weights=False, norm_by_preset=False, means=None, stds=None):
    '''
    if weight is not assigned, it will run linear regression to get weight,
    then use weight to estimated PD and PDRR, then calculate SomersD bewteen 
    input PDRR and estimated PDRR
    if weight is assigned, it will use it to get total score then run linear regression
    to get estimated PD and PDRR, then calculate SomersD bewteen input PDRR and estimated PDRR

    '''
    dat = data[factors].copy()
    y = data[y_col].copy()
    inde = sm.add_constant(dat, prepend = True)
    res = sm.OLS(y, inde).fit()
    if not signs:
        signs = []
        for factor in factors:
            signs.append(np.sign(res.params[factor]))

    if norm_by_preset:
        for i,col in enumerate(factors):
            dat[col]  = signs[i]*50*(dat[col] - means[i] ) / stds[i]
    else:
        for i,col in enumerate(factors):
            dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()
            
    if weights:
        dat['score'] = (weights * dat[factors].values).sum(axis=1)
        inde = sm.add_constant(dat['score'], prepend = True)
        res = sm.OLS(y, inde).fit()
        fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
        Ratings = []
        for i in fitted_pd:
            Ratings.append(sum(MS['new_low']<=i))

        return(weights, signs, SomersD(data[PDRR], Ratings))

    else:
        inde = sm.add_constant(dat, prepend = True)
        res = sm.OLS(y, inde).fit()
        coeff = res.params.iloc[1:]
        coeffsum = coeff.sum()
        weights = [x/coeffsum for x in res.params.iloc[1:]]
        fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
        Ratings = []
        for i in fitted_pd:
            Ratings.append(sum(MS['new_low']<=i))

        return(res, weights, signs, SomersD(data[PDRR], Ratings))


def scorecard(data, factors, signs, y_col, weights, norm_by_preset=False, means=None, stds=None):
    '''
    Apply determinated weight and sign to calculated new columns:
    'total_score', 'fitted_logit_pd','fitted_pd' and 'fitted_PDRR'
    then return the new DataFrame

    '''
    dat = data.copy()
    if norm_by_preset:
        for i,col in enumerate(factors):
            dat[col]  = signs[i]*50*(dat[col] - means[i] ) / stds[i]
    else:
        for i,col in enumerate(factors):
            dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()

    dat['total_score'] = (weights * dat[factors].values).sum(axis=1)

    y = data[y_col].copy()
    inde = sm.add_constant(dat['total_score'], prepend = True)
    res = sm.OLS(y, inde).fit()
    dat['fitted_logit_pd'] = res.fittedvalues
    dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat['fitted_logit_pd'] ]

    Ratings = []
    for i in dat.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd)))
    dat['fitted_PDRR'] = Ratings   
    return(dat)





def SegLR(data, cutoff_score, cutoff_logit_PD):

    data1 = data.query('total_score<=@cutoff_score')
    data2 = data.query('total_score>@cutoff_score')
    res1 = smf.ols(formula='I(logit_PD-cutoff_logit_PD) ~ I(total_score-cutoff_score)+0', data=data1).fit()
    res2 = smf.ols(formula='I(logit_PD-cutoff_logit_PD) ~ I(total_score-cutoff_score)+0', data=data2).fit()

    temp = {'cutoff_score':[],'cutoff_PD':[],'totalSSR':[],'Intercept1':[],'Intercept2':[],'slope1':[],'slope2':[]}
    temp['cutoff_score'] = cutoff_score
    temp['cutoff_logit_PD'] = cutoff_logit_PD
    temp['cutoff_PD'] = np.exp(cutoff_logit_PD) / (1+np.exp(cutoff_logit_PD))
    temp['totalSSR'] = res1.ssr + res2.ssr
    temp['Intercept1'] = cutoff_logit_PD - res1.params[0]*cutoff_score
    temp['slope1'] = res1.params[0]
    temp['Intercept2'] = cutoff_logit_PD - res2.params[0]*cutoff_score
    temp['slope2'] = res2.params[0]

    return( temp)


def SegLRplot(data, CT, **kw):

    data_forsingleline = data.copy()
    res_full = smf.ols(formula='logit_PD ~total_score', data=data_forsingleline).fit()
    
    def _func(x):
        _Intercept = res_full.params[0] +x
        data_forsingleline['logit_PD_est'] = _Intercept + res_full.params[1]*data_forsingleline['total_score']
        data_forsingleline['PD_est'] = data_forsingleline['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        return (data_forsingleline.PD_est.mean()-CT)
    shift = fsolve(_func, 0.01)

    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    fig, ax = plt.subplots()
    ax.scatter(data.total_score,data.logit_PD,s=25)    
    X1_plot = np.linspace(-50,cutoff_score,200)
    ax.plot(X1_plot, (Intercept1 + slope1*X1_plot), label="Seg 1")
    X2_plot = np.linspace(cutoff_score,100,200)
    ax.plot(X2_plot, (Intercept2 + slope2*X2_plot), label="Seg 2")
    X_full_plot = np.linspace(-50,100,200)
    ax.plot(X_full_plot, X_full_plot*res_full.params[1] + res_full.params[0]+shift[0], label="No Seg")
    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()



def SegLRplot_PDRR(data, CT_PDRR, **kw):

    data_forsingleline = data.copy()
    res_full = smf.ols(formula='logit_PD ~total_score', data=data_forsingleline).fit()
    
    def _func(x):
        _Intercept = res_full.params[0] +x
        data_forsingleline['logit_PD_est'] = _Intercept + res_full.params[1]*data_forsingleline['total_score']
        data_forsingleline['PD_est'] = data_forsingleline['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        data_forsingleline['PDRR_est'] = [sum(MS['new_low']<=x) for x in data_forsingleline['PD_est']]
        return (data_forsingleline.PDRR_est.mean()-CT_PDRR)
    shift = fsolve(_func, 0.01)

    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    fig, ax = plt.subplots()
    ax.scatter(data.total_score,data.logit_PD,s=25)    
    X1_plot = np.linspace(-50,cutoff_score,200)
    ax.plot(X1_plot, (Intercept1 + slope1*X1_plot), label="Seg 1")
    X2_plot = np.linspace(cutoff_score,100,200)
    ax.plot(X2_plot, (Intercept2 + slope2*X2_plot), label="Seg 2")
    X_full_plot = np.linspace(-50,100,200)
    ax.plot(X_full_plot, X_full_plot*res_full.params[1] + res_full.params[0]+shift[0], label="No Seg")
    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()




def Segscorecard_afcali(data, **kw):

    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    data1 = data.query('total_score<=@cutoff_score')
    data2 = data.query('total_score>@cutoff_score')
    data1['fitted_logit_pd_afcali'] = Intercept1 + slope1*data1['total_score']
    data2['fitted_logit_pd_afcali'] = Intercept2 + slope2*data2['total_score']
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
    temp = pd.merge(data, dat[['Fund Name', 'fitted_logit_pd_afcali','fitted_pd_afcali','fitted_PDRR_afcali']], on=['Fund Name'], how='inner')
    return( temp)




def UpdateInterceptbyCT(dat, CT, **kw):
    data = dat.copy()
    newparam = copy.deepcopy(kw)
    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')
    CT = CT 

    def _func(x):
        _Intercept1 = Intercept1 +x
        _Intercept2 = Intercept2 +x
        logit_PD_est = []
        for score in data['total_score']:
            if score <= cutoff_score:
                logit_PD_est.append(_Intercept1+slope1*score)
            else:
                logit_PD_est.append(_Intercept2+slope2*score)
        data['logit_PD_est'] = logit_PD_est
        data['PD_est'] = data['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        return (data.PD_est.mean()-CT)

    shift = fsolve(_func, 0.01)
    newparam.update({'Intercept1_origin': Intercept1, 'Intercept2_origin': Intercept2,\
        'shift':shift[0],'Intercept1': Intercept1+shift[0], 'Intercept2': Intercept2+shift[0]})
    
    return(newparam)


def UpdateInterceptbyCT_PDRR(dat, CT_PDRR, **kw):
    data = dat.copy()
    newparam = copy.deepcopy(kw)
    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')
    CT_PDRR = CT_PDRR 

    def _func(x):
        _Intercept1 = Intercept1 +x
        _Intercept2 = Intercept2 +x
        logit_PD_est = []
        for score in data['total_score']:
            if score <= cutoff_score:
                logit_PD_est.append(_Intercept1+slope1*score)
            else:
                logit_PD_est.append(_Intercept2+slope2*score)
        data['logit_PD_est'] = logit_PD_est
        data['PD_est'] = data['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        data['PDRR_est'] = [sum(MS['new_low']<=x[0]) for x in data['PD_est']]
    
        return (data.PDRR_est.mean()-CT_PDRR)

    shift = fsolve(_func, 0.01)
    newparam.update({'Intercept1_origin': Intercept1, 'Intercept2_origin': Intercept2,\
        'shift':shift[0],'Intercept1': Intercept1+shift[0], 'Intercept2': Intercept2+shift[0]})
    
    return(newparam)


def UpdateInterceptbyCT_PDRR_singleline(data, CT_PDRR):

    data_forsingleline = data.copy()
    res_full = smf.ols(formula='logit_PD ~total_score', data=data_forsingleline).fit()
    newparam={}
    def _func(x):
        _Intercept = res_full.params[0] +x
        data_forsingleline['logit_PD_est'] = _Intercept + res_full.params[1]*data_forsingleline['total_score']
        data_forsingleline['PD_est'] = data_forsingleline['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
        data_forsingleline['PDRR_est'] = [sum(MS['new_low']<=x) for x in data_forsingleline['PD_est']]
        return (data_forsingleline.PDRR_est.mean()-CT_PDRR)
    shift = fsolve(_func, 0.01)
    newparam.update({'Intercept_origin': res_full.params[0],'Intercept': res_full.params[0]+shift[0], 'shift':shift[0], 'slope':res_full.params[1]})
    
    return(newparam)

def Scorecard_part1_afcali(data, **kw):

    data1 = data.copy()
    Intercept = kw.pop('Intercept')
    slope = kw.pop('slope')


    data1['fitted_logit_pd_afcali'] = Intercept + slope*data1['total_score']
    data1['fitted_pd_afcali'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in data1['fitted_logit_pd_afcali'] ]

    Ratings = []
    for i in data1.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd_afcali)))
    data1['fitted_PDRR_afcali'] = Ratings   
    temp = pd.merge(data, data1[['Fund Name', 'fitted_logit_pd_afcali','fitted_pd_afcali','fitted_PDRR_afcali']], on=['Fund Name'], how='inner')
    return( temp)


def findcutoff_forpart2(data2, kw1):


    data_part2 = data2.copy()
    Intercept = kw1.pop('Intercept')
    slope = kw1.pop('slope')
    PDRR_sum=[]
    for x in range(36,92):
        y = Intercept + slope * x   

        res2 = smf.ols(formula='I(logit_PD-y) ~ I(total_score-x)+0', data=data_part2).fit() 


        data_part2['fitted_logit_pd'] = res2.fittedvalues + y
        data_part2['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in data_part2['fitted_logit_pd'] ] 
        Ratings = []
        for i in data_part2.iterrows():
            Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd)))
        data_part2['fitted_PDRR'] = Ratings 

        PDRR_sum.append(data_part2['fitted_PDRR'].sum())
    return(PDRR_sum)


def SegLRplot_PDRR2(data, **kw):
    cutoff_score = kw.pop('cutoff_score')
    Intercept1 = kw.pop('Intercept1')
    Intercept2 = kw.pop('Intercept2')
    slope1 = kw.pop('slope1')    
    slope2 = kw.pop('slope2')

    fig, ax = plt.subplots()
    ax.scatter(data.total_score,data.logit_PD,s=25)    
    X1_plot = np.linspace(-50,cutoff_score,200)
    ax.plot(X1_plot, (Intercept1 + slope1*X1_plot), label="Seg 1")
    X2_plot = np.linspace(cutoff_score,100,200)
    ax.plot(X2_plot, (Intercept2 + slope2*X2_plot), label="Seg 2")

    legend = ax.legend(loc='upper left', shadow=True)
    plt.show()




#%% load data and modify some of them:
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
factors = ['CC_HHI', 'BB-FS', 'FundCommitment','InvestorStrength', 'Institutional', 'Overcapitalization']

# get current snapshot 
dat1 = pd.read_excel('..\data\Snapshot Data 0916 a.xlsx')
dat1.dropna(subset=factors, how='any',inplace=True)
dat1['Institutional'].replace({'Institutional':1,'Individual':0}, inplace=True)
dat1['Institutional'].replace({'Institutional ':1,'Individual ':0}, inplace=True)
dat1['InvestorStrength'].replace({'Excellent':1, 'Average':2, 'Below Average':3}, inplace=True)
dat1['InvestorStrength'].replace({'Excellent ':1, 'Average ':2, 'Below Average ':3}, inplace=True)

# get snapshot rating 
dat2 = pd.read_pickle('1year_adj.pickle') # this data is after upgrading 1 notch for Bridge loan
dat2 = dat2[['Customer Name + Number','LGD Risk Rating','WAPD','WAPD2','timestamp']]
dat2.rename(columns={'Customer Name + Number':'Fund Name'}, inplace=True)

# merge them together
data = pd.merge(dat1, dat2, on='Fund Name', how='inner')
data.rename(columns={'WAPD':'Current PDRR', 'WAPD2':'PD'}, inplace=True)
data['logit_PD'] = [( lambda x: np.log(x/(1-x)))(x) for x in data['PD'] ]
#data.to_excel('data_calibration.xlsx')
#data.to_pickle('data_calibration.pickle')



#%% 

signs =  [1.0, -1.0, -1.0, 1.0, -1.0, -1.0]
y_col = 'logit_PD'
PDRR = 'Current PDRR'
ww = [0.05,  0.20, 0.05,  0.20, 0.35, 0.15]
means = [0.198838, 2.800621, 20.923944, 1.323077, 0.938462, 2.882200]
stds = [ 0.275367, 3.511428, 1.209870, 0.516629, 0.241245, 3.224261]

CT_PDRR_all = 3.95#4.04
CT_PDRR_part1 = 3.57#3.61



temp_ww = modelSD(data, factors, y_col, PDRR, signs, weights=ww, norm_by_preset=True, means=means, stds=stds)
scorecard_ww = scorecard(data, factors, signs, y_col, ww, norm_by_preset=True, means=means, stds=stds)

#%%  cut the data into part1 and part2

data1 = scorecard_ww.query('total_score<=60')
data2 = scorecard_ww.query('total_score>60')

# part1: unrestricted linear regression, then shift intercept by match CT_PDRR_part1 
kw=UpdateInterceptbyCT_PDRR_singleline(data1, CT_PDRR_part1)
data1_afcali = Scorecard_part1_afcali(data1, **kw)
stats = TMstats(data1_cafcali, 'fitted_PDRR_afcali', PDRR, PDRR=range(1,10)) 
CreateBenchmarkMatrix(data1_cafcali, 'TM_part1.xlsx','sheet1', 'fitted_PDRR_afcali', PDRR,PDRR=range(1,10))

# part2: deteck cutoff_score betweem 40 and 90 which make the whole sample match CT_PDRR_all
a=findcutoff_forpart2(data1, data2, kw)






# plot and TM



































#%% bin 
scorecard_ww['bin'] = pd.qcut(scorecard_ww['total_score'], 10)
data_bin = scorecard_ww.groupby(by='bin').mean()[['logit_PD','total_score']]
res = smf.ols(formula='logit_PD ~total_score', data=data_bin).fit()
Intercept = res.params[0]; slope=res.params[1]

data_bin = scorecard_ww.copy()
newparam={}
def _func(x):
    _Intercept = Intercept +x
    data_bin['logit_PD_est'] = _Intercept + slope*data_bin['total_score']
    data_bin['PD_est'] = data_bin['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
    data_bin['PDRR_est'] = [sum(MS['new_low']<=x) for x in data_bin['PD_est']]
    return (data_bin.PDRR_est.mean()-CT_PDRR_all)
shift = fsolve(_func, 0.01)

data_bin['logit_PD_est'] = res.params[0]+shift[0] + res.params[1]*data_bin['total_score']
data_bin['PD_est'] = data_bin['logit_PD_est'].apply(lambda x: np.exp(x)/(1+np.exp(x)))
data_bin['PDRR_est'] = [sum(MS['new_low']<=x) for x in data_bin['PD_est']]

stats = TMstats(data_bin, 'PDRR_est', PDRR, PDRR=range(1,10)) 
CreateBenchmarkMatrix(data_bin, 'TM_bin.xlsx','sheet1', 'PDRR_est', PDRR,PDRR=range(1,10))# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 13:15:21 2017

Perform scorecard model selection work. Original is from dev_2_modelselection.py

@author: ub71894 (4e8e6d0b), CSG
"""

import os, pandas as pd, numpy as np
import statsmodels.api as sm 
os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")
from FFMC import SomersD
import time
from itertools import combinations, product


# define functions:

def backwardselection(data, factors, y_col='FundsFinanceFinalPDRR', threshold = 0.15):

    X = data[factors].copy()
    inde = sm.add_constant(X, prepend = True)
    y = data[y_col].copy()
    y = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in y]
    res = sm.OLS(y, inde).fit()
    s=1; newfactors = set(factors)
    pvalues = res.pvalues
    while pvalues.max() > threshold:
        to_remove_factor = pvalues.idxmax()
       # print('{:<80}'.format('In stage {s}, pvalue of factor "{remove}" is {maxpvalue:8.5f}\
       #  and it is dropped.'.format(s=s,remove=to_remove_factor,maxpvalue=pvalues.max())))
        print('In stage {s}, pvalue of factor "{remove}" is {maxpvalue:8.5f} and it is dropped.'\
            .format(s=s,remove=to_remove_factor,maxpvalue=pvalues.max()))
        s += 1
        newfactors = newfactors -  set([to_remove_factor ])
        X = data[list(newfactors)].copy()
        inde = sm.add_constant(X, prepend = True)
        res = sm.OLS(y, inde).fit()
        pvalues = res.pvalues
    print("*"*80)
    print("*"*80)
    print(res.summary())
    return(list(newfactors))


def __LinearReg(data, names, y_col, PDRR):

    dat = data[names].copy()
    inde = sm.add_constant(dat, prepend = True)
    y = data[y_col]
    res = sm.OLS(y, inde).fit()
    fitted_pd = [( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
    Ratings = []
    for i in fitted_pd:
        Ratings.append(sum(MS['new_low']<=i))
    temp1 = SomersD(data[PDRR], Ratings)   
    temp2 = res.rsquared
    return ([temp1, temp2])


def bestsubset(data, factors, atleast_p=3, best_k=5, by='SomersD'):
    '''

    Performs best subset model selection by Linear Regression. 
    According to 'SomersD' or 'Rsquared', it returns the best k model settings.


    '''      
    enum = {'SomersD':0, 'Rsquared':1}
    idx = enum.pop(by, 0) 

    setting=[];    measure=[]
    for p in range(atleast_p, len(factors)+1):
        for names in combinations(factors, p):
            setting.append(names)
            measure.append(__LinearReg(data, list(names))[idx]  )
    result = pd.DataFrame({'Setting':setting, by:measure})
    result.sort_values(by=by, ascending=0, inplace=True)
    return (result.reset_index(drop=True).iloc[:best_k,])
    #return(result)


def bestsubset2(data, categories, y_col, PDRR, best_k=5, by='SomersD'):
    '''
    Performs best subset model selection in preset categories by Linear Regression. 
    According to 'SomersD' or 'Rsquared', it returns the best k model settings.
    '''      
    
    enum = {'SomersD':0, 'Rsquared':1}
    idx = enum.pop(by, 0) 

    setting=[];    measure=[]

    for names in product(*categories):
        setting.append(names)
        measure.append(__LinearReg(data, list(names), y_col, PDRR)[idx]  )
    result = pd.DataFrame({'Setting':setting, by:measure})
    result.sort_values(by=by, ascending=0, inplace=True)
    return (result.reset_index(drop=True).iloc[:best_k,])
    #return(result)


def ARgridsearch(data, factors, y_col, PDRR, signs, weight_range, delta_factor, best_k):   

    dat = data[factors].copy()
    y = data[y_col].copy()
    inde = sm.add_constant(dat, prepend = True)
    res = sm.OLS(y, inde).fit()
    if not signs:
        signs = []
        for factor in factors:
            signs.append(np.sign(res.params[factor]))
    for i,col in enumerate(factors):
        dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()


    factors_weight_range  = dict(zip(factors, weight_range))

    args=[]; rows_list=[]
    # prepare grid for each quant and quali factors:
    for index,i in enumerate(factors):
        args.append(np.linspace(factors_weight_range[i][0],factors_weight_range[i][1], \
            num=int(round((factors_weight_range[i][1]-factors_weight_range[i][0])/delta_factor[index]+1))))
    
    
    weights = product(*args)    
    for all in weights:    
        # check the sum of weights:   
        if sum(all)==1:
            names_weights = list(all)                   
            score = (names_weights*dat[factors].values).sum(axis=1)
            ##### new version of grid search#########################
            inde = sm.add_constant(score, prepend = True)
            res = sm.OLS(y, inde).fit()
            fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
            Ratings = []
            for i in fitted_pd:
                Ratings.append(sum(MS['new_low']<=i))
            ##########################################################
            sd = SomersD(data[PDRR], Ratings)  
            #sd = SomersD(y, score)

            dict1 = {}
            dict1.update({'SomersD':sd})
            dict1.update(dict(zip(factors,names_weights)))
            rows_list.append(dict1) 

    result = pd.DataFrame(rows_list)
    result = result[factors+['SomersD']]
    result.sort_values(by='SomersD',ascending=False, inplace=True)
    result.reset_index(drop=True, inplace=True)
    return(result.head(best_k))
    




def modelSD(data, factors, y_col, PDRR, signs=False, weights=False):
    '''
    if weight is not assigned, it will run linear regression to get weight,
    then use weight to estimated PD and PDRR, then calculate SomersD bewteen 
    input PDRR and estimated PDRR
    if weight is assigned, it will use it to get total score then run linear regression
    to get estimated PD and PDRR, then calculate SomersD bewteen input PDRR and estimated PDRR

    '''

    dat = data[factors].copy()
    y = data[y_col].copy()
    inde = sm.add_constant(dat, prepend = True)
    res = sm.OLS(y, inde).fit()
    if not signs:
        signs = []
        for factor in factors:
            signs.append(np.sign(res.params[factor]))

    for i,col in enumerate(factors):
        dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()

    if weights:
        dat['score'] = (weights * dat[factors].values).sum(axis=1)
        inde = sm.add_constant(dat['score'], prepend = True)
        res = sm.OLS(y, inde).fit()
        fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
        Ratings = []
        for i in fitted_pd:
            Ratings.append(sum(MS['new_low']<=i))

        return(weights, signs, SomersD(data[PDRR], Ratings))

    else:
        inde = sm.add_constant(dat, prepend = True)
        res = sm.OLS(y, inde).fit()
        coeff = res.params.iloc[1:]
        coeffsum = coeff.sum()
        weights = [x/coeffsum for x in res.params.iloc[1:]]
        fitted_pd =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in res.fittedvalues ]
        Ratings = []
        for i in fitted_pd:
            Ratings.append(sum(MS['new_low']<=i))

        return(res, weights, signs, SomersD(data[PDRR], Ratings))


def scorecard(data, factors, signs, y_col, weights):
    '''
    Apply determinated weight and sign to calculated new columns:
    'total_score', 'fitted_logit_pd','fitted_pd' and 'fitted_PDRR'
    then return the new DataFrame

    '''

    dat = data.copy()
    for i,col in enumerate(factors):
        dat[col]  = signs[i]*50*(dat[col] - dat[col].mean() ) / dat[col].std()

    dat['total_score'] = (weights * dat[factors].values).sum(axis=1)

    y = data[y_col].copy()
    inde = sm.add_constant(dat['total_score'], prepend = True)
    res = sm.OLS(y, inde).fit()
    dat['fitted_logit_pd'] = res.fittedvalues
    dat['fitted_pd'] =[( lambda x: np.exp(x)/(1+np.exp(x)))(x) for x in dat['fitted_logit_pd'] ]

    Ratings = []
    for i in dat.iterrows():
        Ratings.append(sum(MS['new_low']<=(i[1].fitted_pd)))
    dat['fitted_PDRR'] = Ratings   
    return(dat)



#%% load data and modify some of them:
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
toremove = ['GS Mezz VI','Hines Poland Sustainable Income Fund (EURO)',
'TPG Capital Partners','Carmel V','GSO COF III','MS Asia IV',
'H2 Core RE Debt Fund','American RE Partners II']
# read MC result
mc = pd.read_pickle('result_info3_66.pickle')
mc = mc[['FundName','MC_pd','MC_PDRR']]

# read Business suggested PDRR
mix = pd.read_excel('MC_results.xlsx')
mix = mix[['names','Business suggested PDRR']]
mix.rename(columns={'names':'FundName'}, inplace=True)
mix = mix[~mix['FundName'].isin(toremove)]
mix['mix_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in mix['Business suggested PDRR'] ]
mix['logit_mix_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in mix['mix_pd'] ]

# read current model and fund data
dat = pd.read_excel('..\data\Funds_0821.xlsx')
data = dat[~dat['FundName'].isin(toremove)]
# transformation
data['Institutional'].replace({'I':1,'NI':0}, inplace=True)
data['MandatoryPrepayment'].replace({'Y':1,'N':0}, inplace=True)
data['DealType'].replace({'Subscription':1,'Bridge':0}, inplace=True)
data['CreditQuality'].replace({'Excellent':1, 'Average':2, 'Below Average':3}, inplace=True)
data['BB-FS'] = data['EffectiveAdvanceRate']* data['FundCommitment'] / data['FacilitySize']

data['FundBorrowingBase'] = [np.log(x) for x in data['FundBorrowingBase']]
data['FundUnpaidCommitment'] = [np.log(x) for x in data['FundUnpaidCommitment']]
data['FundCommitment'] = [np.log(x) for x in data['FundCommitment']]
data['FacilitySize'] = [np.log(x) for x in data['FacilitySize']]
data['TotalAssets'].fillna(data['TotalAssets'].min(), inplace=True)
data['TotalAssets'] = [np.log(x) for x in data['TotalAssets']]
data['TotalAssets+UnpaidCommitment'].fillna(data['TotalAssets+UnpaidCommitment'].min(), inplace=True)
data['TotalAssets+UnpaidCommitment'] = [np.log(x) for x in data['TotalAssets+UnpaidCommitment']]
data['PartnerCapital'].fillna(data['PartnerCapital'].min(), inplace=True)
data['PartnerCapital'][data['PartnerCapital']<=0] =1
data['PartnerCapital'] = [np.log(x) for x in data['PartnerCapital']]
data['NumberOfIncluded_120'] = np.clip(data['NumberOfIncluded'], -10, 120) 
data['NumberOfInvestors_120'] = np.clip(data['NumberOfInvestors'], -10, 120)  

data['final_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['FundsFinanceFinalPDRR'] ]
data['final_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['FundsFinanceFinalPDRR'] ]
data['logit_final_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in data['final_pd'] ]
# merge them together
data = pd.merge(data, mc, on='FundName', how='inner')
data = pd.merge(data, mix, on='FundName', how='inner')
data['logit_MC_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in data['MC_pd'] ]




#%% 
# ignore all result from backwardselection and bestsub due to the discussion with business line





#%% bestsub search by category:
cat1=['CCConcentration3', 'CCConcentration5', 'CCConcentration10', 'CC_HHI']
cat2=['BB-FS']
cat3=['FundCommitment']
cat4=['CreditQuality']
#cat5=['DealType']
cat6=['Institutional']
cat7=[ 'Overcapitalization']

PDRR= 'Business suggested PDRR'
y_col='logit_mix_pd' # this is logit PD which is implied from Business suggested PDRR

allfactors=[cat1,cat2,cat3,cat4, cat6,cat7]
models_mix6=bestsubset2(data, allfactors, y_col=y_col, PDRR=PDRR , best_k=100, by='SomersD')

# we get the best model:
factors = ['CC_HHI', 'BB-FS', 'FundCommitment','CreditQuality', 'Institutional', 'Overcapitalization']
# get the weight and sign:
modelSD(data, factors, y_col, PDRR, signs=False, weights=False)
# signs match business rationale
signs =  [1.0, -1.0, -1.0, 1.0, -1.0, -1.0]

modelSD(data, factors, y_col, PDRR, signs=False, weights=[0.05,  0.20, 0.05,  0.20, 0.35, 0.15])

#%% grid search for top models in previous 'best subset' results
weight_range = [
(0.01,0.06),
(0.19, 0.25),
(0.01,0.1),
(0.1,0.2),
(0.3, 0.4),
(0.13,0.18)
]
delta_factor = [0.01,0.01,0.01,0.01,0.01,0.01]


start_time = time.time()
grid_result_mix = ARgridsearch(data, factors, y_col, PDRR, signs, weight_range, delta_factor, 20)  
print("--- %s seconds ---" % (time.time() - start_time))




# -*- coding: utf-8 -*-
"""
Created on Sun Sep 17 01:22:04 2017

@author: ub71894 (4e8e6d0b), CSG
"""


import os, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\FFS\src")

import seaborn as sns
import matplotlib.pyplot as plt


#%% load data and modify some of them:
factors = ['CC_HHI', 'BB-FS', 'FundCommitment','InvestorStrength', 'Institutional', 'Overcapitalization']
MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
toremove = ['GS Mezz VI','Hines Poland Sustainable Income Fund (EURO)',
'TPG Capital Partners','Carmel V','GSO COF III','MS Asia IV',
'H2 Core RE Debt Fund','American RE Partners II']
# read MC result
mc = pd.read_pickle('result_info3_66.pickle')
mc = mc[['FundName','MC_pd','MC_PDRR']]

# read Business suggested PDRR
mix = pd.read_excel('MC_results.xlsx')
mix = mix[['names','Business suggested PDRR']]
mix.rename(columns={'names':'FundName'}, inplace=True)
mix = mix[~mix['FundName'].isin(toremove)]
mix['mix_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in mix['Business suggested PDRR'] ]
mix['logit_mix_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in mix['mix_pd'] ]

# read current model and fund data
dat = pd.read_excel('..\data\Funds_0821.xlsx')
data = dat[~dat['FundName'].isin(toremove)]
# transformation
data['Institutional'].replace({'I':1,'NI':0}, inplace=True)
data['MandatoryPrepayment'].replace({'Y':1,'N':0}, inplace=True)
data['DealType'].replace({'Subscription':1,'Bridge':0}, inplace=True)
data['CreditQuality'].replace({'Excellent':1, 'Average':2, 'Below Average':3}, inplace=True)
data['BB-FS'] = data['EffectiveAdvanceRate']* data['FundCommitment'] / data['FacilitySize']

data['FundBorrowingBase'] = [np.log(x) for x in data['FundBorrowingBase']]
data['FundUnpaidCommitment'] = [np.log(x) for x in data['FundUnpaidCommitment']]
data['FundCommitment'] = [np.log(x) for x in data['FundCommitment']]
data['FacilitySize'] = [np.log(x) for x in data['FacilitySize']]
data['TotalAssets'].fillna(data['TotalAssets'].min(), inplace=True)
data['TotalAssets'] = [np.log(x) for x in data['TotalAssets']]
data['TotalAssets+UnpaidCommitment'].fillna(data['TotalAssets+UnpaidCommitment'].min(), inplace=True)
data['TotalAssets+UnpaidCommitment'] = [np.log(x) for x in data['TotalAssets+UnpaidCommitment']]
data['PartnerCapital'].fillna(data['PartnerCapital'].min(), inplace=True)
data['PartnerCapital'][data['PartnerCapital']<=0] =1
data['PartnerCapital'] = [np.log(x) for x in data['PartnerCapital']]
data['NumberOfIncluded_120'] = np.clip(data['NumberOfIncluded'], -10, 120) 
data['NumberOfInvestors_120'] = np.clip(data['NumberOfInvestors'], -10, 120)  

data['final_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['FundsFinanceFinalPDRR'] ]
data['final_pd'] = [MS.query("PDRR=={}".format(x))['new_mid'].values[0] for x in data['FundsFinanceFinalPDRR'] ]
data['logit_final_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in data['final_pd'] ]
# merge them together
data = pd.merge(data, mc, on='FundName', how='inner')
data = pd.merge(data, mix, on='FundName', how='inner')
data['logit_MC_pd'] =[( lambda x: np.log(x/(1-x)))(x) for x in data['MC_pd'] ]



# get current snapshot 
dat1 = pd.read_excel('..\data\Snapshot Data 0916 a.xlsx')
dat1.dropna(subset=factors, how='any',inplace=True)
dat1['Institutional'].replace({'Institutional':1,'Individual':0}, inplace=True)
dat1['Institutional'].replace({'Institutional ':1,'Individual ':0}, inplace=True)
dat1['InvestorStrength'].replace({'Excellent':1, 'Average':2, 'Below Average':3}, inplace=True)
dat1['InvestorStrength'].replace({'Excellent ':1, 'Average ':2, 'Below Average ':3}, inplace=True)

# get snapshot rating 
dat2 = pd.read_pickle('1year_adj.pickle') # this data is after upgrading 1 notch for Bridge loan
dat2 = dat2[['Customer Name + Number','LGD Risk Rating','WAPD','WAPD2','timestamp']]
dat2.rename(columns={'Customer Name + Number':'Fund Name'}, inplace=True)

# merge them together
data2 = pd.merge(dat1, dat2, on='Fund Name', how='inner')
data2.rename(columns={'WAPD':'Current PDRR', 'WAPD2':'PD'}, inplace=True)
data2['logit_PD'] = [( lambda x: np.log(x/(1-x)))(x) for x in data2['PD'] ]


#%%


data.rename(columns={'Business suggested PDRR':'Rating','CreditQuality':'InvestorStrength'}, inplace=True)
data = data[factors+['Rating']]
data['type'] = 'Development'

data2.rename(columns={'Current PDRR':'Rating'}, inplace=True)
data2 = data2[factors+['Rating']]
data2['type'] = 'Current'
dat = pd.concat([data,data2])


for factor in factors:
    fig,ax=plt.subplots(1,1,figsize=(8,8))
    ax = sns.violinplot(x="type", y=factor, data=dat)
    fig.savefig(factor+'_violinplot.png')   


fig,ax=plt.subplots(1,1,figsize=(8,8))
ax = sns.countplot(x="Rating", data=dat,hue='type',alpha=0.9)
fig.savefig('Rating_dist.png')
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 15:55:22 2017

@author: ub71894 (4e8e6d0b), CSG
"""



import os, pandas as pd, numpy as np
from scipy.stats import norm
from math import ceil
from numba import jit

# functions:

@jit
def __gen_init_t(hist_init_t, N, randomseed=False):

    if randomseed:
        np.random.seed(randomseed)
    return(np.random.choice(hist_init_t, size=N, replace=True))


@jit
def __gen_latter_t(hist_latter_t, N, Tenor, randomseed=False):

    deltamean = hist_latter_t.mean()
    # 3 times the expectation is to guarantee we have enough delta t
    if randomseed:
        np.random.seed(randomseed)
    Tenor_star = max(2, Tenor) # for some tenor=1yr loans, 3*tenor is not big enough
    return(np.random.choice(hist_latter_t, size=(N,ceil(3*Tenor_star/deltamean)), replace=True))


@jit
def gen_delta_t(hist_init_t, hist_latter_t, N, Tenor, randomseed=False):

    init_t  = __gen_init_t(hist_init_t, N, randomseed)
    latter_t = __gen_latter_t(hist_latter_t, N, Tenor, randomseed)
    # replace first col of latter_t with init_t
    latter_t[:,0] = init_t
    # cumsum latter_t to get timing spot
    t_cumsum = np.cumsum(latter_t, axis=1)
    # find the tau which is the nearest point to maturity
    tau = np.sum(t_cumsum<Tenor, axis=1)
    # begin to build the generated delta_t for capital call timing spot
    delta_t = np.zeros_like(latter_t)
    for i in range(N):
        for j in range(tau[i]):
            delta_t[i,j]=latter_t[i,j]
        # last timing is calibrated rather than simulated
        delta_t[i,tau[i]]=Tenor-t_cumsum[i,tau[i]-1]
    # plus the last call
    tau = tau + 1
    return((delta_t, tau))


@jit
def gen_cc(hist_cc, delta_t, randomseed=False):

    N = delta_t.shape[0];  N_col =delta_t.shape[1]
    if randomseed:
        np.random.seed(randomseed)
    ccr = np.random.choice(hist_cc, size=(N,N_col), replace=True)
    mask = delta_t==0 # after maturity
    ccr = np.ma.masked_array(ccr, mask=mask)
    ccr = np.ma.filled(ccr, fill_value=0)

    tccr = np.cumsum(ccr, axis=1)
    mean_star = tccr[tccr[:,N_col-1]<1,N_col-1].mean() 
    # if total ccr is larger than 1, we need to scale it down to 1
    for i in range(N):
        last = ccr[i,:].sum()
        if last>=1:
            ccr[i,:] = ccr[i,:] / last * mean_star 
    # total_cc_rate is the cumsum of ccr
    tccr = np.cumsum(ccr, axis=1)
    tccr = np.ma.masked_array(tccr, mask=mask)
    tccr = np.ma.filled(tccr, fill_value=0)
    # remaining_cc_rate is the 1-tcct
    rccr = 1-tccr
    rccr = np.ma.masked_array(rccr, mask=mask)
    rccr = np.ma.filled(rccr, fill_value=0)

    return((tccr,rccr))


@jit
def gen_def(N, tau, investors_pd, total_ccr, delta_t, rho, amplitude=10, gamma=3, randomseed=False):
    # since at time t, the amount of tccr that investor had put in is the tccr at time t-1
    tccr_forpd = np.insert(total_ccr, 0, 0, axis=1)
    numofmaxtau = tau.max()
    numofinvestors = investors_pd.size
    alpha_matrix = np.empty((N, numofmaxtau, numofinvestors))
    def_flag = np.empty((N, numofmaxtau, numofinvestors))

    for i in range(N):
        for j in range(tau[i]):
            alpha_matrix[i,j,:] = amplitude * np.exp(-gamma*tccr_forpd[i,j])*investors_pd*delta_t[i,j]
    alpha_matrix = norm.ppf(alpha_matrix)
    if randomseed:
        np.random.seed(randomseed)
    stdnormmat = np.random.randn(N, numofmaxtau, 1+numofinvestors)

    temp_a = rho**0.5;    temp_b = (1-rho)**0.5
    for i in range(N):
        for j in range(tau[i]):
            def_flag[i,j,:] = (temp_a*stdnormmat[i,j,0]+temp_b*stdnormmat[i,j,1:]) < alpha_matrix[i,j,:]

    return(def_flag.astype(int)) 


@jit
def gen_usage(hist_usage, tau, randomseed=False):
    N = tau.shape[0];  Ncol =tau.max()
    if randomseed:
        np.random.seed(randomseed)  
    return(np.random.choice(hist_usage, size=(N,Ncol), replace=True))




def bisect(func, low, high, tol):
    '''
    
    Find root of continuous function where f(low) and f(high) have opposite signs

    '''

    while high-low > tol:
        midpoint = (low + high) / 2
        if func(midpoint)>0:
            high = midpoint
        else:
            low = midpoint

    return midpoint


def SomersD(y_true, y_score, sign=1, unit_concordance=True): 
    '''

    New version of SomersD function which leverages numba.jit to accelerate
    the calculation.

    '''
    
    x = np.array(y_score)
    y = np.array(y_true)
    n = len(x)
    C = 0
    D = 0
    if unit_concordance==True:
        for i in range(n):
            for j in range(i):
                dx = x[i] - x[j]
                dy = y[i] - y[j]
                if (dx*dy) > 0:
                    cij = 1
                    dij = 1
                elif  (dx*dy) < 0:
                    cij = -1
                    dij = 1
                else:
                    cij = 0
                    if dy==0: 
                        dij = 0
                    else: 
                        dij=1
                C = C + cij
                D = D + dij
    else:
        for i in range(n):
            for j in range(i):
                dx = x[i] - x[j]
                dy = y[i] - y[j]
                if  (dx*dy) > 0:
                    cij = abs(dy)
                    dij = abs(dy)
                elif (dx*dy) < 0:
                    cij = -abs(dy)
                    dij = abs(dy)
                else:
                    cij = 0
                    if dy==0: 
                        dij = 0
                    else: 
                        dij=1
                C = C + cij
                D = D + dij            
    return sign*C/D





def load_loan_info(strucdata, loan, ms, fillna_unincluded='B'):

    df_loan = strucdata.query('FundName=="{loan}"'.format(loan=loan))
    total_commit = df_loan['FundCommitment'].values[0]
    tenor = df_loan['Tenor'].values[0]
    facility_size = df_loan['FacilitySize'].values[0]
    df_loan['CapitalCommitment'] = pd.to_numeric(df_loan['CapitalCommitment'], errors='coerce')
    capital_commitment = df_loan['CapitalCommitment'].values
    investors_adrate = df_loan['AdvanceRate'].values
    investors_pct = capital_commitment / total_commit
    weighted_adrate = np.dot(investors_pct, investors_adrate)


    investors_pd = pd.Series([x.upper() for x in df_loan['S&PRating']])
    #investors_pd.replace({'NR':fillna_included,'NRI':fillna_included,'NRNI':fillna_unincluded}, inplace=True)
    investors_pd = np.array([ms.loc[ms['S&P']==x, 'UB_PD'].values[0] for x in investors_pd])
    final_rating = df_loan['FundsFinanceFinalPDRR'].values[0]
    result = {'tenor':tenor, 'total_commit':total_commit, 'facility_size':facility_size, \
    'investors_adrate':investors_adrate, 'investors_pct':investors_pct, \
    'weighted_adrate':weighted_adrate, 'investors_pd':investors_pd, 'final_rating':final_rating}

    return (result)
['0_data_CC.py', '0_data_CT.py', '0_data_fillNAinRating.py', '1_MC.py', '1_MC_CPPD.py', '2_scm_analysis.py', '2_scm_calibration.py', '2_scm_calibration_curr_method1.py', '2_scm_calibration_curr_method2..py', '2_scm_modelselection.py', '2_scm_plot.py', 'FFMC.py']
[87, 345, 385, 518, 639, 834, 1337, 1827, 2308, 2642, 2750, 2969]
