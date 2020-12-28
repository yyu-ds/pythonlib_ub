# -*- coding: utf-8 -*-
"""
Created on Wed May  1 11:07:49 2019

@author: ub71894
"""
import os
import sys
import pandas as pd
import numpy as np
import warnings
import pickle
import seaborn as sns
from matplotlib import pyplot as plt

os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\monitoring\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.PDModel import PDModel
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=FutureWarning)

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')

model_old = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_old.pkl','rb'))
model_LC = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_LC.pkl','rb'))

#%%
def best_worst(model):

    model.best_quantfactor = len(model.quant_factor)*[0]
    model.worst_quantfactor = len(model.quant_factor)*[0]
    for i in range(len(model.quant_factor)):
        temp1 = model.quant_multiplier[i]*50*(model.floor[i]-model.doc_mean[i])/model.doc_std[i]
        temp2 = model.quant_multiplier[i]*50*(model.cap[i]-model.doc_mean[i])/model.doc_std[i]
        if temp1 < temp2:
            model.best_quantfactor[i] = temp1
            model.worst_quantfactor[i] = temp2
        else:
            model.best_quantfactor[i] = temp2
            model.worst_quantfactor[i] = temp1
    model.best_quant = (model.quant_weight * np.array(model.best_quantfactor)).sum()
    model.worst_quant = (model.quant_weight * np.array(model.worst_quantfactor)).sum()

    model.best_qualifactor = len(model.quali_factor)*[0]
    for i in range(len(model.quali_factor)):
        model.best_qualifactor[i] = min(model.qualimapping[i].values())
    model.best_quali= (model.quali_weight * np.array(model.best_qualifactor)).sum()

    model.worst_qualifactor = len(model.quali_factor)*[0]
    for i in range(len(model.quali_factor)):
        model.worst_qualifactor[i] = max(model.qualimapping[i].values())
    model.worst_quali = (model.quali_weight * np.array(model.worst_qualifactor)).sum()

    model.best_score = 50*(model.best_quant-model.quantmean)/model.quantstd*model.quantweight  + \
                       50*(model.best_quali-model.qualimean)/model.qualistd*model.qualiweight 
    model.worst_score = 50*(model.worst_quant-model.quantmean)/model.quantstd*model.quantweight  + \
                       50*(model.worst_quali-model.qualimean)/model.qualistd*model.qualiweight 


best_worst(model_LC)
best_worst(model_old)

#%%
def old_cni(cus_name='Company',quant1=0.0,quant2=0.0, COP=1.0, quant3=0.0,quant4=0.0, TNW=1.0, quant5=0.0,quali1='A',quali2='A',quali3='A',quali4='A'):
    
    invalid_neg = []
    if (quant2<0) & (COP<0):
        invalid_neg.append('quant2 triggers Invalid Negative treatment')
        quant2 = model_old.cap[1]
    if (quant4<0) & (TNW<0):
        invalid_neg.append('quant4 triggers Invalid Negative treatment')
        quant4 = model_old.cap[3]

    pl_quant = [quant1,quant2,quant3,quant4,quant5]
    pl_quali = [quali1,quali2,quali3,quali4]

    # cap/floor for quant factors:
    for i, col in enumerate(model_old.quant_factor):
        pl_quant[i] = np.clip(pl_quant[i], model_old.floor[i], model_old.cap[i])        

    # quant factors transformation:
    for i, col in enumerate(model_old.quant_factor):
        if model_old.quant_log[i]:
            pl_quant[i] = np.log(pl_quant[i])

    # quant factors normalization:
    for i, col in enumerate(model_old.quant_factor):
        pl_quant[i]  = 50*(pl_quant[i] - model_old.doc_mean[i]) / model_old.doc_std[i]      
        
    # quant factors flip sign:  
    for i, col in enumerate(model_old.quant_factor):
        pl_quant[i] = pl_quant[i] * model_old.quant_multiplier[i]    


    for i, col in enumerate(model_old.quali_factor):
        pl_quali[i] = model_old.qualimapping[i][pl_quali[i]]


    pl_quant = np.array(pl_quant)
    pl_quali = np.array(pl_quali)


    pl_quantfactor_pct = (pl_quant-np.array(model_old.worst_quantfactor))/(np.array(model_old.best_quantfactor)-np.array(model_old.worst_quantfactor))
    pl_qualifactor_pct = (pl_quali-np.array(model_old.worst_qualifactor))/(np.array(model_old.best_qualifactor)-np.array(model_old.worst_qualifactor))

    quantscore_raw = (model_old.quant_weight * pl_quant).sum()
    quant_pct = (quantscore_raw-model_old.worst_quant)/(model_old.best_quant-model_old.worst_quant)
    quantscore_std = 50*( quantscore_raw - model_old.quantmean) / model_old.quantstd

    qualiscore_raw = (model_old.quali_weight * pl_quali).sum()
    quali_pct = (qualiscore_raw-model_old.worst_quali)/(model_old.best_quali-model_old.worst_quali)
    qualiscore_std = 50*( qualiscore_raw - model_old.qualimean) / model_old.qualistd
    Totalscore = quantscore_std*model_old.quantweight + qualiscore_std *model_old.qualiweight
    Totalscore_pct = (Totalscore-model_old.worst_score)/(model_old.best_score-model_old.worst_score)

    if Totalscore < model_old.cutoff:
        logitPD = model_old.intercept1 + model_old.slope1*Totalscore
    else:
        logitPD = model_old.intercept2 + model_old.slope2*Totalscore
 
    PD = 100*np.exp(logitPD)/(1+np.exp(logitPD))
    Ratings = sum(model_old.MS['new_low']<=(PD/100))

    pd_result = {
    'CustomerName':cus_name,
    'PD':PD,
    'Ratings':Ratings,
    'quant_pct':quant_pct,
    'quali_pct':quali_pct,
    'Totalscore_pct':Totalscore_pct,
    'quantfactor_pct':pl_quantfactor_pct,
    'qualifactor_pct':pl_qualifactor_pct,
    'Net Profit Margin (%)_Pct':pl_quantfactor_pct[0], 
    'Total Debt/COP_Pct':pl_quantfactor_pct[1],
    ' Total Assets _Pct':pl_quantfactor_pct[2],
    'Total Liabilities/TNW_Pct':pl_quantfactor_pct[3], 
    'ECE/Total Liabilities_Pct':pl_quantfactor_pct[4],
    'SSOR_Pct':pl_qualifactor_pct[0],
    'Level of Waivers_Pct':pl_qualifactor_pct[1],
    'Mgmt_Resp_Adverse_Conditions_Pct':pl_qualifactor_pct[2],
    'Vulnerability_Pct':pl_qualifactor_pct[3],
    'invalid_neg':invalid_neg
    }



    print('The prelim PDRR from old CnI model is '+str(pd_result['Ratings']))
    print('\n')
    temp=pd_result['invalid_neg'][:]
    while temp:
        print(temp.pop())
        print('\n')
    
    print('Quantitative as a % of possible = '+ str(round(100*pd_result['quant_pct']))+'%')
    print('\n')
    print('Qualitative as a % of possible = '+ str(round(100*pd_result['quali_pct']))+'%')    
    print('\n')
    print('Totalscore as a % of possible = '+ str(round(100*pd_result['Totalscore_pct']))+'%')


    df_plot = pd.DataFrame({'Best Score Percentage':pd_result['quantfactor_pct'], 'Factors':model_old.quant_factor})
    fig = plt.figure()
    ax=sns.barplot(x="Best Score Percentage", y="Factors", data=df_plot)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_yticks((0.9,0.7,0.5,0.3,0.1))
    pl_cat = ['Profitability', 'Cash flow leverage', 'Size', 'Balance sheet leverage', 'Liquidity']
    ax2.set_yticklabels([str(round(x[1]*100))+'% '+x[0] for x in list(zip(pl_cat,pd_result['quantfactor_pct']))])
    plt.savefig(cus_name+'_quantpct_old.png', bbox_inches='tight')
    
    df_plot = pd.DataFrame({'Best Score Percentage':pd_result['qualifactor_pct'], 'Factors':model_old.quali_factor})
    fig = plt.figure()
    ax=sns.barplot(x="Best Score Percentage", y="Factors", data=df_plot)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_yticks((0.87,0.62,0.37,0.12))
    ax2.set_yticklabels([str(round(x*100))+'%' for x in pd_result['qualifactor_pct']])
    plt.savefig(cus_name+'_qualipct_old.png', bbox_inches='tight')

    return (pd_result)

