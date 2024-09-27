# -*- coding: utf-8 -*-
"""
@author: l_vdp
edited by: arietma, edited from: sim_create_overview_df.py

This script creates a dataframe with CO2 simulations for many combinations of PAR and Tsfc.
Also, bootstrapped sampling is performed to later show the bootstrap intervals 
in sim_boot_make_bigplot.py. The script takes ~4.5 hours to run.

Input: final merged dataset, and create_df function from prepare_data_for_simulations.py.
Output: 3 dataframes with CO2 predictions for every present combination of PAR and Tsfc
        - boot_simulation_average:  average for every prediction across all bootstrapped samples
        - boot_simulation_5:        5th percentile for every prediction across all bootstrapped samples
        - boot_simulation_95:       95th percentile for every prediction across all bootstrapped samples
        
Edits by: arietma:
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
from prepare_data_for_simulations import create_df

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
Tsfc_values = {'T0': 0, 'T5':5 , 'T10':10, 'T15': 15, 'T20':20, 'T25': 25, 'T30':30}

# create all possible combinations Tsfc and PAR
combis = []
for PAR in PAR_values.keys():
    for Tsfc in Tsfc_values.keys():
        combis.append(PAR+Tsfc)
        
#%% Simulation for every combination of PAR and Tsfc with bootstrapped samples
# (i.e. randomly sample from 'mer' with replacement)
# Takes ~4.5 hours

start_time = time.time()
boot_overview_dfs = {}          # for storing predictions in dictionary
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
    overview_df = pd.DataFrame()

    # predict for every combination of PAR and Tsfc
    # it's possible that a combination is not present, such as PAR=0 and Tsfc=25.
    # therefore try ... except is used

    # iterate over every PAR and Tsfc value
    for PAR in PAR_values.keys():
        for Tsfc in Tsfc_values.keys():
            try:
                
                # dataframe is created from the bootstrapped sample
                mask, df = create_df(PAR_values[PAR], Tsfc_values[Tsfc], boot)
                
                # data is scaled and used to predict
                X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
                CO2_pred = xgbr.predict(X_sc)
                
                # store predictions in dataframe with PAR and Tsfc values as column names
                overview_df[PAR+'_'+Tsfc] = CO2_pred                
                
            except Exception:
                pass
    
    # Store predictions in dictionary
    boot_overview_dfs[f'overview_df_{i}'] = overview_df


end_time = time.time()
elapsed_time = end_time - start_time


print(f"Elapsed time: {elapsed_time:.2f} seconds")
    
# Calculate average predictions for each predicted value in the df across all bootstrapped samples,
# and 5th and 95th percentile. These represent the 90% bootstrap intervals
concatenated_df = pd.concat(boot_overview_dfs.values(), axis=0)
boot_avg_simulation = concatenated_df.groupby(concatenated_df.index).mean()
boot_5_simulation = concatenated_df.groupby(concatenated_df.index).apply(lambda x: x.quantile(0.05))
boot_95_simulation = concatenated_df.groupby(concatenated_df.index).apply(lambda x: x.quantile(0.95))

# Save bootstrapped average, 5th and 95th percentile
boot_avg_simulation.to_csv(f"{WD}/simulations/df_0228_boot_simulation_average_B{B}.csv")
boot_5_simulation.to_csv(f"{WD}/simulations/df_0228_boot_simulation_5_B{B}.csv")
boot_95_simulation.to_csv(f"{WD}/simulations/df_0228_boot_simulation_95_B{B}.csv")


