import pandas as pd 
import numpy as np
os.chdir(r"C:\Users\ub71894\Documents\code\Python\testcode")

import win32com.client
myPowerPoint = win32com.client.DispatchEx( 'Powerpoint.Application' )

ppt = r'C:\Users\ub71894\Documents\code\Python\testcode\OriginalTemplate.pptx'
thePresentation = myPowerPoint.Presentations.Open(ppt, False, False, False )

for i in range(2):
    thePresentation.Slides(2).Duplicate()

thePresentation.SaveAs(r'C:\Users\ub71894\Documents\code\Python\testcode\OriginalTemplate_dup.pptx')
thePresentation.Close() 


