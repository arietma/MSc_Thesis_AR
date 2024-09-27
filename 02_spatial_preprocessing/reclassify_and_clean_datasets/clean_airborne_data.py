# -*- coding: utf-8 -*-
"""
@author: l_vdp
Edited by: arietma

Script to clean the airborne data:
- calculate VPD and PAR_abs
- apply quality flags to data
- only keep rows where 0<NDVI<1
- only keep rows where 0<EVI<1
- omit (few) NaN's of OWASIS variables
- throw out highest 1% and lowest 1% of CO2flx
- only keep relevant columns

Edited by arietma:
    - Calculate OWD from GWS and AHN
    - Calculate Air Exposed Peat Depth from OWD and Peat Depth
    - Omitted shuffling of data, as this is later not useful for train-test 
    data divison
"""

#%% Import packages

import pandas as pd
import numpy as np
import math

#%% Set working directory and load airborne data (already overlaid with reclassified spatial info)

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/' 
data = pd.read_csv(f"{WD}air_1216_reclassified.csv", index_col=0, na_values='nan')

#%% Calculate E_sat, VPD and PAR_abs

# Calculate E_sat, i.e. saturation vapor pressure
# Mangus's equation is used, recommended by the WMO (2021)
# https://library.wmo.int/doc_num.php?explnum_id=11386 , ISBN 978-92-63-10008-5

E_sat_hPa = data['Tair'].apply(lambda x: 6.112 * math.exp(17.62 * (x-273.15) / (243.12 + (x-273.15))))
E_sat_kPa = E_sat_hPa / 10

# Calculate VPD from E_sat and E_act
data['VPD'] = E_sat_kPa - data['E_act'] # in kPa


# Calculate absorbed PAR

# Be sure to reset the index before indexing with .loc
# Indexing with .loc because 
# data['PAR_abs'] = data['PAR_i'] - data['PAR_r']
# Gives the warning: a value is trying to be set on a copy  of a slice from a df

data = data.reset_index()
data.loc[:, 'PAR_abs'] = data['PAR_i'] - data['PAR_r']

#%% Calculate OWD from GWS and AHN

data['OWD'] = data['ahn'] - data['GWS']*100 # ahn in cm, GWS in m
# Correction
data = data[data['OWD'] >= 0] 

#%% Calculate Air Exposed Peat Depth
# If peat depth < OWD, air exposed peat = peat depth
# If peat depth >= OWD, air exposed peat = OWD

data['Exp_PeatD'] = np.where(data['PeatD'] < data['OWD'], data['PeatD'], data['OWD'])

#%% Change unit Tsfc from K to degrees C

data['Tsfc'] = data['Tsfc']-273.15

#%% Quality flags

# Quality flags for CO2 and Ustar, filter umean<20
data = data[(data['QC_CO2flx'] <= 6) & (data['QC_Ustar'] <= 6) &
            (data['umean'] < 20) ]
    
#%% Throw out highest 1% and lowest 1% of CO2flx

# lowest 1%: -29.93, highest 1%: 5.4
data = data[(data['CO2flx'] > data.CO2flx.quantile(0.01)) & (data['CO2flx'] < data.CO2flx.quantile(0.99))]

#%% Correct NDVI/EVI values

# set all values NDVI lower than 0 to 0
data['NDVI'] = data['NDVI'].where(data['NDVI']>=0, other=0)

# And for EVI values
data['EVI'] = data['EVI'].where(data['EVI']>=0, other=0)

#%% Omit NaNs of OWASIS variables

# Note to next user: these NaNs occur in large water bodies, as OWASIS does not
# model groundwater values in these areas. Needs to be checked in QGIS to ensure
# NaNs are not caused by something else, but if the NaNs only occur in large
# lakes, set NAs to 0. This way the CO2 fluxes from large lakes can also be
# modelled.

data.dropna(subset=['BBB'], inplace=True) 

#%% Assign new columns that exist in tower data

# Site names for tower are the tower site names, for airbrone just air
data['site'] = 'air' 

#%% Drop unneccessary columns

colstodrop = ['level_0','Label', 'zm','wind_dir', 'umean', 'sigmav', 'P',  'ol',
              'QC_CH4flx', 'QC_filt', 'QC_CO2flx', 'h', 'QC_H', 'QC_LE', 'QC_Ustar',
              'ahn25_1','Droogtelegging_0', 'Droogtelegging_1', 'Droogtelegging_2',
              'Droogtelegging_3', 'Droogtelegging_4', 'Droogtelegging_5', 'E_act', 
              'sumSOIL', 'Height', 'WinLen', 'WinLenGPS', 'WinTime','StepLen',
              'CO2', 'ustar','H', 'LE', 'Net','PAR_i','PAR_r','old_rownames']



data_cleaned = data.drop(colstodrop, axis='columns')

# Rename row numbers that are connected to the footprint files
data_cleaned.rename(columns={'Unnamed: 0':'old_rownames'}, inplace=True) 


#%% Reset index before saving

data_cleaned = data_cleaned.reset_index()

# Only keep recent index
data_cleaned = data_cleaned.drop(['X'], axis = 'columns') 

#%% Save cleaned airborne dataset

data_cleaned.to_csv(f"{WD}air_1216_final.csv")