# -*- coding: utf-8 -*-
"""
@author: l_vdp
Edited by: arietma, edited from: merge_airborne_tower.py and set_datetimes_merged.py
To enhance workflow efficiency, the two scripts are added in one.

This script merges the airborne and tower datasets, and makes the datetime columns
in a similar format.
Also, the seasonal subsets SepJan and FebAug are created from the final
merged dataset.

Input: the final tower and airborne datasets
Output: the final merged dataset with a correct datetime format, and the two
seasonal subsets

Edits by arietma:
    - Added creation of seasonal subsets

"""
#%% Import packages

import pandas as pd

#%% Set working directory and load final airborne and tower datasets

WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/' 

tower = pd.read_csv(f"{WD}tower_1129_final.csv", index_col=0)
airborne = pd.read_csv(f"{WD}air_1129_final.csv", index_col=0)

#%% Specify source of the datasets

tower['source']='tower'
airborne['source']='airborne'

#%% Merge the two datasets

merged = pd.concat([tower, airborne])

#%% Now, ensure the datetime format is similar
# The datetime of the airborne observations are stored in columns Date and Time,
# which are NAs for the tower observations
# The datetime of the tower observations are stored in the column datetime,
# which is NA for the airborne observations

# First change the format of Date (air) to match datetime (twr)
merged['Date'] = pd.to_datetime(merged['Date'], format='%d-%m-%Y')
merged['Date'] = merged['Date'].dt.strftime('%Y-%m-%d')

# Make new column for merged datetime
merged['Datetime'] = None

# Add twr dates to new column
merged['Datetime'] = pd.to_datetime(merged['datetime'], format = '%Y-%m-%d %H:%M:%S')
# Add air date + time to new column 
merged['Datetime'] = merged['Datetime'].fillna( pd.to_datetime(merged['Date']  + merged['Time'], format = '%Y-%m-%d %H:%M:%S') ) 

# Drop old datetime columns
merged = merged.drop(['Date', 'Time', 'datetime'], axis = 'columns')



#%% Save the final merged dataset
# (Here a later date than the input datasets since I later added the tower and
# airborne datasets with the most recent (OWASIS) observations, not shown here)

merged.to_csv(f"{WD}merged_0228_final.csv")


#%% Create seasonal subsets of the final merged dataset, SepJan and FebAug
# As the name indicates, SepJan includes all rows from the period September - 
# January, and FebAug all rows from the period February - August

# Specify rows for SepJan and FebAug
SepJan_rows = ((merged['Datetime'].dt.month.isin([9,10,11,12,1])))
FebAug_rows = ((merged['Datetime'].dt.month.isin([2,3,4,5,6,7,8])))

# Make two seasonal subsets
mer_SepJan = merged[SepJan_rows]
mer_FebAug = merged[FebAug_rows]

#%% Save the two final seasonal subsets

mer_SepJan.to_csv(f'{WD}merged_SepJan_0228.csv')
mer_FebAug.to_csv(f'{WD}merged_FebAug_0228.csv')
