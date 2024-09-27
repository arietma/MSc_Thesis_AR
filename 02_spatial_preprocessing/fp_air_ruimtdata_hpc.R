#------------
# author: lvdpoel
# edited by: arietma, edited from: fp_ruimtdata_analysis_final.R (original file name)

# fp_analysis ruimtelijk data: soil, land use and peat depth maps
# script computes the percentages of present soil and land use classes, the 
# weighted peat depth  and height in the airborne footprint in HPC
# The ground level height of the footprint is  later used for converting the unit 
# of the groundwater table from relative to sea level to relative to ground level

# Input: land use, soil, peat depth and ahn maps,  all airborne footprint files (.nc), 
# self-made functions from folder 'functions', airborne measurements data (.csv)

# Output: airborne dataframe, with for every measurement, the present percentage of
# every land use and soil class, and the weighted average peat depth and height.
# of the footprint. After running this script, the rows of the airborne dataframe 
# should be sorted in 'dataset_sortrows.R'

# Edits by arietma:
# - Changed the script so that it is run in hpc in a job array, so every observation
# is calculated in parallel (much faster, now a couple of minutes). For this 
# reason, the observations are written to the csv in 'append mode', which means 
# that the observations are not added in a sorted order. Therefore 'dataset_sortrows.R' 
# can be used after running this script to sort the dataframe
# - Added the calculation of Peat Depth and ahn in the airborne footprints
# - Adjusted the script to the data used in the current thesis
#-----------------

rm(list=ls())


######## 
# Libraries

library(terra)
library(stringr)
library(readr)
library(tidyverse)
library(gtools)
library(foreign)
library(randomcoloR)

#########################################
#                                       #
# Get all necessary data and functions  #
#                                       #
#########################################


# Load functions and set working directory
sapply(list.files(path = "/lustre/backup/WUR/ESG/rietm018/thesis/functions_spatpreproc/",full.names = T), source)
setwd('/lustre/backup/WUR/ESG/rietm018/thesis/')

# Load maps
path <- "/lustre/backup/WUR/ESG/rietm018/thesis/ruimtelijke_data_veenweiden"
maps <- importMaps(path)
LGN <- maps$LGN2020         # land use classes
soilmap <- maps$Bodemkaart  # soil classes
PeatDmap <- maps$Veendikte  # peat depth
AHN <- maps$AHN             # DEM

# Load footprint files
fp.folder <- '/lustre/backup/WUR/ESG/rietm018/thesis/fp_airborne_rasters_0907/'
fp.files <- list.files(fp.folder, pattern= '.nc')
fp.files <- mixedsort(fp.files)

# Load airborne data
alldata <- read.csv('/lustre/backup/WUR/ESG/rietm018/thesis/air_0908_spattemp.csv', header=T, row.names=1)

# Add empty columns to the airborne data for storing the calculated data
extra_cols <- c(paste0('LGN2020_',LGN$classes$code),  paste0('Bodemkaart_',soilmap$classes$Value), paste0('PeatD'), paste0('ahn'))
alldata[extra_cols] <- NaN

# Specify output path
df_out <- alldata
# unsorted is added because rows are not added as 1,2,3 but based on which row is calculated first
pathout <- '/lustre/backup/WUR/ESG/rietm018/thesis/air_0915_preprocessed_unsorted.csv'

# Write empty csv with colnames for storing the data, in if-statement so that only once a csv is created
if (!file.exists(pathout)) {
  write.csv(df_out[0,],pathout, row.names=TRUE)  
} 

# Set up connection to the SLURM_ARRAY_TASK_ID (HPC) to run the script as a job 
# array (=parallel, and faster) ADDED
args <- commandArgs(trailingOnly = TRUE)
slurm_task_id <- as.numeric(args[1])

# Loop to calculate fraction of soil / land use classes and peat depth in the
# airborne footprints

stop <- length(fp.files) # run loop for all footprints
start=Sys.time() # keep track of time

for(i in 1:stop){
  if (i == slurm_task_id) { # connects to the array id
    
    print(paste0(i, '/', stop))
    
    # Get the right footprint file
    fp.file <- fp.files[i]
    
    # Name of footprint file is linked to the row in the airborne dataset
    rasterno <- as.numeric(fp.file %>% str_remove('.nc')) 
    
    # Load the footprint file
    mypathFP <- paste0(fp.folder, fp.file)
    myfp <- rast(mypathFP)
    
    # Calculate land use class (LGN) contributions
    # cat = T for categorical data
    lgn <- calc_ruimt_data_in_fp(data = LGN, fpraster = myfp, cat=T) 
    
    # Calculate soil class contributions
    soil <- calc_ruimt_data_in_fp(data = soilmap, fpraster = myfp, cat=T) 
    
    # Calculate peat depth in the footprint
    # cat = F for continuous data
    peat_depth <- calc_ruimt_data_in_fp(data = PeatDmap, fpraster = myfp, cat = F)
    
    # Calculate height of footprint
    ahn <- calc_ruimt_data_in_fp(data = AHN, fpraster = myfp, cat = F)
    
    # Add to the right row in the airborne dataset
    dfrow <- as.integer(rasterno)
    # Save calculations in df_out
    df_out[dfrow,] <- cbind(alldata[dfrow,],lgn,soil,peat_depth, ahn)
    
    # Add row to the csv in append mode, i.e. not overwriting the csv but adding
    # a row. In this way, the script can be run in parallel.
    write.table(df_out[dfrow,], pathout, sep = ',', row.names=TRUE, col.names=FALSE, append=TRUE)
    
  }
  
}  


end=Sys.time()
print(end-start)