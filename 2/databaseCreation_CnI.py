# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 13:43:39 2020

@author: mua2a76
"""

#
# This script has the details and instructions used to build SQLite database and upload Compustat data
# 
#%%
# Step 1: Install SQLite and an editor such as SQLiteStudio
# The below will create a database named insurance032020 and 2 tables to hold the financials for all companies.
# You can check in the editor that the database appears in the file explorer.

#%%

import os, sqlite3, csv
from io import StringIO


dir_name=r'C:\Users\ru87118\Desktop\Compustat\Data'
os.chdir(dir_name)

base_filename='CnI091920_2'
filename_suffix = '.db'
filename = os.path.join(dir_name, base_filename + filename_suffix)
con = sqlite3.connect(filename)


with open(r'C:\Users\ru87118\Desktop\Compustat\Data\SQL\Financials_M_Z_create table.sql', 'r') as file:
    sql_create_Financials_M_Z_table = file.read().replace('\n', ' ')
    
with open(r'C:\Users\ru87118\Desktop\Compustat\Data\SQL\Financials_A_L_create table.sql', 'r') as file:
    sql_create_Financials_A_L_table = file.read().replace('\n', ' ')
    
with open(r'C:\Users\ru87118\Desktop\Compustat\Data\SQL\Company_create table.sql', 'r') as file:
    sql_create_Company_table = file.read()
    
c = con.cursor()

c.execute(sql_create_Financials_M_Z_table)
c.execute(sql_create_Financials_A_L_table)
c.execute(sql_create_Company_table)

con.commit()
c.close()
con.close()

#%%
# Step 2: Import the data in the text files to the two financials tables
#         First, extract the files f_co_afnd1V2 and f_co_afndv2V2 in folders with the same name to avoid special characters in windows folder names

data_dir_A_L = r'C:\Users\ru87118\Desktop\Compustat\Data'
filename_A_L = r'f_co_afnd1V2.txt'
remove_string_A_L = 'H|20200919-07:42:53|co_afnd1V2|6|'

file_A_L = open(os.path.join(data_dir_A_L, filename_A_L),'r').read().replace(remove_string_A_L,'').replace('|',',')
s = StringIO(file_A_L)
# Save a csv for direct manual inspection
with open('afnd1V2.csv', 'w') as f:
    for line in s:
        f.write(line)


table_name = 'Financials_A_L'
con = sqlite3.connect(filename)
cur = con.cursor()

with open(r'C:\Users\ru87118\Desktop\Compustat\Data\afnd1V2.csv',"rt",encoding="utf8") as fin: 
    dr = csv.reader(fin,delimiter=',',quoting=csv.QUOTE_NONE,lineterminator='\n') #use csv.reader to read file
    columns1 = next(dr) #read in the header line 
    ncol     = len(columns1)
    column_list = "(" #build column names and question string
    questionstring ="("
    for n in range(ncol):
        if n+1 < (ncol):
            column_list = column_list+str(columns1[n])+", "
            questionstring = questionstring +"?," 
        else:
            column_list = column_list+str(columns1[n])+")"
            questionstring = questionstring + "?)"
    print(column_list)
    for row in dr:  #write remaining rows into the table
        to_db = [str(row[n]) for n in range(ncol)]         
        writestring = "INSERT INTO "+str(table_name)+" "+column_list+" VALUES "+questionstring+";"
        cur.executemany(writestring, (to_db,))
        con.commit()
con.close()


#%%
# Step 2: Continuation
#

data_dir_M_Z = r'C:\Users\ru87118\Desktop\Compustat\Data'
filename_M_Z = r'f_co_afnd2V2.txt'
remove_string_M_Z = 'H|20200919-07:41:52|co_afnd2V2|6|'

file_M_Z = open(os.path.join(data_dir_M_Z, filename_M_Z),'r').read().replace(remove_string_M_Z,'').replace('|',',')
s = StringIO(file_M_Z)
# Save a csv for direct manual inspection
with open('afnd2V2.csv', 'w') as f:
    for line in s:
        f.write(line)

table_name = 'Financials_M_Z'
con = sqlite3.connect(filename)
cur = con.cursor()

with open(r'C:\Users\ru87118\Desktop\Compustat\Data\afnd2V2.csv',"rt",encoding="utf8") as fin: 
    dr = csv.reader(fin,delimiter=',',quoting=csv.QUOTE_NONE,lineterminator='\n') #use csv.reader to read file
    columns1 = next(dr) #read in the header line 
    ncol     = len(columns1)
    column_list = "(" #build column names and question string
    questionstring ="("
    for n in range(ncol):
        if n+1 < (ncol):
            column_list = column_list+str(columns1[n])+", "
            questionstring = questionstring +"?," 
        else:
            column_list = column_list+str(columns1[n])+")"
            questionstring = questionstring + "?)"
    print(column_list)
    for row in dr:  #write remaining rows into the table
        to_db = [str(row[n]) for n in range(ncol)]         
        writestring = "INSERT INTO "+str(table_name)+" "+column_list+" VALUES "+questionstring+";"
        cur.executemany(writestring, (to_db,))
        con.commit()
con.close()

#%%
# Combine the two tables Financilas_A_L and Fiancials_M_Z into Financials table
# Note that a full join is required here. Sqlite does not support it. This could lead to a minimal loss of data.
con = sqlite3.connect(filename)

with open(r'C:\Users\ru87118\Desktop\Compustat\Data\SQL\Financials_create table.sql', 'r') as file:
    sql_create_Financials_table = file.read().replace('\n', ' ')
    
c = con.cursor()

c.execute(sql_create_Financials_table)

con.commit()
c.close()
con.close()

#%%
# Populate the Company table
data_dir_company = r'C:\Users\ru87118\Desktop\Compustat\Data'
filename_company = r'f_company.txt'
remove_string_company = 'H|20200919-07:32:36|company|1|'

file_company = open(os.path.join(data_dir_company, filename_company),'r').read().replace(remove_string_company,'')
s = StringIO(file_company)
# Save a csv for direct manual inspection
with open('company.txt', 'w') as f:
    for line in s:
        f.write(line)

table_name = 'Company'
con = sqlite3.connect(filename)
cur = con.cursor()

with open(r'C:\Users\ru87118\Desktop\Compustat\Data\company.txt',"rt",encoding="utf8") as fin: 
    dr = csv.reader(fin,delimiter='|',quoting=csv.QUOTE_NONE,lineterminator='\n') #use csv.reader to read file
    columns1 = next(dr) #read in the header line 
    ncol     = len(columns1)
    column_list = "(" #build column names and question string
    questionstring ="("
    for n in range(ncol):
        if n+1 < (ncol):
            column_list = column_list+str(columns1[n])+", "
            questionstring = questionstring +"?," 
        else:
            column_list = column_list+str(columns1[n])+")"
            questionstring = questionstring + "?)"
    print(column_list)
    for row in dr:  #write remaining rows into the table
        to_db = [str(row[n]) for n in range(ncol)]         
        writestring = "INSERT INTO "+str(table_name)+" "+column_list+" VALUES "+questionstring+";"
        cur.executemany(writestring, (to_db,))
        con.commit()
con.close()
#%%
# Construct insurance financials table. This will hold financial data that will be used as input to the python scripts
#
con = sqlite3.connect(filename)

with open(r'C:\Users\ru87118\Desktop\Compustat\Data\SQL\CnIFinancials_create table.sql', 'r') as file:
    sql_create_CnIFinancials_table = file.read().replace('\n', ' ')
    
c = con.cursor()

c.execute(sql_create_CnIFinancials_table)

con.commit()
c.close()
con.close()
#
#
# End of Financial data section
#
#
#%%
# Rating data and related tables
#
data_dir_ratings = r'C:\Users\ru87118\Desktop\Compustat\Data'
filename_ratings = r'spRatingData.txt'

ratingsTableColumns=['ratingDetailId'	,'entitySymbolValue','instrumentSymbolValue'	,'securitySymbolValue',
                     'objectTypeId'	,'orgDebtTypeCode','ratingTypeCode','currentRatingSymbol','ratingSymbol',
                     'ratingDate','creditwatch','outlook','creditwatchDate','outlookDate','priorRatingSymbol',	
                     'priorCreditwatch','priorOutlook','ratingQualifier','regulatoryIndicator','regulatoryQualifier',
                     'ratingActionWord','CWOLActionWord','cwolInd','maturityDate','CUSIP','CINS','ISIN']

table_name = 'Ratings'
con = sqlite3.connect(filename)
cur = con.cursor()

with open(os.path.join(data_dir_ratings,filename_ratings),"rt",encoding="latin-1",newline=None) as fin: 
    contents = fin.readlines()
    contents = contents[0].split('#@#@#')
    contents = [line.replace('\'~\'', '|') for line in contents]
    columns1 = ratingsTableColumns 
    ncol     = len(columns1)
    column_list = "(" #build column names and question string
    questionstring ="("
    for n in range(ncol):
        if n+1 < (ncol):
            column_list = column_list+str(columns1[n])+", "
            questionstring = questionstring +"?," 
        else:
            column_list = column_list+str(columns1[n])+")"
            questionstring = questionstring + "?)"
    print(table_name," ",ncol)
    print(column_list)
 
    executestring = "CREATE TABLE IF NOT EXISTS "+str(table_name)+" "+column_list+";"
    cur.executescript(executestring) #create table if it does not already exist
    for row in contents:  #write remaining rows into the table
        row1=row.split('|')
        if row1[0]=='':
            row1=['' for n in range(len(columns1))]
        to_db = [str(row1[n]) for n in range(len(columns1))]         
        writestring = "INSERT INTO "+str(table_name)+" "+column_list+" VALUES "+questionstring+";"
        cur.executemany(writestring, (to_db,))
        con.commit()
con.close()

#%%
# Create auxiliary tables that link rating data to financials data
#
data_dir_crossCompanyRef = r'C:\Users\ru87118\Desktop\Compustat\Data'
filename_crossCompanyRef = r'CompanyCrossRef.txt'

crossCompanyRefTableColumns=['IdentifierId','companyId','identifierValue','identifierTypeId','startDate','endDate',
                     'activeFlag','PrimaryFlag']

table_name = 'crossCompanyRef'
con = sqlite3.connect(filename)
cur = con.cursor()

with open(os.path.join(data_dir_crossCompanyRef,filename_crossCompanyRef),encoding="utf8") as fin: 
    dr = csv.reader(fin,delimiter='|',quoting=csv.QUOTE_NONE,lineterminator='\n') #use csv.reader to read file
    columns1 = crossCompanyRefTableColumns 
    ncol     = len(columns1)
    column_list = "(" #build column names and question string
    questionstring ="("
    for n in range(ncol):
        if n+1 < (ncol):
            column_list = column_list+str(columns1[n])+", "
            questionstring = questionstring +"?," 
        else:
            column_list = column_list+str(columns1[n])+")"
            questionstring = questionstring + "?)"
    print(column_list)
    executestring = "CREATE TABLE IF NOT EXISTS "+str(table_name)+" "+column_list+";"
    cur.executescript(executestring)
    for row in dr:  
        to_db = [str(row[n]) for n in range(ncol)]         
        writestring = "INSERT INTO "+str(table_name)+" "+column_list+" VALUES "+questionstring+";"
        cur.executemany(writestring, (to_db,))
        con.commit()
con.close()

#%%
#
#
data_dir_ratingIdentifier = r'C:\Users\ru87118\Desktop\Compustat\Data'
filename_ratingIdentifier = r'spRatingIdentifier.txt'

ratingIdentifierTableColumns=['symbolId','symbolTypeId','symbolValue','objectId','relatedCompanyId','activeFlag','primaryFlag']

table_name = 'ratingIdentifier'
con = sqlite3.connect(filename)
cur = con.cursor()

with open(os.path.join(data_dir_ratingIdentifier,filename_ratingIdentifier),"rt",encoding="latin-1",newline=None) as fin: 
    contents = fin.readlines()
    contents = contents[0].split('#@#@#')
    contents = [line.replace('\'~\'', '|') for line in contents]
    columns1 = ratingIdentifierTableColumns 
    ncol     = len(columns1)
    column_list = "(" #build column names and question string
    questionstring ="("
    for n in range(ncol):
        if n+1 < (ncol):
            column_list = column_list+str(columns1[n])+", "
            questionstring = questionstring +"?," 
        else:
            column_list = column_list+str(columns1[n])+")"
            questionstring = questionstring + "?)"
    print(table_name," ",ncol)
    print(column_list)
 
    executestring = "CREATE TABLE IF NOT EXISTS "+str(table_name)+" "+column_list+";"
    cur.executescript(executestring) #create table if it does not already exist
    for row in contents:  #write remaining rows into the table
        row1=row.split('|')
        if row1[0]=='':
            row1=['' for n in range(len(columns1))]
        to_db = [str(row1[n]) for n in range(len(columns1))]         
        writestring = "INSERT INTO "+str(table_name)+" "+column_list+" VALUES "+questionstring+";"
        cur.executemany(writestring, (to_db,))
        con.commit()
con.close()

#%%
#
#
data_dir_ratingIdentifierType = r'C:\Users\ru87118\Desktop\Compustat\Data'
filename_ratingIdentifierType = r'spRatingIdentifierType.txt'

ratingIdentifierTypeTableColumns=['symbolTypeId', 'SymbolTypeName', 'objectTypeId']

table_name = 'ratingIdentifierType'
con = sqlite3.connect(filename)
cur = con.cursor()


with open(os.path.join(data_dir_ratingIdentifierType,filename_ratingIdentifierType),"rt",encoding="latin-1",newline=None) as fin: 
    contents = fin.readlines()
    contents = contents[0].split('#@#@#')
    contents = [line.replace('\'~\'', '|') for line in contents]
    columns1 = ratingIdentifierTypeTableColumns 
    ncol     = len(columns1)
    column_list = "(" #build column names and question string
    questionstring ="("
    for n in range(ncol):
        if n+1 < (ncol):
            column_list = column_list+str(columns1[n])+", "
            questionstring = questionstring +"?," 
        else:
            column_list = column_list+str(columns1[n])+")"
            questionstring = questionstring + "?)"
    print(table_name," ",ncol)
    print(column_list)
 
    executestring = "CREATE TABLE IF NOT EXISTS "+str(table_name)+" "+column_list+";"
    cur.executescript(executestring) #create table if it does not already exist
    for row in contents:  #write remaining rows into the table
        row1=row.split('|')
        if row1[0]=='':
            row1=['' for n in range(len(columns1))]
        to_db = [str(row1[n]) for n in range(len(columns1))]         
        writestring = "INSERT INTO "+str(table_name)+" "+column_list+" VALUES "+questionstring+";"
        cur.executemany(writestring, (to_db,))
        con.commit()
con.close()

#%%
# onstruct the insurance ratings table. This is the second dataset that will be used as input to python scripts
#
con = sqlite3.connect(filename)
c = con.cursor()

#c.execute("DROP TABLE CnIRatings")

with open(r'C:\Users\ru87118\Desktop\Compustat\Data\SQL\CnICompanies_create table.sql', 'r') as file:
    sql_create_CnICompanies_table = file.read().replace('\n', ' ')
    
c.execute(sql_create_CnICompanies_table)


with open(r'C:\Users\ru87118\Desktop\Compustat\Data\SQL\mapRatingsGVKEY_create table.sql', 'r') as file:
    sql_create_mapRatingsGVKEY_table = file.read().replace('\n', ' ')
    
c.execute(sql_create_mapRatingsGVKEY_table)

with open(r'C:\Users\ru87118\Desktop\Compustat\Data\SQL\CnIRatings_create table.sql', 'r') as file:
    sql_create_CnIRatings_table = file.read().replace('\n', ' ')
    
c.execute(sql_create_CnIRatings_table)

con.commit()
c.close()
con.close()

#%%
# The lines below create the dataframes used as input data
#
import pandas as pd
import os, sqlite3, csv

dir_name=r'C:\Users\ru87118\Desktop\Compustat\Data'
os.chdir(dir_name)

base_filename='CnI091920_2'
filename_suffix = '.db'
filename = os.path.join(dir_name, base_filename + filename_suffix)
con = sqlite3.connect(filename)

CnIFinancials = pd.read_sql_query("SELECT * FROM CnIFinancials", con)
CnIRatings = pd.read_sql_query("SELECT * FROM CnIRatings", con)

con.close()

CnIFinancials.to_csv(r'CnIFinancials.csv')
CnIRatings.to_csv(r'CnIRatings.csv')