#%%
def LC_cni(cus_name='Company',NetSales=0, TotalDebt=0, EBITDA=0, TotalAssets=0, 
    Capitalization=0, InterestExpense=0,quali1='A',quali2='A',quali3='A',quali4='A',quali5='A'):
    
    quant1 = EBITDA/NetSales
    quant2 = TotalDebt/EBITDA
    quant3 = np.log(TotalAssets)
    quant4 = TotalDebt/Capitalization
    quant5 = EBITDA/InterestExpense

    invalid_neg = []
    if (quant2<0) & (EBITDA<0):
        invalid_neg.append('quant2 triggers Invalid Negative treatment')
        quant2 = model_LC.cap[1]
    if (quant4<0) & (Capitalization<0):
        invalid_neg.append('quant4 triggers Invalid Negative treatment')
        quant4 = model_LC.cap[3]
    if (quant5<0) & (InterestExpense<0):
        invalid_neg.append('quant5 triggers Invalid Negative treatment')
        quant5 = model_LC.cap[4]

    pl_quant = [quant1,quant2,quant3,quant4,quant5]
    pl_quali = [quali1,quali2,quali3,quali4,quali5]

    # cap/floor for quant factors:
    for i, col in enumerate(model_LC.quant_factor):
        pl_quant[i] = np.clip(pl_quant[i], model_LC.floor[i], model_LC.cap[i])        

    # quant factors transformation:
    for i, col in enumerate(model_LC.quant_factor):
        if model_LC.quant_log[i]:
            pl_quant[i] = np.log(pl_quant[i])

    # quant factors normalization:
    for i, col in enumerate(model_LC.quant_factor):
        pl_quant[i]  = 50*(pl_quant[i] - model_LC.doc_mean[i]) / model_LC.doc_std[i]      
        
    # quant factors flip sign:  
    for i, col in enumerate(model_LC.quant_factor):
        pl_quant[i] = pl_quant[i] * model_LC.quant_multiplier[i]    

    for i, col in enumerate(model_LC.quali_factor):
        pl_quali[i] = model_LC.qualimapping[i][pl_quali[i]]

    pl_quant = np.array(pl_quant)
    pl_quali = np.array(pl_quali)

    pl_quantfactor_pct = (pl_quant-np.array(model_LC.worst_quantfactor))/(np.array(model_LC.best_quantfactor)-np.array(model_LC.worst_quantfactor))
    pl_qualifactor_pct = (pl_quali-np.array(model_LC.worst_qualifactor))/(np.array(model_LC.best_qualifactor)-np.array(model_LC.worst_qualifactor))

    quantscore_raw = (model_LC.quant_weight * pl_quant).sum()
    quant_pct = (quantscore_raw-model_LC.worst_quant)/(model_LC.best_quant-model_LC.worst_quant)
    quantscore_std = 50*( quantscore_raw - model_LC.quantmean) / model_LC.quantstd

    qualiscore_raw = (model_LC.quali_weight * pl_quali).sum()
    quali_pct = (qualiscore_raw-model_LC.worst_quali)/(model_LC.best_quali-model_LC.worst_quali)
    qualiscore_std = 50*( qualiscore_raw - model_LC.qualimean) / model_LC.qualistd
    Totalscore = quantscore_std*model_LC.quantweight + qualiscore_std *model_LC.qualiweight
    Totalscore_pct = (Totalscore-model_LC.worst_score)/(model_LC.best_score-model_LC.worst_score)

    if Totalscore < model_LC.cutoff:
        logitPD = model_LC.intercept1 + model_LC.slope1*Totalscore
    else:
        logitPD = model_LC.intercept2 + model_LC.slope2*Totalscore
 
    PD = 100*np.exp(logitPD)/(1+np.exp(logitPD))
    Ratings = sum(model_LC.MS['new_low']<=(PD/100))

    pd_result = {
    'CustomerName':cus_name,
    'PD':PD,
    'Ratings':Ratings,
    'quant_pct':quant_pct,
    'quali_pct':quali_pct,
    'Totalscore_pct':Totalscore_pct,
    'quantfactor_pct':pl_quantfactor_pct,
    'qualifactor_pct':pl_qualifactor_pct,
    'quant1':quant1,
    'quant2':quant2,
    'quant3':quant3,
    'quant4':quant4,
    'quant5':quant5,
    'quant1_Pct':pl_quantfactor_pct[0], 
    'quant2_Pct':pl_quantfactor_pct[1],
    'quant3_Pct':pl_quantfactor_pct[2],
    'quant4_Pct':pl_quantfactor_pct[3], 
    'quant5_Pct':pl_quantfactor_pct[4],
    'quali1_Pct':pl_qualifactor_pct[0],
    'quali2_Pct':pl_qualifactor_pct[1],
    'quali3_Pct':pl_qualifactor_pct[2],
    'quali4_Pct':pl_qualifactor_pct[3],
    'quali5_Pct':pl_qualifactor_pct[4],
    'invalid_neg':invalid_neg
    }

    print('The prelim PDRR from LC model is '+str(pd_result['Ratings']))
    print('\n')
    temp=pd_result['invalid_neg'][:]
    while temp:
        print(temp.pop())
        print('\n')
    
    print('Quantitative as a % of possible = '+ str(round(100*pd_result['quant_pct']))+'%')
    print('\n')
    print('Qualitative as a % of possible = '+ str(round(100*pd_result['quali_pct']))+'%')    
    print('\n')
    print('Totalscore as a % of possible = '+ str(round(100*pd_result['Totalscore_pct']))+'%')


    df_plot = pd.DataFrame({'Best Score Percentage':pd_result['quantfactor_pct'], 'Factors':model_LC.quant_factor})
    fig = plt.figure()
    ax=sns.barplot(x="Best Score Percentage", y="Factors", data=df_plot)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_yticks((0.9,0.7,0.5,0.3,0.1))
    pl_cat = ['Profitability', 'Cash flow leverage', 'Size', 'Balance sheet leverage', 'Debt Service']
    ax2.set_yticklabels([str(round(x[1]*100))+'% '+x[0] for x in list(zip(pl_cat,pd_result['quantfactor_pct']))])
    plt.savefig(cus_name+'_quantpct_LC.png', bbox_inches='tight')

    
    
    df_plot = pd.DataFrame({'Best Score Percentage':pd_result['qualifactor_pct'], 'Factors':model_LC.quali_factor})
    fig = plt.figure()
    ax=sns.barplot(x="Best Score Percentage", y="Factors", data=df_plot)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_yticks((0.9,0.7,0.5,0.3,0.1))
    ax2.set_yticklabels([str(round(x*100))+'%' for x in pd_result['qualifactor_pct']])
    plt.savefig(cus_name+'_qualipct_LC.png', bbox_inches='tight')

    return (pd_result)
