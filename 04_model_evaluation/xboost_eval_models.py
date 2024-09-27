# -*- coding: utf-8 -*-
"""
@author: l_vdp
edited by: arietma
This script evaluates the final models and produces a plot with the scores.

Input: final merged dataset (.csv), optimized features and 
hyperparameters, given in the code. 
Output: model performances and figure showing the performance of the models

Edits by arietma:
    - Adjusted the code to the dataset, model iterations and the data folds 
    used as test folds in the current thesis
"""

#%% Import packages

import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from xgboost.sklearn import XGBRegressor
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap
import numpy as np

#%% Set up working directory and load data

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/' 
mer = pd.read_csv(f"{WD}merged_0228_final.csv", index_col=0)

# Calculate week number, later used for train-test data division
mer['Datetime'] = pd.to_datetime(mer['Datetime']) 
mer['weekno'] = mer['Datetime'].dt.isocalendar().week

#%% Define features and optimized hyperparameters
# define 6 different merged models, models 1-3 are without a filter for built 
# environment, models 4-6 have a filter for Bld>0.15

# 0228
mer_M1feats = ["PAR_abs", "Tsfc", "RH", "EVI", "SuC", "Bld"]
mer_M1hypp = {'learning_rate': 0.001, 'max_depth': 6, 'n_estimators': 4000, 'subsample': 0.7}

mer_M2feats = ["PAR_abs", "Tsfc", "RH", "EVI", "SuC", "Bld"]
mer_M2hypp = {'learning_rate': 0.001, 'max_depth': 6, 'n_estimators': 4000, 'subsample': 0.7}

mer_M3feats = ["PAR_abs", "Tsfc", "RH", "EVI", "SuC", "Bld"]
mer_M3hypp = {'learning_rate': 0.001, 'max_depth': 6, 'n_estimators': 4000, 'subsample': 0.7}

mer_M4feats = ["PAR_abs", "Tsfc", "RH", "EVI", "SuC", "Wat", "Bld", "OWD"]
mer_M4hypp = {'learning_rate': 0.005, 'max_depth': 6, 'n_estimators': 750, 'subsample': 0.65}

mer_M5feats = ['PAR_abs', 'Tsfc', 'RH', 'EVI', 'SuC', 'Wat', 'Bld', 'Exp_PeatD'] 
mer_M5hypp = {'learning_rate': 0.001, 'max_depth': 6, 'n_estimators': 4000, 'subsample': 0.55}

mer_M6feats = ["PAR_abs", "Tsfc", "RH", "EVI", "SuC", "Wat", "Bld"]
mer_M6hypp = {'learning_rate': 0.005, 'max_depth': 6, 'n_estimators': 1000, 'subsample': 0.6}

#%% Specify Bld filter 

# Exclude airborne observations with >15% built environment
Bld_filter = (mer['Bld'] > 0.15) & (mer['source']== 'airborne')
mer_Bldfilt = mer[-Bld_filter]

#%% function to evaluate all models

def evalmodel(data, feats, hyperparams):

    # Division of train/test data
    weeks = list(range(1, 51))  # list of 50 weeks (so even 10 weeks per fold)
    folds = [[] for _ in range(5)]  #  5 empty lists for storing the week numbers

    # assign week numbers to each fold, avoid consecutive weeks in each fold
    for i, week in enumerate(weeks, 1):
        fold_index = i % 5  # % gives remainder of division and is used to cycle through the week numbers
        folds[fold_index].append(week) # so fold 1 has week numbers 5, 10, 15, 20 etc.
        
    # Check how many obs per fold 
    fold1 = data[data['weekno'].isin(folds[0])]
    fold2 = data[data['weekno'].isin(folds[1])]
    fold3 = data[data['weekno'].isin(folds[2])]
    fold4 = data[data['weekno'].isin(folds[3])]
    fold5 = data[data['weekno'].isin(folds[4])]
        
    # give fold3 and fold4 the remaining weeks since these contain the least observations
    folds[2] = folds[2]+[51]
    folds[3] = folds[3]+[52]

    # update fold 3 and 4
    fold3 = data[data['weekno'].isin(folds[2])]
    fold4 = data[data['weekno'].isin(folds[3])]

    test_data = fold4
    train_data = pd.concat([fold1, fold2, fold3, fold5])
    
    # Define train and test variables and Y
    X_train = train_data[feats]
    y_train = train_data['CO2flx']
    
    X_test = test_data[feats]
    y_test = test_data['CO2flx']

    # scale
    sc = StandardScaler()

    X_train_sc = pd.DataFrame(sc.fit_transform(X_train), columns=X_train.columns)
    X_test_sc = pd.DataFrame(sc.transform(X_test),columns=X_train.columns)
    
    # model with the correct hyperparameters
    xgbr = XGBRegressor(learning_rate = hyperparams['learning_rate'], 
                  max_depth = hyperparams['max_depth'], 
                  n_estimators = hyperparams['n_estimators'],
                  subsample = hyperparams['subsample'])
    
    # to show that you need to do testing and training, you can also train AND test on the same dataset
    # X_sc = pd.DataFrame(sc.fit_transform(X), columns=X.columns)
    # X_train_sc = X_sc; y_train = y; X_test_sc = X_sc; y_test = y 

    # fit model    
    xgbr.fit(X_train_sc, y_train)
    
    # predict values for test set
    y_pred = xgbr.predict(X_test_sc)
    
    # compute scores
    MSE = mean_squared_error(y_test,y_pred)
    R2 = r2_score(y_test,y_pred)
    return MSE, R2, y_pred, y_test

#%% evaluate all models and store results in variables

