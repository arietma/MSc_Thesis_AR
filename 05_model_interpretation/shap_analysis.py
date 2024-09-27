# -*- coding: utf-8 -*-
"""
@author: l_vdp
edited by: arietma

This script performs the shapley analysis on the final merged model. A number of 
possible plots is shown. Also, Linear regression is performed on the Shapley 
values of Exp_PeatD for Exp_PeatD < 45 cm.

Input: final merged dataset, selected features and optimized hyperparameters
Output: shapley values of the merged model (shap_values_xgb_mer), Shapley plots:
    beeswarm plot (overview figure, Figure 6 in thesis), 
    single scatterplot of choice (not in thesis), 
    large figure with 7 subplots (not in thesis), 
    linear regression plot (Figure 8 in thesis)

Note: in order to run shap_figures_modelcomp.py or shap_analysis_bootstrap.py,
this script has to be run first to have the shapley values of the merged model
(shap_values_xgb_mer)

Specify here that this should be first run before running shap_figures_modelcomp

Edits by arietma:
    - Adjusted the code (also for plots) to the dataset, model, model specs and 
    linear regression used in the current thesis
"""


#%% Import packages
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import shap
from xgboost import XGBRegressor
import statsmodels.formula.api as smf

#%% Set up working directory and load data
WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'

mer = pd.read_csv(f"{WD}merged_0228_final.csv", 
                  index_col=0)

# Add filter: exclude airborne observations with >15% built environment
Bld_filter = (mer['Bld'] > 0.15) & (mer['source']== 'airborne')
mer = mer[-Bld_filter]

#%% Specify features and hyperparameters of the final merged model

mer_M5feats = ['PAR_abs', 'Tsfc', 'RH', 'EVI', 'SuC', 'Wat', 'Bld', 'Exp_PeatD']
mer_M5hypp = {'learning_rate': 0.001, 'max_depth': 6, 'n_estimators': 4000, 'subsample': 0.55}

mer_X = mer[mer_M5feats]
mer_y = mer['CO2flx']
mer_hypp = mer_M5hypp

#%% Select data for Shapley analysis

X = mer_X; y = mer_y; hyperparams = mer_hypp

X100 = shap.utils.sample(X, 100)

#%% fit optimized model

model_xgb = XGBRegressor(learning_rate = hyperparams['learning_rate'], 
             max_depth = hyperparams['max_depth'], 
             n_estimators = hyperparams['n_estimators'],
             subsample = hyperparams['subsample']).fit(X, y)

#%% Initialize explainer
explainer_xgb = shap.TreeExplainer(model_xgb, X100)

#%% It is possible to explain only part of the dataset, for example:

#X = X[mer.source == 'airborne']
#X = X[(X.Tsfc > 20)]
#X = X[X.PAR_abs < 10]
#X = X[X.PAR_abs > 800] 

#%% Explaining values with Shapley explainer

shap_values_xgb_mer = explainer_xgb(X) # takes ~2u20mins

#%% NOW PLOTTING
# For plotting, specify which shap value to use

shap_values_xgb = shap_values_xgb_mer

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


#%% Beeswarm plot, corresponds to Figure 6 in Thesis

fig, ax = plt.subplots(figsize=(15,15))
shap.plots.beeswarm(shap_values_xgb, max_display=8, show=False)
plt.title('Feature importance based on Shapley values')
plt.tight_layout()

# Save figure
fig.savefig(f"{WD}/figures/0228_M5_beeswarm_goodquality.png", dpi=1000)

#%% Shapley plot of any feature
# any feature from the model can filled in at 'feature=', colored by 'col_feat'
feature = 'Wat'
col_feat = 'PAR_abs'

fig, ax = plt.subplots(figsize=(7,5))

shap.plots.scatter(shap_values_xgb[:,feature], show=False,
                   title= f'Shapley values of {feature}',  
                   color=shap_values_xgb[:,col_feat], ax = ax) 

plt.xlabel(feature)
plt.ylabel('Shapley value of ' + feature)
plt.axhline(0, color='gray', ls='--')
plt.tight_layout()

plt.savefig(f'{WD}figures/0228_M5_{feature}_{col_feat}.png', dpi=300)

#%% Example of a big plot (not present in Thesis) Shapley analysis of Exp_PeatD
# 8 plots in 1, each plot colored by a different feature

fig, ((ax1,ax2,ax3,ax4), (ax5,ax6,ax7,ax8)) = plt.subplots(2,4,figsize=(25,10))

### AX1
shap.plots.scatter(shap_values_xgb[:,'Exp_PeatD'], show=False,
                   color=shap_values_xgb[:,'PAR_abs'], ax=ax1, ylabel=None,
                   alpha = 0.45)
ax1.set_ylabel('Shapley value')
ax1.set_xlabel('Exp_PeatD')
ax1.set_frame_on(True)
ax1.text(100,-1.5, 'Exp_PeatD &\nPAR_abs',fontdict={'fontweight':'bold'})


### AX2
shap.plots.scatter(shap_values_xgb[:,'Exp_PeatD'], show=False,
                   color=shap_values_xgb[:,'Tsfc'], ax=ax2,
                   alpha = 0.45)
ax2.set_ylabel('Shapley value')
ax2.set_xlabel('Exp_PeatD')
ax2.text(100,-1.5, ' Exp_PeatD &\nTsfc', fontdict={'fontweight':'bold'})


