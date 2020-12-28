"""
Created on Fri Aug 14 15:53:13 2015

@author: ub71894
"""

import os,sqlite3
import pandas as pd

os.chdir(r"C:\Users\ub71894\Documents\code\Python") #change this to the directory where your csv files are stored
txt_files={} # we store the dataframes in a dictionary

dir_name=r'C:\Users\ub71894\Documents\data\REIG_TOPS\db'
base_filename='CMO South'
filename_suffix = '.db'
filename = os.path.join(dir_name, base_filename + filename_suffix)
con = sqlite3.connect(filename)
cur = con.cursor()

executestring = 'SELECT * FROM CMD_PROPERTY_INFO_HISTORY'

cur.execute(executestring)

names = list(map(lambda x: x[0], cur.description))
data=pd.DataFrame(cur.fetchall(),columns=names)




#rows = cur.fetchall()
#for row in rows:
#    print(row)
    
con.close()