mer_M1MSE, mer_M1R2, mer_M1ypred, mer_M1ytest = evalmodel(mer, mer_M1feats, mer_M1hypp)
mer_M2MSE, mer_M2R2, mer_M2ypred, mer_M2ytest = evalmodel(mer, mer_M2feats, mer_M2hypp)
mer_M3MSE, mer_M3R2, mer_M3ypred, mer_M3ytest = evalmodel(mer, mer_M3feats, mer_M3hypp)
mer_M4MSE, mer_M4R2, mer_M4ypred, mer_M4ytest = evalmodel(mer_Bldfilt, mer_M4feats, mer_M4hypp)
mer_M5MSE, mer_M5R2, mer_M5ypred, mer_M5ytest = evalmodel(mer_Bldfilt, mer_M5feats, mer_M5hypp)
mer_M6MSE, mer_M6R2, mer_M6ypred, mer_M6ytest = evalmodel(mer_Bldfilt, mer_M6feats, mer_M6hypp)

#%% prepare for hexbin colors

binary = cm.get_cmap('binary', 256)
newcolors = binary(np.linspace(0, 15,256))

newcmp = ListedColormap(newcolors)

#%% Plot figure 
fig, ax = plt.subplots(2,3,sharex=True, sharey=True, figsize=(6,6))

# M1
ax[0,0].hexbin(mer_M1ytest, mer_M1ypred, gridsize=(20), cmap = newcmp)
#ax[0,0].scatter(mer_M1ytest, mer_M1ypred, label = 'Merged 1', s=10)
ax[0,0].plot(range(-50,50), range(-50,50), '--', c='red')
ax[0,0].set_title('Merged 1')
ax[0,0].set_xlabel('True CO2')
ax[0,0].set_ylabel('Predicted CO2')
ax[0,0].text(-47,40, 'R2: '+ str(mer_M1R2.round(2)))
ax[0,0].text(-47,30, 'MSE: '+ str(mer_M1MSE.round(1)))

# M2
ax[0,1].hexbin(mer_M2ytest, mer_M2ypred, gridsize=(20), cmap = newcmp)
#ax[0,1].scatter(mer_M2ytest, mer_M2ypred, label = 'Merged 2', s=10)
ax[0,1].plot(range(-50,50), range(-50,50), '--', c='red')
ax[0,1].set_title('Merged 2')
ax[0,1].set_xlabel('True CO2')
ax[0,1].set_ylabel('Predicted CO2')
ax[0,1].text(-47,40, 'R2: '+ str(mer_M2R2.round(2)))
ax[0,1].text(-47,30, 'MSE: '+ str(mer_M2MSE.round(1)))

# M3
ax[0,2].hexbin(mer_M3ytest, mer_M3ypred, gridsize=(20), cmap = newcmp)
#ax[0,2].scatter(mer_M3ytest, mer_M3ypred, label = 'Merged 3', s=10)
ax[0,2].plot(range(-50,50), range(-50,50), '--', c='red')
ax[0,2].set_title('Merged 3')
ax[0,2].set_xlabel('True CO2')
ax[0,2].set_ylabel('Predicted CO2')
ax[0,2].text(-47,40, 'R2: '+ str(mer_M3R2.round(2)))
ax[0,2].text(-47,30, 'MSE: '+ str(mer_M3MSE.round(1)))

# M4
ax[1,0].hexbin(mer_M4ytest, mer_M4ypred, gridsize=(20), cmap = newcmp)
#ax[1,0].scatter(mer_M4ytest, mer_M4ypred, label = 'Merged 4', s=10)
ax[1,0].plot(range(-50,50), range(-50,50), '--', c='red')
ax[1,0].set_title('Merged 4')
ax[1,0].set_xlabel('True CO2')
ax[1,0].set_ylabel('Predicted CO2')
ax[1,0].text(-47,40, 'R2: '+ str(mer_M4R2.round(2)))
ax[1,0].text(-47,30, 'MSE: '+ str(mer_M4MSE.round(1)))

# M5
ax[1,1].hexbin(mer_M5ytest, mer_M5ypred, gridsize=(20), cmap = newcmp)
#ax[1,1].scatter(mer_M5ytest, mer_M5ypred, label = 'Merged 5', s=10)
ax[1,1].plot(range(-50,50), range(-50,50), '--', c='red')
ax[1,1].set_title('Merged 5')
ax[1,1].set_xlabel('True CO2')
ax[1,1].set_ylabel('Predicted CO2')
ax[1,1].text(-47,40, 'R2: '+ str(mer_M5R2.round(2)))
ax[1,1].text(-47,30, 'MSE: '+ str(mer_M5MSE.round(1)))

# M6
ax[1,2].hexbin(mer_M6ytest, mer_M6ypred, gridsize=(20), cmap = newcmp)
#ax[1,2].scatter(mer_M6ytest, mer_M6ypred, label = 'Merged 6', s=10)
ax[1,2].plot(range(-50,50), range(-50,50), '--', c='red')
ax[1,2].set_title('Merged 6')
ax[1,2].set_xlabel('True CO2')
ax[1,2].set_ylabel('Predicted CO2')
ax[1,2].text(-47,40, 'R2: '+ str(mer_M6R2.round(2)))
ax[1,2].text(-47,30, 'MSE: '+ str(mer_M6MSE.round(1)))



fig.suptitle('Performance of six models')
plt.subplots_adjust(wspace=0.3, hspace=0.3)

#%% save figure

fig.savefig(f'{WD}figures/preds_final_models_optimizedhypp_0228_hexbin.png', bbox_inches='tight', dpi=1000)