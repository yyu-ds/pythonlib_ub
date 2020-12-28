#%%

from sas7bdat import SAS7BDAT
import pandas as pd 
import os

os.chdir(r"C:\Users\ub71894\Documents\code\python\testcode")


#old mehtod
f = SAS7BDAT('cola.sas7bdat') 
ff= f.to_data_frame()


#new: doesn't work

df = pd.read_sas("cola.sas7bdat") 
