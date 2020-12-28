
import os, sqlite3, csv
from io import StringIO


dir_name=r'C:\Users\ru87118\Desktop\Compustat\Data'
os.chdir(dir_name)

data_dir = r'C:\Users\ru87118\Desktop\Compustat\Data'
filename_A_L = r'f_co_afnd1V2.txt'
remove_string_A_L = 'H|20200919-07:42:53|co_afnd1V2|6|'

file_A_L = open(os.path.join(data_dir, filename_A_L),'r').read().replace(remove_string_A_L,'').replace('|',',')
s = StringIO(file_A_L)
# Save a csv for direct manual inspection
with open('afnd1V2.csv', 'w') as f:
    for line in s:
        #print(line)
        f.write(line)
        

filename_M_Z = r'f_co_afnd2V2.txt'
remove_string_M_Z = 'H|20200919-07:41:52|co_afnd2V2|6|'

file_M_Z = open(os.path.join(data_dir, filename_M_Z),'r').read().replace(remove_string_M_Z,'').replace('|',',')
s = StringIO(file_M_Z)
# Save a csv for direct manual inspection
with open('afnd2V2.csv', 'w') as f:
    for line in s:
        f.write(line)
        

filename_company = r'f_company.txt'
remove_string_company = 'H|20200919-07:32:36|company|1|'

file_company = open(os.path.join(data_dir, filename_company),'r').read().replace(remove_string_company,'').replace('|',',')
s = StringIO(file_company)
# Save a csv for direct manual inspection
with open('company.csv', 'w') as f:
    for line in s:
        f.write(line)        
        
        
filename_rating = r'spRatingData.txt'

file_rating = open(os.path.join(data_dir, filename_rating),'r').read().replace('\'~\'',',').replace('#@#@#','\n')
s = StringIO(file_rating)

ratingsTableColumns = str(['ratingDetailId','entitySymbolValue','instrumentSymbolValue','securitySymbolValue',
                     'objectTypeId'	,'orgDebtTypeCode','ratingTypeCode','currentRatingSymbol','ratingSymbol',
                     'ratingDate','creditwatch','outlook','creditwatchDate','outlookDate','priorRatingSymbol',	
                     'priorCreditwatch','priorOutlook','ratingQualifier','regulatoryIndicator','regulatoryQualifier',
                     'ratingActionWord','CWOLActionWord','cwolInd','maturityDate','CUSIP','CINS','ISIN'])

# Save a csv for direct manual inspection
with open('spRatingData.csv', 'w') as f:
    f.write(ratingsTableColumns) 
    f.write("\n")
    for line in s:
        f.write(line)        
        

filename_key = r'CompanyCrossRef.txt'

file_key = open(os.path.join(data_dir, filename_key),'r').read().replace('|',',')
s = StringIO(file_key)
# Save a csv for direct manual inspection
with open('CompanyCrossRef.csv', 'w') as f:
    for line in s:
        f.write(line)             
        
        
