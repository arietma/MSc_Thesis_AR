# -*- coding: utf-8 -*-
"""
@author: arietma

This script performs bootstrapped sampling of the Shapley values of Air Exposed
Peat Depth and surface T, for uncertainty calculation around the Shapley values
of Air Exposed Peat Depth, and to calculate the zero crossings of Air Exposed 
Peat Depth and surface T, i.e. the values of Air Exposed Peat Depth and surface 
Temperature at which the Shapley value = 0 is crossed. This shows from which value 
the feature starts to positively contribute to the predicted CO2 flux.

Note: before running this script, shap_analysis.py has to be run first to have 
the Shapley values of the merged model (shap_values_xgb_mer)

Input: the final merged dataset, the Shapley values of the merged model
Output: plot showing the bootstrap intervals (uncertainty intervals) around
the Shapley values of Exp_PeatD (Figure D1) in thesis, and the zero crossing
of Exp_PeatD and surface T

"""

#%% Import packages
import panda as pd
from sklearn.utils import resample
import matplotlib.pyplot as plt

#%% Set up working directory
WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'

#%% Bootstrap from Shapley values
# Perform bootstrapped sampling from the Shapley values to
# (1) calculate the uncertainty around the Shapley values for Air Exposed Peat 
# Depth

# (2) calculate the value of Air Exposed Peat Depth and surface Temperature
# at which the Shapley value = 0 is crossed, i.e. at which value the feature
# starts to positively contribute to the predicted CO2 flux



feature = 'Exp_PeatD'
feature_index = shap_values_xgb_mer.feature_names.index(feature) # for selecting
# the columns corresponding to Exp_PeatD

# Store Shapley values of Exp_PeatD
shaps_ExpP = pd.DataFrame({'Exp_PeatD':shap_values_xgb_mer.data[:,feature_index], 
                           'Shapley_values': shap_values_xgb_mer.values[:,feature_index]} )



# Bootstrapped sampling with sample size = 1,000 and no. samples = 10,000

# Initialize dictionary and define 10,000 random states
bootstraps = {}
set_seeds = range(1,10001) 

# Sampling loop
for i in set_seeds:
    # Bootstrap from Shapley values, i.e. sampling with replacement
    boot = resample(shaps_ExpP, replace = True, n_samples = 1000, random_state = i)
    boot['Exp_P_rounded'] = round(boot['Exp_PeatD']*2)/2 # round the Exp_PeatD to .5 (or .0)
    
    # Average Shapley value over each rounded Exp_PeatD value
    boot_avg = boot.groupby('Exp_P_rounded').agg(
        avg_Shapley = ('Shapley_values', 'mean'),

    # Also add a list with the total unique values used, later used in plotting
        unique_indices=('Shapley_values', lambda x: list(x.index))).reset_index()
    
    # Store bootstrapped averages
    bootstraps[f'boot_avg_{i}'] = boot_avg



# Calculate the total bootstrapped mean and 90% bootstrap intervals
# Add all data to 1 df
all_boots = pd.concat(bootstraps.values(), ignore_index=True)

boots_stats = all_boots.groupby('Exp_P_rounded').agg(
    avg_Shapley = ('avg_Shapley', 'mean'),
    Shapley_5 = ('avg_Shapley', lambda x: x.quantile(0.05)),# To calculate the 90% bootstrap intervals
    Shapley_95 = ('avg_Shapley', lambda x: x.quantile(0.95)), 
    all_indices=('unique_indices', lambda x: list(x))  # Collect all indices
    ).reset_index()



# Calculate the unique number of values used to construct the bootstrap interval
# for every (rounded) value of Exp_PeatD

# Sum up all the indices to a single list
boots_stats['all_indices'] = boots_stats['all_indices'].apply(lambda x: sum(x, []))

# Only keep the unique indices and count unique indices, where
# set(x) removes duplicates, len(set) then counts the unique indices
boots_stats['unique_indices_count'] = boots_stats['all_indices'].apply(lambda x: len(set(x)))

# This shows that, for example:
# for exp_P = 0, 169 different indices are used to calculate the bootstrap interval
# for exp_P = 117.5, only 1 observation is used to calculate the bootstrap interval,
# which causes an 'uncertainty' of zero, simply because there is only one observation
# of this Air Exposed Peat Depth. Therefore this unique_indices_count is added to the graph

#%% Plot figure, corresponds to Figure D1 in Thesis

# Initialize plot
fig, ax1 = plt.subplots(figsize=(10, 6))

# coloring: blue for negative average Shapley values, red for positive ones
colors = ['#1E88E5' if y < 0 else '#ff0d57' for y in boots_stats['avg_Shapley']]



# Plot the bootstrapped averaged Shapley values
ax1.scatter('Exp_P_rounded', 'avg_Shapley', data=boots_stats,color=colors)

# Plot the quantiles
ax1.plot('Exp_P_rounded', 'Shapley_95', data=boots_stats, color = 'tab:orange', alpha = 0.6)
ax1.plot('Exp_P_rounded', 'Shapley_5', data=boots_stats, color = 'tab:orange', alpha = 0.6)