#%%
dat = pd.read_excel(r'..\data\Data_4.xlsx')
dat = dat.head(5)
dat[' Tangible Net Worth '].fillna(99999, inplace=True)
dat['COP'] = 99999


pl_result = []
for row in dat.iterrows():
    pl_result.append(old_cni(
        cus_name=row[1]['Customer Name'],
        quant1=row[1]['Net Profit Margin (%)'], 
        quant2=row[1]['Total Debt/COP'], 
        COP=row[1]['COP'], 
        quant3=row[1][' Total Assets '],
        quant4=row[1]['Total Liabilities/TNW'], 
        TNW=row[1][' Tangible Net Worth '], 
        quant5=row[1]['ECE/Total Liabilities'],
        quali1=row[1]['Strength of other SORs (excluding PSOR) to prevent default'],
        quali2=row[1]['Level of Waivers or Covenant Modifications'],
        quali3=row[1]['Management Communication'],
        quali4=row[1]['Vulnerability to Changes']
        )
    )

df_result = pd.DataFrame(pl_result)
df_result['invalid_neg_old'] = df_result['invalid_neg']
df_result_old = df_result[[
 'Net Profit Margin (%)_Pct',
 'Total Debt/COP_Pct',
 ' Total Assets _Pct',
 'Total Liabilities/TNW_Pct',
 'ECE/Total Liabilities_Pct',
 'SSOR_Pct',
 'Level of Waivers_Pct',
 'Mgmt_Resp_Adverse_Conditions_Pct',
 'Vulnerability_Pct',
 'invalid_neg_old'
]]

