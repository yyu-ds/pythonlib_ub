# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 16:56:38 2015

@author: ub71894  modified based on ub69401
"""

import re
import os,csv, sqlite3

#define path name to put the database file
dir_name=r'C:\Users\ub71894\Documents\Python Scripts'
#define result file name
base_filename='new2'
filename_suffix = '.db'
filename = os.path.join(dir_name, base_filename + filename_suffix)
#create and connect to db file
sqlite_file = filename
con = sqlite3.connect(filename)
cur = con.cursor()

path = r'C:\Users\ub71894\Documents\Python Scripts'
for root, dirs, files in os.walk(path): #go through all files, subdirectories
    for name in files: #loop over files
        if name.endswith((".txt")): #but only open .txt files
            searchObj = re.search( r'_(.*?).txt$' , str(name), re.M|re.I) #strip out the group name
            print(searchObj.group(1)) #check if it is correct
            table_name = searchObj.group(1) #group name becomes the table name
            with open(os.path.join(root,name),"rt",encoding="utf8") as fin: #open each txt for reading
                dr = csv.reader(fin,delimiter='|') #use csv.reader to read file
                columns1 = next(dr) #read in the header line 
                columns2 = columns1[4:] #read header line, ignore first 4 elements as meta-data
                ncol     = len(columns1)-4 #adjust number of columns
                # column_list = "(" #build column names and question string
                # questionstring ="("
                # for n in range(ncol):
                #     if n+1 < (ncol):
                #         column_list = column_list+str(columns2[n])+", "
                #         questionstring = questionstring +"?," 
                #     else:
                #         column_list = column_list+str(columns2[n])+")"
                #         questionstring = questionstring + "?)"
                # print(name," ",ncol)
                # print(column_list)
                #fin.seek(0) #go back to the beginning of the file
                executestring = "DROP TABLE IF EXISTS "+str(table_name)+";CREATE TABLE "+str(table_name)+" ("+ ','.join(map(str,columns2))+ ");" # modified
                cur.executescript(executestring) #create table if it does not already exist
                for row in dr:  #write remaining rows into the table
                    to_db = [str(row[n]) for n in range(ncol)]
                    writestring = "INSERT INTO "+str(table_name)+" ("+ ','.join(map(str,columns2))+ ") VALUES "+ " ("+ ','.join('?'*len(columns2))+ ");"# modified
                    cur.executemany(writestring, (to_db,))
                    con.commit()
con.close()

