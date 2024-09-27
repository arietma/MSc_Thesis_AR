#------------
# author: arietma

# This script loads the tower data, calculates the surface temperature using
# Fourier's law, and then adds all tower site datasets in one dataset with all
# tower sites.

# Input: raw tower data, each file representing one tower site
# Output: one large tower dataset including all tower sites, and calculated 
# surface temperature
#------------

#### Load tower data ####
# Clean up environment
rm(list = ls(all.names = TRUE))

# Set path to folder
folder_path <- "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/tower/tower_notfpfiltered_MDS/"

# Get a list of all RDS files
file_list <- list.files(path=folder_path, pattern='*.RDS')

# Loop to load in RDS files
for (file_name in file_list) {
  file_path <- paste(folder_path, file_name, sep = "")
  data_name <- tools::file_path_sans_ext(file_name)  # remove the file extension from the file name
  assign(data_name, readRDS(file_path))
}

# Store site names
site_names <- tools::file_path_sans_ext(file_list)

#### Calculate Tsfc ####
# Using Fourier's law: q = -L * (dT/dz) with
# q: heat flux                        [W m-2]
# L: thermal conductivity             [W m-1 K-1]
# dT: temperature gradient            [K or degrees C]
# dz: distance btwn thermal surfaces  [m]

# Then: Tsfc = Tsoil + (q*dz)/-L

# L is calculated as follows: L = Ldry + (Lsat-Ldry) x log2(1+Sr), based on
# Zhao et al. (2019) (https://doi.org/10.1016/j.agrformet.2019.04.004) where
# Ldry: conductivity for dry peat soil       (0.055, on average)
# Lsat: conductivity for saturated peat soil (0.675, on average)
# Sr: degree of saturation, I calculated this: soil water content (dynamic)/ 
# saturated water content (constant, taken from Table 2 of 
# https://doi.org/10.1002/jpln.200621992 # (average) value for drained fen in NE 
# Germany)

# Constants
Ldry <- 0.055
Lsat <- 0.675
dz <- 0 - 5/100 # since calculating Tsfc based on Tsoil at 5 cm depth
saturated_water_cont <- mean(0.797,0.730,0.741,0.891)

# Filter to prevent strange Tsfc's
HOH$SHF1[18478:18867] <- NA # filter clearly is broken this time period, values
# ranging from -100 to +300.
# This can be shown with plot(HOH$SHF1) 

# Filter for AMM since high too high Tsfc are calculated where
# SWC is very low and SHF is high 
AMM$SWC_1_005[AMM$SWC_1_005 < 0.45] <- NA

for (site_name in site_names) {
  
  # Get the dataframe based on the site name
  df <- get(site_name)
  df$SHF1[df$SHF1 < -100| df$SHF1 == Inf] <- NA # to prevent strange Tsfc
  df$Tsoil_1_005[df$Tsoil_1_005 < -10] <- NA # to prevent strange Tsfc
  
  # Get dynamic variables
  soil_water_cont <- df$SWC_1_005 # soil water content, measured at 5cm
  Sr <- soil_water_cont/saturated_water_cont # Degree of saturation
  SHF <- df$SHF1 # soil heat flux, measured at ~5-10 cm in W/m2
  Tsoil_005 <- df$Tsoil_1_005
  L <- Ldry + (Lsat-Ldry) * log2(1+Sr) # thermal conductivity
  df$Tsfc <- rep(NA,nrow(df))
  
  # Calculation of Tsfc
  end <- nrow(df) 
  
  for (i in 2:end){ # 2 since for the first observation, flow cannot be calculated
    
    df$Tsfc[i] =  (Tsoil_005[i-1]+((SHF[i-1]*dz)/-L[i-1]))
  }
  
  assign(site_name, df) # save df with new column
}



##### Now make a df with all columns and all sites ######

# To store all column names
all_columns <- c()

for (site_name in site_names) {
  
  # Get the dataframe based on the site name
  df <- get(site_name)
  
  df_columns <- colnames(df)
  
  # Add all column names together
  all_columns <- union(all_columns, df_columns)
}

# Initialize empty dataframe
tower <- data.frame()

# Fill missing columns in with NA and bind all dataframes together
for (site_name in site_names){
  df <- get(site_name)
  df$site <- site_name
  
  # Fill in missing columns with NA
  missing_columns <- setdiff(all_columns, names(df))
  for (col in missing_columns) {
    df[[col]] <- NA
  }
  
  # Bind dataframes together
  tower <- rbind(tower, df)
}

# Save tower dataset
file_path <- "C:/Users/ariet/Documents/Climate Studies/WSG Thesis/data/"
write.csv(tower, paste(file_path,"tower_0607_allcolumns.csv",sep=""), row.names=FALSE)
