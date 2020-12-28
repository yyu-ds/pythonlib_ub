"""
Created on Thu Nov 12 11:26:50 2015

@author: ub71894
"""

import numpy as np
import pandas as pd
from scipy import stats, integrate
import matplotlib.pyplot as plt
import seaborn as sns
import string




sns.set(style="white")

# Generate a large random dataset
rs = np.random.RandomState(33)
d = pd.DataFrame(data=rs.normal(size=(100, 26)),
                 columns=list(string.ascii_letters[:26]))

# Compute the correlation matrix
corr = d.corr()

# Generate a mask for the upper triangle
mask = np.zeros_like(corr, dtype=np.bool)
mask[np.triu_indices_from(mask)] = True

# Set up the matplotlib figure
f, ax = plt.subplots(figsize=(11, 9))

# Generate a custom diverging colormap
cmap = sns.diverging_palette(220, 10, as_cmap=True)

# Draw the heatmap with the mask and correct aspect ratio
sns.heatmap(corr, mask=mask, cmap=cmap, vmax=.3,
            square=True, xticklabels=5, yticklabels=5,
            linewidths=.5, cbar_kws={"shrink": .5}, ax=ax)





import seaborn as sns
sns.set()
#fig1
seafig= sns.pairplot(trans_data)

#fig2
seafig = sns.pairplot(trans_data, palette="Set2", diag_kind="kde", size=2.5)

#fig3
seafig = sns.PairGrid(trans_data)
seafig.map_upper(plt.scatter)
seafig.map_lower(sns.kdeplot, cmap="Blues_d")
seafig.map_diag(sns.kdeplot, lw=3, legend=False);

seafig.savefig('seaborn.pdf')





sns.set()
plt.figure(figsize=(18, 6))
# Create a random dataset across several variables
rs = np.random.RandomState(0)
n, p = 40, 12
d = rs.normal(0, 2, (n, p))
d += np.log(np.arange(1, p + 1)) * -5 + 10

# Use cubehelix to get a custom sequential palette
pal = sns.cubehelix_palette(p, rot=-.5, dark=.3)

# Show each distribution with both violins and points
d= pd.DataFrame(d,columns=list('abcdefghijkl'))
sns.violinplot(data=d, palette=pal, inner="quart")

plt.savefig('seaborn.pdf')
