"""
@author: l_vdp
edited by: arietma

This script calculates the feature importances based on the feature selection 
method embedded in XGBoost.

Input: Final mer dataset (.csv)
Output: dataframe with all feature importances for all features (.csv),
and a plot visualising these feature importances. The plot corresponds to Figure
4 (right) in the current thesis

Edits by arietma:
    - Adjusted the code to the dataset and features used in the current thesis
    - Only calculate feature importance for the merged dataset, not for the
    airborne and tower datasets separately, since in the current thesis
    only the merged dataset/model is used
    - Added red line in figure to clarify which features are dropped before
    moving on to SBFS (the least important features)

"""

#%% Import packages

import pandas as pd
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

#%% Set up working directory and load data

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'

mer = pd.read_csv(f"{WD}merged_0228_final.csv", 
                  index_col=0)

#%% Overview of features

LGN_classes = ['Grs', 'SuC', 'SpC', 'Ghs', 'dFr', 'cFr', 'Wat',
       'Bld', 'bSl', 'Hth', 'FnB', 'Shr']
soil_classes = ['hV', 'W', 'pV', 'kV', 'hVz', 'V',
       'Vz', 'aVz', 'kVz', 'overigV', 'zandG', 'zeeK', 'rivK', 'gedA', 'leem']


meteo_vars = ['Tsfc', 'VPD', 'PAR_abs']
owasis_vars = ['BBB', 'OWD' , 'GWS']

all_feats = ['PAR_abs', 'Tsfc', 'VPD', 'RH', 'NDVI', 'EVI', 'BBB', 'GWS', 'OWD', 'PeatD', 'Exp_PeatD'] + LGN_classes + soil_classes


feature_names=np.array(all_feats)

#%% Prepare X and y for the merged dataset

mer_X = mer[all_feats]
mer_y = mer['CO2flx']

#%% function to get feature importances

def xgboost_fi(X,y):
  
  # scale X data
  sc = StandardScaler()
  X_sc = pd.DataFrame(sc.fit_transform(X), columns=X.columns)

  # fit model on all data with standard hyperparameters
  model = XGBRegressor(n_estimators = 1000, learning_rate= 0.1, max_depth=6, subsample=1)
  model.fit(X_sc, y)

  # feature importances embedded in model:
  feat_imps = model.feature_importances_
  return feat_imps

#%% Run function

mer_imps = xgboost_fi(mer_X, mer_y)

#%% Organize results

mer_results = pd.DataFrame(columns = ['feat', 'importance', 'CO2_feature'])
mer_results['feat'] = feature_names
mer_results['importance'] = mer_imps
mer_results['CO2_feature'] ='CO2flx'
mer_results['datatype'] = 'mer'

# Sort feature importances for plotting purpose
mer_results = mer_results.sort_values(by='importance', ascending=False, key=abs)

#%% Create figure of feature importance, corresponds to Figure 4 (right) in thesis

sns.set_style("white")
fig, ax = plt.subplots(figsize=(5,7))
sns.barplot( x=mer_results.importance, y =mer_results.feat, color = sns.color_palette()[0])
plt.title('Feature importance based on XGBoost')
plt.xlabel('XGBoost Feature Importance')
plt.ylabel('Features')

# The last 14 features do not continue to SBFS, indicated by a red line:
plt.axhline(y= 23.5,color = 'red', linestyle = '--')

plt.tight_layout()

# Save figure
fig.savefig(f'{WD}figures/0228_mer_selectedfeat_xgboostimps_redline.png',dpi=1000)
