# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 15:53:13 2015

@author: ub69401
"""

import os,sqlite3

os.chdir(r"C:\Users\ub69401\Documents\compustat\database") #change this to the directory where your csv files are stored
txt_files={} # we store the dataframes in a dictionary

dir_name=r'C:\Users\ub69401\Documents\compustat\database'
base_filename='compustat'
filename_suffix = '.db'
filename = os.path.join(dir_name, base_filename + filename_suffix)
sqlite_file = filename
con = sqlite3.connect(filename)
cur = con.cursor()

COMPUSTAT = "'USA'"
executestring = "SELECT * FROM COMPANY WHERE LOC="+str(COMPUSTAT)

cur.execute(executestring)

rows = cur.fetchall()
for row in rows:
    print(row)
    
con.close()# -*- coding: utf-8 -*-
