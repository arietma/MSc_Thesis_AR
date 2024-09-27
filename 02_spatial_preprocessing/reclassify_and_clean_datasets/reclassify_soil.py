"""
@author: ariet

This script reclassifies the soil classes to fewer classes. An 
overview of the old soil classes and corresponding codes can be found in the 
MSc Thesis by L. van der Poel (2022), 'Analysing airborne CO2 flux measurements 
in relation to landscape characteristics with machine learning', Appendix A.1,
or in the NOBV datasets.

Some changes to the reclassification described in Appendix A.1 are made, which 
are specified in the script below. 

The script should be run once for the airborne dataset, and once for the tower
datset. 

Input: airborne and tower dataset after running reclassify_LGN
Output: airborne and tower dataset with reclassified soil classes
"""

#%% some imports
import pandas as pd
import matplotlib.pyplot as plt

#%% get tower or airborne data (already overlaid with spatial info)
WD = 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/'

# tower
# rawdata = pd.read_csv(f"{WD}tower_0607_reclassifiedLGN.csv", index_col=0)
# data = rawdata.reset_index() # reset index for indexing wit loc[]

# airborne
rawdata = pd.read_csv(f"{WD}air_0915_reclassifiedLGN.csv", index_col=0)
data = rawdata.reset_index() # reset index for indexing wit loc[]

#%% Defining new soil classes

# soil codes are double checked
# changes with respect to Laura's Appendix A.2:
    # new category 'Unclassified' for all unclassified soils
    
soilcodes = { 'W': [1,7,29,31,40,41,44,53,63,65,72,82,88,104,123,124,126,131,143,
                    149,152,174,179,187,191,226,239],
             'zandG' : [2,16,21,22,23,24,32,33,34,35,36,37,43,45,46,73,84,91,94,
                        96,99,107,116,121,122,134,135,137,140,147,151,157,159,
                        171,193,201,204,209,213,218,224,225,227,229,230,240,256,
                        259,260,261,262,263,264,265,268,272,282,296,300,301],  
             'zeeK' : [3,27,30,39,48,54,55,56,57,59,60,61,79,80,85,87,89,106,110,
                       113,125,139,148,154,156,160,161,166,167,170,172,173,176,
                       177,180,194,210,222,228,236,241,251,271,274,275,276,277,
                       278,279,280,286,294,295,297,298,299,302],
             'rivK' : [4,5,6,8,9,10,11,12,13,15,17,18,19,20,49,50,51,52,81,83,
                       128,129,130,136,141,142,145,162,165,178,181,182,192,195,
                       208,220,266,267,270,285,287,289],
             'V' : [14,153,158,163,169,202,203,269],
             'overigV' : [25,26,28,38,64,77,86,144,273,290,291,292],
             'pV' : [42,189,190,281,283,284,288],
             'hV' : [47,132,138,146,175,247],
             'gedA' : [58,66,67,75,76,78,95,100,101,102,103,105,108,109,111,112,
                       115,117,118,127,155,183,188,231,232,233,234,235,237,238,
                       242,243,244,245,246,248,249,250,252,254,255,257,258],
             'aVz' : [62],
             'leem' : [68,69,70,71,74,90,92,93,97,98,114,119,120,150,168,186,196,197,198,205,
                       206,207,211,212,214,215,216,219,221,223],
             'hVz' : [133],
             'kV' : [164,184,199,200,217,293],
             'kVz' : [185],
             'Vz' : [253],
             'Unclassified' : [999]}

#%% Reclassify soil codes in dataframe

# List of Bodemkaart columns (old soil codes) that appear in data
col_bodem = [col for col in data.columns if col.lower().startswith('bodemkaart')]

# Add columns with new soil codes, and sum all old soil codes (values) that 
# belong to the same new soil code (key)

summed_cols = [] # to keep track of the columns that are summed

for key in range(len(soilcodes)):
    key_name = list(soilcodes.keys())[key]
    values = soilcodes[key_name]
    
    # column list in one key:value pair
    string_list = [f'Bodemkaart_{value}' for value in values]
    cols_to_sum = [col for col in string_list if col in col_bodem] # columns of string_list that are present in col_bodem

    for j in data.index: # sum rows of old soil codes to new soil code
        row = data.loc[j]
        data.loc[j, key_name]=row[cols_to_sum].sum(skipna=True)

    summed_cols+= cols_to_sum

# Test if all columns have been summed
[col for col in col_bodem if col not in summed_cols]

#%% Check if soil classes add up to 1
soil_classes = ['hV', 'W', 'pV', 'kV', 'hVz', 'V',
       'Vz', 'aVz', 'kVz', 'overigV', 'zandG', 'zeeK', 'rivK', 'gedA', 'leem',
       'Unclassified']

sumSOIL = []

for i in data.index:
  row = data.loc[i] # possible since index is reset

  sumSOIL.append(row[soil_classes].sum(skipna=True)) # sum rows of soil classes

plt.hist(sumSOIL) # all 1
min(sumSOIL)
max(sumSOIL)

#%% Add values to category Unclassified
# No observations have values>0 for 'Unclassified'

# Some rows do not add up to 1, i.e. have a sumSOIL below 1
# These observations are randomly checked in QGIS and belong to a water body or 
# built environment, so 0.9999-sumSOIL is assigned to the category 'Unclassified'

data['Unclassified'] = 0.9999 - data['sumSOIL']

# Assign the value 0 to rows that have a negative number
data.loc[data['Unclassified'] < 0, 'Unclassified'] = 0


#%% Drop columns with old soil classes and save result
# tower
# data = data.drop(summed_cols, axis='columns')
# data.to_csv(f"{WD}tower_0607_reclassified.csv", na_rep='NA')

# airborne
data = data.drop(summed_cols, axis='columns')
data.to_csv(f"{WD}air_0915_reclassified.csv", na_rep='NA')