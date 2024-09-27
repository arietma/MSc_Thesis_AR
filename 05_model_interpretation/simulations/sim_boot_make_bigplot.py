# -*- coding: utf-8 -*-
"""
@author: l_vdp
edited by: arietma, edited from: sim_make_bigplot.py

This script simulates CO2 fluxes using the final merged model and creates
a big figure showing the simulation results + bootstrap intervals and corresponding 
histograms.

This script defines combinations of PAR and Tsfc values. The function create_df
is used to create dataframes with corresponding PAR and Tsfc ranges, average RH, 
EVI, SuC, Wat and Bld values, and Exp_PeatD from 0 to 125. For every subplot of 
the final big plot, the dataframe with combination X is used as data for the 
model to predict for. The same combination X is used to create a histogram for 
in the subplot below.


Input: final merged dataset, create_df function from prepare_data_for_simulations.py
        and bootstrapped simulations (avg, 5th and 95th percentile)
Output: big plot with simulations and histograms, with 90% bootstrap intervals.
        The figure corresponds to Figure 9 in the thesis.

Edits by: arietma
- Added the 90% bootstrap intervals calculated in sim_bootstrap.py
- Adjusted the code to the features and model specs used in the current thesis
- Some figure specs
 
"""

#%% Import packages

import pandas as pd
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor
import matplotlib.pyplot as plt
import os
from matplotlib.lines import Line2D
import seaborn as sns

#%% Import own function

os.chdir("C:/Users/ariet/Documents/Climate Studies/WSG Thesis/Script/Edited_script_Laura/05_model_interpretation/simulations/")
from prepare_data_for_simulations import create_df

#%% Load data

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'
mer = pd.read_csv(f'{WD}merged_0228_final.csv', index_col=0)

# Add filter: exclude airborne observations with >15% built environment
Bld_filter = (mer['Bld'] > 0.15) & (mer['source']== 'airborne')
mer = mer[-Bld_filter]

# Load bootstrapped simulation results
boot_5_simulation = pd.read_csv(f'{WD}simulations/df_0228_boot_simulation_5_B1000.csv')
boot_95_simulation = pd.read_csv(f'{WD}simulations/df_0228_boot_simulation_95_B1000.csv')
boot_avg_simulation = pd.read_csv(f'{WD}simulations/df_0228_boot_simulation_average_B1000.csv')

#%% Define model specs 

mer_M5feats = ['PAR_abs', 'Tsfc', 'RH', 'EVI', 'SuC', 'Wat', 'Bld', 'Exp_PeatD']
hyperparams = {'learning_rate': 0.001, 'max_depth': 6, 'n_estimators': 4000, 'subsample': 0.55}

X = mer[mer_M5feats]
y = mer['CO2flx']

#%% train model (on ALL data, no need to split in test and train)

# scale and fit model
sc = StandardScaler()

X_sc = pd.DataFrame(sc.fit_transform(X), columns=X.columns)

xgbr = XGBRegressor(learning_rate = hyperparams['learning_rate'], 
             max_depth = hyperparams['max_depth'], 
             n_estimators = hyperparams['n_estimators'],
             subsample = hyperparams['subsample'])

xgbr.fit(X_sc, y) 

#%% prepare combinations of PAR/Tsfc-string with PAR/Tsfc-value in dictionary

PAR_values = {'PAR0': 0,'PAR400' : 400, 'PAR800': 800, 'PAR1200' : 1200, 'PAR1600' : 1600}
Tsfc_values = {'T0': 0, 'T5':5 , 'T10':10, 'T15': 15, 'T20':20, 'T25': 25, 'T30':30}

#%% create sets of combinations with selected values for PAR and Tsfc
# for these combinations, dataframes with features will be created using function create_df
# then, simulations and histograms will be made for every combination

#%%
combi_PAR0 = [[PAR_values['PAR0'], Tsfc_values['T0']], 
                 [PAR_values['PAR0'], Tsfc_values['T5']],
                 [PAR_values['PAR0'], Tsfc_values['T10']],
                 [PAR_values['PAR0'], Tsfc_values['T15']],
                 [PAR_values['PAR0'], Tsfc_values['T20']],
                 ]
