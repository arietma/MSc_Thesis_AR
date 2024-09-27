# -*- coding: utf-8 -*-
"""
@author: l_vdp
edited by: arietma, edited from: sim_create_overview_df.py

This script creates a dataframe with CO2 simulations for many combinations of 
PAR and EVI. Also, bootstrapped sampling is performed to later show the bootstrap 
intervals in sim_boot_make_bigplot_EVI.py. The script takes ~4.5 hours to run.

Input: final merged dataset, and create_df_EVI function from prepare_data_for_simulations_EVI.py.
Output: 3 dataframes with CO2 predictions for every present combination of PAR and Tsfc
        - boot_simulation_average_EVI:  average for every prediction across all bootstrapped samples
        - boot_simulation_5_EVI:        5th percentile for every prediction across all bootstrapped samples
        - boot_simulation_95_EVI:       95th percentile for every prediction across all bootstrapped samples

Edits by: arietma
- Changed the script to predict for many combinations of PAR and EVI (instead of Tsfc)
- Adjusted the code to the features and model specs used in the current thesis
- Incorprated bootstrapped sampling in the simulation exercise. Now, simulated predictions
are made for 1,000 samples (so B=1,000 times) with sample size n=10,000. In every iteration,
the model is trained on the sampled data.
"""

#%% Import packages

import os
import pandas as pd
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample
import time


os.chdir("C:/Users/ariet/Documents/Climate Studies/WSG Thesis/Script/Edited_script_Laura/05_model_interpretation/simulations/")
from prepare_data_for_simulations_EVI import create_df_EVI

#%% Import data and define model specs
WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'
mer = pd.read_csv(f'{WD}merged_0228_final.csv', index_col=0)

# Add filter: exclude airborne observations with >15% built environment
Bld_filter = (mer['Bld'] > 0.15) & (mer['source']== 'airborne')
mer = mer[-Bld_filter]

# Features and hypp of the final merged model
mer_M5feats = ['PAR_abs', 'Tsfc', 'RH', 'EVI', 'SuC', 'Wat', 'Bld', 'Exp_PeatD']
hyperparams = {'learning_rate': 0.001, 'max_depth': 6, 'n_estimators': 4000, 'subsample': 0.55}

#%% Combis for which predictions are made

PAR_values = {'PAR0': 0,'PAR400' : 400, 'PAR800': 800, 'PAR1200' : 1200, 'PAR1600' : 1600}
EVI_values = {'EVI02': 0.2, 'EVI04': 0.4, 'EVI06': 0.6, 'EVI08': 0.8}

#%% create all possible combinations Tsfc and EVI

combis = []
for PAR in PAR_values.keys():
        for EVI in EVI_values.keys():
            combis.append(PAR+EVI)

#%% Simulation for every combination of PAR and EVI with bootstrapped samples
# (i.e. randomly sample from 'mer' with replacement)
# Takes ~4.5 hours

start_time = time.time()            
boot_overview_dfs_EVI = {}      # for storing predictions in dictionary
set_seeds = range(1,1001)       # iterate over these set seeds
B = len(set_seeds)              # no. bootstrap samples
n = 10000                       # sample size

for i in set_seeds:
    # Create bootstrapped sample from merged dataset
    boot = resample(mer, replace = True, n_samples = n, random_state = i)
    
    X = boot[mer_M5feats]
    y = boot['CO2flx']
    
    # Train model on all sampled data
    sc = StandardScaler()

    X_sc = pd.DataFrame(sc.fit_transform(X), columns=X.columns)

    xgbr = XGBRegressor(learning_rate = hyperparams['learning_rate'], 
                 max_depth = hyperparams['max_depth'], 
                 n_estimators = hyperparams['n_estimators'],
                 subsample = hyperparams['subsample'])

    xgbr.fit(X_sc, y) 
    
    # initialize dataframe
    overview_df_EVI = pd.DataFrame()

    # predict for every combination of PAR and EVI
    # it's possible that a combination is not present
    # therefore try ... except is used
    for PAR in PAR_values.keys():
            for EVI in EVI_values.keys():
                try:
                    
                    # dataframe is created 
                    mask, df = create_df_EVI(PAR_values[PAR], EVI_values[EVI], boot)
                    
                    # data is scaled and used to predict
                    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
                    CO2_pred = xgbr.predict(X_sc)
                    
                    # store predictions in dataframe with PAR and Tsfc values as column names
                    overview_df_EVI[PAR+'_'+EVI] = CO2_pred
                                
                except Exception:
                    pass
                
    # Store predictions in dictionary
    boot_overview_dfs_EVI[f'overview_df_EVI_{i}'] = overview_df_EVI


end_time = time.time()
elapsed_time = end_time - start_time


print(f"Elapsed time: {elapsed_time:.2f} seconds")
    
# Calculate average predictions for each predicted value in the df across all bootstrapped samples,
# and 5th and 95th percentile. These represent the 90% bootstrap intervals
concatenated_df_EVI = pd.concat(boot_overview_dfs_EVI.values(), axis=0)
boot_avg_sim_EVI = concatenated_df_EVI.groupby(concatenated_df_EVI.index).mean()
boot_5_sim_EVI = concatenated_df_EVI.groupby(concatenated_df_EVI.index).apply(lambda x: x.quantile(0.05))
boot_95_sim_EVI = concatenated_df_EVI.groupby(concatenated_df_EVI.index).apply(lambda x: x.quantile(0.95))

# Save bootstrapped average, 5th and 95th percentile
boot_avg_sim_EVI.to_csv(f"{WD}/simulations/df_0228_boot_simulation_EVI_average_B{B}.csv")
boot_5_sim_EVI.to_csv(f"{WD}/simulations/df_0228_boot_simulation_EVI_5_B{B}.csv")
boot_95_sim_EVI.to_csv(f"{WD}/simulations/df_0228_boot_simulation_EVI_95_B{B}.csv")


