

import os, sys, pandas as pd, numpy as np
os.chdir(r"C:\Users\ub71894\Documents\Docs\cheatsheet")
from PyPDF2 import PdfFileMerger

pdfs = ['Bokeh.pdf',
'ImportingData.pdf',
'JupyterNotebook.pdf',
'Keras.pdf',
'Matplotlib.pdf',
'Numpy.pdf',
'Pandas.pdf',
'PySpark_RDD.pdf',
'PySpark_SQL.pdf',
'ScikitLearn.pdf',
'SciPy_LinearAlgebra.pdf',
'Seaborn.pdf']


merger = PdfFileMerger()

for pdf in pdfs:
    merger.append(pdf)

merger.write("result.pdf")import pyupset as pyu
