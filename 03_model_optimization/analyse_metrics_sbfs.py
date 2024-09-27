# -*- coding: utf-8 -*-
"""
@author: l_vdp
Edits by: arietma

This script analyses the results produced by sequential backward feature selection,
'sbfs_hpc'.

Input: Dataframes of metrics resulting from SBFS (.csv).
Output: Two figures, one figure corresponding to Figure 5 in thesis, showing
the SBFS metrics for the final merged model, M5, with different data folds as
test folds. The other figure shows the SBFS metrics for the chosen test fold 
(data fold = 4), for model iterations M4-6.

Edits by arietma:
    - Adjusted the code to the current model iterations and the five data folds 
    used as test folds in this thesis

"""
#%% Import packages

import pandas as pd
import matplotlib.pyplot as plt
# from matplotlib.ticker import MaxNLocator
from matplotlib.lines import Line2D

#%% Set up working directory
WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'

#%% Load data 
# sbfs results for all model iterations

# Initialize empty dictionary for all metrics 
all_metrics = {}

# Iterate over all different model iterations (M: 1-6) and test folds (testfold: 1-5)
for M in range(1,7):
    for testfold in range (1,6):
        
        # dynamic file path
        file_path = f"{WD}modelling/0228_mer_featsel_metrics_basedonSBSF_r2_mlxtend_M{M}_testfold{testfold}.csv"
        # name of file in dictionary (key)
        key = f"M{M}_testfold{testfold}"
        
        # load the csv and store in all_metrics
        try:
            all_metrics[key] = pd.read_csv(file_path, index_col=0)
            print(f"Loaded file: {key}")
        
        except FileNotFoundError:
            print(f"File not found: {key}")

#%% Select same colors used throughout this study

standard_blue = '#1f77b4'
standard_orange = '#ff7f0e'
standard_green = '#2ca02c'

#%% Create plot for metrics of M5 (Exp_PeatD + applied Bld filter)
# Corresponds to Figure 5 in thesis

# Plot R2 of all different testfolds of M5
# Data fold 4 is chosen as the test fold, based on:
    # Average performance
    # Also, the percentage of airborne data and total no. observations in this
    # data fold is average

fig, ax1a = plt.subplots(figsize=(10, 6))
ax1a.plot(all_metrics['M5_testfold1']['r2'], color='black', label = 'R2')
ax1a.plot(all_metrics['M5_testfold2']['r2'], color='black', label = 'R2')
ax1a.plot(all_metrics['M5_testfold3']['r2'], color='black', label = 'R2')
ax1a.plot(all_metrics['M5_testfold4']['r2'], color='black', label = 'R2', linestyle = '--')
ax1a.plot(all_metrics['M5_testfold5']['r2'], color='black', label = 'R2')


# X and Y axis labels
ax1a.set_ylabel('R$^{2}$ score')
ax1a.set_xlabel('Number of features')
ax1a.set_ylim(0.6, 0.8)

# Add title
plt.title('Performance metrics of the merged model per number of features')

# Create second axis for plotting MSE, variance and bias
ax1b = ax1a.twinx()
ax1b.plot(all_metrics['M5_testfold1']['mse'], color=standard_blue, label='MSE')
ax1b.plot(all_metrics['M5_testfold1']['var'], color=standard_orange, label='Var')
ax1b.plot(all_metrics['M5_testfold1']['bias'], color=standard_green, label = 'Bias')

ax1b.plot(all_metrics['M5_testfold2']['mse'], color=standard_blue)
ax1b.plot(all_metrics['M5_testfold2']['var'], color=standard_orange)
ax1b.plot(all_metrics['M5_testfold2']['bias'], color=standard_green)

ax1b.plot(all_metrics['M5_testfold3']['mse'], color=standard_blue)
ax1b.plot(all_metrics['M5_testfold3']['var'], color=standard_orange)
ax1b.plot(all_metrics['M5_testfold3']['bias'], color=standard_green)