#%%
combi_PAR400 = [[PAR_values['PAR400'], Tsfc_values['T5']],
                 [PAR_values['PAR400'], Tsfc_values['T10']],
                 [PAR_values['PAR400'], Tsfc_values['T15']],
                 [PAR_values['PAR400'], Tsfc_values['T20']],
                 [PAR_values['PAR400'], Tsfc_values['T25']]]
                 #[PAR_values['PAR400'], Tsfc_values['T30']]] #T30 is available but too little observations
#%%
combi_PAR800 = [[PAR_values['PAR800'], Tsfc_values['T10']],
                 [PAR_values['PAR800'], Tsfc_values['T15']],
                 [PAR_values['PAR800'], Tsfc_values['T20']],
                 [PAR_values['PAR800'], Tsfc_values['T25']],
                 [PAR_values['PAR800'], Tsfc_values['T30']]]
#%%
combi_PAR1200 = [[PAR_values['PAR1200'], Tsfc_values['T10']],
                 [PAR_values['PAR1200'], Tsfc_values['T15']],
                 [PAR_values['PAR1200'], Tsfc_values['T20']],
                 [PAR_values['PAR1200'], Tsfc_values['T25']],
                 [PAR_values['PAR1200'], Tsfc_values['T30']]]

#%%
combi_PAR800 = [[PAR_values['PAR800'], Tsfc_values['T10']],
                 [PAR_values['PAR800'], Tsfc_values['T15']],
                 [PAR_values['PAR800'], Tsfc_values['T20']],
                 [PAR_values['PAR800'], Tsfc_values['T25']],
                 [PAR_values['PAR800'], Tsfc_values['T30']]]
#%%

combi_PAR1600 = [[PAR_values['PAR1600'], Tsfc_values['T15']],
                 [PAR_values['PAR1600'], Tsfc_values['T20']],
                 [PAR_values['PAR1600'], Tsfc_values['T25']],
                 [PAR_values['PAR1600'], Tsfc_values['T30']]]
#%%
combi_T1520 = [[PAR_values['PAR1200'], Tsfc_values['T15']], 
                 [PAR_values['PAR1200'], Tsfc_values['T20']],
                 [PAR_values['PAR1600'], Tsfc_values['T15']],
                 [PAR_values['PAR1600'], Tsfc_values['T20']],
                 ]


#%% prepare colors

colors = sns.color_palette("Paired")
colors[6] = colors[9]
  
#%% Create big plot with histograms (Figure 9 in thesis)

# create grid for plots to be in
gridspec = dict(hspace=0.05, height_ratios=[4, 4, 0.4, 4,4],wspace=0.2)
fig, ((ax1, ax2,ax3), # simulation top row
      (ax1a, ax2a,ax3a), # histograms 
      (nv1, nv2, nv3), # not visible
      (ax4, ax5, ax6), # simulations
      (ax4a, ax5a, ax6a) ) = plt.subplots(5,3, # histograms
                                         sharex=True,
                                         figsize=(20,25),
                                         gridspec_kw=gridspec)

# every sub plot is structured the same way
# in the first subplot I show what has been done

data = mer

# select which combinations of PAR and Tsfc
combinations = combi_PAR0
store_EVI_0 = [] # To show that EVI has different values for each simulation 
# and thus has hidden influence in the simulation exercise

for i in range(len(combinations)): # looping over combinations

    # select PAR and Tsfc value
    PAR_value = combinations[i][0]; Tsfc_value = combinations[i][1]  
    
    # create dataframe using function        
    mask, df = create_df(PAR_value, Tsfc_value, data)
    store_EVI_0.append(df['EVI'][0])
    
    # scale data and predict
    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
    df['CO2_pred'] = xgbr.predict(X_sc)
    
    # ax 1: simulation plot for current combination
    ax1.scatter(df.index, df['CO2_pred'],s=3, 
                # coloris based on index of Tsfc value
                 color=colors[list(Tsfc_values.values()).index(Tsfc_value)])
    ax1.set_ylabel('Predicted CO2 flux')
    ax1.set_xlim(-5,125)
    ax1.set_ylabel('Predicted CO$_2$ flux [µmol m$^{-2}$ s$^{-1}$]')
    ax1.set_title('PAR_abs = 0')
    
    # Fill the 90% bootstrap interval    
    # select right column for boot_5_simulation and boot_95_simulation
    # These represent the 90% bootstrap intervals
    col = f'PAR{PAR_value}_T{Tsfc_value}'
    ax1.fill_between(boot_5_simulation.index, boot_5_simulation[col], 
                     boot_95_simulation[col], alpha = 0.15,color=colors[list(Tsfc_values.values()).index(Tsfc_value)])

    
    # ax 1a: histogram plot for current combination
    ax1a.hist(mask.Exp_PeatD, color=colors[list(Tsfc_values.values()).index(Tsfc_value)], 
              alpha=0.5)
    ax1a.set_ylabel('Count')
    ax1a.set_xlabel('Exp_PeatD [cm]')
    ax1a.tick_params(axis="x", which="both", length=6)
    ax1a.set_ylim(0,430)


    
