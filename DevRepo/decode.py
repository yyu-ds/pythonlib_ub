

import os
os.chdir(r"C:\Users\ub71894\Documents\DevRepo\PDScorecardTool")

s=0
list_file=[]
for root, dirs, files in os.walk(os.getcwd(),topdown=False):
    for file in files:
        if file.endswith(".py"):
            s+=1
            list_file.append(file)


data = ''
list_lines=[]
for i in range(s):
    with open(list_file[i]) as fp: 
        tmp = fp.read()

        #print(len(data.splitlines()))
        data += tmp
        list_lines.append(len(data.splitlines()))


with open ('combo.py', 'w') as fp: 
    fp.write(data) 
    fp.write('%s\n' % list_file)
    fp.write('%s\n' % list_lines)
    #fp.write('%s\n' % len(list_lines))




#%% in another file 


import os
os.chdir(r"/Users/yangyu/Dropbox/github/pythonlib_ub/2")


with open ('combo.py') as ff: 
    data1 = ff.read() 
with open ('combo.py') as ff: 
    data2 = ff.readlines() 
exec('plist_lines='+data1.splitlines()[-1])
exec('plist_files='+data1.splitlines()[-2])

file_num = len(plist_lines)
first = 0
for i in range(file_num):
    line_range = (first, plist_lines[i])
    lines = data2[line_range[0]:line_range[1]]
    with open (f'{plist_files[i]}', 'w') as fp: 
        fp.writelines(lines) 
    first = line_range[1]
