
import pandas as pd
import statsmodels.api as sm 
import statsmodels.formula.api as smf

data = pd.read_table('CHDAGE.txt', sep='\s+')


#%% Using statsmodels.api.Logit
dat=data.copy()
dat['const'] = 1
x=sm.add_constant(dat['AGE'],prepend = True)
y=(dat.CHD)

logit = sm.Logit(y, x)
result = logit.fit()
print (result.summary())

'''            Logit Regression Results                           
==============================================================================
Dep. Variable:                    CHD   No. Observations:                  100
Model:                          Logit   Df Residuals:                       98
Method:                           MLE   Df Model:                            1
Date:                Fri, 13 Nov 2015   Pseudo R-squ.:                  0.2145
Time:                        11:24:53   Log-Likelihood:                -53.677
converged:                       True   LL-Null:                       -68.331
                                        LLR p-value:                 6.168e-08
==============================================================================
                 coef    std err          z      P>|z|      [95.0% Conf. Int.]
------------------------------------------------------------------------------
const         -5.3095      1.134     -4.683      0.000        -7.531    -3.088
AGE            0.1109      0.024      4.610      0.000         0.064     0.158
==============================================================================
'''




#%% Using statsmodels.api.GLM

dat=data.copy()
dat['const'] = 1
x=sm.add_constant(dat['AGE'],prepend = True)
y=(dat.CHD)


glm_lr = sm.GLM(y, x, family=sm.families.Binomial())
glm_results = glm_lr.fit()
print(glm_results.summary())


'''
                 Generalized Linear Model Regression Results                  
==============================================================================
Dep. Variable:                    CHD   No. Observations:                  100
Model:                            GLM   Df Residuals:                       98
Model Family:                Binomial   Df Model:                            1
Link Function:                  logit   Scale:                             1.0
Method:                          IRLS   Log-Likelihood:                -53.677
Date:                Fri, 13 Nov 2015   Deviance:                       107.35
Time:                        11:24:05   Pearson chi2:                     102.
No. Iterations:                     6                                         
==============================================================================
                 coef    std err          z      P>|z|      [95.0% Conf. Int.]
------------------------------------------------------------------------------
const         -5.3095      1.134     -4.683      0.000        -7.531    -3.088
AGE            0.1109      0.024      4.610      0.000         0.064     0.158
==============================================================================
'''
glm_results.predict([[1,20],[1,23],[1,24]])

glm_results.mu[:3]



#%% Using statsmodels.formula.api.glm


dat=data.copy()
dta = dat[['CHD','AGE']]
endog = dta['CHD']
formula = 'CHD ~ AGE'

glm_lr = smf.glm(formula=formula, data=dta, family=sm.families.Binomial())
res = glm_lr.fit()
print(res.summary())
 
'''
 Generalized Linear Model Regression Results                  
==============================================================================
Dep. Variable:                    CHD   No. Observations:                  100
Model:                            GLM   Df Residuals:                       98
Model Family:                Binomial   Df Model:                            1
Link Function:                  logit   Scale:                             1.0
Method:                          IRLS   Log-Likelihood:                -53.677
Date:                Fri, 13 Nov 2015   Deviance:                       107.35
Time:                        14:00:02   Pearson chi2:                     102.
No. Iterations:                     6                                         
==============================================================================
                 coef    std err          z      P>|z|      [95.0% Conf. Int.]
------------------------------------------------------------------------------
Intercept     -5.3095      1.134     -4.683      0.000        -7.531    -3.088
AGE            0.1109      0.024      4.610      0.000         0.064     0.158
==============================================================================

'''
#%% Using scikit-learn
from sklearn import linear_model

dat=data.copy()
dta = dat[['CHD','AGE']]

model = linear_model.LogisticRegression(fit_intercept=False, penalty='l2', dual=False, tol=0.0001, C=10000)
dat['const'] = 1
x=dat[['const','AGE']]
y=dat['CHD']
model.fit(x,y)
model.coef_