#%%
pl_result = []
for row in dat.iterrows():
    pl_result.append(LC_cni(
        cus_name=row[1]['Customer Name'],
        NetSales=row[1][' Net Sales '],
        TotalDebt=row[1][' Total Debt '],
        EBITDA=row[1][' EBITDA '],
        TotalAssets=row[1][' Total Assets '],
        Capitalization=row[1][' Capitalization '],
        InterestExpense=row[1][' Interest Expense '],
        quali1=row[1]['Strength of other SORs (excluding PSOR) to prevent default'],
        quali2=row[1]['Level of Waivers or Covenant Modifications'],
        quali3=row[1]['Management Quality'],
        quali4=row[1]['Vulnerability to Changes'],
        quali5=row[1]['Access to Outside Capital'],
        )
    )


df_result = pd.DataFrame(pl_result)
df_result['invalid_neg_LC'] = df_result['invalid_neg']
df_result_LC = df_result[[
 'quant1',
 'quant1_Pct',
 'quant2',
 'quant2_Pct',
 'quant3',
 'quant3_Pct',
 'quant4',
 'quant4_Pct',
 'quant5',
 'quant5_Pct',
 'quali1_Pct',
 'quali2_Pct',
 'quali3_Pct',
 'quali4_Pct',
 'quali5_Pct',
 'invalid_neg_LC',
]]


#%%
data = pd.concat([dat, df_result_old, df_result_LC], axis=1)
data = data[['Index (All financials in $USD)',
 'Analyst',
 'ModelTeam',
 'Currency',
 'Customer Name',
 'CIF Number',
 'Statement Date',
 'MAUG',
 'NAICS',
 'Net Profit Margin (%)',
  'Net Profit Margin (%)_Pct',
 'Total Debt/COP',
 'Total Debt/COP_Pct',
 'Total Liabilities/TNW',
 'Total Liabilities/TNW_Pct',
 'invalid_neg_old',
 'ECE/Total Liabilities',
 'ECE/Total Liabilities_Pct',
 ' Net Operating Profit ',
 ' Net Sales ',
 ' Total Debt ',
 ' EBITDA ',
 ' UB EBITDA ',
 ' Tangible Net Worth ',
 ' End Cash and Equivs ',
 ' Total Assets ',
 ' Total Assets _Pct',
 ' Total Liabilties ',
 ' Capitalization ',
 ' Interest Expense ',
 'quant1',
 'quant1_Pct',
 'quant2',
 'quant2_Pct',
 'quant3',
 'quant3_Pct',
 'quant4',
 'quant4_Pct',
 'quant5',
 'quant5_Pct', 
 'invalid_neg_LC', 
 'Strength of other SORs (excluding PSOR) to prevent default',
 'SSOR_Pct',
 'quali1_Pct',
 'Level of Waivers or Covenant Modifications',
 'Level of Waivers_Pct',
 'quali2_Pct',
 'Management Quality',
 'quali3_Pct',
 'Vulnerability to Changes',
 'Vulnerability_Pct',
 'quali4_Pct',
 'Access to Outside Capital',
 'quali5_Pct',
 'Management Communication',
 'Mgmt_Resp_Adverse_Conditions_Pct',
 'Quant as a % of Possible',
 'Quali as a % of Possible',
 'Total as a % of Possible',
 'RLA_Category_1',
 'RLA_Reason_1',
 'RLA_Reason_1_Details',
 'RLA_Notches_1',
 'RLA_Category_2',
 'RLA_Reason_2',
 'RLA_Reason_2_Details',
 'RLA_Notches_2',
 'RLA_Category_3',
 'RLA_Reason_3',
 'RLA_Reason_3_Details',
 'RLA_Notches_3',
 'Override_Category_1',
 'Override_Reason_1',
 'Override_Notches_1',
 'Override_Category_2',
 'Override_Reason_2',
 'Override_Notches_2',
 'Override_Category_3',
 'Override_Reason_3',
 'Override_Notches_3',
 'Unstructured_Override_Reason',
 'Unstructured_Override_Notches',
 'Guarantor_Information',
 'Guarantor_Notches',
 'S&P Rating',
 'SP_PDRR',
 "Moody's Rating",
 'Mdy_PDRR',
 'External_PDRR',
 'New_Prelim_PDRR_EBITDA',
 'New_Prelim_PDRR_UBEBITDA',
 'Old_Preliminary_PDRR_Uncapped',
 'Old_Preliminary_PDRR_After_Cap',
 'RLA_total',
 'Ovr_total',
 'Old_Final_PDRR']]

data.to_excel('updated_4.xlsx')
# -*- coding: utf-8 -*-
"""
Created on Wed May  1 11:07:49 2019

@author: ub71894
"""
import os
import sys
import pandas as pd
import numpy as np
import warnings
import pickle
import seaborn as sns
from matplotlib import pyplot as plt

os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\monitoring\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.PDModel import PDModel
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=FutureWarning)

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')

model_old = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_old.pkl','rb'))
#model_LC = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_LC.pkl','rb'))
model_MM = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_MM.pkl','rb'))

