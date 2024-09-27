"""
@author: l_vdp
edited by: arietma

original script name: seq_backw_feat_sel_sbfs.py

This script performs sequential backward floating selection in HPC.

Important: SBFS is run in six iterations. Currently the script is ready to run
for model iteration 5, by untagging it can be run for the other iterations. 
Each iteration has a different groundwater-related variable (BBB, OWD or Exp_PeatD),
and the airborne filter for built environment is either applied or not.

The script can be run on HPC, in parallel, with different folds of the merged 
dataset as a test set. Later, 'in analyse_metrics_sbfs.py', the fold that is
the final test set is selected.

Input: final merged dataset (.csv). Also: the pre-selected features
based on correlation and XGBoost feature importance, these are present in the code
and here denoted by first_sel_X.

Output: Dataframe metrics for every subset of features during the SBFS (.csv).  
Also, a dictionary of all the best features is saved in a textfile (.txt). For 
each model iteration, five different csv/txt files are produced, with each a 
different fold of the dataset that represents the test set.
These features with corresponding metrics are analysed in 'analyse_metrics_sbfs.py'.


Edits by arietma:
    - Adjusted the code to the dataset, features and model iterations used in 
    the current thesis
    - Changed the data division into train and test set (used to be random division)
    - Changed the code so that it can be run (in parellel) in HPC
"""

#%% Import packages

from mlxtend.feature_selection import SequentialFeatureSelector as SFS
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import r2_score, explained_variance_score
from sklearn.preprocessing import StandardScaler
from mlxtend.evaluate import bias_variance_decomp
from datetime import datetime
import sys

#%% Set up working directory and load data

WD = '/home/WUR/rietm018/thesis/'

# Load data
mer = pd.read_csv(f"{WD}merged_0228_final.csv", index_col=0, na_values='nan')
mer = mer.reset_index()

# Calculate week number for train-test data division
mer['Datetime'] = pd.to_datetime(mer['Datetime']) 
mer['weekno'] = mer['Datetime'].dt.isocalendar().week

#%% Add filter: exclude airborne observations with >15% built environment

# Only untag when using filter, i.e. when running the script for M4, M5 and M6

Bld_filter = (mer['Bld'] > 0.15) & (mer['source']== 'airborne')
mer = mer[-Bld_filter]


#%% Divide data in 5 folds based on week number

weeks = list(range(1, 51))  # list of 50 weeks (so even 10 weeks per fold)
folds = [[] for _ in range(5)]  #  5 empty lists for storing the week numbers

# assign week numbers to each fold, avoid consecutive weeks in each fold
for i, week in enumerate(weeks, 1):
    fold_index = i % 5  # % gives remainder of division and is used to cycle through the week numbers
    folds[fold_index].append(week) # so fold 1 has week numbers 5, 10, 15, 20 etc.
    
# Check how many obs per fold 
fold1 = mer[mer['weekno'].isin(folds[0])]
fold2 = mer[mer['weekno'].isin(folds[1])]
fold3 = mer[mer['weekno'].isin(folds[2])]
fold4 = mer[mer['weekno'].isin(folds[3])]
fold5 = mer[mer['weekno'].isin(folds[4])]
    
# give fold3 and fold4 the remaining weeks since these contain the least observations
folds[2] = folds[2]+[51]
folds[3] = folds[3]+[52]

# update fold 3 and 4
fold3 = mer[mer['weekno'].isin(folds[2])]
fold4 = mer[mer['weekno'].isin(folds[3])]


#%% Organize features
# Updated soil classes to exclude peat classes
LGN_classes = ['Grs', 'SuC', 'SpC', 'Ghs', 'dFr', 'cFr', 'Wat',
       'Bld', 'bSl', 'Hth', 'FnB', 'Shr']

soil_classes = ['W', 'zandG', 'zeeK', 'rivK', 'gedA', 'leem']

all_feats = ['PAR_abs', 'Tsfc', 'VPD', 'RH', 'NDVI', 'EVI', 'BBB', 'GWS', 'OWD', 'PeatD', 'Exp_PeatD'] + LGN_classes + soil_classes

# For now, discard all groundwater-related variables. Under 'Define model iterations',
# specify which groundwater-related variable to include in the iteration
discarded = ['NDVI', 'VPD', 'leem', 'Grs', 'GWS', 'rivK', 'bSl', 'Ghs', 'Hth', 'dFr', 'SpC', 'Shr', 'W', 'cFr', 'BBB', 'GWS', 'OWD', 'PeatD', 'Exp_PeatD']

first_sel_m = [feat for feat in all_feats if feat not in discarded]

#%% Set up connection to SLURM_ARRAY_TASK_ID to run the script as a job array (=parallel, and faster)

