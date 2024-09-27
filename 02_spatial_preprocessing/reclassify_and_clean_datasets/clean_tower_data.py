# -*- coding: utf-8 -*-
"""
@author: l_vdp
Edited by: arietma

Script to clean the tower data:

- calculate PAR_abs
- only keep rows where 0<NDVI<1
- only keep rows where 0<EVI<1
- omit rows without PAR value
- throw out highest and lowest 1% of CO2flx
- only keep relevant columns
- rename columns to match airborne data


Edits by arietma:
    - Calculate OWD from GWS and AHN
    - Calculate Air Exposed Peat Depth from OWD and Peat Depth
    - Omit rows with unrepresentative OWASIS values (highest drainage of entire
                                                     dataset, in January)
    - Manually reversed some PAR_i and PAR_r values as these were inadvertently
    reversed during an earlier preprocessing stage
    - Omitted shuffling of data, as this is later not useful for train-test 
    data divison
"""
#%% Import packages

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#%% Set working directory and load airborne data (already overlaid with reclassified spatial info)

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/' 
twr = pd.read_csv(f"{WD}tower_1129_reclassified.csv", index_col=0) 

#%% Calculate OWD from GWS and AHN

twr['OWD'] = twr['ahn'] - twr['GWS']*100 # ahn in cm, GWS in m
# Correction
twr = twr[twr['OWD'] >= 0]

#%% Calculate Air Exposed Peat Depth
# If peat depth < OWD, air exposed peat = peat depth
# If peat depth >= OWD, air exposed peat = OWD

twr['Exp_PeatD'] = np.where(twr['PeatD'] < twr['OWD'], twr['PeatD'], twr['OWD'])

#%% Omit OWASIS values with unrepresentative modeled GWS
# For ALB_MS and ALB_RF, 01-01-2023 up until 13-01-2023. These values show very
# low groundwater tables, i.e. very high drainage (highest of the entire dataset), 
# while in this time of the year high groundwater tables are expected

twr['datetime'] = pd.to_datetime(twr['datetime'], format = "%d-%m-%Y %H:%M")

start_date = pd.to_datetime('2023-01-01')
end_date = pd.to_datetime('2023-01-14')

con = (
       ((twr['site']=='ALB_MS') | (twr['site']=='ALB_RF')) 
       & (twr['datetime'] < end_date) 
       & (twr['datetime'] >= start_date)
       )

twr = twr[-con]

#%% Correct NDVI and EVI values

# only keep observations with NDVI <=1
twr = twr[twr['NDVI'] <= 1] # no observations are deleted

# only keep observations with EVI <= 1
twr = twr[twr['EVI'] <= 1] # no observations are deleted

#%% Throw out highest 1% and lowest 1% of CO2flx

# lowest 1%: -26.7, highest 1%: 16.8
twr = twr[(twr['NEE_CO2'] > twr.NEECO2.quantile(0.01)) & (twr['NEE_CO2'] < twr.NEECO2.quantile(0.99))]

#%% Calculate PAR_abs
# In some instances, PAR and RPAR values were accidentally reversed in preprocessing
# For these time periods, the calculation of PAR_abs is adjusted so that PAR_abs 
# is a positive number
# This is done for 6 specific time periods and sites

# Create temporary (_temp) PAR_abs column
twr.loc[:, 'PAR_abs_temp'] = twr['PAR'] - twr['RPAR']

# Assign values of PAR_abs_temp to PAR_abs. The manually corrected values are
# added to PAR_abs, the original values of PAR_abs remain in PAR_abs_temp
twr['PAR_abs'] = twr['PAR_abs_temp']
twr['datetime'] = pd.to_datetime(twr['datetime'], format = "%d-%m-%Y %H:%M") # set to datetime for plotting

# 1. HOC 2021-10 and 11
site = 'HOC'
year = 2021
month = [10,11]

subset = twr[ (twr['site'] == site) & ((twr['datetime'].dt.year == year) & 
                 (twr['datetime'].dt.month.isin(month)))]

# Plotting to check if RPAR is >> PAR
# plt.figure(figsize=(10, 6))
# plt.plot(subset['datetime'], subset['PAR'],label = 'PAR')
# plt.plot(subset['datetime'], subset['RPAR'], label = 'RPAR')
# plt.legend()
# plt.title(f'PAR vs. RPAR site {site}')

# Create a boolean series for the rows for which PAR and RPAR should be reversed
rws_to_change = (twr['site'] == site) & (twr['datetime'].dt.year == year) & (twr['datetime'].dt.month.isin(month))

# Adjust calculation of PAR_abs for these rws in twr
twr.loc[rws_to_change, 'PAR_abs'] = np.where(
    twr.loc[rws_to_change, 'RPAR'] > twr.loc[rws_to_change, 'PAR'], # where RPAR>PAR (in reality, PAR is > RPAR)
    twr.loc[rws_to_change, 'RPAR'] - twr.loc[rws_to_change, 'PAR'], # perform RPAR-PAR instead of
    twr.loc[rws_to_change, 'PAR'] - twr.loc[rws_to_change, 'RPAR'] # the other way around
)


