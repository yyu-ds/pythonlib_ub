import pandas as pd
import numpy as np 
#import scipy as sp 
#from sklearn.linear_model import LogisticRegression, LinearRegression
import statsmodels.api as sm 
import seaborn as sns
#import statsmodels.formula.api as smf


x = np.random.randn(1000,3)
alpha=4.5; beta = pd.Series([11.3,4.23])
x=pd.DataFrame(x)
y_true = alpha + x[0]*beta[0] + x[1]*beta[1] 
y = y_true + x[2]

inde = sm.add_constant(x[[0,1]],prepend = True)

mod = sm.OLS(y, inde)
res = mod.fit()

ybar = y.mean()
SST = sum((y-ybar)**2)
SSE = sum((y-res.fittedvalues)**2)

SSR = sum((ybar-res.fittedvalues)**2)

res.summary()

dat = pd.concat([y,inde],axis=1,names='haha')
dat.columns = ['ysome','const','x1','x2']

sns.regplot(x="x1",y="ysome",data=dat)
#%%
import matplotlib.pyplot as plt
from statsmodels.sandbox.regression.predstd import wls_prediction_std


prstd, iv_l, iv_u = wls_prediction_std(res)

fig, ax = plt.subplots(figsize=(8,6))

ax.plot(x[0], y, 'o', label="data")
ax.plot(x[0], y_true, 'bo', label="True")
ax.plot(x[0], res.fittedvalues, 'ro', label="OLS")
ax.plot(x[0], iv_u, 'ro')
ax.plot(x[0], iv_l, 'ro')
ax.legend(loc='best');




#%% experiment:

x = np.random.randn(1000,3)
x[0] =  x[0]*3+2; x[1] =  x[1]*2+5;

alpha=14.5; beta = pd.Series([11.3,4.23])
x=pd.DataFrame(x)
y_true = alpha + x[0]*beta[0] + x[1]*beta[1] 
y = y_true + x[2]

# with intercept:
inde = sm.add_constant(x[[0,1]],prepend = True)
mod = sm.OLS(y, inde)
res = mod.fit()
res.summary()



#without intercept
mod = sm.OLS(y, x[[0,1]])
res = mod.fit()
res.summary()

xx=x.copy()
xx[0]= x[0]*res.params[0]
xx[1]= x[1]*res.params[1]

inde = sm.add_constant(xx[[0,1]],prepend = True)
mod = sm.OLS(y, inde)
res = mod.fit()
res.summary()


x12= x[0]*res.params[0]+x[1]*res.params[1]
inde = sm.add_constant(x12,prepend = True)
mod = sm.OLS(y, inde)
res = mod.fit()

res.summary()




#%%
plt.subplot(221)
plt.scatter(dat.Totalscore, dat.Final_PD_Risk_Rating, s=25)    
plt.subplot(224)
plt.scatter(dat.Totalscore, dat.Prelim_PD_Risk_Rating_Uncap, s=25)    


# works
plt.subplot(221)
sns.scatterplot(x='quantscore', y='Prelim_PD_Risk_Rating_Uncap', data=dat)
plt.subplot(224)
sns.scatterplot(x='quantscore', y='Final_PD_Risk_Rating', data=dat)


# works
ax=plt.subplot(221)
sns.regplot(x='quantscore', y='Prelim_PD_Risk_Rating_Uncap', data=dat)
plt.subplot(224)
plt.scatter(dat.quantscore, dat.Prelim_PD_Risk_Rating_Uncap, s=25)    


# works
fig, ax = plt.subplots(3,3, sharex='col')
sns.regplot(x='quantscore', y='Prelim_PD_Risk_Rating_Uncap', data=dat,ax=ax[0,1])
ax[2,1].scatter(dat.quantscore, dat.Prelim_PD_Risk_Rating_Uncap, s=25) 