args = sys.argv[1:]
slurm_task_id = int(args[0]) # in the sbatch file: #SBATCH --array=1-5

#%% Split in train and test data

# The script is now run in parallel, with each data fold being the test fold once

dataframes = [fold1, fold2, fold3, fold4, fold5]

foldno = slurm_task_id # connects to array id
test_data = dataframes[foldno-1] # foldno -1 is added because indexing starts at 0

# Make a list for the train data without the test fold:
train_data_list = [data for j, data in enumerate(dataframes) if j != foldno-1] 
train_data = pd.concat(train_data_list)

#%% Define model iterations

# Untag only one of the iterations, each with a different groundwater-related
# variable. 
# Remember to adjust the file names written at the bottom of the script accordingly


# Model iterations 1 and 4 (for 4, also untag Bld filter): with OWD and PeatD
# X_train = train_data[first_sel_m + ['PeatD', 'OWD']]
# y_train = train_data['CO2flx']

# X_test = test_data[first_sel_m + ['PeatD', 'OWD']]
# y_test = test_data['CO2flx']


# Model iterations 2 and 5 (for 5, also untag Bld filter): with Exp_PeatD
X_train = train_data[first_sel_m + ['Exp_PeatD']]
y_train = train_data['CO2flx']

X_test = test_data[first_sel_m + ['Exp_PeatD']]
y_test = test_data['CO2flx']


# # Model iterations 3 and 6 (for 6, also untag Bld filter): with BBB and PeatD
# X_train = train_data[first_sel_m + ['PeatD', 'BBB']]
# y_train = train_data['CO2flx']

# X_test = test_data[first_sel_m + ['PeatD', 'BBB']]
# y_test = test_data['CO2flx']

# %% Scale

sc = StandardScaler()

X_train_sc = pd.DataFrame(sc.fit_transform(X_train), columns=X_train.columns)
X_test_sc = pd.DataFrame(sc.transform(X_test), columns=X_train.columns)

#%% Prepare model with standard hyperparameters

model = XGBRegressor(n_estimators = 1000, learning_rate= 0.05, max_depth=6, subsample=1)
sfs_scoring = 'r2'

#%% function to run sequential backward floating selection

def feature_selection(model, n_features, X_train, y_train):
    sfs1 = SFS(model, k_features=n_features, forward=False, floating=True,
               verbose=2, scoring=sfs_scoring, cv=10)
    sfs1 = sfs1.fit(X_train, y_train)

    best_features = list(sfs1.k_feature_names_)
    best_score = sfs1.k_score_
    return best_features, best_score

#%% Prepare dict to store which features score best each round
# and dataframe to store metrics of the model with these subsets of features

results = {}
metrics = ['mse', 'bias', 'var', 'r2', 'expl_var']
metrics_df = pd.DataFrame(index=range(len(X_train.columns)), columns=metrics)
#%% run SBFS (takes long, couple of days)
start = datetime.now()

# SBFS starts at all features, goes back to 4 features 
# (it is expected that <4 feautres won't perform well)

for i in range(4,len(X_train.columns)): 
    n_features=i
    print(i, '/', len(X_train.columns))
    print('sbfs function...')
    top_features, score = feature_selection(model, n_features=i, 
                                            X_train = X_train_sc,
                                            y_train = y_train)
    
    # store top features in dict
    results[i] = top_features
    
    # get X with top_features
    X_train_top = X_train_sc[top_features]
    X_test_top = X_test_sc[top_features]
    
    print('fitting model...')
    # fit model with top features
    model.fit(X_train_top, y_train)
    y_pred = model.predict(X_test_top)
    
    # calculate metrics
    r2 = r2_score(y_test, y_pred)
    expl_var = explained_variance_score(y_test,y_pred)
    
    print('bias-variance...')
    # calculate bias-variance trade-off
    mse, bias, var = bias_variance_decomp(model, X_train_top.values, y_train.values, X_test_top.values, y_test.values, loss='mse', num_rounds=200, random_seed=1)
    
    # store metrics in dataframe
    metrics_df.loc[i][metrics] = [mse, bias, var, r2, expl_var]
    
end = datetime.now()
print(end-start)

# Save metrics dataframe
# TO BE SPECIFIED based on the model iteration
metrics_df.to_csv(f"{WD}modelling/0228_mer_featsel_metrics_basedonSBSF_r2_mlxtend_M5_testfold{foldno}.csv")

# Save top features dict as string in textfile
# TO BE SPECIFIED based on the model iteration
text_file = f"{WD}/modelling/0228_mer_feats_basedonSBSF_r2_mlxtend_M5_testfold{foldno}.txt"

f = open(text_file,"w")

# Write file
f.write( str(results) )

# Close file
f.close()