model_LC = pickle.load(open(r'C:\Users\ub71894\Documents\Projects\CNI\src\UBEBITDA\model_UBEBITDA_af.pkl','rb'))

#%%
def best_worst(model):

    model.best_quantfactor = len(model.quant_factor)*[0]
    model.worst_quantfactor = len(model.quant_factor)*[0]
    for i in range(len(model.quant_factor)):
        temp1 = model.quant_multiplier[i]*50*(model.floor[i]-model.doc_mean[i])/model.doc_std[i]
        temp2 = model.quant_multiplier[i]*50*(model.cap[i]-model.doc_mean[i])/model.doc_std[i]
        if temp1 < temp2:
            model.best_quantfactor[i] = temp1
            model.worst_quantfactor[i] = temp2
        else:
            model.best_quantfactor[i] = temp2
            model.worst_quantfactor[i] = temp1
    model.best_quant = (model.quant_weight * np.array(model.best_quantfactor)).sum()
    model.worst_quant = (model.quant_weight * np.array(model.worst_quantfactor)).sum()

    model.best_qualifactor = len(model.quali_factor)*[0]
    for i in range(len(model.quali_factor)):
        model.best_qualifactor[i] = min(model.qualimapping[i].values())
    model.best_quali= (model.quali_weight * np.array(model.best_qualifactor)).sum()

    model.worst_qualifactor = len(model.quali_factor)*[0]
    for i in range(len(model.quali_factor)):
        model.worst_qualifactor[i] = max(model.qualimapping[i].values())
    model.worst_quali = (model.quali_weight * np.array(model.worst_qualifactor)).sum()

    model.best_score = 50*(model.best_quant-model.quantmean)/model.quantstd*model.quantweight  + \
                       50*(model.best_quali-model.qualimean)/model.qualistd*model.qualiweight 
    model.worst_score = 50*(model.worst_quant-model.quantmean)/model.quantstd*model.quantweight  + \
                       50*(model.worst_quali-model.qualimean)/model.qualistd*model.qualiweight 


best_worst(model_LC)
best_worst(model_MM)
best_worst(model_old)


#%%


#%%
# RPM INTERNATIONAL INC
#old_cni(quant1=0.0536,quant2=3.69, COP=1.0, quant3=5223392000, quant4=-22.26, TNW=-10, quant5=0.056,quali1='A',quali2='A',quali3='A',quali4='B')

# Boeing
#old_cni(quant1=0.0992,quant2=0.84, COP=1.0, quant3=113195000000, quant4=-12.09, TNW=-10, quant5=0.0852,quali1='A',quali2='A',quali3='A',quali4='A')
from ipywidgets import interact, interactive, fixed, interact_manual,FloatSlider
import ipywidgets as widgets



