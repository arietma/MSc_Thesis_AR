#------------
# author: lvdpoel
# edited by: arietma, edited from: fp_spat_temp_analysis_final.R (original file name)

# This script calculates the weighted average of two OWASIS variables (BBB and GWS) 
# and two MODIS variables (NDVI and EVI) in the airborne footprints, in HPC. Later,
# from GWS and ahn (DEM), groundwater relative to the ground level is calculated 
# (OWD)

# Input: all OWASIS data (.tif), all NDVI/EVI data (.tiff), all footprint files 
# (.nc), self-made functions from folder 'functions', airborne measurements data 
# (.csv)

# Output: airborne dataframe, with for every measurement, average NDVI, EVI, and 
# OWASIS variables (GWS and BBB). After running this script, the rows of the airborne 
# dataframe should be sorted in 'dataset_sortrows.R'

# Important note: be sure to load in the correct airborne dataset in the function
# find_ndvi_for_air and find_owasis_for_air, and make sure that the Date column 
# is in the correct format

# Edits by arietma:
# - Changed the script so that it is run in hpc in a job array, so every observation
# is calculated in parallel (much faster, a couple of minutes). For this 
# reason, the observations are written to the csv in 'append mode', which means 
# that the observations are not added in a sorted order. Therefore 'dataset_sortrows.R' 
# can be used after running this script to sort the dataframe
# - Removed the calculation of OWASIS variable OWD (this variable is later calculated
# from GWS and ahn)
# - Added the calculation of EVI
# - Adjusted the script to the data used in the current thesis
#---------------

rm(list=ls())

#####
# Libraries

library(stringr)
library(rlang)
library(terra)
library(lubridate)
library(gtools)
library(pracma)

################
# PREPARATION #
###############

# Load functions and set working directory
sapply(list.files(path = "/lustre/backup/WUR/ESG/rietm018/thesis/functions_spatpreproc/",full.names = T), source)
setwd('/lustre/backup/WUR/ESG/rietm018/thesis/')

# Create dataframes with file names of OWASIS data
# And save year + day of year of every file

## Bodemberging
ow.bb.folder <- "/lustre/backup/WUR/ESG/rietm018/thesis/Beschikbare.Bodemberging/"
ow.bb.files <- list.files(ow.bb.folder, pattern= '.tif')
ow.bb.df <- as.data.frame(ow.bb.files)

for(i in 1:nrow(ow.bb.df)){
  string <- ow.bb.df[i,1]
  ow.bb.df[i,'yeardoy'] = paste0(substr(string, 64,67), str_pad(yday(substr(string, 64,73)), 3, pad='0'))
  ow.bb.df[i,'yeardoy'] = as.numeric(ow.bb.df[i,'yeardoy'])
}


## Grondwaterstand
ow.gr.folder <- "/lustre/backup/WUR/ESG/rietm018/thesis/Grondwaterstand/"
ow.gr.files <- list.files(ow.gr.folder, pattern= '.tif')
ow.gr.df <- as.data.frame(ow.gr.files)

for(i in 1:nrow(ow.gr.df)){
  string <- ow.gr.df[i,1]
  ow.gr.df[i,'yeardoy'] = paste0(substr(string, 55,58), str_pad(yday(substr(string, 55,64)), 3, pad='0'))
  ow.gr.df[i,'yeardoy'] = as.numeric(ow.gr.df[i,'yeardoy'])
}

# Load NDVI and EVI data
ndvi_all <- rast("/lustre/backup/WUR/ESG/rietm018/thesis/modis_0531/NDVI_all.tiff")
evi_all <- rast("/lustre/backup/WUR/ESG/rietm018/thesis/modis_0531/EVI_all.tiff")

# Load footprint files
fp.folder <- '/lustre/backup/WUR/ESG/rietm018/thesis/fp_airborne_rasters_0907/'
fp.files <- list.files(fp.folder, pattern= '.nc')
fp.files <- mixedsort(fp.files)

# Load airborne data
alldata <- read.csv('/lustre/backup/WUR/ESG/rietm018/thesis/airborne_morecols_0907.csv', header=T, row.names=1)

