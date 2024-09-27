# -*- coding: utf-8 -*-
"""
@author: l_vdp
edited by: arietma, edited from shap_analysis.py

This script performs the shapley analysis on the two seasonal models (SepJan
and FebAug). A number of possible plots is shown. This script should be run
twice, once specifying months = 'SepJan' and once months = 'FebAug'


Input: final seasonal datasets, selected features and optimized hyperparameters
Output: shapley values of the seasonal models (shap_values_xgb_sj and 
    shap_values_xgb_fa), Shapley plots:
    beeswarm plot (overview figures, Figure D3 and D4 in thesis), 
    single scatterplot of choice (not in thesis), 

Note: in order to run shap_figures_modelcomp.py,
this script has to be run twice to have the shapley values of the seasonal models
stored in the variables shap_values_xgb_sj and shap_values_xgb_fa.

Edits by arietma:
    - Adjusted the code (also for plots) to the seasonal datasets, models and 
    model specs 

"""


#%%
import pandas as pd
import matplotlib.pyplot as plt
import shap
from xgboost import XGBRegressor

#%% Set up working directory and load data
WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'

# Specify whether the script is run for SepJan or FebAug
months = 'FebAug' #or 'SepJan' 

# Load subset of the dataset, either SepJan or FebAug
mer = pd.read_csv(f"{WD}merged_{months}_0228.csv", index_col=0, na_values='nan')

# Add filter: exclude airborne observations with >15% built environment
Bld_filter = (mer['Bld'] > 0.15) & (mer['source']== 'airborne')
mer = mer[-Bld_filter]

#%% Specify features and hyperparameters
# Same features are present in both models
mer_feats = ['PAR_abs', 'Tsfc', 'RH', 'EVI', 'Bld', 'Wat', 'Exp_PeatD']

if months == 'SepJan':
    mer_hypp = {'learning_rate': 0.001, 'max_depth': 9, 'n_estimators': 4000, 'subsample': 0.55}
elif months == 'FebAug':
    mer_hypp = {'learning_rate': 0.001, 'max_depth': 3, 'n_estimators': 7000, 'subsample': 0.65}

mer_X = mer[mer_feats]
mer_y = mer['CO2flx']

#%% Select data for Shapley analysis

X = mer_X; y = mer_y; hyperparams = mer_hypp

X100 = shap.utils.sample(X, 100)

#%% Fit optimized model

model_xgb = XGBRegressor(learning_rate = hyperparams['learning_rate'], 
             max_depth = hyperparams['max_depth'], 
             n_estimators = hyperparams['n_estimators'],
             subsample = hyperparams['subsample']).fit(X, y)# next: with optimized parameters

#%% Initialize explainer
explainer_xgb = shap.TreeExplainer(model_xgb, X100)

#%% It is possible to explain only part of the dataset, for example:

#X = X[mer.source == 'airborne']
#X = X[(X.Tsfc > 20)]
#X = X[X.PAR_abs < 10]
#X = X[X.PAR_abs > 800] 

#%% Explaining values with shapley explainer

if months == 'SepJan': 
    shap_values_xgb_sj = explainer_xgb(X) # takes ~2u 10mins (because more complex tree)
elif months == 'FebAug':
    shap_values_xgb_fa = explainer_xgb(X) # takes ~15 mins


#%% NOW PLOTTING
# For plotting, specify which shap value to use
if months == 'SepJan':
    shap_values_xgb = shap_values_xgb_sj
elif months == 'FebAug':
    shap_values_xgb = shap_values_xgb_fa
    
#%% Shapley has many plotting options 
# Here a bunch of shapley plots for inspiration

sample_ind=15

shap.plots.scatter(shap_values_xgb[:,"PAR_abs"], color=shap_values_xgb[:, 'Tsfc'])

shap.plots.bar(shap_values_xgb)

shap.plots.heatmap(shap_values_xgb[:1000])

shap.plots.beeswarm(shap_values_xgb, max_display=30)

shap.force_plot(base_value=explainer_xgb.expected_value, shap_values=shap_values_xgb.values[sample_ind,:],
                features = X.iloc[sample_ind,:].round(2), feature_names=X.columns, matplotlib=True,
                show=True, figsize=(20,3), text_rotation=0)


#%% Beeswarm plot (overview), corresponds to Figure D3 and D4 in thesis

fig, ax = plt.subplots(figsize=(15,15))
shap.plots.beeswarm(shap_values_xgb, max_display=8, show=False)
plt.title(f'Feature importance based on Shapley values, {months} model')
plt.tight_layout()

# Save figure
fig.savefig(f"{WD}/figures/months/0228_{months}_beeswarm.png", dpi=1000)


#%% Scatterplot 
# any feature from the model can filled in at 'feature=', colored by 'col_feat'

fig, ax = plt.subplots(figsize=(7,5))
feature = 'Exp_PeatD'
col_feat = 'EVI'
shap.plots.scatter(shap_values_xgb[:,feature], show=False,
                   title= f'Shapley values of {feature}, {months} model',  
                   color=shap_values_xgb[:,col_feat], ax = ax) 

plt.xlabel(feature)
plt.ylabel('Shapley value of ' + feature)
plt.axhline(0, color='gray', ls='--')
plt.tight_layout()

# Save figure
fig.savefig(f"{WD}/figures/months/0228_{months}_{feature}_{col_feat}.png", dpi=1000)

