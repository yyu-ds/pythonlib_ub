# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 17:02:33 2016

@author: 
"""



import pyautogui,time

#pyautogui.PAUSE = 1
pyautogui.FAILSAFE = False

#pyautogui.size()
#width, height = pyautogui.size()
#%% office
i=0
while True:
    pyautogui.moveTo(1630, 547, duration=5)
    pyautogui.moveTo(1632, 547, duration=5)
    time.sleep(50)
    i+=1    
    print(i)

#%%no dock:
i=0
while True:
    time.sleep(57)
    pyautogui.moveTo(1778, 413, duration=3)
    pyautogui.click(1779,404)
    i+=1
    print(i)

#%%
    
i=0
while i<600:
    time.sleep(57)
    pyautogui.moveTo(1778, 413, duration=3)
    pyautogui.click(1779,404)
    i+=1
    print(i)
    
 #%%
pyautogui.position()

#%% timer to shutdown:
import os
i=0
while i<20:
    time.sleep(57)
    pyautogui.moveTo(1778, 413, duration=3)
    pyautogui.click(1779,404)
    i+=1
    print(i)
    
os.system("shutdown /s /t 1") 
