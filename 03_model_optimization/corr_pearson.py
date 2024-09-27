# -*- coding: utf-8 -*-
"""
@author: l_vdp
edited by: arietma

Script to make Pearson correlation plot for all features with CO2, for the
merged dataset.

Input: Final merged dataset (.csv).
Output: Pearson correlation plot, which corresponds to Figure 4 (left) in the 
current thesis.

Edits by arietma:
    - Adjusted the code to the dataset and features used in the current thesis
    - Only calculate pearson corr for the merged dataset, not for the
    airborne and tower datasets separately, since in the current thesis
    only the merged dataset/model is used
    - Added red line in figure to clarify which features are dropped before
    moving on to SBFS (the least correlated features)
"""

#%% Import packages

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#%% Set up working directory and load data

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'

mer = pd.read_csv(f"{WD}merged_0228_final.csv", 
                  index_col=0)

#%% Organize features

LGN_classes = ['Grs', 'SuC', 'SpC', 'Ghs', 'dFr', 'cFr', 'Wat',
       'Bld', 'bSl', 'Hth', 'FnB', 'Shr']
soil_classes = ['hV', 'W', 'pV', 'kV', 'hVz', 'V',
       'Vz', 'aVz', 'kVz', 'overigV', 'zandG', 'zeeK', 'rivK', 'gedA', 'leem']


meteo_vars = ['Tsfc', 'VPD', 'PAR_abs']
owasis_vars = ['BBB', 'OWD' , 'GWS']

all_feats = ['CO2flx', 'PAR_abs', 'Tsfc', 'VPD', 'RH', 'NDVI', 'EVI', 'BBB', 'GWS', 'OWD', 'PeatD', 'Exp_PeatD'] + LGN_classes + soil_classes

#%% Calculate correlation and sort

merged_corr = mer[all_feats].corr()

me_corrCO2 = pd.DataFrame(merged_corr['CO2flx'].sort_values(ascending=False, key=abs))
me_corrCO2 = me_corrCO2.drop(['CO2flx'], axis=0)

#%%% Plot Pearson Correlation with CO2 flux
# Figure corresponds to Figure 4 (left) in the current thesis

sns.set_style("white")
fig, ax = plt.subplots(figsize=(5,7))
sns.barplot(x=me_corrCO2.CO2flx, y=me_corrCO2.index, color=sns.color_palette()[0])
plt.title('Pearson Correlation with $CO_2$ flux')
plt.xlabel('Pearson Correlation')
plt.ylabel('Features')

# In between Grs and overigV a red line, indicating that the 6 lowest features
# do not continue to SBFS
plt.axhline(y= 31.5,color = 'red', linestyle = '--')

# Figure specs
ax.grid(False)
plt.tight_layout()

# Save figure
fig.savefig(f'{WD}figures/0228_mer_selectedfeat_pearsoncorr_redline.png',dpi=1000)