# Add empty columns to the airborne data for storing the calculated data
alldata['BBB'] <- NaN
alldata['GWS'] <- NaN
alldata['OWD'] <- NaN
alldata['NDVI'] <- NaN
alldata['EVI'] <- NaN

# Specify output path
df_out <- alldata
# unsorted is added because rows are not added as 1,2,3 but based on which row is calculated first
pathout <- '/lustre/backup/WUR/ESG/rietm018/thesis/air_0908_spattemp_unsorted.csv'

# Write empty csv with colnames for storing the data, in if-statement so that only once a csv is created
if (!file.exists(pathout)) {
  write.csv(df_out[0,],pathout, row.names=TRUE)  # write a csv if there is not yet a file with the column names
} 

# Set up connection to the SLURM_ARRAY_TASK_ID to run the script as a job array 
# (=parallel, and faster) ADDED
args <- commandArgs(trailingOnly = TRUE)
slurm_task_id <- as.numeric(args[1])

##################################
# calculate average values in fp #
##################################

start=Sys.time() # keep track of time

for(i in 1:length(fp.files)){ # run loop for all footprints
  
  # Connect to the array id.  
  if (i == slurm_task_id) { # connects to the array id
    
    print(paste0(i, '/', length(fp.files)))
    
    # Get the right footprint file
    fp.file <- fp.files[[i]]
    
    # Name of footprint file is linked to the row in the airborne dataset
    rasterno <- as.numeric(fp.file %>% str_remove('.nc')) 
    
    # Load the footprint file
    mypathFP <- paste0(fp.folder, fp.file)
    myfp <- rast(mypathFP)
    
    # Find the correct files in time and calculate contributions
    
    # for BBB
    mybbfile <- find_owasis_for_air(rasterno=rasterno, owasisdf = ow.bb.df)$Owfile
    mybb <- rast(paste0(ow.bb.folder, mybbfile))
    bb_contr <- calc_spatdata_in_fp(fp=myfp, spatdata=mybb)$spatdata_contr
    
    # for GR
    mygrfile <- find_owasis_for_air(rasterno=rasterno, owasisdf =ow.gr.df)$Owfile
    mygr <- rast(paste0(ow.gr.folder, mygrfile))
    gr_contr <- calc_spatdata_in_fp(fp=myfp, spatdata = mygr)$spatdata_contr
    
    # NDVI
    myndvifile <- find_ndvi_for_air(rasterno=rasterno, ndvi_all=ndvi_all)
    myndvi <- myndvifile$Modfile
    # NDVI (also EVI) is linearly interpolated, so the closest and second to closest 
    # file in time is found: 
    myndvi2 <- myndvifile$Modfile2
    ndvi_contr <- calc_ndvi_in_fp(fp=myfp, ndvi=myndvi, ndvi2 = myndvi2, daydiff = myndvifile$DayDiff, daydiff2 = myndvifile$DayDiff2)$ndvi_contr
    
    # EVI
    myevifile <- find_ndvi_for_air(rasterno=rasterno, ndvi_all=evi_all)
    myevi <- myevifile$Modfile
    myevi2 <- myevifile$Modfile2
    evi_contr <- calc_ndvi_in_fp(fp=myfp, ndvi=myevi, ndvi2 = myevi2, daydiff = myevifile$DayDiff, daydiff2 = myevifile$DayDiff2)$ndvi_contr
    
    # save in df_out
    dfrow <- as.integer(rasterno)
    df_out[dfrow,'BBB'] <- bb_contr
    df_out[dfrow, 'GWS'] <- gr_contr
    df_out[dfrow, 'NDVI'] <- ndvi_contr
    df_out[dfrow, 'EVI'] <- evi_contr
    
    # Add rows to csv in append mode, , i.e. not overwriting the csv but adding
    # a row. In this way, the script can be run in parallel.
    write.table(df_out[dfrow,], pathout, sep = ',', row.names=TRUE, col.names=FALSE, append=TRUE)
    
    
  }
  
}  


end=Sys.time()
print(end-start)