# Plotting to see if PAR_abs is adjusted correctly
# subset = twr[ (twr['site'] == site) & (twr['datetime'].dt.year == year) & 
#                   (twr['datetime'].dt.month.isin(month)) ]
# plt.figure(figsize=(10, 6))
# plt.plot(subset['datetime'], subset['PAR_abs_temp'],label = 'PAR_abs_temp')
# plt.plot(subset['datetime'], subset['PAR_abs'], label = 'PAR_abs')
# plt.title(f'PAR_abs_temp and fixed PAR_abs for site {site}')
# plt.legend()

# 2. LDC 2021-10 and 2021-11-02 and 01
site = 'LDC'
year = 2021
month = [10]
month2 = 11
day2=[1,2]

subset = twr[(twr['site'] == site) & ((twr['datetime'].dt.year == year) & 
                 (twr['datetime'].dt.month.isin(month)) |
                 (twr['datetime'].dt.year == year) & 
                 (twr['datetime'].dt.month == month2) &
                 (twr['datetime'].dt.day.isin(day2)))]

rws_to_change = (twr['site'] == site) & ((twr['datetime'].dt.year == year) & 
                (twr['datetime'].dt.month.isin(month)) | 
                (twr['datetime'].dt.year == year) & 
                (twr['datetime'].dt.month == month2) & 
                (twr['datetime'].dt.day.isin(day2)))

twr.loc[rws_to_change, 'PAR_abs'] = np.where(
    twr.loc[rws_to_change, 'RPAR'] > twr.loc[rws_to_change, 'PAR'], # where RPAR>PAR (in reality, PAR is > RPAR)
    twr.loc[rws_to_change, 'RPAR'] - twr.loc[rws_to_change, 'PAR'], # perform RPAR-PAR instead of
    twr.loc[rws_to_change, 'PAR'] - twr.loc[rws_to_change, 'RPAR'] # the other way around
)

# 3. LDC 2022-11 
site = 'LDC'
year = 2022
month = [11]

subset = twr[ (twr['site'] == site) & ((twr['datetime'].dt.year == year) & 
                 (twr['datetime'].dt.month.isin(month)))]

rws_to_change = (twr['site'] == site) & (twr['datetime'].dt.year == year) & (twr['datetime'].dt.month.isin(month))

twr.loc[rws_to_change, 'PAR_abs'] = np.where(
    twr.loc[rws_to_change, 'RPAR'] > twr.loc[rws_to_change, 'PAR'], # where RPAR>PAR (in reality, PAR is > RPAR)
    twr.loc[rws_to_change, 'RPAR'] - twr.loc[rws_to_change, 'PAR'], # perform RPAR-PAR instead of
    twr.loc[rws_to_change, 'PAR'] - twr.loc[rws_to_change, 'RPAR'] # the other way around
)

#4. HOH 2021-11
site = 'HOH'
year = 2021
month = [11]

subset = twr[ (twr['site'] == site) & ((twr['datetime'].dt.year == year) & 
                 (twr['datetime'].dt.month.isin(month)))]

rws_to_change = (twr['site'] == site) & (twr['datetime'].dt.year == year) & (twr['datetime'].dt.month.isin(month))

twr.loc[rws_to_change, 'PAR_abs'] = np.where(
    twr.loc[rws_to_change, 'RPAR'] > twr.loc[rws_to_change, 'PAR'], # where RPAR>PAR (in reality, PAR is > RPAR)
    twr.loc[rws_to_change, 'RPAR'] - twr.loc[rws_to_change, 'PAR'], # perform RPAR-PAR instead of
    twr.loc[rws_to_change, 'PAR'] - twr.loc[rws_to_change, 'RPAR'] # the other way around
)

# 5. HOH 2022-11 and 2022-12 
site = 'HOH'
year = 2022
month = [11,12]

subset = twr[ (twr['site'] == site) & ((twr['datetime'].dt.year == year) & 
                 (twr['datetime'].dt.month.isin(month)))]

rws_to_change = (twr['site'] == site) & (twr['datetime'].dt.year == year) & (twr['datetime'].dt.month.isin(month))

twr.loc[rws_to_change, 'PAR_abs'] = np.where(
    twr.loc[rws_to_change, 'RPAR'] > twr.loc[rws_to_change, 'PAR'], # where RPAR>PAR (in reality, PAR is > RPAR)
    twr.loc[rws_to_change, 'RPAR'] - twr.loc[rws_to_change, 'PAR'], # perform RPAR-PAR instead of
    twr.loc[rws_to_change, 'PAR'] - twr.loc[rws_to_change, 'RPAR'] # the other way around
)

#6. AMM 2022-11 
site = 'AMM'
year = 2022
month = [11]
day = [22,23,24,25,26] # from 27-11 PAR>RPAR, so not necessary to adjust calculation

