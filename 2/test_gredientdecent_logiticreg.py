import pandas as pd
import numpy as np
from sklearn import linear_model
from sklearn import datasets
diabetes= datasets.load_diabetes()
dat= diabetes['data']
y = diabetes['target']>140

#%%
model = linear_model.LogisticRegression(fit_intercept=True, penalty='l2', dual=False, tol=0.0001, C=1000000000)
model.fit(dat,y)
model.coef_
model.intercept_

#%%
import statsmodels.api as sm 
dat2 = pd.DataFrame(dat, columns=['a','b','c','d','e','f','g','h','i','j'])
dat2['y'] = y 
x=sm.add_constant(dat2[['a','b','c','d','e','f','g','h','i','j']],prepend = True)
y=dat2['y']

logit = sm.Logit(y, x)
result = logit.fit()
print (result.summary())



#%%
X = dat.T;  Y = y.reshape((1,442))              
W_new = np.random.randn(10,1);    b_new=0
W_old = W_new+1;    b_old = 1

alpha=0.01 / 442
def sigmoid(z):
    return(1/(1+np.exp(-z)))
n=0
while np.linalg.norm(W_new-W_old)>0.0001:
    
#while n <= 10:
    W_old = W_new;      b_old = b_new; 
    A = sigmoid(np.dot(W_old.T,X)+b_old)
    W_new = W_old - alpha*np.dot(X,(A-Y).T)

    b_new = b_old - alpha*(A-Y).T.sum()

    cost = -np.dot(Y,np.log(A).T)-np.dot((1-Y),np.log(1-A).T)
    print("after "+str(n)+" iterations, the cost function is "+ str(cost))
    n +=1


W_new = np.array([1,-11,13,11,-32,22,-0.5,1,30,0]); W_new=W_new.reshape((10,1));    b_new=0
W_old = W_new+1;    b_old = 1
n=0
while np.linalg.norm(W_new-W_old)>0.0001:
    
#while n <= 10:
    W_old = W_new;      b_old = b_new; 
    A = sigmoid(np.dot(W_old.T,X)+b_old)
    W_new = W_old - alpha*np.dot(X,(A-Y).T)

    b_new = b_old - alpha*(A-Y).T.sum()

    cost = -np.dot(Y,np.log(A).T)-np.dot((1-Y),np.log(1-A).T)
    print("after "+str(n)+" iterations, the cost function is "+ str(cost))
    n +=1




W_new = np.zeros((10,1));    b_new=0
W_old = W_new+1;    b_old = 1
n=0
while np.linalg.norm(W_new-W_old)>0.0001:
    
#while n <= 10:
    W_old = W_new;      b_old = b_new; 
    A = sigmoid(np.dot(W_old.T,X)+b_old)
    W_new = W_old - alpha*np.dot(X,(A-Y).T)

    b_new = b_old - alpha*(A-Y).T.sum()

    cost = -np.dot(Y,np.log(A).T)-np.dot((1-Y),np.log(1-A).T)
    print("after "+str(n)+" iterations, the cost function is "+ str(cost))
    n +=1



#%% SGD
W_new = np.zeros((10,1));    b_new=0
W_new = np.array([1,-11,13,11,-32,22,-0.5,1,30,0]); W_new=W_new.reshape((10,1));    b_new=0
W_new = np.random.randn(10,1);    b_new=0

W_old = W_new+1;    b_old = 1
n=0; alpha=0.01

while np.linalg.norm(W_new-W_old)>0.00001:
    
    for i in range(442):       

        X_i = X[:,i].reshape((10,1)); Y_i = Y[0,i]
        W_old = W_new;      b_old = b_new; 
        A_i = sigmoid(np.dot(W_old.T,X_i)+b_old)
        W_new = W_old - alpha*X_i*(A_i-Y_i) 

        b_new = b_old - alpha*(A_i-Y_i).sum()

    A = sigmoid(np.dot(W_new.T,X)+b_new)
    cost = -np.dot(Y,np.log(A).T)-np.dot((1-Y),np.log(1-A).T)
    print("after "+str(n)+" iterations, the cost function is "+ str(cost))
    n +=1