ax1b.plot(all_metrics['M5_testfold4']['mse'], color=standard_blue, linestyle = '--')
ax1b.plot(all_metrics['M5_testfold4']['var'], color=standard_orange, linestyle = '--')
ax1b.plot(all_metrics['M5_testfold4']['bias'], color=standard_green, linestyle = '--')

ax1b.plot(all_metrics['M5_testfold5']['mse'], color=standard_blue)
ax1b.plot(all_metrics['M5_testfold5']['var'], color=standard_orange)
ax1b.plot(all_metrics['M5_testfold5']['bias'], color=standard_green)

# Y axis label and lims
ax1b.set_ylabel('MSE, variance, and bias')
ax1b.set_ylim(0,30)

# Add legend
legend_elements = [Line2D([0], [0], label='R$^{2}$', color='black'),
                   Line2D([0], [0], label='MSE', color=standard_blue),
                   Line2D([0], [0], label='Bias', color=standard_green),
                   Line2D([0], [0], label='Var', color=standard_orange)]

ax1b.legend(handles=legend_elements,  loc = 'lower right', bbox_to_anchor=(0.99,0.1)) 

# Save figure
#fig.savefig(f'{WD}figures/metrics_sbfs_0228_M5.png', bbox_inches='tight', dpi=1000)

#%% Create figure for M4-6, all with testfold = 4
# Figure not in thesis

# Plot R2
fig, ax1a = plt.subplots(figsize=(10, 6))
ax1a.plot(all_metrics['M4_testfold4']['r2'], color='black', label = 'R2')
ax1a.plot(all_metrics['M5_testfold4']['r2'], color='black', label = 'R2', linestyle = '--')
ax1a.plot(all_metrics['M6_testfold4']['r2'], color='black', label = 'R2', linestyle = ':')

# Y and X axis labels and lims
ax1a.set_ylabel('R2 score')
ax1a.set_xlabel('Number of features')
ax1a.set_ylim(0.70, 0.77)

# Add title and subtitle
plt.title('Merged models M4-6 (with Bld filter), only testfold = fold4')
ax1a.text(7,0.765, '4: solid, 5: dashed, 6:dotted', weight='bold').set_backgroundcolor('white')

# Create second axis for plotting MSE, variance and bias
ax1b = ax1a.twinx()
ax1b.plot(all_metrics['M4_testfold4']['mse'], color=standard_blue, label='MSE')
ax1b.plot(all_metrics['M4_testfold4']['var'], color=standard_orange, label='Var')
ax1b.plot(all_metrics['M4_testfold4']['bias'], color=standard_green, label = 'Bias')

ax1b.plot(all_metrics['M5_testfold4']['mse'], color=standard_blue, label='MSE', linestyle = '--')
ax1b.plot(all_metrics['M5_testfold4']['var'], color=standard_orange, label='Var', linestyle = '--')
ax1b.plot(all_metrics['M5_testfold4']['bias'], color=standard_green, label = 'Bias', linestyle = '--')

ax1b.plot(all_metrics['M6_testfold4']['mse'], color=standard_blue, label='MSE', linestyle = ':')
ax1b.plot(all_metrics['M6_testfold4']['var'], color=standard_orange, label='Var', linestyle = ':')
ax1b.plot(all_metrics['M6_testfold4']['bias'], color=standard_green, label = 'Bias', linestyle = ':')

# Add Y axis label and lims
ax1b.set_ylabel('MSE, Var, bias score')
ax1b.set_ylim(0,22)
ax1b.set_ylim(10,20)

# Add legend
legend_elements = [Line2D([0], [0], label='R2', color='black'),
                   Line2D([0], [0], label='MSE', color=standard_blue),
                   Line2D([0], [0], label='Bias', color=standard_green),
                   Line2D([0], [0], label='Var', color=standard_orange)]

ax1b.legend(handles=legend_elements, loc='upper left')

# Save figure
#fig.savefig(f'{WD}figures/metrics_sbfs_0228_M4-6.png', bbox_inches='tight', dpi=1000)

