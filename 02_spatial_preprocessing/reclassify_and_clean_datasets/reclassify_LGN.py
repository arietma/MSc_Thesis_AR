"""
@author: ariet

This script reclassifies the land use (LGN) classes to fewer classes. An 
overview of the old LGN classes and corresponding codes can be found in the 
MSc Thesis by L. van der Poel (2022), 'Analysing airborne CO2 flux measurements 
in relation to landscape characteristics with machine learning', Appendix A.1,
or in the NOBV datasets. 
Some changes to the reclassification described in Appendix A.1 are made, which 
are specified in the script below. 

The script should be run once for the airborne dataset, and once for the tower
datset. 

Input: airborne and tower dataset after running fp_air/twr_ruimtdata_hpc
Output: airborne and tower dataset with reclassified land use classes

"""

#%% Import packages
import pandas as pd
import matplotlib.pyplot as plt

#%% Get tower or airborne data (already overlaid with spatial info)
WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'

# tower
# rawdata = pd.read_csv(f"{WD}tower_0607_preprocessed.csv", index_col=0)
# data = rawdata.reset_index() # reset index for indexing wit loc[]

# airborne
rawdata = pd.read_csv(f"{WD}air_0915_preprocessed.csv", index_col=0)
data = rawdata.reset_index() # reset index for indexing wit loc[]

#%% Defining new LGN classes

# LGN codes are double checked
# Changes with respect to Laura's Appendix A.1:
    # Code 20 occurred twice; 20 for FnB is discarded
    # Code 45 occurred twice; 45 for FnB is discarded
    # Code 39 did not occur, added to FnB since it represents bogs
    # In Shr, code 332 appeared twice. The last 332 is changed to 333, which 
    # corresponds to the description 'high shrubs'
    
LGNcodes = { 'bSl': [31,35],
            'Bld': [18,19,20,22,23,24,25,26,28],
            'cFr': [12,40],
            'dFr': [9,11,43,61,62],
            'FnB': [39,41,42],
            'Grs': [45,1,27,30,46,47],
            'Ghs': [8],
            'Hth': [32,33,34,36,37,38],
            'Wat': [16,17],
            'Shr': [321,322,323,331,332,333],
            'SpC': [5,10],
            'SuC': [2,3,4,6]
            }
  
#%% Reclassify LGN codes in dataframe

# List of columns in data that start with LGN (i.e. old LGN codes)
col_lgn = [col for col in data.columns if col.lower().startswith('lgn2020')]

# Add columns with new LGN codes, and sum all old LGN codes (values) that 
# belong to the same new LGN code (key)

summed_cols = [] # to keep track of the columns that are summed

for key in range(len(LGNcodes)): 
    key_name = list(LGNcodes.keys())[key]
    values = LGNcodes[key_name]
    
    # column list in one key:value pair
    string_list = [f'LGN2020_{value}' for value in values]
    cols_to_sum = [col for col in string_list if col in col_lgn] # columns of string_list that are present in col_lgn

    for j in data.index: # sum rows of old LGN codes to new LGN code
        row = data.loc[j]
        data.loc[j, key_name]=row[cols_to_sum].sum(skipna=True)

    summed_cols+= cols_to_sum

# Test if all columns have been summed
[col for col in col_lgn if col not in summed_cols]

#%% Check if LGN classes add up to 1
LGN_classes = ['Grs', 'SuC', 'SpC', 'Ghs', 'dFr', 'cFr', 'Wat',
       'Bld', 'bSl', 'Hth', 'FnB', 'Shr']

sumLGN = []

for i in data.index:
  row = data.loc[i] # possible since index is reset
  
  sumLGN.append(row[LGN_classes].sum(skipna=True)) # sum rows of LGN classes


plt.hist(sumLGN) # all 1
min(sumLGN)
max(sumLGN)

#%% Drop columns with old LGN classes and save result

# tower
# data = data.drop(summed_cols, axis='columns')
# data.to_csv(f"{WD}tower_0607_reclassifiedLGN.csv", na_rep='NA')

# airborne
data = data.drop(summed_cols, axis='columns')
data.to_csv(f"{WD}air_0915_reclassifiedLGN.csv", na_rep='NA')