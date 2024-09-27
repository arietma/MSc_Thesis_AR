"""
@author: lvdpoel
Edited by: arietma, edited from: seq_backw_feat_sel_sbfs.py

This script calculates the metrics of the seasonal models before hyperparameter
optimization, and is used to select a data fold as test fold for hyperparameter
optimization. The datafold used as test fold for both seasonal models is data 
fold 5, as these folds show average performance compared to all others. 
The script should be run once for SepJan, and once for FebAug

Input: the final seasonal datasets, and the features to be included in the 
seasonal models, which is based on the features included in the merged model
Output: model metrics for the seasonal models (5 csv's for each seasonal model,
                                               with each csv a different test fold)

Edits by arietma:
    - Specified the script for the seasonal datasets and models
    - Included different data folds based on week number
    - Changed division of train-test data
"""

#%% Import packages

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, explained_variance_score
from xgboost.sklearn import XGBRegressor
from mlxtend.evaluate import bias_variance_decomp

#%% Load in data

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/' 

mer_SepJan = pd.read_csv(f'{WD}merged_SepJan_0228.csv',
                   index_col=0, na_values='nan')
mer_FebAug = pd.read_csv(f'{WD}merged_FebAug_0228.csv',
                   index_col=0, na_values='nan')

# Calculate week number for train-test data division
mer_SepJan['Datetime'] = pd.to_datetime(mer_SepJan['Datetime']) 
mer_SepJan['weekno'] = mer_SepJan['Datetime'].dt.isocalendar().week

mer_FebAug['Datetime'] = pd.to_datetime(mer_FebAug['Datetime']) 
mer_FebAug['weekno'] = mer_FebAug['Datetime'].dt.isocalendar().week

#%%
feats = ['PAR_abs', 'Tsfc', 'RH', 'EVI', 'Bld', 'Wat', 'Exp_PeatD']
#months = 'SepJan' # or 
months = 'FebAug'

#%% Divide data in 5 folds based on week number

if months == 'SepJan':
    mer_subset = mer_SepJan
elif months == 'FebAug':
    mer_subset = mer_FebAug
    
# Specify relevant week numbers    
if months == 'SepJan':
    weeks = list(range(1, 6)) + list(range(35, 53))  # SepJan
elif months == 'FebAug':
    weeks = list(range(5,36)) # FebAug, 31 weeks

# Create 5 empty lists for storing the week numbers
folds = [[] for _ in range(5)]  

# Assign week numbers to each fold, avoid consecutive weeks in each fold
for i, week in enumerate(weeks, 1):
    fold_index = i % 5  # % gives remainder of division and is used to cycle through the week numbers
    folds[fold_index].append(week) 
    
# Make 5 subsets each with the specified week numbers
# Each of these 'folds' is used as a test fold in the following code
fold1 = mer_subset[mer_subset['weekno'].isin(folds[0])]
fold2 = mer_subset[mer_subset['weekno'].isin(folds[1])]
fold3 = mer_subset[mer_subset['weekno'].isin(folds[2])]
fold4 = mer_subset[mer_subset['weekno'].isin(folds[3])]
fold5 = mer_subset[mer_subset['weekno'].isin(folds[4])]

#%% Calculate the model performance metrics, iterating over different data folds
# as test folds. 

dataframes = [fold1, fold2, fold3, fold4, fold5]
for foldno, test_data in enumerate(dataframes, start=1): #iterates over foldnumbers 1-5)

    test_data = dataframes[foldno-1]
    
    # gives a list without the test fold:
    train_data_list = [data for j, data in enumerate(dataframes) if j != foldno-1] # foldno -1 is added because indexing starts at 0
    
    # Get train data
    train_data = pd.concat(train_data_list)
    
    # Specify X and Y for train and test data
    X_train = train_data[feats]
    y_train = train_data['CO2flx']

    X_test = test_data[feats]
    y_test = test_data['CO2flx']

    # Scale X data
    sc = StandardScaler()
    X_train_sc = pd.DataFrame(sc.fit_transform(X_train), columns=X_train.columns)
    X_test_sc = pd.DataFrame(sc.transform(X_test),columns=X_train.columns)
    
    # Prepare model with standard hyperparameters
    model = XGBRegressor(n_estimators = 1000, learning_rate= 0.05, max_depth=6, subsample=1)
    sfs_scoring = 'r2'

    # Initialize df for storing results
    results = {}
    metrics = ['mse', 'bias', 'var', 'r2', 'expl_var']
    metrics_df = pd.DataFrame(index=range(1,6), columns=metrics)
    
    print('fitting model...')
    # Fit model with selected features
    model.fit(X_train_sc, y_train)
    y_pred = model.predict(X_test_sc)
    
    # calculate metrics
    r2 = r2_score(y_test, y_pred)
    expl_var = explained_variance_score(y_test,y_pred)
    
    print('bias-variance...')
    # Calculate bias-variance trade-off 
    mse, bias, var = bias_variance_decomp(model, X_train_sc.values, y_train.values, X_test_sc.values, y_test.values, loss='mse', num_rounds=200, random_seed=1)
    
    print('storing variables')
    # Store metrics in dataframe
    metrics_df.loc[foldno][metrics] = [mse, bias, var, r2, expl_var]
    
    # Save metrics
    # {months} shows whether it's run for SepJan or FebAug, {foldno} shows the
    # data fold that is used as test fold
    print('writing csv')
    metrics_df.to_csv(f"{WD}modelling/0228_mer_{months}_featsel_metrics_basedonSBSF_r2_mlxtend_M5_{foldno}.csv")

