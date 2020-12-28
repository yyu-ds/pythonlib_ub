'''
                                       
      3.141592653589793238462643383279  
    5028841971693993751058209749445923  
   07816406286208998628034825342117067  
   9821    48086         5132           
  823      06647        09384           
 46        09550        58223           
 17        25359        4081            
           2848         1117            
           4502         8410            
           2701         9385            
          21105        55964            
          46229        48954            
          9303         81964            
          4288         10975            
         66593         34461            
        284756         48233            
        78678          31652        71  
       2019091         456485       66  
      9234603           486104543266485
     2133936            0726024914127   
     3724587             00660631558    
     817488               152092096     
'''

from dirsync import sync

#%% from local to I drive
local = [
r'C:\Users\ub71894\Documents\Projects\CNI',
r'C:\Users\ub71894\Documents\Projects\MachineLearning',
r'C:\Users\ub71894\Documents\Data',
r'C:\Users\ub71894\Documents\Code',
r'C:\Users\ub71894\Documents\DevRepo',
r'C:\Users\ub71894\Documents\Projects\AnnualPerformance',
r'C:\Users\ub71894\Documents\Projects\GlobalCorporation',
r'C:\Users\ub71894\Documents\Projects\CNI_redev'
]

Udrive = [
r'I:\YangY\Projects\CNI', 
r'I:\YangY\Projects\MachineLearning', 
r'I:\YangY\Data', 
r'I:\YangY\Code', 
r'I:\YangY\DevRepo',
r'I:\YangY\Projects\AnnualPerformance',
r'I:\YangY\Projects\GlobalCorporation',
r'I:\YangY\Projects\CNI_redev'
]

for i in range(len(local)):
	sync(local[i], Udrive[i], action='sync', purge=True, create=True)

print("I: drive sync finished")
#%% from local to U drive
local = [
r'C:\Users\ub71894\Documents\Code', 
r'C:\Users\ub71894\Documents\Docs', 
r'C:\Users\ub71894\Documents\Projects',
#r'C:\Users\ub71894\Documents\Data',
#r'C:\Users\ub71894\Documents\DevRepo',
r'C:\Users\ub71894\Documents\OneNote Notebooks'
]

Udrive = [
r'U:\Code', 
r'U:\Docs', 
r'U:\Projects', 
#r'U:\Data', 
#r'U:\DevRepo', 
r'U:\OneNote Notebooks']

for i in range(len(local)):
	sync(local[i], Udrive[i], action='sync', purge=True, create=True)

