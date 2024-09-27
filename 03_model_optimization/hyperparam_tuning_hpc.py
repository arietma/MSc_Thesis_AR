"""
@author: l_vdp
edited by: arietma

original script name: hyperparam_tuning.py

This script looks for the best hyperparameters for the XGBoost model in a grid-mannered
way (using GridSearchCV), in HPC. Un-comment the model iteration the script should 
be run for. This script needs a long time to run (~4-5 days).

Input: Final merged datasets (.csv). Also, here written in the code,
the selected features after SBFS. 

Output: Textfile with the optimal hyperparameters (.txt).

Edits by arietma:
    - Adjusted the code to the dataset, features, and model iterations used in 
    the current thesis
    - Changed the data division into train and test set (used to be random division)
    - Changed the code so that it can be run in HPC

"""
#%% Import packages

import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler
from xgboost.sklearn import XGBRegressor
from datetime import datetime

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

#%% Specify features
# Only untag the features for the model iteration that is run, in this case, M5

# M1
# feats = ["PAR_abs", "Tsfc", "RH", "EVI", "SuC", "Bld"]

# M2
# feats = ["PAR_abs", "Tsfc", "RH", "EVI", "SuC", "Bld"]

# M3
# feats = ["PAR_abs", "Tsfc", "RH", "EVI", "SuC", "Bld"]

# M4
# feats = ["PAR_abs", "Tsfc", "RH", "EVI", "SuC", "Wat", "Bld", "OWD"]

# M5
feats = ['PAR_abs', 'Tsfc', 'RH', 'EVI', 'SuC', 'Wat', 'Bld', 'Exp_PeatD']

# M6
# feats = ["PAR_abs", "Tsfc", "RH", "EVI", "SuC", "Wat", "Bld"]

#%% Divide data in 5 folds based on week number

weeks = list(range(1, 51))  # list of 50 weeks (so even 10 weeks per fold)
folds = [[] for _ in range(5)]  #  5 empty lists for storing the week numbers

# Assign week numbers to each fold, avoid consecutive weeks in each fold
for i, week in enumerate(weeks, 1):
    fold_index = i % 5  # % gives remainder of division and is used to cycle through the week numbers
    folds[fold_index].append(week) # so fold 1 has week numbers 5, 10, 15, 20 etc.
    
# Check how many observations per fold 
fold1 = mer[mer['weekno'].isin(folds[0])]
fold2 = mer[mer['weekno'].isin(folds[1])]
fold3 = mer[mer['weekno'].isin(folds[2])]
fold4 = mer[mer['weekno'].isin(folds[3])]
fold5 = mer[mer['weekno'].isin(folds[4])]
    
# Give fold3 and fold4 the remaining weeks since these contain the least observations
folds[2] = folds[2]+[51]
folds[3] = folds[3]+[52]

# Update fold 3 and 4
fold3 = mer[mer['weekno'].isin(folds[2])]
fold4 = mer[mer['weekno'].isin(folds[3])]

# Define which data fold is the test set, the same for all iterations
test_data = fold4
train_data = pd.concat([fold1, fold2, fold3, fold5])


#%% Get train and test folder

X_train = train_data[feats]
y_train = train_data['CO2flx']

X_test = test_data[feats]
y_test = test_data['CO2flx']

#%% Scale X data
sc = StandardScaler()

X_train_sc = pd.DataFrame(sc.fit_transform(X_train), columns=X_train.columns)
X_test_sc = pd.DataFrame(sc.transform(X_test),columns=X_train.columns)


#%% Initialize XGBoost
xgb1 = XGBRegressor()

#%% Hyperparameters grid
parameters = {'n_estimators':[750, 1000, 4000,7000],
              'max_depth':[3, 6, 9, 12], 
              'learning_rate':[0.1, 0.05, 0.01, 0.005, 0.001],
              'subsample': [0.55, 0.6, 0.65, 0.7, 0.8, 1]}

#%% Prepare Grid Search CV 
xgb_grid = GridSearchCV(xgb1,
                        parameters,
                        verbose=2,
                        cv = 10, 
                        scoring = 'r2'  )

#%% Run the grid search (takes long, a couple of days)
start = datetime.now()

xgb_grid.fit(X_train,  y_train)  

end = datetime.now()
print(end-start)

#%% Print results
print(xgb_grid.best_score_)
print(xgb_grid.best_params_)

#%% Get and print scores of these optimal hyperparams
y_pred = xgb_grid.predict(X_test)
print('R2:')
print(r2_score(y_test, y_pred))
print('MSE of the result is:')
print(mean_squared_error(y_test, y_pred))

#%% Save results
params = xgb_grid.best_params_

# Save best hyperparameters in textfile
# TO BE SPECIFIED based on the iteration
text_file = f"{WD}/modelling/mer0228_hyperp_M5.txt"
f = open(text_file,"w")

# Write file
f.write( str(params) )

# Close file
f.close()