### AX3
shap.plots.scatter(shap_values_xgb[:,'Exp_PeatD'], show=False,
                   color=shap_values_xgb[:,'EVI'], ax=ax3,
                   alpha = 0.45)
ax3.set_ylabel('Shapley value')
ax3.set_xlabel('Exp_PeatD')
ax3.text(100,-1.5, ' Exp_PeatD\n& EVI', fontdict={'fontweight':'bold'})

### AX4
shap.plots.scatter(shap_values_xgb[:,'Exp_PeatD'], show=False,
                    color=shap_values_xgb[:,'Bld'], ax=ax4,
                    alpha = 0.45)
ax4.set_ylabel('Shapley value')
ax4.set_xlabel('Exp_PeatD')
ax4.text(100,-1.5, ' Exp_PeatD\n& Bld', fontdict={'fontweight':'bold'})

### AX5
shap.plots.scatter(shap_values_xgb[:,'Exp_PeatD'], show=False,
                   color=shap_values_xgb[:,'SuC'], ax=ax5, 
                   alpha = 0.45)
ax5.set_ylabel('Shapley value')
ax5.set_xlabel('Exp_PeatD')
ax5.text(100,-1.5, ' Exp_PeatD\n& SuC', fontdict={'fontweight':'bold'})

### AX6
shap.plots.scatter(shap_values_xgb[:,'Exp_PeatD'], show=False,
                    color=shap_values_xgb[:,'RH'], ax=ax6,
                    alpha = 0.45)
ax6.set_ylabel('Shapley value')
ax6.set_xlabel('Exp_PeatD')
ax6.text(100,-1.5, ' Exp_PeatD\n& RH', fontdict={'fontweight':'bold'})

### AX7
shap.plots.scatter(shap_values_xgb[:,'Exp_PeatD'], show=False,
                    color=shap_values_xgb[:,'Wat'], ax=ax7,
                    alpha = 0.45)
ax7.set_ylabel('Shapley value')
ax7.set_xlabel('Exp_PeatD')
ax7.text(100,-1.5, ' Exp_PeatD\n& Wat', fontdict={'fontweight':'bold'})

# hide AX8
# Hide the last subplot 
ax8.axis('off')


fig.subplots_adjust(wspace=0.3, hspace=0.2)

fig.suptitle('Shapley analysis of Air Exposed Peat Depth')

# Save figure
fig.savefig(f"{WD}/figures/0228_shap_Exp_PeatD_scatter8.png", dpi=300)

#%% Create Shapley plot of Exp_PeatD with linear regression for Exp_PeatD < 45
# Corresponds to Figure 8 in Thesis

# Select features included in the merged model
mer_M5feats = ['PAR_abs', 'Tsfc', 'RH', 'EVI', 'SuC', 'Wat', 'Bld', 'Exp_PeatD']
X = mer[mer_M5feats]

# Create subset of the merged dataset with Exp_PeatD < 45
mask = X.Exp_PeatD < 45
df = pd.DataFrame()

# Select Exp_PeatD values in X where Exp_PeatD is < 45
df['Exp_PeatD'] = X[mask].Exp_PeatD

# Select corresponding Shapley values for Exp_PeatD in this range
df['shapley'] = shap_values_xgb_mer[:,'Exp_PeatD'].values[mask]

# Perform ordinary least squares regression
lm_fit = smf.ols('shapley ~ Exp_PeatD', data=df).fit()

# Store coefficients and other results
b0 = lm_fit.params.Intercept.round(4)
b1 = lm_fit.params.Exp_PeatD.round(4)
conf_int = lm_fit.conf_int()
r2 = lm_fit.rsquared.round(2)

# Print results
print(lm_fit.summary())

#%% Plot figure 

# Plot Shapley values of Exp_PeatD
shap.plots.scatter(shap_values_xgb_mer[:,'Exp_PeatD'], show=False,
                   title= 'Linear regression on Shapley values for Exp_PeatD < 45', 
                   color=shap_values_xgb_mer[:,'Tsfc'], 
                   alpha=0.3, dot_size=8, cmap='viridis')

# Add x-axis label
plt.xlabel('Exp_PeatD [cm]')

# Create sequence of numbers for lin reg
xseq = np.linspace(0, 45, num=500)

# Plot regression line
plt.plot(xseq, b0 + b1 * xseq, color="black", lw=2, ls='dashed')

# Add text with the regression equation and performance
plt.text(60, -2, "y = %s + %sx \n$R^2$ = %s"
         % (b0, b1, r2))


# Plot confidence interval
y1 = conf_int.loc['Intercept', 0] + conf_int.loc['Exp_PeatD', 0] * xseq
y2 = conf_int.loc['Intercept', 1] + conf_int.loc['Exp_PeatD', 1] * xseq

# Fill the area of the confidence interval
plt.fill_between(xseq, y1, y2, color='lightgrey', alpha=0.9)

# Save figure
plt.savefig(f"{WD}/figures/0228_shap_{feature}_linreg_045.png", dpi=1000)

#%% Convert units of b1

#b1 = 0.0005 # can be used to calculate the uncertainty (= confidence interval of slope)
mol_m2_s = b1* (10 ** -6) # umol to mol
gram_m2_s = mol_m2_s * 44.0095 # CO2
kg_m2_s = gram_m2_s / 1000 # gram to kg
kg_ha_s = kg_m2_s * (10 ** 4) # m2 to ha
kg_ha_yr = kg_ha_s * 60 * 60 * 24 * 365.25 # s to year