combinations = combi_PAR400
store_EVI_400 = []
for i in range(len(combinations)):
    PAR_value = combinations[i][0]; Tsfc_value = combinations[i][1]        
    mask, df  = create_df(PAR_value, Tsfc_value, data)
    store_EVI_400.append(df['EVI'][0])
    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
    df['CO2_pred'] = xgbr.predict(X_sc)
    ax2.scatter(df.index,df['CO2_pred'], s=3,
                 color=colors[list(Tsfc_values.values()).index(Tsfc_value)])
    ax2.set_ylabel('Predicted CO$_2$ flux [µmol m$^{-2}$ s$^{-1}$]')
    ax2.set_title('PAR_abs = 400')
    
    # Fill the 90% bootstrap interval    
    # select right column for boot_5_simulation and boot_95_simulation
    # These represent the 90% bootstrap intervals
    col = f'PAR{PAR_value}_T{Tsfc_value}'
    ax2.fill_between(boot_5_simulation.index, boot_5_simulation[col], 
                     boot_95_simulation[col], alpha = 0.15,color=colors[list(Tsfc_values.values()).index(Tsfc_value)])

    
    
    
    ax2a.hist(mask.Exp_PeatD, color=colors[list(Tsfc_values.values()).index(Tsfc_value)], 
              alpha=0.5)
    ax2a.set_ylabel('Count')
    ax2a.set_xlabel('Exp_PeatD [cm]')
    ax2a.set_ylim(0,430)
 


combinations = combi_PAR800
store_EVI_800 = []
for i in range(len(combinations)):
    PAR_value = combinations[i][0]; Tsfc_value = combinations[i][1]        
    mask, df = create_df(PAR_value, Tsfc_value, data)
    store_EVI_800.append(df['EVI'][0])
    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
    df['CO2_pred'] = xgbr.predict(X_sc)
    ax3.scatter(df.index, df['CO2_pred'],s=3,
                 color=colors[list(Tsfc_values.values()).index(Tsfc_value)])
    ax3.set_ylabel('Predicted CO$_2$ flux [µmol m$^{-2}$ s$^{-1}$]')
    ax3a.set_xlabel('Exp_PeatD [cm]')
    ax3.set_ylim(-15.5,-6.5)
    ax3.set_title('PAR_abs = 800')

    col = f'PAR{PAR_value}_T{Tsfc_value}'
    ax3.fill_between(boot_5_simulation.index, boot_5_simulation[col], 
                boot_95_simulation[col], alpha = 0.15,color=colors[list(Tsfc_values.values()).index(Tsfc_value)])
    
    ax3a.hist(mask.Exp_PeatD, color=colors[list(Tsfc_values.values()).index(Tsfc_value)], 
               alpha=0.5)
    ax3a.set_ylabel('Count')
    ax3a.set_ylim(0,430)

# set center row to not visible
nv1.set_visible(False)
nv2.set_visible(False)    
nv3.set_visible(False)     
    
