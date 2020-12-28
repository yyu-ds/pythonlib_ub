from sklearn.metrics import roc_auc_score


from sklearn.datasets import make_hastie_10_2
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble.partial_dependence import plot_partial_dependence

#%% easy emample
X, y = make_hastie_10_2(random_state=0)
X_train, X_test = X[:2000], X[2000:]
y_train, y_test = y[:2000], y[2000:]

clf = GradientBoostingClassifier(n_estimators=100, learning_rate=1.0, max_depth=1, random_state=0).fit(X_train, y_train)
clf.score(X_train, y_train)               

yest = clf.predict(X_train)
roc_auc_score(y_train,yest)



#%% CRE PERM data
X_train = combo.iloc[:,:9]
y_train = combo.iloc[:,9]
clf = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1, max_depth=10, random_state=0,subsample=0.5).fit(X_train, y_train)

yest = clf.predict(X_train)
roc_auc_score(y_train,yest)

features = [0,1,2,3,(1,3)]
fig, axs = plot_partial_dependence(clf, X_train, features, feature_names=('Eff_Gross_Income','LTV','Tot_cur_UBOC_Comm_over_NOI','Sbmkt_Vacancy_Rate_Pct')) 




#%%

from sklearn.ensemble import GradientBoostingClassifier


clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1,max_depth=10, random_state=0).fit(X_train, y_train)
features = [1,3,(0,1)]
fig, axs = plot_partial_dependence(clf, X_train, features, feature_names=('Eff_Gross_Income', 'LTV')) 


#%%



















#%%
name=['AR_def_in','AR_PDRR_in','within2_PDRR_in','within1_PDRR_in','AR_PDRR_out','within2_PDRR_out','within1_PDRR_out,']
result = [AR_def_in,AR_PDRR_in,within2_PDRR_in,within1_PDRR_in,AR_PDRR_out,within2_PDRR_out,within1_PDRR_out]
df = pd.DataFrame.from_dict(dict(zip(name,result)))
df=df[name]import numba
