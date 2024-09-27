# -*- coding: utf-8 -*-
"""
@author: arietma

This script produces plots of Shapley values for all three models (merged, SepJan 
and FebAug) at once. The script can be run for any feature that is present in all
three models, but is currently specified for Exp_PeatD and EVI (with the right xlims) 

Note: before running this script, shap_analysis.py and shap_analysis_SepJan_FebAug.py
have to be run first to have: 
Shapley values of the merged model (shap_values_xgb_mer)
Shapley values of the SepJan model (shap_values_xgb_sj)
Shapley values of the FebAug model (shap_values_xgb_fa)

Input: the final merged dataset, shapley values of the merged, SepJan and FebAug
models
Output: plots comparing Shapley values for all three models, correpsonding to 
Figure 7 and D2 in thesis

"""



#%% Import packages

import panda as pd
import numpy as np
import matplotlib.pyplot as plt

#%% Set up working directory and load data
WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'

mer = pd.read_csv(f"{WD}merged_0228_final.csv", 
                  index_col=0)

# Add filter: exclude airborne observations with >15% built environment
Bld_filter = (mer['Bld'] > 0.15) & (mer['source']== 'airborne')
mer = mer[-Bld_filter]

mer['Datetime'] = pd.to_datetime(mer['Datetime'])

#%% Create Shapley figures including all three models
# Corresponds to Figure 7 and Figure D2 of Thesis

# To specify:
feature = 'EVI'           # feature of which Shapley values are plotted
unit = ' '                # unit of feature
col_feat = 'Tsfc'         # feature used for coloring
cmap = 'viridis'          # specify colormap



# Get the right column of the plotted feature in the shap_values variable
feature_index_mer = shap_values_xgb_mer.feature_names.index(feature)
feature_index_sj = shap_values_xgb_sj.feature_names.index(feature)
feature_index_fa = shap_values_xgb_fa.feature_names.index(feature)

# Select SepJan and FebAug rows in the merged dataset to specify the rows
# used in coloring the subplots
sj_rows = ((mer['Datetime'].dt.month.isin([9,10,11,12,1])))     # to specify cmap
fa_rows = ((mer['Datetime'].dt.month.isin([2,3,4,5,6,7,8])))    # to specify cmap

# Get min and max value of the coloring feature for coloring all subplots with 
# the same cbar
norm = plt.Normalize(vmin=mer[col_feat].min(), vmax=mer[col_feat].max()) 

# Specify xlims
if feature == 'Exp_PeatD':
    xlim = [-5,130]
elif feature == 'EVI':
    xlim = [-0.1, 0.9]

# Specify ylims by calculating the overall minimum and maximum Shapley value
ylim_min = np.min([shap_values_xgb_mer.values[:,feature_index_mer].min(), 
                   shap_values_xgb_sj.values[:, feature_index_sj].min(),
                   shap_values_xgb_fa.values[:, feature_index_fa].min()]) -0.15
ylim_max = np.max([shap_values_xgb_mer.values[:,feature_index_mer].max(), 
                   shap_values_xgb_sj.values[:, feature_index_sj].max(),
                   shap_values_xgb_fa.values[:, feature_index_fa].max()]) +0.15



# Create figure
fig, axs = plt.subplots(1,3, figsize = (15,4))
row_indices = [0,1,2]
text_color = '#333333'

# Plot merged model: all observations
scatter = axs[0].scatter(x = shap_values_xgb_mer.data[:,feature_index_mer], 
                        y = shap_values_xgb_mer.values[:,feature_index_mer],
                        alpha = 0.45, s=15, edgecolor = 'none',
                        c=mer[col_feat], cmap = cmap, norm = norm)
axs[0].set_title('Merged model: all observations', color=text_color)

# Plot SepJan model
scatter = axs[1].scatter(x = shap_values_xgb_sj.data[:,feature_index_sj], 
                         y = shap_values_xgb_sj.values[:,feature_index_sj],
                         alpha = 0.45, s=15, edgecolor = 'none',
                         c=mer[col_feat][sj_rows], cmap = cmap, norm=norm)
axs[1].set_title('SepJan model', color=text_color)

# Plot FebAug model
scatter = axs[2].scatter(x = shap_values_xgb_fa.data[:,feature_index_fa], 
                         y = shap_values_xgb_fa.values[:,feature_index_fa],
                         alpha = 0.45, s=15, edgecolor = 'none',
                         c=mer[col_feat][fa_rows], cmap = cmap, norm=norm)
axs[2].set_title('FebAug model', color=text_color)

# Perform the following lines of code for all subplots
for row_index in row_indices:   
    # Plot horizontal line at y=0
    axs[row_index].axhline(0, color='gray', ls='--')
    
    # Adjust some figure specs
    cbar = plt.colorbar(scatter,ax=axs[row_index] , aspect = 50) 
    cbar.set_label(col_feat)  # Add colorbar label
    cbar.outline.set_visible(False)  # Hide colorbar outline
    
    # Hide top and right spines
    axs[row_index].spines['top'].set_visible(False) # gets rid of upper and right border lines
    axs[row_index].spines['right'].set_visible(False)
    
    axs[row_index].spines['left'].set_linewidth(0.5)  # make the bottom border line a bit smaller
    axs[row_index].spines['bottom'].set_linewidth(0.5) 
    
    # Set x axis label
    axs[row_index].set_xlabel(feature+unit, color=text_color)
    
    # Set color for tick labels
    axs[row_index].tick_params(axis='x', colors=text_color)
    axs[row_index].tick_params(axis='y', colors=text_color)
    
    # Set similar xlims and ylims for all subplots
    axs[row_index].set_ylim(ylim_min,ylim_max)
    axs[row_index].set_xlim(xlim)

# Set y axis label only for left plot
axs[0].set_ylabel('Shapley value of ' + feature, color=text_color)

# Set overall title
plt.suptitle(f'Shapley values of {feature}', color=text_color)

plt.tight_layout()
plt.show()



# Save figure
fig.savefig(f'{WD}figures/0228_allmodels_{feature}_colored_{col_feat}.png', dpi=1000)


