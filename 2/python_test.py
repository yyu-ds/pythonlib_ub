# -*- coding: utf-8 -*-
"""
Created on Mon Jun 10 09:34:17 2019

@author: ub71894
"""

#%% use coin to generate Uniform (1,20) discrete number
import numpy as np
import pandas as pd
from scipy.stats import bernoulli
import seaborn as sns
import matplotlib.pyplot as plt
from math import pow

N=100000
pl_num=[]
for i in range(N):
    s=0
    for j in range(5):
        #s+= pow(2,j)*bernoulli.rvs(0.5,size=1)[0]
        s+= pow(2,j)*np.random.binomial(1,0.5) # faster
    if  s>19:
        continue
    else:
        pl_num.append(1+s)
        
    
np.array(pl_num).mean()
df= pd.DataFrame()
df['num']  = pl_num

a=df['num'].value_counts().to_frame()
a.reset_index(drop=False, inplace=True)

sns.barplot(x='index', y='num', data=a)
plt.bar(a['index'], a.num)



#%% combination function
from scipy.special import comb
comb(n,r)

import operator as op
from functools import reduce
def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer / denom



from math import factorial as fact
def ncr2(n, r):
    r = min(r, n-r)
    numer = fact(n)
    denom = fact(r)*fact(n-r)
    return numer / denom



def ncr_mul(n, pl_r):
    numer = fact(n)
    denom = 1
    for num in pl_r:
        denom *= fact(num)        
    return numer / denom



#%% 
import numpy as np
from numba import jit
@jit
def sim(N):
    pl_result =[]
    for i in range(N):
        a = np.random.randint(1,10001,100)
        b = np.random.randint(1,10001,100)
        s=0
        for num in b:
            if num in a:
                s+=1
        pl_result.append(s)
    return (pl_result)


np.array(sim(500000)).mean()
sim(100)

#%% shuffle 1,2,...N and in the shuffled list, what's the expect number of pair
#(n,n+1) that list[n+1] = list[n]+1, answer = (N-1)/N
 
@jit
def simu(N):
    arr = np.arange(N)
    np.random.shuffle(arr)
    Y=0
    for i in range (N-1):
        if (arr[i+1] == arr[i]+1):
            Y+=1
    return(Y)
s=0
N=10000000
for i in range(N):
   s+=simu(5)
s/N
#%% plot random number 
import matplotlib.pyplot as plt
y = np.random.rand(1000)
x = np.arange(1000)

fig, ax = plt.subplots()
ax.scatter(x,y)


#%% 10 normal rv's max's exp
@jit
def simu(N):
    s=0
    for i in range(N):
        x = np.random.randn(10)
        s+=max(x)
    return (s/N)


#%% 
from scipy.stats import norm
norm.cdf(2)
norm.ppf(.975)
# 1.959963984540054
norm.ppf(.975, 1, 2)
# 4.919927969080108

from scipy.stats import f
f.ppf(0.975, 32, 59)
# 1.8022087474311501
f.cdf(2, 32, 59)

from scipy.stats import chi2
df=5
x = np.linspace(chi2.ppf(0.01, df),chi2.ppf(0.99, df), 100)
fig, ax = plt.subplots()
ax.plot(x, chi2.pdf(x, df),'r-', lw=5, alpha=0.6, label='chi2 pdf')


from scipy.stats import t
df = 30
mean, var, skew, kurt = t.stats(df, moments='mvsk')

t.ppf(0.975, 10)
#2.2281388519649385
#%% 
dat
'''
Out[147]: 
     id  month  times
0    yu      1    100
1  wang      1    100
2  wang      2    200
3  wang      3    300
4   sun      1    100
5   sun      2    200
6   sun      3    300
7   sun      4    400
'''
aa= dat.groupby(by=['id']).mean()['times']

#%% Fib

# Recurssive program to find n'th fibonacci number 
def fib(n): 
    if n <= 1: 
        return n 
    return fib(n-1) + fib(n-2) 

#%% 2 sample test
from scipy.stats import ttest_ind
a = np.random.randn(1000)+0.5
b = np.random.randn(1000)+0.4
ttest_ind(a,b)  
ttest_ind(a,b, equal_var=False)    

# rank sum / Wilcoxon test
from scipy.stats import ranksums
ranksums(a,b)

from scipy.stats import wilcoxon  # signed rank test
a = np.random.randn(1000)+0.5
b = np.random.randn(1000)+0.4
c=a-b
wilcoxon(c)

from scipy.stats import ks_2samp
ks_2samp(a, b)# power is low sometime



#%% other tests
from scipy.stats import levene
a = np.random.randn(1000)+0.3
b = np.random.randn(1000)+0.4
levene(a,b)
from scipy.stats import f
F = a.var() / b.var()
f.cdf(F, 999,999)
from scipy.stats import f_oneway
f_oneway(a,b)  # equilevent with t test

from scipy.stats import chisquare
chisquare([16, 18, 16, 14, 12, 12]) # assume uniform dist
chisquare([16, 18, 16, 14, 12, 12], f_exp=[14.66,]*6)
chisquare([16, 18, 16, 14, 12, 12], f_exp=[16, 16, 16, 16, 16, 8])


# normality test
from scipy.stats import kstest, shapiro, normaltest
a = np.random.randn(1000)
kstest(a, 'norm')
kstest(a, 't', args=[10])
shapiro(a)
normaltest(a) # D’Agostino




#%% 
import statsmodels.api as sm
import numpy as np
import pandas as pd
df = pd.DataFrame()
df['x1'] = np.random.rand(1000)
df['x2']= 3*np.random.randn(1000)

y = 5*df.x1 + 2*df.x2 + np.random.randn(1000)
df['y']=y
X = sm.add_constant(df[['x1','x2']])
ss=sm.OLS(y, X).fit()
ss.summary()


#%% ANOVA
#http://www.statsmodels.org/devel/generated/statsmodels.stats.anova.anova_lm.html


#%% truncated normal dist
import numpy as np
from scipy.stats import norm
from scipy.optimize import root

mu = 1
sigma = 4
x= np.random.normal(mu, sigma,100000)

T = -5
y = x[x<T]

Ex = y.mean()
EVar = y.var()

phi = norm.pdf
PHI = norm.cdf


def fun1(mu, sigma):
    beta = (T- mu)/sigma
    return (mu-sigma*phi(beta)/PHI(beta) - Ex )
def fun2(mu, sigma):
    beta = (T- mu)/sigma
    return (sigma**2*(1-beta*phi(beta)/PHI(beta)-phi(beta)**2/PHI(beta)**2) - EVar)

def ssfun(x):
    return ([fun1(x[0],x[1]), fun2(x[0],x[1])])

root(ssfun, [0.5,0.5])




mu=1
sigma=4
beta = (T- mu)/sigma
mu-sigma*phi(beta)/PHI(beta)
sigma**2*(1-beta*phi(beta)/PHI(beta)-phi(beta)**2/PHI(beta)**2)

Ex
EVar
