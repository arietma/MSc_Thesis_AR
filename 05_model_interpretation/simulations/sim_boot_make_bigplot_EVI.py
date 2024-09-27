# -*- coding: utf-8 -*-
"""
@author: l_vdp
edited by: arietma, edited from: sim_make_bigplot.py

This script simulates CO2 fluxes using the final merged model and creates
a big figure showing the simulation results + bootstrap intervals and corresponding 
histograms.

This script defines combinations of PAR and EVI values. The function create_df_EVI
is used to create ataframes with corresponding PAR and EVI ranges, average RH, 
Tsfc, SuC, Wat and Bld values, and Exp_PeatD from 0 to 125. For every subplot of 
the final big plot, the dataframe with combination X is used as data for the model 
to predict for. The same combination X is used to create a histogram for in the 
subplot below.


Input: final merged dataset, and create_df_EVI function from prepare_data_for_simulations_EVI.py
         and bootstrapped simulations (avg, 5th and 95th percentile)
Output: big plot with simulations and histograms, with 90% bootstrap intervals.
        The figure corresponds to Figure E1 in the thesis.

Edits by: arietma
- Added the 90% bootstrap intervals calculated in sim_bootstrap_EVI.py
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
from prepare_data_for_simulations_EVI import create_df_EVI

#%% Load data

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'
mer = pd.read_csv(f'{WD}merged_0228_final.csv', index_col=0)

# Add filter: exclude airborne observations with >15% built environment
Bld_filter = (mer['Bld'] > 0.15) & (mer['source']== 'airborne')
mer = mer[-Bld_filter]

# Load bootstrapped simulation results
boot_5_sim_EVI = pd.read_csv(f'{WD}simulations/df_0228_boot_simulation_EVI_5_B1000.csv')
boot_95_sim_EVI = pd.read_csv(f'{WD}simulations/df_0228_boot_simulation_EVI_95_B1000.csv')
boot_avg_sim_EVI = pd.read_csv(f'{WD}simulations/df_0228_boot_simulation_EVI_average_B1000.csv')

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

#%% prepare combinations of PAR/EVI-string with PAR/EVI-value in dictionary

PAR_values = {'PAR0': 0,'PAR400' : 400, 'PAR800': 800, 'PAR1200' : 1200, 'PAR1600' : 1600}
EVI_values = {'EVI02': 0.2, 'EVI04': 0.4, 'EVI06': 0.6, 'EVI08': 0.8}

#%% create sets of combinations with selected values for PAR and EVI
# for these combinations, dataframes with features will be created using function create_df_EVI
# then, simulations and histograms will be made for every combination

#%%
combi_PAR0 = [[PAR_values['PAR0'], EVI_values['EVI02']], 
                 [PAR_values['PAR0'], EVI_values['EVI04']],
                 [PAR_values['PAR0'], EVI_values['EVI06']],
                 [PAR_values['PAR0'], EVI_values['EVI08']],
                 ]
#%%
combi_PAR400 = [[PAR_values['PAR400'], EVI_values['EVI02']],
                 [PAR_values['PAR400'], EVI_values['EVI04']],
                 [PAR_values['PAR400'], EVI_values['EVI06']],
                 [PAR_values['PAR400'], EVI_values['EVI08']],
                 ]
#%%
combi_PAR800 = [[PAR_values['PAR800'], EVI_values['EVI02']],
                [PAR_values['PAR800'], EVI_values['EVI04']],
                [PAR_values['PAR800'], EVI_values['EVI06']],
                [PAR_values['PAR800'], EVI_values['EVI08']],
                 ]
#%%
combi_PAR1200 = [[PAR_values['PAR1200'], EVI_values['EVI02']],
                 [PAR_values['PAR1200'], EVI_values['EVI04']],
                 [PAR_values['PAR1200'], EVI_values['EVI06']],
                 [PAR_values['PAR1200'], EVI_values['EVI08']],
                 ]

#%%
combi_PAR800 = [[PAR_values['PAR1200'], EVI_values['EVI02']],
                [PAR_values['PAR1200'], EVI_values['EVI04']],
                [PAR_values['PAR800'], EVI_values['EVI06']],
                [PAR_values['PAR800'], EVI_values['EVI08']],
                 ]
#%%

combi_PAR1600 = [[PAR_values['PAR1600'], EVI_values['EVI02']],
                 [PAR_values['PAR1600'], EVI_values['EVI04']],
                 [PAR_values['PAR1600'], EVI_values['EVI06']],
                 [PAR_values['PAR1600'], EVI_values['EVI08']],
                 ]
#%%
combi_EVI0608 = [[PAR_values['PAR1200'], EVI_values['EVI06']], 
                 [PAR_values['PAR1200'], EVI_values['EVI08']],
                 [PAR_values['PAR1600'], EVI_values['EVI06']],
                 [PAR_values['PAR1600'], EVI_values['EVI08']],
                 ]


#%% prepare colors

palette = sns.color_palette("Paired")
colors = [palette[11], palette[6], palette[2], palette[3]]
#%% create big plot with histograms (Figure E1 in thesis)

# create grid for plots to be in
gridspec = dict(hspace=0.05, height_ratios=[4, 4, 0.4, 4,4],wspace=0.2)
fig, ((ax1, ax2,ax3), # simulation top row
      (ax1a, ax2a,ax3a), # histograms 
      (nv1, nv2, nv3), # not visible
      (ax4, ax5,ax6), # simulations
      (ax4a, ax5a,ax6a) ) = plt.subplots(5,3, # histograms
                                         sharex=True,
                                         figsize=(20,25),
                                         gridspec_kw=gridspec)

# every sub plot is structured the same way
# in the first subplot I show what has been done

data = mer

# select which combinations of PAR and Tsfc
combinations = combi_PAR0

for i in range(len(combinations)): # looping over combinations

    # select PAR and Tsfc value
    PAR_value = combinations[i][0]; EVI_value = combinations[i][1]  
    
    # create dataframe using function        
    mask, df = create_df_EVI(PAR_value, EVI_value, data)
    
    # scale data and predict
    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
    df['CO2_pred'] = xgbr.predict(X_sc)
    
    # ax 1: simulation plot for current combination
    ax1.scatter(df.index, df['CO2_pred'],s=3, 
                # coloris based on index of EVI value
                 color=colors[list(EVI_values.values()).index(EVI_value)])
    ax1.set_ylabel('Predicted CO2 flux')
    ax1.set_xlim(-5,125)
    ax1.set_ylabel('Predicted CO$_2$ flux [µmol m$^{-2}$ s$^{-1}$]')
    ax1.set_title('PAR_abs = 0')
    
    # Add bootstrap intervals
    # Adjust selecting the right column so that EVI_value is 02, not 0.2 (and so on)
    col = f'PAR{PAR_value}_EVI{EVI_value:.1f}'.replace('.','') # select column corresponding to the current combination of PAR and EVI
    
    ax1.fill_between(boot_5_sim_EVI.index, boot_5_sim_EVI[col], 
                     boot_95_sim_EVI[col], alpha = 0.15,color=colors[list(EVI_values.values()).index(EVI_value)])
    
    
    # ax 1a: histogram plot for current combination
    ax1a.hist(mask.Exp_PeatD, color=colors[list(EVI_values.values()).index(EVI_value)], 
              alpha=0.5)
    ax1a.set_ylabel('Count')
    ax1a.set_xlabel('Exp_PeatD [cm]')
    ax1a.set_ylim(0,850)
    ax1a.tick_params(axis="x", which="both", length=6)
    
combinations = combi_PAR400
for i in range(len(combinations)):
    PAR_value = combinations[i][0]; EVI_value = combinations[i][1]        
    mask, df  = create_df_EVI(PAR_value, EVI_value, data)
    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
    df['CO2_pred'] = xgbr.predict(X_sc)
    ax2.scatter(df.index,df['CO2_pred'], s=3,
                 color=colors[list(EVI_values.values()).index(EVI_value)])
    ax2.set_ylabel('Predicted CO$_2$ flux [µmol m$^{-2}$ s$^{-1}$]')
    ax2.set_title('PAR_abs = 400')

    
    col = f'PAR{PAR_value}_EVI{EVI_value:.1f}'.replace('.','')
    ax2.fill_between(boot_5_sim_EVI.index, boot_5_sim_EVI[col], 
                     boot_95_sim_EVI[col], alpha = 0.15,color=colors[list(EVI_values.values()).index(EVI_value)])
    
    ax2a.hist(mask.Exp_PeatD, color=colors[list(EVI_values.values()).index(EVI_value)], 
              alpha=0.5)
    ax2a.set_ylabel('Count')
    ax2a.set_xlabel('Exp_PeatD [cm]')
    ax2a.set_ylim(0,850)
    

 # manually create legend
legend_PAR = [
            Line2D([0], [0], marker ='.', label='PAR_abs = 1200', color='white', markersize=10, markerfacecolor = 'black'),#colors[list(PAR_values).index('PAR1200')]),
            Line2D([0], [0], marker ='^',label='PAR_abs = 1600', color='white', markersize=10, markerfacecolor = 'black')
            ]
      

# set center row to not visible
nv1.set_visible(False)
nv2.set_visible(False)    
nv3.set_visible(False)    

    
combinations = combi_PAR800
for i in range(len(combinations)):
    PAR_value = combinations[i][0]; EVI_value = combinations[i][1]        
    mask, df = create_df_EVI(PAR_value, EVI_value, data)
    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
    df['CO2_pred'] = xgbr.predict(X_sc)
    ax3.scatter(df.index, df['CO2_pred'],s=3,
                 color=colors[list(EVI_values.values()).index(EVI_value)])
    ax3.set_ylabel('Predicted CO$_2$ flux [µmol m$^{-2}$ s$^{-1}$]')
    ax3a.set_xlabel('Exp_PeatD [cm]')
    ax3.set_ylim(-22,-7)
    ax3.set_title('PAR_abs = 800')

    col = f'PAR{PAR_value}_EVI{EVI_value:.1f}'.replace('.','')
    ax3.fill_between(boot_5_sim_EVI.index, boot_5_sim_EVI[col], 
                     boot_95_sim_EVI[col], alpha = 0.15,color=colors[list(EVI_values.values()).index(EVI_value)])

    ax3a.hist(mask.Exp_PeatD, color=colors[list(EVI_values.values()).index(EVI_value)], 
               alpha=0.5)
    ax3a.set_ylabel('Count')
    ax3a.set_ylim(0,850)

    
    
combinations = combi_PAR1200
for i in range(len(combinations)):
    PAR_value = combinations[i][0]; EVI_value = combinations[i][1]        
    mask, df = create_df_EVI(PAR_value, EVI_value, data)
    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
    df['CO2_pred'] = xgbr.predict(X_sc)
    ax4.scatter(df.index, df['CO2_pred'],s=3,
              color=colors[list(EVI_values.values()).index(EVI_value)])
    ax4a.set_xlabel('Exp_PeatD [cm]')
    ax4.set_ylabel('Predicted CO$_2$ flux [µmol m$^{-2}$ s$^{-1}$]')
    ax4.set_ylim(-22,-7)
    ax4.set_title('PAR_abs = 1200')
    
    col = f'PAR{PAR_value}_EVI{EVI_value:.1f}'.replace('.','')
    ax4.fill_between(boot_5_sim_EVI.index, boot_5_sim_EVI[col], 
                     boot_95_sim_EVI[col], alpha = 0.15,color=colors[list(EVI_values.values()).index(EVI_value)])

    ax4a.hist(mask.Exp_PeatD, color=colors[list(EVI_values.values()).index(EVI_value)], 
               alpha=0.5)
    ax4a.set_ylabel('Count')
    ax4a.set_ylim(0,850)



combinations = combi_PAR1600
for i in range(len(combinations)):
    PAR_value = combinations[i][0]; EVI_value = combinations[i][1]        
    mask, df = create_df_EVI(PAR_value, EVI_value, data)
    X_sc = pd.DataFrame(sc.transform(df[mer_M5feats]),columns=mer_M5feats)
    df['CO2_pred'] = xgbr.predict(X_sc)
    ax5.scatter(df.index, df['CO2_pred'],s=3,
                 color=colors[list(EVI_values.values()).index(EVI_value)])
    ax5.set_title('PAR_abs = 1600')
    ax5a.set_xlabel('Exp_PeatD [cm]')
    ax5.set_ylabel('Predicted CO$_2$ flux [µmol m$^{-2}$ s$^{-1}$]')
    ax5.set_ylim(-22,-7)
    
    col = f'PAR{PAR_value}_EVI{EVI_value:.1f}'.replace('.','')
    ax5.fill_between(boot_5_sim_EVI.index, boot_5_sim_EVI[col], 
                     boot_95_sim_EVI[col], alpha = 0.15,color=colors[list(EVI_values.values()).index(EVI_value)])

    ax5a.hist(mask.Exp_PeatD, color=colors[list(EVI_values.values()).index(EVI_value)], 
                   alpha=0.5)
    ax5a.set_ylabel('Count')
    ax5a.set_ylim(0,850)

# Set last subplots to not visible
ax6.set_visible(False)
ax6a.set_visible(False)

# manually create legend elements
legend_elements = [Line2D([0], [0], marker = 'o', label='EVI =  0.2', color='white', markersize=15, markerfacecolor = colors[list(EVI_values).index('EVI02')]),
                  Line2D([0], [0],  marker ='o',label='EVI = 0.4', color='white', markersize=15, markerfacecolor = colors[list(EVI_values).index('EVI04')]),
                   Line2D([0], [0], marker = 'o', label='EVI = 0.6', color='white', markersize=15, markerfacecolor = colors[list(EVI_values).index('EVI06')]),
                   Line2D([0], [0],  marker ='o',label='EVI = 0.8', color='white', markersize=15, markerfacecolor = colors[list(EVI_values).index('EVI08')]),
                  ]
                   

# add legend in two places
ax5a.legend(handles=legend_elements, loc='upper right')
ax3a.legend(handles=legend_elements, loc='upper right')

#%% Save figure

fig.savefig(f'{WD}/figures/0228_sim_hist_all_titles_bootstrap_EVI_B1000.png', bbox_inches='tight', dpi=1000)