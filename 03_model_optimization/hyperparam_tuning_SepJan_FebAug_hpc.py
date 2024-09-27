"""
@author: l_vdp
edited by: arietma, edited from: hyperparam_tuning.py

This script looks for the best hyperparameters for the XGBoost model in a grid-mannered
way (using GridSearchCV), in HPC, for the seasonal models 'FebAug' and 'SepJan'.
This script needs a long time to run (~4-5 days). Important: this script should
be run twice, once for SepJan and once for FebAug. This can be specified in the
'months' variable.

Input: Final SepJan and FebAug datasets (.csv). Also, here written in the code,
the selected features, which were manually selected after the SBFS in the merged
model. 

Output: Textfile with the optimal hyperparameters (.txt).

Edits by arietma:
    - Adjusted the code to the seasonal datasets, features, and model iterations 
    used in the current thesis
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

# Define variable 'months' to choose for which seasonal model the script is run
# months variable is used for:
    # loading in the merged dataset
    # specifying the week numbers for dividing the data into train and test sets
    # specifying the names for the output files

months = 'FebAug' # 'SepJan' 

# Load dataset
mer = pd.read_csv(f"{WD}merged_{months}_0228.csv", index_col=0, na_values='nan')
mer = mer.reset_index()

# Calculate week number for train-test data division
mer['Datetime'] = pd.to_datetime(mer['Datetime']) 
mer['weekno'] = mer['Datetime'].dt.isocalendar().week

#%% Add filter: exclude airborne observations with >15% built environment

Bld_filter = (mer['Bld'] > 0.15) & (mer['source']== 'airborne')
mer = mer[-Bld_filter]

#%% Specify features
# Both seasonal models are built with the same features, so that model results
# can be compared 

feats = ['PAR_abs', 'Tsfc', 'RH', 'EVI', 'Bld', 'Wat', 'Exp_PeatD']

#%% Divide data in 5 folds based on week number

# Specify relevant week numbers for autumn or spring
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
fold1 = mer[mer['weekno'].isin(folds[0])]
fold2 = mer[mer['weekno'].isin(folds[1])]
fold3 = mer[mer['weekno'].isin(folds[2])]
fold4 = mer[mer['weekno'].isin(folds[3])]
fold5 = mer[mer['weekno'].isin(folds[4])]

# Both seasonal models have the same data fold as test set
test_data = fold5
train_data = pd.concat([fold1, fold2, fold3, fold4])

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

#%% Run the grid search (takes long, couple of days)
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
text_file = f"{WD}/modelling/mer0228_{months}_hyperp.txt"
f = open(text_file,"w")

# Write file
f.write( str(params) )

# Close file
f.close()