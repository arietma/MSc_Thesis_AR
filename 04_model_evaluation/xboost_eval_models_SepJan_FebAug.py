"""
@author: l_vdp
edited by: arietma, edited from: xboost_eval_models.py

This script evaluates the seasonal models and gives their performance scores.

Input: final seasonal datasets (SepJan and FebAug), features and 
hyperparameters, given in the code. 
Output: figure showing the performance of the models

Edits by arietma:
    - Adjusted the code to the seasonal datasets, model specs and the data folds 
    used as test folds in the current thesis
"""

#%% Import packages

import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from xgboost.sklearn import XGBRegressor

#%% Set up working directory and load data

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/' 

# Specify for which seasonal data and model the script is run
months = 'FebAug' #or 'SepJan' 
mer = pd.read_csv(f"{WD}merged_{months}_0228.csv", index_col=0, na_values='nan')

# Calculate week number, later used for train-test data division
mer['Datetime'] = pd.to_datetime(mer['Datetime']) 
mer['weekno'] = mer['Datetime'].dt.isocalendar().week

#%% Define features and optimized hyperparameters

# Seasonal models have the same features
mer_feats = ['PAR_abs', 'Tsfc', 'RH', 'EVI', 'Bld', 'Wat', 'Exp_PeatD']

if months == 'SepJan':
    mer_hypp = {'learning_rate': 0.001, 'max_depth': 9, 'n_estimators': 4000, 'subsample': 0.55}
elif months == 'FebAug':
    mer_hypp = {'learning_rate': 0.001, 'max_depth': 3, 'n_estimators': 7000, 'subsample': 0.65}

#%% Specify Bld filter 

# Exclude airborne observations with >15% built environment
Bld_filter = (mer['Bld'] > 0.15) & (mer['source']== 'airborne')
mer_Bldfilt = mer[-Bld_filter]

#%% function to evaluate all models

def evalmodel(data, feats, hyperparams, months):
    
    # Specify relevant week numbers for autumn or spring 
    if months == 'SepJan':
        weeks = list(range(1, 6)) + list(range(35, 53))  # SepJan
    elif months == 'FebAug':
        weeks = list(range(5,36)) # FebAug, 31 weeks

    # Create 5 empty lists for storing the week numbers
    folds = [[] for _ in range(5)]  

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
    
    # Both models have the same data fold as test set
    test_data = fold5
    train_data = pd.concat([fold1, fold2, fold3, fold4])
  
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
    
    # compute scores
    y_pred = xgbr.predict(X_test_sc)
    MSE = mean_squared_error(y_test,y_pred)
    R2 = r2_score(y_test,y_pred)
    return MSE, R2, y_pred, y_test

#%% evaluate all models and store results in variables
mer_MSE, mer_R2, mer_ypred, mer_ytest = evalmodel(mer_Bldfilt, mer_feats, mer_hypp, months = months)