def LC_cni(cus_name='Company',NetSales=0, TotalDebt=0, EBITDA=0, TotalAssets=0, 
    Capitalization=0, InterestExpense=0,quali1='A',quali2='A',quali3='A',quali4='A',quali5='A'):
    
    quant1 = EBITDA/NetSales
    quant2 = TotalDebt/EBITDA
    quant3 = np.log(TotalAssets)
    quant4 = TotalDebt/Capitalization
    quant5 = EBITDA/InterestExpense

    invalid_neg = []
    if (quant2<0) & (EBITDA<0):
        invalid_neg.append('quant2 triggers Invalid Negative treatment')
        quant2 = model_LC.cap[1]
    if (quant4<0) & (Capitalization<0):
        invalid_neg.append('quant4 triggers Invalid Negative treatment')
        quant4 = model_LC.cap[3]
    if (quant5<0) & (InterestExpense<0):
        invalid_neg.append('quant5 triggers Invalid Negative treatment')
        quant5 = model_LC.cap[4]

    pl_quant = [quant1,quant2,quant3,quant4,quant5]
    pl_quali = [quali1,quali2,quali3,quali4,quali5]

    # cap/floor for quant factors:
    for i, col in enumerate(model_LC.quant_factor):
        pl_quant[i] = np.clip(pl_quant[i], model_LC.floor[i], model_LC.cap[i])        

    # quant factors transformation:
    for i, col in enumerate(model_LC.quant_factor):
        if model_LC.quant_log[i]:
            pl_quant[i] = np.log(pl_quant[i])

    # quant factors normalization:
    for i, col in enumerate(model_LC.quant_factor):
        pl_quant[i]  = 50*(pl_quant[i] - model_LC.doc_mean[i]) / model_LC.doc_std[i]      
        
    # quant factors flip sign:  
    for i, col in enumerate(model_LC.quant_factor):
        pl_quant[i] = pl_quant[i] * model_LC.quant_multiplier[i]    

    for i, col in enumerate(model_LC.quali_factor):
        pl_quali[i] = model_LC.qualimapping[i][pl_quali[i]]

    pl_quant = np.array(pl_quant)
    pl_quali = np.array(pl_quali)

    pl_quantfactor_pct = (pl_quant-np.array(model_LC.worst_quantfactor))/(np.array(model_LC.best_quantfactor)-np.array(model_LC.worst_quantfactor))
    pl_qualifactor_pct = (pl_quali-np.array(model_LC.worst_qualifactor))/(np.array(model_LC.best_qualifactor)-np.array(model_LC.worst_qualifactor))

    quantscore_raw = (model_LC.quant_weight * pl_quant).sum()
    quant_pct = (quantscore_raw-model_LC.worst_quant)/(model_LC.best_quant-model_LC.worst_quant)
    quantscore_std = 50*( quantscore_raw - model_LC.quantmean) / model_LC.quantstd

    qualiscore_raw = (model_LC.quali_weight * pl_quali).sum()
    quali_pct = (qualiscore_raw-model_LC.worst_quali)/(model_LC.best_quali-model_LC.worst_quali)
    qualiscore_std = 50*( qualiscore_raw - model_LC.qualimean) / model_LC.qualistd
    Totalscore = quantscore_std*model_LC.quantweight + qualiscore_std *model_LC.qualiweight
    Totalscore_pct = (Totalscore-model_LC.worst_score)/(model_LC.best_score-model_LC.worst_score)

    if Totalscore < model_LC.cutoff:
        logitPD = model_LC.intercept1 + model_LC.slope1*Totalscore
    else:
        logitPD = model_LC.intercept2 + model_LC.slope2*Totalscore
 
    PD = 100*np.exp(logitPD)/(1+np.exp(logitPD))
    Ratings = sum(model_LC.MS['new_low']<=(PD/100))

    pd_result = {
    'PD':PD,
    'Ratings':Ratings,
    'quant_pct':quant_pct,
    'quali_pct':quali_pct,
    'Totalscore_pct':Totalscore_pct,
    'quantfactor_pct':pl_quantfactor_pct,
    'qualifactor_pct':pl_qualifactor_pct,
    'invalid_neg':invalid_neg
    }
    print('The model PD is '+str(pd_result['PD']))
    print('The prelim PDRR from LC model is '+str(pd_result['Ratings']))
    print('\n')
    while pd_result['invalid_neg']:
        print(pd_result['invalid_neg'].pop())
        print('\n')
    
    print('Quantitative as a % of possible = '+ str(round(100*pd_result['quant_pct']))+'%')
    print('\n')
    print('Qualitative as a % of possible = '+ str(round(100*pd_result['quali_pct']))+'%')    
    print('\n')
    print('Totalscore as a % of possible = '+ str(round(100*pd_result['Totalscore_pct']))+'%')


    df_plot = pd.DataFrame({'Best Score Percentage':pd_result['quantfactor_pct'], 'Factors':model_LC.quant_factor})
    fig = plt.figure()
    ax=sns.barplot(x="Best Score Percentage", y="Factors", data=df_plot)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_yticks((0.9,0.7,0.5,0.3,0.1))
    pl_cat = ['Profitability', 'Cash flow leverage', 'Size', 'Balance sheet leverage', 'Debt Service']
    ax2.set_yticklabels([str(round(x[1]*100))+'% '+x[0] for x in list(zip(pl_cat,pd_result['quantfactor_pct']))])
    plt.savefig(cus_name+'_quantpct_LC.png', bbox_inches='tight')

    
    
    df_plot = pd.DataFrame({'Best Score Percentage':pd_result['qualifactor_pct'], 'Factors':model_LC.quali_factor})
    fig = plt.figure()
    ax=sns.barplot(x="Best Score Percentage", y="Factors", data=df_plot)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_yticks((0.9,0.7,0.5,0.3,0.1))
    ax2.set_yticklabels([str(round(x*100))+'%' for x in pd_result['qualifactor_pct']])
    plt.savefig(cus_name+'_qualipct_LC.png', bbox_inches='tight')


interact_manual.opts['manual_name'] = 'LC model'
style = {'description_width': 'initial'}
interact_manual(LC_cni, 
    cus_name=widgets.Text(
    value='Company',
    description='Customer Name:',
    disabled=False
),NetSales=widgets.FloatText(
    value=1.0,
    description='Net Sales',
    disabled=False, style=style
),TotalDebt=widgets.FloatText(
    value=1.0,
    description='Total Debt',
    disabled=False, style=style
),EBITDA=widgets.FloatText(
    value=1.0,
    description='EBITDA',
    disabled=False, style=style
),TotalAssets=widgets.FloatText(
    value=1.0,
    description='Total Assets',
    disabled=False, style=style    
),Capitalization=widgets.FloatText(
    value=1.0,
    description='Capitalization',
    disabled=False, style=style
),InterestExpense=widgets.FloatText(
    value=1.0,
    description='Interest Expense',
    disabled=False, style=style
),quali1=widgets.Dropdown(
    options=['A', 'B', 'C', 'D'],
    value='A',
    description='quali1:  '+model_LC.quali_factor[0],
    disabled=False, style=style
),quali2=widgets.Dropdown(
    options=['A', 'B', 'C', 'D'],
    value='A',
    description='quali2:  '+model_LC.quali_factor[1],
    disabled=False, style=style
),quali3=widgets.Dropdown( 
    options=['A', 'B', 'C', 'D', 'E'],
    value='A',
    description='quali3:  '+model_LC.quali_factor[2],
    disabled=False, style=style
),quali4=widgets.Dropdown(
    options=['A', 'B', 'C'],
    value='A',
    description='quali4:  '+model_LC.quali_factor[3],
    disabled=False, style=style
),quali5=widgets.Dropdown(
    options=['A', 'B', 'C'],
    value='A',
    description='quali5:  '+model_LC.quali_factor[4],
    disabled=False, style=style
))from ipywidgets import interact, interactive, fixed, interact_manual,FloatSlider
import ipywidgets as widgets



