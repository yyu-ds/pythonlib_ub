#%%
import numpy as np
from pandas import Series, DataFrame
import pandas as pd
from datetime import datetime

long = Series(np.random.randn(1000).cumsum(), index=pd.date_range('1/1/2000', periods=1000))
long.plot()
pd.rolling_mean(long,50).plot()



std50 = pd.rolling_std(long,50)
std50.plot()'''original example for checking how far GAM works