combinations = combi_PAR1200
store_EVI_1200 = []
for i in range(len(combinations)):
    PAR_value = combinations[i][0]; Tsfc_value = combinations[i][1]        
    mask, df = create_df(PAR_value, Tsfc_value, data)
    store_EVI_1200.append(df['EVI'][0])
    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
    df['CO2_pred'] = xgbr.predict(X_sc)
    ax4.scatter(df.index, df['CO2_pred'],s=3,
              color=colors[list(Tsfc_values.values()).index(Tsfc_value)])
    ax4a.set_xlabel('Exp_PeatD [cm]')
    ax4.set_ylabel('Predicted CO$_2$ flux [µmol m$^{-2}$ s$^{-1}$]')
    ax4.set_ylim(-21,-8)
    ax4.set_title('PAR_abs = 1200')


    col = f'PAR{PAR_value}_T{Tsfc_value}'
    ax4.fill_between(boot_5_simulation.index, boot_5_simulation[col], 
                    boot_95_simulation[col], alpha = 0.15,color=colors[list(Tsfc_values.values()).index(Tsfc_value)])
    
    ax4a.hist(mask.Exp_PeatD, color=colors[list(Tsfc_values.values()).index(Tsfc_value)], 
               alpha=0.5)
    ax4a.set_ylabel('Count')
    ax4a.set_ylim(0,430)



combinations = combi_PAR1600
store_EVI_1600 = []
for i in range(len(combinations)):
    PAR_value = combinations[i][0]; Tsfc_value = combinations[i][1]        
    mask, df = create_df(PAR_value, Tsfc_value, data)
    store_EVI_1600.append(df['EVI'][0])
    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
    df['CO2_pred'] = xgbr.predict(X_sc)
    ax5.scatter(df.index, df['CO2_pred'],s=3,
                 color=colors[list(Tsfc_values.values()).index(Tsfc_value)])
    ax5.set_title('PAR = 1600')
    ax5a.set_xlabel('Exp_PeatD [cm]')
    ax5.set_ylabel('Predicted CO$_2$ flux [µmol m$^{-2}$ s$^{-1}$]')
    ax5.set_title('PAR_abs = 1600')
    
    col = f'PAR{PAR_value}_T{Tsfc_value}'
    ax5.fill_between(boot_5_simulation.index, boot_5_simulation[col], 
                     boot_95_simulation[col], alpha = 0.15,color=colors[list(Tsfc_values.values()).index(Tsfc_value)])
    ax5.set_ylim(-21,-9.5)

    ax5a.hist(mask.Exp_PeatD, color=colors[list(Tsfc_values.values()).index(Tsfc_value)], 
                   alpha=0.5)
    ax5a.set_ylabel('Count')
    ax5a.set_ylim(0,430)

# Set last subplots to not visible
ax6.set_visible(False)
ax6a.set_visible(False)

# manually create legend elements
legend_elements_3a = [Line2D([0], [0], marker = 'o', label='Tsfc =  0', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T0')]),
                      Line2D([0], [0],  marker ='o',label='Tsfc = 5', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T5')]),
                      Line2D([0], [0], marker = 'o', label='Tsfc = 10', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T10')]),
                      Line2D([0], [0],  marker ='o',label='Tsfc = 15', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T15')]),
                      Line2D([0], [0], marker = 'o', label='Tsfc = 20', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T20')]),
                      Line2D([0], [0], marker = 'o', label='Tsfc = 25', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T25')]),
                      ]
                   
legend_elements_5a = [Line2D([0], [0], marker = 'o', label='Tsfc =  0', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T0')]),
                      Line2D([0], [0],  marker ='o',label='Tsfc = 5', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T5')]),
                      Line2D([0], [0], marker = 'o', label='Tsfc = 10', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T10')]),
                      Line2D([0], [0],  marker ='o',label='Tsfc = 15', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T15')]),
                      Line2D([0], [0], marker = 'o', label='Tsfc = 20', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T20')]),
                      Line2D([0], [0], marker = 'o', label='Tsfc = 25', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T25')]),
                      Line2D([0], [0], marker = 'o', label='Tsfc = 30', color='white', markersize=15, markerfacecolor = colors[list(Tsfc_values).index('T30')]),
                      ]
                   

# add legend in two places
ax5a.legend(handles=legend_elements_5a, loc='upper right')
ax3a.legend(handles=legend_elements_3a, loc='upper right')

#%% Save figure

fig.savefig(f'{WD}/figures/0228_sim_hist_all_titles_bootstrap_B1000.png', bbox_inches='tight', dpi=1000)