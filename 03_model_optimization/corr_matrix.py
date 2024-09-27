"""
@author: l_vdp
edited by: arietma

Script to make correlation matrix that shows the Pearson correlation between
all features. The figure corresponds to Figure 3 in the current thesis. 

Input: Final merged dataset (.csv).
Output: Correlation matrix for all non-constant features

Edits by arietma:
    - Adjusted the code to the dataset and features used in the current thesis
    - Only calculate pearson corr for the merged dataset, not for the
      airborne and tower datasets separately, since in the current thesis
      only the merged dataset/model is used

"""
#%% Import packages

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#%% Set up working directory and load data

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/' 
mer = pd.read_csv(f"{WD}merged_0228_final.csv", 
                  index_col=0, na_values='nan')

#%% Organize features

LGN_classes = ['Grs', 'SuC', 'SpC', 'Ghs', 'dFr', 'cFr', 'Wat',
       'Bld', 'bSl', 'Hth', 'FnB', 'Shr']
soil_classes = ['hV', 'W', 'pV', 'kV', 'hVz', 'V',
       'Vz', 'aVz', 'kVz', 'overigV', 'zandG', 'zeeK', 'rivK', 'gedA', 'leem']

meteo_vars = ['Tsfc', 'VPD', 'PAR_abs']
owasis_vars = ['BBB', 'OWD' , 'GWS']

all_feats = ['CO2flx', 'PAR_abs', 'Tsfc', 'VPD', 'RH', 'NDVI', 'EVI', 'BBB', 'GWS', 'OWD', 'PeatD', 'Exp_PeatD'] + LGN_classes + soil_classes

#%% Select data and features to make corr_matrix for

data = mer[all_feats]

# Can also be made for the tower/airborne dataset separately
air = mer[mer['source']=='airborne']
twr = mer[mer['source']=='tower']

data = air[all_feats]
data = twr[all_feats]

#%% Drop all constant features (with correlation = NA)
corr = data.corr()
corr = corr.dropna(how='all', axis=1)
corr = corr.dropna(how='all', axis=0) # leem is dropped

#%% Correlation matrix plot

fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111)

fig.subplots_adjust(left=0.2)
cax = ax.matshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
fig.colorbar(cax)
ticks = np.arange(0,len(corr.columns),1)
ax.grid(False)
ax.set_xticks(ticks)
ax.set_yticks(ticks)
ax.set_xticklabels(list(corr.columns), rotation=90)
ax.set_yticklabels(list(corr.columns), rotation=0)

# Save figure
#fig.savefig(f'{WD}figures/0228_mer_allfeatst_corrmatrix.png',dpi=1000)