def old_cni(cus_name='Company',quant1=0.0,quant2=0.0, COP=1.0, quant3=0.0,quant4=0.0, TNW=1.0, quant5=0.0,quali1='A',quali2='A',quali3='A',quali4='A'):
    
    invalid_neg = []
    if (quant2<0) & (COP<0):
        invalid_neg.append('quant2 triggers Invalid Negative treatment')
        quant2 = model_old.cap[1]
    if (quant4<0) & (TNW<0):
        invalid_neg.append('quant4 triggers Invalid Negative treatment')
        quant4 = model_old.cap[3]

    pl_quant = [quant1,quant2,quant3,quant4,quant5]
    pl_quali = [quali1,quali2,quali3,quali4]

    # cap/floor for quant factors:
    for i, col in enumerate(model_old.quant_factor):
        pl_quant[i] = np.clip(pl_quant[i], model_old.floor[i], model_old.cap[i])        

    # quant factors transformation:
    for i, col in enumerate(model_old.quant_factor):
        if model_old.quant_log[i]:
            pl_quant[i] = np.log(pl_quant[i])

    # quant factors normalization:
    for i, col in enumerate(model_old.quant_factor):
        pl_quant[i]  = 50*(pl_quant[i] - model_old.doc_mean[i]) / model_old.doc_std[i]      
        
    # quant factors flip sign:  
    for i, col in enumerate(model_old.quant_factor):
        pl_quant[i] = pl_quant[i] * model_old.quant_multiplier[i]    


    for i, col in enumerate(model_old.quali_factor):
        pl_quali[i] = model_old.qualimapping[i][pl_quali[i]]


    pl_quant = np.array(pl_quant)
    pl_quali = np.array(pl_quali)


    pl_quantfactor_pct = (pl_quant-np.array(model_old.worst_quantfactor))/(np.array(model_old.best_quantfactor)-np.array(model_old.worst_quantfactor))
    pl_qualifactor_pct = (pl_quali-np.array(model_old.worst_qualifactor))/(np.array(model_old.best_qualifactor)-np.array(model_old.worst_qualifactor))

    quantscore_raw = (model_old.quant_weight * pl_quant).sum()
    quant_pct = (quantscore_raw-model_old.worst_quant)/(model_old.best_quant-model_old.worst_quant)
    quantscore_std = 50*( quantscore_raw - model_old.quantmean) / model_old.quantstd

    qualiscore_raw = (model_old.quali_weight * pl_quali).sum()
    quali_pct = (qualiscore_raw-model_old.worst_quali)/(model_old.best_quali-model_old.worst_quali)
    qualiscore_std = 50*( qualiscore_raw - model_old.qualimean) / model_old.qualistd
    Totalscore = quantscore_std*model_old.quantweight + qualiscore_std *model_old.qualiweight
    Totalscore_pct = (Totalscore-model_old.worst_score)/(model_old.best_score-model_old.worst_score)

    if Totalscore < model_old.cutoff:
        logitPD = model_old.intercept1 + model_old.slope1*Totalscore
    else:
        logitPD = model_old.intercept2 + model_old.slope2*Totalscore
 
    PD = 100*np.exp(logitPD)/(1+np.exp(logitPD))
    Ratings = sum(model_old.MS['new_low']<=(PD/100))

    pd_result = {
    'PD':PD,
    'Ratings':Ratings,
    'quant_pct':quant_pct,
    'quali_pct':quali_pct,
    'Totalscore_pct':Totalscore_pct,
    'quantfactor_pct':pl_quantfactor_pct,
    'qualifactor_pct':pl_qualifactor_pct,
    'invalid_neg':invalid_neg
    }
    print('The model PD is '+str(pd_result['PD']))
    print('The prelim PDRR from old CnI model is '+str(pd_result['Ratings']))
    print('\n')
    while pd_result['invalid_neg']:
        print(pd_result['invalid_neg'].pop())
        print('\n')
    
    print('Quantitative as a % of possible = '+ str(round(100*pd_result['quant_pct']))+'%')
    print('\n')
    print('Qualitative as a % of possible = '+ str(round(100*pd_result['quali_pct']))+'%')    
    print('\n')
    print('Totalscore as a % of possible = '+ str(round(100*pd_result['Totalscore_pct']))+'%')


    df_plot = pd.DataFrame({'Best Score Percentage':pd_result['quantfactor_pct'], 'Factors':model_old.quant_factor})
    fig = plt.figure()
    ax=sns.barplot(x="Best Score Percentage", y="Factors", data=df_plot)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_yticks((0.9,0.7,0.5,0.3,0.1))
    pl_cat = ['Profitability', 'Cash flow leverage', 'Size', 'Balance sheet leverage', 'Liquidity']
    ax2.set_yticklabels([str(round(x[1]*100))+'% '+x[0] for x in list(zip(pl_cat,pd_result['quantfactor_pct']))])
    plt.savefig(cus_name+'_quantpct_old.png', bbox_inches='tight')

    
    
    df_plot = pd.DataFrame({'Best Score Percentage':pd_result['qualifactor_pct'], 'Factors':model_old.quali_factor})
    fig = plt.figure()
    ax=sns.barplot(x="Best Score Percentage", y="Factors", data=df_plot)
    ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis
    ax2.set_yticks((0.87,0.62,0.37,0.12))
    ax2.set_yticklabels([str(round(x*100))+'%' for x in pd_result['qualifactor_pct']])
    plt.savefig(cus_name+'_qualipct_old.png', bbox_inches='tight')




