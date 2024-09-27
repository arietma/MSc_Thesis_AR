#------------
# author: arietma

# This script should be run after running fp_air_spattemp_hpc.R, fp_twr_spattemp_hpc.R,
# fp_air_ruimtdata_hpc.R and fp_twr_ruimtdata_hpc.R, so four times in total. 
# These four scripts are run in hpc in parallel, so the newly calculated rows
# are added based on which is calculated first. 

# This script first checks whether all rows are present in the new dataset (can 
# be used for debugging) and next sorts the rows of the datasets

# Input: unsorted datasets after running fp_air_spattemp_hpc.R, fp_twr_spattemp_hpc.R,
# fp_air_ruimtdata_hpc.R and fp_twr_ruimtdata_hpc.R

# Output: sorted datasets. The sorted datasets of fp_air_sattemp_hpc.R and fp_spattemp_hpc.R
# are then used as input into fp_air_ruimtdata_hpc.R and fp_twr_ruimtdata_hpc.R

#------------

# Library
library(gtools)

# For one file, I show what has been done

# Load in air_0908_spattemp_unsorted.csv (new dataset after running fp_air_spattemp_hpc.R)
air_spattemp_unsorted <- read.csv('C:/Users/ariet/Documents/Climate Studies/WSG Thesis/Script/Edited_script_Laura/02_spatial_preprocessing/02_HPC_0907/air_0908_spattemp_unsorted.csv', header=T, row.names = 'X')

# First check whether all rows are present in the dataframe 
# If not, NAs occurred when calculating the spatiotemporal variables, and the 
# specific row numbers are present in missing_rws. Can be used for debugging
all_rws <- 1:2924
rws <- as.numeric(row.names(air_spattemp_unsorted))
missing_rws <- t(setdiff(all_rws, rws))

# Sort the dataframe based on the row numbers
air_spattemp_sorted <- air_spattemp_unsorted[mixedsort(rownames(air_spattemp_unsorted)), ]

# Save sorted df
write.csv(air_spattemp_sorted, 'C:/Users/ariet/Documents/Climate Studies/WSG Thesis/Script/Edited_script_Laura/02_spatial_preprocessing/02_HPC_0907/air_0908_spattemp.csv', row.names=TRUE)