# Add shade to the graph between the 0.05 and 0.95 quantiles
ax1.fill_between(boots_stats['Exp_P_rounded'], boots_stats['Shapley_95'], 
                 boots_stats['Shapley_5'], alpha = 0.15, color = 'tab:orange')

# Create a second y-axis for the histogram, showing the unique no. bootstrapped
# observations per Exp_PeatD value
ax2 = ax1.twinx()

# Store maximum unique no. observations and a factor for adjusting the y axis
maxim = boots_stats['unique_indices_count'].max()
factor = 2

# Plot the number of unique observations used to calculate the bootstrap interval
for i in range(len(boots_stats)):
    x = boots_stats.iloc[i]['Exp_P_rounded']
    height = boots_stats.iloc[i]['unique_indices_count']*0.5 # multiplied by 0.5 to reduce bar height
    ax2.plot([x, x], [0, height], color='grey', linestyle='-', alpha=0.5)
    ax2.set_ylim(0,maxim*factor)

# Hide the second y-axis
ax2.get_yaxis().set_visible(False)

# Add title and x and y labels
ax1.set_title('Bootstrapped mean Shapley values and 90% bootstrap intervals')
ax1.set_xlabel('Exp_PeatD [cm]', fontsize = 11)
ax1.set_ylabel('Shapley value', fontsize = 11)
fig.tight_layout()



# Save figure
fig.savefig(f"{WD}/figures/0228_shap_bootstrap_int.png", dpi=1000)

#%% Calculate the value of Exp_PeatD at which Shapley = 0 is crossed

# Initialize dictionary and define 10,000 random states
bootstraps = {}
set_seeds = range(1,10001) 

# Now, the averaging is performed the other way around: Shapley values are
# rounded, and then the bootstrapped mean and 90% interval of Exp_PeatD for every
# (rounded) Shapley value is calculated.
# From this the Exp_PeatD value corresponding to Shapley = 0 is found

for i in set_seeds:
    # Bootstrap from Shapley values
    boot = resample(shaps_ExpP, replace = True, n_samples = 1000, random_state = i)
    # Now, Shapley values are rounded to 2 decimals
    boot['Shap_rounded'] = round(boot['Shapley_values'], 2) # round the Shapley value to 2 decimals
    
    # Average over shap
    boot_avg = boot.groupby('Shap_rounded').agg(
        avg_ExpP = ('Exp_PeatD', 'mean')).reset_index()

    # Store bootstrapped averages
    bootstraps[f'boot_avg_{i}'] = boot_avg



# Calculate the total bootstrapped mean and 90% bootstrap intervals
# Add all data to 1 df
all_boots = pd.concat(bootstraps.values(), ignore_index=True)

boots_stats = all_boots.groupby('Shap_rounded').agg(
    avg_ExpP = ('avg_ExpP', 'mean'),
    ExpP_5 = ('avg_ExpP', lambda x: x.quantile(0.05)),# To calculate the 90% bootstrap intervals
    ExpP_95 = ('avg_ExpP', lambda x: x.quantile(0.95))).reset_index() 

# Now, in boots_stats, look at Shap_rounded = 0 and the corresponding ExpP values

#%% Calculate the vlaue of Tsfc at which Shapley = 0 is crossed

feature = 'Tsfc'

feature_index = shap_values_xgb_mer.feature_names.index(feature) # for selecting
# the columns corresponding to Tsfc
# Store Shapley values of Tsfc
shaps_Tsfc = pd.DataFrame({'Tsfc':shap_values_xgb_mer.data[:,feature_index], 
                           'Shapley_values': shap_values_xgb_mer.values[:,feature_index]} )

# Initialize dictionary and define 10,000 random states
bootstraps = {}
set_seeds = range(1,10001)

# Shapley values are rounded, and the bootstrapped mean and 90% interval of Tsfc
# are calculated 
for i in set_seeds:
    # Bootstrap from Shapley values
    boot = resample(shaps_Tsfc, replace = True, n_samples = 1000, random_state = i)
    
    # Round the Shapley values to 1 decimal (since the range in Shapley values
    # of Tsfc is wider than for Exp_PeatD) 
    boot['Shap_rounded'] = round(boot['Shapley_values'], 1) 
    
    # Average over shap
    boot_avg = boot.groupby('Shap_rounded').agg(
        avg_Tsfc = ('Tsfc', 'mean')).reset_index()

    # Store bootstrapped averages
    bootstraps[f'boot_avg_{i}'] = boot_avg



# Calculate the total bootstrapped mean and 90% bootstrap intervals
# Add all data to 1 df
all_boots = pd.concat(bootstraps.values(), ignore_index=True)

boots_stats = all_boots.groupby('Shap_rounded').agg(
    avg_Tsfc = ('avg_Tsfc', 'mean'),
    Tsfc_5 = ('avg_Tsfc', lambda x: x.quantile(0.05)),# To calculate the 90% bootstrap intervals
    Tsfc_95 = ('avg_Tsfc', lambda x: x.quantile(0.95))).reset_index() 

# Now, in boots_stats, look at Shap_rounded = 0 and the corresponding Tsfc values