subset = twr[ (twr['site'] == site) & ((twr['datetime'].dt.year == year) & 
                 (twr['datetime'].dt.month.isin(month)) & 
                 (twr['datetime'].dt.day.isin(day)))] 

rws_to_change = (twr['site'] == site) & (twr['datetime'].dt.year == year) & (twr['datetime'].dt.month.isin(month))

twr.loc[rws_to_change, 'PAR_abs'] = np.where(
    twr.loc[rws_to_change, 'RPAR'] > twr.loc[rws_to_change, 'PAR'], # where RPAR>PAR (in reality, PAR is > RPAR)
    twr.loc[rws_to_change, 'RPAR'] - twr.loc[rws_to_change, 'PAR'], # perform RPAR-PAR instead of
    twr.loc[rws_to_change, 'PAR'] - twr.loc[rws_to_change, 'RPAR'] # the other way around
)


#%% Drop rows where PAR_abs is NaN or <0 and where Tsfc is NaN

twr = twr[(twr['PAR_abs'] > 0)] # NaNs are automatically also discarded
twr = twr.dropna(axis=0, subset=['Tsfc'])

#%% Rename columns to match column names of airborne data
# key = old name
# value = new name

dict = {'DOY':'DoY',
        'NEE_CO2':'CO2flx',
        }

twr.rename(columns=dict,  inplace=True)

#%% Assign new columns that exist in airborne data 

twr['FPlen_80'] = np.nan
twr['FPwgt_max'] = np.nan

#%% Drop unnecessary columns

colstodrop = ['filename', 'zm','measuringPeriod', 'hour','F_CO2','CO2_strg', 'SigStr_CO2',
              'co2_var', 'CH4_strg','h', 'sigmav','sumSOIL', 'NEE_CH4_MDS','NEE_CO2_MDS',
              'SWC_1_005','SWC_1_015','SWC_1_025','SWC_1_035','SWC_1_045','SWC_1_055',
              'SWC_1_065','SWC_1_075','SWC_1_085','SWC_1_095','SWC_1_105','SWC_1_115',
              'WL_cor','CO2_flag','CH4_flag','h2o_flag','H_flag','LE_flag','Tau_flag',
              'spikes_hf','amp_res_hf','drop_out_hf','abs_lim_hf','skw_kur_hf','skw_kur_sf',
              'discontinuities_hf','discontinuities_sf','time_lag_hf','time_lag_sf',
              'non_steady_wind_hf','attack_angle_hf','X.z.d..L','ol','model','x_peak',
              'x_offset','SWIN_KNMI','Tair_KNMI','PA_KNMI','RH_KNMI','WIND_KNMI',
              'WINS_KNMI','RAIN_KNMI','SWIN_NOBV1','SWIN_NOBV2','SWIN_NOBV3','SWIN_NOBV4',
              'SWOUT_NOBV1','SWOUT_NOBV2','SWOUT_NOBV3','SWOUT_NOBV4','LWIN_NOBV1',
              'LWIN_NOBV2','LWIN_NOBV3','LWIN_NOBV4','LWOUT_NOBV1','LWOUT_NOBV2',
              'LWOUT_NOBV3','LWOUT_NOBV4','PAR_NOBV1','PAR_NOBV2','PAR_NOBV3',
              'PAR_NOBV4','RPAR_NOBV1','RPAR_NOBV2','RPAR_NOBV3','RPAR_NOBV4','NIR_NOBV1',
              'NIR_NOBV2','NIR_NOBV3','NIR_NOBV4','RNIR_NOBV1','RNIR_NOBV2','RNIR_NOBV3',
              'RNIR_NOBV4','Tair_NOBV1','Tair_NOBV2','Tair_NOBV3','Tair_NOBV4',
              'RH_NOBV1','RH_NOBV2','RH_NOBV3','RH_NOBV4','WIND_NOBV2','VPD_NOBV3',
              'VPD_NOBV4','sunrise','sunset','daytime','WINS_f','VPD_EP_f','WIND_EP_f',
              'WINS_EP_f','UstarThreshold', 'RAIN', 'umean', 'wind_dir', 'WIND_EP',
              'ustar', 'u_var','v_var','DateTime', 'ET', 'RPAR', 'level_0', 'PAR_abs_temp',
              'PAR', 'SWIN', 'SWOUT', 'LWIN', 'LWOUT']


twr_cleaned = twr.drop(colstodrop, axis=1)

# Rename row numbers that are connected to the footprint files
twr_cleaned.rename(columns={'Unnamed: 0':'old_rownames'}, inplace=True)

#%% Reset index before saving 
twr_cleaned = twr_cleaned.reset_index()

# Only keep recent index
twr_cleaned = twr_cleaned.drop(['index'], axis = 'columns') 

#%% #%% Save cleaned tower dataset

twr_cleaned.to_csv(f"{WD}tower_1129_final.csv")
