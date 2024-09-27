"""
@author: l_vdp
edited by: arietma, edited from: prepare_data_for_simulations.py

This script provides two functions: get_cond and create_df_EVI.

get_cond gets the correct format for a 'condition', which can be used as a mask in selecting
rows from a dataframe and is based on a PAR and EVI value. For PAR, the condition is
+/- 200, for EVI, the condition is +/- 0.1.

create_df_EVI uses get_cond to create a sub-dataframe from the merged dataset, based 
on the condition provided by get_cond. This dataframe has constant values for
all other features included in the merged model, based on the masked dataframe.

The function create_df_EVI is imported in sim_bootstrap_EVI.py and sim_boot_make_bigplot_EVI.py


Edits by arietma:
    - Changed function create_df in prepare_data_for_simulations.py to create_df_EVI
    to omit Tsfc and simulate for EVI instead
    - Adjusted the code to the features used in the current thesis

"""
#%% import

import pandas as pd

#%% get conditions to create sub-dataframe
# PAR +/- 200 and EVI +/- 0.1

def get_cond(feat, value, data):
    """
    feat: feature 'PAR_abs' or 'EVI'
    value: value of feature around which range should be computed
    data: dataframe from which rows should be selected, e.g. merged dataset
    """
    value = float(value)
    
    # for PAR: range of +/- 200
    if feat == 'PAR_abs':
        upper = value + 200
        lower = value - 200
    
    # for EVI: range of +/- 0.1
    elif feat == 'EVI':
        upper = value + 0.1
        lower = value - 0.1
        
    cond = (data[feat] > lower) & (data[feat] < upper)
    
    if value == 0: 
        cond = (data[feat] < 2)
    return cond 
        

#%% function to create dataframe, based on condition 

def create_df_EVI(PAR_value, EVI_value, data):
    """
    PAR_value: value for PAR around which range should be computed
    EVI_value: value of EVI around which range should be computed
    data: dataframe from which rows should be selected, e.g. merged dataset
    """
    mask = data[get_cond('PAR_abs', PAR_value, data) & get_cond('EVI', EVI_value, data)] 
    
    # check if there exists data for the combination of PAR and EVI
    if len(mask) != 0:
        
        # create dataframe
        df = pd.DataFrame(index=range(125))    
        
        df['PAR_abs'] = PAR_value #  constant selected PAR value
        df['EVI'] = EVI_value # constant selected EVI value
        
        df['RH'] = mask['RH'].mean() # constant mean RH value, based on masked dataframe
        df['Tsfc'] = mask['Tsfc'].mean() # constant selected Tsfc value
        df['SuC'] = mask['SuC'].mean() # same as with RH
        df['Wat'] = mask['Wat'].mean() # same as with RH
        df['Bld'] = mask['Bld'].mean() # same as with RH
        df['Exp_PeatD'] = range(125) # artifical Exp_PeatD values
        df['Exp_PeatD_og'] = mask['Exp_PeatD'].sample(n=125, ignore_index=True, replace=True) # keep real Exp_PeatD values
    
    else:
        print('There is no data with PAR=', PAR_value, 'and EVI=', EVI_value)
        df = pd.DataFrame()
    
    return mask, df
    
  



    
    


                         