interact_manual.opts['manual_name'] = 'Old CnI model'
style = {'description_width': 'initial'}
interact_manual(old_cni, 
    cus_name=widgets.Text(
    value='Company',
    description='Customer Name:',
    disabled=False
),quant1=widgets.FloatText(
    value=0,
    description='quant1:  '+model_old.quant_factor[0],
    disabled=False, style=style
),quant2=widgets.FloatText(
    value=0,
    description='quant2:  '+model_old.quant_factor[1],
    disabled=False, style=style
),COP=widgets.FloatText(
    value=1.0,
    description='Cash Operating Profit',
    disabled=False, style={'description_width': '75%'}
),quant3=widgets.FloatText(
    value=0,
    description='quant3:  '+model_old.quant_factor[2],
    disabled=False, style=style    
),quant4=widgets.FloatText(
    value=0,
    description='quant4:  '+model_old.quant_factor[3],
    disabled=False, style=style
),TNW=widgets.FloatText(
    value=1.0,
    description='Tangible Net Worth',
    disabled=False, style={'description_width': '75%'}
),quant5=widgets.FloatText(
    value=0,
    description='quant5:  '+model_old.quant_factor[4],
    disabled=False, style=style
),quali1=widgets.Dropdown(
    options=['A', 'B', 'C', 'D'],
    value='A',
    description='quali1:  '+model_old.quali_factor[0],
    disabled=False, style=style
),quali2=widgets.Dropdown(
    options=['A', 'B', 'C', 'D'],
    value='A',
    description='quali2:  '+model_old.quali_factor[1],
    disabled=False, style=style
),quali3=widgets.Dropdown( 
    options=['A', 'B', 'C', 'D', 'E','F'],
    value='A',
    description='quali3:  '+model_old.quali_factor[2],
    disabled=False, style=style
),quali4=widgets.Dropdown(
    options=['A', 'B', 'C'],
    value='C',
    description='quali4:  '+model_old.quali_factor[3],
    disabled=False, style=style
));# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 14:07:53 2018

@author: ub71894 (4e8e6d0b), CSG
"""

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\src_monitoring")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
import seaborn as sns
import pickle
import matplotlib.pyplot as plt

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')
# load model setting
model_LC = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_LC.pkl','rb'))
model_MM = pickle.load(open(r'C:\Users\ub71894\Documents\DevRepo\Files\model_MM.pkl','rb'))




def manual_input(model):
    if model.model_name == "CNI_LargeCorporate":
        pl_names = ["EBITDA",
                    "NetSales",
                    "TotalDebt",
                    "TotalAsset",
                    "Capitalization",
                    "InterestExpense",
                    "SSOR",
                    "Level of Waivers or Covenant Modifications",
                    "Management Quality",
                    "Vulnerability to Changes",
                    "Access to Outside Capital"]
    else:
        pl_names = ["NOP",xxx
                    "NetSales",
                    "TotalDebt",
                    "UBEBITDA",
                    "Capitalization",
                    "ECE", xxx
                    "TotalLiability",
                    "TangNW", xxx
                    "TotalAsset"]

    return (factors)

def file_input(model, spreadsheet_file):
    return (factors)


def gen_prelim_rating(model, factors):



x= input("first one is")
y= input("second one is")
z= input("third one is")

print(x+y+z)


1. Net Operating Profit ($)
2. Net Sales ($)
3. Total Debt ($)
4. UB EBITDA ($)
5. Tangible Net Worth ($)
6. Capitalization ($)
7. Ending Cash and Equivalents ($)
8. Total Assets ($)
9. Total Liabilities ($)

1. Strength of other SORs (excluding PSOR) to prevent default
2. Level of Waiver Modification
3. Management Response to Adverse Conditions
4. Vulnerability to Changes
5. Management Quality
import os
import sys
import pandas as pd
import numpy as np
import warnings
import pickle
import seaborn as sns
from matplotlib import pyplot as plt

os.chdir(r"C:\Users\ub71894\Documents\Projects\CNI\monitoring\src")
sys.path.append(r'C:\Users\ub71894\Documents\DevRepo')
from PDScorecardTool.PDModel import PDModel
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", category=FutureWarning)

MS = pd.read_excel(r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx')

# load model setting
quant_factor = ['Net_Profit_Margin','Total_Debt_By_COP','Total_Assets','Total_Liab_by_Tang_Net_Worth','End_Cash_Equiv_By_Tot_Liab']
quali_factor = ['Strength_SOR_Prevent_Default','Level_Waiver_Covenant_Mod','Mgmt_Resp_Adverse_Conditions','Vulnerability_To_Changes']
PDInfo_file = r'C:\Users\ub71894\Documents\DevRepo\Files\PDModelParameters.xlsx'
masterscale_file = r'C:\Users\ub71894\Documents\DevRepo\Files\MasterScale.xlsx'
model_name = 'C&I'; version = 1.2
model_old = PDModel(PDInfo_file, model_name, version, quant_factor, quali_factor, masterscale_file)
model_old.save(r'C:\Users\ub71894\Documents\DevRepo\Files\model_old.pkl')


model_LC = pickle.load(open(r'C:\Users\ub71894\Documents\Projects\CNI\src\spec\model_af_calib.pkl','rb'))
model_LC.quali_factor[:2] = model_old.quali_factor[:2]
model_LC.quali_factor[3] = model_old.quali_factor[3]
model_LC.save(r'C:\Users\ub71894\Documents\DevRepo\Files\model_LC.pkl')
['calculate_pct.py', 'header_calculator.py', 'LC_calculator.py', 'old_calculator.py', 'prototype_tool.py', 'update_model_spec.py']
[490, 566, 739, 905, 982, 1013]

